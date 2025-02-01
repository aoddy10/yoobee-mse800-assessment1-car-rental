import os,sys
import json
import configparser
import mysql.connector as MySQL
from mysql.connector import Error
from sql_statement import *
import hashlib
from seed_data import seed_data

class Database:
    # Implement singleton design pattern for database
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.config_filename = None
            self.connection = None
            self.cursor = None
            self.get_db_config_file()
            self._init_database()
            # Prevent to run __init__ multiple times
            self._initialized = True
        
    def _init_database(self):
        config = self.load_config()
        
        self._check_database_exists()
        
        try:
            if self.connection.is_connected():
                self._seed_database()
                
                return True
            
        except MySQL.Error as e:
            print(f"Error while connecting to MySQL: {e}")
            
        
        return False
    
    def get_db_config_file(self):
        # Load database configuration

        BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        config_file_path = os.path.join(BASE_DIR, "config_file.ini")

        self.config_filename = config_file_path

    
    def load_config(self):
        # Load database configuration
        config = configparser.ConfigParser()
        
        config.read(self.config_filename)
        
        return {key: value for key, value in config['mysql'].items()}
    
    # Database connection
    def create_connection_parser(self):
        config = self.load_config()
  
        self.connection = MySQL.connect(
                **config,
                autocommit=True
            )

        if self.connection.is_connected():
            return self.connection.cursor(dictionary=True)
        else:
            raise Exception()
        
    def _check_database_exists(self):
        config = self.load_config()
        
        try:
            self.connection = MySQL.connect(
                host=config["host"],
                user=config["user"],
                password=config["password"]
            )
            self.cursor = self.connection.cursor()
            self.cursor.execute(f"SHOW DATABASES LIKE '{config['database']}';")
            db_exists = self.cursor.fetchone() is not None
            
            if not db_exists:
                print(f"Database '{config['database']}' not found. Creating...")
                config['database'] = DEFAULT_DB_NAME
                
                self.cursor.execute(f'{CREATE_DB} {config['database']};')
                self.save_config(config)
            
            self.cursor = self.create_connection_parser()
            
        except MySQL.Error as e:
            print(f"Error checking database existence: {e}")
            return False
            
        
    # check if database exists
    def _check_table_exists(self, table_name):
        self.cursor.execute("SHOW TABLES LIKE %s", (table_name,))
        return self.cursor.fetchone() is not None
    
    def _is_table_empty(self, table_name):
        self.cursor.execute(f"SELECT COUNT(*) AS count FROM {table_name}")
        result = self.cursor.fetchone()  # Returns a dictionary if cursor is dictionary=True
        return result and result.get("count", 0) == 0
        
    def save_config(self, config):
        # Save database configuration to the INI file
        config_parser = configparser.ConfigParser()
        config_parser['mysql'] = config
        
        # Write the configuration to the file
        with open(self.config_filename, 'w') as config_file:
            config_parser.write(config_file)
    
    
    # Insert data into tables
    def _seed_database(self):
    
        # Check if tables are exist before create
        users_exists = self._check_table_exists("users")
        cars_exists = self._check_table_exists("cars")
        bookings_exists = self._check_table_exists("bookings")

        # Create tables if not existed
        self.cursor.execute(CREATE_USER_TABLE)
        self.cursor.execute(CREATE_CAR_TABLE)
        self.cursor.execute(CREATE_BOOKING_TABLE)
        self.connection.commit()


        # Check again if tables is created and do not have data
        new_tables = {
            "users": (not users_exists and self._check_table_exists("users") and self._is_table_empty("users")),
            "cars": (not cars_exists and self._check_table_exists("cars") and self._is_table_empty("cars")),
            "bookings": (not bookings_exists and self._check_table_exists("bookings") and self._is_table_empty("bookings")),
        }

        if any(new_tables.values()):
            print("Seeding database...")

            if new_tables["users"]:
                self._seed_users(seed_data["users"])
            if new_tables["cars"]:
                self._seed_cars(seed_data["cars"])
            if new_tables["bookings"]:
                self._seed_bookings(seed_data["bookings"])

            print("Database seeded successfully!")

        self.connection.commit()
        
    def _seed_users(self, users):
        """ Insert users if the users table was newly created """
        for user in users:
            self.cursor.execute("""
                INSERT INTO users (id, first_name, last_name, email, phone, username, password, role, 
                                  is_suspended, address, driver_license, driver_license_expired_date, 
                                  created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user["id"], user["first_name"], user["last_name"], user["email"], user["phone"],
                  user["username"], user["password"], user["role"], user["is_suspended"], user["address"],
                  user["driver_license"], user["driver_license_expired_date"], user["created_at"], user["updated_at"]))

    def _seed_cars(self, cars):
        """ Insert cars if the cars table was newly created """
        for car in cars:
            self.cursor.execute("""
                INSERT INTO cars (id, make, model, year, color, plate_no, mileage, rent_price_per_day, 
                                  min_rent_period, max_rent_period, is_available, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (car["id"], car["make"], car["model"], car["year"], car["color"], car["plate_no"],
                  car["mileage"], car["rent_price_per_day"], car["min_rent_period"], car["max_rent_period"],
                  car["is_available"], car["created_at"], car["updated_at"]))

    def _seed_bookings(self, bookings):
        """ Insert bookings if the bookings table was newly created """
        for booking in bookings:
            self.cursor.execute("""
                INSERT INTO bookings (id, customer_id, car_id, start_date, end_date, rental_price_per_day, 
                                      rental_period, rental_fees, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (booking["id"], booking["customer_id"], booking["car_id"], booking["start_date"],
                  booking["end_date"], booking["rental_price_per_day"], booking["rental_period"],
                  booking["rental_fees"], booking["status"], booking["created_at"], booking["updated_at"]))

        
        
    # ----------------------------------------------------------------     
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        # Hash the plain password
        password_to_check = hashlib.sha256(plain_password.encode()).hexdigest()
        # Compare the hashes
        return password_to_check == hashed_password
    
    def get_user_by_username_and_password(self, username: str, password: str):
        try:
            
            values = (
                username,
                )
            
            self.cursor.execute(FIND_USER_BY_USERNAME, values)
            user = self.cursor.fetchone()
            
            
            # if not found user, return None
            if not user:
                return None
            
            # compare password from decoded password
            stored_hashed_password = user['password']  # hashed password from database
            user_input_password = password  # password entered by user
            

            # If password is match, return user data. If not 
            if not self.verify_password(user_input_password, stored_hashed_password):
                return None

            # return user data
            return user
        except Error as e:
            print(f"Error get user login from database: {e}")
            return None
    
    # add user to the database
    def add_new_user(self, new_user, username: str, password: str) -> bool:
        try:
            
            # hash password
            hash_password = hashlib.sha256(password.encode()).hexdigest()
            
            values = (
                new_user.first_name, 
                new_user.last_name, 
                new_user.email,
                new_user.phone,
                username,
                hash_password,
                )
            
            self.cursor.execute(INSERT_USER, values)
            new_user.id = self.cursor.lastrowid
            
            return True
        except Error as e:
            print(f"Error adding user to database: {e}")
            return False
        
    def get_all_users(self):
        try:

            self.cursor.execute(FIND_ALL_CUSTOMER)
            users = self.cursor.fetchall()

            return users
        except Error as e:
            print(f"Error get all users from database: {e}")
            return None

    def get_user_by_id(self, id:int):
        try:

            values = (
                id,
                )

            self.cursor.execute(FIND_ONE_USER, values)
            user = self.cursor.fetchone()

            return user
        except Error as e:
            print(f"Error get user by id from database: {e}")
            return None
        
    def get_user_by_username_and_email(self,username: str, email: str):
        try:

            values = (
                username,
                email,
                )

            self.cursor.execute(FIND_ONE_USER_BY_USERNAME_AND_EMAIL, values)
            user = self.cursor.fetchone()

            return user
        except Error as e:
            print(f"Error get user by email from database: {e}")
            return None
        
    def update_user(self, user) -> bool:
        try:

            values = (
                user.first_name,
                user.last_name,
                user.email,
                user.phone,
                user.role,
                user.is_suspended,
                user.address,
                user.driver_license,
                user.driver_license_expired_date,
                user.id
            )

            self.cursor.execute(UPDATE_USER, values)

            return True
        except Error as e:
            print(f"Error update user to database: {e}")
            return False

    def update_user_password(self, user_id: int, new_password: str) -> bool:
        try:
            
            # Hash password
            hash_password = hashlib.sha256(new_password.encode()).hexdigest()

            values = (
                hash_password,
                user_id
            )

            self.cursor.execute(UPDATE_USER_PASSWORD, values)

            return True
        except Error as e:
            print(f"Error update user to database: {e}")
            return False
                
    def delete_one_user(self, id:int) -> bool:
        try:

            values = (
                id,
                )

            self.cursor.execute(DELETE_ONE_USER, values)

            return True
        except Error as e:
            print(f"Error delete user from database: {e}")
            return False

    # ----------------------------------------------------------------
    def add_new_car(self, new_car) -> bool:
        try:
            
            values = (
                new_car.make,
                new_car.model,
                new_car.year,
                new_car.color,
                new_car.plate_no,
                new_car.mileage,
                new_car.rent_price_per_day,
                new_car.min_rent_period,
                new_car.max_rent_period,
                )
    

            self.cursor.execute(INSERT_CAR, values)

            return True
        except Error as e:
            print(f"Error adding car to database: {e}")
            return False
        
    def get_all_cars(self):
        try:

            self.cursor.execute(FIND_ALL_CAR)
            cars = self.cursor.fetchall()

            return cars
        except Error as e:
            print(f"Error get all cars from database: {e}")
            return None
        
    def get_available_cars(self):
        try:

            self.cursor.execute(FIND_AVAILABLE_CAR)
            cars = self.cursor.fetchall()

            return cars
        except Error as e:
            print(f"Error get available cars from database: {e}")
            return None
    
    def get_rented_cars(self):
        try:

            self.cursor.execute(FIND_RENTED_CAR)
            cars = self.cursor.fetchall()

            return cars
        except Error as e:
            print(f"Error get rented cars from database: {e}")
            return None
    
    def get_car_by_id(self, id:int):
        try:

            values = (
                id,
                )

            self.cursor.execute(FIND_ONE_CAR, values)
            car = self.cursor.fetchone()

            return car
        except Error as e:
            print(f"Error get car by id from database: {e}")
    
    def update_car(self, car) -> bool:
        try:
            
            values = (
                car.make,
                car.model,
                car.year,
                car.color,
                car.plate_no,
                car.mileage,
                car.rent_price_per_day,
                car.min_rent_period,
                car.max_rent_period,
                car.is_available,
                car.id
            )
            self.cursor.execute(UPDATE_CAR, values)

            return True
        except Error as e:
            print(f"Error update car to database: {e}")
            return False
        
    def delete_one_car(self, id:int) -> bool:
        try:

            values = (
                id,
                )

            self.cursor.execute(DELETE_ONE_CAR, values)

            return True
        except Error as e:
            print(f"Error delete car from database: {e}")
            return False


    # ----------------------------------------------------------------
    def add_new_booking(self, booking) -> bool:
        try:

            values = (
                booking.customer_id,
                booking.car_id,
                booking.start_date,
                booking.end_date,
                booking.rental_price_per_day,
                booking.rental_period,
                booking.rental_fees,
                )

            self.cursor.execute(INSERT_BOOKING, values)
            new_booking_id = self.cursor.lastrowid

            return new_booking_id
        except Error as e:
            print(f"Error adding booking to database: {e}")
            return False
        
    def get_all_bookings(self):
        try:

            self.cursor.execute(FIND_ALL_BOOKING)
            bookings = self.cursor.fetchall()

            return bookings
        except Error as e:
            print(f"Error get all bookings from database: {e}")
            return None
        
    def get_bookings_by_user_id(self, customer_id:int):
        try:

            values = (
                customer_id,
                )

            self.cursor.execute(FIND_BOOKING_BY_USER_ID, values)
            bookings = self.cursor.fetchall()

            return bookings
        except Error as e:
            print(f"Error get bookings by customer id from database: {e}")
            return None
        
    def get_booking_by_id(self, id:int):
        try:

            values = (
                id,
                )

            self.cursor.execute(FIND_ONE_BOOKING, values)
            booking = self.cursor.fetchone()

            return booking
        except Error as e:
            print(f"Error get booking by id from database: {e}")
            return None
        
    def update_booking_status(self, id: int, status: str) -> bool:
        try:

            values = (
                status,
                id
                )

            self.cursor.execute(UPDATE_BOOKING_STATUS, values)

            return True
        except Error as e:
            print(f"Error update booking status to database: {e}")
            
        return False
    
    def delete_one_booking(self, id:int) -> bool:
        try:

            values = (
                id,
                )

            self.cursor.execute(DELETE_ONE_BOOKING, values)

            return True
        except Error as e:
            print(f"Error delete booking from database: {e}")
            return False