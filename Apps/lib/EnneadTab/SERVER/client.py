"""Client module for networking functionality.

This module provides client-side networking capabilities including:
- TCP socket client
- Server discovery
- Connection logging
- Authentication
"""

import os
import socket
import json
import logging
import platform
import uuid
import hmac
import hashlib
import datetime
import subprocess
import time

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
file_handler = logging.FileHandler(os.path.join(os.path.expanduser('~'), 'client_operations.log'))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Prevent propagation to root logger
logger.propagate = False

class SocketClient(NetworkBase):
    """TCP Socket client implementation."""
    
    def __init__(self, server_ip=None, port=None):
        """Initialize the client with network configuration."""
        super().__init__(port=port)
        self.computer_name = platform.node().upper()
        
        # Try to get server IP if not provided
        if not server_ip:
            try:
                server_ip = socket.gethostbyname("SZHANG")
                logger.info("Resolved SZHANG to {}".format(server_ip))
            except socket.gaierror:
                logger.error("Could not resolve SZHANG hostname")
                raise
                
        self.server_ip = server_ip
        logger.info("="*50)
        logger.info("Client Initialization")
        logger.info("Computer Name: {}".format(self.computer_name))
        logger.info("Target Server: {}".format(self.server_ip))
        logger.info("Port: {}".format(self.port))
        logger.info("="*50)

    def connect(self):
        """Connect to the server and handle the session."""
        logger.info("Attempting to connect to server: {}:{}".format(self.server_ip, self.port))
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.settimeout(5)  # 5 second timeout
                client.connect((self.server_ip, self.port))
                
                request = json.dumps({
                    'token': self.generate_token(),
                    'computer_name': self.computer_name
                })
                
                logger.info("Sending connection request")
                client.sendall(request.encode('ascii'))
                
                response = client.recv(1024).decode('ascii')
                response_data = json.loads(response)
                
                if response_data.get('status') == 'connected':
                    logger.info("Successfully connected to server")
                    return True
                else:
                    logger.warning("Server returned unexpected status: {}".format(response_data.get('status')))
                    return False
                
        except Exception as e:
            logger.error("Failed to connect to server: {}".format(str(e)))
            return False

def connect_to_server(server_ip=None, port=None):
    """Convenience function to connect to server."""
    client = SocketClient(server_ip, port)
    return client.connect()

if __name__ == '__main__':
    client = SocketClient()
    client.connect()
