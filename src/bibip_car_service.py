from datetime import datetime
from decimal import Decimal
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path
        for index_file in [
            "models_index.txt",
            "cars_index.txt",
            "sales_index.txt"
        ]:
            with open(f"{self.root_directory_path}/{index_file}", "a"):
                pass

    def add_model(self, model: Model) -> Model:
        models_index = {}
        with open(f"{self.root_directory_path}/models_index.txt", "r") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(':')
                    models_index[int(parts[0])] = int(parts[1])

        str_model = f'{model.id},{model.name},{model.brand}'
        str_model_500 = str_model.ljust(500) + "\n"
        with open(f"{self.root_directory_path}/models.txt", "a") as f:
            f.write(str_model_500)

        line_number = len(models_index) + 1
        models_index[model.id] = line_number

        with open(f"{self.root_directory_path}/models_index.txt", "w") as f:
            for id_, line_num in sorted(models_index.items()):
                f.write(f"{id_}:{line_num}\n")

        return model

    def add_car(self, car: Car) -> Car:
        cars_index = {}
        with open(f"{self.root_directory_path}/cars_index.txt", "r") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(':')
                    cars_index[parts[0]] = int(parts[1])

        str_car = (f'{car.vin},{car.model},{car.price},'
                   f'{car.date_start},{car.status.value}')
        str_car_500 = str_car.ljust(500) + "\n"
        with open(f"{self.root_directory_path}/cars.txt", "a") as f:
            f.write(str_car_500)

        line_number = len(cars_index) + 1
        cars_index[car.vin] = line_number

        with open(f"{self.root_directory_path}/cars_index.txt", "w") as f:
            for id_, line_num in sorted(cars_index.items()):
                f.write(f"{id_}:{line_num}\n")

        return car

    def sell_car(self, sale: Sale) -> Car:
        cars_index = {}
        with open(f"{self.root_directory_path}/cars_index.txt", "r") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(':')
                    cars_index[parts[0]] = int(parts[1])

        line_num = cars_index[sale.car_vin]

        with open(f"{self.root_directory_path}/cars.txt", "r+") as cars_file:
            cars_file.seek((line_num - 1) * 501)
            data = cars_file.read(500).strip().split(',')

            car = Car(
                vin=data[0],
                model=int(data[1]),
                price=Decimal(data[2]),
                date_start=datetime.strptime(data[3], "%Y-%m-%d %H:%M:%S"),
                status=CarStatus.sold
            )

            cars_file.seek((line_num - 1) * 501)
            updated_car = (
                f"{car.vin},{car.model},{car.price},"
                f"{car.date_start},{car.status.value}"
            ).ljust(500)
            cars_file.write(updated_car)

        str_sale = (f'{sale.sales_number},{sale.car_vin},'
                    f'{sale.sales_date},{sale.cost}')
        str_sale_500 = str_sale.ljust(500) + "\n"
        with open(f"{self.root_directory_path}/sales.txt", "a") as sales_file:
            sales_file.write(str_sale_500)

        sales_index = {}
        with open(f"{self.root_directory_path}/sales_index.txt", "r") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(':')
                    sales_index[parts[0]] = int(parts[1])

        line_number = len(sales_index) + 1
        sales_index[sale.car_vin] = line_number

        with open(f"{self.root_directory_path}/sales_index.txt", "w") as f:
            for id_, line_num in sorted(sales_index.items()):
                f.write(f"{id_}:{line_num}\n")

        return car

    def get_cars(self, status: CarStatus) -> list[Car]:
        available_cars = []
        with open(f"{self.root_directory_path}/cars.txt", "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(',')
                if len(parts) >= 5 and parts[4] == status.value:
                    available_cars.append(
                        Car(
                            vin=parts[0],
                            model=int(parts[1]),
                            price=Decimal(parts[2]),
                            date_start=datetime.strptime(
                                parts[3], "%Y-%m-%d %H:%M:%S"
                            ),
                            status=CarStatus(parts[4])
                        )
                    )
        return available_cars

    def get_car_info(self, vin: str) -> CarFullInfo | None:
        cars_index = {}
        with open(f"{self.root_directory_path}/cars_index.txt", "r") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(':')
                    cars_index[parts[0]] = int(parts[1])

        if vin not in cars_index:
            return None

        with open(f"{self.root_directory_path}/cars.txt", "r") as cars_file:
            cars_file.seek((cars_index[vin] - 1) * 501)
            car_data = cars_file.read(500).strip().split(',')

        models_index = {}
        with open(f"{self.root_directory_path}/models_index.txt", "r") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(':')
                    models_index[int(parts[0])] = int(parts[1])

        model_id = int(car_data[1])
        if model_id not in models_index:
            return None

        with open(
            f"{self.root_directory_path}/models.txt", "r"
        ) as models_file:
            models_file.seek((models_index[model_id] - 1) * 501)
            model_data = models_file.read(500).strip().split(',')

        sales_date = None
        sales_cost = None
        if car_data[4] == CarStatus.sold.value:
            with open(
                f"{self.root_directory_path}/sales.txt", "r"
            ) as sales_file:
                for line in sales_file:
                    line = line.strip()
                    if not line or ',is_deleted' in line:
                        continue
                    sale_data = line.split(',')
                    if len(sale_data) >= 4 and sale_data[1] == vin:
                        sales_date = datetime.strptime(
                            sale_data[2], "%Y-%m-%d %H:%M:%S"
                        )
                        sales_cost = Decimal(sale_data[3])
                        break

        return CarFullInfo(
            vin=vin,
            car_model_name=model_data[1],
            car_model_brand=model_data[2],
            price=Decimal(car_data[2]),
            date_start=datetime.strptime(car_data[3], "%Y-%m-%d %H:%M:%S"),
            status=CarStatus(car_data[4]),
            sales_date=sales_date,
            sales_cost=sales_cost
        )

    def update_vin(self, vin: str, new_vin: str) -> Car:
        cars_index = {}
        with open(f"{self.root_directory_path}/cars_index.txt", "r") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(':')
                    cars_index[parts[0]] = int(parts[1])

        with open(f"{self.root_directory_path}/cars.txt", "r+") as cars_file:
            line_num = cars_index[vin]
            cars_file.seek((line_num - 1) * 501)
            data = cars_file.read(500).strip().split(',')
            data[0] = new_vin
            updated_data = f"{','.join(data)}".ljust(500)
            cars_file.seek((line_num - 1) * 501)
            cars_file.write(updated_data)

        cars_index[new_vin] = cars_index.pop(vin)
        with open(f"{self.root_directory_path}/cars_index.txt", "w") as f:
            for id_, line_num in sorted(cars_index.items()):
                f.write(f"{id_}:{line_num}\n")

        return Car(
            vin=new_vin,
            model=int(data[1]),
            price=Decimal(data[2]),
            date_start=datetime.strptime(data[3], "%Y-%m-%d %H:%M:%S"),
            status=CarStatus(data[4])
        )

    def revert_sale(self, sales_number: str) -> Car:
        with open(f"{self.root_directory_path}/sales.txt", "r") as f:
            for line in f:
                line = line.strip()
                if not line or ',is_deleted' in line:
                    continue
                parts = line.split(',')
                if parts[0] == sales_number and len(parts) >= 4:
                    vin = parts[1]
                    break

        cars_index = {}
        with open(f"{self.root_directory_path}/cars_index.txt", "r") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(':')
                    cars_index[parts[0]] = int(parts[1])

        line_num = cars_index[vin]

        with open(f"{self.root_directory_path}/cars.txt", "r+") as f:
            f.seek((line_num - 1) * 501)
            data = f.read(500).strip().split(',')
            data[4] = CarStatus.available.value
            updated_car = f"{','.join(data)}".ljust(500)
            f.seek((line_num - 1) * 501)
            f.write(updated_car)

        with open(f"{self.root_directory_path}/sales.txt", "r+") as f:
            lines = f.readlines()
            f.seek(0)
            for line in lines:
                line = line.strip()
                if line.startswith(sales_number + ','):
                    line = f"{line},is_deleted".ljust(500) + "\n"
                f.write(line)

        return Car(
            vin=vin,
            model=int(data[1]),
            price=Decimal(data[2]),
            date_start=datetime.strptime(data[3], "%Y-%m-%d %H:%M:%S"),
            status=CarStatus.available
        )

    def top_models_by_sales(self) -> list[ModelSaleStats]:
        model_sales: dict[int, int] = {}

        # Сначала прочитаем все продажи
        with open(f"{self.root_directory_path}/sales.txt", "r") as sales_file:
            for line in sales_file:
                line = line.strip()
                if not line or ',is_deleted' in line:
                    continue
                parts = line.split(',')
                if len(parts) >= 2:
                    vin = parts[1]

                    # Найдем модель для этого VIN
                    cars_index = {}
                    with open(
                        f"{self.root_directory_path}/cars_index.txt", "r"
                    ) as f:
                        for idx_line in f:
                            if idx_line.strip():
                                car_parts = idx_line.strip().split(':')
                                cars_index[car_parts[0]] = int(car_parts[1])

                    if vin not in cars_index:
                        continue

                    with open(
                        f"{self.root_directory_path}/cars.txt", "r"
                    ) as cars_file:
                        cars_file.seek((cars_index[vin] - 1) * 501)
                        car_data = cars_file.read(500).strip().split(',')
                        if len(car_data) >= 2:
                            model_id = int(car_data[1])
                            model_sales[model_id] = (
                                model_sales.get(model_id, 0) + 1
                            )

        # Отсортируем модели по количеству продаж
        sorted_models = sorted(
            model_sales.items(), key=lambda item: item[1], reverse=True
        )
        top_models = sorted_models[:3]

        result = []
        # Прочитаем информацию о моделях
        models_index = {}
        with open(f"{self.root_directory_path}/models_index.txt", "r") as f:
            for idx_line in f:
                if idx_line.strip():
                    model_parts = idx_line.strip().split(':')
                    models_index[int(model_parts[0])] = int(model_parts[1])

        for model_id, sales_count in top_models:
            if model_id not in models_index:
                continue

            with open(
                f"{self.root_directory_path}/models.txt", "r"
            ) as models_file:
                models_file.seek((models_index[model_id] - 1) * 501)
                model_line = models_file.read(500).strip()
                model_data = model_line.split(',')

                if len(model_data) >= 3:
                    result.append(ModelSaleStats(
                        car_model_name=model_data[1].strip(),
                        brand=model_data[2].strip(),
                        sales_number=sales_count
                    ))

        return result
