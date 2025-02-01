class Car():
    def __init__(self, make: str, model: str, year: int, color: str, plate_no: str, mileage: int, rent_price_per_day: float, min_rent_period: int , max_rent_period: int, is_available: bool = True, id: int = None):
        try:
            self.id = id
            self.make = make
            self.model = model
            self.year = year
            self.color = color
            self.plate_no = plate_no
            self.mileage = mileage
            self.rent_price_per_day = rent_price_per_day
            self.is_available = is_available
            self.min_rent_period = min_rent_period
            self.max_rent_period = max_rent_period
        except Exception as e:
            print(f'Error: {e}')
        
    def __str__(self):
        return f"Car ID: {self.id}, Make: {self.make}, Model: {self.model}, Year: {self.year}, Color: {self.color}, Plate No: {self.plate_no}, Mileage: {self.mileage}, Rent Price Per Day: {self.rent_price_per_day}, Is Available: {self.is_available}, Min Rent Period: {self.min_rent_period}, Max Rent Period: {self.max_rent_period}"

    # display car information
    def display_car_detail(self):
        print(f'Car ID: {self.id}')
        print(f'Make: {self.make}')
        print(f'Model: {self.model}')
        print(f'Year: {self.year}')
        print(f'Color: {self.color}')
        print(f'Plate No: {self.plate_no}')
        print(f'Mileage: {self.mileage:,}')
        print(f'Rent Price: ${self.rent_price_per_day:,.2f}')
        print(f'Min Rent Period: {self.min_rent_period}')
        print(f'Max Rent Period: {self.max_rent_period}')
        print(f'Available: {'Yes' if self.is_available else 'No'}')
        
    