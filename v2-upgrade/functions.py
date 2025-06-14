from extraction import volver_al_menu, try_opcion, casos_archivo
import os
import csv
from tkinter.ttk import Treeview
import pandas as pd
import tkinter as tk
from tkinter import Toplevel, Scrollbar, ttk, messagebox
from tkcalendar import DateEntry

def leer_datos(data):
    """
    Abre una ventana con todos los datos cargados desde el CSV.
    """
    # Create popup window
    ventana = Toplevel()
    ventana.title("Datos del archivo")

    tree = Treeview(ventana)
    tree.pack(side="left", fill="both", expand=True)

    # Add vertical scrollbar
    vsb = Scrollbar(ventana, orient="vertical", command=tree.yview)
    vsb.pack(side="right", fill="y")
    tree.configure(yscrollcommand=vsb.set)

    # Define columns
    tree["columns"] = list(data.columns)
    tree["show"] = "headings"

    for col in data.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="w")

    # Insert data rows
    for _, row in data.iterrows():
        tree.insert("", "end", values=list(row))

def localidad_diccionario(data_local):
    """
    Generates a stats dictionary for a given localidad's DataFrame slice.
    
    :param DataFrame data_local: Filtered DataFrame for one localidad
    :return dict: Dictionary with statistics
    """

    diccionario_localidad = {
        "Total contagiados": len(data_local),
        "Sexo": {},
        "Tipo de caso": {},
        "Tipo de ubicacion": {},
        "Edades": {
            "0 a 13 anos": 0,
            "14 a 17 anos": 0,
            "18+ anos": 0
        },
        "Estado": {}
    }

    # Sexo
    sexo_counts = data_local["Sexo"].value_counts()
    diccionario_localidad["Sexo"]["Hombres"] = sexo_counts.get("M", 0)
    diccionario_localidad["Sexo"]["Mujeres"] = sexo_counts.get("F", 0)

    # Tipo de caso
    diccionario_localidad["Tipo de caso"] = data_local["Tipo de caso"].value_counts().to_dict()

    # Tipo de ubicacion
    diccionario_localidad["Tipo de ubicacion"] = data_local["Ubicacion"].value_counts().to_dict()

    # Estado
    diccionario_localidad["Estado"] = data_local["Estado"].value_counts().to_dict()

    # Edades (convert column to int first if not already)
    edades = pd.to_numeric(data_local["Edad"], errors='coerce').dropna().astype(int)
    diccionario_localidad["Edades"]["0 a 13 anos"] = (edades <= 13).sum()
    diccionario_localidad["Edades"]["14 a 17 anos"] = ((edades > 13) & (edades <= 17)).sum()
    diccionario_localidad["Edades"]["18+ anos"] = (edades > 17).sum()

    return diccionario_localidad

def estadisticas_localidad(localidad, data):
    """
    GUI version: shows stats for a selected localidad.
    """

    # Filter the DataFrame
    data_local = data[data["Localidad de residencia"] == localidad]
    print("Filtered")

    if data_local.empty:
        messagebox.showinfo("Sin datos", f"No hay datos para la localidad: {localidad}")
        return
    
    # Get the stats from your helper function
    stats_dict = localidad_diccionario(data_local)

    # Define available keys
    opciones = [
        "Total contagiados",
        "Sexo",
        "Tipo de caso",
        "Tipo de ubicacion",
        "Edades",
        "Estado"
    ]

    # Create window
    ventana = Toplevel()
    ventana.title(f"Estadísticas de {localidad}")
    ventana.geometry("450x400")

    label = ttk.Label(ventana, text=f"Estadísticas para: {localidad}", font=("Segoe UI", 12, "bold"))
    label.pack(pady=10)

    # Dropdown menu
    seleccion = tk.StringVar()
    dropdown = ttk.Combobox(ventana, textvariable=seleccion, values=opciones, state="readonly")
    dropdown.pack(pady=5)
    dropdown.current(0)

    # Text output
    output = tk.Text(ventana, height=15, width=50, wrap="word", font=("Courier New", 10))
    output.pack(pady=10)

    def mostrar_estadistica():
        selected = seleccion.get()
        output.delete(1.0, tk.END)

        if selected == "Total contagiados":
            output.insert(tk.END, f"Total contagiados en {localidad}: {stats_dict['Total contagiados']}")
        elif selected == "Sexo":
            output.insert(tk.END, f"Hombres: {stats_dict['Sexo'].get('Hombres', 0)}\n")
            output.insert(tk.END, f"Mujeres: {stats_dict['Sexo'].get('Mujeres', 0)}")
        elif selected in stats_dict:
            output.insert(tk.END, f"{selected}\n\n")
            for k, v in stats_dict[selected].items():
                output.insert(tk.END, f"{k:<30} {v}\n")
        else:
            output.insert(tk.END, "Estadística no disponible.")

    ttk.Button(ventana, text="Mostrar", command=mostrar_estadistica).pack()
    ttk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=5)

