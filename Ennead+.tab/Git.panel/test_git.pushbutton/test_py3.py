

from EnneadTab import ENVIRONMENT_CONSTANTS
import sys

sys.path.insert(0, ENVIRONMENT_CONSTANTS.DEPENDENCY_FOLDER_PY3)


import requests

def fetch_data(url):
    try:
        # Perform a GET request to the specified URL
        response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            print("Request was successful!")
            # Print the response data in JSON format
            print("Response data:")
            print(response.json())
        else:
            print(f"Request failed with status code: {response.status_code}")
    except requests.RequestException as e:
        # Handle any exceptions that occur during the request
        print(f"An error occurred: {e}")

def main():
    # URL of a public API that returns JSON data
    url = "https://jsonplaceholder.typicode.com/posts/1"
    
    # Fetch data from the API
    fetch_data(url)

if __name__ == '__main__':
    main()
