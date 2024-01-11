from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ObjectProperty
from kivy.graphics import Rectangle
from kivy.lang import Builder
from random import randint
Builder.load_file('main.kv')
def collides(rect1, rect2):
    return (
        rect1[0] < rect2[0] + rect2[2] and
        rect1[0] + rect1[2] > rect2[0] and
        rect1[1] < rect2[1] + rect2[3] and
        rect1[1] + rect1[3] > rect2[1])

class Background(Widget):
    pass

class Character(Image):
    velocity = NumericProperty(0)

class Button(Widget):
    pass
class Arrow(Image):
    velocity = NumericProperty(3)


class ArrowHandler(Widget):
    creating_arrows = True  

    def create_arrow(self, pos):
        if self.creating_arrows:
            arrow = Arrow(source='arrow.png', pos=pos, size=(50, 50))
            self.add_widget(arrow)
            return arrow

    def stop_creating_arrows(self):
        self.creating_arrows = False

    def start_creating_arrows(self):
        self.creating_arrows = True

    def move_arrow(self, dt):
        for arrow in self.children:
            if isinstance(arrow, Arrow):
                arrow.x -= 500 * dt
                arrow.y += 200 * dt

class GameWidget(Widget):
    enemy_pos = ObjectProperty((2000, 300))
    enemy_speed = 600

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.character = Character()
        self.add_widget(self.character)
        self.arrow_handler = ArrowHandler()
        self.add_widget(self.arrow_handler)
        self._keyboard = Window.request_keyboard(
            self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        self.pressed_keys = set()
        Clock.schedule_interval(self.character_move, 1/60)
        self.create_enemy()

    def create_enemy(self):
        self.enemy_pos = (Window.height, randint(1, Window.width + 500))
        with self.canvas:
            self.enemy = Rectangle(source='arrow.png', pos=self.enemy_pos, size=(280, 180))
        self.create_arrow()
        
    def create_arrow(self):
        pos = (self.enemy_pos[1], self.enemy_pos[0])
        arrow = self.arrow_handler.create_arrow(pos)
    
    def start_app(self):
        pass
        
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
        self.enemy_pos = (self.enemy_pos[1] - self.enemy_speed * dt, self.enemy_pos[0])
        self.enemy.pos = self.enemy_pos

        if self.enemy_pos[1] < -100:
            self.create_enemy()

        if collides((cur_x, cur_y, 50, 50), (self.enemy_pos[0], self.enemy_pos[1], self.enemy.size[0] - 200, self.enemy.size[1] - 100)):
            self.gameover()

        for arrow in self.arrow_handler.children:
            if isinstance(arrow, Arrow) and collides((cur_x, cur_y, 50, 50), (arrow.x, arrow.y, arrow.width, arrow.height)):
                self.gameover()

        self.arrow_handler.move_arrow(dt)

        if cur_x < -200 or cur_x > Window.width - 200 or cur_y < -200 or cur_y > Window.height - 200:
            self.gameover()

        self.character.pos = (cur_x, cur_y)

    def gameover(self):
        App.get_running_app().stop()

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
