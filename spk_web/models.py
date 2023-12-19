from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class leptop(Base):
    def __init__(self):
        self.leptop = pd.read_csv('ml-latest-small/tbl_laptop.csv')
        self.lpt = self.leptop.to_numpy()
        
    __tablename__ = "tbl_leptop"
    no = Column(Integer, primary_key=True)
    brand = Column(String(255))
    ram = Column(String(255))
    cpu = Column(String(255))
    gpu = Column(String(255))
    baterai = Column(String(255))
    harga = Column(String(255))
    ukuran_layar = Column(String(255))

    def __init__(self, brand, ram, cpu, gpu, baterai, harga, ukuran_layar):
        self.type = type
        self.brand = brand
        self.ram = ram
        self.cpu = cpu
        self.gpu = gpu
        self.baterai = baterai
        self.harga = harga
        self.ukuran_layar = ukuran_layar

    def calculate_score(self, dev_scale):
        score = 0
        score += self.ram * dev_scale['ram']
        score += self.cpu * dev_scale['cpu']
        score += self.gpu * dev_scale['gpu']
        score += self.baterai * dev_scale['baterai']
        score -= self.harga * dev_scale['harga']
        score += self.ukuran_layar * dev_scale['ukuran_layar']
        return score

    def __repr__(self):
        return f"leptop(type={self.type!r}, brand={self.brand!r}, ram={self.ram!r}, cpu={self.cpu!r}, gpu={self.gpu!r}, baterai={self.baterai!r}, harga={self.harga!r}, ukuran_layar={self.ukuran_layar!r})"
