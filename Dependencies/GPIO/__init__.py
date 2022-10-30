"""
GPIO Management classes
"""

# Import the RPi.GPIO module to get input from the buttons
import RPi.GPIO as GPIO

# Import the modified PWMOut class from pwmio to control the LEDs
from Dependencies.GPIO.pwmio.PWMOut import PWMOut

# Import asyncio to allow for multiple tasks to be run at once
import asyncio

# Define the LEDManager class to manage a LED
class LEDManager():
    """Manages a LED."""
    def __init__(self, pin:int, name:str) -> None:
        # Store the pin and name in data attributes
        self.pin, self.name = pin, name

        # Set up the GPIO for output
        GPIO.setup(pin, GPIO.OUT)
    
    def change_state(self, state:bool) -> None:
        """Change the output of the LED: True for on, False for off."""
        GPIO.output(self.pin, state)

    def on(self) -> None:
        """Turn on the LED."""
        self.change_state(True)

    def off(self) -> None:
        """Turn off the LED."""
        self.change_state(False)

 
# Define the RGBLEDManager sto manage one of the RGB LEDs 
class RGBLEDManager():
    """Manages one of the RGB LEDs.""" 
    def __init__(self, pin:int, name:str, initialBrightness:int=0) -> None:

        # Store the name in a data attribute
        self.name = name

        # Store the initial brightness in a data attribute
        self.__initialBrightness = initialBrightness

        # Set the brightness data attribute to the initial brightness
        self.brightness = self.__initialBrightness

        # Store the frequency (500Hz) of the LED in a data attribute
        self.__frequency = 500

        self.__pwm = PWMOut(pin, frequency=self.__frequency, duty_cycle=self.brightness)



    # Define the setBrightness method to change the brightness of the LED to change its color
    def setBrightness(self, brightness:int) -> None:
        """Set the brightness and thus the color of the LED. The brightness ranges from 0 to 100."""
        self.brightness = brightness
        self.__pwm.duty_cycle = self.brightness


    # Define the resetBrightness method to change the brightness of the LED back to its initial
    def resetBrightness(self) -> None:
        """Reset the brightness back to its initial brightness."""
        self.setBrightness(self.__initialBrightness)


    # Define the getBrightness method to get the duty cycle of the LED
    def getBrightness(self) -> int:
        """Get the duty cycle of the LED."""
        return self.__pwm.duty_cycle


    # Define the getPWMString method to get information on the LED
    def getPWMString(self) -> int:
        """Get info on the LED."""
        return str(self.__pwm)


    # Define the stop method to stop the PWM
    def stop(self) -> None:
        """Stop the PWM and turn off the LED."""
        self.__pwm.deinit()


# Define the RGBLEDManagement to manage a RGB LED
class RGBLEDManagement():
    """Manages a RGB LED."""
    def __init__(self, redPin:int, greenPin:int, bluePin:int, defaultColor:str) -> None:
        # Get the default brightnesses for each color LED
        redInitial, greenInitial, blueInitial = self.__get_hex(defaultColor)

        # Store the default color in a data attribute
        self.defaultColor = defaultColor
        
        # Create a RGBLEDManager object for each of the RGB LEDs
        self.__redLED = RGBLEDManager(redPin, 'Red', redInitial)
        self.__greenLED = RGBLEDManager(greenPin, 'Green', greenInitial)
        self.__blueLED = RGBLEDManager(bluePin, 'Blue', blueInitial)
    
    
    # Define the __set_color method to set the RGB LED color
    def __set_color(self, r:int=None, g:int=None, b:int=None) -> None:
        """Set the color of the RGB LED."""

        # Only set the brightness of the LED if an argument was supplied
        if r != None: self.__redLED.setBrightness(r)
        if g != None: self.__greenLED.setBrightness(g)
        if b != None: self.__blueLED.setBrightness(b)

    # Define the __get_hex method to get the LED brightnesses for a hexString number
    def __get_hex(self, hexNum:str) -> tuple:
        """Get the LED brightnesses for a hex number."""
        
        # Create a format for the hex number
        hexFormat = '0x{}'

        # Convert the hex string number to an integer with base 16 for each LED, dividing by 2.55 to get the percentage
        r = int(int(hexFormat.format(hexNum[:2]), 16)/2.55)
        g = int(int(hexFormat.format(hexNum[2:4]), 16)/2.55)
        b = int(int(hexFormat.format(hexNum[4:]), 16)/2.55)

        # Return the LED integers
        return r, g, b


    # Define the set_hex method to set the LED colors using a hex number
    def set_hex(self, hexNum:str) -> None:
        """Set the color of the RGB LED using a hex number."""
        self.__set_color(*self.__get_hex(hexNum))


    # Define the reset method to reset the RGB LED colors to their initial brightnesses
    def reset(self) -> None:
        """Reset the color of the RGB LED."""
        self.__redLED.resetBrightness()
        self.__greenLED.resetBrightness()
        self.__blueLED.resetBrightness()


    # Define the stop method to stop the RGB LED
    def stop(self) -> None:
        """Stop the RGB LED."""
        self.__redLED.stop()
        self.__greenLED.stop()
        self.__blueLED.stop()


