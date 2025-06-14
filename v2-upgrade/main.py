from functions import opciones
from file_utils import get_data_path, check_file_exists
from gui import launch_gui

def main():
    csv_path = get_data_path()
    print(csv_path)
    if check_file_exists(csv_path):
        launch_gui(csv_path)

if __name__ == '__main__':
    main()
