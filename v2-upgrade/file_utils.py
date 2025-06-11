from pathlib import Path

def get_data_path(filename="Bogota_covid19.csv") -> Path:
    print(Path(__file__))
    return Path(__file__).resolve().parent / "data" / filename

def check_file_exists(csv_path: Path) -> bool:
    if csv_path.exists():
        return True
    else:
        print(f'\n❌ El archivo "{csv_path.name}" no existe en: {csv_path.parent}')
        return False
