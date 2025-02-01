
import sys
from datetime import datetime
from getpass import getpass
from lib import clear_screen
import display
from database import Database
from user import User, Admin
from car import Car
from email_validator import validate_email, EmailNotValidError
from colorama import init, Fore
from datetime import date
init(autoreset=True)

# connect database
db = Database()
auth_user = None
    
    
def run_portal():
    selected_main_menu = None
    # Loop menu until user select choice 9 to exit program
    while not selected_main_menu or selected_main_menu != 9:
        
        match selected_main_menu:
            case 1: # Display all car
                # Display all car
                display.display_car_list()
                # Ask user to select car
                selected_car = display.get_car_selection()

                if selected_car:                
                    # Ask user to select action with the selected car
                    # If user role is not admin, then check car is available or not
                    if auth_user.role != 'admin':
                    
                        # If car is not available, tell user press enter to return
                        if not selected_car.is_available:
                            input(Fore.RED + '\nThis Car is not available. Press enter to return...')
                            continue
                        # if car is available, ask user to input Y if user need to book the car, or N to return
                        else:
                            book_car = input(Fore.RESET + '\nDo you want to book this car? (Y/N): ' + Fore.CYAN)
                            if book_car.upper() == 'Y':
                                # Validate address, driver license and driver license expiration date
                                # If address, driver license or driver license expiration date not existing or expiration date expired, ask user to fill in the form, then update to database
                                if not auth_user.address or not auth_user.driver_license or not auth_user.driver_license_expired_date or auth_user.driver_license_expired_date < datetime.now().date():
                                    print(Fore.YELLOW + '\nPlease update your information below.')
                                    
                                    try:
                                        # address
                                        address = auth_user.address
                                        if not address:
                                            address = input(Fore.RESET + f'Address: ' + Fore.CYAN)
                                            
                                        # driver license
                                        driver_license = auth_user.driver_license
                                        if not driver_license:
                                            driver_license = input(Fore.RESET + f'Driver License: ' + Fore.CYAN)
                                        
                                        # driver license expiration date
                                        driver_license_expired_date = auth_user.driver_license_expired_date
                                        if not driver_license_expired_date or driver_license_expired_date < datetime.now().date():
                                            driver_license_expired_date = datetime.strptime(input(Fore.RESET + f'Driver License Expiration Date (DD-MM-YYYY): ' + Fore.CYAN), '%d-%m-%Y').date()
 
                                    except ValueError as e:
                                        input(Fore.RED + f'\nInvalid input information. Press enter to continue...')
                                        continue
                                    
                                    # Validate the driver license information
                                    if not address or not driver_license or not driver_license_expired_date:
                                        input(Fore.RED + '\nInvalid input, please try again. Press enter to continue...')
                                        continue
                                    else:
                                        auth_user.address = address
                                        auth_user.driver_license = driver_license
                                        auth_user.driver_license_expired_date = driver_license_expired_date
                                        if db.update_user(auth_user):
                                            input(Fore.GREEN + '\nUpdate driver license information successfully! Press enter to continue...')
                                        else:
                                            input(Fore.RED + '\nUpdate driver license information failed! Press enter to continue...')
                                        
                                        continue
                                
                                # booking car
                                auth_user.booking_car(selected_car)
                            else:
                                continue
                    # if user role is admin, ask user to select action with the selected car
                    else:
                        # Admin action
                        print(Fore.CYAN + f'\nPlease select action')
                        selected_action = input(Fore.RESET + '1: Edit \n2: Delete \n3: Create booking for customer \n\nInput your choice or leave it empty to got back to select car again: ' + Fore.CYAN)
                        

                        while selected_action not in ['1', '2','3', '']:
                            selected_action = input(Fore.RED + 'Invalid input, please try again.\n' + Fore.RESET + '\nInput your choice or leave it empty to got back to select car again: ' + Fore.CYAN)
                            
                            
                        # Match selection and take action as user selects
                        match selected_action:
                            case '1': # Edit car
                                auth_user.update_car(selected_car)
                                
                            case '2': # Delete car
                                # Confirm user for delete car
                                confirm = input(Fore.RESET + '\nAre you sure to delete this car? (Y/N): ' + Fore.CYAN)
                                if confirm.upper() != 'Y':
                                    continue
                                
                                auth_user.delete_car(selected_car.id)
                                
                            case '3': # Admin can create booking for customer
                                # Check if the selected car is not available
                                if not selected_car.is_available:
                                    input(Fore.CYAN + '\nThe selected car is not available. Press enter to return...')
                                    continue
                                
                                auth_user.booking_car_for_customer(selected_car)
                            
                            case _:
                                pass
                else:
                    selected_main_menu = None
                
            case 2: # Display booking records
                display.display_bookings(auth_user)
                
                # Ask user to select a booking from the list
                booking = display.get_booking_selection(auth_user)
                
                if booking:
                    # If user role is admin, ask user to select action with the selected booking
                    if auth_user.role == 'admin':
                        # Ask user to select 1 for approve, 2 for reject, 3 for delete if booking status is Pending
                        if booking.status == 'Pending':
                            selected_action = input(Fore.RESET + '\nSelect action (1: Approve, 2: Reject, 3: Delete): ' + Fore.CYAN)

                            while selected_action not in ['1', '2', '3', '']:
                                selected_action = input(Fore.RED + 'Invalid input, please try again.\n' + Fore.RESET + 'Select action (1: Approve, 2: Reject, 3: Delete): ' + Fore.CYAN)
                                
                            # Match selection and take action as user selects
                            match selected_action:
                                case '1':
                                    # Approve booking
                                    confirm = input(Fore.RESET + '\nAre you sure to approve this booking? (Y/N): ' + Fore.CYAN)
                                    if confirm.upper() != 'Y':
                                        continue
                                    
                                    auth_user.approve_booking(booking)
                                case '2':
                                    # Reject booking
                                    confirm = input(Fore.RESET + '\nAre you sure to reject this booking? (Y/N): ' + Fore.CYAN)
                                    if confirm.upper() != 'Y':
                                        continue
                                    
                                    auth_user.reject_booking(booking)
                                case '3':
                                    # Delete booking
                                    confirm = input(Fore.RESET + '\nAre you sure to delete this booking? (Y/N): ' + Fore.CYAN)
                                    if confirm.upper() != 'Y':
                                        continue
                                    
                                    auth_user.delete_booking(booking)
                                case _:
                                    pass
                        elif booking.status == 'Renting':
                            return_car = input(Fore.RESET + '\nDo you want to return this car? (Y/N): ' + Fore.CYAN)
                            if return_car.upper() == 'Y':
                                # return car
                                auth_user.return_car(booking)
                            else:
                                continue
                        else:
                            input(f'\nThis record has been {booking.status}. Press enter to continue...')
                    
                    # If user role is not admin, ask user to select action with the selected booking
                    else:
                        # If booking status is Renting, ask user to select to return car by input Y or N
                        if booking.status == 'Renting':
                            return_car = input(Fore.RESET + '\nDo you want to return this car? (Y/N): ' + Fore.CYAN)
                            if return_car.upper() == 'Y':
                                # return car
                                auth_user.return_car(booking)
                            else:
                                continue
                        elif booking.status == 'Pending':
                            cancel_booking = input(Fore.RESET + '\nDo you want to cancel this booking? (Y/N): ' + Fore.CYAN)
                            if cancel_booking.upper() == 'Y':
                                # cancel booking
                                auth_user.cancel_booking(booking)
                            else:
                                continue
                        else:
                            input(f'\nThis record has been {booking.status}. Press enter to continue...')
                            continue
                
                else:
                    selected_main_menu = None
                    
            case 3: # Add new car
                clear_screen()
                print(Fore.YELLOW + f'============= Add New Car =============','\n')
                
                try:
                    # Asking user to input car detail
                    car = {
                        "make": input(Fore.RESET + "Enter car make: " + Fore.CYAN),
                        "model": input(Fore.RESET + "Enter car model: " + Fore.CYAN),
                        "year": int(input(Fore.RESET + "Enter car year: " + Fore.CYAN)),
                        "color": input(Fore.RESET + "Enter car color: " + Fore.CYAN),
                        "plate_no": input(Fore.RESET + "Enter car plate number: " + Fore.CYAN),
                        "mileage": int(input(Fore.RESET + "Enter car mileage: " + Fore.CYAN)),
                        "rent_price_per_day": float(input(Fore.RESET + "Enter car rent price per day: " + Fore.CYAN)),
                        "min_rent_period": int(input(Fore.RESET + "Enter car minimum rent period: " + Fore.CYAN)),
                        "max_rent_period": int(input(Fore.RESET + "Enter car maximum rent period: " + Fore.CYAN)),
                    }
                    # Create new car object
                    new_car = Car(**car)
                
                    # Add new car to database
                    if (new_car):
                        auth_user.add_new_car(new_car)
                except Exception as e:
                    input(Fore.RED + f'Error while input car detail, please try again. Press enter to continue...')
                    
                selected_main_menu = None
                
            case 4: # Manage users
                clear_screen()
                # Display user table
                display.display_user_list()
                
                # Get user selection
                user = display.get_user_selection()
                
                if user:
                    # Display user detail if user exists
                    print("")
                    user.display_user_details()
                    
                    # Ask user to select action with the selected user
                    print(Fore.CYAN + f'\nPlease select action.')
                    selected_action = input(Fore.RESET + '1: Edit user \n2: Suspend/Unsuspend user \n3: Delete user \n\nInput your choice or leave it empty to got back to select user again: ' + Fore.CYAN)
                        
                    while selected_action not in ['1', '2','3', '']:
                            selected_action = input(Fore.RED + 'Invalid input, please try again.\n' + Fore.RESET + '\nInput your choice or leave it empty to got back to select user again: ' + Fore.CYAN)
                        
                    # Match selection and take action as user selects
                    match selected_action:
                        case '1': # Edit user
                            auth_user.update_user(user)
                            
                        case '2': # Suspend user
                            # Ask user to confirm suspend/unsuspend user
                            confirm = input(Fore.RESET + '\nAre you sure to suspend/unsuspend this user? (Y/N): ' + Fore.CYAN)
                            if confirm.upper() != 'Y':
                                continue
                            
                            auth_user.toggle_suspend_user(user)
                            
                        case '3': # Delete user
                            # Ask user to confirm delete user
                            confirm = input(Fore.RESET + '\nAre you sure to delete this user? (Y/N): ' + Fore.CYAN)
                            if confirm.upper() != 'Y':
                                continue
                            
                            auth_user.delete_user(user.id)
                        
                        case _:
                            pass
                
                else:
                    selected_main_menu = None
            
            case _:
                selected_main_menu = None
        
        # Display main menu if it is not selected
        if not selected_main_menu:
            display.display_main_menu(user=auth_user)
            selected_main_menu = display.get_main_menu_selection(user=auth_user)
    
    # Say good bye
    input(Fore.YELLOW + '\nThank you for using our system. Good bye and see you again.')
    

