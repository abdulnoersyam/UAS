from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Laptop(Base):
    __tablename__ = 'laptop'
    id = Column(Integer, primary_key=True)
    nama_laptop = Column(String(50))
    prosesor = Column(String(50)) 
    grafis = Column(String(50))
    ram = Column(String(50))
    harga = Column(String(20))

    def __repr__(self):
        return f"Laptop(id={self.id!r}, nama_laptop={self.nama_laptop!r}"