"""Image generation module for ViewPrettifier.

This module handles:
1. Edge detection from architectural images
2. Integration with Stable Diffusion for image generation
3. Progress reporting during processing
4. Image processing utilities
5. Model and ControlNet selection
6. Step and guidance scale configuration
"""

from __future__ import print_function, division, absolute_import

import os
import time
try:
    from io import BytesIO  # Python 3
except ImportError:
    from StringIO import StringIO as BytesIO  # Python 2
import base64
import gc
import psutil
import logging
import platform
import subprocess
try:
    from typing import Optional, Tuple, Dict, Any, Callable  # Python 3
except ImportError:
    pass  # Ignore type hints in Python 2
import sys
import importlib

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('viewprettifier_debug.log')
    ]
)
logger = logging.getLogger('ViewPrettifier.ImageGenerator')

def get_openai_api_keys():
    """Get API keys from various sources.
    
    Returns:
        Dict containing API keys for different services
    """
    keys = {
        "replicate": None,
        "huggingface": None
    }
    
    # Try environment variables first
    keys["replicate"] = os.environ.get("REPLICATE_API_TOKEN")
    keys["huggingface"] = os.environ.get("HUGGINGFACE_API_KEY")
    
    # If not found in env vars, try EnneadTab SECRET
    if not any(keys.values()):
        try:
            # Add lib path to system path for importing SECRET
            lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib"))
            if lib_path not in sys.path:
                sys.path.append(lib_path)
            
            try:
                from EnneadTab import SECRET
                # Try to get keys from SECRET
                if not keys["replicate"]:
                    keys["replicate"] = SECRET.get_openai_api_key("replicate")
                if not keys["huggingface"]:
                    keys["huggingface"] = SECRET.get_openai_api_key("huggingface")
            except ImportError as e:
                logger.warning(f"Could not import EnneadTab SECRET: {str(e)}")
            except Exception as e:
                logger.warning(f"Error getting keys from SECRET: {str(e)}")
                
        except Exception as e:
            logger.warning(f"Error accessing SECRET module: {str(e)}")
    
    # Log what we found (without showing the actual keys)
    for service, key in keys.items():
        if key:
            logger.info(f"Found API key for {service}")
        else:
            logger.info(f"No API key found for {service}")
    
    return keys

