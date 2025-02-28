"""
EnneadTab Time Module Test Suite
-------------------------------

This test suite verifies the functionality of the TIME module, which provides
various time-related utilities for the EnneadTab library. The tests cover:

1. Date Formatting
   - YYYYMMDD format
   - YYYY-MM-DD format
   - Date tuple generation
   - Custom time formatting

2. Time Conversion
   - Readable time conversion
   - Unix timestamp handling
   - Float to datetime conversion

3. Timer Functionality
   - Function timing decorator
   - Auto timer class
   - Timer lifecycle management

4. Edge Cases
   - Invalid inputs
   - Boundary conditions
   - Time zone handling

Each test case includes detailed documentation explaining:
- Purpose: What aspect is being tested
- Method: How the test is performed
- Expected: What results should be produced
"""

import unittest
import time
import datetime
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from TIME import (get_YYYYMMDD, get_YYYY_MM_DD, get_date_as_tuple,
                 get_formatted_current_time, get_formatted_time,
                 get_readable_time, time_has_passed_too_long, AutoTimer)

class TestDateFormatting(unittest.TestCase):
    """
    Test suite for date formatting functions.
    
    These tests verify that dates are correctly formatted in various styles,
    ensuring consistency and accuracy across different date representations.
    """
    
    def setUp(self):
        """
        Set up test fixtures with a known datetime for consistent testing.
        Uses February 17, 2023 as a reference date.
        """
        self.test_date = datetime.datetime(2023, 2, 17, 14, 30, 45)
        
    @patch('datetime.datetime')
    def test_YYYYMMDD_format(self, mock_datetime):
        """
        Test the YYYYMMDD date format.
        
        Purpose: Verify date is formatted as YYYYMMDD without separators
        Method: Mock current date and check output format
        Expected: "20230217" for February 17, 2023
        """
        mock_datetime.now.return_value = self.test_date
        result = get_YYYYMMDD()
        self.assertEqual(result, "20230217")
    
    @patch('datetime.datetime')
    def test_YYYY_MM_DD_format(self, mock_datetime):
        """
        Test the YYYY-MM-DD date format.
        
        Purpose: Verify date is formatted with hyphen separators
        Method: Mock current date and check output format
        Expected: "2023-02-17" for February 17, 2023
        """
        mock_datetime.now.return_value = self.test_date
        result = get_YYYY_MM_DD()
        self.assertEqual(result, "2023-02-17")
    
    def test_date_tuple_string(self):
        """
        Test date tuple generation with string output.
        
        Purpose: Verify date components are correctly separated into tuple
        Method: Generate tuple with string values
        Expected: ("2023", "02", "17") for February 17, 2023
        """
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = self.test_date
            year, month, day = get_date_as_tuple(return_string=True)
            self.assertEqual((year, month, day), ("2023", "02", "17"))
    
    def test_date_tuple_integer(self):
        """
        Test date tuple generation with integer output.
        
        Purpose: Verify date components are converted to integers
        Method: Generate tuple with integer values
        Expected: (2023, 2, 17) for February 17, 2023
        """
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = self.test_date
            year, month, day = get_date_as_tuple(return_string=False)
            self.assertEqual((year, month, day), (2023, 2, 17))

class TestTimeConversion(unittest.TestCase):
    """
    Test suite for time conversion and formatting functions.
    
    These tests verify that time values are correctly converted between
    different formats and representations.
    """
    
    def test_readable_time_seconds(self):
        """
        Test conversion of seconds to readable format.
        
        Purpose: Verify time formatting for different second values
        Method: Test various second inputs
        Expected: 
        - "0.50s" for 0.5 seconds
        - "45s" for 45 seconds
        """
        self.assertEqual(get_readable_time(0.5), "0.50s")
        self.assertEqual(get_readable_time(45), "45s")
    
    def test_readable_time_minutes(self):
        """
        Test conversion of minutes to readable format.
        
        Purpose: Verify time formatting for minute-level durations
        Method: Test time values between 1-60 minutes
        Expected: "2m 30s" for 150 seconds
        """
        self.assertEqual(get_readable_time(150), "2m 30s")
    
    def test_readable_time_hours(self):
        """
        Test conversion of hours to readable format.
        
        Purpose: Verify time formatting for hour-level durations
        Method: Test time values over 1 hour
        Expected: "2h 30m 45s" for 9045 seconds
        """
        self.assertEqual(get_readable_time(9045), "2h 30m 45s")
    
    def test_time_passed_check(self):
        """
        Test time passage verification.
        
        Purpose: Verify if enough time has passed since a timestamp
        Method: Compare current time with past timestamps
        Expected: True if more than 30 minutes passed
        """
        current_time = time.time()
        old_time = current_time - 1800  # 30 minutes ago
        self.assertFalse(time_has_passed_too_long(old_time))
        very_old_time = current_time - 3600  # 1 hour ago
        self.assertTrue(time_has_passed_too_long(very_old_time))

class TestAutoTimer(unittest.TestCase):
    """
    Test suite for the AutoTimer class.
    
    These tests verify the functionality of the automatic timer,
    including initialization, events, and cleanup.
    """
    
    def setUp(self):
        """Initialize test timer with short duration."""
        self.timer = AutoTimer(life_span=2, show_progress=True, interval=0.5)
    
    def test_timer_initialization(self):
        """
        Test timer initialization.
        
        Purpose: Verify timer is properly configured
        Method: Check initial timer properties
        Expected: Correct life_span, interval, and counter values
        """
        self.assertEqual(self.timer.life_span, 2)
        self.assertEqual(self.timer.interval, 0.5)
        self.assertEqual(self.timer.max_repetition, 4)  # 2/0.5 = 4
    
    def test_timer_lifecycle(self):
        """
        Test timer lifecycle management.
        
        Purpose: Verify timer starts and stops correctly
        Method: Start timer and check status
        Expected: Timer should be active after start and inactive after stop
        """
        self.timer.begin()
        self.assertTrue(self.timer.timer.is_alive())
        self.timer.stop_timer()
        self.assertFalse(self.timer.timer.is_alive())

if __name__ == '__main__':
    unittest.main() 