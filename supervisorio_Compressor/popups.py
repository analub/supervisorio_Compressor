from kivy.uix.popup import Popup


class ModbusPopup(Popup):
    """
    Popup da configuração do MODBUS
    """
    pass

class ScanPopup(Popup):
    """
    Popup da configuração do tempo de varredura
    """
    def __init__(self, scantime, **kwargs):
        """
        Construtor da classe ScanPopup
        """
        super().__init__(**kwargs)
        self.ids.txt_st.text = str(scantime)
    pass