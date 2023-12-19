import sys

from colorama import Fore, Style
from models import Base, Laptop
from engine import engine

from sqlalchemy import select
from sqlalchemy.orm import Session
from settings import DEV_SCALE_nama_laptop,DEV_SCALE_prosesor,DEV_SCALE_grafis,DEV_SCALE_ram,DEV_SCALE_harga

session = Session(engine)

def create_table():
    Base.metadata.create_all(engine)
    print(f'{Fore.GREEN}[Success]: {Style.RESET_ALL}Database has created!')

class BaseMethod():

    def __init__(self):
        # 1-5
        self.raw_weight = {'nama_laptop': 5, 'prosesor': 4, 'grafis': 3,'ram': 3, 'harga': 2}

    @property
    def weight(self):
        total_weight = sum(self.raw_weight.values())
        return {k: round(v/total_weight, 2) for k,v in self.raw_weight.items()}

    @property
    def data(self):
        query = select(Laptop)
        return [{'id': laptop.id, 
        'nama_laptop': DEV_SCALE_nama_laptop[laptop.nama_laptop], 
        'prosesor': DEV_SCALE_prosesor[laptop.prosesor], 
        'grafis': DEV_SCALE_grafis[laptop.grafis],
        'ram': DEV_SCALE_ram[laptop.ram], 
        'harga': DEV_SCALE_harga[laptop.harga]} for laptop in session.scalars(query)]
    
    @property
    def normalized_data(self):
        # x/max [benefit]
        # min/x [cost]
        nama_laptops = [] # max
        prosesors = [] # max
        grafiss = [] # max
        rams = [] # max
        hargas = [] # min
        for data in self.data:
            nama_laptops.append(data['nama_laptop'])
            prosesors.append(data['prosesor'])
            grafiss.append(data['grafis'])
            rams.append(data['ram'])
            hargas.append(data['harga'])

        max_nama_laptop = max(nama_laptops)
        max_prosesor = max(prosesors)
        max_grafis = max(grafiss)
        max_ram = max(rams)
        min_harga = min(hargas)

        return [
            {   'id': data['id'],
                'nama_laptop': data['nama_laptop']/max_nama_laptop, # benefit
                'prosesor': data['prosesor']/max_prosesor, # benefit
                'grafis': data['grafis']/max_grafis, # benefit
                'ram': data['ram']/max_ram, # benefit
                'harga': min_harga/data['harga'] # cost
                }
            for data in self.data
        ]

    

class WeightedProduct(BaseMethod):
    @property
    def calculate(self):
        weight = self.weight
        # calculate data and weight[WP]
        result =  {row['id']:
            round(
                row['nama_laptop']**weight['nama_laptop'] *
                row['prosesor']**weight['prosesor'] *
                row['grafis']**weight['grafis'] *
                row['ram']**weight['ram'] *
                row['harga']**weight['harga'],
            2)
            for row in self.normalized_data
        }
        # sorting
        return dict(sorted(result.items(), key=lambda x:x[1], reverse=True))

class SimpleAdditiveWeighting(BaseMethod):
    
    @property
    def calculate(self):
        weight = self.weight
        # calculate data and weight
        result =  {row['id']:
            round(row['nama_laptop'] * weight['nama_laptop'] +
            row['prosesor'] * weight['prosesor'] +
            row['grafis'] * weight['grafis'] +
            row['ram'] * weight['ram'] +
            row['harga'] * weight['harga'], 2)
            for row in self.normalized_data
        }
        # sorting
        return dict(sorted(result.items(), key=lambda x:x[1]))

def run_saw():
    saw = SimpleAdditiveWeighting()
    print('result:', saw.calculate)

def run_wp():
    wp = WeightedProduct()
    print('result:', wp.calculate)
    pass

if len(sys.argv)>1:
    arg = sys.argv[1]

    if arg == 'create_table':
        create_table()
    elif arg == 'saw':
        run_saw()
    elif arg =='wp':
        run_wp()
    else:
        print('command not found')
