import tkinter as tk
from tkinter import ttk
from simulador import Simulador
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
from tkinter import messagebox
import numpy as np

class SimuladorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Simulador de Procesos")
        self.simulador = Simulador()
        self.simulaciones_historial = {}

        self.algoritmo_var = tk.StringVar(self.master)
        self.quantum = tk.IntVar(self.master)
        self.quantum.set(4)

        self.label_tiempo_retorno_promedio = None
        self.label_tiempo_espera_promedio = None

        self.colores_procesos = {}

        self.fig, (self.ax_gantt, self.ax_hist) = plt.subplots(2, 1, figsize=(8, 4))
        
        self.linea_actual_gantt, = self.ax_gantt.plot([], [], color='red', linestyle='--', linewidth=1, zorder=2)
        self.tiempo_label_gantt = self.ax_gantt.text(0, 1.05, '', ha='center', va='bottom', fontsize=8, color='red')
        
        self.fig.tight_layout(pad=5.0)

        self.instante_actual_animacion = 0
        self.historial_visual_keys = []
        self.proceso_anterior_animacion = None
        self.tiempo_inicio_segmento_animacion = None
        self.animation_id = None

        self.crear_widgets()

    def generar_color_aleatorio(self):
        return "#%06x" % random.randint(0, 0xFFFFFF)

    def anadir_proceso(self):
        try:
            nombre = self.entry_nombre.get()
            tiempo_cpu = int(self.entry_tiempo_cpu.get())
            instante_llegada = int(self.entry_instante_llegada.get())

            if not nombre or tiempo_cpu <= 0 or instante_llegada < 0:
                messagebox.showwarning("Advertencia", "Los datos del proceso no son válidos. Por favor, asegúrese de que el nombre no esté vacío, el tiempo de CPU sea un número positivo y el instante de llegada sea un número no negativo.")
                return

            self.simulador.agregar_proceso(nombre, tiempo_cpu, instante_llegada)
            self.actualizar_visualizacion_lista_procesos()

            self.entry_nombre.delete(0, tk.END)
            self.entry_tiempo_cpu.delete(0, tk.END)
            self.entry_instante_llegada.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Error", "Por favor, introduzca valores numéricos válidos para el tiempo de CPU y el instante de llegada.")

    def actualizar_visualizacion_lista_procesos(self):
        self.lista_procesos_cola.delete(0, tk.END)
        for proceso in self.simulador.cola_llegadas:
            self.lista_procesos_cola.insert(tk.END, f"PID: {proceso.pid} - Nombre: {proceso.nombre} - Tiempo: {proceso.tiempo_cpu} - Llegada: {proceso.instante_llegada}")
    
    def iniciar_simulacion(self):
        if not self.lista_procesos_cola.get(0, tk.END):
            messagebox.showwarning("Advertencia", "Por favor, añada al menos un proceso antes de iniciar la simulación.")
            return

        if self.animation_id:
            self.master.after_cancel(self.animation_id)

        self.simulador = Simulador()
        procesos_en_cola = self.lista_procesos_cola.get(0, tk.END)
        for p_str in procesos_en_cola:
            partes = p_str.split(" - ")
            nombre = partes[1].split(": ")[1]
            tiempo_cpu = int(partes[2].split(": ")[1])
            instante_llegada = int(partes[3].split(": ")[1])
            self.simulador.agregar_proceso(nombre, tiempo_cpu, instante_llegada)
            
        algoritmo = self.algoritmo_var.get()
        
        self.lista_procesos_historial.delete(0, tk.END)

        self.ax_gantt.clear()
        self.ax_gantt.set_title(f'Diagrama de Gantt - {algoritmo}')
        self.ax_gantt.set_xlabel('Tiempo')
        self.ax_gantt.set_ylabel('Proceso')
        self.ax_gantt.set_yticks([])
        self.ax_gantt.set_ylim(0, 1)

