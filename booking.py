from datetime import date
from database import Database


class Booking():
    def __init__(self, customer_id:int, car_id: int, start_date: date, end_date: date, rental_price_per_day: float, rental_period: int, rental_fees: float, status: str = 'Pending', id: int = None):
        self.customer_id = customer_id
        self.car_id = car_id
        self.start_date = start_date
        self.end_date = end_date
        self.rental_price_per_day = rental_price_per_day
        self.rental_period = rental_period
        self.rental_fees = rental_fees
        self.status = status
        self.id = id
        
    def __str__(self):
        return f"Booking ID: {self.id}, Customer ID: {self.customer_id}, Car ID: {self.car_id}, Start Date: {self.start_date}, End Date: {self.end_date}, Rental price per day: {self.rental_price_per_day}, Rental Period: {self.rental_period}, Rental Fees: {self.rental_fees}, Status: {self.status}" 
    
    def display_booking_details(self):
        try:
            db = Database()
            booking = db.get_booking_by_id(self.id)
            
            print(f"Booking ID: {booking['id']}")
            print(f"Customer: {booking['customer']}")
            print(f"Car Plate No: {booking['car_plate_no']}")
            print(f"Start Date: {booking['start_date']}")
            print(f"End Date: {booking['end_date']}")
            print(f"Rental Price Per Day: ${booking['rental_price_per_day']:,.2f}")
            print(f"Rental Period: {booking['rental_period']} days")
            print(f"Rental Fees: ${booking['rental_fees']:,.2f}")
            print(f"Status: {booking['status']}")
        except Exception as e:
            print(f"Error while display booking details: {e}")