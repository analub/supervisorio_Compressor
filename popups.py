from kivy.uix.popup import Popup

class ModbusPopup(Popup):
    """
        Popup para configuração do protocolo Modbus
    """
    pass

class ScanPopup(Popup):
    """
        Popup para exibir o progresso da varredura 
    """
    def __init__(self, scantime,**kwargs): #receber varios argumentos sem precisar especificar cada um
        """
        Construtor da classe ScanPopup"
        """
        super().__init__(**kwargs)
        self.ids.txt_st.text = str(scantime)
