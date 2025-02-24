import requests
import socket
import os
import math
from typing import Dict, Tuple

def calculate_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.
    Returns distance in kilometers.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    R = 6371  # Earth's radius in kilometers

    # Convert latitude and longitude to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def get_physical_location() -> Dict[str, str]:
    """
    Get the physical location of the current computer using IP-based geolocation.
    Returns a dictionary containing location information.
    """
    try:
        # Get the local machine's IP address
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Try primary API (ipapi.co with API key - more reliable but requires signup)
        response = requests.get('https://ipapi.co/json/')
        
        # If primary API fails, try backup API (ip-api.com)
        if response.status_code != 200:
            response = requests.get('http://ip-api.com/json/')
        
        if response.status_code == 200:
            location_data = response.json()
            
            # Handle different API response formats
            if 'lat' in location_data:  # ip-api.com format
                return {
                    'city': location_data.get('city', 'Unknown'),
                    'region': location_data.get('regionName', 'Unknown'),
                    'country': location_data.get('country', 'Unknown'),
                    'latitude': str(location_data.get('lat', 'Unknown')),
                    'longitude': str(location_data.get('lon', 'Unknown')),
                    'ip': location_data.get('query', local_ip)
                }
            else:  # ipapi.co format
                return {
                    'city': location_data.get('city', 'Unknown'),
                    'region': location_data.get('region', 'Unknown'),
                    'country': location_data.get('country_name', 'Unknown'),
                    'latitude': str(location_data.get('latitude', 'Unknown')),
                    'longitude': str(location_data.get('longitude', 'Unknown')),
                    'ip': location_data.get('ip', local_ip)
                }
        else:
            return {
                'error': f'API requests failed with status code: {response.status_code}',
                'ip': local_ip
            }
    except Exception as e:
        return {
            'error': f'Failed to get location: {str(e)}',
            'ip': local_ip
        }

if __name__ == '__main__':
    location = get_physical_location()
    print("Current Computer Location:")
    for key, value in location.items():
        print(f"{key.capitalize()}: {value}")
    
    # Check if location is near any office
    OFFICE_COORDS = [
        (40.71294262082848, -74.01295663511299),  # New York
        (31.210880235016344, 121.47085755700422),  # Shanghai
        (34.05050553174108, -118.24774866805332)   # Los Angeles
    ]
    OFFICE_NAMES = ["New York", "Shanghai", "Los Angeles"]
    DISTANCE_THRESHOLD = 1.0  # 1.0 kilometers

    if 'latitude' in location and 'longitude' in location and 'error' not in location:
        try:
            current_coords = (float(location['latitude']), float(location['longitude']))
            
            # Calculate distance to each office
            distances = []
            for office_coords in OFFICE_COORDS:
                distance = calculate_distance(current_coords, office_coords)
                distances.append(distance)
            
            # Check if near any office
            is_near_any_office = any(d <= DISTANCE_THRESHOLD for d in distances)
            os.environ['IS_NEAR_OFFICE'] = str(is_near_any_office)
            
            # Print distances to all offices
            print("\nDistances to offices:")
            for office_name, distance in zip(OFFICE_NAMES, distances):
                print(f"{office_name}: {distance:.2f} km")
            print(f"\nIS_NEAR_OFFICE environment variable set to: {is_near_any_office}")

        except ValueError as e:
            print(f"Error calculating distance: {e}")
            os.environ['IS_NEAR_OFFICE'] = 'False'
    else:
        print("\nCould not determine location accurately")
        os.environ['IS_NEAR_OFFICE'] = 'False'
