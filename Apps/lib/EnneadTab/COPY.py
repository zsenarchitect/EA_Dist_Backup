"""
The main purpose of this moudle to is to handle Rhino 8 situation. 
Native shutil.copyfile will fail in some cases, so we use dotnet to copy the file.
This module also ensures that large files are completely copied before returning.

"""

import shutil
import os
import time




def copyfile(src, dst, include_metadata=True, verify=True, timeout=120):
    """
    Copy a file from source to destination with verification to ensure complete copy.
    
    Args:
        src: Source file path
        dst: Destination file path
        include_metadata: Whether to include file metadata in the copy
        verify: Whether to verify the file is completely copied
        timeout: Maximum time in seconds to wait for copy verification
    
    Returns:
        bool: True if copy was successful, False otherwise
    """
    try:
        return copyfile_with_cpy(src, dst, include_metadata, verify, timeout)
    except Exception as e:
        # print("Standard copy failed, trying dotnet method:", e)
        return copyfile_with_dotnet(src, dst, verify, timeout)


def copyfile_with_cpy(src, dst, include_metadata=True, verify=True, timeout=120):
    """
    Copy a file from source to destination with verification to ensure complete copy.
    
    Args:
        src: Source file path
        dst: Destination file path
    """
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
    
def copyfile_with_dotnet(src, dst, verify=True, timeout=120):
    """
    Copy a file using dotnet with verification to ensure complete copy.
    
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
            import os
            src_size = os.path.getsize(src)
        except:
            from System.IO import FileInfo  # pyright: ignore
            src_size = FileInfo(src).Length
    
    # Perform copy using dotnet
    from System.IO import File  # pyright: ignore
    File.Copy(src, dst, True)  # True to overwrite if exists
    
    # Verify the copy is complete for large files
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
    
    # Run the tests
    print("Running file copy unit tests...")
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestFileCopy))
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
    import unittest
    run_unittest()
