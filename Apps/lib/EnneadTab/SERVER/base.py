"""Base networking functionality.

This module provides core networking capabilities shared between
server and client implementations including:
- Common configuration
- Logging setup
- Authentication
- Connection tracking
"""

import os
import json
import logging
import platform
import uuid
import hmac
import hashlib
import datetime
import socket

class NetworkBase:
    """Base class for network operations.
    
    Provides shared functionality for both server and client implementations:
    - Common configuration
    - Logging setup
    - Authentication
    - Connection tracking
    """
    
    # Default configuration
    DEFAULT_PORT = 12345
    DEFAULT_HOST = '0.0.0.0'
    SECRET_KEY = 'your_network_secret_key'
    
    def __init__(self, host=None, port=None):
        """Initialize base network configuration.
        
        Args:
            host (str): Host address to bind/listen on
            port (int): Port number to use
        """
        self.host = host or self.DEFAULT_HOST
        self.port = port or self.DEFAULT_PORT
        self.computer_name = platform.node().upper()
        self.fqdn = socket.getfqdn()
        self.domain = self.fqdn.split('.', 1)[1] if '.' in self.fqdn else None
        
        self._setup_logging()
        self._initialize_log()
        
        self._log_initialization()

    def _setup_logging(self):
        """Configure logging for network operations."""
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # File handler
            log_file = os.path.join(
                os.path.expanduser('~'),
                '{}_operations.log'.format(self.__class__.__name__.lower())
            )
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _initialize_log(self):
        """Initialize the connection log file."""
        self.connection_log_path = os.path.join(
            os.path.expanduser('~'),
            '{}_connection_log.json'.format(self.__class__.__name__.lower())
        )
        
        if not os.path.exists(self.connection_log_path):
            self.logger.info("Creating new connection log at: {}".format(self.connection_log_path))
            with open(self.connection_log_path, 'w') as f:
                json.dump([], f)
        else:
            self.logger.debug("Connection log already exists")

    def _log_initialization(self):
        """Log initialization details."""
        self.logger.info("="*50)
        self.logger.info("{} Initialization".format(self.__class__.__name__))
        self.logger.info("Computer Name: {}".format(self.computer_name))
        self.logger.info("FQDN: {}".format(self.fqdn))
        self.logger.info("Domain: {}".format(self.domain))
        self.logger.info("Host: {}".format(self.host))
        self.logger.info("Port: {}".format(self.port))
        self.logger.info("="*50)

    def generate_token(self):
        """Generate a secure authentication token."""
        token = hmac.new(
            self.SECRET_KEY.encode('utf-8'),
            msg=str(uuid.uuid4()).encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        return token

    def log_connection(self, remote_address, success=True):
        """Log connection attempt details.
        
        Args:
            remote_address (str): Remote host address
            success (bool): Whether connection was successful
        """
        try:
            self.logger.info("Connection {}: {}".format(
                "from" if isinstance(self, SocketServer) else "to",
                remote_address
            ))
            self.logger.info("Status: {}".format("SUCCESS" if success else "FAILED"))
            
            with open(self.connection_log_path, 'r') as f:
                logs = json.load(f)
            
            logs.append({
                'timestamp': datetime.datetime.now().isoformat(),
                'remote_address': remote_address,
                'success': success
            })
            
            with open(self.connection_log_path, 'w') as f:
                json.dump(logs, f, indent=2)
            
        except Exception as e:
            self.logger.error("Failed to log connection: {}".format(str(e))) 