from tabulate import tabulate
from lib import clear_screen
from colorama import init, Fore, Back
from user import User
from database import Database
from car import Car
from booking import Booking
init(autoreset=True)

db = Database()

login_menus = [
    [1, "Register"],
    [2, "Login"],
    [3, "Forget Password"],
    [4, "Exit"]
]

main_menus = [
    [1, "View cars",None],
    [2, "View renting records", None],
    [3, "Add new cars", "admin"],
    [4, "Manage users", "admin"],
    [9, "Logout", None]
]

# create decorator for print title and description
def screen_title(title: str):
    def display_title(func):
    
        def wrapper(*args, **kwargs):
        
            clear_screen()
            print(Fore.BLACK + Back.YELLOW + f'          CAR RENTAL SYSTEM          ')
            
            # Get user from kwargs if provided
            user = kwargs.get('user')
            # display login user
            if user:
                print(f'User: {user.first_name} {user.last_name}  Email: {user.email}')
            
            print(Fore.YELLOW +f'\n============= {title} =============')
            
            values = func(*args, **kwargs)
            return values
        return wrapper
    return display_title


@screen_title("Login menu")
def display_login_menu():
    '''
    This function use to display the main login menu
    '''
    
    print('Please select from the following options:',"\n")

    # display selected menu
    print(tabulate(login_menus, headers=["Choice", "Selection"]),'\n')


def get_login_menu_selection() -> int:
    '''
    This function will ask user to select the login menu
    If the user input is not in the list, it will ask again.
    If the user input is not a number, it will return None.
    If the user input is a number, it will return the selected menu.
    '''
    
    selected_menu = None
        
    try:
        # ask the user to select
        selected_menu = int(input(Fore.RESET + 'Enter your selection: '+ Fore.CYAN))

        while not selected_menu or selected_menu not in [menu[0] for menu in login_menus]:
            print('Your selection is not in the list.', "\n")
            selected_menu = int( input(Fore.RESET + 'Enter your selection: ' + Fore.CYAN))
    
    except Exception as e:
        input(Fore.RESET + "Invalid selection. Press enter to continue...")
 
    return selected_menu

@screen_title("Main menu")
def display_main_menu(user: User):
    '''
    This function displays the main menu by separating to two list for customer and admin users.
    The function requires the user role as a parameter. the type of user role is string and it should be one of customer or admin
    '''
    
    print('Please select from the following options:',"\n")
    
    menus = []
    
    # filter admin menu out if user role is not admin user
    if user.role == 'admin':
        menus = [[menu[0], menu[1]] for menu in main_menus]
    else:
        menus = [[menu[0], menu[1]] for menu in main_menus if menu[2] != 'admin']
    
    # display menu
    print(tabulate(menus, headers=["Choice", "Menu"]), '\n')

def get_main_menu_selection(user: User) -> int:
    menus = []
    
    # filter admin menu out if user role is not admin user
    if user.role == 'admin':
        menus = [[menu[0], menu[1]] for menu in main_menus]
    else:
        menus = [[menu[0], menu[1]] for menu in main_menus if menu[2] != 'admin']
    
    selected_menu = None
        
    try:
        # ask the user to select
        selected_menu = int(input(Fore.RESET + 'Enter your selection: '+ Fore.CYAN))

        while not selected_menu or selected_menu not in [menu[0] for menu in menus]:
            print('Your selection is not in the list.', "\n")
            selected_menu = int(input(Fore.RESET + 'Enter your selection: '+ Fore.CYAN))
            
            
    except Exception as e:
        input(Fore.RESET + "Invalid selection, please try again.")
        
    return selected_menu

