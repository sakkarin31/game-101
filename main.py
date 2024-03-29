from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ObjectProperty
from kivy.graphics import Rectangle
from kivy.uix.popup import Popup
from kivy.core.audio import SoundLoader 
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from random import randint

def collides(rect1, rect2): # สร้างไว้สำหรับการเช็คตัวละคร
    return (
        rect1[0] < rect2[0] + rect2[2] and
        rect1[0] + rect1[2] > rect2[0] and
        rect1[1] < rect2[1] + rect2[3] and
        rect1[1] + rect1[3] > rect2[1]
    )

class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # เป็นส่วนการสร้างปุ่มที่ไว้ใช้งานหน้าเมนู
        button_layout = BoxLayout(orientation='vertical')
        start_button = Button(text='Go to Game', on_press=self.switch_to_game)
        quit_button = Button(text='Quit', on_press=self.quit_app)
        #ปุ่มเสียง ที่กดเปิดปิดได้
        sound_button = ToggleButton(text='Sound: On', group='sound', on_press=self.toggle_sound)
        sound_button.bind(state=self.on_sound_button_state)
        #เป็นว่สนที่ใส่ widget ปุ่มที่สร้างมาต่างๆรวมไว้ด้วยกัน
        button_layout.add_widget(start_button)
        button_layout.add_widget(sound_button)
        button_layout.add_widget(quit_button)

        self.add_widget(button_layout)

    def switch_to_game(self, instance): # เป็นฟังก์ชั่นที่เมื่อกดปุ่ม Go to Game จะไปสู่หน้าเกม ด้วยการกด on_press=self.switch_to_game
        self.manager.get_screen('game').reset_game()
        self.manager.current = 'game'

    def quit_app(self, instance): #ออกเมื่อกดปุ่ม Quit
        App.get_running_app().stop()

    def toggle_sound(self, instance): # เป็นฟังก์ชั่นที่ทำให้เพลงหยุดและเปิดได้
        game_screen = self.manager.get_screen('game')
        if instance.state == 'down':
            game_screen.play_background_music()
        else:
            game_screen.stop_background_music()

    def on_sound_button_state(self, instance, value): 
        instance.text = f"Sound: {'On' if value == 'down' else 'Off'}"
        
class Character(Image): #เป็นการกำหนดค่าต่างๆของตัวละคร เช่นรูป ขนาด ตำแหน่งเมื่อเริ่มต้น
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.character = Image(source='character.png')
        self.size_hint = (None, None)  
        self.size = (400, 300)
        self.pos = 50,50
        
class Background(Widget): # ส่วนที่กำหนด พื้นหลัภายในเกม
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background = Image(source='background.png', allow_stretch=True, keep_ratio=False)
        self.add_widget(self.background)

    def on_size(self, *args):
        self.background.size = self.size
        self.background.pos = self.pos



class Arrow(Image):
    velocity = NumericProperty(0)

class ArrowHandler(Widget): #เป็นส่วยกำหนด ศัตรูหรืออุปสรรคภายในเกม 
    creating_arrows = True

    def create_arrow(self, pos):
        if self.creating_arrows and not self.parent.game_over:
            arrow = Arrow(source='arrow.png', pos=pos, size=(50, 50))
            self.add_widget(arrow)
            return arrow

    def stop_creating_arrows(self):
        self.creating_arrows = False

    def start_creating_arrows(self):
        self.creating_arrows = True  #ส่วนนี้จะเชื่อมกับปุ่มหยุดภายในเกมทำให้ธนูไม่สร้างเมื่อกดหยุด

    def move_arrows(self, dt):
        arrows_to_remove = []
        for arrow in self.children:
            if isinstance(arrow, Arrow):
                arrow.x -= 500 * dt
                arrow.y += 200 * dt
                if arrow.x < -arrow.width or arrow.y > Window.height:
                    arrows_to_remove.append(arrow)

        for arrow in arrows_to_remove:
            self.remove_widget(arrow)


