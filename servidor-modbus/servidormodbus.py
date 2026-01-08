from pyModbusTCP.server import DataBank, ModbusServer
from time import sleep
import random

class ServidorMODBUS():
    """
    Classe Servidor MODBUS
    """
    def __init__(self, host_ip,port):
        """
        Construtor
        """

        self._server =  ModbusServer(host=host_ip, port=port,no_block=True)
    
    def run(self):
        """
         Execução do servidor
        """
        self._server.start()
        print("Servidor em execução...")
        while True:
            # 1. DADOS PRINCIPAIS
            self._server.data_bank.set_holding_registers(884, [random.randrange(1000, 1800)])   # Velocidade motor
            self._server.data_bank.set_holding_registers(1420, [random.randrange(50, 200)])    # Torque
            self._server.data_bank.set_holding_registers(714, [random.randrange(0, 100)])      # Pressão/Vazão
            self._server.data_bank.set_holding_registers(716, [random.randrange(0, 50)])       # Vazão válvulas 2-6

            # 2. TEMPERATURA E FREQUÊNCIA
            self._server.data_bank.set_holding_registers(706, [random.randrange(30, 80)])      # Temp. Carcaça
            self._server.data_bank.set_holding_registers(830, [60])                            # Freq. Rede (60Hz)

            # 3. TENSÕES (DDP)
            self._server.data_bank.set_holding_registers(847, [random.randrange(210, 230)])   # Fase RS
            self._server.data_bank.set_holding_registers(848, [random.randrange(210, 230)])   # Fase ST
            self._server.data_bank.set_holding_registers(849, [random.randrange(210, 230)])   # Fase TR

            # 4. CORRENTES
            self._server.data_bank.set_holding_registers(840, [random.randrange(5, 15)])       # Corrente R
            self._server.data_bank.set_holding_registers(841, [random.randrange(5, 15)])       # Corrente S
            self._server.data_bank.set_holding_registers(842, [random.randrange(5, 15)])       # Corrente T
            self._server.data_bank.set_holding_registers(843, [0])                             # Corrente Neutro
            self._server.data_bank.set_holding_registers(845, [random.randrange(5, 15)])       # Corrente Média

            # 5. POTÊNCIAS E FATOR DE POTÊNCIA
            self._server.data_bank.set_holding_registers(855, [random.randrange(2000, 5000)]) # Ativa Total
            self._server.data_bank.set_holding_registers(859, [random.randrange(100, 500)])   # Reativa Total
            self._server.data_bank.set_holding_registers(863, [random.randrange(2000, 5000)]) # Aparente Total
            self._server.data_bank.set_holding_registers(871, [92])                            # Fator Potência (0.92)

            # 6. DEMANDA
            self._server.data_bank.set_holding_registers(1204, [1500])                         # Demanda Anterior
            self._server.data_bank.set_holding_registers(1205, [random.randrange(1500, 2000)]) # Demanda Atual
            self._server.data_bank.set_holding_registers(1206, [1700])                         # Demanda Média
            self._server.data_bank.set_holding_registers(1208, [2100])
            
            sleep(1)
            
        


