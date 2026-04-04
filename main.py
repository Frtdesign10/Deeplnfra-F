from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock

class FrtDesignApp(App):
    def build(self):
        self.label = Label(text="Waiting for Sensor Data...")
        Clock.schedule_interval(self.read_sensor, 1.0)
        return self.label

    def read_sensor(self, dt):
        try:
            line_status = "Line Detected" 
            self.label.text = f"Status: {line_status}"
        except Exception as e:
            self.label.text = "Sensor Error: No Data"

if __name__ == "__main__":
    FrtDesignApp().run()