@screen_title("Car List")
def display_car_list(type:str = 'all'):
    '''
    This function displays the car list by separating to three list for all, available and rented cars.
    
    The type argument can be
    - all (default)
    - available
    - rented
    '''

    cars = []
    # if type is 'all', get all cars from database.
    # if type is 'available', get all cars that is_available is True from database.
    # if type is 'rented', get all cars that is_available is False from database.
    if type == 'all':
        cars = db.get_all_cars()
    elif type == 'available':
        cars = db.get_available_cars()
    elif type == 'rented':
        cars = db.get_rented_cars()
        
            
    # Display car list type
    print(f'List type: {Fore.CYAN}{type.capitalize()}','\n')

    # Filter only column that need to display
    car_list = [
        [car['id'],
        car['make'],
        car['model'],
        car['year'],
        car['color'],
        f"{car['mileage']:,}",  # Add commas to mileage
        f"${car['rent_price_per_day']:,.2f}",  # Add dollar sign and commas to price
        car['min_rent_period'],
        car['max_rent_period'],
        'Yes' if car['is_available'] else 'No'] for car in cars]
    
    # Display booking list
    headers = ["ID", "Make", "Model", "Year","Color","Mileage (km.)","Price/day","Min rent","Max rent","Available"]
    # Define column alignments: right align for ID, Rental period, and Rental fees, left align for others
    column_align = ["right", "left", "left", "right", "left", "right", "right", "right", "right", "center"]
    
    if car_list:
        print(tabulate(car_list, 
                headers=headers, 
                colalign=column_align,
                tablefmt="simple"), '\n')
    else:
        print('No car found.', '\n')

def get_car_selection(type:str = 'all'):
    '''
    Car list type:
    - all
    - available
    - rented
    '''

    selected_menu = None
    
    try:
        # create car list
        car_list = []
        # if type is 'all', get all cars from database.
        # if type is 'available', get all cars that is_available is True from database.
        # if type is 'rented', get all cars that is_available is False from database.
        if type == 'all':
            car_list = db.get_all_cars()
        elif type == 'available':
            car_list = db.get_available_cars()
        elif type == 'rented':
            car_list = db.get_rented_cars()
            
        # Check if car_list is not existing, return none
        if not car_list:
            input('No car found. Press enter to continue...')
            return None
        
        # ask the user to select
        selected_menu = input(Fore.RESET + 'Choose car ID or press enter to go back: '+ Fore.CYAN)
        if selected_menu == '':
            return None
        else:
            try:
                selected_menu = int(selected_menu)
            except ValueError:
                selected_menu = None
        
        # Loop until the selection is in the car list
        # If the car selection is not in the car list, ask user to select again.
        # If selection is empty, return None.
        while not selected_menu or selected_menu not in [car['id'] for car in car_list]:
            print('Your selection is not in the list.', "\n")
            selected_menu = input(Fore.RESET + 'Choose car ID or press enter to go back: '+ Fore.CYAN)
            if selected_menu == '':
                return None
            else:
                try:
                    selected_menu = int(selected_menu)
                except ValueError:
                    selected_menu = None
                
        # return car in the car list as user select
        car = [car for car in car_list if car['id'] == selected_menu][0]
        
        # return car object
        return Car(car['make'],car['model'],car['year'],car['color'],car['plate_no'],car['mileage'],car['rent_price_per_day'],car['min_rent_period'],car['max_rent_period'],car['is_available'],car['id'])
        
    except Exception as e:
        input(f'{Fore.RED}Error while get car selection: {e}. Press enter to continue...')
        
    return None
        
@screen_title('Booking List')
def display_bookings(user: User):
    '''
    This function displays the booking list by separating to two list for customer and admin users.
    The function requires the user role as a parameter. the type of user role is string and it should be one of customer or admin
    '''
    
    # Validate user
    if not user:
        input('Invalid user. Press enter to continue...')
        return

    bookings = []
    
    # If user role is admin, get all bookings from database.
    # If user role is customer, get all bookings that user_id is current user id from database.
    if user.role == 'admin':
        bookings = db.get_all_bookings()
    else:
        bookings = db.get_bookings_by_user_id(user.id)

    # Filter only needed columns to display
    booking_list = [[
        booking['id'], 
        booking['customer'], 
        booking['car_plate_no'], 
        booking['start_date'], 
        booking['end_date'], 
        f'${booking['rental_price_per_day']}',
        booking['rental_period'], 
        f'${booking['rental_fees']:,.2f}',
        booking['status'],
        ] for booking in bookings]
    
    # Display booking list
    headers = ["ID", "Customer", "Car plate no.", "Start date", "End date","Price/day", "Rental period", "Rental fees","Status"]
    # Define column alignments: right align for ID, Rental period, and Rental fees, left align for others
    column_align = ("right", "left", "left", "left", "left", "right", "right", "right","center")

    if booking_list:
        print(tabulate(booking_list, 
                headers=headers, 
                colalign=column_align,
                tablefmt="simple"), '\n')
    else:
        print(tabulate(booking_list, 
                headers=headers,
                tablefmt="simple"), '\n')
    
