from http import HTTPStatus
from flask import Flask, request, abort
from flask_restful import Resource, Api
from models import leptop as LeptopModel
from engine import engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from tabulate import tabulate

session = Session(engine)

app = Flask(__name__)
api = Api(app)


class BaseMethod():

    def __init__(self):
        self.raw_weight = {'ram': 4, 'cpu': 3, 'gpu': 4, 'baterai': 3, 'harga': 5, 'ukuran_layar': 4}

    @property
    def weight(self):
        total_weight = sum(self.raw_weight.values())
        return {k: round(v/total_weight, 2) for k, v in self.raw_weight.items()}

    @property
    def data(self):
        query = select(LeptopModel.no, LeptopModel.brand, LeptopModel.ram, LeptopModel.cpu, LeptopModel.gpu,
                       LeptopModel.baterai, LeptopModel.harga, LeptopModel.ukuran_layar)
        result = session.execute(query).fetchall()
        print(result)
        return [{'no': leptop.no, 'brand': leptop.brand, 'ram': leptop.ram, 'cpu': leptop.cpu,
                'gpu': leptop.gpu, 'baterai': leptop.baterai, 'harga': leptop.harga, 'ukuran_layar': leptop.ukuran_layar} for leptop in result]

    @property
    def normalized_data(self):
        # x/max [benefit]
        # min/x [cost]
        ram_values = []  # max
        cpu_values = []  # max
        gpu_values = []  # max
        baterai_values = []  # max
        harga_values = []  # min
        ukuran_layar_values = []  # max

        for data in self.data:
            # RAM
            ram_spec = data['ram']
            ram_numeric_values = [
                int(value) for value in ram_spec.split() if value.isdigit()]
            max_ram_value = max(
                ram_numeric_values) if ram_numeric_values else 1
            ram_values.append(max_ram_value)

            # cpu
            cpu_spec = data['cpu']
            cpu_numeric_values = [
                int(value) for value in cpu_spec.split() if value.isdigit()]
            max_cpu_value = max(
                cpu_numeric_values) if cpu_numeric_values else 1
            cpu_values.append(max_cpu_value)

            # gpu
            gpu_spec = data['gpu']
            numeric_values = [int(value.split()[0]) for value in gpu_spec.split(
                ',') if value.split()[0].isdigit()]
            max_gpu_value = max(numeric_values) if numeric_values else 1
            gpu_values.append(max_gpu_value)

            # Baterai
            baterai_spec = data['baterai']
            baterai_numeric_values = [int(
                value.split()[0]) for value in baterai_spec.split() if value.split()[0].isdigit()]
            max_baterai_value = max(
                baterai_numeric_values) if baterai_numeric_values else 1
            baterai_values.append(max_baterai_value)

            # Harga
            harga_cleaned = ''.join(
                char for char in data['harga'] if char.isdigit())
            harga_values.append(float(harga_cleaned)
                                if harga_cleaned else 0)  # Convert to float

            # Layar
            ukuran_layar_spec = data['ukuran_layar']
            ukuran_layar_numeric_values = [float(value.split()[0]) for value in ukuran_layar_spec.split(
            ) if value.replace('.', '').isdigit()]
            max_ukuran_layar_value = max(
                ukuran_layar_numeric_values) if ukuran_layar_numeric_values else 1
            ukuran_layar_values.append(max_ukuran_layar_value)


        return [
            {'no': data['no'],
             'brand': data['brand'],
             'ram': ram_value / max(ram_values),
             'cpu': cpu_value / max(cpu_values),
             'gpu': gpu_value / max(gpu_values),
             'baterai': baterai_value / max(baterai_values),
             # To avoid division by zero
             'harga': min(harga_values) / max(harga_values) if max(harga_values) != 0 else 0,
             'ukuran_layar': ukuran_layar_value / max(ukuran_layar_values)
             }
            for data, ram_value, cpu_value, gpu_value, baterai_value, harga_value, ukuran_layar_value
            in zip(self.data, ram_values, cpu_values, gpu_values, baterai_values, harga_values, ukuran_layar_values)
        ]

    def update_weights(self, new_weights):
        self.raw_weight = new_weights


class WeightedProductCalculator(BaseMethod):
    def update_weights(self, new_weights):
        self.raw_weight = new_weights

    @property
    def calculate(self):
        normalized_data = self.normalized_data
        produk = [
            {
                'no': row['no'],
                'produk': row['ram']**self.weight['ram'] *
                row['cpu']**self.weight['cpu'] *
                row['gpu']**self.weight['gpu'] *
                row['baterai']**self.weight['baterai'] *
                row['harga']**self.weight['harga'] *
                row['ukuran_layar']**self.weight['ukuran_layar'],
                'brand': row.get('brand', '')
            }
            for row in normalized_data
        ]
        sorted_produk = sorted(produk, key=lambda x: x['produk'], reverse=True)
        sorted_data = [
            {
                'ID': product['no'],
                'brand': product['brand'],
                'score': round(product['produk'], 3)
            }
            for product in sorted_produk
        ]
        return sorted_data


class WeightedProduct(Resource):
    def get(self):
        calculator = WeightedProductCalculator()
        result = calculator.calculate
        return sorted(result, key=lambda x: x['score'], reverse=True), HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        calculator = WeightedProductCalculator()
        calculator.update_weights(new_weights)
        result = calculator.calculate
        return {'laptop': sorted(result, key=lambda x: x['score'], reverse=True)}, HTTPStatus.OK.value


class SimpleAdditiveWeightingCalculator(BaseMethod):
    @property
    def calculate(self):
        weight = self.weight
        result = [
            {
                'no': row['no'],
                'brand': row.get('brand'),
                'Score': round(row['ram'] * weight['ram'] +
                               row['cpu'] * weight['cpu'] +
                               row['gpu'] * weight['gpu'] +
                               row['baterai'] * weight['baterai'] +
                               row['harga'] * weight['harga'] +
                               row['ukuran_layar'] * weight['ukuran_layar'], 3)
            }
            for row in self.normalized_data
        ]
        sorted_result = sorted(result, key=lambda x: x['Score'], reverse=True)
        return sorted_result

    def update_weights(self, new_weights):
        self.raw_weight = new_weights


class SimpleAdditiveWeighting(Resource):
    def get(self):
        saw = SimpleAdditiveWeightingCalculator()
        result = saw.calculate
        return sorted(result, key=lambda x: x['Score'], reverse=True), HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        saw = SimpleAdditiveWeightingCalculator()
        saw.update_weights(new_weights)
        result = saw.calculate
        return {'laptop': sorted(result, key=lambda x: x['Score'], reverse=True)}, HTTPStatus.OK.value


api.add_resource(WeightedProduct, '/wp')
api.add_resource(SimpleAdditiveWeighting, '/saw')

if __name__ == '__main__':
    app.run(port='5005', debug=True)