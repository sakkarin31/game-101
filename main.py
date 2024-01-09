from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Rectangle
from kivy.uix.floatlayout import FloatLayout

class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        self.pressed_keys = set()
        Clock.schedule_interval(self.move_step, 1/60)

        with self.canvas:
            self.character = Rectangle(source='character.png', pos=(0, 0), size=(400, 300))

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

    def move_step(self, dt):
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

class Background(Image):
    pass
     
class MainApp(App):
    def build(self):
        flaot = FloatLayout()
        back = Background(source='background.png', allow_stretch=True, keep_ratio=False)
        game_widget = GameWidget()
        flaot.add_widget(back)
        flaot.add_widget(game_widget)
        return flaot
    
if __name__=="__main__":
    MainApp().run()
