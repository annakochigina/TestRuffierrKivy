from kivy.app import App
from kivy.effects.scroll import ScrollEffect
from kivy.metrics import dp, sp
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import rgba

from instructions import txt_instruction, txt_test1, txt_test2, txt_test3
from runner import SquatAnimation
from seconds import Seconds
from ruffier import format_result

class DataStore:
    def __init__(self):
        self.username = ""
        self.user_age = 0
        self.pulse1 = 0
        self.pulse2 = 0
        self.pulse3 = 0

class FirstScr(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical', padding=8, spacing=8)

        scroll_view = ScrollView(size_hint=(1, 0.5), do_scroll_x=False, bar_color=[0.2, 0.6, 0.9, 0.9],
                                 bar_inactive_color=[0.7, 0.7, 0.7, 0.5], effect_cls=ScrollEffect)
        instruction = Label(text=txt_instruction, halign='center', valign='center', size_hint_y=None, font_size='15sp',
                            pos_hint='center_y',text_size=(scroll_view.width - 20, None), padding=[10, 5])
        instruction.bind(texture_size=lambda *x: setattr(instruction,'height',instruction.texture_size[1]))
        instruction.bind(width=lambda *x: setattr(instruction,'text_size',(instruction.width - 20, None)))
        scroll_view.add_widget(instruction)

        line1 = BoxLayout(size_hint=(0.8, None), height=dp(30), spacing=dp(10))
        lbl_name = Label(text='Введите имя:', halign='right')
        self.input_name = TextInput(multiline=False, input_filter=lambda sub, undo: ''.join(c for c in sub if c.isalpha()
                                                                            or c.isspace() or c == '-'))
        line1.add_widget(lbl_name)
        line1.add_widget(self.input_name)

        line2 = BoxLayout(size_hint=(0.8, None), height='30sp')
        lbl_age = Label(text='Введите возраст:', halign='right')
        self.input_age = TextInput(multiline=False, input_filter='int')
        line2.add_widget(lbl_age)
        line2.add_widget(self.input_age)

        self.btn = Button(text='Начать', size_hint=(0.3, 0.1), pos_hint={'center_x': 0.5})
        self.btn.bind(on_press=self.next)

        main_layout.add_widget(scroll_view)
        main_layout.add_widget(line1)
        main_layout.add_widget(line2)
        main_layout.add_widget(self.btn)

        self.add_widget(main_layout)

    def next(self, instance):
        app = App.get_running_app()
        result = app.check_input(name=self.input_name.text, age=self.input_age.text, screen='first')
        if result:
            app.user_store.username = self.input_name.text
            if int(self.input_age.text) < 7:
                app.user_store.user_age = 7
            else:
                app.user_store.user_age = int(self.input_age.text)
            self.manager.current = 'pulse1'
            print('test')

class PulseScr(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.next_screen = False
        self.update_event = None

        line_info_user = BoxLayout(size_hint=(1, None), height=dp(40), spacing=dp(10))
        self.lbl_user = Label(text=f"{app.user_store.username}, {app.user_store.user_age} лет", size_hint=(1, None),
                              height=dp(30), font_size=sp(16))
        line_info_user.add_widget(self.lbl_user)

        instruction = Label(text=txt_test1)
        self.lbl_sec = Seconds(15)
        self.lbl_sec.font_size = sp(16)
        self.lbl_sec.size_hint = (1, None)
        self.lbl_sec.height = dp(30)
        self.lbl_sec.halign = 'center'
        self.lbl_sec.bind(done=self.sec_finished)
        self.lbl_sec.bind(done=self.sec_finished)

        self.progress = ProgressBar(max=100, value=0, size_hint=(1, None), height='20sp')

        line = BoxLayout(size_hint=(0.8, None), height='30sp')
        lbl_result = Label(text='Введите результат:', halign='right')
        self.input_result = TextInput(multiline=False, input_filter='int')
        self.input_result.set_disabled(True)

        line.add_widget(lbl_result)
        line.add_widget(self.input_result)

        self.btn = Button(text='Начать', size_hint=(0.3, 0.4), pos_hint={'center_x': 0.5})
        self.btn.on_press = self.next

        main_layout = BoxLayout(orientation='vertical', padding=8, spacing=8)
        main_layout.add_widget(line_info_user)
        main_layout.add_widget(instruction)
        main_layout.add_widget(self.lbl_sec)
        main_layout.add_widget(self.progress)
        main_layout.add_widget(line)
        main_layout.add_widget(self.btn)

        self.add_widget(main_layout)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.lbl_user.text = f'{app.user_store.username}, {str(app.user_store.user_age)}'

    def sec_finished(self, *args):
        self.next_screen = True
        self.input_result.set_disabled(False)
        self.btn.set_disabled(False)
        self.btn.text = 'Продолжить'

    def update_progress(self, sec):
        if self.lbl_sec.current > 0:
            total = self.lbl_sec.total
            elapsed = self.lbl_sec.current
            self.progress.value = (elapsed / total) * 100
        return True

    def next(self):
        if not self.next_screen:
            self.btn.set_disabled(True)
            self.lbl_sec.start()
            self.update_event = Clock.schedule_interval(self.update_progress, 1)
        else:
            if self.update_event:
                self.update_event.cancel()
            app = App.get_running_app()
            result = app.check_input(pulse=[self.input_result.text], screen='pulse1')
            if result:
                app.user_store.pulse1 = int(self.input_result.text)
                self.manager.current = 'sits'


class CheckSits(Screen):
    current_squat = NumericProperty(0)
    squat_count = NumericProperty(0)
    image_state = StringProperty('up')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.next_screen = False
        self.update_event = None
        self.squat_animation = None

        line_info_user = BoxLayout(size_hint=(1, None), height=dp(30), spacing=dp(30))
        self.lbl_user = Label(text=f"{app.user_store.username}, {app.user_store.user_age} лет", size_hint=(1, None),
                              height=dp(30), font_size=sp(16), halign='left')
        line_info_user.add_widget(self.lbl_user)

        scroll_view = ScrollView(size_hint=(1, 0.5), do_scroll_x=False, bar_color=[0.2, 0.6, 0.9, 0.9],
                                 bar_inactive_color=[0.7, 0.7, 0.7, 0.5], effect_cls=ScrollEffect)
        instruction = Label(text=txt_test2, halign='center', valign='center', size_hint_y=None, font_size='15sp',
                            pos_hint='center_y', text_size=(scroll_view.width - 20, None), padding=[10, 5])
        instruction.bind(texture_size=lambda *x: setattr(instruction, 'height', instruction.texture_size[1]))
        instruction.bind(width=lambda *x: setattr(instruction, 'text_size', (instruction.width - 20, None)))
        scroll_view.add_widget(instruction)

        self.counter_label = Label(text="Приседаний: 0 / 30", size_hint=(1, None), height=dp(35), font_size=sp(20),
                                   halign='center', valign='middle')

        image_container = BoxLayout(size_hint=(1, 0.3), padding=[dp(20), 0])
        self.squat_image = Image(source='first_sit.png', size_hint=(1, 1), pos_hint={'center_x': 0.5},
                                 keep_ratio=True, allow_stretch=True)
        image_container.add_widget(self.squat_image)

        self.progress = ProgressBar(max=30, value=0, size_hint=(1, None), height='20sp')

        self.btn = Button(text='Начать', size_hint=(0.4, None), pos_hint={'center_x': 0.5}, height=dp(45), font_size=sp(18))
        self.btn.bind(on_press=self.start_animation)

        main_layout = BoxLayout(orientation='vertical', padding=8, spacing=8)
        main_layout.add_widget(line_info_user)
        main_layout.add_widget(scroll_view)
        main_layout.add_widget(self.counter_label)
        main_layout.add_widget(image_container)
        main_layout.add_widget(self.progress)
        main_layout.add_widget(self.btn)

        self.add_widget(main_layout)

        self.squat_animation = SquatAnimation(total_time=45, target_squats=30, image_widget=self.squat_image,
                                              counter_label=self.counter_label, progress_bar=self.progress)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.lbl_user.text = f'{app.user_store.username}, {str(app.user_store.user_age)}'

    def start_animation(self, instance):
        if self.next_screen:
            self.manager.current = 'pulse2'
        else:
            self.squat_animation.start()
            self.btn.text = 'Выполняется..'
            self.btn.disabled = True
            self.btn.background_color = (0.5, 0.5, 0.5, 1)
            self.update_event = Clock.schedule_interval(self.check_animation_completion, 0.1)

    def check_animation_completion(self, dt):
        if not self.squat_animation.is_animating:
            self.update_event.cancel()
            self.btn.text = 'Продолжить'
            self.btn.disabled = False
            self.next_screen = True
            return False
        return True


class PulseScr2(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.next_screen = False
        self.update_event = None
        self.stage = 1

        line_info_user = BoxLayout(size_hint=(1, None), height=dp(30), spacing=dp(30))
        self.lbl_user = Label(text=f"{app.user_store.username}, {app.user_store.user_age} лет", size_hint=(1, None),
                              height=dp(30), font_size=sp(16), halign='left')
        line_info_user.add_widget(self.lbl_user)

        scroll_view = ScrollView(size_hint=(1, 0.5), do_scroll_x=False, bar_color=[0.2, 0.6, 0.9, 0.9],
                                 bar_inactive_color=[0.7, 0.7, 0.7, 0.5], effect_cls=ScrollEffect)
        instruction = Label(text=txt_test2, halign='center', valign='center', size_hint_y=None, font_size='15sp',
                            pos_hint='center_y', text_size=(scroll_view.width - 20, None), padding=[10, 5])
        instruction.bind(texture_size=lambda *x: setattr(instruction, 'height', instruction.texture_size[1]))
        instruction.bind(width=lambda *x: setattr(instruction, 'text_size', (instruction.width - 20, None)))
        scroll_view.add_widget(instruction)

        self.lbl_pulse = Label(text='Считайте пульс', size_hint=(1, None), height=dp(30), font_size=sp(18),
                               halign='center', valign='middle')

        self.lbl_sec = Seconds(15)
        self.lbl_sec.font_size = sp(16)
        self.lbl_sec.size_hint = (1, None)
        self.lbl_sec.height = dp(30)
        self.lbl_sec.halign = 'center'
        self.lbl_sec.bind(done=self.sec_finished)

        self.progress = ProgressBar(max=100, value=0, size_hint=(1, None), height='20sp')

        line1 = BoxLayout(size_hint=(0.9, None), height=dp(30), spacing=dp(10))
        lbl_result1 = Label(text='Результат:', halign='right', size_hint=(0.4, 1), font_size=sp(15),valign='center')
        self.input_result1 = TextInput(multiline=False, input_filter='int')
        self.input_result1.set_disabled(True)
        line1.add_widget(lbl_result1)
        line1.add_widget(self.input_result1)

        line2 = BoxLayout(size_hint=(0.9, None), height=dp(30), spacing=dp(10))
        lbl_result2 = Label(text='Результат 2:', halign='right', size_hint=(0.4, 1), font_size=sp(15),valign='center')
        self.input_result2 = TextInput(multiline=False, input_filter='int')
        self.input_result2.set_disabled(True)
        line2.add_widget(lbl_result2)
        line2.add_widget(self.input_result2)

        self.btn = Button(text='Начать', size_hint=(0.3, None), pos_hint={'center_x': 0.5}, font_size=sp(18),)
        self.btn.on_press = self.next

        main_layout = BoxLayout(orientation='vertical', padding=8, spacing=8)
        main_layout.add_widget(line_info_user)
        main_layout.add_widget(scroll_view)
        main_layout.add_widget(self.lbl_pulse)
        main_layout.add_widget(self.lbl_sec)
        main_layout.add_widget(self.progress)
        main_layout.add_widget(line1)
        main_layout.add_widget(line2)
        main_layout.add_widget(self.btn)
        self.add_widget(main_layout)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.lbl_user.text = f'{app.user_store.username}, {str(app.user_store.user_age)}'

    def sec_finished(self, *args):
        if self.lbl_sec.done:
            if self.stage == 1:
                self.stage = 2
                self.lbl_pulse.text = 'Отдыхайте'
                self.lbl_sec.restart(30)
                self.input_result1.set_disabled(False)
                self.progress.value = 0
                self.update_event = Clock.schedule_interval(self.update_progress, 1)
            elif self.stage == 2:
                self.stage = 3
                self.lbl_pulse.text = 'Считайте пульс'
                self.lbl_sec.restart(15)
                self.progress.value = 0
                self.update_event = Clock.schedule_interval(self.update_progress, 1)
            else:
                self.input_result2.set_disabled(False)
                self.btn.set_disabled(False)
                self.btn.text = 'Завершить'
                self.next_screen = True

    def update_progress(self, sec):
        if self.lbl_sec.current > 0:
            total = self.lbl_sec.total
            elapsed = self.lbl_sec.current
            self.progress.value = (elapsed / total) * 100
            return True
        self.progress.value = 100
        return False

    def next(self):
        if not self.next_screen:
            self.btn.set_disabled(True)
            self.lbl_sec.start()
            self.update_event = Clock.schedule_interval(self.update_progress, 1)
        else:
            if self.update_event:
                self.update_event.cancel()
            app = App.get_running_app()
            result = app.check_input(pulse=[self.input_result1.text, self.input_result2.text], screen='pulse2')
            if result:
                app.user_store.pulse2 = int(self.input_result1.text)
                app.user_store.pulse3 = int(self.input_result2.text)
                self.manager.current = 'result'

class Result(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.main_layout = BoxLayout(orientation='vertical', padding=8, spacing=8)
        self.instr = Label(text='')
        self.main_layout.add_widget(self.instr)

        self.add_widget(self.main_layout)

    def on_pre_enter(self):
        app = App.get_running_app()
        self.instr.text = app.user_store.username + '\n' + format_result(app.user_store.pulse1, app.user_store.pulse2, app.user_store.pulse3, app.user_store.user_age)

class HeartCheck(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_store = DataStore()

    def build(self):
        sm = ScreenManager()
        sm.add_widget(FirstScr(name='instr'))
        sm.add_widget(PulseScr(name='pulse1'))
        sm.add_widget(CheckSits(name='sits'))
        sm.add_widget(PulseScr2(name='pulse2'))
        sm.add_widget(Result(name='result'))
        return sm

    def check_input(self, **kwargs):
        if 'name' in kwargs:
            if kwargs['name'] == '' and kwargs['age'] == '':
                self.show_popup('Поля ввода пустые!', 'Введите, пожалуйста, свои данные!')
            elif kwargs['name'] == '':
                self.show_popup('Поле ввода пустое!', 'Введите, пожалуйста, своё имя!')
            elif kwargs['age'] == '':
                self.show_popup('Поле ввода пустое!', 'Введите, пожалуйста, свой возраст!')
            elif int(kwargs['age']) <= 0:
                self.show_popup('Поле ввода пустое!', 'Введите, пожалуйста, корректный возраст!')
            else:
                return True

        if 'pulse' in kwargs:
            if len(kwargs['pulse']) == 1:
                if kwargs['pulse'][0] == '':
                    self.show_popup('Поле ввода пустое!', 'Введите, пожалуйста, свой пульс!')
                elif int(kwargs['pulse'][0]) <= 10:
                    self.show_popup('Некорректные данные!', 'Введите, пожалуйста, корректный пульс!')
                else:
                    return True
            else:
                if kwargs['pulse'][1] == '':
                    self.show_popup('Поле ввода пустое!', 'Введите, пожалуйста, свой пульс!')
                elif int(kwargs['pulse'][1]) <= 10:
                    self.show_popup('Некорректные данные!', 'Введите, пожалуйста, корректный пульс!')
                else:
                    return True
        return False

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical',spacing=dp(10), padding=dp(15))
        msg_label = Label(text=message, halign='center', valign='middle', size_hint=(1, 0.7), text_size=(None, None), color=rgba('#2196F3'))

        btn_close = Button(text='OK', size_hint=(0.5, 0.3), pos_hint={'center_x': 0.5}, font_size=sp(16))

        content.add_widget(msg_label)
        content.add_widget(btn_close)

        popup = Popup(title=title, title_color=rgba('#2196F3'), title_size=sp(18), content=content, size_hint=(0.7, 0.35), auto_dismiss=False)

        btn_close.bind(on_press=popup.dismiss)
        popup.open()


app = HeartCheck()
app.run()
