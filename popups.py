from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen

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
    def trocar_tela(self, nome_tela):
        """
        Troca a subtela de configuração conforme o tipo de partida
        """
        self.ids.sm.current = nome_tela
    def on_open(self):
        # garante que todas as screens já foram carregadas
        self.ids.sm.current = "vazia"


# =====================================
# SCREENS DO COMANDO DE PARTIDA
# =====================================

class VaziaScreen(Screen):
    """
    Tela inicial (nenhuma partida selecionada)
    """
    pass

class TesysDiretaScreen(Screen):
    """
    Tela de configuração do motor Tesys Direta
    """
    pass


class ATS48Screen(Screen):
    """
    Tela de configuração do Soft-Starter ATS48
    """
    pass


class ATV31Screen(Screen):
    """
    Tela de configuração do Inversor ATV31
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

