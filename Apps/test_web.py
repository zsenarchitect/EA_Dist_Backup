import os
import sys
import socket

# Add the Apps directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.EnneadTab import WEB

def check_server_status(host, port):
    """Check if server is reachable and port is open."""
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 second timeout
        
        # Try to connect
        result = sock.connect_ex((host, port))
        if result == 0:
            print(f"Server {host}:{port} is reachable and port is open")
        else:
            print(f"Server {host}:{port} is reachable but port is closed")
        
        sock.close()
    except socket.error as e:
        print(f"Error checking server status: {e}")

def main():
    # Get current computer's full address
    current_fqdn = socket.getfqdn()
    print(f"Current computer's full address: {current_fqdn}")
    
    # Extract domain and construct server address
    domain = current_fqdn.split('.', 1)[1] if '.' in current_fqdn else None
    server_address = f"SZHANG.{domain}" if domain else "SZHANG"
    print(f"Attempting to connect to server at: {server_address}")
    
    # Check server status before attempting connection
    check_server_status(server_address, 12345)
    
    # Try to connect
    WEB.call_me(server_ip=server_address)

if __name__ == "__main__":
    main() 