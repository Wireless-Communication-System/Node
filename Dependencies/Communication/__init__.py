"""
Communication class to communicate with the ALFRED server
"""

# From the subprocess module import Popen and PIPE to send messages to and receive messages from the ALFRED server
from subprocess import Popen, PIPE

# From the codecs module import escape_decode to remove extra backslash characters from messages received from the server
from codecs import escape_decode

# From the pickle module import dump and load for handling the attributes file, as well as loads and UnpicklingError for server communication
from pickle import dump, loads, UnpicklingError


class Communication():
    """Communicate with the ALFRED Server."""
    def __init__(self) -> None:
        # Set up the sent and received data attributes
        self.sent_data_dict, self.received_data_dict = {}, {}
    

    # Define the message_encode method to encode a pandas object or basic variable to be sent to the ALFRED server
    def __message_encode(self, data, datatype):
        # Get the filename
        filename = fr'Sent/{datatype}_data.dat'

        # Open a file for binary writing
        with open(filename, 'wb') as fileObject:
            
            # Dump the data into the file
            dump(data, fileObject)
        
        # Return the filename
        return filename
    

    # Define the send_message method to send a message to the ALFRED server
    def send_message(self, data, datatype):
        # Encode the data to be sent to the server
        filename = self.__message_encode(data, datatype)

        # Add the data to the dictionary
        self.sent_data_dict.update({datatype: data})

        # Format the command for the message to be sent 
        sendMessage = fr'sudo cat {filename} | sudo alfred -s {datatype}'

        # Send the message to the server
        messageProcess = Popen(sendMessage, shell=True, stdout=PIPE, stderr=PIPE)



    # Define the data_decode method to decode a pickled object received from the ALFRED server
    def __data_decode(self, data):
        # Remove the unnecessary parts of each entry in the data
        data = escape_decode(escape_decode(data, 'hex')[0], 'hex')[0]
        data = data.split(b'",')
        data = [element for element in data if b'.' in element]
        data = list(map(lambda element: element.strip().lstrip(b'"'), data))

        # Try to decode using the loads pickle function
        try:

            # Use the loads function instead to decode the pickle elements
            decodedObjects = [loads(element) for element in data]
        
        # Catch an UnpicklingError exception if elements are not pickle objects
        except UnpicklingError:

            # Set the decoded objects to an empty list to be returned as None
            decodedObjects = []

        # Finally
        finally:
            
            # Return the decoded objects as is
            return decodedObjects


    # Define the receive_data method to request and receive the data for a datatype from the ALFRED server
    def receive_data(self, datatype, singular=False):
        # Format the command to request the data from the server
        requestData = f'sudo alfred -r {datatype}'
        
        # Request the data from the server
        requestProcess = Popen(requestData, shell=True, stdout=PIPE, stderr=PIPE)
    
        # Store the process output in data
        output = requestProcess.stdout.read()
        
        # Decode the process output
        data = self.__data_decode(output)

        # Add the data to the dictionary
        self.received_data_dict.update({datatype: data})

        # If the data is an empty list, then return None
        if data == []:

            # Return None
            return None
        
        # Else if there is only one element in the list and singular is True, return the singular decoded object
        elif len(data) == 1 and singular:

            # Return the first element of the list
            return data[0]
        
        # Else, return the entire list of data
        else:

            # Return the list of data
            return data
