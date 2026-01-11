from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup
from pyModbusTCP.client import ModbusClient # Importa a classe responsável por conectar o supervisório ao servidor Modbus TCP
from kivy.core.window import Window # Permite controlar propriedades da janela, como o cursor do mouse
from threading import Thread # Permite rodar funções em segundo plano sem travar a interface
from time import sleep # Utilizado para criar intervalos de tempo entre as leituras
from datetime import datetime

class MainWidget(BoxLayout):
    """
    Widget principal do aplicativo
    """
    # Atributos para controle da thread de atualização de dados
    _updateThread = None # Armazena o objeto da Thread que fará a leitura constante
    _updateWidgets = True # Flag (bandeira) para controlar quando o loop de leitura deve rodar ou parar
    _tags = {}
    def __init__(self, **kwargs):
        """
        Construtor do widget principal.
        """
        super().__init__()
        # Configurações iniciais recebidas da main.py
        self._scan_time = kwargs.get('scan_time')
        self._serverIP = kwargs.get('server_ip')
        self._serverPort = kwargs.get('server_port')

        # Instancia os componentes de interface e comunicação
        self._scanPopup = ScanPopup(scantime=self._scan_time)
        self._modbusPopup = ModbusPopup(self._serverIP, self._serverPort)
        self._modbusClient = ModbusClient(host=self._serverIP, port=self._serverPort)
        
        # Estrutura de dados para armazenar as medições em tempo real
        self._meas = {'timestamp': None, 'values': {}}

        # Mapeamento de unidades de medida da planta de compressão
        units = {
            'vel_motor': ' RPM', 
            'torque': ' Nm', 
            'pressao_vazao': ' bar', 
            'vazao_valvulas': ' m³/h',
            'temp_carcaca': ' °C', 
            'freq_rede': ' Hz', 
            'ddp_rs': ' V', 
            'ddp_st': ' V', 
            'ddp_tr': ' V',
            'corr_r': ' A', 
            'corr_s': ' A', 
            'corr_t': ' A', 
            'corr_neutro': ' A', 
            'corr_media': ' A',
            'pot_ativa_total': ' kW', 
            'pot_reativa_total': ' kVAr', 
            'pot_aparente_total': ' kVA',
            'dem_anterior': ' kW', 
            'dem_atual': ' kW', 
            'dem_media': ' kW', 
            'dem_prevista': ' kW',
            'pot_ativa_r': ' kW', 
            'pot_ativa_s': ' kW', 
            'pot_ativa_t': ' kW', 
            'fp_total': ''
        }

        # Organiza as configurações de cada sensor (Endereço, Cor no Gráfico e Unidade)
        for key, value in kwargs.get('modbus_addrs').items():
            if key in ['vel_motor', 'torque', 'pressao_vazao']:
                plot_color = (1, 0, 0, 1) # Vermelho (Principais)
            elif 'ddp' in key:
                plot_color = (0, 0, 1, 1) # Azul (Tensões)
            elif 'corr' in key:
                plot_color = (1, 0.5, 0, 1) # Laranja (Correntes)
            else:
                plot_color = (0, 1, 0, 1) # Verde (Outros)
            self._tags[key] = {'addr': value, 'color': plot_color, 'unit': units.get(key, '')}

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
            while self._updateWidgets:
                self.readData()
                self.updateGUI()
                # Aqui entrará a rotina de inserir os dados no Banco de Dados para histórico
                # Aguarda o tempo de varredura definido (convertido para segundos)
                sleep(self._scan_time/1000)
        except Exception as e:
            self._modbusClient.close()
            print("Erro: ", e.args)

    def readData(self):
        """
        Realiza o polling (consulta) dos registradores Modbus.
        """
        self._meas['timestamp'] = datetime.now()
        for key, value in self._tags.items():
            # Lê 1 registrador (holding register) por vez no endereço da tag
            result = self._modbusClient.read_holding_registers(value['addr'], 1)
            if result is not None:
                self._meas['values'][key] = result[0]

    def updateGUI(self):
        """
        Método para atualização da interface gráfica a partir dos dados lidos.
        """
        # atualização dos labels
        for key, tag_info in self._tags.items():
            if key in self._meas['values']:
                valor = self._meas['values'][key]
                unidade = tag_info['unit']
                # Atualiza o ID correspondente na interface Kivy
                self.ids[key].text = f"{valor}{unidade}"

    def stopRefresh(self):
        """ 
        Para o loop da Thread de forma segura ao fechar o app. 
        """
        self._updateWidgets = False