def install_dependencies():
    """Install or upgrade required dependencies."""
    logger.info("Checking and installing dependencies...")
    
    # Core dependencies that are always needed
    core_dependencies = [
        "torch",
        "diffusers",
        "transformers",
        "opencv-python",
        "pillow",
        "requests",
        "importlib-metadata"  # For better package version checking
    ]
    
    # Get API keys to check which cloud providers we need
    api_keys = get_openai_api_keys()
    
    # Add cloud dependencies only if we have their API keys
    cloud_dependencies = []
    if api_keys["replicate"]:
        logger.info("Replicate API key found, will install replicate package")
        cloud_dependencies.append("replicate")
    if api_keys["huggingface"]:
        logger.info("Hugging Face API key found, will install huggingface-hub package")
        cloud_dependencies.append("huggingface-hub")
    
    # Combine dependencies
    dependencies = core_dependencies + cloud_dependencies
    
    for package in dependencies:
        try:
            importlib.import_module(package.replace("-", "_"))
            logger.info(f"{package} is already installed")
        except ImportError:
            logger.info(f"Installing {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                logger.info(f"Successfully installed {package}")
            except Exception as e:
                logger.error(f"Failed to install {package}: {str(e)}")
                return False
    
    return True

# Install dependencies first
if not install_dependencies():
    logger.error("Failed to install required dependencies")
    raise ImportError("Required dependencies could not be installed")

# Now import the dependencies
try:
    import cv2
    import numpy as np
    from PIL import Image
    import torch
    from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
    from diffusers.utils import load_image
    DEPENDENCIES_AVAILABLE = True
    logger.info("All dependencies imported successfully")
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    logger.error(f"Failed to import dependencies: {str(e)}")
    raise

def check_gpu_availability():
    """Check for available GPU and its capabilities.
    
    Returns:
        Dict containing GPU information and availability
    """
    gpu_info = {
        "has_gpu": False,
        "cuda_available": False,
        "gpu_name": None,
        "vram_gb": None,
        "recommended_backend": "cpu"
    }
    
    try:
        # Check NVIDIA GPU with system commands first
        if platform.system() == "Windows":
            try:
                nvidia_smi = subprocess.check_output(["nvidia-smi", "-L"]).decode()
                if nvidia_smi:
                    gpu_info["has_gpu"] = True
                    gpu_info["gpu_name"] = nvidia_smi.split("GPU 0: ")[1].split("(")[0].strip()
            except:
                pass
        
        # Check CUDA availability through PyTorch
        if torch.cuda.is_available():
            gpu_info["cuda_available"] = True
            gpu_info["gpu_name"] = torch.cuda.get_device_name(0)
            gpu_info["vram_gb"] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            gpu_info["recommended_backend"] = "cuda"
            
            # Check if GPU is powerful enough
            if gpu_info["vram_gb"] < 4:
                logger.warning("GPU has less than 4GB VRAM, might be too slow or unstable")
                gpu_info["recommended_backend"] = "cpu"
        
        # Check for Apple Silicon
        elif platform.system() == "Darwin" and platform.processor() == "arm":
            try:
                import torch.mps
                if torch.backends.mps.is_available():
                    gpu_info["has_gpu"] = True
                    gpu_info["gpu_name"] = "Apple Silicon"
                    gpu_info["recommended_backend"] = "mps"
            except:
                pass
                
    except Exception as e:
        logger.error(f"Error checking GPU availability: {str(e)}")
    
    logger.info(f"GPU check results: {gpu_info}")
    return gpu_info

def check_cloud_compute_availability():
    """Check for available free cloud compute options.
    
    Returns:
        Dict containing cloud compute availability and details
    """
    cloud_info = {
        "available": False,
        "provider": None,
        "api_key_required": False,
        "estimated_cost": "Free",
        "limitations": None
    }
    
    try:
        # Check for Hugging Face Inference API availability
        try:
            from huggingface_hub import HfApi
            cloud_info["available"] = True
            cloud_info["provider"] = "Hugging Face"
            cloud_info["api_key_required"] = True
            cloud_info["limitations"] = "Rate limits apply for free tier"
        except ImportError:
            pass
            
        # Check for Replicate availability
        try:
            import replicate
            cloud_info["available"] = True
            cloud_info["provider"] = "Replicate"
            cloud_info["api_key_required"] = True
            cloud_info["estimated_cost"] = "Credits required"
        except ImportError:
            pass
            
    except Exception as e:
        logger.error(f"Error checking cloud compute availability: {str(e)}")
    
    logger.info(f"Cloud compute check results: {cloud_info}")
    return cloud_info

def get_compute_backend():
    """Get the best available compute backend based on priority:
    1. Replicate API (if key available)
    2. Hugging Face API (if key available)
    3. Local GPU
    4. Local CPU
    
    Returns:
        Dict containing compute backend information
    """
    backend_info = {
        "type": "cpu",
        "name": "CPU",
        "provider": None,
        "api_key": None,
        "reason": "Fallback to CPU compute"
    }
    
    # Get API keys first
    api_keys = get_openai_api_keys()
    
    # Only try cloud providers if we have their keys
    if api_keys["replicate"]:
        # Only import replicate if we have a key
        try:
            import replicate
            # Test the API key
            try:
                client = replicate.Client(api_token=api_keys["replicate"])
                # Just access a property to verify the key works
                _ = client.api_token
                backend_info["type"] = "cloud"
                backend_info["name"] = "Replicate"
                backend_info["provider"] = "replicate"
                backend_info["api_key"] = api_keys["replicate"]
                logger.info("Using Replicate cloud compute")
                return backend_info
            except Exception as e:
                logger.warning(f"Replicate API key validation failed: {str(e)}")
        except ImportError:
            logger.info("Replicate package not available, skipping")
    else:
        logger.debug("No Replicate API key found, skipping Replicate check")
    
    # Try Hugging Face only if we have a key
    if api_keys["huggingface"]:
        try:
            from huggingface_hub import HfApi
            # Test the API key
            try:
                api = HfApi(token=api_keys["huggingface"])
                # Just access a property to verify the key works
                _ = api.token
                backend_info["type"] = "cloud"
                backend_info["name"] = "Hugging Face"
                backend_info["provider"] = "huggingface"
                backend_info["api_key"] = api_keys["huggingface"]
                logger.info("Using Hugging Face cloud compute")
                return backend_info
            except Exception as e:
                logger.warning(f"Hugging Face API key validation failed: {str(e)}")
        except ImportError:
            logger.info("Hugging Face package not available, skipping")
    else:
        logger.debug("No Hugging Face API key found, skipping Hugging Face check")
    
    # Try Local GPU
    gpu_info = check_gpu_availability()
    if gpu_info["recommended_backend"] == "cuda":
        backend_info["type"] = "gpu"
        backend_info["name"] = gpu_info["gpu_name"]
        backend_info["provider"] = "local"
        backend_info["reason"] = "Using local GPU acceleration"
        logger.info(f"Using local GPU compute: {gpu_info['gpu_name']}")
        return backend_info
    
    # Fallback to CPU
    logger.info("No better compute options available, using CPU")
    backend_info["reason"] = f"Using CPU (no GPU or cloud compute available)"
    return backend_info

class ImageGenerator:
    """Class to handle image generation with progress tracking.
    
    This class encapsulates the state of the generation process and
    removes the need for global variables.
    """
    
    def __init__(self):
        """Initialize the image generator with default values."""
        # State tracking
        self._progress = 0
        self._status = "Idle"
        self._last_progress_time = time.time()
        self._thread = None
        self._is_running = False
        self._output_image = None
        
        # Get best available compute backend
        self._compute_info = get_compute_backend()
        logger.info(f"Selected compute backend: {self._compute_info['name']} ({self._compute_info['type']})")
        
        # Configuration parameters (can be changed by GUI)
        self._model_id = "runwayml/stable-diffusion-v1-5"
        self._controlnet_id = "lllyasviel/sd-controlnet-canny"
        self._steps = 30
        self._guidance_scale = 7.5
        
        # Initialize appropriate provider if using cloud
        self._cloud_provider = None
        if self._compute_info["type"] == "cloud":
            if self._compute_info["provider"] == "replicate":
                self._cloud_provider = ReplicateProvider()
                self._cloud_provider.api_key = self._compute_info["api_key"]
            elif self._compute_info["provider"] == "huggingface":
                self._cloud_provider = HuggingFaceProvider()
                self._cloud_provider.api_key = self._compute_info["api_key"]
        
        logger.debug("ImageGenerator initialized")
        
    @property
    def progress(self) -> int:
        """Get current progress percentage."""
        return self._progress
        
    @property
    def status(self) -> str:
        """Get current status message."""
        return self._status
        
    @property
    def is_running(self) -> bool:
        """Check if generation is currently running."""
        return self._is_running
        
    @property
    def compute_backend(self) -> str:
        """Get current compute backend name."""
        return self._compute_info["name"]
        
    def update_progress(self, progress: int, status: str) -> None:
        """Update the progress and status of the generation."""
        self._progress = progress
        self._status = status
        self._last_progress_time = time.time()
        logger.info(f"Progress updated: {progress}% - {status}")
        
    def get_progress_status(self) -> Tuple[int, str, float]:
        """Get the current progress status."""
        time_since_update = time.time() - self._last_progress_time
        logger.debug(f"Current progress: {self._progress}% - Status: {self._status} - Time since update: {time_since_update:.1f}s")
        return self._progress, self._status, time_since_update
    
    def detect_edges(self, image_path):
        """Detect edges in an image to preserve structure for AI generation.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Path to the generated edge map image
        """
        self.update_progress(5, "Detecting edges")
        
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image from {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detect edges using Canny
        edges = cv2.Canny(blurred, 50, 150)
        
        # Save edge map
        edge_path = os.path.join(os.path.dirname(image_path), "edge_map.jpg")
        cv2.imwrite(edge_path, edges)
        
        # Update progress
        self.update_progress(20, "Edge detection complete")
        
        return edge_path
    
    def generate_with_stable_diffusion(self, base_image, edge_map, style_image, prompt, negative_prompt):
        """Generate an image using Stable Diffusion with ControlNet.
        
        Args:
            base_image: Path to the base image
            edge_map: Path to the edge map image
            style_image: Path to the style reference image
            prompt: Text prompt for generation
            negative_prompt: Negative text prompt
            
        Returns:
            Generated image as PIL Image object
        """
        self.update_progress(30, "Loading models")
        
        # If using cloud compute, delegate to appropriate provider
        if self._compute_info["type"] == "cloud":
            logger.info(f"Using cloud compute via {self._compute_info['provider']}")
            try:
                # Load the control image
                control_image = load_image(edge_map)
                
                # If style reference exists, adjust prompt
                if os.path.exists(style_image):
                    prompt = f"{prompt}, in the style of the reference image"
                    logger.info(f"Using style reference image: {style_image}")
                
                # Use asyncio to run the async cloud generation
                import asyncio
                output = asyncio.run(self._cloud_provider.generate_image(prompt, control_image))
                
                if output:
                    self.update_progress(90, "Cloud generation complete")
                    return output
                else:
                    logger.error("Cloud generation failed")
                    self._status = "Failed"
                    return None
                    
            except Exception as e:
                logger.error(f"Error using cloud compute: {str(e)}")
                logger.info("Falling back to local compute")
                # Continue with local compute as fallback
        
        # Local compute (GPU or CPU)
        # Log what we're using
        logger.info(f"Using model: {self._model_id}")
        logger.info(f"Using controlnet: {self._controlnet_id}")
        
        # Load ControlNet model for edge guidance
        try:
            logger.info("Loading ControlNet model (downloading if needed)...")
            controlnet = ControlNetModel.from_pretrained(
                self._controlnet_id,
                torch_dtype=torch.float16
            )
            self.update_progress(35, "ControlNet model loaded")
        except Exception as e:
            logger.error(f"Error loading ControlNet model: {str(e)}")
            self._status = "Failed"
            return None
        
        # Load Stable Diffusion pipeline
        try:
            logger.info("Loading Stable Diffusion model (downloading if needed)...")
            pipe = StableDiffusionControlNetPipeline.from_pretrained(
                self._model_id,
                controlnet=controlnet, 
                torch_dtype=torch.float16,
                safety_checker=None
            )
            self.update_progress(40, "Stable Diffusion pipeline loaded")
        except Exception as e:
            logger.error(f"Error loading Stable Diffusion pipeline: {str(e)}")
            self._status = "Failed"
            return None
        
        # Use more efficient scheduler
        pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
        
        # Move to GPU if using local GPU
        if self._compute_info["type"] == "gpu":
            pipe = pipe.to("cuda")
            logger.info("Using GPU acceleration for generation")
        else:
            logger.info("Running on CPU (this may be slow)")
        
        self.update_progress(50, "Preparing images")
        
        # Load the control image
        control_image = load_image(edge_map)
        
        # If style reference exists, adjust prompt
        if os.path.exists(style_image):
            prompt = f"{prompt}, in the style of the reference image"
            logger.info(f"Using style reference image: {style_image}")
        
        self.update_progress(60, "Generating image")
        
        # Log generation parameters
        logger.info(f"Using {self._steps} inference steps with guidance scale {self._guidance_scale}")
        
        # Generate image with progress callback
        try:
            def callback(step, timestep, latents):
                # Update progress during generation (60-90%)
                progress = 60 + int((step / self._steps) * 30)
                self.update_progress(progress, "Generating image")
                return True
            
            output = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=control_image,
                num_inference_steps=self._steps,
                guidance_scale=self._guidance_scale,
                callback=callback,
                callback_steps=1
            ).images[0]
            
            self.update_progress(90, "Processing final image")
            
            # Free up GPU memory if using GPU
            if self._compute_info["type"] == "gpu":
                torch.cuda.empty_cache()
            del pipe
            del controlnet
            gc.collect()
            
            return output
        except Exception as e:
            logger.error(f"Error during image generation: {str(e)}")
            self._status = "Failed"
            return None
    
    def generate_image(self, input_image_path: str, edge_map_path: str = None, progress_callback: Callable[[float, str], None] = None) -> str:
        """Generate an image using the selected provider.
        
        Args:
            input_image_path: Path to input image
            edge_map_path: Optional path to edge map image
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to generated image
        """
        try:
            # Check if we have any API keys
            api_keys = self.get_openai_api_keys()
            if not any(api_keys.values()):
                logger.info("No API keys available - using local model")
                return self._generate_image_local(input_image_path, edge_map_path, progress_callback)
            
            # Try cloud providers first
            if api_keys["replicate"]:
                return self._generate_image_replicate(input_image_path, edge_map_path, progress_callback)
            elif api_keys["huggingface"]:
                return self._generate_image_huggingface(input_image_path, edge_map_path, progress_callback)
            else:
                logger.warning("No API keys available for cloud providers")
                return self._generate_image_local(input_image_path, edge_map_path, progress_callback)
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise

    def _generate_image_local(self, input_image_path: str, edge_map_path: str = None, progress_callback: Callable[[float, str], None] = None) -> str:
        """Generate image using local model.
        
        Args:
            input_image_path: Path to input image
            edge_map_path: Optional path to edge map image
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to generated image
        """
        try:
            import torch
            from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
            from PIL import Image
            import numpy as np
            
            if progress_callback:
                progress_callback(0.1, "Loading local model...")
            
            logger.info("Loading local model...")
            
            # Load control net model
            controlnet = ControlNetModel.from_pretrained(
                "lllyasviel/sd-controlnet-canny",
                torch_dtype=torch.float32
            )
            
            # Load pipeline
            pipe = StableDiffusionControlNetPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                controlnet=controlnet,
                torch_dtype=torch.float32
            )
            
            if progress_callback:
                progress_callback(0.3, "Processing input image...")
            
            # Load and process input image
            input_image = Image.open(input_image_path)
            edge_image = Image.open(edge_map_path) if edge_map_path else None
            
            if progress_callback:
                progress_callback(0.4, "Generating image...")
            
            # Generate image
            output = pipe(
                "architectural visualization, photorealistic, high quality render",
                image=input_image,
                control_image=edge_image,
                num_inference_steps=20,
                guidance_scale=7.5
            ).images[0]
            
            # Save output
            output_path = os.path.join(os.path.dirname(input_image_path), "generated_image.png")
            output.save(output_path)
            
            if progress_callback:
                progress_callback(1.0, "Done!")
            
            logger.info(f"Generated image saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error in local generation: {str(e)}")
            raise
    
    def check_if_stuck(self, timeout_seconds=600, progress_timeout_seconds=180):
        """Check if the process appears to be stuck."""
        current_time = time.time()
        total_time = current_time - self._last_progress_time
        
        if total_time > timeout_seconds:
            msg = f"Process exceeded total timeout of {timeout_seconds} seconds"
            logger.warning(msg)
            return True, msg
            
        if total_time > progress_timeout_seconds and self._status != "Complete":
            msg = f"No progress update in {progress_timeout_seconds} seconds"
            logger.warning(msg)
            return True, msg
            
        return False, ""
    
    def get_system_info(self):
        """Get system resource information for diagnostics."""
        try:
            memory = psutil.virtual_memory()
            info = {
                "Total RAM": f"{memory.total / (1024**3):.1f}GB",
                "Available RAM": f"{memory.available / (1024**3):.1f}GB",
                "RAM Usage": f"{memory.percent}%",
                "CPU Usage": f"{psutil.cpu_percent()}%"
            }
            if torch.cuda.is_available():
                info["CUDA Available"] = "Yes"
                info["GPU"] = torch.cuda.get_device_name(0)
                info["GPU Memory"] = f"{torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f}GB"
            else:
                info["CUDA Available"] = "No"
            logger.debug(f"System info: {info}")
            return info
        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}", exc_info=True)
            return {"Error": str(e)}
    
    def terminate(self):
        """Terminate the generation process."""
        logger.info("Terminating generation process")
        self._is_running = False
        if self._thread and self._thread.is_alive():
            # Signal the thread to stop
            self._thread.join(timeout=5)
        self._status = "Terminated"
        self._progress = 0
        

