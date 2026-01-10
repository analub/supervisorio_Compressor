from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup
from pyModbusTCP.client import ModbusClient # # Importa a classe responsável por conectar o supervisório ao servidor Modbus TCP
from kivy.core.window import Window # Permite controlar propriedades da janela, como o cursor do mouse
from threading import Thread # Permite rodar funções em segundo plano sem travar a interface
from time import sleep # Utilizado para criar intervalos de tempo entre as leituras

class MainWidget(BoxLayout):
    """
        Widget principal do aplicativo
    """
    # Atributos para controle da thread de atualização de dados
    _updateThread = None # Armazena o objeto da Thread que fará a leitura constante
    _updateWidgets = True # Flag (bandeira) para controlar quando o loop de leitura deve rodar ou parar
    def __init__(self, **kwargs):
        """
        Construtor do widget principal.
        """
        super().__init__()
        self._scan_time = kwargs.get('scan_time')
        self._scanPopup = ScanPopup(scantime=self._scan_time)

        # Esse bloco é configuração do protocolo MODBUS

        self._serverIP = kwargs.get('server_ip')
        self._serverPort = kwargs.get('server_port')
        self._modbusPopup = ModbusPopup(self._serverIP, self._serverPort)
        self._modbusClient = ModbusClient(host=self._serverIP, port=self._serverPort)

    # Esse bloco é coleta de dados

    def startDataRead(self, ip, port):
        """
        Configura o IP/Porta e inicia a Thread de leitura se a conexão for aberta.
        """
        self._serverIP = ip
        self._serverPort = port
        self._modbusClient.host = self._serverIP
        self._modbusClient.port = self._serverPort
        try:
            # Muda o cursor para 'espera' enquanto tenta conectar
            Window.set_system_cursor("wait")
            self._modbusClient.open()
            Window.set_system_cursor("arrow") # Volta o cursor ao normal
            if self._modbusClient.is_open():
                # Inicia a Thread para que a interface não trave durante o loop de leitura
                self._updateThread = Thread(target=self.updater)
                self._updateThread.start()
                # Atualiza a interface indicando sucesso
                self.ids.img_con.source = 'imgs/conectado.png'
                self._modbusPopup.dismiss()
            else:
                self._modbusPopup.setInfo("Falha na conexão com o servidor.")
        except Exception as e:
            print("Erro: ", e.args)

    def updater(self):
        """
        Loop de execução em segundo plano para leitura de dados e atualização da tela.
        """
        try:
            while self._updateWdigets:
                # Aqui entrarão as rotinas de:
                # 1. Ler os dados via protocolo Modbus
                # 2. Atualizar os labels e gráficos da interface
                # 3. Inserir os dados no Banco de Dados para histórico

                # Aguarda o tempo de varredura definido (convertido para segundos)
                sleep(self._scan_time/1000)
        except Exception as e:
            self._modbusClient.close()
            print("Erro: ", e.args)


