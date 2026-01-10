from kivy.app import App
from mainwidget import MainWidget
from kivy.lang.builder  import Builder

# Carregamento dos arquivos de interface gráfica (.kv)
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
        # Passamos o IP e a Porta do servidor como argumentos.
        # Isso permite que o MainWidget já inicie configurado para o localhost (127.0.0.1).
        self._widget = MainWidget(scan_time=1000, server_ip='127.0.0.1', server_port=502)
        return self._widget
    
if __name__ == "__main__":
    #Builder.load_string(open("mainwidget.kv", encoding="utf-8").read(), rulesonly=True)
    MainApp().run() # Inicia a execução do aplicativo