"""allow async function to run in the background but this is using ironpython and .NET solution.

this is not going to work in Rhino and Revit due to thread design pattern."""

try:    
    import clr #pyright: ignore
    clr.AddReference("System")
    from System.Threading.Tasks import Task #pyright: ignore
except:
    pass

def as_async(func):
    """define a function to run in the background"""
    def wrapper(*args, **kwargs):
        task = Task.Factory.StartNew(lambda: func(*args, **kwargs))
        return task
    return wrapper


if __name__ == "__main__":
    import time

    @as_async
    def example_function(x, y):
        """Example function that simulates a time-consuming task"""
        time.sleep(2)  # Simulate a delay
        return x + y

    # Define arguments as a dictionary
    args_list = [
        {'x': 1, 'y': 2},
        {'x': 3, 'y': 4},
        {'x': 5, 'y': 6}
    ]

    # Start tasks
    tasks = [example_function(**args) for args in args_list]

    # Wait for all tasks to complete
    Task.WhenAll(tasks).Wait()

    # Collect results in the order tasks were started
    results = [task.Result for task in tasks]

    print("Results:", results)