def menu_localidades_gui(data):
    """
    Opens a GUI window showing all localidades to choose from.
    Calls estadisticas_localidad(localidad, data) with selection.
    """
    # Get unique localidades
    if "Localidad de residencia" not in data.columns:
        messagebox.showerror("Error", "La columna 'Localidad' no se encuentra en el archivo.")
        return

    localidades = sorted(data["Localidad de residencia"].dropna().unique())

    # Popup window
    ventana = Toplevel()
    ventana.title("Seleccionar localidad")
    ventana.geometry("300x200")

    label = ttk.Label(ventana, text="Seleccione una localidad:", font=("Segoe UI", 12))
    label.pack(pady=10)

    selected = tk.StringVar()
    combobox = ttk.Combobox(ventana, textvariable=selected, values=localidades, state="readonly")
    combobox.pack(pady=5)
    combobox.current(0)

    def confirmar():
        localidad = selected.get()
        if localidad:
            try:
                estadisticas_localidad(localidad, data)
                ventana.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo ejecutar la función:\n{e}")
        else:
            messagebox.showwarning("Aviso", "Debe seleccionar una localidad.")

    ttk.Button(ventana, text="Aceptar", command=confirmar).pack(pady=10)
    ttk.Button(ventana, text="Cancelar", command=ventana.destroy).pack()

def rango_fecha(data):

    # Ensure the 'Fecha de diagnostico' column is datetime
    data["Fecha de diagnostico"] = pd.to_datetime(data["Fecha de diagnostico"], errors='coerce', dayfirst=True)

    # GUI
    # Popup window
    ventana = Toplevel()
    ventana.title("Contagiados por Rango de Fecha")
    ventana.geometry("400x600")

    # Labels
    start_label = ttk.Label(ventana, text="Fecha inicial:")
    start_label.grid(row=0, column=0, sticky=tk.W)
    end_label = ttk.Label(ventana, text="Fecha final:")
    end_label.grid(row=1, column=0, sticky=tk.W)

    # Date Pickers
    start_date = DateEntry(ventana, date_pattern='dd-mm-yyyy')
    start_date.grid(row=0, column=1, padx=5)
    end_date = DateEntry(ventana, date_pattern='dd-mm-yyyy')
    end_date.grid(row=1, column=1, padx=5)

    # Result Box
    result_box = tk.Text(ventana, height=30, width=50)
    result_box.grid(row=3, column=0, columnspan=2, pady=10)

    # Function to filter and display results
    def show_results():
        ini = pd.to_datetime(start_date.get(), format='%d-%m-%Y')
        fin = pd.to_datetime(end_date.get(), format='%d-%m-%Y')
        filtered = data[(data['Fecha de diagnostico'] >= ini) & (data['Fecha de diagnostico'] <= fin)]
        counts = filtered['Localidad de residencia'].value_counts().sort_index()
        
        result_box.delete('1.0', tk.END)
        result_box.insert(tk.END, f"Datos entre {ini.strftime('%d-%m-%Y')} y {fin.strftime('%d-%m-%Y')}\n\n")
        for localidad, count in counts.items():
            result_box.insert(tk.END, f"{localidad:<20}: {count}\n")

    # Button
    btn = ttk.Button(ventana, text="Mostrar resultados", command=show_results)
    btn.grid(row=2, column=0, columnspan=2, pady=5)

def mayor_contagio_popup(data):
    '''
    Muestra un popup con las tres localidades con más contagios.
    :param DataFrame data: DataFrame con los datos de casos.
    '''
    contagios_por_localidad = data["Localidad de residencia"].value_counts().head(3)

    popup = Toplevel()
    popup.title("Top 3 Localidades con Mayor Contagio")
    popup.geometry("400x200")

    ttk.Label(popup, text="Top 3 Localidades con Mayor Contagio", font=("Arial", 14, "bold")).pack(pady=10)

    for localidad, contagios in contagios_por_localidad.items():
        ttk.Label(popup, text=f"{localidad:<20}: {contagios} casos", font=("Arial", 12)).pack()

