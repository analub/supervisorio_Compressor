from kivy.app import App
from mainwidget import MainWidget
from kivy.lang.builder import Builder

# Carregamento dos arquivos de interface gráfica (.kv)
Builder.load_file("mainwidget.kv")
Builder.load_file("widgets_auxiliares.kv")
Builder.load_file("popups.kv")

class MainApp(App):
    """
    Classe principal do aplicativo.
    """
    def build(self):    
        """
        Método que gera o aplicativo com base no widget principal.
        """
        # Passamos o IP e a Porta do servidor como argumentos.
        # Isso permite que o MainWidget já inicie configurado para o localhost (127.0.0.1).
        self._widget = MainWidget(scan_time=1000, server_ip='10.15.30.182', server_port=502, modbus_addrs = {
            # --- DADOS PRINCIPAIS ---
            'vel_motor': 884,         # Velocidade do motor
            'torque_motor': 1420,           # Torque
            'pressao_reservatorio': 714,     # Pressão (vazão)
            'vazao_valvulas': 716,    # Vazão no ramo das válvulas 2 a 6

            # --- DADOS SECUNDÁRIOS ---
            'temp_carcaca': 706,      # Temperatura da carcaça
            'freq_rede': 830,         # Frequência da rede
            
            # Tensões (DDP)
            'ddp_rs': 847,            # DDP fase RS
            'ddp_st': 848,            # DDP fase ST
            'ddp_tr': 849,            # DDP fase TR

            # Correntes
            'corr_r': 840,            # Corrente fase R
            'corr_s': 841,            # Corrente fase S
            'corr_t': 842,            # Corrente fase T
            'corr_neutro': 843,       # Corrente Neutro
            'corr_media': 845,        # Corrente média

            # Potências Totais
            'pot_ativa_total': 855,   # Potência ativa total
            'pot_reativa_total': 859, # Potência reativa total
            'pot_aparente_total': 863, # Potência aparente total

            # Demanda
            'dem_anterior': 1204,     # Demanda anterior
            'dem_atual': 1205,        # Demanda atual
            'dem_media': 1206,        # Demanda média
            'dem_prevista': 1208,     # Demanda prevista

            # Potências por Fase
            'pot_ativa_r': 852,       # Potência ativa fase R
            'pot_ativa_s': 853,       # Potência ativa fase S
            'pot_ativa_t': 854,       # Potência ativa fase T

            # Fator de Potência
            'fp_total': 871,          # Fator de potência total

            # --- VÁLVULAS (Todas no endereço 712) ---
            'XV_2': 712,
            'XV_3': 712,
            'XV_4': 712,
            'XV_5': 712,
            'XV_6': 712
        })
        return self._widget
    
    def on_stop(self):
        """
        Garante que a Thread de leitura seja encerrada ao fechar a janela, 
        evitando que o processo continue rodando em segundo plano.
        """
        self._widget.stopRefresh()
    
if __name__ == "__main__":
    #Builder.load_string(open("mainwidget.kv", encoding="utf-8").read(), rulesonly=True)
    MainApp().run() 
