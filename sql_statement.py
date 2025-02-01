# sql_statement.py
DEFAULT_DB_NAME = "MSE800_CarRental"

# create database statement
CREATE_DB = "CREATE DATABASE IF NOT EXISTS"

# create tables statements
CREATE_USER_TABLE = """
CREATE TABLE IF NOT EXISTS Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL DEFAULT 'customer',
    is_suspended BOOLEAN NOT NULL DEFAULT FALSE,
    address VARCHAR(255),
    driver_license VARCHAR(255),
    driver_license_expired_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
"""
CREATE_CAR_TABLE = """
CREATE TABLE IF NOT EXISTS Cars (
    id INT AUTO_INCREMENT PRIMARY KEY,
    make VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    year INT NOT NULL,
    color VARCHAR(255) NOT NULL,
    plate_no VARCHAR(10) NOT NULL,
    mileage INT NOT NULL,
    rent_price_per_day DECIMAL(10, 2) NOT NULL,
    min_rent_period INT NOT NULL,
    max_rent_period INT NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
"""
CREATE_BOOKING_TABLE = """
CREATE TABLE IF NOT EXISTS Bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    car_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    rental_price_per_day DECIMAL(10, 2) NOT NULL,
    rental_period INT,
    rental_fees DECIMAL(10, 2) NOT NULL,
    status VARCHAR(255) NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES Users(id),
    FOREIGN KEY (car_id) REFERENCES Cars(id)
);
"""

# SQL statements for CRUD operations
# Users
FIND_USER_BY_USERNAME = "SELECT * FROM Users WHERE username = %s;"
INSERT_USER = "INSERT INTO Users (first_name, last_name, email, phone, username, password) VALUES (%s, %s, %s, %s, %s, %s);"
FIND_ALL_CUSTOMER = "SELECT id,first_name, last_name, email, phone, role, is_suspended, address, driver_license, driver_license_expired_date FROM Users WHERE role <> 'admin' ORDER BY id;"
FIND_ONE_USER = "SELECT id,first_name, last_name, email, phone, role, is_suspended, address, driver_license, driver_license_expired_date FROM Users WHERE id = %s;"
FIND_ONE_USER_BY_USERNAME_AND_EMAIL = "SELECT id,first_name, last_name, email, phone, role, is_suspended, address, driver_license, driver_license_expired_date FROM Users WHERE username = %s AND email = %s;"
UPDATE_USER = "UPDATE Users SET first_name=%s, last_name=%s, email=%s, phone=%s, role=%s, is_suspended=%s, address=%s, driver_license=%s, driver_license_expired_date=%s WHERE id=%s;"
UPDATE_USER_PASSWORD = "UPDATE Users SET password=%s WHERE id=%s;"
DELETE_ONE_USER = "DELETE FROM Users WHERE id = %s;"

# Cars
INSERT_CAR = "INSERT INTO Cars (make, model, year, color, plate_no, mileage, rent_price_per_day, min_rent_period, max_rent_period) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
FIND_ALL_CAR = "SELECT * FROM Cars ORDER BY id;"
FIND_AVAILABLE_CAR = "SELECT * FROM Cars WHERE is_available = TRUE ORDER BY id;"
FIND_RENTED_CAR = "SELECT * FROM Cars WHERE is_available = FALSE ORDER BY id;"
FIND_ONE_CAR = "SELECT * FROM Cars WHERE id = %s;"
UPDATE_CAR = "UPDATE Cars SET make=%s, model=%s, year=%s, color=%s, plate_no=%s, mileage=%s, rent_price_per_day=%s, min_rent_period=%s, max_rent_period=%s, is_available=%s WHERE id=%s;"
DELETE_ONE_CAR = "DELETE FROM Cars WHERE id = %s;"

# Bookings
INSERT_BOOKING = "INSERT INTO Bookings (customer_id, car_id, start_date, end_date, rental_price_per_day, rental_period, rental_fees) VALUES (%s, %s, %s, %s, %s, %s, %s);"
FIND_ALL_BOOKING = "SELECT b.*\
    ,CONCAT(u.first_name, ' ', u.last_name) as customer\
    ,c.plate_no as car_plate_no \
    FROM Bookings b INNER JOIN Cars c ON b.car_id = c.id \
    INNER JOIN Users u ON b.customer_id = u.id \
    ORDER BY b.id;"
FIND_ONE_BOOKING = "SELECT b.*\
    ,CONCAT(u.first_name, ' ', u.last_name) as customer\
    ,c.plate_no as car_plate_no \
    FROM Bookings b INNER JOIN Cars c ON b.car_id = c.id \
    INNER JOIN Users u ON b.customer_id = u.id \
    WHERE b.id = %s \
    ORDER BY b.id;"
FIND_BOOKING_BY_USER_ID = "SELECT b.*\
    ,CONCAT(u.first_name, ' ', u.last_name) as customer\
    ,c.plate_no as car_plate_no \
    FROM Bookings b INNER JOIN Cars c ON b.car_id = c.id \
    INNER JOIN Users u ON b.customer_id = u.id \
    WHERE b.customer_id = %s \
    ORDER BY b.id;"
UPDATE_BOOKING_STATUS = "UPDATE Bookings SET status = %s WHERE id = %s;"
DELETE_ONE_BOOKING = "DELETE FROM Bookings WHERE id = %s;"