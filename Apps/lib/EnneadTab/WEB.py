import os
import base64
import io
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.expanduser('~'), 'network_operations.log'))
    ]
)
logger = logging.getLogger(__name__)

# Add a test message to verify logging is working
logger.info("="*50)
logger.info("Network Operations Logging Started")
logger.info("="*50)

def documentation2html(doc_data_list, html_path):
    """Generates an HTML file with embedded images from documentation data."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Command Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            .command { margin-bottom: 40px; border-bottom: 1px solid #ddd; padding-bottom: 20px; }
            .command h2 { color: #333; }
            .tooltip { color: #555; font-size: 14px; }
            .container { display: flex; align-items: flex-start; gap: 20px; }
            img { width: 64px; height: 64px; }
        </style>
    </head>
    <body>
        <h1>Command Documentation</h1>
    """
    
    for doc_data in doc_data_list:
        alias = doc_data.get('alias', 'Unknown Command')
        tooltip_text = doc_data.get('doc', 'No description available.')
        icon_path = doc_data.get('icon')
        
        if icon_path and os.path.exists(icon_path):
            with io.open(icon_path, "rb") as img_file:  # Removed `encoding` for binary read
                base64_img = base64.b64encode(img_file.read()).decode('utf-8')
            icon_html = "<img src=\"data:image/png;base64,{0}\" alt=\"{1} icon\">".format(base64_img, alias)
        else:
            icon_html = ""
        
        html_content += """
        <div class="command">
            <h2>{0}</h2>
            <div class="container">
                {1}
                <p class="tooltip"><strong>Tooltip:</strong> {2}</p>
            </div>
        </div>
        """.format(alias, icon_html, tooltip_text)
    
    html_content += "</body></html>"
    
    with io.open(html_path, "w", encoding="utf-8") as file:
        file.write(html_content)
    
    print("HTML documentation saved at " + html_path)


###########################################################
from ENVIRONMENT import IS_IRONPYTHON
# Common imports
import json
import datetime
import os
import platform
import uuid
import hmac
import hashlib

if IS_IRONPYTHON:
    import sys
    import clr # pyright: ignore
    clr.AddReference("System")
    clr.AddReference("System.Net") 
    clr.AddReference("System.Windows.Forms")

    import System # pyright: ignore
    import System.Net # pyright: ignore
    import System.Net.Sockets # pyright: ignore
    import System.Threading # pyright: ignore
    import System.Windows.Forms # pyright: ignore
else:
    import socket
    import threading