def get_booking_selection(user: User):
    selected_booking = None
    
    try:
        
        # Get booking from database
        bookings = None
        
        if user.role == 'admin':
            bookings = db.get_all_bookings()
        else:
            bookings = db.get_bookings_by_user_id(user.id)
            
        # Check if bookings is not existing, return none
        if not bookings:
            input('No booking found. Press enter to continue...')
            return None
        
        # Ask user to select booking
        selected_booking = input(Fore.RESET + 'Choose booking ID or press enter to go back: '+ Fore.CYAN)
        if selected_booking == '':
            return None
        else:
            selected_booking = int(selected_booking)
            
        # Loop until user select booking in the bookings table
        while not selected_booking or selected_booking not in [booking['id'] for booking in bookings]:
            # Ask user to select booking again
            print('Your selection is not in the list.', "\n")
            selected_booking = input(Fore.RESET + 'Choose booking ID or press enter to go back: '+ Fore.CYAN)
            if selected_booking == '':
                return None
            else:
                selected_booking = int(selected_booking)
                
        # find booking in the booking list as user select
        booking = [booking for booking in bookings if booking['id'] == selected_booking][0]
        
        # return booking object
        return Booking(booking['customer_id'], booking['car_id'], booking['start_date'], booking['end_date'],booking['rental_price_per_day'], booking['rental_period'], booking['rental_fees'], booking['status'], booking['id'])

    except Exception as e:
        input(f'{Fore.RED}Error while get booking selection: {e}. Press enter to continue...')
        
    return None
    
@screen_title('User List')
def display_user_list():
    '''
    This function displays the user list and it will display only customer role.
    '''

    user_list = db.get_all_users()
    
    # Filter only needed columns to display
    user_list = [[
        user['id'], 
        user['first_name'], 
        user['last_name'], 
        user['email'], 
        user['phone'],
        user['driver_license'],
        user['driver_license_expired_date'], 
        'Yes' if user['is_suspended'] else None
        ] for user in user_list]
    
    headers=["ID", "First Name", "Last Name", "Email", "Phone","Driver license","Expired date","Suspended"]
    
    column_align = ("right", "left", "left", "left", "left", "left", "left", "center")
    
    if user_list:
        print(tabulate(user_list,
                headers=headers,
                colalign=column_align,
                tablefmt="simple"), '\n')
    else:    
        print(tabulate(user_list, headers=headers), '\n')
    
def get_user_selection():
    selected_user = None

    try:

        # Get user from database
        users = db.get_all_users()
        # Filter admin out from user
        users = [user for user in users if user['role'] != 'admin']

        # Check if users is not existing, return none
        if not users:
            input('No user found. Press enter to continue...')
            return None

        # Ask user to select user
        try:
            selected_user = input(Fore.RESET + 'Choose user ID or press enter to go back: '+ Fore.CYAN)
            if selected_user == '':
                return None
            else:
                selected_user = int(selected_user)
        except ValueError:
            selected_user = None

        # Loop until user select user in the users
        while not selected_user or selected_user not in [user['id'] for user in users]:
            # Ask user to select user again
            print('Your selection is not in the list.', "\n")
            try:
                selected_user = input(Fore.RESET + 'Choose user ID or press enter to go back: '+ Fore.CYAN)
                if selected_user == '':
                    return None
                else:
                    selected_user = int(selected_user)
            except ValueError:
                selected_user = None

        # Find user in the users as user select
        user = [user for user in users if user['id'] == selected_user][0]

        # Return user object
        return User(user['id'], user['first_name'], user['last_name'], user['email'],user['phone'], user['role'],user['is_suspended'],user['address'],user['driver_license'],user['driver_license_expired_date'])

    except Exception as e:
        input(f'{Fore.RED}Error while get user selection: {e}. Press enter to continue...')

    return None