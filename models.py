from db import Base
from sqlalchemy import Column, Integer, DateTime, Float
from datetime import datetime

class CompData(Base):
    """
    Modelo dos dados do CLP
    """
    __tablename__ = 'dados_comp'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now)

    # variáveis principais de monitoramento

    fit_03 = Column(Float)
    torque = Column(Float)
    velocidade = Column(Float)
    pressao = Column(Float)
    valvulas = Column(Integer)

    temp_carc = Column(Float)
    freq_rede = Column(Float)
    ddp_rs = Column(Float)
    ddp_st = Column(Float)
    ddp_tr = Column(Float)
    corrente_r = Column(Float)
    corrente_s = Column(Float)
    corrente_t = Column(Float)
    corrente_n = Column(Float)
    corrente_med = Column(Float)
    pot_ativa_r = Column(Float)
    pot_ativa_s = Column(Float)
    pot_ativa_t = Column(Float)
    pot_ativa_tot = Column(Float)
    pot_reativa_tot = Column(Float)
    pot_aparente_tot = Column(Float)
    demanda_ant = Column(Float)
    demanda_atual = Column(Float)
    demanda_med = Column(Float)
    demanda_prev = Column(Float)
    fat_pot_tot = Column(Float)