"""
Error storage and exception classes
"""

# Import the load and dump function from the json module for storing the errors, as well as the JSONDecodeError
from json import load as json_load, dump as json_dump, JSONDecodeError

# Import the format_exc function from the traceback module to get the traceback information
from traceback import format_exc

# Define the ErrorStorage class to store errors
class ErrorStorage():
    """Log errors to a JSON file."""
    def __init__(self, filename:str):
        self.filename = filename
        self.__error_load()


    # Define the __error_load method to load from the json file
    def __error_load(self):
        # Try to get the contents of the file
        try:
            with open(self.filename, 'r') as fileObject:
                self.__errors = json_load(fileObject)

        # Catch an exception if the file does not exist
        except (OSError, IOError, EOFError, JSONDecodeError):

            # Set errors to an empty list
            self.__errors = []
    

    # Define the __error_dump method to dump to the json file
    def __error_dump(self):
        # Dump the errors to the file
        with open(self.filename, 'w') as fileObject:
            json_dump(self.__errors, fileObject)
    
    
    # Define the update method to update the errors list with an error
    def update(self):
        """Update the errors list if it there is a new error."""
        # Get the traceback of the exception
        trace = format_exc()

        # Update the list with the traceback if the traceback is not already in the list
        if trace not in self.__errors:
            self.__errors.append(trace)
            
        # Dump the errors to its file
        self.__error_dump()
    

    # Define the clear method to clear the errors list
    def clear(self):
        """Clear the errors list."""
        # Clear the errors list
        self.__errors.clear()

        # Dump the errors to its file
        self.__error_dump()
    

    # Define the get method to get the list of errors
    def get(self):
        """Get the list of errors."""
        # Return the list of errors
        return self.__errors
    

    # Define the __bool__ method to determine the truth value of the class object
    def __bool__(self):
        """Determine if the errors list is empty."""
        # If the errors list is empty, return False
        if self.__errors == []:
            return False
        
        # Else, return True
        else:
            return True


class Stop(Exception):
    """An exception raised when the program should be stopped."""
    pass