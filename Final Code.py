from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2 as cv
from LengthMeasurement import main_cv

Window.size = (1500, 1000)
Window.clearcolor = (27/255, 36/255, 52/255, 1)

paper_size_list = ['A3', 'A4', 'A5', 'Custom']
unit_list = ['MM', 'CM', 'INCH', 'FOOT']
steps_list = ['1', '2', '3', '4', '5']
paper_size = 'A4'
unit = 'CM'
steps = '5'
previous_state = ''


class Boxes(Widget):

    def click(self, value):
        global paper_size, unit, steps

        if value.state == 'normal':
            value.state = 'down'


        if value.text in paper_size_list:
            paper_size = value.text
        elif value.text in unit_list:
            unit = value.text
        elif value.text in steps_list:
            steps = value.text

    pass



class LengthMeasurementApp(App):

    def build(self):
        self.icon = "ruler.png"
        layout = Boxes()
        self.img1 = Image()
        self.img2 = Image()
        layout.add_widget(self.img1)
        layout.add_widget(self.img2)
        Clock.schedule_interval(self.update, 1 / 30)
        return layout

    def update(self, dt):
        self.load_video()

        ret, frame = self.capture.read()
        if ret:
            pass
        else:
            print('no video')
            self.capture.set(cv.CAP_PROP_POS_FRAMES, 0)
            return

        frame2 = main_cv(frame, paper_size, unit, steps)
        # convert Image 1 & 2 to texture
        texture1 = self.image_to_texture(frame)
        texture2 = self.image_to_texture(frame2)

        #display image 1 & 2 from the texture
        self.display_image(self.img1, texture1, pos_hint=(0.0066666, 0.008), size_hint=(0.384, 0.864), allow_stretch=True, keep_ratio=False)
        self.display_image(self.img2, texture2, pos_hint=(0.3973333, 0.008), size_hint=(0.384, 0.864), allow_stretch=True, keep_ratio=False)

    def load_video(self):
        global previous_state

        current_state = paper_size
        if current_state != previous_state:
            # print(previous_state)
            # print(current_state)
            # print('---------------')
            if current_state == 'A3':
                self.capture = cv.VideoCapture('A3.mp4')
                self.capture.set(cv.CAP_PROP_POS_FRAMES, 0)
                previous_state = current_state
            if current_state == 'A4':
                self.capture = cv.VideoCapture('A4.mp4')
                self.capture.set(cv.CAP_PROP_POS_FRAMES, 0)
                previous_state = current_state
            if current_state == 'A5':
                self.capture = cv.VideoCapture('A5.mp4')
                self.capture.set(cv.CAP_PROP_POS_FRAMES, 0)
                previous_state = current_state
            if current_state == 'Custom':
                self.capture = cv.VideoCapture('Currently Not Available.mp4')
                self.capture.set(cv.CAP_PROP_POS_FRAMES, 0)
                previous_state = current_state

    def image_to_texture(self, frame_to_conv):
        buf1 = cv.flip(frame_to_conv, 0)
        buf = buf1.tobytes()
        texture = Texture.create(size=(frame_to_conv.shape[1], frame_to_conv.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        return texture

    def display_image(self,instance, img, pos_hint=(0, 0), size_hint=(0.5, 0.5), allow_stretch=True, keep_ratio=False):
        instance.texture = img
        instance.pos = Window.width * pos_hint[0], Window.height * pos_hint[1]
        instance.size = (Window.width * size_hint[0], Window.height * size_hint[1])
        instance.allow_stretch = allow_stretch
        instance.keep_ratio = keep_ratio





if __name__ == "__main__":
    LengthMeasurementApp().run()