if __name__ == '__main__':
    # if database is not available, display error message and exit
    if not db.connection:
        print('Error connecting to database. Please contact system administrator.')
        sys.exit(1)

    # ask user to select until get correct selection
    while not auth_user:
        display.display_login_menu()
        login_menu_selected = display.get_login_menu_selection()
        
        match login_menu_selected:
            case 1: # Register
                clear_screen()
                
                print(Fore.YELLOW + f'============= Register User =============','\n')
                print('Please fill in user detail:',"\n")
                
                first_name = input(Fore.RESET + 'Enter your first name: ' + Fore.CYAN)
                last_name = input(Fore.RESET + 'Enter your last name: ' + Fore.CYAN)
                email = input(Fore.RESET + 'Enter your email: ' + Fore.CYAN)
                phone = input(Fore.RESET + 'Enter your phone: ' + Fore.CYAN)
                username = input(Fore.RESET + 'Enter your username: ' + Fore.CYAN)
                password = getpass(Fore.RESET + 'Enter your password: ' + Fore.CYAN)
                
                # Validate input before create user
                if not first_name or not last_name or not email:
                    input(Fore.RED + '\nInvalid input, please try again. Press enter to continue...')
                    continue
                
                # TODO: Move validation to user register function.
                # Validate email
                try:
                    email_info = validate_email(email, check_deliverability=False)
                    email = email_info.normalized
                except EmailNotValidError as e:
                    input(Fore.RED + f'\n{e}, please try again. Press enter to continue...')
                    continue
                
                # Validate username and password
                if not username or not password:
                    input(Fore.RED + '\nRequire username and password to register user. Press enter to continue...')
                    continue
                
                # Create user object
                user = User(0, first_name, last_name, email, phone)
                # Register user
                user.register(username, password)
                
            case 2: # Login
                # Display login screen and ask user to input username and password
                clear_screen()
                
                print(Fore.YELLOW + f'============= Login User =============','\n')
                username = input(Fore.RESET + 'Enter your username: ' + Fore.CYAN)
                password = getpass(Fore.RESET + 'Enter your password: ' + Fore.CYAN)
                
                # Validate username and password before login user
                if not username or not password:
                    input(Fore.RED + '\nInvalid input, please try again. Press enter to continue...')
                    continue
                
                # assign username and password to user
                user = User()
                
                # login user
                if not user.login(username, password):
                    continue
                
                # check if user is login successfully
                if user.role == 'admin':
                    auth_user = Admin(user.id, user.first_name, user.last_name, user.email, user.phone, user.role, user.is_suspended)
                else:
                    auth_user = user
                
                # ----------------------------------------------------------------
                # if login successfully, display welcome message and go to main menu
                run_portal()
                
                # Set auth user to None after logout
                auth_user = None
                
            case 3: #Forget password
                # Display forget password screen and ask user to input username and password
                clear_screen()

                # Ask user to enter username and email address
                print(Fore.YELLOW + f'============= Reset Password =============', '\n')
                username = input(Fore.RESET + 'Enter your username: ' + Fore.CYAN)
                email = input(Fore.RESET + 'Enter your email: ' + Fore.CYAN)
                
                # Validate username
                if not username:
                    input(Fore.RED + '\nUsername is required. Press enter to continue...')
                    continue
                
                # Validate email
                try:
                    email_info = validate_email(email, check_deliverability=False)
                    email = email_info.normalized
                except EmailNotValidError as e:
                    input(Fore.RED + f'\n{e}, please try again. Press enter to continue...')
                    continue
                
                # Check email in database
                user = db.get_user_by_username_and_email(username, email)
                
                # If user is not existing, exit
                if not user or user["id"] is None:
                    input(Fore.RED + '\nUser is not existing. Press enter to continue...')
                    continue
                
                # Ask user to enter new password
                print('\n')
                new_password = getpass(Fore.RESET + 'Enter your new password: ' + Fore.CYAN)
                check_password = getpass(Fore.RESET + 'Enter your new password again: ' + Fore.CYAN)
                
                # Check if new password is match
                if new_password != check_password:
                    input(Fore.RED + '\nPassword is not match. Press enter to continue...')
                    continue
                
                # Update password in database
                if db.update_user_password(user["id"], new_password):
                    # Display success message and ask user to login again
                    input(Fore.GREEN + '\nUpdate password successfully. Press enter to continue...')
                else:
                    input(Fore.RED + '\nUpdate password failed. Press enter to continue...')

            case 4: # Exit
                sys.exit(0)
                
            case _:
                pass

