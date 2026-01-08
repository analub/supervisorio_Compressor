from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup

class MainWidget(BoxLayout):
    """
        Widget principal do aplicativo
    """
    def __init__(self, **kwargs):
        """
        Construtor do widget principal
        """
        super().__init__()
        self._scan_time = kwargs.get('scan_time')
        self.modbusPopup = ModbusPopup()
        self.scanPopup = ScanPopup(scantime=self._scan_time)

