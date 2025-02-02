from gpiozero import Button
from signal import pause

class ButtonController:
    def __init__(self, pin=21):
        print(f"Initializing button on GPIO pin {pin}")
        self.button = Button(pin, pull_up=True)
        self._setup_handlers()

    def _setup_handlers(self):
        print("Setting up button handlers...")
        self.button.when_pressed = self._handle_press
        self.button.when_released = self._handle_release

    def _handle_press(self):
        print("Button was pressed!")
        print(f"Button is_pressed: {self.button.is_pressed}")

    def _handle_release(self):
        print("Button was released!")
        print(f"Button is_pressed: {self.button.is_pressed}")

    def run(self):
        print("Waiting for button press...")
        print(f"Initial button state - is_pressed: {self.button.is_pressed}")
        pause()

def main():
    try:
        controller = ButtonController()
        controller.run()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        print("Cleaning up...")

if __name__ == "__main__":
    main()
