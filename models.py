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