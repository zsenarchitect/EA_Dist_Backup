"""Test script to verify module auto-installation functionality in ENGINE.py.

This script intentionally imports modules that might not be pre-installed in the
Python embeddable package, triggering the auto-installation mechanism.
"""

print("Starting module test script...")

print("Testing standard library imports...")
import os
import sys
import datetime
print("Standard library imports successful!")

print("\nTesting requests module (requires installation if not present)...")
import requests
print("Requests module imported successfully!")
print("Requests version:", requests.__version__)

print("\nTesting simple HTTP request...")
response = requests.get("https://www.google.com")
print("HTTP request status code:", response.status_code)

print("\nAll tests completed successfully!") 