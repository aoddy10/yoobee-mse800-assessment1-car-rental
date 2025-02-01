from os import system, name as os_name

# define clear terminal function
def clear_screen():

    # for windows
    if os_name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')