from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup, ComandoPopup

class MainWidget(BoxLayout):
    """
        Widget principal do aplicativo
    """
    def __init__(self, **kwargs):    #criar/colocar os popups aqui
        """
        Construtor do widget principal
        """
        super().__init__()
        self._scan_time = kwargs.get('scan_time')
        self._modbusPopup = ModbusPopup()
        self._scanPopup = ScanPopup(scantime=self._scan_time)
        self._comandoPopup = ComandoPopup()

