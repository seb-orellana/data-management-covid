from functions import opciones
from extraction import try_opcion
from file_utils import get_data_path, check_file_exists

def menu(csv_path):
    #El menu queda activo hasta que se de la opcion de salir.
    while True:
        print("\n\tMenu principal\n")

        #Opciones.
        print("1. Leer datos")
        print("2. Ver estadisticas por localidad")
        print("3. Ver contagidos dentro de un rango de fechas")
        print("4. Ver las tres localidades con mayor contagio")
        print("5. Ver las tres localidades con menor contagio")
        print("6. Descargar estadisticas por caso")
        print("7. Descargar estadisticas generales")
        print("8. Salir")

        #Opcion del operador.
        opcion = input("\nEscoga una opcion (Escriba el numero correspondiente): ")
        
        #Prueba si la opcion del operador es una opcion valida.
        while not try_opcion(opcion) or int(opcion) < 1 or int(opcion) > 8:
            print("\nLa opcion tiene que ser un numero natural entre 1 y 8. Vuelva a intentar.")
            opcion = input("\nEscoga una opcion (Escriba el numero correspondiente): ")

        #Convierte a int la opcion.
        opcion = int(opcion)

        #En caso de que la opcion sea 8.
        if opcion == 8:
            break

        #Llama la funcion opciones() con parametro opcion del operador.
        opciones(opcion, csv_path)

def main():
    csv_path = get_data_path()
    print(csv_path)
    if check_file_exists(csv_path):
        menu(csv_path)

if __name__ == '__main__':
    main()
