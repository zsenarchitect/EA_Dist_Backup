"""
The main purpose of this module is to handle file copying operations with verification across different Python environments. In previous Rhino 8 there is a bug that shutil.copyfile will fail. 
Supports both standard Python and IronPython 2.7 in Rhino by providing multiple file copy methods.
This module ensures that large files are completely copied before returning.
"""


import os
import time
import threading


def copyfile(src, dst, include_metadata=True, verify=True, timeout=120, run_threaded=False):
    """
    Copy a file from source to destination with verification to ensure complete copy.
    Automatically selects the best copy method based on environment capabilities.
    
    Args:
        src: Source file path
        dst: Destination file path
        include_metadata: Whether to include file metadata in the copy
        verify: Whether to verify the file is completely copied
        timeout: Maximum time in seconds to wait for copy verification
        run_threaded: Whether to run the copy operation in a separate thread
    
    Returns:
        bool: True if copy was successful, False otherwise
        If run_threaded is True, returns the thread object instead
    """
    if run_threaded:
        # Create a thread for the copy operation
        copy_thread = threading.Thread(
            target=_copyfile_thread,
            args=(src, dst, include_metadata, verify, timeout)
        )
        copy_thread.daemon = True  # Don't let this thread block program exit
        copy_thread.start()
        return copy_thread
    else:
        # Run synchronously
        return _copyfile_thread(src, dst, include_metadata, verify, timeout)


def _copyfile_thread(src, dst, include_metadata=True, verify=True, timeout=120):
    """
    Internal function to handle the actual copy operation, potentially in a thread.
    """
    try:
        return copyfile_with_cpy(src, dst, include_metadata, verify, timeout)
    except Exception as e:
        try:
            # Only print debug info for specific user
            if os.getenv("USERNAME") == "szhang":
                print("Standard copy failed, trying dotnet method:", e)
            
            # Try .NET method which works in IronPython
            return copyfile_with_dotnet(src, dst, verify, timeout)
        except Exception as e2:
            # Last resort - basic file copy if all else fails
            if os.getenv("USERNAME") == "szhang":
                print("Dotnet copy failed, trying basic method:", e2)
            return copyfile_basic(src, dst, verify, timeout)


def copyfile_with_cpy(src, dst, include_metadata=True, verify=True, timeout=120):
    """
    Copy a file from source to destination using Python's shutil.
    
    Args:
        src: Source file path
        dst: Destination file path
        include_metadata: Whether to include file metadata in the copy
        verify: Whether to verify the file is completely copied
        timeout: Maximum time in seconds to wait for copy verification
        
    Returns:
        bool: True if copy was successful, False otherwise
    """
    import shutil
     # Get source file size for verification
    if verify and os.path.exists(src):
        src_size = os.path.getsize(src)
    
    # Perform the copy operation
    if include_metadata:
        # Copy file with metadata
        shutil.copy2(src, dst)  # shutil.copy2 copies both file content and metadata
    else:
        # Copy file content only
        shutil.copyfile(src, dst)
        
    # Verify the copy is complete for large files
    if verify and src_size > 1024*1024:  # Only verify for files larger than 1MB
        return verify_copy_complete(src, dst, src_size, timeout)
    
    return True
    
def copyfile_with_dotnet(src, dst, verify=True, timeout=120):
    """
    Copy a file using .NET framework methods - compatible with IronPython.
    
    Args:
        src: Source file path
        dst: Destination file path
        verify: Whether to verify the file is completely copied
        timeout: Maximum time in seconds to wait for copy verification
    
    Returns:
        bool: True if copy was successful, False otherwise
    """

    # Get source file size for verification
    if verify:
        try:
            # Try normal Python method first
            src_size = os.path.getsize(src)
        except:
            # Fall back to .NET method
            try:
                from System.IO import FileInfo  # pyright: ignore
                src_size = FileInfo(src).Length
            except:
                # If this also fails, skip verification
                verify = False
    
    # Create destination directory if it doesn't exist
    try:
        dst_dir = os.path.dirname(dst)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
    except:
        pass
        
    # Perform copy using dotnet
    try:
        from System.IO import File  # pyright: ignore
        File.Copy(src, dst, True)  # True to overwrite if exists
    except ImportError:
        # Fall back if System.IO not available
        raise Exception("System.IO not available in this Python environment")
    
    # Verify the copy is complete for large files
    if verify and src_size > 1024*1024:  # Only verify for files larger than 1MB
        return verify_copy_complete(src, dst, src_size, timeout)
        
    return True


