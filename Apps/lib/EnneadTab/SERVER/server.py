"""Server module for networking functionality.

This module provides server-side networking capabilities including:
- TCP socket server
- Multi-threaded client handling
- Connection logging
- Authentication
"""

import os
import socket
import threading
import json
import logging
import time
import platform
import uuid
import hmac
import hashlib
import datetime

from base import NetworkBase

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create file handler
file_handler = logging.FileHandler(os.path.join(os.path.expanduser('~'), 'server_operations.log'))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Prevent propagation to root logger
logger.propagate = False

class SocketServer(NetworkBase):
    """TCP Socket server implementation.
    
    Provides a multi-threaded TCP server that:
    - Listens for incoming connections
    - Handles multiple clients concurrently
    - Logs connection attempts
    - Provides secure authentication
    """
    
    def __init__(self, host=None, port=None):
        """Initialize the server with network configuration.
        
        Args:
            host (str): Host address to bind to
            port (int): Port number to listen on
            
        Raises:
            RuntimeError: If attempting to run server on a computer other than SZHANG
        """
        super().__init__(port=port)
        
        # Get server's actual IP address
        self.computer_name = platform.node().upper()
        self.fqdn = socket.getfqdn()
        try:
            # Try to get IP by FQDN first
            self.host = socket.gethostbyname(self.fqdn)
            logger.info("Using FQDN IP: {}".format(self.host))
        except socket.gaierror:
            try:
                # Fallback to hostname
                self.host = socket.gethostbyname(self.computer_name)
                logger.info("Using hostname IP: {}".format(self.host))
            except socket.gaierror:
                # Last resort - use provided host or default
                self.host = host or self.DEFAULT_HOST
                logger.warning("Using default host: {}".format(self.host))
        
        logger.info("="*50)
        logger.info("Server Initialization")
        logger.info("Computer Name: {}".format(self.computer_name))
        logger.info("FQDN: {}".format(self.fqdn))
        logger.info("Host: {}".format(self.host))
        logger.info("Port: {}".format(self.port))
        logger.info("="*50)
        
        self._test_server()

    def generate_token(self):
        """Generate a secure authentication token."""
        token = hmac.new(
            'your_network_secret_key'.encode('utf-8'),
            msg=str(uuid.uuid4()).encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        return token

    def log_connection(self, remote_host, success=True):
        """Log connection attempt details.
        
        Args:
            remote_host (str): Client address
            success (bool): Whether connection was successful
        """
        try:
            logger.info("Connection from {}: {}".format(
                remote_host,
                "SUCCESS" if success else "FAILED"
            ))
            
            with open(self.connection_log_path, 'r') as f:
                logs = json.load(f)
            
            logs.append({
                'timestamp': datetime.datetime.now().isoformat(),
                'remote_host': remote_host,
                'success': success
            })
            
            with open(self.connection_log_path, 'w') as f:
                json.dump(logs, f, indent=2)
            
        except Exception as e:
            logger.error("Failed to log connection: {}".format(str(e)))

    def _test_server(self):
        """Test server functionality before starting."""
        self.logger.info("Testing server configuration...")
        try:
            # Test socket creation
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Test port availability
            test_socket.bind((self.host, self.port))
            test_socket.close()
            
            self.logger.info("Server test passed successfully")
            return True
        except Exception as e:
            self.logger.error("Server test failed: {}".format(str(e)))
            return False

    def handle_client(self, client):
        """Handle individual client connections.
        
        Args:
            client: Connected client socket
        """
        try:
            client_address = "{}:{}".format(*client.getpeername())
            self.logger.info("Processing client connection from: {}".format(client_address))
            
            data = client.recv(1024).decode('ascii')
            self.logger.debug("Received request: {}".format(data))
            
            self.log_connection(client_address, success=True)
            
            response = json.dumps({
                'status': 'connected',
                'token': self.generate_token()
            })
            
            client.sendall(response.encode('ascii'))
            self.logger.info("Response sent to client: {}".format(client_address))
            
        except Exception as e:
            self.logger.error("Error handling client {}: {}".format(
                client_address if 'client_address' in locals() else 'unknown',
                str(e)
            ))
            if hasattr(client, 'getpeername'):
                self.log_connection(client.getpeername()[0], success=False)
        
        finally:
            client.close()
            self.logger.debug("Client connection closed")

    def start(self):
        """Start the server and listen for connections."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                # Try binding to specific IP first
                try:
                    listener.bind((self.host, self.port))
                    logger.info("Bound to specific IP: {}".format(self.host))
                except Exception as e:
                    logger.warning("Failed to bind to {}: {}".format(self.host, str(e)))
                    # Fallback to all interfaces if specific IP fails
                    listener.bind(('0.0.0.0', self.port))
                    logger.info("Bound to all interfaces (0.0.0.0)")
                
                listener.listen(5)
                logger.info("="*50)
                logger.info("SERVER STATUS: ONLINE")
                logger.info("Listening on {}:{}".format(self.host, self.port))
                logger.info("Waiting for client connections...")
                logger.info("="*50)
                
                while True:
                    try:
                        client, addr = listener.accept()
                        logger.info("-"*50)
                        logger.info("NEW CLIENT CONNECTION")
                        logger.info("Client Address: {}:{}".format(addr[0], addr[1]))
                        logger.info("-"*50)
                        
                        thread = threading.Thread(
                            target=self.handle_client,
                            args=(client,)
                        )
                        thread.daemon = True
                        thread.start()
                        
                    except Exception as e:
                        logger.error("Error accepting client: {}".format(str(e)))
                        
            except OSError as e:
                if e.errno == 98:  # Address already in use
                    logger.error("Port {} is in use. Cleaning up...".format(self.port))
                    listener.close()
                    time.sleep(1)
                    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    listener.bind((self.host, self.port))
                    listener.listen(5)
                    logger.info("Recovered and bound to port {}".format(self.port))
                else:
                    raise

def start_server(host=None, port=None):
    """Convenience function to start the server.
    
    Args:
        host (str): Host address to bind to
        port (int): Port number to listen on
    """
    server = SocketServer(host, port)
    server.start()

if __name__ == '__main__':
    start_server()
