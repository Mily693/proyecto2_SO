# main.py (SimuladorApp)
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import numpy as np
# Importamos la clase Simulador (que a su vez importa Proceso)
from simulador import Simulador 

class SimuladorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Simulador de Procesos")
        self.simulador = Simulador()
        self.simulaciones_historial = {}

        self.algoritmo_var = tk.StringVar(self.master)
        self.quantum = tk.IntVar(self.master, value=4) # Valor inicial para RR

        self.label_tiempo_retorno_promedio = None
        self.label_tiempo_espera_promedio = None
        self.label_indice_servicio_promedio = None 
        
        self.colores_procesos = {}

        # MODIFICACIÓN CLAVE 1: Crear dos subplots nuevamente: 
        # uno para el Gantt por Proceso y otro para el Gantt de CPU.
        self.fig, (self.ax_gantt_per_process, self.ax_gantt_cpu) = plt.subplots(2, 1, figsize=(8, 6)) 
        self.fig.tight_layout(pad=3.0) 

        # Renombramos el Gantt principal para mayor claridad
        self.ax_gantt = self.ax_gantt_per_process 
        
        self.instante_actual_animacion = 0
        self.historial_visual_keys = []
        self.animation_id = None
        
        self.treeview_metricas_por_proceso = None

        self.crear_widgets()

    def generar_color_aleatorio(self):
        return "#%06x" % random.randint(0, 0xFFFFFF)

    def anadir_proceso(self):
        try:
            nombre = self.entry_nombre.get()
            tiempo_cpu = int(self.entry_tiempo_cpu.get())
            instante_llegada = int(self.entry_instante_llegada.get())

            if not nombre or tiempo_cpu <= 0 or instante_llegada < 0:
                messagebox.showwarning("Advertencia", "Datos no válidos.")
                return

            self.simulador.agregar_proceso(nombre, tiempo_cpu, instante_llegada)
            self.actualizar_visualizacion_lista_procesos()

            self.entry_nombre.delete(0, tk.END)
            self.entry_tiempo_cpu.delete(0, tk.END)
            self.entry_instante_llegada.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos.")

    def actualizar_visualizacion_lista_procesos(self):
        self.lista_procesos_cola.delete(0, tk.END)
        for proceso in self.simulador.cola_llegadas:
            self.lista_procesos_cola.insert(tk.END, f"PID: {proceso.pid} - Nombre: {proceso.nombre} - CPU: {proceso.tiempo_cpu_total} - Llegada: {proceso.instante_llegada}")
    
    def iniciar_simulacion(self):
        if not self.simulador.cola_llegadas:
            messagebox.showwarning("Advertencia", "Añade al menos un proceso.")
            return

        if self.animation_id:
            self.master.after_cancel(self.animation_id)

        algoritmo = self.algoritmo_var.get()
        
        # Ejecución del algoritmo
        if algoritmo == "FCFS":
            self.simulador.ejecutar_fcfs()
        elif algoritmo == "SJF":
            self.simulador.ejecutar_sjf()
        elif algoritmo == "SRTF":
            self.simulador.ejecutar_srtf()
        elif algoritmo == "Round Robin":
            quantum_valor = self.quantum.get()
            if quantum_valor <= 0:
                messagebox.showwarning("Advertencia", "El quantum debe ser positivo.")
                return
            self.simulador.ejecutar_round_robin(quantum_valor)
        
        # Post-simulación
        self.asignar_colores_procesos()
        self.actualizar_tabla_metricas()
        self.actualizar_metricas_ui()
        
        # MODIFICACIÓN CLAVE 2: Llamar a la nueva función para dibujar el Gantt de CPU
        self.dibujar_gantt_cpu() 
        
        # Reiniciar y empezar la visualización del Gantt por proceso
        self.instante_actual_animacion = 0
        self.historial_visual_keys = sorted(list(self.simulador.historial_ejecucion_visual.keys()))
        self.dibujar_gantt_estatico()
        self.iniciar_animacion_gantt()
        
    def asignar_colores_procesos(self):
        nombres_procesos = set(self.simulador.historial_ejecucion_visual.values())
        
        if "Inactivo" in nombres_procesos:
            self.colores_procesos["Inactivo"] = "#D3D3D3" # Gris claro
            nombres_procesos.remove("Inactivo")
        
        for nombre in sorted(list(nombres_procesos)):
            if nombre not in self.colores_procesos:
                self.colores_procesos[nombre] = self.generar_color_aleatorio()

    # =================================================================
    # DIBUJO DEL GANTT EN CUADRÍCULA (SIN CAMBIOS)
    # =================================================================
    def dibujar_gantt_estatico(self):
        self.ax_gantt.clear()
        algoritmo = self.algoritmo_var.get()
        self.ax_gantt.set_title(f'Diagrama de Gantt - {algoritmo}')
        self.ax_gantt.set_xlabel('Tiempo')
        
        tiempos = sorted(self.simulador.historial_ejecucion_visual.keys())
        if not tiempos:
            self.fig.canvas.draw()
            return

        fin_total = max(tiempos) + 1 if tiempos else 0
        
        nombres_procesos_ejecutados = sorted(list(set(p.nombre for p in self.simulador.historial_ejecucion)))
        
        y_pos = {nombre: i for i, nombre in enumerate(nombres_procesos_ejecutados)}
        
        if not nombres_procesos_ejecutados:
            self.fig.canvas.draw()
            return

        segmentos = []
        if tiempos:
            inicio_segmento = tiempos[0]
            proceso_anterior = self.simulador.historial_ejecucion_visual.get(inicio_segmento)
            
            for i in range(1, len(tiempos)):
                tiempo_actual_iteracion = tiempos[i]
                proceso_actual_iteracion = self.simulador.historial_ejecucion_visual.get(tiempo_actual_iteracion)
                
                if proceso_actual_iteracion != proceso_anterior:
                    segmentos.append({
                        'proceso': proceso_anterior,
                        'inicio': inicio_segmento,
                        'fin': tiempo_actual_iteracion
                    })
                    inicio_segmento = tiempo_actual_iteracion
                    proceso_anterior = proceso_actual_iteracion
            
            segmentos.append({
                'proceso': proceso_anterior,
                'inicio': inicio_segmento,
                'fin': fin_total
            })

        for seg in segmentos:
            nombre = seg['proceso']
            inicio = seg['inicio']
            fin = seg['fin']
            
            if nombre != "Inactivo" and nombre in y_pos:
                y_coord = y_pos[nombre]
                
                self.ax_gantt.barh(y_coord, fin - inicio, left=inicio, height=0.7, 
                                    color=self.colores_procesos.get(nombre, 'gray'), edgecolor='none', zorder=3)
                                    
                for t_step in range(inicio, fin):
                    if self.simulador.historial_ejecucion_visual.get(t_step) == nombre:
                        simbolo = 'X' 
                        self.ax_gantt.text(t_step + 0.5, y_coord, simbolo,
                                        ha='center', va='center', color='white', fontsize=8, zorder=4)

        self.ax_gantt.set_yticks(list(y_pos.values()))
        self.ax_gantt.set_yticklabels(nombres_procesos_ejecutados)
        self.ax_gantt.set_ylim(-0.5, len(nombres_procesos_ejecutados) - 0.5) 
        self.ax_gantt.invert_yaxis() 

        self.ax_gantt.set_xlim(0, fin_total)
        self.ax_gantt.set_xticks(np.arange(0, fin_total + 1, 1))
        
        self.ax_gantt.grid(False) 
        
        for x_val in np.arange(0, fin_total + 1, 1):
            self.ax_gantt.axvline(x=x_val, color='gray', linestyle='-', linewidth=0.5, zorder=1)
        
        for y_val in np.arange(-0.5, len(nombres_procesos_ejecutados), 1):
            self.ax_gantt.axhline(y=y_val, color='gray', linestyle='-', linewidth=0.5, zorder=1)

        self.fig.canvas.draw()
        
    def iniciar_animacion_gantt(self):
        # Esta función solo actualizará la línea de tiempo sobre el Gantt estático (el de cuadrícula)
        if not self.historial_visual_keys or self.instante_actual_animacion > max(self.historial_visual_keys, default=0):
            self.ax_gantt.lines = [l for l in self.ax_gantt.lines if not l.get_color() == 'red']
            self.ax_gantt.texts = [t for t in self.ax_gantt.texts if not t.get_color() == 'red']
            self.fig.canvas.draw()
            return

        tiempo_actual_en_simulacion = self.historial_visual_keys[self.instante_actual_animacion]
        
        self.ax_gantt.lines = [l for l in self.ax_gantt.lines if not (l.get_color() == 'red' and l.get_linestyle() == '--')] 
        self.ax_gantt.axvline(x=tiempo_actual_en_simulacion, color='red', linestyle='--', linewidth=1.5, zorder=5) 

        self.ax_gantt.texts = [t for t in self.ax_gantt.texts if not t.get_color() == 'red'] 
        self.ax_gantt.text(tiempo_actual_en_simulacion, -1.0, f't={tiempo_actual_en_simulacion}', 
                            ha='center', va='bottom', fontsize=8, color='red', zorder=5)
        
        self.fig.canvas.draw()
        
        self.instante_actual_animacion += 1
        self.animation_id = self.master.after(500, self.iniciar_animacion_gantt) 
        
    def actualizar_metricas_ui(self):
        promedio_retorno, promedio_espera, promedio_indice_servicio = self.simulador.calcular_metricas()
            
        self.label_tiempo_retorno_promedio.config(text=f"Tiempo de Retorno Promedio: {promedio_retorno:.2f}")
        self.label_tiempo_espera_promedio.config(text=f"Tiempo de Espera Promedio: {promedio_espera:.2f}")
        self.label_indice_servicio_promedio.config(text=f"Índice de Servicio Promedio: {promedio_indice_servicio:.2f}")

    # =================================================================
    # NUEVA FUNCIÓN: Dibuja el Gantt de la CPU (similar a la Imagen 2)
    # =================================================================
    def dibujar_gantt_cpu(self):
        self.ax_gantt_cpu.clear()
        algoritmo = self.algoritmo_var.get()
        self.ax_gantt_cpu.set_title('Diagrama de Gantt de la CPU')
        self.ax_gantt_cpu.set_xlabel('Tiempo')
        self.ax_gantt_cpu.set_ylabel('CPU')
        
        tiempos = sorted(self.simulador.historial_ejecucion_visual.keys())
        if not tiempos:
            self.fig.canvas.draw()
            return

        fin_total = max(tiempos) + 1 if tiempos else 0
        
        # Preparar segmentos para el Gantt de CPU
        segmentos_cpu = []
        if tiempos:
            inicio_segmento = tiempos[0]
            proceso_actual_en_cpu = self.simulador.historial_ejecucion_visual.get(inicio_segmento)
            
            for i in range(1, len(tiempos)):
                tiempo_actual_iteracion = tiempos[i]
                siguiente_proceso_en_cpu = self.simulador.historial_ejecucion_visual.get(tiempo_actual_iteracion)
                
                if siguiente_proceso_en_cpu != proceso_actual_en_cpu:
                    segmentos_cpu.append({
                        'proceso': proceso_actual_en_cpu,
                        'inicio': inicio_segmento,
                        'fin': tiempo_actual_iteracion
                    })
                    inicio_segmento = tiempo_actual_iteracion
                    proceso_actual_en_cpu = siguiente_proceso_en_cpu
            
            segmentos_cpu.append({
                'proceso': proceso_actual_en_cpu,
                'inicio': inicio_segmento,
                'fin': fin_total
            })

        # Dibujar los segmentos en una sola línea para la CPU
        y_cpu = 0.5 # Posición fija para la línea de la CPU
        for seg in segmentos_cpu:
            nombre_proceso = seg['proceso']
            inicio = seg['inicio']
            fin = seg['fin']
            
            color = self.colores_procesos.get(nombre_proceso, 'gray')
            if nombre_proceso == "Inactivo":
                color = self.colores_procesos.get("Inactivo", '#D3D3D3') # Color específico para inactivo

            self.ax_gantt_cpu.barh(y_cpu, fin - inicio, left=inicio, height=0.7, 
                                    color=color, edgecolor='black', linewidth=0.5)
            
            # Añadir la etiqueta del proceso en el centro del segmento
            if nombre_proceso != "Inactivo":
                self.ax_gantt_cpu.text(inicio + (fin - inicio) / 2, y_cpu, nombre_proceso,
                                        ha='center', va='center', color='white', fontsize=9, fontweight='bold')

        # Configuración del eje Y para la CPU
        self.ax_gantt_cpu.set_yticks([y_cpu])
        self.ax_gantt_cpu.set_yticklabels(['CPU'])
        self.ax_gantt_cpu.set_ylim(0, 1) # Para centrar la barra 'CPU'
        
        # Configuración del eje X para el tiempo
        self.ax_gantt_cpu.set_xlim(0, fin_total)
        self.ax_gantt_cpu.set_xticks(np.arange(0, fin_total + 1, 1))
        
        # Añadir líneas de cuadrícula para cada unidad de tiempo
        self.ax_gantt_cpu.grid(axis='x', linestyle='--', alpha=0.7)
        
        self.fig.canvas.draw()
        
    def actualizar_tabla_metricas(self):
        for item in self.treeview_metricas_por_proceso.get_children():
            self.treeview_metricas_por_proceso.delete(item)

        self.simulador.calcular_metricas()
        
        self.lista_procesos_historial.delete(0, tk.END)
        
        for proceso in self.simulador.historial_ejecucion:
            self.treeview_metricas_por_proceso.insert('', tk.END, values=(
                proceso.nombre,
                proceso.instante_llegada,
                proceso.tiempo_cpu_total,
                proceso.tiempo_finalizacion,
                proceso.tiempo_retorno,
                proceso.tiempo_espera,
                f"{proceso.indice_servicio:.2f}"
            ))
            self.lista_procesos_historial.insert(tk.END, f"PID: {proceso.pid} - Nombre: {proceso.nombre} - Tiempo Final: {proceso.tiempo_finalizacion}")

    def crear_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        main_frame.grid_columnconfigure(0, weight=0) 
        main_frame.grid_columnconfigure(1, weight=1) 

        # --- Fila 0: Creación de Procesos ---
        frame_crear_proceso = ttk.LabelFrame(main_frame, text="Añadir Nuevo Proceso", padding="10")
        frame_crear_proceso.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        frame_crear_proceso.grid_columnconfigure(1, weight=1)
        frame_crear_proceso.grid_columnconfigure(3, weight=1)
        frame_crear_proceso.grid_columnconfigure(5, weight=1)

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
        
        # --- Fila 1: Configuración de Simulación ---
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
        
        # --- Fila 2: Listas y Gráficas ---
        main_frame.grid_rowconfigure(2, weight=1) 

        frame_listas = ttk.Frame(main_frame)
        frame_listas.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        frame_listas.grid_rowconfigure(1, weight=1) 
        frame_listas.grid_rowconfigure(3, weight=1) 

        ttk.Label(frame_listas, text="Cola de Procesos Listos").grid(row=0, column=0, pady=2, sticky="ew")
        self.lista_procesos_cola = tk.Listbox(frame_listas, height=10, width=50) 
        self.lista_procesos_cola.grid(row=1, column=0, sticky="nsew", padx=5, pady=2) 
        
        ttk.Label(frame_listas, text="Historial de Procesos Ejecutados").grid(row=2, column=0, pady=2, sticky="ew")
        self.lista_procesos_historial = tk.Listbox(frame_listas, height=10) 
        self.lista_procesos_historial.grid(row=3, column=0, sticky="nsew", padx=5, pady=2)
        
        frame_metricas_y_gantt = ttk.Frame(main_frame)
        frame_metricas_y_gantt.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
        
        frame_metricas_y_gantt.grid_rowconfigure(0, weight=0) 
        frame_metricas_y_gantt.grid_rowconfigure(1, weight=0) 
        frame_metricas_y_gantt.grid_rowconfigure(2, weight=0) 
        frame_metricas_y_gantt.grid_rowconfigure(3, weight=0) 
        frame_metricas_y_gantt.grid_rowconfigure(4, weight=1) # El canvas del Gantt por Proceso
        
        ttk.Label(frame_metricas_y_gantt, text="Métricas de Rendimiento", font=('Arial', 10, 'bold')).grid(row=0, column=0, pady=(5,2), sticky="w")
        
        self.label_tiempo_retorno_promedio = ttk.Label(frame_metricas_y_gantt, text="Tiempo de Retorno Promedio: 0.00")
        self.label_tiempo_retorno_promedio.grid(row=1, column=0, pady=1, sticky="w")
        
        self.label_tiempo_espera_promedio = ttk.Label(frame_metricas_y_gantt, text="Tiempo de Espera Promedio: 0.00")
        self.label_tiempo_espera_promedio.grid(row=2, column=0, pady=1, sticky="w")

        self.label_indice_servicio_promedio = ttk.Label(frame_metricas_y_gantt, text="Índice de Servicio Promedio: 0.00")
        self.label_indice_servicio_promedio.grid(row=3, column=0, pady=1, sticky="w")
        
        self.canvas_gantt = FigureCanvasTkAgg(self.fig, master=frame_metricas_y_gantt)
        self.canvas_gantt_widget = self.canvas_gantt.get_tk_widget()
        # El canvas de Matplotlib ahora tiene ambos subplots
        self.canvas_gantt_widget.grid(row=4, column=0, sticky="nsew")


        # --- Fila 3: Tabla de Métricas por Proceso (Cuadrícula) ---
        frame_tabla_detallada = ttk.LabelFrame(main_frame, text="Métricas por Proceso (Procedimiento en Cuadrícula)", padding="10")
        frame_tabla_detallada.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        columnas = ("proceso", "llegada", "cpu", "finalizacion", "retorno", "espera", "servicio")
        
        self.treeview_metricas_por_proceso = ttk.Treeview(frame_tabla_detallada, columns=columnas, show='headings', height=6)
        
        self.treeview_metricas_por_proceso.heading("proceso", text="Proceso")
        self.treeview_metricas_por_proceso.heading("llegada", text="Instante de llegada ($T_l$)")
        self.treeview_metricas_por_proceso.heading("cpu", text="Tiempo en CPU ($T_{CPU}$)")
        self.treeview_metricas_por_proceso.heading("finalizacion", text="Instante de finalización ($T_f$)")
        self.treeview_metricas_por_proceso.heading("retorno", text="Tiempo de retorno ($T_r = T_f - T_l$)")
        self.treeview_metricas_por_proceso.heading("espera", text="Tiempo de espera ($T_e$)")
        self.treeview_metricas_por_proceso.heading("servicio", text="Índice de servicio ($I = T_{CPU}/T_r$)")

        self.treeview_metricas_por_proceso.column("proceso", width=60, anchor='center')
        self.treeview_metricas_por_proceso.column("llegada", width=120, anchor='center')
        self.treeview_metricas_por_proceso.column("cpu", width=120, anchor='center')
        self.treeview_metricas_por_proceso.column("finalizacion", width=150, anchor='center')
        self.treeview_metricas_por_proceso.column("retorno", width=150, anchor='center')
        self.treeview_metricas_por_proceso.column("espera", width=120, anchor='center')
        self.treeview_metricas_por_proceso.column("servicio", width=150, anchor='center')
        
        self.treeview_metricas_por_proceso.pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorApp(root)
    root.mainloop()