from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup, ComandoPopup, MedidasPopup, TemperaturaPopup, GraficoPopup, BancoDadosPopup
from timeseriesgraph import TimeSeriesGraph
from pyModbusTCP.client import ModbusClient # Importa a classe responsável por conectar o supervisório ao servidor Modbus TCP
from kivy.core.window import Window # Permite controlar propriedades da janela, como o cursor do mouse
from threading import Thread # Permite rodar funções em segundo plano sem travar a interface
from time import sleep # Utilizado para criar intervalos de tempo entre as leituras
from datetime import datetime
import struct
from kivy.properties import BooleanProperty
from kivy.properties import ListProperty
from kivy.uix.floatlayout import FloatLayout
from db import Session
from models import CompData

class MainWidget(BoxLayout):
    """
    Widget principal do aplicativo
    """
    # Estado inicial das imagens (motor e conexão -> planta desligada)
    motor_ligado = BooleanProperty(False)
     # False = fechada | True = aberta
    valvulas = ListProperty([False, False, False, False, False])
    conectado = BooleanProperty(False)

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
        self._partida_type = ''

        self._session = Session() # Cria conexão com o Banco de Dados
        
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
            'dem_anterior': {'type': 'int', 'div': 1, 'unit': ' W'},
            'dem_atual': {'type': 'int', 'div': 1, 'unit': ' W'},
            'dem_media': {'type': 'int', 'div': 1, 'unit': ' W'},
            'dem_prevista': {'type': 'int', 'div': 1, 'unit': ' W'},
            'pot_ativa_total': {'type': 'int', 'div': 1, 'unit': ' W'},
            'pot_reativa_total': {'type': 'int', 'div': 1, 'unit': ' VAr'},
            'pot_aparente_total': {'type': 'int', 'div': 1, 'unit': ' VA'},
            'pot_ativa_r': {'type': 'int', 'div': 1, 'unit': ' W'},
            'pot_ativa_s': {'type': 'int', 'div': 1, 'unit': ' W'},
            'pot_ativa_t': {'type': 'int', 'div': 1, 'unit': ' W'},

            # Tags de comando
            'tipo_motor': {'type': 'int', 'div': 1},
            'indica_driver': {'type': 'int', 'div': 1},
            'sel_driver': {'type': 'int', 'div': 1},
            'tesys': {'type': 'int', 'div': 1},
            'atv31': {'type': 'int', 'div': 1},
            'ats48': {'type': 'int', 'div': 1},
            'ats48_dcc': {'type': 'int', 'div': 1},
            'ats48_acc': {'type': 'int', 'div': 1},
            'atv31_velocidade': {'type': 'int', 'div': 10},
            'habilita': {'type': 'bit', 'div': 1}
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
        packed = struct.pack('>HH', registers[1], registers[0]) 
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
                self.conectado = True  #conexao ok -> aparece imagem na tela
                self._updateThread = Thread(target=self.updater)
                self._updateThread.start()
                # Atualiza a interface indicando sucesso
                self.ids.img_con.source = 'imgs/conectado.png'
                self._modbusPopup.dismiss()
            else:
                self.conectado = False          #erro de conexão -> aparece imagem vermelha
                self._modbusPopup.setInfo("Falha na conexão com o servidor.")
        except Exception as e:
            self.conectado = False              #erro -> imagem vermelha  
            print("Erro: ", e.args)

    def updater(self):
        """
        Loop de execução em segundo plano para leitura de dados e atualização da tela.
        """
        try:
            while self._updateWidgets:
                self.readData()
                self.updateGUI()
                self.save_data()
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
        for key, tag_info in self._tags.items():
            if key in self._meas['values']:
                valor = self._meas['values'][key]
                unidade = tag_info.get('unit', '')
                
                # Formatação do texto
                if tag_info['type'] == 'bit':
                    txt = "FECHADA" if valor == 1 else "ABERTA"
                elif tag_info['div'] > 1 or tag_info['type'] == 'fp':
                    txt = f"{valor:.2f}{unidade}"
                else:
                    txt = f"{int(valor)}{unidade}"

                # --- ATUALIZAÇÃO INDEPENDENTE ---
                
                # 1. Atualiza a Tela Principal
                if key in self.ids:
                    self.ids[key].text = txt
                
                # 2. Atualiza o Popup de Medidas
                if hasattr(self, '_medidasPopup') and key in self._medidasPopup.ids:
                    self._medidasPopup.ids[key].text = txt

                # 3. Atualiza o Popup de Temperatura (temp_carcaca)
                if hasattr(self, '_temperaturaPopup') and key in self._temperaturaPopup.ids:
                    self._temperaturaPopup.ids[key].text = txt

    def write_register(self, address, value):
        try:
            if self._modbusClient.is_open:
                self._modbusClient.write_single_register(address, value)
            else:
                print(f"[WARN] Modbus desconectado. Escrita ignorada ({address})")
        except Exception as e:
            print(f"[ERROR] Erro ao escrever registrador {address}: {e}")

    def save_data(self):
        """
        Salva os dados atuais lidos no Banco de Dados
        """
        try:
            data_to_save = {}
            data_to_save['timestamp'] = datetime.now()

            for key, value in self._meas['values'].items():
                data_to_save[key] = value
            
            dado = CompData(**data_to_save)
            self._session.add(dado)
            self._session.commit()
            print("Dados salvos no histórico") #debug

        except Exception as e:
            print("Erro ao salvar no Banco de Dados", e)
            self._session.rollback() #desfaz alterações em caso de erro

    def set_partida_type(self, partida_type):
        self._partida_type = partida_type

        partidas_map = {
            'direta': self._tags['tesys']['addr'],
            'softstart': self._tags['ats48']['addr'],
            'inversor': self._tags['atv31']['addr']
        }
        sel_driver_map = {'softstart': 1, 'inversor': 2, 'direta': 3}
        sel_driver_addr = self._tags['sel_driver']['addr']
        sel_value = sel_driver_map.get(partida_type, 3)

        if not self._modbusClient.is_open:
            print("[WARN] Modbus não conectado")
            return

        # Zera partidas não selecionadas
        for key, addr in partidas_map.items():
            if key != partida_type:
                self._modbusClient.write_single_register(addr, 0)

        # Escreve seleção
        self._modbusClient.write_single_register(sel_driver_addr, sel_value)

    def send_motor_command(self, command):
        command_map = {'liga': 1, 'desliga': 0, 'reset': 2}
        value = command_map.get(command)

        if value is None:
            return

        addr_map = {
            'direta': self._tags['tesys']['addr'],
            'softstart': self._tags['ats48']['addr'],
            'inversor': self._tags['atv31']['addr']
        }

        addr = addr_map.get(self._partida_type)

        if addr and self._modbusClient.is_open:
            self._modbusClient.write_single_register(addr, value)

    def stopRefresh(self):
        """ 
        Para o loop da Thread de forma segura ao fechar o app. 
        """
        self._updateWidgets = False

    def toggle_motor(self):
        """
        Método que muda o estado do motor. Usado para mudar a imagem da planta
        """
        self.motor_ligado = not self.motor_ligado

    def toggle_valvula(self, idx):
        
        estados = self.valvulas[:]
        estados[idx] = not estados[idx]
        self.valvulas = estados
        