class CloudComputeProvider:
    """Base class for cloud compute providers."""
    
    def __init__(self):
        self.api_key = None
        
    def is_available(self) -> bool:
        """Check if this provider is available."""
        return False
        
    async def generate_image(self, prompt: str, image: Image.Image) -> Optional[Image.Image]:
        """Generate image using cloud compute."""
        raise NotImplementedError

class HuggingFaceProvider(CloudComputeProvider):
    """Hugging Face Inference API provider."""
    
    def __init__(self):
        super().__init__()
        self._client = None
        
    def is_available(self) -> bool:
        try:
            from huggingface_hub import HfApi
            return True
        except ImportError:
            return False
            
    async def generate_image(self, prompt: str, image: Image.Image) -> Optional[Image.Image]:
        """Generate image using Hugging Face Inference API."""
        try:
            from huggingface_hub import InferenceClient
            if not self._client and self.api_key:
                self._client = InferenceClient(token=self.api_key)
                
            if not self._client:
                logger.error("Hugging Face API key not set")
                return None
                
            # Convert PIL Image to bytes
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Call the API
            result = await self._client.post(
                "stabilityai/stable-diffusion-xl-base-1.0",
                inputs={
                    "prompt": prompt,
                    "image": img_byte_arr,
                }
            )
            
            # Convert result to PIL Image
            return Image.open(BytesIO(result))
            
        except Exception as e:
            logger.error(f"Error using Hugging Face API: {str(e)}")
            return None

