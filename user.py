from datetime import datetime
from database import Database
from colorama import init, Fore
from car import Car
from booking import Booking
init(autoreset=True)

db = Database()

class User:
    def __init__(self,id: int = None, first_name: str=None, last_name: str=None, email: str=None, phone: str=None, role: str=None, is_suspended: bool = False,address: str = None,driver_license: str = None, driver_license_expired_date: datetime = None ):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.role = role
        self.address = address
        self.is_suspended = is_suspended
        self.driver_license = driver_license
        self.driver_license_expired_date = driver_license_expired_date
        
    def __str__(self):
        return f"User ID: {self.id}, First Name: {self.first_name}, Last Name: {self.last_name}, Email: {self.email}, Phone: {self.phone}, Role: {self.role}, Is Suspended: {self.is_suspended}, Address: {self.address},Driver License: {self.driver_license}, Driver License Expired Date: {self.driver_license_expired_date}"
    
    def display_user_details(self):
        print(f"User ID: {self.id}")
        print(f"================ Personal details ===============")
        print(f"First Name: {self.first_name}")
        print(f"Last Name: {self.last_name}")
        print(f"Email: {self.email}")
        print(f"Phone: {self.phone}")
        print(f"Role: {self.role}")
        print(f"Suspended: {'Yes' if self.is_suspended else 'No'}")
        print(f"Address: {self.address}")
        print(f"================ Driver license =================")
        print(f"Driver License: {self.driver_license}")
        print(f"Driver License Expiry Date: {self.driver_license_expired_date}")

    def register(self, username: str, password: str):
        # Validate username and password
        if not username or not password:
            print(Fore.RED + 'Require username and password to register user!')
            return
        
        # Validate user
        if not self.first_name or not self.last_name or not self.email:
            print(Fore.RED + 'User is not valid!')
            return
        
        # Add user to database
        if db.add_new_user(self, username, password):
            input(Fore.GREEN + '\nRegister user successfully! Press enter to continue...')
        else:
            input(Fore.RED + '\nRegister user failed! Press enter to continue...')
            
    def login(self, username: str, password: str):
        
        # Verify username and password
        if not username or not password:
            input(Fore.RED + '\nRequire username and password to login!')
            return
        
        # Get user from database by username and password
        user = db.get_user_by_username_and_password(username, password)
        
        if not user:
            input(Fore.RED + '\nLogin failed! Press enter to continue...')
            return False
            
        # Check if user is suspended, tell user that the account is suspended
        if user['is_suspended']:
            input(Fore.RED + '\nYour account has been suspended! Please contact admin to activate your account.')
            return False
        
        # Assign user data to user
        self.id = user['id']
        self.first_name = user['first_name']
        self.last_name = user['last_name']
        self.email = user['email']
        self.phone = user['phone']
        self.role = user['role']
        self.is_suspended = user['is_suspended']
        self.address = user['address']
        self.driver_license = user['driver_license']
        self.driver_license_expired_date = user['driver_license_expired_date']
        
        input(Fore.GREEN + '\nLogin successfully! Press enter to continue...')
        return True
        
    def booking_car(self, car: Car) -> bool:
        
        # Validate car input
        if not car.id or not car.rent_price_per_day or not car.min_rent_period or not car.max_rent_period or not car.is_available:
            input(Fore.RED + 'Car is not valid or Car is not available!')
            return
        
        # Validate user driver license and driver license expiration data
        if not self.driver_license or not self.driver_license_expired_date:
            input(Fore.RED + '\nPlease update your driver license and driver license expiration date before booking car!')
            return
        
        # Ask user for start date and end date
        try:
            start_date = datetime.strptime(input(Fore.RESET + 'Enter start date (DD-MM-YYYY): ' + Fore.CYAN), '%d-%m-%Y').date()
            end_date = datetime.strptime(input(Fore.RESET + 'Enter end date (DD-MM-YYYY): ' + Fore.CYAN), '%d-%m-%Y').date()
        except ValueError:
            input(Fore.RED + '\nDate is not valid! Please use DD-MM-YYYY format.')
            return
        
        # Check if rental period is not less than min rent period and is not greater than max rent period
        rental_period = (end_date - start_date).days + 1


        # Validate rental period
        if rental_period < 0:
            input(Fore.RED + '\nEnd date must be greater than start date!')
            return
        elif rental_period < car.min_rent_period or rental_period > car.max_rent_period:
            input(Fore.RED + f'\nRent period is not valid! Min rent period is {car.min_rent_period} days and max rent period is {car.max_rent_period} days.')
            return
        
        # Calculate rental
        rental_fees = rental_period * car.rent_price_per_day

        # Create bookings record for car
        new_booking = Booking(self.id,car.id,start_date,end_date,car.rent_price_per_day,rental_period, rental_fees)
        if db.add_new_booking(new_booking):
            # Change car status to invalid
            car.is_available = False
            # Update car status
            if not db.update_car(car):
                input(Fore.RED + '\nBook car failed! Press enter to continue...')
                
            # If successful, update car status to not available
            input(Fore.GREEN + '\nBook car successfully! Press enter to continue...')
            return True
        else:
            input(Fore.RED + '\nBook car failed! Press enter to continue...')
        
        return False
        
    def return_car(self, booking: Booking) -> bool:
        # Validate booking input
        if not booking.id or not booking.car_id or booking.status != 'Renting':
            print(Fore.RED + 'Booking is not valid or booking status is not renting!')
            return

        # Create database connection

        # Update booking status to returned
        if db.update_booking_status(booking.id, 'Returned'):
            # Change car status to available
            car = db.get_car_by_id(booking.car_id)
            car = Car(car['make'], car['model'], car['year'], car['color'], car['plate_no'], car['mileage'], car['rent_price_per_day'], car['min_rent_period'], car['max_rent_period'], car['is_available'], car['id'])
            car.is_available = True
            # Update car status
            if not db.update_car(car):
                input(Fore.RED + '\nReturn car failed! Press enter to continue...')
                return False

            # If successful, update booking status to returned
            input(Fore.GREEN + '\nReturn car successfully! Press enter to continue...')
            return True
        else:
            input(Fore.RED + '\nReturn car failed! Press enter to continue...')

        return False

    def cancel_booking(self, booking: Booking) -> bool:
        # Validate booking input
        if not booking.id or not booking.car_id or booking.status != 'Pending':
            print(Fore.RED + 'Booking is not valid or you can cancel only pending booking!')
            return

        # Create database connection

        # Update booking status to returned
        if db.update_booking_status(booking.id, 'Cancelled'):
            # Change car status to available
            car = db.get_car_by_id(booking.car_id)

            # Create car object from car
            car = Car(car['make'], car['model'], car['year'], car['color'], car['plate_no'], car['mileage'], car['rent_price_per_day'], car['min_rent_period'], car['max_rent_period'], car['is_available'],car['id'])
            car.is_available = True
            
            # Update car status
            if not db.update_car(car):
                input(Fore.RED + '\nCancel booking failed! Press enter to continue...')
                return False

            # If successful, update booking status to returned
            input(Fore.GREEN + '\nCancel booking successfully! Press enter to continue...')
            return True
        else:
            input(Fore.RED + '\nCancel booking failed! Press enter to continue...')

        return False
        

