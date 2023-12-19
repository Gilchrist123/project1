import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from plyer import bluetooth as plyer_bluetooth

class DistanceApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Distance: Not connected")
        self.button_scan = Button(text="Scan Devices", on_press=self.scan_devices)
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.button_scan)
        Clock.schedule_interval(self.update_distance, 1)  # Update every second
        return self.layout

    def scan_devices(self, instance):
        try:
            if plyer_bluetooth.available:
                nearby_devices = plyer_bluetooth.discover_devices(duration=8, lookup_names=True, lookup_class=True)
                if not nearby_devices:
                    self.label.text = "No devices found"
                else:
                    for addr, name, _ in nearby_devices:
                        button = Button(text=name, on_press=lambda instance, addr=addr: self.connect_to_device(addr))
                        self.layout.add_widget(button)
            else:
                self.label.text = "Bluetooth not available on this platform."

        except Exception as e:
            print(f"Error during device scan: {e}")
            self.label.text = "Error during device scan"

    def connect_to_device(self, device_address):
        try:
            self.label.text = f"Connecting to {device_address}..."
            # Create a Bluetooth socket using plyer
            socket = plyer_bluetooth.socket(plyer_bluetooth.RFCOMM)

            # Connect to the Bluetooth module on the Arduino
            socket.connect((device_address, 1))  # The second argument is the port, usually 1 for SPP

            # Update the label and save the socket
            self.label.text = f"Connected to {device_address}"
            self.socket = socket

        except Exception as e:
            print(f"Connection error: {e}")
            self.label.text = "Connection failed"

    def update_distance(self, dt):
        try:
           # Check if the socket is available
            if hasattr(self, 'socket') and self.socket is not None:
                # Receive distance data (assuming it's a string)
                distance_data = self.socket.recv(1024).decode('utf-8')

                # Parse the received data (assuming it's a simple string representation of distance)
                try:
                    distance = int(distance_data)
                    self.label.text = f"Distance: {distance} cm"
                except ValueError:
                    print("Invalid distance data received.")
        except Exception as e:
            print(f"Error during distance update: {e}")
            self.label.text = "Connection lost"

if __name__ == '__main__':
    DistanceApp().run()
