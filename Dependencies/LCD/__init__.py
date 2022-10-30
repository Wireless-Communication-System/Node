"""
LCD Display Class
"""

# Import the required custom modules for the I2CLCD1602 display
from .PCF8574 import PCF8574_GPIO
from .Adafruit_LCD1602 import Adafruit_CharLCD
from .addresses import ADDRESSES

# Define the LCDDisplay class to control the LCD display
class LCDDisplay():
    """Sets up and allows one to control a 16 by 2 LCD display."""
    def __init__(self) -> None:
        # Set the default data attribute values
        self.__message = ''
        self.__currentPriority = 0

        # Set up the display
        self.__display_setup()


    # Define the __display_setup method to set up the LCD display
    def __display_setup(self) -> None:
        """Set up the display."""

        # Set the isSetup flag to True by default
        self.__isSetup = True

        # Try to set up a GPIO adapter with an address, breaking when one is found
        for address in ADDRESSES:
            try:
                adapter = PCF8574_GPIO(address)
            except OSError:
                print(f'Address {address} did not work for the LCD.')
            else:
                break
        
        # Else, if a suitable address is not found, then set the isSetup flag to False
        else:
            self.__isSetup = False

        # If the isSetup flag is True, then finish the setup
        if self.__isSetup:

            # Set up the lcd display and store it in a data attribute
            self.__display = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=adapter)

            # Set the number of columns and rows of the display to 16 by 2
            self.__display.begin(16, 2)


    # Define the display_text method to display text on the LCD display
    def display_text(self, text:str, priority:int=1) -> None:
        """Display text on the 16 by 2 LCD display."""
        
        # If the display is setup, then display the message
        if self.__isSetup and priority >= self.__currentPriority:

            # Store only the first 32 characters in self.__message to be displayed
            self.__message = text[:32]

            # Reset the cursor position to the top left corner of the display
            self.__display.home()

            # Display the first 16 characters of the message on the first row of the LCD display
            self.__display.message(self.__message[:16] + '\n')

            # Display the next 16 characters of the message on the second row of the LCD display
            self.__display.message(self.__message[16:32])

            # Update the current priority
            self.change_priority(priority)


    # Define the change_priority method to change the priority of the display
    def change_priority(self, priority:int=0) -> None:
        """Change the priority of the display to allow for lower priority text to be displayed (with a low priority)
        or no text to be displayed (with a high priority)."""
        self.__currentPriority = priority


    # Define the get method to get the currently displayed message
    def get(self) -> str:
        """Get the currently displayed message."""
        # Return the currently display message
        return self.__message


    # Define the clear method to clear the display
    def clear(self) -> None:
        """Clear the display of its text."""

        # Clear the display
        self.__display.clear()
    

    # Define the __bool__ method to determine the truth value of the class object
    def __bool__(self) -> bool:
        """Return the truth value of the class object."""
        
        # If the display was set up
        if self.__isSetup:
            return True
        
        # Else, return False
        else:
            return False