class Admin(User):
    def __init__(self, id: int, first_name: str, last_name: str, email: str, phone: str, role: str = 'admin', is_suspended: bool = True):
        super().__init__(id, first_name, last_name, email, phone, role, is_suspended)

    # Add car to db
    def add_new_car(self, car: Car) -> bool:
        
        # validate car input
        if not car.make or not car.model or not car.year or not car.color or not car.plate_no or not car.mileage or not car.rent_price_per_day:
            print(Fore.RED + 'Car is not valid!')
            return

        # add car to database
        if db.add_new_car(car):
            input(Fore.GREEN + '\nAdd car successfully! Press enter to continue...')
            return True
        else:
            input(Fore.RED + '\nAdd car failed! Press enter to continue...')
            
        return False

    # Update car in db
    def update_car(self, car: Car) -> bool:
        
        # validate car input
        if not car or not car.id:
            print(Fore.RED + 'Car is not valid!')
            return False
        
        # Asking user to input update car information by display current detail and then change detail if user change data or leave it unchanged if user leave it empty
        print(f'\nPlease input changed car information. Leave it empty if you do not want to change the car information')
        try:
            # Loop through car fields
            for field in car.__dict__:
                # Skip id field
                if field == 'id':
                    continue

                # Get current car field value
                current_value = getattr(car, field)

                # Ask user to input new value
                new_value = input(Fore.RESET + f'Enter new {field} ({current_value}): ' + Fore.CYAN)

                # If user input new value, update car field
                if new_value:
                    setattr(car, field, new_value)
                
        except Exception as e:
            input(Fore.RED + f'\n{e}, please try again. Press enter to continue...')
            return False
        
        # update car in database
        if db.update_car(car):
            input(Fore.GREEN + 'Update car successfully! Press enter to continue...')
            return True
        else:
            input(Fore.RED + 'Update car failed! Press enter to continue...')
            
        return False

    # Delete car in db
    def delete_car(self, car_id: int) -> bool:
        # Validate car id
        if not car_id:
            print(Fore.RED + 'Require car id to delete car! Press enter to continue...')
            return False
        
        # Delete car in database
        if db.delete_one_car(car_id):
            input(Fore.GREEN + 'Delete car successfully! Press enter to continue...')
            return True
        else:
            input(Fore.RED + 'Delete car failed! Press enter to continue...')
            
        return False

    def update_user(self, user: User) -> bool:
        # Validate user input
        if not user or not user.id:
            print(Fore.RED + 'User is not valid!')
            return False

        # Asking user to input update user information by display current detail and then change detail if user change data or leave it unchanged if user leave it empty
        print(f'\nPlease input changed user information. Leave it empty if you do not want to change the user information')
        try:
            # Loop through user fields
            for field in user.__dict__:
                # Skip id field
                if field == 'id':
                    continue

                # Get current user field value
                current_value = getattr(user, field)

                # Ask user to input new value
                new_value = input(Fore.RESET + f'Enter new {field} ({current_value}): ' + Fore.CYAN)

                # If user input new value, update user field
                if new_value:
                    setattr(user, field, new_value)

        except Exception as e:
            input(Fore.RED + f'\n{e}, please try again. Press enter to continue...')
            return False

        # update user in database
        if db.update_user(user):
            input(Fore.GREEN + '\nUpdate user successfully! Press enter to continue...')
            return True
        else:
            input(Fore.RED + '\nUpdate user failed! Press enter to continue...')

        return False
            
    def toggle_suspend_user(self, user: User) -> bool:
        # Validate user input
        if not user or not user.id:
            print(Fore.RED + 'User is not valid!')
            return False

        # Set the user to be suspended
        user.is_suspended = not user.is_suspended

        # Suspend user in database
        if db.update_user(user):
            input(Fore.GREEN + '\nSuspend/Unsuspend user successfully! Press enter to continue...')
            return True
        else:
            input(Fore.RED + '\nSuspend/Unsuspend user failed! Press enter to continue...')
                
        return False
    
    def delete_user(self, user_id: int) -> bool:
        # Validate user id
        if not user_id:
            print(Fore.RED + 'Require user id to delete user! Press enter to continue...')
            return False

        # Delete user in database
        if db.delete_one_user(user_id):
            input(Fore.GREEN + '\nDelete user successfully! Press enter to continue...')
            return True
        else:
            input(Fore.RED + '\nDelete user failed! Press enter to continue...')

        return False
                 
    def approve_booking(self, booking: Booking) -> bool:
        # Validate booking and booking status need to be Pending
        if not booking or not booking.id or booking.status != 'Pending':
            print(Fore.RED + 'Booking is not valid or Booking status is not Pending!')
            return False
        
        # approve booking in database
        if db.update_booking_status(booking.id, 'Renting'):
            input(Fore.GREEN + 'Approve booking successfully! Press enter to continue...')
            return True
        else:
            input(Fore.RED + 'Approve booking failed! Press enter to continue...')
            
        return False
    
    def reject_booking(self, booking: Booking) -> bool:
        # Validate booking and booking status need to be Pending
        if not booking or not booking.id or booking.status != 'Pending':
            print(Fore.RED + 'Booking is not valid or Booking status is not Pending!')
            return False

        # reject booking in database
        if db.update_booking_status(booking.id, 'Rejected'):
            # Change car status to available
            car = db.get_car_by_id(booking.car_id)

            # Create car object from car
            car = Car(car['make'], car['model'], car['year'], car['color'], car['plate_no'], car['mileage'], car['rent_price_per_day'], car['min_rent_period'], car['max_rent_period'], car['is_available'],car['id'])
            car.is_available = True
            
            # Update car status
            if not db.update_car(car):
                input(Fore.RED + '\Reject booking failed! Press enter to continue...')
                return False
            
            input(Fore.GREEN + 'Reject booking successfully! Press enter to continue...')
            return True
        else:
            input(Fore.RED + 'Reject booking failed! Press enter to continue...')

        return False
    
    def delete_booking(self, booking: Booking) -> bool:
        # Validate booking and booking status need to be Pending
        if not booking or not booking.id:
            print(Fore.RED + 'Booking is not valid!')
            return False

        # delete booking in database
        if db.delete_one_booking(booking.id):
            # Change car status to available
            car = db.get_car_by_id(booking.car_id)

            # Create car object from car
            car = Car(car['make'], car['model'], car['year'], car['color'], car['plate_no'], car['mileage'], car['rent_price_per_day'], car['min_rent_period'], car['max_rent_period'], car['is_available'],car['id'])
            car.is_available = True
            
            # Update car status
            if not db.update_car(car):
                input(Fore.RED + '\Delete booking failed! Press enter to continue...')
                return False
            
            input(Fore.GREEN + 'Delete booking successfully! Press enter to continue...')
            return True
        else:
            input(Fore.RED + 'Delete booking failed! Press enter to continue...')

        return False

    def booking_car_for_customer(self, car: Car) -> bool:
        # Validate car input
        if not car.id or not car.rent_price_per_day or not car.min_rent_period or not car.max_rent_period or not car.is_available:
            print(Fore.RED + 'Car is not valid or Car is not available!')
            return
        
        # Create database connection
        
        # Ask user for user ID
        try:
            user_id = int(input(Fore.RESET + 'Enter user ID: ' + Fore.CYAN))
        except ValueError:
            input(Fore.RED + '\nUser ID is not valid!')
            return
        
        # Validate user ID
        if db.get_user_by_id(user_id) is None:
            input(Fore.RED + '\nDoes not have this user in the system.')
            return
        
        # Ask user for start date and end date
        try:
            start_date = datetime.strptime(input(Fore.RESET + 'Enter start date (DD-MM-YYYY): ' + Fore.CYAN), '%d-%m-%Y').date()
            end_date = datetime.strptime(input(Fore.RESET + 'Enter end date (DD-MM-YYYY): ' + Fore.CYAN), '%d-%m-%Y').date()
        except ValueError:
            input(Fore.RED + '\nDate is not valid! Please use DD-MM-YYYY format.')
            return
        
        
        # Check if rental period is not less than min rent period and is not greater than max rent period
        rental_period = (end_date - start_date).days + 1


        # Validate rental period
        if rental_period < 0:
            input(Fore.RED + '\nEnd date must be greater than start date!')
            return
        elif rental_period < car.min_rent_period or rental_period > car.max_rent_period:
            input(Fore.RED + f'\nRent period is not valid! Min rent period is {car.min_rent_period} days and max rent period is {car.max_rent_period} days.')
            return
        
        # Calculate rental
        rental_fees = rental_period * car.rent_price_per_day

        # Create bookings record for car
        new_booking = Booking(user_id,car.id,start_date,end_date,car.rent_price_per_day,rental_period, rental_fees)
        new_booking_id = db.add_new_booking(new_booking)
        if new_booking_id:
            
            # Update booking status to be renting
            db.update_booking_status(new_booking_id, 'Renting')
            
            
            # Change car status to invalid
            car.is_available = False
            # Update car status
            if not db.update_car(car):
                input(Fore.RED + '\nBook car failed! Press enter to continue...')
                
            # If successful, update car status to not available
            input(Fore.GREEN + '\nBook car successfully! Press enter to continue...')
            return True
        else:
            input(Fore.RED + '\nBook car failed! Press enter to continue...')
        
        return False