from kivy.app import App
from mainwidget import MainWidget
from kivy.lang.builder  import Builder

Builder.load_file("mainwidget.kv")
Builder.load_file("widgets_auxiliares.kv")
Builder.load_file("popups.kv")


class MainApp(App):
    """
        Classe principal do aplicativo
    """
    def build(self):    
        """
        Método que gera o aplicativo com base no widget principal.
        """
        self._widget = MainWidget(scan_time=1000) 
        return self._widget
    
if __name__ == "__main__":
    #Builder.load_string(open("mainwidget.kv", encoding="utf-8").read(), rulesonly=True)
    MainApp().run() 