class ReplicateProvider(CloudComputeProvider):
    """Replicate.com provider."""
    
    def __init__(self):
        super().__init__()
        self._client = None
        
    def is_available(self) -> bool:
        try:
            import replicate
            return True
        except ImportError:
            return False

    async def generate_image(self, prompt: str, image: Image.Image) -> Optional[Image.Image]:
        """Generate image using Replicate API."""
        try:
            import replicate
            if not self._client and self.api_key:
                self._client = replicate.Client(api_token=self.api_key)
                
            if not self._client:
                logger.error("Replicate API key not set")
                return None
                
            # Convert PIL Image to base64
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            img_base64 = base64.b64encode(img_byte_arr).decode()
            
            # Run the model
            output = self._client.run(
                "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                input={
                    "prompt": prompt,
                    "image": img_base64
                }
            )
            
            # Get the result image URL and download it
            if output and len(output) > 0:
                from PIL import Image
                import requests
                response = requests.get(output[0])
                return Image.open(BytesIO(response.content))
            return None
            
        except Exception as e:
            logger.error(f"Error using Replicate API: {str(e)}")
            return None

def create_image_generator() -> ImageGenerator:
    """Factory function to create an ImageGenerator instance.
    
    This replaces the global generator instance with a proper factory pattern.
    """
    return ImageGenerator()

# Remove all global variables and instances
__all__ = ['ImageGenerator', 'create_image_generator', 'check_gpu_availability', 'check_cloud_compute_availability'] 