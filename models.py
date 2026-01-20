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

    vazao_valvulas = Column(Float)
    torque_motor = Column(Float)
    vel_motor = Column(Float)
    pressao_reservatorio = Column(Float)

    temp_carcaca = Column(Float)
    freq_rede = Column(Float)
    ddp_rs = Column(Float)
    ddp_st = Column(Float)
    ddp_tr = Column(Float)
    corr_r = Column(Float)
    corr_s = Column(Float)
    corr_t = Column(Float)
    corr_neutro = Column(Float)
    corr_media = Column(Float)
    pot_ativa_r = Column(Float)
    pot_ativa_s = Column(Float)
    pot_ativa_t = Column(Float)
    pot_ativa_total = Column(Float)
    pot_reativa_total = Column(Float)
    pot_aparente_total = Column(Float)
    dem_anterior = Column(Float)
    dem_atual = Column(Float)
    dem_media = Column(Float)
    dem_prevista = Column(Float)
    fp_total = Column(Float)