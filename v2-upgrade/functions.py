from pathlib import Path
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
    shows stats for a selected localidad.
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

def descargar_estadisticas_caso_popup(data):
    '''
    Genera un archivo CSV "estadisticas_caso.csv" con casos desglosados por localidad, sexo y tipo de caso.
    '''

    tipos_caso = sorted(data["Tipo de caso"].unique())
    localidades = sorted(data["Localidad de residencia"].unique())

    # Columnas para el DataFrame de salida
    columnas = (
        [f"F_{t}" for t in tipos_caso] + ["F_Total"] +
        [f"M_{t}" for t in tipos_caso] + ["M_Total", "Total"]
    )

    resultados = {}

    for loc in localidades:
        data_loc = data[data["Localidad de residencia"] == loc]
        total = len(data_loc)

        # Femenino
        data_f = data_loc[data_loc["Sexo"] == "F"]
        f_total = len(data_f)
        f_tipos = [(data_f["Tipo de caso"] == tipo).sum() for tipo in tipos_caso]

        # Masculino
        data_m = data_loc[data_loc["Sexo"] == "M"]
        m_total = len(data_m)
        m_tipos = [(data_m["Tipo de caso"] == tipo).sum() for tipo in tipos_caso]

        row = f_tipos + [f_total] + m_tipos + [m_total, total]
        resultados[loc] = row

    # Crear DataFrame final
    output_data = pd.DataFrame.from_dict(resultados, orient='index', columns=columnas)
    output_data.reset_index(inplace=True)
    output_data.rename(columns={'index': 'Localidad'}, inplace=True)

    # Guardar archivo
    output_dir = Path(__file__).resolve().parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / "estadisticas_caso.csv"

    with open(file_path, "w", encoding="utf-8", newline='') as f:
        f.write("sep=,\n")
        output_data.to_csv(f, index=False)

    # Popup de confirmación
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(
        "Archivo generado",
        f"El archivo 'estadisticas_caso.csv' fue creado exitosamente en:\n{file_path}"
    )

def descargar_estadisticas_popup(data):
    '''
    Genera un archivo CSV con estadísticas generales
    Muestra un popup con la ruta del archivo guardado.
    :param DataFrame data: DataFrame con los casos.
    '''

    # Define categorías
    ubicaciones = sorted(data["Ubicacion"].unique())
    tipos_casos = sorted(data["Tipo de caso"].unique())
    sexos = sorted(data["Sexo"].unique())
    edades = ["Niños", "Adolescentes", "Adultos"]

    columnas = ubicaciones + tipos_casos + sexos + edades

    # Diccionario para acumular resultados por localidad
    localidades = sorted(data["Localidad de residencia"].unique())
    data_dict = {}

    for localidad in localidades:
        data_loc = data[data["Localidad de residencia"] == localidad]
        total = len(data_loc)
        fila = []

        # Por ubicación
        for ubic in ubicaciones:
            porcentaje = (data_loc["Ubicacion"] == ubic).sum() * 100 / total
            fila.append(round(porcentaje, 2))

        # Por tipo de caso
        for tipo in tipos_casos:
            porcentaje = (data_loc["Tipo de caso"] == tipo).sum() * 100 / total
            fila.append(round(porcentaje, 2))

        # Por sexo
        for sexo in sexos:
            porcentaje = (data_loc["Sexo"] == sexo).sum() * 100 / total
            fila.append(round(porcentaje, 2))

        # Por edad
        edades_contadas = [0, 0, 0]
        for edad in data_loc["Edad"]:
            edad = int(edad)
            if edad < 14:
                edades_contadas[0] += 1
            elif edad < 18:
                edades_contadas[1] += 1
            else:
                edades_contadas[2] += 1

        for valor in edades_contadas:
            fila.append(round(valor * 100 / total, 2))

        data_dict[localidad] = fila

    # Convertir a DataFrame y transponer
    output_data = pd.DataFrame.from_dict(data_dict, orient='index', columns=columnas)

    # Asegurarse de que el índice es columna
    output_data.reset_index(inplace=True)
    output_data.rename(columns={'index': 'Localidad'}, inplace=True)

    # Guardar como CSV con separador explícito
    output_dir = Path(__file__).resolve().parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / "estadisticas_generales.csv"

    with open(file_path, "w", encoding="utf-8", newline='') as f:
        f.write("sep=,\n")
        output_data.to_csv(f, index=False)

    # Mostrar popup
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(
        "Archivo generado",
        f"El archivo 'estadisticas_generales.csv' fue creado exitosamente en:\n{file_path}"
    )

def opciones(opcion, csv_path):
    '''
    Ejecuta una funcion de acuerdo a la opcion que escogio el operador
    :param int opcion: el numero de la opcion que escoge el operador
    No retorna
    '''
    
    # Read CSV with pandas
    print(csv_path)
    data = pd.read_csv(csv_path)

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
        descargar_estadisticas_caso_popup(data)
    elif opcion == 7:
        descargar_estadisticas_popup(data)
