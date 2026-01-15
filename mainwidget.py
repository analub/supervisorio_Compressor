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


class MainWidget(BoxLayout):
    """
    Widget principal do aplicativo
    """
    # Estado inicial das imagens (motor e conexão -> planta desligada)
    motor_ligado = BooleanProperty(False)
     # False = fechada | True = aberta
    valvulas = ListProperty([False, False, False, False, False])

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

        # Mapeamento de tipos e divisores
        self._tag_setup = {
            # Tags que são Floating Point (FP) - 32 bits / 2 registradores
            'vel_motor': {'type': 'fp', 'div': 1},
            'torque_motor': {'type': 'fp', 'div': 1},
            'pressao_reservatorio': {'type': 'fp', 'div': 1},
            'vazao_valvulas': {'type': 'fp', 'div': 1},
            'temp_carcaca': {'type': 'fp', 'div': 10}, # FP que ainda precisa dividir por 10

            # Tags que são Inteiros (4X) - 16 bits / 1 registrador + Divisor
            'freq_rede': {'type': 'int', 'div': 100},
            'ddp_rs': {'type': 'int', 'div': 10},
            'ddp_st': {'type': 'int', 'div': 10},
            'ddp_tr': {'type': 'int', 'div': 10},
            'corr_r': {'type': 'int', 'div': 10},
            'corr_s': {'type': 'int', 'div': 10},
            'corr_t': {'type': 'int', 'div': 10},
            'corr_neutro': {'type': 'int', 'div': 10},
            'corr_media': {'type': 'int', 'div': 10},
            'fp_total': {'type': 'int', 'div': 1000},
            'dem_anterior': {'type': 'int', 'div': 10},
            'dem_atual': {'type': 'int', 'div': 10},
            'dem_media': {'type': 'int', 'div': 10},
            'dem_prevista': {'type': 'int', 'div': 10}

            # # Válvulas e seus respectivos bits (conforme a tabela do CLP)
            # 'XV_2': {'type': 'bit', 'bit': 1},
            # 'XV_3': {'type': 'bit', 'bit': 2},
            # 'XV_4': {'type': 'bit', 'bit': 3},
            # 'XV_5': {'type': 'bit', 'bit': 4},
            # 'XV_6': {'type': 'bit', 'bit': 5}
            
            # As demais potências são Divisor 1 (valor direto)
        }

        # Mapeamento de unidades de medida da planta de compressão
        units = {
            'vel_motor': ' RPM', 
            'torque_motor': ' Nm', 
            'pressao_reservatorio': ' bar', 
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
            if key in ['vel_motor', 'torque_motor', 'pressao_reservatorio']:
                plot_color = (1, 0, 0, 1) # Vermelho (Principais)
            elif 'ddp' in key:
                plot_color = (0, 0, 1, 1) # Azul (Tensões)
            elif 'corr' in key:
                plot_color = (1, 0.5, 0, 1) # Laranja (Correntes)
            else:
                plot_color = (0, 1, 0, 1) # Verde (Outros)
            # Adicionamos as informações de tratamento na tag
            setup = self._tag_setup.get(key, {'type': 'int', 'div': 1}) # Padrão é inteiro div 1
            self._tags[key] = {
                'addr': value, 
                'color': plot_color, 
                'unit': units.get(key, ''),
                'type': setup['type'],
                'div': setup['div']
            }

    def registers_to_float(self, registers):
        """
        Converte 2 registradores de 16 bits em 1 float de 32 bits 
        """
        packed = struct.pack('>HH', *registers)
        return struct.unpack('>f', packed)[0]
    
    # def sendCommand(self, key, value):
    #     """
    #     Envia um comando de escrita para o servidor Modbus.
    #     key: ID da tag (ex: 'XV_2')
    #     value: 0 para Abrir, 1 para Fechar
    #     """
    #     try:
    #         if not self._modbusClient.is_open():
    #             print("Erro: Cliente Modbus desconectado.")
    #             return

    #         tag = self._tags.get(key)
    #         if tag and tag['type'] == 'bit':
    #             # --- Lógica de Escrita em Bit (Read-Modify-Write) ---
    #             # 1. Lê o valor atual do registrador (16 bits)
    #             current_value = self._modbusClient.read_holding_registers(tag['addr'], 1)
                
    #             if current_value:
    #                 new_val = current_value[0]
    #                 bit_pos = tag['bit']
                    
    #                 if value == 1: # Fechar (Setar bit para 1)
    #                     new_val |= (1 << bit_pos)
    #                 else:          # Abrir (Zerar bit para 0)
    #                     new_val &= ~(1 << bit_pos)
                    
    #                 # 2. Escreve o novo valor inteiro de volta no endereço
    #                 success = self._modbusClient.write_single_register(tag['addr'], new_val)
    #                 if success:
    #                     print(f"Comando enviado com sucesso para {key}: {value}")
    #                 else:
    #                     print(f"Falha ao enviar comando para {key}")

    #         elif tag and tag['type'] == 'int':
    #             # Escrita simples para inteiros (ex: Setpoint)
    #             self._modbusClient.write_single_register(tag['addr'], int(value * tag['div']))

    #     except Exception as e:
    #         print(f"Erro ao enviar comando: {e.args}")

    def startDataRead(self, ip, port):
        """
        Configura o IP/Porta e inicia a Thread de leitura se a conexão for aberta.
        """
        self._serverIP = ip
        self._serverPort = port
        self._modbusClient.host = self._serverIP
        self._modbusClient.port = self._serverPort
        print("conectou bbs")
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
                # LER DADOS DO TIPO BIT (VÁLVULAS)
                if tag['type'] == 'bit':
                    result = self._modbusClient.read_holding_registers(tag['addr'], 1)
                    if result:
                        # EXTRAÇÃO DO BIT:
                        # 1. Pegamos o valor (ex: 712)
                        # 2. Deslocamos os bits para a direita (>>) até o bit que queremos
                        # 3. Fazemos um AND (& 1) para isolar apenas aquele bit
                        status_bit = (result[0] >> tag['bit']) & 1
                        self._meas['values'][key] = status_bit

                # LER DADOS DO TIPO FP (MOTOR, TORQUE, PRESSÃO)
                elif tag['type'] == 'fp':
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
                unidade = tag_info['unit']
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

    def toggle_motor(self):
        """
        Método que muda o estado do motor. Usado para mudar a imagem da planta
        """
        self.motor_ligado = not self.motor_ligado

    def toggle_valvula(self, idx):
        
        estados = self.valvulas[:]
        estados[idx] = not estados[idx]
        self.valvulas = estados
        
