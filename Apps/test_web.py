import sys
import os
import socket
import argparse

# Add the Apps directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.EnneadTab import WEB

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', action='store_true', help='Run in server mode')
    args = parser.parse_args()

    if args.server:
        print("Starting server mode...")
        WEB.start_server()
        return

    # Client mode
    current_fqdn = socket.getfqdn()
    print("Current computer's full address: {}".format(current_fqdn))
    
    domain = current_fqdn.split('.', 1)[1] if '.' in current_fqdn else None
    server_address = "SZHANG.{}".format(domain) if domain else "SZHANG"
    print("Attempting to connect to server at: {}".format(server_address))
    
    # Try to connect
    WEB.call_me(server_ip=server_address)

if __name__ == "__main__":
    main() 