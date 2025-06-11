import os

def leer_datos(Casos_matriz):
    '''
    Muestra cada linea del archivo "Bogota_covid19.csv" organizado por numero de caso.
    :param list Casos_matriz: Matriz con los casos.
    Retorna para volver al menu.
    '''

    #Indica la opcion seleccionada.
    print("\nEscogio la opcion de leer datos.")

    #Permite volver al menu principal.
    if volver_al_menu():
        return
    
    #Inicializa un diccionario.
    Casos = {"Numero de caso": Casos_matriz[0]}
    
    #Actualiza el diccionario.
    for caso in range(1, len(Casos_matriz)):
        #Al diccionario "Casos" le agrega una llave "Caso x", donde x es el numero del caso.
        #Agrega cada caso como lista a Casos["Caso x"].
        Casos["Caso {}".format(caso)] = Casos_matriz[caso]
        
    #Inicializa una lista.
    Categorias_lens = []

    #Mira la string mas larga en cada categoria.
    for categoria in range(len(Casos_matriz[0])):
        Lista_temporal = []
        for caso in range(len(Casos_matriz)):
            Lista_temporal.append(len(Casos_matriz[caso][categoria]))
        Categorias_lens.append(max(Lista_temporal))
        
    #Imprime el encabezado de la primera columna.
    print("\nNumero de caso", end="\t")
    
    #Imprime el resto del encabezado y una linea vacia.
    for categoria in range(len(Casos["Numero de caso"])):
        print("{:<{}}".format(Casos["Numero de caso"][categoria], Categorias_lens[categoria]), end="\t")
    print()
    
    #Imprime el numero de caso (llave del diccionario) y sus caracteristicas (valor respectivo).
    #El Categorias_lens es usado como identacion para que se vea organizado.
    for caso in range(1, len(Casos)):
        print("\n{:^14}".format(caso), end="\t")
        for categoria in range(len(Casos["Caso {}".format(caso)])):
            print("{:<{}}".format(Casos["Caso {}".format(caso)][categoria], Categorias_lens[categoria]), end="\t")

    #Permite que el operador decida cuando volver al menu.
    input("\n\nPresione enter para volver al menu: ")

def casos_archivo():
    '''
    Organiza los casos del archivo en una matriz.
    :return list Casos_matriz: Matriz con los casos de covid19.
    '''

    # Path to the directory where this .py file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Build the path to the CSV file
    csv_path = os.path.join(current_dir, "data", "Bogota_covid19.csv")

    #Abre el archivo y guarda los casos en una lista.
    Archivo_covid19 = open(csv_path, "r")
    Casos_lista = Archivo_covid19.readlines()
    Archivo_covid19.close()

    #Crea una matriz con los casos.
    Casos_matriz = [caso[:len(caso) - 1].split(",") for caso in Casos_lista]

    #Retorna la matriz con los casos.
    return Casos_matriz
    
#Define la funcion volver_al_menu()
def volver_al_menu():
    '''
    Permite volver al menu principal en caso que el operador quiera cambiar de opcion.
    :return bool: True or False de acuerdo al resultado.
    '''

    #Indica las opciones disponibles.
    print("\nPara volver al menu principal presione 1\nPara continuar presione 2")

    #Opcion del operador.
    opcion = input("Opcion: ")

    #Verifica que la opcion sea valida.
    while not try_opcion(opcion) or int(opcion) < 1 or int(opcion) > 2:
        print("\nOpcion no valida, vuelva a intentar.")
        print("\nPara volver al menu principal presione 1\nPara continuar presione 2")
        opcion = input("Opcion: ")

    #Retorna de acuerdo a la opcion escogida.
    if int(opcion) == 1:
        return True

    else:
        return False
    
#Define la funcion try_opcion()
def try_opcion(opcion):
    '''
    Prueba si la opcion recibida es un numero entero.
    :param string opcion: input de la funcion menu.
    :return bool: True | False (De acuerdo al resultado)
    '''
    #Intenta convertir la opcion a entero, si puede, retorna True, si no, retorna False.
    try:
        int(opcion)
        return True

    except:
        return False