def menor_contagio_popup(data):
    '''
    Muestra un popup con las tres localidades con menos contagios.
    :param DataFrame data: DataFrame con los datos de casos.
    '''
    contagios_por_localidad = data["Localidad de residencia"].value_counts().tail(3)

    popup = Toplevel()
    popup.title("Top 3 Localidades con Menor Contagio")
    popup.geometry("400x200")

    ttk.Label(popup, text="Top 3 Localidades con Menor Contagio", font=("Arial", 14, "bold")).pack(pady=10)

    for localidad, contagios in contagios_por_localidad.items():
        ttk.Label(popup, text=f"{localidad:<20}: {contagios} casos", font=("Arial", 12)).pack()

#Define la funcion descargar_estadisticas_caso()
def descargar_estadisticas_caso(Casos_matriz):
    '''
    Crea un archivo con el nombre "estadisticas_caso.csv" que contiene datos por localidad y sexo.
    :param list Casos_matriz: Matriz con los casos.
    No retorna a menos que sea para volver al menu.
    '''

    #Indica la opcion seleccionada.
    print("\nEscogio la opcion de descargar estadisticas por caso.")

    #Permite volver al menu principal.
    if volver_al_menu():
        return

    #Elimina la primera linea de la matriz.
    del Casos_matriz[0]

    #Crea una lista con las localidades organizadas alfabeticamente.
    localidades = list(set([caso[2] for caso in Casos_matriz]))
    localidades.sort()

    #Crea una lista con los tipos de caso organizados alfabeticamente.
    tipos_de_caso = list(set([caso[5] for caso in Casos_matriz]))
    tipos_de_caso.sort()

    #Crea una variable.
    categoria = tipos_de_caso + ["F Total"] + tipos_de_caso + ["M Total"] + ["Total"]

    #Crea un diccionario.
    diccionario = {"Localidad": categoria}

    #Agrega las localidades como llaves al diccionario.
    for localidad in localidades:
        diccionario[localidad] = [0 for tipo_de_caso in categoria]

    #Actualiza el diccionario.
    for caso in Casos_matriz:
        diccionario[caso[2]][len(diccionario[caso[2]]) - 1] += 1

        if caso[4] == "M":
            diccionario[caso[2]][len(diccionario[caso[2]]) - 2] += 1
            for tipo_de_caso in range(len(tipos_de_caso)):
                if caso[5] == tipos_de_caso[tipo_de_caso]:
                    diccionario[caso[2]][len(tipos_de_caso) + 1 + tipo_de_caso] += 1

        elif caso[4] == "F":
            diccionario[caso[2]][len(diccionario[caso[2]]) - 3 - len(tipos_de_caso)] += 1
            for tipo_de_caso in range(len(tipos_de_caso)):
                if caso[5] == tipos_de_caso[tipo_de_caso]:
                    diccionario[caso[2]][tipo_de_caso] += 1

    #Los valores del diccionario se convierten a string.
    for llave in diccionario.keys():
        diccionario[llave] = [str(valor) for valor in diccionario[llave]]

    # Path to the directory where this .py file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Build the path to the CSV file
    csv_path = os.path.join(current_dir, "data", "estadisticas_caso.csv")

    #Se crea el archivo "estadisticas_caso.csv" en la carpeta "archivos".
    Archivo_estadisticas_caso = open(csv_path, "w")
        
    #Indica el separador y lo escribe en el archivo.
    Archivo_estadisticas_caso.write("sep=,\n")

    #Escribe los datos en el archivo.
    for llave in diccionario.keys():
        Archivo_estadisticas_caso.write(llave + ",")
        Archivo_estadisticas_caso.write(",".join(diccionario[llave]) + "\n")

    #Cierra el archivo.
    Archivo_estadisticas_caso.close()

    #Le indica el operador que se ha creado el archivo.
    print('\nEl archivo "estadisticas_caso.csv" se ha generado correctamente en la carpeta archivos')

    #Permite que el operador decida cuando volver al menu.
    input("\nPresione enter para volver al menu: ")

