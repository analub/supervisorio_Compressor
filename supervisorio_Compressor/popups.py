from kivy.uix.popup import Popup
from kivy.uix.label import Label # Importa a classe Label para criar mensagens de texto dinâmicas dentro do popup

class ModbusPopup(Popup):
    """
    Popup para configuração do protocolo Modbus.
    """
    _info_lb = None # Atributo para armazenar a label que exibirá mensagens de erro ou status
    def __init__(self, server_ip, server_port,**kwargs): # O **kwargs permite que a classe receba múltiplos parâmetros sem ter que especificar cada um.
        """
        Construtor da classe ModbusPopup
        """
        super().__init__(**kwargs)
        # Preenche automaticamente os campos de texto com o IP e Porta definidos na inicialização
        self.ids.txt_ip.text = str(server_ip)
        self.ids.txt_port.text = str(server_port)
    
    def setInfo(self, message):
        """
        Cria e adiciona uma mensagem de erro ou informação visualmente no layout do popup.
        """
        self._info_lb = Label(text=message)
        self.ids.layout.add_widget(self._info_lb)

    def clearInfo(self):
        """
        Remove a mensagem anterior para limpar o layout antes de uma nova tentativa de conexão.
        """
        if self._info_lb is not None:
            self.ids.layout.remove_widget(self._info_lb)

class ScanPopup(Popup):
    """
    Popup para exibir e configurar o tempo de varredura (scan time).
    """
    def __init__(self, scantime,**kwargs):
        """
        Construtor da classe ScanPopup"
        """
        super().__init__(**kwargs)
        # Inicializa o campo de texto com o valor atual do tempo de varredura
        self.ids.txt_st.text = str(scantime)
