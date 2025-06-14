import tkinter as tk
from tkinter import ttk, messagebox
from functions import opciones

class Menu:
    def __init__(self, root, csv_path):
        self.root = root
        self.csv_path = csv_path
        self.root.title("Bogotá COVID-19")

        self.label = ttk.Label(root, text="Selecciona una opción:", font=("Segoe UI", 14))
        self.label.pack(pady=10)

        options = [
            "Leer datos",
            "Estadísticas por localidad",
            "Contagios por rango de fechas",
            "Top 3 localidades con más contagios",
            "Top 3 localidades con menos contagios",
            "Descargar estadísticas por caso",
            "Descargar estadísticas generales",
            "Salir"
        ]

        for i, option in enumerate(options, start=1):
            ttk.Button(root, text=f"{i}. {option}", command=lambda i=i: self.handle_option(i)).pack(padx=10, pady=4, fill='x')

    def handle_option(self, option):
        if option == 8:
            self.root.quit()
        else:
            try:
                opciones(option, self.csv_path)
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error:\n{str(e)}")

def launch_gui(csv_path):
    root = tk.Tk()
    app = Menu(root, csv_path)
    root.mainloop()
