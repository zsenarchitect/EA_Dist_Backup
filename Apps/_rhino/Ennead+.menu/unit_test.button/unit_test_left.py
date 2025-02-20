__title__ = "UnitTest"
__doc__ = """Execute unit tests for EnneadTab components.

Key Features:
- Comprehensive module testing
- Automated error detection
- System integrity verification
- Performance validation
- Debug report generation"""


from EnneadTab import ERROR_HANDLE, LOG, UNIT_TEST
@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def unit_test():
    UNIT_TEST.test_core_module()
    

    
if __name__ == "__main__":
    unit_test()