# Define the ButtonManager class to manage the button
class ButtonManager():
    """Manages the button input."""
    def __init__(self, inPin:int) -> None:
        # Store the pin in a data attribute
        self.inPin = inPin

        # Set isPressed to False by default
        self.isPressed = False

        # Set up for input in pull up mode so that there is pull-up resistance
        GPIO.setup(self.inPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Set up event detection for the button for when it is pressed
        GPIO.add_event_detect(self.inPin, GPIO.RISING, callback=self.pressed, bouncetime=200)


    # Define the pressed method to change the button to the pressed state
    def pressed(self, channel) -> None:
        """Changed the pressed state to True."""
        self.isPressed = True


    # Define the reset method to reset the button back to the not pressed state
    def reset(self) -> None:
        """Changed the pressed state to False."""
        self.isPressed = False


    # Define the stop method to clean up the event detection
    def stop(self) -> None:
        """Remove event detection for the button."""
        GPIO.remove_event_detect(self.inPin)


# Define the GPIOManagement class to manage everything related to GPIO besides the LCD display
class GPIOManagement():
    """Manages GPIO devices, including the LEDs and button."""
    def __init__(self, RGB_pins:list, defaultColor:str, buttonLEDPin:int, buttonInPin:int, delay:int) -> None:
        # Store the delay in a data attribute
        self.__delay = delay

        # Turn off the warnings for GPIO
        GPIO.setwarnings(False)
        
        # Set the GPIO mode to the Broadcom pin-numbering scheme
        GPIO.setmode(GPIO.BCM)

        # Set the isConnected flag to False by default
        self.__isConnected = False

        # Set the screen task to the default screen
        self.default_screen()

        # Set the button task to be off 
        self.button_state(False)

        # Create the screen and button args to their defaults
        self.__screenArg = defaultColor
        self.__buttonArg = False

        # Set up the RGB LED
        self.__RGB = RGBLEDManagement(*RGB_pins, defaultColor)

        # Set up the Button LED
        self.__buttonLED = LEDManager(buttonLEDPin, 'Button')

        # Set up the button input
        self.__buttonInput = ButtonManager(buttonInPin)
    

    # Define the get_delay method to get the delay of sleep statements
    def get_delay(self) -> int:
        """Get the delay of sleep statements."""
        return self.__delay


    # Define the pressed method to determine if the button is pressed
    def pressed(self) -> bool:
        """Determine if the button is pressed."""
        return self.__buttonInput.isPressed

    
    # Define the standby method to create a task to make the screen solid yellow
    def standby(self) -> None:
        """Create a task to make the screen solid yellow."""

        # Make the screen basic yellow
        self.solid_screen('FFFF00')


    # Define the multiple_standbys method to create a task to make the screen blink yellow
    def multiple_standbys(self) -> None:
        """Create a task to make the screen blink yellow."""

        # Blink the screen basic yellow
        self.blink_screen('FFFF00')


    # Define the go method to create a task to make the screen solid green and turn on the button LED
    def go(self) -> None:
        """Create a task to make the screen solid green and turn on the button LED."""

        # Make the screen basic green
        self.solid_screen('00FF00')


    # Define the default_screen method to create a task to make the screen the default color
    def default_screen(self) -> None:
        """Create a task to make the screen the default color."""
        self.__screenTask = self.__default_screen
    

    # Define the async __default_screen method to set the screen to the default color
    async def __default_screen(self, _=None) -> None:
        """Make the screen its default color."""
        self.__RGB.reset()


    # Define the solid_screen method to create a task to make the screen a solid color
    def solid_screen(self, hexString:str) -> None:
        """Create a task to make the screen a solid color."""

        # Set the screen task to the solid screen
        self.__screenTask = self.__solid_screen

        # Set the screen arg to the hex string
        self.__screenArg = hexString


    # Define the solid_screen method to make the screen a solid color
    async def __solid_screen(self, hexString:str) -> None:
        """Make the screen a solid color."""
        
        # Display the hexString color
        self.__RGB.set_hex(hexString)

    
    # Define the blink_screen method to create a task to blink the screen
    def blink_screen(self, hexString:str) -> None:
        """Create a task to blink the screen and add it to the tasks list."""

        # Set the screen task to blink the screen
        self.__screenTask = self.__blink_screen

        # Set the screen arg to the hex string
        self.__screenArg = hexString


    # Define the async __blink_screen method to blink the screen a hexString color
    async def __blink_screen(self, hexString:str) -> None:
        """Blink the screen."""
        
        # Display the hexString color
        await self.__solid_screen(hexString)

        # Wait for delay seconds
        await asyncio.sleep(self.__delay)

        # Display the initial color
        await self.__default_screen()

    # Define the button_state method to create a task to set the button LED to on or off
    def button_state(self, state:bool) -> None:
        """Create a task to turn on or off the button's LED."""
        self.__buttonTask = self.__button_state

        # Set the button arg to the state
        self.__buttonArg = state
    

    # Define the async __button_state method to create a task to set the button LED to on or off
    async def __button_state(self, state:bool) -> None:
        """Turn on or off the button's LED."""
        self.__buttonLED.change_state(state)


    # Define the blink_button method to create a task to blink the LED on the button
    def blink_button(self) -> None:
        """Create a task to blink the button's LED."""
        self.__buttonTask = self.__blink_button


    # Define the async __blink_button method to blink the LED on the button
    async def __blink_button(self, _) -> None:
        """Blink the button's LED."""
        
        # Turn on the button's LED
        await self.__button_state(True)

        # Wait for delay seconds
        await asyncio.sleep(self.__delay)

        # Turn off the button's LED
        await self.__button_state(False)


    # Define the connected method to stop blinking red when the node is connected to the server
    def connected(self, state:bool) -> None:
        """Stop blinking red when connected to the server, and start blinking red when not connected."""
        
        # Set the isConnected flag to state
        self.__isConnected = state


    # Define the async __not_connected method to blink red when the node is not connected to the server
    async def __not_connected(self) -> None:
        """Blink red when not connected to the server."""
        await self.__blink_screen('FF0000')
    

    # Define the reset_button_pressed method to reset the isPressed variable of the button to False
    def reset_button_pressed(self) -> None:
        """Reset the button's isPressed variable to False."""
        self.__buttonInput.reset()


    # Define the async run_LED_tasks method to run the LED tasks at the same time
    async def run_LED_tasks(self):
        """Run the LED tasks at the same time."""

        # If the node is connected to the server, gather and await the LED tasks
        if self.__isConnected:

            # Gather and await the button LED and screen tasks
            tasks = await asyncio.gather(
                self.__buttonTask(self.__buttonArg),
                self.__screenTask(self.__screenArg))

        # Else, blink red on the display
        else:

            # Turn off the button LED and blink red on the LCD
            tasks = await asyncio.gather(
                self.__button_state(False),
                self.__not_connected())


    # Define the cleanup method to clean up the GPIO
    def cleanup(self) -> None:
        """Clean up the GPIO."""

        # Turn off the display
        self.__RGB.set_hex('000000')
        
        # Stop the RGB LED
        self.__RGB.stop()

        # Stop detecting button presses
        self.__buttonInput.stop()
        
        # Clean up the GPIO
        GPIO.cleanup()
