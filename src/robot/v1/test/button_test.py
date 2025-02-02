from gpiozero import Button
from signal import pause

class ButtonController:
    def __init__(self, pin=21):
        self.button = Button(pin)
        self._setup_handlers()

    def _setup_handlers(self):
        self.button.when_pressed = self._handle_press
        self.button.when_released = self._handle_release

    def _handle_press(self):
        print("Button was pressed!")

    def _handle_release(self):
        print("Button was released!")

    def run(self):
        print("Waiting for button press...")
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
