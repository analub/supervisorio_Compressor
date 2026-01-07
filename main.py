from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

Builder.load_file("telas.kv")

class TelaPrincipal(Screen):
    pass

class SupervisórioApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(TelaPrincipal(name="principal"))
        return sm

if __name__ == "__main__":
    SupervisórioApp().run()