#Define la funcion descargar_estadisticas()
def descargar_estadisticas(Casos_matriz):
    '''
    Crea un archivo de nombre "estadisticas_generales.csv" con estadisticas generales.
    :param list Casos_matriz: Matriz con los casos.
    No retorna a menos que sea para volver al menu.
    '''

    #Indica la opcion seleccionada.
    print("\nEscogio la opcion de descargar estadisticas generales")

    #Permite volver al menu principal.
    if volver_al_menu():
        return

    #Elimina la primera linea.
    del Casos_matriz[0]
   
    #Crea una lista con las localidades organizadas alfabeticamente.
    localidades = list(set([caso[2] for caso in Casos_matriz]))
    localidades.sort()

    #Crea una lista con las ubicaciones organizadas alfabeticamente.
    ubicaciones = list(set([caso[6] for caso in Casos_matriz]))
    ubicaciones.sort()

    #Crea una lista con los tipos de casos organizados alfabeticamente.
    tipos_de_casos = list(set([caso[5] for caso in Casos_matriz]))
    tipos_de_casos.sort()

    #Crea una lista con las posibilidades de sexo.
    Sexos = list(set([caso[4] for caso in Casos_matriz]))

    #Crea una lista con cateogrias para la edad.
    Edades = ["Niños", "Adolescentes", "Adultos"]

    #Inicializa un diccionario con estadisticas generales.
    diccionario = {"Localidad": ubicaciones + tipos_de_casos + Sexos + Edades}

    #Inicializa un diccionario de localidades.
    localidades_totales = {}

    #Actualiza ambos diccionarios con las localidades como llaves, pero diferentes valores.
    for localidad in localidades:
        localidades_totales[localidad] = 0
        diccionario[localidad] = [0 for categoria in diccionario["Localidad"]]

    #Actualiza el diccionario de localidades.
    for caso in Casos_matriz:
        for localidad in localidades:
            if caso[2] == localidad:
                localidades_totales[localidad] += 1
                break

    #Actualiza el diccionario con estadisticas generales.
    for caso in Casos_matriz:
        for ubicacion in range(len(ubicaciones)):
            if caso[6] == ubicaciones[ubicacion]:
                diccionario[caso[2]][ubicacion] += 1
                break
        
        for tipo_de_caso in range(len(tipos_de_casos)):
            if caso[5] == tipos_de_casos[tipo_de_caso]:
                diccionario[caso[2]][len(ubicaciones) + tipo_de_caso] += 1
                break

        for sexo in range(len(Sexos)):
            if caso[4] == Sexos[sexo]:
                diccionario[caso[2]][len(ubicaciones) + len(tipos_de_casos) + sexo] += 1
                break

        if int(caso[3]) < 14:
            diccionario[caso[2]][len(diccionario[caso[2]]) - 3] += 1

        elif int(caso[3]) < 18:
            diccionario[caso[2]][len(diccionario[caso[2]]) - 2] += 1

        else:
            diccionario[caso[2]][len(diccionario[caso[2]]) - 1] += 1

    #Divide los valores del diccionarios con estadisticas generales por los casos totales en esa localidad y lo multiplica por cien para obtener el porcentaje.
    for localidad in localidades:
        diccionario[localidad] = [str(round(valor*100/localidades_totales[localidad], 2)) + "%" for valor in diccionario[localidad]]

    # Path to the directory where this .py file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Build the path to the CSV file
    csv_path = os.path.join(current_dir, "data", "estadisticas_generales.csv")

    #Se crea el archivo "estadisticas_caso.csv" en la carpeta "archivos".
    Archivo = open(csv_path, "w")

    #Escribe el seperador.
    Archivo.write("sep=,\n")

    #Escribe las estadisticas generales.
    for llave in diccionario.keys():
        Archivo.write(llave + ",")
        Archivo.write(",".join(diccionario[llave]) + "\n")

    #Cierra el archivo.
    Archivo.close()

    #Imprime una verificacion de la creacion del archivo.
    print('\nEl archivo "estadisticas_generales.csv" se ha creado exitosamente.')

    #Permite que el operador decida cuando volver al menu.
    input("\nPresione enter para volver al menu: ")

#Define la funcion opciones()
def opciones(opcion, csv_path):
    '''
    Ejecuta una funcion de acuerdo a la opcion que escogio el operador
    :param int opcion: el numero de la opcion que escoge el operador
    No retorna
    '''
    Casos_matriz = casos_archivo()

    # Read CSV with pandas
    print(csv_path)
    data = pd.read_csv(csv_path)

    #Condicionales de acuerdo a la opcion escogida, ejecuta funciones diferentes.
    if opcion == 1:
        leer_datos(data)

    elif opcion == 2: 
        menu_localidades_gui(data)

    elif opcion == 3:
        rango_fecha(data)

    elif opcion == 4:
        mayor_contagio_popup(data)

    elif opcion == 5:
        menor_contagio_popup(data)

    elif opcion == 6:
        descargar_estadisticas_caso(Casos_matriz)

    elif opcion == 7:
        descargar_estadisticas(Casos_matriz)
