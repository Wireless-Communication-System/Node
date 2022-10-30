"""
Wireless Communication System
Node Code
"""

# Import the pandas module for storing information
import pandas as pd

# Import the asyncio module to allow for multiple methods to run at the same time
import asyncio

# Import the ErrorStorage class to log errors
from Dependencies.errors import ErrorStorage

# Import the Communication class to communicate with the ALFRED server
from Dependencies.Communication import Communication

# Import the LCD_Display class to control the LCD display
from Dependencies.LCD import LCDDisplay

# Import the GPIOManagement class to manage GPIO buttons and LEDs
from Dependencies.GPIO import GPIOManagement

# Import the get_mac function to get the mac address of the Raspberry Pi
from Dependencies.MAC import get_mac

# Define the Node class
class Node():
    """Communicates with the server and other nodes on the mesh network through the ALFRED server."""
    def __init__(self, errorStorageFile:str):
        # Store the errorStorageFile in data attributes
        self.__errorStorageFile = errorStorageFile

        # Create a dictionary with the datatype numbers for each type of data
        self.__datatype_dict = {
            'Online': 65,
            'Attributes': 68,
            'Cue to Node': 69,
            'Current': 70,
            'Node': 71
        }

        # Set the nodeSeries to an empty Series by default
        self.__nodeSeries = pd.Series()

        # Set the changeState flag and initialState flag to False and True
        self.__changeState, self.__initialState = False, True

        # Get the mac address of the node
        self.__mac = get_mac() 

        # Create an instance of the ErrorStorage class to store errors
        self.__errorStorage = ErrorStorage(self.__errorStorageFile)

        # Create an instance of the Communication class to communicate with the ALFRED server
        self.__communication = Communication()

        # Create an instance of the LCDDisplay class to control the LCD display
        self.__LCD = LCDDisplay()

        # Create an instance of the GPIOManagement class
        self.__GPIO = GPIOManagement(RGB_pins=[19, 13, 12], defaultColor='0000FF', buttonLEDPin=6, buttonInPin=5, delay=1)


    # Define the __get_node_series_value method to get a value from the node series
    async def __get_node_series_value(self, index):
        # Try to get the value from the node series
        try:

            # Get the value stored under the index argument in the node series
            value = self.__nodeSeries[index]
        
        # Catch a KeyError exception if the node series is not set up
        except KeyError:

            # Set the value to None to show that the node series has not been set up yet
            value = 'None'

        # Return the value
        return value


    # Define the __get_attribute_value method to get a value from the attribute dictionary
    async def __get_attribute_value(self, key):
        # Try to get the value from the attribute dictionary
        try:

            # Get the value stored under the key argument in the attribute dictionary
            value = self.__attributes_dict[key]
        
        # Catch a KeyError exception if the key is not set up
        except KeyError:

            # Set the value to None to show that the key has not been set up yet
            value = 'None'

        # Return the value
        return value


    # Define the cleanup method to clean up the GPIO and display
    def cleanup(self) -> None:
        """Clean up the GPIO and LCD."""

        # Clean up the GPIO
        self.__GPIO.cleanup()

        # Clear the display
        self.__LCD.clear()


    # Define the run_tasks method to concurrently (at the same time) run each part of the node
    async def run_tasks(self):

        try:

            # Initially set the up-to-date data attribute to its not connected state
            self.__uptodate_future = asyncio.get_running_loop().create_future()

            # Gather and store the setup tasks in a data attribute and shield it from cancellation
            self.__setup_tasks = asyncio.gather(
                # Try to update the state dataframe according to the server
                self.__update_state_frame(),

                # Try to update the node attributes according to the server
                self.__update_attributes()
            )

            # Schedule each task concurrently
            tasks = await asyncio.gather(

                # Check if the server is up-to-date
                self.__uptodate_check(),

                # Update the state of the LEDs
                self.__update_LEDs(),

                # Run the LED task
                self.__run_LEDs(),

                # Run the setup tasks
                self.__setup_tasks,

                # Update the information on the display
                self.__update_display(),

                # Get the current cue series from the server
                self.__get_cue_series(),

                # Get input from the button
                self.__get_button_input(),

                # Update the node series and send it the server
                self.__update_node_series()
            )
        
        # Catch all exceptions and log them
        except Exception:

            # Add the error to storage
            self.__errorStorage.update()

            # Display that an exception occurred on the LCD
            self.__LCD.display_text('An error has occurred: check log', priority=2)

            # Sleep for 10 seconds
            await asyncio.sleep(10)

            # Cleanup the LCD and GPIO
            self.cleanup()


    # Define the __uptodate_check method to determine if the data received from the server would be up-to-date before trying to get data from the server
    async def __uptodate_check(self) -> None:
        """Determine if the node is connected to the server."""

        # Get the server's current timestamp to compare intially
        self.__oldServerTime = self.__communication.receive_data(self.__datatype_dict['Online'], singular=True)

        # Forever
        while True:

            # Get the timestamp currently stored in the server
            newServerTime = self.__communication.receive_data(self.__datatype_dict['Online'], singular=True)

            # If the new server time is not none and the new server time is not equal to the old server time
            if newServerTime != None and newServerTime != self.__oldServerTime:

                # If the data attribute has not been updated, update it
                if not(self.__uptodate_future.done()):

                    # Set the uptodate_future data attribute to its done state
                    self.__uptodate_future.set_result('updated')

                # Set the old server time to the new server time
                self.__oldServerTime = newServerTime
                
                # Sleep for 5 seconds to allow other tasks to run
                await asyncio.sleep(5)

            # Else, if the new and old server time match, sleep for less time
            else:

                # If the future object is currently done, make a new future object for the methods to await
                if self.__uptodate_future.done():
                
                    # Set the data attribute to a new future object
                    self.__uptodate_future = asyncio.get_running_loop().create_future()
            
                # Sleep for a shorter time of 0.25 seconds to allow other tasks to run
                await asyncio.sleep(0.25)
        

    # Define the __update_attributes method to update the node attributes according to the server
    async def __update_attributes(self) -> str:
        """Update the attributes based on the server."""

        # Set the updated flag to False
        updated = False

        # While the attributes have not been updated, try to update them
        while not(updated):
            
            # Wait for the server data to be up-to-date
            await self.__uptodate_future

            # Get the dataframe with all the node attributes from the server
            all_attributes = self.__communication.receive_data(self.__datatype_dict['Attributes'], singular=True)

            # Try to locate the attributes
            try:

                # Locate the attributes by using the node's MAC address
                attributes_series = all_attributes.loc[self.__mac]   
                
                # Convert the attributes series to a dictionary and store it in a data attribute
                self.__attributes_dict = attributes_series.to_dict()

            # Catch an exception if the server has not set up the node yet
            except (KeyError, AttributeError):

                # Wait for 5 seconds
                await asyncio.sleep(5)
            
            # Else, if no errors occurred, then set the update flag to True
            else: updated = True

        
        # Else, return that the attributes were updated
        else:

            # Return that the attributes were updated
            return 'Attributes Updated'


    # Define the __update_state_frame method to update the state dataframe dictating the starting and ending node states according to the server
    async def __update_state_frame(self) -> str:
        """Get the state frame from the server."""

        # Set the updated flag to False
        updated = False
        
        # While the state dataframe has not been updated, try to update it
        while not(updated):

            # Wait for the server data to be up-to-date
            await self.__uptodate_future

            # Get the server's state frame from the server
            serverFrame = self.__communication.receive_data(self.__datatype_dict['Cue to Node'], singular=True)

            # If the server frame is not none
            if not(isinstance(serverFrame, type(None))):

                # Update the node's state frame to the server's state frame
                self.__stateFrame = serverFrame

                # Set the updated flag to True
                updated = True
            
            # Else, wait for 2.5 seconds
            else:

                # Wait for 2.5 seconds
                await asyncio.sleep(2.5)
        
        # Else, return that the the state dataframe was updated
        else:

            # Return that the state dataframe was updated
            return 'State Dataframe Updated'


    # Define the __get_cue_series method to get the current cue info as a series from the server
    async def __get_cue_series(self) -> None:
        """Get the necessary cues from the server."""

        # Wait for the setup tasks to finish
        await self.__setup_tasks

        # Set cue series to an empty series by default
        self.__cueSeries = pd.Series()

        # Forever
        while True:

            # Wait for the server data to be up-to-date
            await self.__uptodate_future

            # Get the dataframe with all the cues from the server
            all_cue_nums = self.__communication.receive_data(self.__datatype_dict['Current'], singular=True)

            # Try to locate the cues for the node
            try:

                # Locate the current cue number and state using the prefix attribute and update the data attribute
                self.__cueSeries = all_cue_nums.loc[await self.__get_attribute_value('Cue Prefix')]
            
            # Catch a KeyError or AttributeError exception if there are no cues for the node
            except (KeyError, AttributeError):

                # Sleep for 1 second to allow other tasks to run
                await asyncio.sleep(1)

            # Finally, sleep for 1 second to allow other tasks to run
            finally:

                # Sleep for 1 second to allow other tasks to run
                await asyncio.sleep(1) 
    

    # Define the __update_node_series method to update the node's data for the current cue and send it to the server
    async def __update_node_series(self) -> None:
        """Update the node series based off the cue series."""

        # Wait for the setup tasks to finish
        await self.__setup_tasks

        # Set node series to an empty series by default
        self.__nodeSeries = pd.Series()

        # Forever
        while True:

            # Wait for the server data to be up-to-date
            await self.__uptodate_future

            # If the cue series is empty, set the updated flag to False to prevent error
            if self.__cueSeries.empty: updated = False

            # Else if the node series is empty or the cue numbers don't match or the cue states don't match, update the node series
            elif self.__nodeSeries.empty or any([self.__cueSeries[attribute] != await self.__get_node_series_value(attribute) for attribute in ('Cue Number', 'Cue State')]):

                # Copy the cue series
                self.__nodeSeries = self.__cueSeries.copy()

                # Set the node state of the current series according to the node states dataframe and the cue state
                self.__nodeSeries['Node State'] = self.__stateFrame.at[self.__nodeSeries['Cue State'], 'Initial Node State']

                # Add the Node Number to the node series
                self.__nodeSeries['Node Number'] = await self.__get_attribute_value('Node Number')

                # Reset the changeState flag to False and set the initialState flag to True to allow for button presses to affect the node state
                self.__changeState, self.__initialState = False, True

                # Reset the GPIO's button press state
                self.__GPIO.reset_button_pressed()

                # Set the updated flag to True
                updated = True

            # Else if the changeState and initialState flag are True, update the series's node state to its final state
            elif self.__changeState and self.__initialState:
                
                # Update the node state of the series according to the node states dataframe and the cue state
                self.__nodeSeries['Node State'] = self.__stateFrame.at[self.__nodeSeries['Cue State'], 'Final Node State']

                # Set the initialState flag to False to prevent further updates for the current cue
                self.__initialState = False

                # Set the updated flag to True
                updated = True
            
            # Else, set the updated flag to False
            else: updated = False
            
            # If the node series has been updated, add the timestamp, pickle it to its file, and send it the server
            if updated:
                
                # Sleep for 1 second to allow other tasks to run
                await asyncio.sleep(1)

                # Add the current uptodate time to the node series
                self.__nodeSeries['Timestamp'] = self.__oldServerTime

                # Send a message to the server with the node series
                self.__communication.send_message(self.__nodeSeries, self.__datatype_dict['Node'])
            
            # Sleep for 1 second to allow other tasks to run
            await asyncio.sleep(1)


    # Define the __update_display method to update the display with relevant info
    async def __update_display(self) -> None:
        """Update the LCD display's text."""
        
        # Set the first flag to True by default
        first = True

        # Forever
        while True:

            # If the setup tasks are done, then display the cue information
            if self.__setup_tasks.done():
                
                # If the node just finished setup, display its attributes
                if first:

                    # Create tasks to get each part of the attributes dictionary
                    attributeTasks = [asyncio.create_task(self.__get_attribute_value(key)) for key in ('Node Number', 'Node Name', 'Cue Prefix')]

                    # Get the Node Number, Node Name, and Cue Prefix from the attributes dictionary
                    nodeNum, nodeName, cuePrefix = await asyncio.gather(*attributeTasks)

                    # Format the message to display the values of the attributes dictionary
                    message = f'Setup: {nodeNum}, {nodeName}, {cuePrefix}' + ' '*32

                    # Sleep for 8 seconds
                    await asyncio.sleep(8)

                    # Set the first flag to False
                    first = False

                # Else, display the normal cue information
                else:

                    # Get the Cue Number and Action from the node series
                    nodeTasks = [asyncio.create_task(self.__get_node_series_value(index)) for index in ('Cue Number', 'Action')]
                    cueNum, action = await asyncio.gather(*nodeTasks)

                    # Format the message to display the cue information
                    message = f'Cue {cueNum}: {action}' + ' '*32
                
            
            # Else, if the setup tasks are not yet done, then display the setup information
            else:

                # Display the MAC address of the node
                message = f'MAC Addr: {self.__mac}'

            # If the display was set up, then display the message on the display
            self.__LCD.display_text(message)
        
            # Sleep for 2 seconds to allow other tasks to run
            await asyncio.sleep(2)


    # Define the __update_LEDs method to update the color of the LEDs based on the cue state, node state, and connection to server
    async def __update_LEDs(self) -> None:
        """Update the RGB LED and the button's LED."""

        # Set the justPressed flag to False by default
        self.__justPressed = False

        # Forever
        while True:

            # Set the connected state of the GPIO Management to the uptodate data attribute
            self.__GPIO.connected(self.__uptodate_future.done())

            # If the node is connected to the server
            if self.__uptodate_future.done():
            
                # Get the cue and node states
                cueState, nodeState = await asyncio.gather(self.__get_node_series_value('Cue State'), self.__get_node_series_value('Node State'))
            
                # If the nodeState is not None # If the cue state is Go and the node state is not None or both values are None, then display the default colors
                if nodeState != 'None':#if (cueState == 'Go' and nodeState != 'None') or (cueState == 'None' and nodeState == 'None'):
                    
                    # If cue state is Go and the button was just pressed, then make the button's LED solid
                    if cueState == 'Go' and self.__justPressed:
                        self.__GPIO.button_state(True)
                    
                    # Else, turn off the button's1 LED
                    else:
                        self.__GPIO.button_state(False)

                    # Set the screen to default
                    self.__GPIO.default_screen()
                
                # Else, continue to determine what to do with the LEDs
                else:

                    # If cue state is Go and node state is None, then light up for go
                    if cueState == 'Go':
                        self.__GPIO.go()
                        self.__GPIO.blink_button()

                    # Else, turn off the button's LED
                    else:
                        self.__GPIO.button_state(False)
                    
                        # If cue state is Standby, then light up for standby
                        if cueState == 'Standby': self.__GPIO.standby()

                        # Elif cue state is Multiple Standbys, then light up for multiple standbys
                        elif cueState == 'Multiple Standbys': self.__GPIO.multiple_standbys()
            
            # Sleep for 0.2 seconds to allow other tasks to run
            await asyncio.sleep(0.2)


    # Define the __run_LEDs method to run the LED tasks
    async def __run_LEDs(self) -> None:
        """Run the LED tasks for the RGB LED and the button's LED."""

        # Get the delay of the sleep statements
        delay = self.__GPIO.get_delay()
        
        # Forever
        while True:

            # Run the tasks
            await self.__GPIO.run_LED_tasks()

            # Sleep for delay seconds
            await asyncio.sleep(delay)


    # Define the __get_button_input method to get input from the button to change the node state
    async def __get_button_input(self) -> None:
        """Get the input of the button."""

        # Wait for the setup tasks to finish
        await self.__setup_tasks

        # Forever
        while True:

            # If the changeState flag is False 
            if not self.__changeState:
                
                # Set the changeState flag to the button pressed boolean value
                self.__changeState = self.__GPIO.pressed()

                # If the changeState flag is now True
                if self.__changeState:

                    # Set the justPressed flag to True
                    self.__justPressed = True

                    # Sleep for 4 seconds to have the button's LED change to clearly change to solid
                    await asyncio.sleep(4)

                    # Set the justPressed flag to False
                    self.__justPressed = False

            # Sleep for 0.01 seconds to allow other tasks to run
            await asyncio.sleep(0.01)
    
    

# Define the main function
def main():

    # Create an instance of the node class
    cueNode = Node(r'errors.json')

    # Run all the node's tasks simultaneously using asyncio
    asyncio.run(cueNode.run_tasks())


# When the program runs
if __name__ == '__main__':

    # Call the main function
    main()