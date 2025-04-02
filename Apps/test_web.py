import socket
import argparse
import threading
import json
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def server_listener(host='0.0.0.0', port=12345):
    """Server mode: Listen for incoming connections."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind((host, port))
        listener.listen()
        logger.info("="*50)
        logger.info("SERVER STATUS: ONLINE")
        logger.info("Listening on {}:{}".format(host, port))
        logger.info("Waiting for client connections...")
        logger.info("="*50)
        
        while True:
            try:
                client, addr = listener.accept()
                logger.info("-"*50)
                logger.info("NEW CLIENT CONNECTION")
                logger.info("Client Address: {}:{}".format(addr[0], addr[1]))
                logger.info("-"*50)
                
                # Handle client in a new thread
                thread = threading.Thread(
                    target=handle_client,
                    args=(client,)
                )
                thread.start()
            except Exception as e:
                logger.error("Server error: {}".format(str(e)))

def handle_client(client):
    """Handle individual client connections."""
    try:
        client_address = "{}:{}".format(*client.getpeername())
        logger.info("Processing client connection from: {}".format(client_address))
        
        data = client.recv(1024).decode('ascii')
        logger.info("Received request: {}".format(data))
        
        response = json.dumps({
            'status': 'connected',
            'message': 'Hello from server!'
        })
        
        client.sendall(response.encode('ascii'))
        logger.info("Response sent to client: {}".format(client_address))
    
    except Exception as e:
        logger.error("Error handling client {}: {}".format(
            client_address if 'client_address' in locals() else 'unknown',
            str(e)
        ))
    
    finally:
        client.close()
        logger.debug("Client connection closed")

def client_connection(server_ip, port=12345):
    """Client mode: Connect to server."""
    try:
        logger.info("Attempting to connect to server: {}:{}".format(server_ip, port))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((server_ip, port))
            
            request = json.dumps({
                'message': 'Hello from client!'
            })
            
            logger.info("Sending request to server")
            client.sendall(request.encode('ascii'))
            
            response = client.recv(1024).decode('ascii')
            logger.info("Server response: {}".format(response))
            
    except Exception as e:
        logger.error("Failed to connect to server: {}".format(str(e)))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', action='store_true', help='Run in server mode')
    args = parser.parse_args()

    if args.server:
        # Get the machine's IP address
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        print("Starting server mode...")
        print("Server hostname: {}".format(hostname))
        print("Server IP: {}".format(ip_address))
        server_listener(host=ip_address)
        return

    # Client mode
    current_fqdn = socket.getfqdn()
    print("Current computer's full address: {}".format(current_fqdn))
    
    # Try both FQDN and IP resolution
    try:
        server_ip = socket.gethostbyname("SZHANG.ad.ennead.com")
        print("Resolved server IP: {}".format(server_ip))
    except socket.gaierror:
        print("Could not resolve SZHANG.ad.ennead.com, trying SZHANG...")
        try:
            server_ip = socket.gethostbyname("SZHANG")
            print("Resolved server IP: {}".format(server_ip))
        except socket.gaierror:
            print("Could not resolve SZHANG either. Check DNS resolution.")
            return
    
    # Try to connect
    client_connection(server_ip)

if __name__ == "__main__":
    main() 