from pyModbusTCP.server import DataBank, ModbusServer
from time import sleep
import random
import struct

class ServidorMODBUS():
    """
    Classe Servidor MODBUS
    """
    def __init__(self, host_ip,port):
        """
        Construtor
        """
        self._server =  ModbusServer(host=host_ip, port=port,no_block=True)

    def float_to_registers(self, value):
        """
        Converte um valor float (32 bits) em dois registradores de 16 bits (padrão IEEE 754)
        """
        # '>' indica Big-Endian, 'f' indica float
        packed_float = struct.pack('>f', value)
        # 'H' indica unsigned short (16 bits)
        return struct.unpack('>HH', packed_float)
    
    def run(self):
        """
        Execução do servidor
        """
        self._server.start()
        print("Servidor em execução...")

        while True:
            # --- 1. DADOS PRINCIPAIS (FLOAT - 2 REGISTRADORES) ---
            # Velocidade motor (884), Torque (1420), Pressão (714), Vazão (716)
            self._server.data_bank.set_holding_registers(884, list(self.float_to_registers(random.uniform(1000.0, 1800.0))))
            self._server.data_bank.set_holding_registers(1420, list(self.float_to_registers(random.uniform(50.0, 200.0))))
            self._server.data_bank.set_holding_registers(714, list(self.float_to_registers(random.uniform(6.0, 8.5)))) # Ex: 7.2 bar
            self._server.data_bank.set_holding_registers(716, list(self.float_to_registers(random.uniform(20.0, 45.0))))

            # --- 2. DADOS SECUNDÁRIOS ESCALONADOS (TIPO 4X COM DIVISOR) ---
            # Nota: Multiplicamos pelo DIV para que o supervisório divida e tenha a casa decimal
            
            # Temperatura Carcaça (706) - FP mas com Div 10 na tabela
            temp_raw = random.uniform(35.0, 65.0) * 10
            self._server.data_bank.set_holding_registers(706, list(self.float_to_registers(temp_raw)))
            
            # Frequência Rede (830) - Div 100 -> 60Hz vira 6000
            self._server.data_bank.set_holding_registers(830, [int(60.0 * 100)])

            # Tensões ddp (847, 848, 849) - Div 10
            self._server.data_bank.set_holding_registers(847, [int(random.uniform(218, 222) * 10)])
            self._server.data_bank.set_holding_registers(848, [int(random.uniform(218, 222) * 10)])
            self._server.data_bank.set_holding_registers(849, [int(random.uniform(218, 222) * 10)])

            # Correntes (840-845) - Div 10
            self._server.data_bank.set_holding_registers(840, [int(random.uniform(8, 12) * 10)])
            self._server.data_bank.set_holding_registers(841, [int(random.uniform(8, 12) * 10)])
            self._server.data_bank.set_holding_registers(842, [int(random.uniform(8, 12) * 10)])
            self._server.data_bank.set_holding_registers(843, [0]) # Neutro
            self._server.data_bank.set_holding_registers(845, [int(10.5 * 10)])

            # Fator de Potência (871) - Div 1000 -> 0.92 vira 920
            self._server.data_bank.set_holding_registers(871, [int(0.92 * 1000)])

            # --- 3. DADOS SEM ESCALONAMENTO (DIV 1) ---
            # Potências (855, 859, 863, 852, 853, 854)
            self._server.data_bank.set_holding_registers(855, [random.randint(3000, 4500)]) # Ativa Total
            self._server.data_bank.set_holding_registers(859, [random.randint(200, 400)])   # Reativa
            self._server.data_bank.set_holding_registers(863, [random.randint(3000, 4500)]) # Aparente
            self._server.data_bank.set_holding_registers(852, [1200]) # Ativa R
            self._server.data_bank.set_holding_registers(853, [1200]) # Ativa S
            self._server.data_bank.set_holding_registers(854, [1200]) # Ativa T

            # Demandas (1204-1208) - Div 10
            self._server.data_bank.set_holding_registers(1204, [int(1500 * 10)])
            self._server.data_bank.set_holding_registers(1205, [int(random.randint(1500, 1800) * 10)])
            self._server.data_bank.set_holding_registers(1206, [int(1600 * 10)])
            self._server.data_bank.set_holding_registers(1208, [int(2000 * 10)])
            
            sleep(1)
            
        


