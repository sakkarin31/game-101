from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class MainMenu(BoxLayout):
    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)

        start_game_button = Button(text="Start Game", size_hint=(None, None))
        start_game_button.bind(on_press=self.on_start_game)
        self.add_widget(start_game_button)

        exit_button = Button(text="Exit", size_hint=(None, None))
        exit_button.bind(on_press=self.on_exit)
        self.add_widget(exit_button)

    def on_start_game(self, instance):
        print("Start Game button pressed")

    def on_exit(self, instance):
        App.get_running_app().stop()

class MyApp(App):
    def build(self):
        return MainMenu()

if __name__ == "__main__":
    MyApp().run()