def copyfile_basic(src, dst, verify=True, timeout=120):
    """
    Basic file copy using raw Python - last resort method.
    
    Args:
        src: Source file path
        dst: Destination file path
        verify: Whether to verify the file is completely copied
        timeout: Maximum time in seconds to wait for copy verification
    
    Returns:
        bool: True if copy was successful, False otherwise
    """
    # Get source file size for verification
    if verify and os.path.exists(src):
        try:
            src_size = os.path.getsize(src)
        except:
            verify = False
    
    # Create destination directory if it doesn't exist
    try:
        dst_dir = os.path.dirname(dst)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
    except:
        pass
            
    # Basic file copy operation
    with open(src, 'rb') as src_file:
        with open(dst, 'wb') as dst_file:
            dst_file.write(src_file.read())
            
    # Verify the copy is complete
    if verify and src_size > 1024*1024:  # Only verify for files larger than 1MB
        return verify_copy_complete(src, dst, src_size, timeout)
        
    return True


def verify_copy_complete(src, dst, src_size, timeout=120):
    """
    Verify that a file has been completely copied by checking file sizes.
    
    Args:
        src: Source file path
        dst: Destination file path
        src_size: Size of the source file in bytes
        timeout: Maximum time in seconds to wait for verification
    
    Returns:
        bool: True if verification successful, False otherwise
    """

    try:
        # print("Copy verification started")
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not os.path.exists(dst):
                time.sleep(0.5)
                continue
                
            dst_size = os.path.getsize(dst)
            if dst_size == src_size:
                # print("Copy verification successful, copy took {} seconds".format(time.time() - start_time))
                return True
                
            # Wait a bit before checking again
            time.sleep(0.5)
        
        # If we got here, verification timed out
        print("Copy verification timed out after {} seconds".format(timeout))
        return False
    except Exception as e:
        print("Verification failed:", e)
        return False

def run_unittest():
    """
    Test function to verify file copying works with large files
    """
    import tempfile
    import unittest
    class TestFileCopy(unittest.TestCase):
        def setUp(self):
            # Create temp directory for testing
            self.test_dir = tempfile.mkdtemp()
            
            # Create a source file path
            self.src_path = os.path.join(self.test_dir, "source_large_file.dat")
            self.dst_path = os.path.join(self.test_dir, "destination_large_file.dat")
            
            # Create a mock large file (100MB)
            self.file_size = 100 * 1024 * 1024  # 100MB
            self.create_large_file(self.src_path, self.file_size)
            
        def create_large_file(self, filepath, size):
            """Create a file of specified size with random data"""
            with open(filepath, 'wb') as f:
                # Write in chunks to avoid memory issues
                chunk_size = 1024 * 1024  # 1MB chunks
                remaining = size
                
                while remaining > 0:
                    write_size = min(chunk_size, remaining)
                    f.write(os.urandom(write_size))
                    remaining -= write_size
            
            # Verify the file was created with the correct size
            self.assertEqual(os.path.getsize(filepath), size)
            print("Created test file: {} ({:.2f} MB)".format(
                os.path.basename(filepath), 
                os.path.getsize(filepath) / (1024 * 1024)
            ))
            
        def tearDown(self):
            # Clean up test files
            import shutil
            try:
                shutil.rmtree(self.test_dir)
                print("Test cleanup successful")
            except Exception as e:
                print("Warning: Test cleanup failed:", e)
                
        def test_copy_large_file(self):
            """Test that large files are copied correctly"""
            print("\nTesting copy of large file...")
            
            # Test with verification
            result = copyfile(self.src_path, self.dst_path, verify=True)
            self.assertTrue(result, "Copy operation with verification failed")
            
            # Check file sizes match
            src_size = os.path.getsize(self.src_path)
            dst_size = os.path.getsize(self.dst_path)
            self.assertEqual(src_size, dst_size, 
                "File sizes don't match: src={}, dst={}".format(src_size, dst_size))
            
            print("Copy test successful: File copied correctly with verification")
            
        def test_copy_speed(self):
            """Test the speed of file copying"""
            print("\nTesting copy speed...")
            
            # Time the copy operation
            start_time = time.time()
            result = copyfile(self.src_path, self.dst_path, verify=True)
            elapsed = time.time() - start_time
            
            self.assertTrue(result, "Copy operation failed")
            print("Copy completed in {:.2f} seconds".format(elapsed))
            print("Copy speed: {:.2f} MB/s".format(
                self.file_size / (1024 * 1024) / elapsed if elapsed > 0 else 0
            ))
            
        def test_threaded_copy(self):
            """Test that threaded copying works"""
            print("\nTesting threaded copy...")
            
            # Test with threading
            thread = copyfile(self.src_path, self.dst_path, verify=True, run_threaded=True)
            
            # Wait for thread to complete
            thread.join(timeout=30)
            
            # Verify the copy worked
            self.assertTrue(os.path.exists(self.dst_path), "Threaded copy failed to create destination file")
            
            # Check file sizes match
            src_size = os.path.getsize(self.src_path)
            dst_size = os.path.getsize(self.dst_path)
            self.assertEqual(src_size, dst_size, "File sizes don't match in threaded copy")
            
            print("Threaded copy test successful")
    
    # Run the tests
    print("Running file copy unit tests...")
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestFileCopy))
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
    import unittest
    run_unittest()
