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
        if algoritmo == "FCFS":
            self.simulador.ejecutar_fcfs()
        elif algoritmo == "SJF":
            self.simulador.ejecutar_sjf()
        elif algoritmo == "SRTF":
            self.simulador.ejecutar_srtf()
        elif algoritmo == "Round Robin":
            quantum_valor = self.quantum.get()
            if quantum_valor <= 0:
                messagebox.showwarning("Advertencia", "El quantum debe ser un valor positivo.")
                return
            self.simulador.ejecutar_round_robin(quantum_valor)
        
        self.actualizar_visualizacion_historial()
        self.actualizar_metricas_ui()
        self.actualizar_histograma()

        self.instante_actual_animacion = 0
        self.historial_visual_keys = sorted(list(self.simulador.historial_ejecucion_visual.keys()))
        self.proceso_anterior_animacion = None
        self.tiempo_inicio_segmento_animacion = None
        self.animation_id = None
        
        self.asignar_colores_procesos()
        
        self.linea_actual_gantt.set_xdata([0, 0])
        self.linea_actual_gantt.set_ydata([0, 1])
        
        self.iniciar_animacion_gantt()

    def asignar_colores_procesos(self):
        nombres_procesos = sorted(list(set(self.simulador.historial_ejecucion_visual.values())))
        if "Inactivo" in nombres_procesos:
            self.colores_procesos["Inactivo"] = "#D3D3D3"
            nombres_procesos.remove("Inactivo")
        
        for nombre in nombres_procesos:
            if nombre not in self.colores_procesos:
                self.colores_procesos[nombre] = self.generar_color_aleatorio()

        self.ax_gantt.set_yticks([0.5])
        self.ax_gantt.set_yticklabels(['CPU'])

    def iniciar_animacion_gantt(self):
        if self.instante_actual_animacion >= len(self.historial_visual_keys):
            if self.proceso_anterior_animacion is not None:
                self.dibujar_segmento_gantt(self.proceso_anterior_animacion, self.tiempo_inicio_segmento_animacion, self.historial_visual_keys[-1] + 1)
            self.linea_actual_gantt.set_xdata([])
            self.tiempo_label_gantt.set_text('')
            
            # Dibuja las líneas de llegada y finalización después de la animación
            self.dibujar_lineas_temporales()
            
            self.fig.canvas.draw()
            return

        tiempo_actual_en_simulacion = self.historial_visual_keys[self.instante_actual_animacion]
        proceso_actual_nombre = self.simulador.historial_ejecucion_visual[tiempo_actual_en_simulacion]
        
        if proceso_actual_nombre != self.proceso_anterior_animacion:
            if self.proceso_anterior_animacion is not None:
                self.dibujar_segmento_gantt(self.proceso_anterior_animacion, self.tiempo_inicio_segmento_animacion, tiempo_actual_en_simulacion)
            
            self.tiempo_inicio_segmento_animacion = tiempo_actual_en_simulacion
            self.proceso_anterior_animacion = proceso_actual_nombre

        self.linea_actual_gantt.set_xdata([tiempo_actual_en_simulacion, tiempo_actual_en_simulacion])
        self.tiempo_label_gantt.set_text(f't={tiempo_actual_en_simulacion}')
        self.tiempo_label_gantt.set_position((tiempo_actual_en_simulacion, 1.05))
        
        # Setea los ticks del eje x para que se muestren de uno en uno
        max_tiempo = max(self.historial_visual_keys) + 2 if self.historial_visual_keys else 10
        self.ax_gantt.set_xlim(left=0, right=max_tiempo)
        self.ax_gantt.set_xticks(np.arange(0, int(max_tiempo), 1))
        
        self.fig.canvas.draw()
        
        self.instante_actual_animacion += 1
        self.animation_id = self.master.after(1000, self.iniciar_animacion_gantt)

    def dibujar_segmento_gantt(self, nombre_proceso, inicio_tiempo, fin_tiempo):
        self.ax_gantt.barh(0.5, fin_tiempo - inicio_tiempo, left=inicio_tiempo, height=0.5, 
                          color=self.colores_procesos.get(nombre_proceso, self.generar_color_aleatorio()), 
                          edgecolor='black')
        
        self.ax_gantt.text(inicio_tiempo + (fin_tiempo - inicio_tiempo) / 2, 0.5, nombre_proceso, 
                          ha='center', va='center', color='white', fontsize=8)

    def dibujar_lineas_temporales(self):
        for proceso in self.simulador.historial_ejecucion:
            self.ax_gantt.axvline(x=proceso.instante_llegada, color=self.colores_procesos.get(proceso.nombre, 'gray'), linestyle=':', linewidth=1)
            self.ax_gantt.axvline(x=proceso.tiempo_finalizacion, color=self.colores_procesos.get(proceso.nombre, 'gray'), linestyle='--', linewidth=1)
            
            # Etiqueta para el tiempo de finalización
            self.ax_gantt.text(proceso.tiempo_finalizacion, 0.75, f'{proceso.tiempo_finalizacion}', rotation=90, va='center', ha='right', fontsize=6, color=self.colores_procesos.get(proceso.nombre, 'gray'))

    def actualizar_visualizacion_historial(self):
        self.lista_procesos_historial.delete(0, tk.END)
        for proceso in self.simulador.historial_ejecucion:
            self.lista_procesos_historial.insert(tk.END, f"PID: {proceso.pid} - Nombre: {proceso.nombre} - Tiempo Final: {proceso.tiempo_finalizacion}")
    
    def actualizar_metricas_ui(self):
        promedio_retorno, promedio_espera = self.simulador.calcular_metricas()
        
        self.label_tiempo_retorno_promedio.config(text=f"Tiempo de Retorno Promedio: {promedio_retorno:.2f}")
        self.label_tiempo_espera_promedio.config(text=f"Tiempo de Espera Promedio: {promedio_espera:.2f}")

    def actualizar_histograma(self):
        algoritmo_actual = self.algoritmo_var.get()
        tiempos_espera = [p.tiempo_espera for p in self.simulador.historial_ejecucion]
        
        self.simulaciones_historial[algoritmo_actual] = tiempos_espera
        
        
        self.ax_hist.clear()