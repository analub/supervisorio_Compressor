from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup, ComandoPopup, MedidasPopup, TemperaturaPopup, GraficoPopup, BancoDadosPopup
from timeseriesgraph import TimeSeriesGraph
from pyModbusTCP.client import ModbusClient # Importa a classe responsável por conectar o supervisório ao servidor Modbus TCP
from kivy.core.window import Window # Permite controlar propriedades da janela, como o cursor do mouse
from threading import Thread # Permite rodar funções em segundo plano sem travar a interface
from time import sleep # Utilizado para criar intervalos de tempo entre as leituras
from datetime import datetime
import struct

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
        GRAY_COLOR = (0.5, 0.5, 0.5, 1)
        super().__init__()
        # Configurações iniciais recebidas da main.py
        self._scan_time = kwargs.get('scan_time')
        
        self._comandoPopup = ComandoPopup()
        self._medidasPopup = MedidasPopup()
        self._temperaturaPopup = TemperaturaPopup()
        self._graficoPopup = GraficoPopup()
        self._bancoDadosPopup = BancoDadosPopup()        
        self._serverIP = kwargs.get('server_ip')
        self._serverPort = kwargs.get('server_port')

        # Instancia os componentes de interface e comunicação
        self._scanPopup = ScanPopup(scantime=self._scan_time)
        self._modbusPopup = ModbusPopup(self._serverIP, self._serverPort)
        self._modbusClient = ModbusClient(host=self._serverIP, port=self._serverPort)
        
        # Estrutura de dados para armazenar as medições em tempo real
        self._meas = {'timestamp': None, 'values': {}}

        # Mapeamento de tipos, divisores e unidades
        self._tag_setup = {
            # Tags que são Floating Point (FP) - 32 bits / 2 registradores
            'vel_motor': {'type': 'fp', 'div': 1, 'unit': ' RPM'},
            'torque_motor': {'type': 'fp', 'div': 1, 'unit': ' Nm'},
            'pressao_reservatorio': {'type': 'fp', 'div': 1, 'unit': ' bar'},
            'vazao_valvulas': {'type': 'fp', 'div': 1, 'unit': ' m³/h'},
            'temp_carcaca': {'type': 'fp', 'div': 10, 'unit': ' ºC'}, # FP que ainda precisa dividir por 10

            # Tags que são Inteiros (4X) - 16 bits / 1 registrador + Divisor
            'freq_rede': {'type': 'int', 'div': 100, 'unit': ' Hz'},
            'ddp_rs': {'type': 'int', 'div': 10, 'unit': ' V'},
            'ddp_st': {'type': 'int', 'div': 10, 'unit': ' V'},
            'ddp_tr': {'type': 'int', 'div': 10, 'unit': ' V'},
            'corr_r': {'type': 'int', 'div': 10, 'unit': ' A'},
            'corr_s': {'type': 'int', 'div': 10, 'unit': ' A'},
            'corr_t': {'type': 'int', 'div': 10, 'unit': ' A'},
            'corr_neutro': {'type': 'int', 'div': 10, 'unit': ' A'},
            'corr_media': {'type': 'int', 'div': 10, 'unit': ' A'},
            'fp_total': {'type': 'int', 'div': 1000, 'unit': ''},
            'dem_anterior': {'type': 'int', 'div': 10, 'unit': ' kW'},
            'dem_atual': {'type': 'int', 'div': 10, 'unit': ' kW'},
            'dem_media': {'type': 'int', 'div': 10, 'unit': ' kW'},
            'dem_prevista': {'type': 'int', 'div': 10, 'unit': ' kW'},
            'pot_ativa_total': {'type': 'int', 'div': 1, 'unit': ' kW'},
            'pot_reativa_total': {'type': 'int', 'div': 1, 'unit': ' kVAr'},
            'pot_aparente_total': {'type': 'int', 'div': 1, 'unit': ' kVA'},
            'pot_ativa_r': {'type': 'int', 'div': 1, 'unit': ' kW'},
            'pot_ativa_s': {'type': 'int', 'div': 1, 'unit': ' kW'},
            'pot_ativa_t': {'type': 'int', 'div': 1, 'unit': ' kW'}
        }

        # Organiza as configurações de cada sensor (Endereço, Cor no Gráfico, Tipo, Divisor e Unidade)
        for key, value in kwargs.get('modbus_addrs').items():
            # Adicionamos as informações de tratamento na tag
            setup = self._tag_setup.get(key, {'type': 'int', 'div': 1, 'unit': ''})
            self._tags[key] = {
                'addr': value, 
                'color': setup.get('color', GRAY_COLOR),
                **setup  # Isso "descompacta" todas as chaves do setup para dentro de _tags[key]
            }

    def registers_to_float(self, registers):
        """
        Converte 2 registradores de 16 bits em 1 float de 32 bits 
        """
        packed = struct.pack('>HH', *registers)
        return struct.unpack('>f', packed)[0]

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
            if self._modbusClient.is_open:
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
        for key, tag in self._tags.items():
            try:
                # LER DADOS DO TIPO FP (MOTOR, TORQUE, PRESSÃO)
                if tag['type'] == 'fp':
                    result = self._modbusClient.read_holding_registers(tag['addr'], 2)
                    if result:
                        self._meas['values'][key] = self.registers_to_float(result) / tag['div']

                # LER DADOS DO TIPO INT (FREQ, DDP, CORRENTE, ETC)
                else:
                    result = self._modbusClient.read_holding_registers(tag['addr'], 1)
                    if result:
                        self._meas['values'][key] = result[0] / tag['div']

            except Exception as e:
                print(f"Erro na leitura da tag {key}: {e.args}")

    def updateGUI(self):
        """
        Método para atualização da interface gráfica a partir dos dados lidos.
        """
        for key, tag_info in self._tags.items():
            if key in self._meas['values']:
                valor = self._meas['values'][key]
                unidade = tag_info.get('unit', '')
                # Formata para 2 casas decimais se for float ou tiver divisor
                if tag_info['div'] > 1 or tag_info['type'] == 'fp':
                    self.ids[key].text = f"{valor:.2f}{unidade}"
                else:
                    self.ids[key].text = f"{int(valor)}{unidade}"

    def stopRefresh(self):
        """ 
        Para o loop da Thread de forma segura ao fechar o app. 
        """
        self._updateWidgets = False

