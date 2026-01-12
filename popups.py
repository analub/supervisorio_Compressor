from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView

# Aqui serão colocados os popups do supervisório

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

class ComandoPopup(Popup):
    """
        Popup para enviar comandos de partida ao sistema
    """
    pass

class TemperaturaPopup(Popup):
    """
        Popup para exibir informações de temperatura
    """
    pass

class MedidasPopup(Popup):
    """
        Popup para exibir informações de medidas
    """
    pass

class GraficoPopup(Popup):
    """
        Popup para exibir gráficos
    """
    pass

class BancoDadosPopup(Popup):
    """
        Popup para exibir informações do banco de dados
    """
    pass