class MainApp(Screen): #เป็นส่วนหลักในเกม
    enemy_pos = ObjectProperty((2000, 300))
    enemy_speed = 600
    countdown_label = Label(text='', font_size=20, pos_hint={'right': 1, 'top': 1})
    countdown_seconds = 120
    initial_enemy_speed = 600
    initial_countdown_seconds = 120
    initial_hp = 100
    game_over = False
    def __init__(self, **kwargs): #ส่วนนี้จะเป็นส่วนสำคัญที่สุด เป็นส่วนที่นำสิ่งต่างๆมารวมไว้ให้ MainApp และการกำหนดตรงนี้จะทำให้สามารถสืบทอดตัวแปรในฟังก์ชั่นต่างๆ
        super().__init__(**kwargs)
        self.background = Background()
        self.add_widget(self.background)
        self.character = Character()
        self.add_widget(self.character)
        self.arrow_handler = ArrowHandler()
        self.add_widget(self.arrow_handler)
        self.add_widget(self.countdown_label)
        self.hp = 100 
        self.pause_button = Button(text='Pause', size_hint=(None, None), size=(100, 50), )
        self.pause_button.bind(on_press=self.pause_game)
        self.add_widget(self.pause_button)
        enemy = ObjectProperty(None)    
        self.hp_label = Label(text=f'HP: {self.hp}', font_size=20, pos_hint={'right': 1, 'top': 0.95})
        self.add_widget(self.hp_label)
        Clock.schedule_interval(self.update_countdown, 1)
        self._keyboard = Window.request_keyboard(
            self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        self.pressed_keys = set()
        Clock.schedule_interval(self.character_move, 1/60)
        self.reset_game()
        self.background_music = SoundLoader.load('sound_bg.mp3')
        if self.background_music: #
            self.background_music.loop = True
            self.background_music.volume = 0.1
            self.background_music.play()
    
    def update_countdown(self, dt): # ส่วนนับถอยหลัง ในตัวเกม
        if not self.game_over:
            self.countdown_seconds -= 1
            self.enemy_speed += 10
            self.countdown_label.text = f'Time left: {self.countdown_seconds} seconds'

            if self.countdown_seconds <= 0: 
                self.game_over = True
                self.countdown_label.text = 'WOWWWWWWWWWWWWWWWWW!!!!!!!!'
                self.show_congrat_popup()
                
    def reset_game(self): #ฟังกค์ชั่นนี้คือฟังกค์ชั่น รีเซ็ตค่าที่เคยมี เมื่อกดเริ่มเกมใหม่ค่าทุกอย่างจะรีเซ็ต เช่น ตำแหน่ง เวลานับถอยหลัง สปีดธนู เลือด เป็นต้น
        self.character.pos = (50, 50)
        self.countdown_seconds = self.initial_countdown_seconds
        self.enemy_speed = self.initial_enemy_speed
        self.game_over = False
        self.countdown_label.text = f'Time left: {self.countdown_seconds} seconds'
        self.create_enemy()
        self.arrow_handler.clear_widgets()
        self.hp = self.initial_hp
        self.update_hp_label() 
        
    def pause_game(self, *args): #ปุ่มหยุดในหน้าเริ่มเล่นเกมจะทำงานเมื่อกดปุ่ม pause
        Clock.unschedule(self.character_move)
        self.arrow_handler.stop_creating_arrows()
        Clock.unschedule(self.update_countdown)
        self.show_pause_popup()

    def show_pause_popup(self): #นี้จะเป็นส่วนที่แสดงขึ้นมาเมื่อกดหยุด
        self.continue_button = Button(text='Continue', size_hint=(None, None), size=(100, 50))
        self.continue_button.bind(on_press=self.continue_game) # สร้างปุ่มและสามารถกดได้เพื่อเล่นต่อ
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text='Game Paused', font_size=20))
        content.add_widget(self.continue_button)
        
        

        self.popup = Popup(title='Pause', content=content, size_hint=(None, None), size=(400, 200))
        self.popup.open()
        self.popup.content.size_hint_y = None
        self.popup.content.height = self.continue_button.height
        
    def continue_game(self, *args): # เริ่มเล่นเกมต่อ ทุกอย่างที่หยุดเมื่อกดหยุดนั้นจะกลับมางานเหมือนเดิม
        Clock.schedule_interval(self.character_move, 1 / 60)
        self.arrow_handler.start_creating_arrows()
        Clock.schedule_interval(self.update_countdown, 1)
        self.popup.dismiss()
        
    def update_hp_label(self): # จอแสดงพลังชีวิต
        self.hp_label.text = f'HP: {self.hp}'

    def take_damage(self, damage): #เช็คว่าตายหรือยัง
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.game_over = True
            self.show_gameover_popup()
        self.update_hp_label()

    def create_enemy(self): #สร้างศัตรูออกมา
        self.enemy_pos = (Window.height, randint(1, Window.width + 800))
        with self.canvas:
            self.enemy = Rectangle(source='arrow.png', pos=self.enemy_pos, size=(280, 180))
        self.create_arrow()

    def create_arrow(self): #เป็นการบอกว่าต้องสร้างอะไร
        pos = (self.enemy_pos[1], self.enemy_pos[0])
        arrow = self.arrow_handler.create_arrow(pos)

    def _on_keyboard_closed(self): 
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers): 
        self.pressed_keys.add(text)
        if text == 'd':
            self.character.source = "jumpright.png" 
        if text == 'a':
            self.character.source = "jumpleft.png" #เป็นส่วนที่จพทำให้ตัวละครดูมีมิติเมื่อกดขยับ

    def _on_key_up(self, keyboard, keycode):
        text = keycode[1]
        self.character.source = "character.png"
        if text in self.pressed_keys:
            self.pressed_keys.remove(text)

    def character_move(self, dt): # ส่วนที่ทำให้ตัวละครเคลื่อนที่ และสมูทเพราะมีการใช้ dt
        cur_x = self.character.pos[0]
        cur_y = self.character.pos[1]
        step = 250 * dt
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
            self.create_enemy() #สร้างธนูมาใหม่เมื่อธนูถึงพื้น

        if collides((cur_x, cur_y, 50, 50), (self.enemy_pos[0], self.enemy_pos[1], self.enemy.size[0] - 250, self.enemy.size[1] - 180)):
            self.take_damage(5) #เมื่อตัวละครโดนธนูรับดาเมจเรื่อยหาไม่หลบออกกจากธนู

        for arrow in self.arrow_handler.children:
            if isinstance(arrow, Arrow) and collides((cur_x, cur_y, 50, 50), (arrow.x, arrow.y, arrow.width, arrow.height)):
                self.take_damage(5) 

        self.arrow_handler.move_arrows(dt)

        if cur_x < -200 or cur_x > Window.width - 100 or cur_y < -100 or cur_y > Window.height - 100:
            self.show_free_popup() #เป็นส่วนพิเศษ ทำให้ตัวละครออกจากหน้าจอก็จะพบข้อความพิเศษ

        self.character.pos = (cur_x, cur_y)

    def show_gameover_popup(self): # ทำการแสดงข้อความ Gameover เมื่อพ่ายแพ้และส่งกลับไปหน้าเมนู
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text='Gameover!', font_size=20))

        self.popup = Popup(title='Haha!! ', content=content, size_hint=(None, None), size=(400, 200))
        self.popup.open()
        Clock.schedule_once(lambda dt: self.switch_to_menu(), 1)
        
    def show_congrat_popup(self): #ทำการแสดงข้อความยินดี
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text='Congratulations! You completed the game.', font_size=20))

        self.popup = Popup(title='Good Job!!', content=content, size_hint=(None, None), size=(400, 200))
        self.popup.open()

        Clock.schedule_once(lambda dt: self.switch_to_menu(), 1)
        
    def show_free_popup(self): #ทำการแสดงข้อความพิเศษ
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text='Congratulations! You got the FREEDOMMM.', font_size=20))

        self.popup = Popup(title='FREEEEEE!!', content=content, size_hint=(None, None), size=(400, 200))
        self.popup.open()

        Clock.schedule_once(lambda dt: self.quit(), 4)
    
    def quit(self):
        App.get_running_app().stop()
        
    def switch_to_menu(self): #นี้คือส่วนสำคัญในการที่ทำให้หน้าจอนั้นสลับไปมาได้ด้วยการ App.get_running_app().root.current = 'menu'
        self.popup.dismiss()
        self.reset_game()
        App.get_running_app().root.current = 'menu'
    
    def play_background_music(self): #ส่วนนี้จะไปเชื่อมกับด้านบนที่เปิดปิดได้
        if self.background_music:
            self.background_music.play()
    def stop_background_music(self):
        if self.background_music:
            self.background_music.stop()
     
class TestApp(App):

    def build(self):
        sm = ScreenManager()
        menu_screen = MainMenu(name='menu')
        sm.add_widget(menu_screen)
        game_screen = MainApp(name='game')
        sm.add_widget(game_screen) #เป็นส่วนที่แยกหน้าจอแต่ละอัน และสามารถสลับไป เกมหรือเมนู
        return sm
if __name__ == "__main__":
    TestApp().run()
