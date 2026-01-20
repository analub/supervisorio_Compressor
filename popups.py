from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy_garden.graph import LinePlot
from kivy.uix.boxlayout import BoxLayout

from datetime import datetime
from db import Session
from models import CompData

# Aqui serão colocados os popups do supervisório

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

class ComandoPopup(Popup):
    """
        Popup para enviar comandos de partida ao sistema
    """

    def trocar_tela(self, nome_tela):
        """
        Troca a subtela de configuração conforme o tipo de partida
        """
        self.ids.screenTipoPartida.current = nome_tela
    def on_open(self):
        # garante que todas as screens já foram carregadas
        self.ids.screenTipoPartida.current = "vazia"


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
    # def __init__(self, xmax,plot_color, **kwargs):
    #     super().__init__(**kwargs)
    #     self.plot = LinePlot(line_width=1.5, color=plot_color) #linha que será plotada no gráfico de temperatura, o gráfico é só o fundo
    #     self.ids.graph.add_plot(self.plot)
    #     self.ids.graph.xmax = xmax
    pass

class BancoDadosPopup(Popup):
    """
        Popup para exibir informações do banco de dados
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Cria a linha do gráfico (cor amarela)
        self.plot = LinePlot(line_width=1.5, color=[1, 1, 0, 1]) 
        # Adiciona a linha ao objeto Graph definido no arquivo .kv
        self.ids.graph_bd.add_plot(self.plot)

    def plotar_grafico(self):
        session = Session()
        try:
            # Obtém data e hora inicial e final de consulta
            dt_inicial = datetime.strptime(self.ids.txt_init_time.text, '%d/%m/%Y %H:%M:%S')
            dt_final = datetime.strptime(self.ids.txt_final_time.text, '%d/%m/%Y %H:%M:%S')

            #Obtém a variável escolhida na seleção
            variavel_selecionada = self.ids.dropdown.text

            #Escolher coluna correspondente do Banco de Dados
            coluna_banco = getattr(CompData, variavel_selecionada)

            #Consulta no Banco de Dados
            dados = session.query(CompData.timestamp, coluna_banco).filter(CompData.timestamp.between(dt_inicial, dt_final)).order_by(CompData.timestamp).all()
            if not dados:
                print("Nenhum dado encontrado")
                return
            
            pontos = []
            valores_y = []

            for i, registro in enumerate(dados):
                eixo_x = i
                eixo_y = registro[1]
                if eixo_y is not None:
                    pontos.append((eixo_x, eixo_y))
                    valores_y.append(eixo_y)

            self.plot.points = pontos
            if valores_y:
                self.ids.graph_widget.xmax = len(pontos)
                self.ids.graph_widget.xmin = 0
                self.ids.graph_widget.ymax = max(valores_y) * 1.1 # 10% de folga em cima
                self.ids.graph_widget.ymin = min(valores_y) * 0.9 # 10% de folga embaixo

        except AttributeError:
            print(f"Erro: A variável '{variavel_selecionada}' não existe na tabela do banco.")
        except ValueError as e:
            print("Erro de formato de data:", e)
        except Exception as e:
            print("Erro genérico:", e)
        finally:
            session.close()
            
class historicoPopup(Popup):
    """
        Popup para exibir hisotorico do banco de dados
    """
    def __init__(self,**kwargs):
        super().__init__()
    

class LabelCheckBoxGrafico(BoxLayout):
    pass
