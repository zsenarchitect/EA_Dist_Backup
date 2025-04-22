"""Helper functions to connect with Speckle server

Reference: https://www.youtube.com/watch?v=-A16gHzzBXA
"""

SPECKLE_AVAILABLE = True
try:
    from specklepy.api.client import SpeckleClient
    from specklepy.api.credentials import get_default_account, get_local_accounts
    from specklepy.transports.server import ServerTransport
    from specklepy.api import operations
    from specklepy.objects.base import Base
except ImportError:
    SPECKLE_AVAILABLE = False


def check_speckle_available(func):
    """Decorator to check if Speckle is available before executing function."""
    def wrapper(*args, **kwargs):
        if not SPECKLE_AVAILABLE:
            raise ImportError(
                "Speckle packages are not installed. Please install specklepy.")
        return func(*args, **kwargs)
    return wrapper


@check_speckle_available
def get_speckle_client(host="https://speckle.xyz"):
    """Initialize and return a Speckle client with default account."""
    client = SpeckleClient(host=host)
    account = get_default_account()
    if not account:
        accounts = get_local_accounts()
        if accounts:
            account = accounts[0]
        else:
            raise Exception(
                "No Speckle account found. Please login using Speckle Manager.")
    client.authenticate_with_token(token=account.token)
    return client


def get_stream_by_id(client, stream_id):
    """Get a specific stream by its ID."""
    return client.stream.get(id=stream_id)


def get_all_streams(client):
    """Get all streams accessible to the authenticated user."""
    return client.stream.list()


def create_stream(client, name, description=""):
    """Create a new stream with given name and description."""
    return client.stream.create(name=name, description=description)


def get_branch_by_name(client, stream_id, branch_name="main"):
    """Get a specific branch from a stream."""
    return client.branch.get(stream_id, branch_name)


def get_commit_by_id(client, stream_id, commit_id):
    """Get a specific commit from a stream."""
    return client.commit.get(stream_id, commit_id)


def receive_data(client, stream_id, commit_id):
    """Receive data from a specific commit."""
    transport = ServerTransport(client=client, stream_id=stream_id)
    commit = client.commit.get(stream_id, commit_id)
    return operations.receive(commit.referencedObject, transport)


@check_speckle_available
def send_data(client, stream_id, data, commit_message=""):
    """Send data to a stream with a commit message."""
    transport = ServerTransport(client=client, stream_id=stream_id)
    
    # Create a base object if data isn't already one
    if not isinstance(data, Base):
        base = Base()
        base.data = data
    else:
        base = data
    
    # Send data and create commit
    obj_id = operations.send(base, transport)
    commit_id = client.commit.create(
        stream_id=stream_id,
        object_id=obj_id,
        message=commit_message,
        branch_name="main"
    )
    return obj_id, commit_id


def get_latest_commit(client, stream_id, branch_name="main"):
    """Get the latest commit from a specific branch."""
    branch = client.branch.get(stream_id, branch_name)
    if branch and branch.commits:
        return branch.commits.items[0]
    return None


def create_branch(client, stream_id, name, description=""):
    """Create a new branch in a stream."""
    return client.branch.create(
        stream_id=stream_id,
        name=name,
        description=description
    )


def delete_stream(client, stream_id):
    """Delete a stream by its ID."""
    return client.stream.delete(id=stream_id)


def update_stream(client, stream_id, name=None, description=None, is_public=None):
    """Update stream properties."""
    update_dict = {}
    if name is not None:
        update_dict["name"] = name
    if description is not None:
        update_dict["description"] = description
    if is_public is not None:
        update_dict["isPublic"] = is_public
    
    return client.stream.update(
        id=stream_id,
        **update_dict
    )


if __name__ == "__main__":
    try:
        # Initialize client
        client = get_speckle_client()
        print("Successfully connected to Speckle!")

        # Create a new stream
        stream = create_stream(
            client=client,
            name="Test Stream",
            description="A test stream created via Python",
            is_public=True
        )
        print("Created new stream: {} (ID: {})".format(stream.name, stream.id))

        # Send some test data
        test_data = {
            "points": [
                {"x": 0, "y": 0, "z": 0},
                {"x": 1, "y": 1, "z": 1},
                {"x": 2, "y": 2, "z": 2}
            ],
            "metadata": {
                "creator": "EnneadTab",
                "date": "2024"
            }
        }
        
        obj_id, commit_id = send_data(
            client=client,
            stream_id=stream.id,
            data=test_data,
            commit_message="Initial test commit"
        )
        print("Sent data with object ID: {}".format(obj_id))
        print("Created commit with ID: {}".format(commit_id))

        # Receive the data back
        received_data = receive_data(
            client=client,
            stream_id=stream.id,
            object_id=obj_id
        )
        print("Received data: {}".format(received_data.data))

        # Get latest commit
        latest = get_latest_commit(client, stream.id)
        print("Latest commit ID: {}".format(latest.id))
        print("Latest commit message: {}".format(latest.message))

        # List all streams
        streams = get_all_streams(client)
        print("\nAll available streams:")
        for s in streams:
            print("- {} (ID: {})".format(s.name, s.id))

    except Exception as e:
        print("An error occurred: {}".format(str(e)))



if __name__ == "__main__":
    account = get_default_account()
    print (account)