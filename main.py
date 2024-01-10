from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty

class Background(Widget):
    pass

class Character(Image):
    velocity = NumericProperty(0)

class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.character = Character()
        self.add_widget(self.character)
        
        self._keyboard = Window.request_keyboard(
            self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        self.pressed_keys = set()
        Clock.schedule_interval(self.character_move, 1/60)

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        self.pressed_keys.add(text)
        if text == 'd':
            self.character.source = "jumpright.png"
        if text == 'a':
            self.character.source = "jumpleft.png"

    def _on_key_up(self, keyboard, keycode):
        text = keycode[1]
        self.character.source = "character.png"
        if text in self.pressed_keys:
            self.pressed_keys.remove(text)

    def character_move(self, dt):
        cur_x = self.character.pos[0]
        cur_y = self.character.pos[1]
        step = 200 * dt
        if 'w' in self.pressed_keys:
            cur_y += step
        if 's' in self.pressed_keys:
            cur_y -= step
        if 'a' in self.pressed_keys:
            cur_x -= step
        if 'd' in self.pressed_keys:
            cur_x += step
        self.character.pos = (cur_x, cur_y)

class MainApp(App):
    def build(self):
        float_layout = FloatLayout()
        background = Background()
        game_widget = GameWidget()
        float_layout.add_widget(background)
        float_layout.add_widget(game_widget)
        return float_layout

if __name__ == "__main__":
    MainApp().run()
