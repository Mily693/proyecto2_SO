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

        algoritmos_graficar = list(self.simulaciones_historial.keys())
        tiempos_por_algoritmo = [self.simulaciones_historial[alg] for alg in algoritmos_graficar]

        if tiempos_por_algoritmo and any(tiempos_por_algoritmo):
            self.ax_hist.hist(tiempos_por_algoritmo, bins=5, label=algoritmos_graficar, color=[self.colores_procesos.get(alg, self.generar_color_aleatorio()) for alg in algoritmos_graficar], edgecolor='black')
        else:
            self.ax_hist.text(0.5, 0.5, 'No hay datos para mostrar', ha='center', va='center', transform=self.ax_hist.transAxes)
        
        self.ax_hist.set_title("Comparación de Tiempos de Espera")
        self.ax_hist.set_xlabel("Tiempo de Espera")
        self.ax_hist.set_ylabel("Frecuencia")
        self.ax_hist.legend(loc='best')
        self.fig.canvas.draw()
        
    def crear_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        frame_crear_proceso = ttk.LabelFrame(main_frame, text="Añadir Nuevo Proceso", padding="10")
        frame_crear_proceso.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        ttk.Label(frame_crear_proceso, text="Nombre:").grid(row=0, column=0, padx=2, pady=2, sticky="w")
        self.entry_nombre = ttk.Entry(frame_crear_proceso)
        self.entry_nombre.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        
        ttk.Label(frame_crear_proceso, text="Tiempo CPU:").grid(row=0, column=2, padx=2, pady=2, sticky="w")
        self.entry_tiempo_cpu = ttk.Entry(frame_crear_proceso)
        self.entry_tiempo_cpu.grid(row=0, column=3, padx=2, pady=2, sticky="ew")

        ttk.Label(frame_crear_proceso, text="Llegada:").grid(row=0, column=4, padx=2, pady=2, sticky="w")
        self.entry_instante_llegada = ttk.Entry(frame_crear_proceso)
        self.entry_instante_llegada.grid(row=0, column=5, padx=2, pady=2, sticky="ew")

        ttk.Button(frame_crear_proceso, text="Añadir Proceso", command=self.anadir_proceso).grid(row=0, column=6, padx=10, pady=2)
        
        frame_algoritmo = ttk.LabelFrame(main_frame, text="Configuración de Simulación", padding="10")
        frame_algoritmo.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        algoritmos = ["FCFS", "SJF", "SRTF", "Round Robin"]
        self.algoritmo_var.set(algoritmos[0])
        
        ttk.Label(frame_algoritmo, text="Algoritmo:").grid(row=0, column=0, padx=2, pady=2, sticky="w")
        opcion_menu_algoritmo = ttk.OptionMenu(frame_algoritmo, self.algoritmo_var, algoritmos[0], *algoritmos)
        opcion_menu_algoritmo.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        
        ttk.Label(frame_algoritmo, text="Quantum (RR):").grid(row=0, column=2, padx=2, pady=2, sticky="w")
        ttk.Entry(frame_algoritmo, textvariable=self.quantum, width=5).grid(row=0, column=3, padx=2, pady=2, sticky="ew")
        
        ttk.Button(frame_algoritmo, text="Iniciar Simulación", command=self.iniciar_simulacion).grid(row=0, column=4, padx=10, pady=2)
        
        frame_listas = ttk.Frame(main_frame)
        frame_listas.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        main_frame.grid_rowconfigure(2, weight=1)

        ttk.Label(frame_listas, text="Cola de Procesos Listos").pack(pady=2)
        self.lista_procesos_cola = tk.Listbox(frame_listas, height=15, width=50)
        self.lista_procesos_cola.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        ttk.Label(frame_listas, text="Historial de Procesos Ejecutados").pack(pady=2)
        self.lista_procesos_historial = tk.Listbox(frame_listas, height=15)
        self.lista_procesos_historial.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        frame_metricas_y_gantt = ttk.Frame(main_frame)
        frame_metricas_y_gantt.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(frame_metricas_y_gantt, text="Métricas de Rendimiento", font=('Arial', 10, 'bold')).pack(pady=(5,2))
        self.label_tiempo_retorno_promedio = ttk.Label(frame_metricas_y_gantt, text="Tiempo de Retorno Promedio: 0.00")
        self.label_tiempo_retorno_promedio.pack(pady=1, anchor="w")
        
        self.label_tiempo_espera_promedio = ttk.Label(frame_metricas_y_gantt, text="Tiempo de Espera Promedio: 0.00")
        self.label_tiempo_espera_promedio.pack(pady=1, anchor="w")

        ttk.Label(frame_metricas_y_gantt, text="Diagrama de Gantt", font=('Arial', 10, 'bold')).pack(pady=(10, 5))
        
        self.canvas_gantt = FigureCanvasTkAgg(self.fig, master=frame_metricas_y_gantt)
        self.canvas_gantt_widget = self.canvas_gantt.get_tk_widget()
        self.canvas_gantt_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorApp(root)
    root.mainloop()