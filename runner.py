from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.event import EventDispatcher


class SquatAnimation(EventDispatcher):
    """Отдельный класс для управления анимацией приседаний"""
    current_squat = NumericProperty(0)
    image_state = StringProperty('up')
    is_animating = BooleanProperty(False)

    def __init__(self, total_time, target_squats, image_widget, counter_label, progress_bar, **kwargs):
        super().__init__(**kwargs)

        # Виджеты для обновления
        self.image_widget = image_widget
        self.counter_label = counter_label
        self.progress_bar = progress_bar
        # Параметры анимации
        self.total_time = total_time
        self.elapsed_time = 0
        self.target_squats = target_squats
        self.temp_animating = self.total_time/self.target_squats/2
        self.squat_animation_event = None
        self.timer_event = None
        self.is_animating = False
        self.image_state = 'up'


    def start(self):
        self.is_animating = True
        self.squat_animation_event = Clock.schedule_interval(self.animate_squat, self.temp_animating)
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def animate_squat(self, dt):
        if not self.is_animating:
            return False

        if self.image_state == 'up':
            self.image_widget.source = 'second_sit.png'
            self.image_state = 'down'
            self.current_squat += 1
            self.progress_bar.value = self.current_squat
            self.counter_label.text = f"Приседаний: {self.current_squat} / {self.target_squats}"
        else:
            self.image_widget.source = 'first_sit.png'
            self.image_state = 'up'
        return True

    def update_timer(self, dt):
        self.elapsed_time += 1

        if self.total_time - self.elapsed_time <= 0:
            self.is_animating = False
            return False
        return True