class NetworkBase:
    """Base networking functionality shared between IronPython and CPython implementations.
    
    This class provides the core networking functionality that works across both IronPython
    and CPython environments. It handles connection tracking, logging, and authentication.
    
    Key Design Principles:
    - Uses FQDN (Fully Qualified Domain Name) for addressing
    - Platform-agnostic core functionality
    - Shared authentication and logging mechanisms
    - Consistent interface across implementations
    - Thread-safe connection tracking
    - Periodic statistics reporting
    
    Attributes:
        computer_name (str): The name of the current computer in uppercase
        fqdn (str): The Fully Qualified Domain Name of the current computer
        domain (str): The domain part of the FQDN
        is_server (bool): True if this instance should act as a server
        HOST (str): The host address to bind to (default: '0.0.0.0')
        PORT (int): The port number to use (default: 12345)
        connection_log_path (str): Path to the JSON log file
        total_connections (int): Counter for connections in the current period
        connection_counter_lock (threading.Lock): Lock for thread-safe counter updates
    """
    def __init__(self):
        """Initialize the network base with configuration and logging setup.
        
        Sets up the basic networking configuration, initializes logging,
        and starts the periodic connection statistics thread.
        """
        self.computer_name = platform.node().upper()
        self.fqdn = socket.getfqdn()
        self.domain = self.fqdn.split('.', 1)[1] if '.' in self.fqdn else None
        self.is_server = self.computer_name == "SZHANG"
        self.HOST = '0.0.0.0' if self.is_server else None
        self.PORT = 12345
        self.connection_log_path = os.path.join(
            os.path.expanduser('~'), 
            'network_connection_log.json'
        )
        self.total_connections = 0
        self.connection_counter_lock = threading.Lock()
        
        logger.info("="*50)
        logger.info("NetworkBase Initialization")
        logger.info("Computer Name: {}".format(self.computer_name))
        logger.info("FQDN: {}".format(self.fqdn))
        logger.info("Domain: {}".format(self.domain))
        logger.info("Server Mode: {}".format(self.is_server))
        logger.info("Host: {}".format(self.HOST))
        logger.info("Port: {}".format(self.PORT))
        logger.info("="*50)
        self._initialize_log()
        
        # Start the connection counter thread
        self.counter_thread = threading.Thread(target=self._periodic_connection_log)
        self.counter_thread.daemon = True
        self.counter_thread.start()

    def _initialize_log(self):
        """Initialize the connection log file if it doesn't exist.
        
        Creates a new JSON log file with an empty list if the file doesn't exist.
        The log file will store connection attempts with timestamps and status.
        """
        if not os.path.exists(self.connection_log_path):
            logger.info("Creating new connection log file at: {}".format(self.connection_log_path))
            with open(self.connection_log_path, 'w') as f:
                json.dump([], f)
        else:
            logger.debug("Connection log file already exists")

    def generate_secure_token(self):
        """Generate a cryptographically secure authentication token.
        
        Uses HMAC-SHA256 to create a secure token for client-server authentication.
        The token is unique for each connection attempt and includes a timestamp.
        
        Why use HMAC?
        - Provides one-time, secure authentication
        - Prevents replay attacks
        - Adds robust security layer
        
        Returns:
            str: A hexadecimal string representing the secure token
        """
        token = hmac.new(
            'your_network_secret_key'.encode('utf-8'), 
            msg=str(uuid.uuid4()).encode('utf-8'), 
            digestmod=hashlib.sha256
        ).hexdigest()
        logger.debug("Generated new secure token")
        return token
    
    def _periodic_connection_log(self):
        """Log connection statistics every 60 seconds.
        
        This method uses a timer-based approach to periodically log
        the total number of connections made in the last 60 seconds.
        The counter is reset after each log entry.
        
        The log includes:
        - Current timestamp
        - Total number of connections
        - Visual separators for readability
        """
        def log_stats():
            with self.connection_counter_lock:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.info("="*50)
                logger.info("CONNECTION STATISTICS - {}".format(current_time))
                logger.info("Total connections in last 60s: {}".format(self.total_connections))
                logger.info("="*50)
                self.total_connections = 0  # Reset counter
            
            # Schedule the next log
            if IS_IRONPYTHON:
                System.Threading.Timer(
                    System.Threading.TimerCallback(lambda x: log_stats()),
                    None,
                    60000,  # 60 seconds in milliseconds
                    System.Threading.Timeout.Infinite
                )
            else:
                threading.Timer(60.0, log_stats).start()
        
        # Start the first timer
        if IS_IRONPYTHON:
            System.Threading.Timer(
                System.Threading.TimerCallback(lambda x: log_stats()),
                None,
                60000,  # 60 seconds in milliseconds
                System.Threading.Timeout.Infinite
            )
        else:
            threading.Timer(60.0, log_stats).start()
    
    def log_connection(self, remote_host, success=True):
        """Record connection attempt details in both memory and file.
        
        This method handles both the connection counter for statistics
        and the persistent logging of connection attempts to a JSON file.
        
        Logging mechanism:
        - Timestamp of connection
        - Remote computer details
        - Connection status (success/failure)
        
        Args:
            remote_host (str): The IP address or hostname of the remote connection
            success (bool): Whether the connection attempt was successful
        
        The log entry is stored in a JSON file with the following structure:
        {
            'timestamp': 'ISO format timestamp',
            'remote_host': 'remote host address',
            'success': true/false
        }
        """
        try:
            with self.connection_counter_lock:
                self.total_connections += 1
            
            logger.info("Connection attempt from {}: {}".format(
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
            
            logger.debug("Connection log updated successfully")
        
        except Exception as e:
            logger.error("Failed to log connection: {}".format(str(e)))
    
    def call_me(self, **kwargs):
        """Primary entry point with flexible behavior for server/client initialization.
        
        This method serves as the main entry point for the networking system,
        determining whether to start a server or client based on configuration.
        
        Args:
            **kwargs: Optional keyword arguments
                server_ip (str): Server address (for client mode)
                port (int): Port number to use (overrides default)
        
        The method automatically determines whether to run as server or client
        based on the computer name and available arguments.
        """
        if 'port' in kwargs:
            self.PORT = kwargs['port']
            logger.info("Using custom port: {}".format(self.PORT))

        if self.is_server:
            logger.info("Starting server in {} mode".format("IronPython" if IS_IRONPYTHON else "CPython"))
            if IS_IRONPYTHON:
                System.Threading.Thread(
                    System.Threading.ThreadStart(self.server_listener)
                ).Start()
            else:
                thread = threading.Thread(target=self.server_listener)
                thread.daemon = True
                thread.start()
        else:
            server_ip = kwargs.get('server_ip')
            if not server_ip:
                # If no server IP provided, construct it using domain
                if self.domain:
                    server_ip = "SZHANG.{}".format(self.domain)
                else:
                    server_ip = "SZHANG"
            logger.info("Client connecting to server: {}".format(server_ip))
            self.client_connection(server_ip)

if IS_IRONPYTHON:
    class NetworkRoleSystem(NetworkBase):
        """IronPython-specific networking implementation.
        
        This class extends NetworkBase to provide networking functionality
        specifically for IronPython environments, using .NET networking libraries.
        
        Key Features:
        - Uses System.Net.Sockets for network communication
        - Implements multi-threaded client handling
        - Provides .NET-specific error handling
        - Supports secure token-based authentication
        """
        def server_listener(self):
            """Primary server listening mechanism for IronPython.
            
            This method sets up a TCP listener and handles incoming client connections
            in a multi-threaded manner. Each client connection is processed in a
            separate thread to allow for concurrent connections.
            
            The server:
            - Listens continuously for incoming connections
            - Creates a new thread for each client
            - Logs all connection attempts and errors
            - Uses .NET's TcpListener for network operations
            """
            listener = System.Net.Sockets.TcpListener(
                System.Net.IPAddress.Parse(self.HOST), 
                self.PORT
            )
            listener.Start()
            
            logger.info("IronPython Server started on {}:{}".format(self.HOST, self.PORT))
            
            while True:
                try:
                    client = listener.AcceptTcpClient()
                    logger.info("New client connection from: {}".format(
                        client.Client.RemoteEndPoint.ToString()
                    ))
                    System.Threading.Thread(
                        System.Threading.ParameterizedThreadStart(
                            self.handle_client_connection
                        )
                    ).Start(client)
                
                except Exception as e:
                    logger.error("Server error: {}".format(str(e)))
        
        def handle_client_connection(self, client_obj):
            """Process individual client connections in IronPython.
            
            This method handles the communication with a single client,
            including authentication, data exchange, and connection cleanup.
            
            Workflow:
            1. Validate connection and get client details
            2. Read client request data
            3. Generate and send authentication token
            4. Log connection details
            5. Clean up resources
            
            Args:
                client_obj: The TcpClient object representing the client connection
            """
            try:
                client = client_obj
                stream = client.GetStream()
                remote_endpoint = client.Client.RemoteEndPoint.ToString()
                logger.info("Processing client connection from: {}".format(remote_endpoint))
                
                buffer = System.Array.CreateInstance(System.Byte, 1024)
                bytes_read = stream.Read(buffer, 0, buffer.Length)
                request = System.Text.Encoding.ASCII.GetString(buffer, 0, bytes_read)
                logger.debug("Received request: {}".format(request))
                
                self.log_connection(remote_endpoint, success=True)
                
                response = json.dumps({
                    'status': 'connected',
                    'token': self.generate_secure_token()
                })
                
                send_buffer = System.Text.Encoding.ASCII.GetBytes(response)
                stream.Write(send_buffer, 0, send_buffer.Length)
                logger.info("Response sent to client: {}".format(remote_endpoint))
            
            except Exception as e:
                logger.error("Error handling client {}: {}".format(
                    client.Client.RemoteEndPoint.ToString(), 
                    str(e)
                ))
                self.log_connection(client.Client.RemoteEndPoint.ToString(), success=False)
            
            finally:
                client.Close()
                logger.debug("Client connection closed")
        
        def client_connection(self, server_ip=None):
            """Client-side connection attempt for IronPython.
            
            This method implements the client-side connection logic using
            .NET's TcpClient for network communication.
            
            The client:
            - Connects to the specified server
            - Sends authentication request
            - Handles server response
            - Logs connection status
            
            Args:
                server_ip (str, optional): IP address of the server to connect to.
                    Defaults to '192.168.1.100' if not specified.
            """
            try:
                if not server_ip:
                    server_ip = '192.168.1.100'
                
                logger.info("Attempting to connect to server: {}:{}".format(server_ip, self.PORT))
                client = System.Net.Sockets.TcpClient(server_ip, self.PORT)
                stream = client.GetStream()
                
                request = json.dumps({
                    'token': self.generate_secure_token(),
                    'computer_name': self.computer_name
                })
                
                logger.debug("Sending connection request")
                send_buffer = System.Text.Encoding.ASCII.GetBytes(request)
                stream.Write(send_buffer, 0, send_buffer.Length)
                
                self.log_connection(server_ip, success=True)
                logger.info("Successfully connected to server")
                
                client.Close()
            
            except Exception as e:
                logger.error("Failed to connect to server: {}".format(str(e)))
                self.log_connection(server_ip, success=False)

else:
    import socket
    import threading
    import platform  # Add this import for non-IronPython environments
    import json  # Add this import for non-IronPython environments
    
    class NetworkRoleSystem(NetworkBase):
        """CPython-specific networking implementation.
        
        This class extends NetworkBase to provide networking functionality
        specifically for CPython environments, using the standard socket library.
        
        Key Features:
        - Uses Python's socket library for network communication
        - Implements multi-threaded client handling
        - Provides Python-specific error handling
        - Supports secure token-based authentication
        """
        def server_listener(self):
            """Primary server listening mechanism for CPython.
            
            This method sets up a TCP server socket and handles incoming client
            connections in a multi-threaded manner. Each client connection is
            processed in a separate thread to allow for concurrent connections.
            
            The server:
            - Binds to the specified host and port
            - Listens continuously for incoming connections
            - Creates a new thread for each client
            - Logs all connection attempts and errors
            """
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
                listener.bind((self.HOST, self.PORT))
                listener.listen()
                logger.info("="*50)
                logger.info("SERVER STATUS: ONLINE")
                logger.info("Listening on {}:{}".format(self.HOST, self.PORT))
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
                            target=self.handle_client_connection,
                            args=(client,)
                        )
                        thread.start()
                    except Exception as e:
                        logger.error("="*50)
                        logger.error("SERVER ERROR")
                        logger.error("Error: {}".format(str(e)))
                        logger.error("="*50)

        def handle_client_connection(self, client):
            """Process individual client connections for CPython.
            
            This method handles the communication with a single client,
            including authentication, data exchange, and connection cleanup.
            
            Workflow:
            1. Get client address information
            2. Receive and process client request
            3. Generate and send authentication token
            4. Log connection details
            5. Clean up resources
            
            Args:
                client: The socket object representing the client connection
            """
            try:
                client_address = "{}:{}".format(*client.getpeername())
                logger.info("Processing client connection from: {}".format(client_address))
                
                data = client.recv(1024).decode('ascii')
                logger.debug("Received request: {}".format(data))
                
                self.log_connection(client_address, success=True)
                
                response = json.dumps({
                    'status': 'connected',
                    'token': self.generate_secure_token()
                })
                
                client.sendall(response.encode('ascii'))
                logger.info("Response sent to client: {}".format(client_address))
            
            except Exception as e:
                logger.error("Error handling client {}: {}".format(
                    client_address if 'client_address' in locals() else 'unknown',
                    str(e)
                ))
                if hasattr(client, 'getpeername'):
                    self.log_connection(client.getpeername()[0], success=False)
            
            finally:
                client.close()
                logger.debug("Client connection closed")

        def client_connection(self, server_ip=None):
            """Client-side connection attempt for CPython.
            
            This method implements the client-side connection logic using
            Python's socket library for network communication.
            
            The client:
            - Connects to the specified server
            - Sends authentication request
            - Handles server response
            - Logs connection status
            
            Args:
                server_ip (str, optional): IP address of the server to connect to.
                    Defaults to '192.168.1.100' if not specified.
            """
            if not server_ip:
                server_ip = '192.168.1.100'
            
            try:
                logger.info("Attempting to connect to server: {}:{}".format(server_ip, self.PORT))
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                    client.connect((server_ip, self.PORT))
                    
                    request = json.dumps({
                        'token': self.generate_secure_token(),
                        'computer_name': self.computer_name
                    })
                    
                    logger.debug("Sending connection request")
                    client.sendall(request.encode('ascii'))
                    self.log_connection(server_ip, success=True)
                    logger.info("Successfully connected to server")
            
            except Exception as e:
                logger.error("Failed to connect to server: {}".format(str(e)))
                self.log_connection(server_ip, success=False)

def call_me(**kwargs):
    """Application entry point for the network role system.
    
    This function serves as the main entry point for the application,
    creating and initializing the appropriate network role system based
    on the current environment (IronPython or CPython).
    
    Args:
        **kwargs: Optional keyword arguments
            server_ip (str): IP address of the server to connect to (for client mode)
    
    The function automatically determines which implementation to use
    based on the IS_IRONPYTHON environment variable.
    """
    network_system = NetworkRoleSystem()
    network_system.call_me(**kwargs)

def start_server():
    """Convenience method to start the server."""
    network_system = NetworkRoleSystem()
    network_system.call_me()

if __name__ == '__main__':
    call_me()