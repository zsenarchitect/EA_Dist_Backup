import os
import base64
import io

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
            with io.open(icon_path, "rb", encoding="utf-8") as img_file:
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

    import json
    import datetime
    import os
    import platform
    import uuid
    import hmac
    import hashlib
else:
    pass

class NetworkBase:
    """Base networking functionality shared between IronPython and CPython implementations.
    
    Key Design Principles:
    - Platform-agnostic core functionality
    - Shared authentication and logging mechanisms
    - Consistent interface across implementations
    """
    def __init__(self):
        self.computer_name = platform.node().upper()
        self.is_server = self.computer_name == "SZHANG"
        self.HOST = '0.0.0.0'
        self.PORT = 12345
        self.connection_log_path = os.path.join(
            os.path.expanduser('~'), 
            'network_connection_log.json'
        )
        self._initialize_log()

    def _initialize_log(self):
        if not os.path.exists(self.connection_log_path):
            with open(self.connection_log_path, 'w') as f:
                json.dump([], f)

    def generate_secure_token(self):
        """
        Generate cryptographically secure authentication token
        
        Why use HMAC?
        - Provides one-time, secure authentication
        - Prevents replay attacks
        - Adds robust security layer
        """
        secret_key = 'your_network_secret_key'.encode('utf-8')
        return hmac.new(
            secret_key, 
            msg=str(uuid.uuid4()).encode('utf-8'), 
            digestmod=hashlib.sha256
        ).hexdigest()
    
    def log_connection(self, remote_host, success=True):
        """
        Record connection attempt details
        
        Logging mechanism:
        - Timestamp of connection
        - Remote computer details
        - Connection status
        """
        try:
            # Read existing log
            with open(self.connection_log_path, 'r') as f:
                logs = json.load(f)
            
            # Append new connection record
            logs.append({
                'timestamp': datetime.datetime.now().isoformat(),
                'remote_host': remote_host,
                'success': success
            })
            
            # Write updated log
            with open(self.connection_log_path, 'w') as f:
                json.dump(logs, f, indent=2)
        
        except Exception as e:
            print("Logging error: " + str(e))
    
    def call_me(self, **kwargs):
        """
        Primary entry point with flexible behavior
        
        Handles:
        - Server initialization
        - Client connection attempts
        - Optional parameter processing
        """
        if not kwargs:
            # Default initialization behavior
            if self.is_server:
                # Start server in separate thread
                System.Threading.Thread(
                    System.Threading.ThreadStart(self.server_listener)
                ).Start()
            else:
                # Attempt connection to server
                self.client_connection()
        
        else:
            # Process specific kwargs
            server_ip = kwargs.get('server_ip')
            if server_ip:
                self.client_connection(server_ip)

if IS_IRONPYTHON:
    class NetworkRoleSystem(NetworkBase):
        """IronPython-specific networking implementation."""
        def server_listener(self):
            """
            Primary server listening mechanism
            
            Handles:
            - Continuous socket listening
            - Client connection processing
            """
            listener = System.Net.Sockets.TcpListener(
                System.Net.IPAddress.Parse(self.HOST), 
                self.PORT
            )
            listener.Start()
            
            print("Server listening on " + self.HOST + ":" + str(self.PORT))
            
            while True:
                try:
                    client = listener.AcceptTcpClient()
                    System.Threading.Thread(
                        System.Threading.ParameterizedThreadStart(
                            self.handle_client_connection
                        )
                    ).Start(client)
                
                except Exception as e:
                    print("Server error: " + str(e))
        
        def handle_client_connection(self, client_obj):
            """
            Process individual client connections
            
            Workflow:
            1. Validate connection
            2. Log connection details
            3. Send acknowledgment
            """
            try:
                client = client_obj
                stream = client.GetStream()
                
                # Read client data
                buffer = System.Array.CreateInstance(System.Byte, 1024)
                bytes_read = stream.Read(buffer, 0, buffer.Length)
                request = System.Text.Encoding.ASCII.GetString(buffer, 0, bytes_read)
                
                # Log connection
                self.log_connection(
                    client.Client.RemoteEndPoint.ToString(), 
                    success=True
                )
                
                # Prepare response
                response = json.dumps({
                    'status': 'connected',
                    'token': self.generate_secure_token()
                })
                
                # Send response
                send_buffer = System.Text.Encoding.ASCII.GetBytes(response)
                stream.Write(send_buffer, 0, send_buffer.Length)
            
            except Exception as e:
                self.log_connection(
                    client.Client.RemoteEndPoint.ToString(), 
                    success=False
                )
                print("Client handling error: " + str(e))
            
            finally:
                client.Close()
        
        def client_connection(self, server_ip=None):
            """
            Client-side connection attempt
            
            Attempts to connect to server and log results
            """
            try:
                if not server_ip:
                    # Default to broadcast or specific network configuration
                    server_ip = '192.168.1.100'  # Replace with your network config
                
                client = System.Net.Sockets.TcpClient(server_ip, self.PORT)
                stream = client.GetStream()
                
                # Send initial connection request
                request = json.dumps({
                    'token': self.generate_secure_token(),
                    'computer_name': self.computer_name
                })
                
                send_buffer = System.Text.Encoding.ASCII.GetBytes(request)
                stream.Write(send_buffer, 0, send_buffer.Length)
                
                # Log successful connection
                self.log_connection(server_ip, success=True)
                
                client.Close()
            
            except Exception as e:
                # Log connection failure
                self.log_connection(server_ip, success=False)
                print("Connection error: " + str(e))

else:
    import socket
    import threading
    
    class NetworkRoleSystem(NetworkBase):
        """CPython-specific networking implementation."""
        def server_listener(self):
            """Primary server listening mechanism for CPython."""
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
                listener.bind((self.HOST, self.PORT))
                listener.listen()
                print("Server listening on {}:{}".format(self.HOST, self.PORT))
                
                while True:
                    try:
                        client, addr = listener.accept()
                        thread = threading.Thread(
                            target=self.handle_client_connection,
                            args=(client,)
                        )
                        thread.start()
                    except Exception as e:
                        print("Server error: {}".format(e))

        def handle_client_connection(self, client):
            """Process individual client connections for CPython."""
            try:
                data = client.recv(1024).decode('ascii')
                self.log_connection(client.getpeername()[0], success=True)
                
                response = json.dumps({
                    'status': 'connected',
                    'token': self.generate_secure_token()
                })
                
                client.sendall(response.encode('ascii'))
            
            except Exception as e:
                if hasattr(client, 'getpeername'):
                    self.log_connection(client.getpeername()[0], success=False)
                print("Client handling error: {}".format(e))
            
            finally:
                client.close()

        def client_connection(self, server_ip=None):
            """Client-side connection attempt for CPython."""
            if not server_ip:
                server_ip = '192.168.1.100'
            
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                    client.connect((server_ip, self.PORT))
                    
                    request = json.dumps({
                        'token': self.generate_secure_token(),
                        'computer_name': self.computer_name
                    })
                    
                    client.sendall(request.encode('ascii'))
                    self.log_connection(server_ip, success=True)
            
            except Exception as e:
                self.log_connection(server_ip, success=False)
                print("Connection error: {}".format(e))

def call_me(**kwargs):
    """
    Application entry point
    Demonstrates flexible network role system
    """
    network_system = NetworkRoleSystem()
    network_system.call_me(**kwargs)

if __name__ == '__main__':
    call_me()