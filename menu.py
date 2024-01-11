from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class MainMenu(BoxLayout):
    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        start_button = Button(text="Start Game")
        start_button.bind(on_press=self.on_start_button_press)
        layout.add_widget(Label(text="Welcome to the Game"))
        layout.add_widget(start_button)
        self.add_widget(layout)

    def on_start_button_press(self, instance):
        print("Start Game button pressed")
