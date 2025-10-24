# simulador.py
import math
# Asume que la clase Proceso está en el archivo proceso.py
from proceso import Proceso 

class Simulador:
    """Clase principal del simulador de planificación de procesos."""

    def __init__(self):
        self.cola_llegadas = []
        self.historial_ejecucion = []
        self.historial_ejecucion_visual = {} # {tiempo: nombre_proceso}

    def agregar_proceso(self, nombre, tiempo_cpu, instante_llegada):
        # NOTA: Al agregar un proceso, la clase Proceso maneja la asignación de PID.
        proceso = Proceso(nombre, tiempo_cpu, instante_llegada)
        self.cola_llegadas.append(proceso)

    def _reset_simulacion(self):
        """Prepara el simulador para una nueva ejecución, clonando los procesos y reiniciando el estado."""
        self.historial_ejecucion = []
        self.historial_ejecucion_visual = {}
        
        # Clonar procesos para que los originales en cola_llegadas no se alteren
        procesos_clonados = []
        Proceso.siguiente_pid = 1 # Resetear el contador de PID antes de clonar
        for p in self.cola_llegadas:
            # Crea una nueva instancia de Proceso con los datos originales
            proceso_clon = Proceso(p.nombre, p.tiempo_cpu_total, p.instante_llegada)
            procesos_clonados.append(proceso_clon)
            
        # Ordenar los procesos por llegada para la simulación
        procesos_clonados.sort(key=lambda p: p.instante_llegada)
        return procesos_clonados
    
    # [MODIFICACIÓN CLAVE]: Devuelve los 3 promedios, incluyendo el Índice de Servicio.
    def calcular_metricas(self):
        """Calcula las métricas promedio a partir de los procesos terminados, incluyendo el índice de servicio."""
        
        for p in self.historial_ejecucion:
            p.calcular_metricas() # Aseguramos que el índice individual esté calculado
             
        total_tiempo_retorno = sum(p.tiempo_retorno for p in self.historial_ejecucion)
        total_tiempo_espera = sum(p.tiempo_espera for p in self.historial_ejecucion)
        total_indice_servicio = sum(p.indice_servicio for p in self.historial_ejecucion)
        
        num_procesos = len(self.historial_ejecucion)
        
        promedio_retorno = total_tiempo_retorno / num_procesos if num_procesos > 0 else 0
        promedio_espera = total_tiempo_espera / num_procesos if num_procesos > 0 else 0
        promedio_indice_servicio = total_indice_servicio / num_procesos if num_procesos > 0 else 0
        
        # [CORREGIDO] Retorna los 3 valores: Retorno, Espera, Índice de Servicio
        return promedio_retorno, promedio_espera, promedio_indice_servicio

    # ------------------ ALGORITMOS NO PREVENTIVOS (FCFS, SJF) ------------------

    def ejecutar_fcfs(self):
        procesos_para_simular = self._reset_simulacion()
        tiempo_actual = 0
        
        cola_listos = procesos_para_simular 
        
        while cola_listos:
            proceso_actual = cola_listos.pop(0)

            if tiempo_actual < proceso_actual.instante_llegada:
                self.historial_ejecucion_visual.update({i: "Inactivo" for i in range(tiempo_actual, proceso_actual.instante_llegada)})
                tiempo_actual = proceso_actual.instante_llegada

            proceso_actual.tiempo_inicio_ejecucion = tiempo_actual
            inicio_ejecucion = tiempo_actual
            tiempo_actual += proceso_actual.tiempo_cpu_total # Uso de tiempo_cpu_total
            
            proceso_actual.tiempo_finalizacion = tiempo_actual
            proceso_actual.calcular_metricas() 
            
            self.historial_ejecucion.append(proceso_actual)
            self.historial_ejecucion_visual.update({i: proceso_actual.nombre for i in range(inicio_ejecucion, proceso_actual.tiempo_finalizacion)})

    def ejecutar_sjf(self):
        procesos_para_simular = self._reset_simulacion()
        tiempo_actual = 0
        procesos_pendientes = procesos_para_simular
        cola_listos = []
        
        while procesos_pendientes or cola_listos:
            while procesos_pendientes and procesos_pendientes[0].instante_llegada <= tiempo_actual:
                cola_listos.append(procesos_pendientes.pop(0))
                
            if cola_listos:
                # SJF ordena por tiempo_cpu_total
                cola_listos.sort(key=lambda p: (p.tiempo_cpu_total, p.instante_llegada))
                proceso_ejecutandose = cola_listos.pop(0)

                if tiempo_actual < proceso_ejecutandose.instante_llegada:
                    self.historial_ejecucion_visual.update({i: "Inactivo" for i in range(tiempo_actual, proceso_ejecutandose.instante_llegada)})
                    tiempo_actual = proceso_ejecutandose.instante_llegada

                proceso_ejecutandose.tiempo_inicio_ejecucion = tiempo_actual
                inicio_ejecucion = tiempo_actual
                tiempo_actual += proceso_ejecutandose.tiempo_cpu_total # Uso de tiempo_cpu_total
                
                proceso_ejecutandose.tiempo_finalizacion = tiempo_actual
                proceso_ejecutandose.calcular_metricas()

                self.historial_ejecucion.append(proceso_ejecutandose)
                self.historial_ejecucion_visual.update({i: proceso_ejecutandose.nombre for i in range(inicio_ejecucion, proceso_ejecutandose.tiempo_finalizacion)})
            else:
                if procesos_pendientes:
                    tiempo_siguiente_llegada = procesos_pendientes[0].instante_llegada
                    self.historial_ejecucion_visual.update({i: "Inactivo" for i in range(tiempo_actual, tiempo_siguiente_llegada)})
                    tiempo_actual = tiempo_siguiente_llegada
                else:
                    break

    # ------------------ ALGORITMOS PREVENTIVOS (SRTF, Round Robin) ------------------
    
    def ejecutar_srtf(self):
        procesos_para_simular = self._reset_simulacion()
        tiempo_actual = 0
        procesos_pendientes = procesos_para_simular
        cola_listos = []
        proceso_ejecutandose = None

        while procesos_pendientes or cola_listos or proceso_ejecutandose:
            while procesos_pendientes and procesos_pendientes[0].instante_llegada <= tiempo_actual:
                cola_listos.append(procesos_pendientes.pop(0))
            
            if proceso_ejecutandose and proceso_ejecutandose.tiempo_restante > 0:
                cola_listos.append(proceso_ejecutandose)
                
            proximo_proceso_elegido = None
            if cola_listos:
                cola_listos.sort(key=lambda p: (p.tiempo_restante, p.instante_llegada))
                proximo_proceso_elegido = cola_listos.pop(0)

            proceso_ejecutandose = proximo_proceso_elegido
            
            if proceso_ejecutandose is None:
                if procesos_pendientes:
                    tiempo_siguiente_llegada = procesos_pendientes[0].instante_llegada
                    self.historial_ejecucion_visual.update({i: "Inactivo" for i in range(tiempo_actual, tiempo_siguiente_llegada)})
                    tiempo_actual = tiempo_siguiente_llegada
                    continue
                else:
                    break
            
            if proceso_ejecutandose.tiempo_inicio_ejecucion == -1:
                proceso_ejecutandose.tiempo_inicio_ejecucion = tiempo_actual 

            self.historial_ejecucion_visual[tiempo_actual] = proceso_ejecutandose.nombre
            proceso_ejecutandose.tiempo_restante -= 1
            
            if proceso_ejecutandose.tiempo_restante == 0:
                proceso_ejecutandose.tiempo_finalizacion = tiempo_actual + 1
                proceso_ejecutandose.calcular_metricas()
                self.historial_ejecucion.append(proceso_ejecutandose)
                proceso_ejecutandose = None
            
            tiempo_actual += 1


    def ejecutar_round_robin(self, quantum):
        procesos_para_simular = self._reset_simulacion()
        tiempo_actual = 0
        procesos_pendientes = procesos_para_simular
        cola_rr = []

        while procesos_pendientes or cola_rr:
            while procesos_pendientes and procesos_pendientes[0].instante_llegada <= tiempo_actual:
                cola_rr.append(procesos_pendientes.pop(0))
            
            if not cola_rr:
                if procesos_pendientes:
                    tiempo_siguiente_llegada = procesos_pendientes[0].instante_llegada
                    self.historial_ejecucion_visual.update({i: "Inactivo" for i in range(tiempo_actual, tiempo_siguiente_llegada)})
                    tiempo_actual = tiempo_siguiente_llegada
                    continue
                else:
                    break

            proceso_actual = cola_rr.pop(0)
            tiempo_ejecucion = min(proceso_actual.tiempo_restante, quantum)

            if proceso_actual.tiempo_inicio_ejecucion == -1:
                proceso_actual.tiempo_inicio_ejecucion = tiempo_actual
            
            for _ in range(tiempo_ejecucion):
                self.historial_ejecucion_visual[tiempo_actual] = proceso_actual.nombre
                tiempo_actual += 1
                proceso_actual.tiempo_restante -= 1
                
                while procesos_pendientes and procesos_pendientes[0].instante_llegada == tiempo_actual:
                    cola_rr.append(procesos_pendientes.pop(0))

            if proceso_actual.tiempo_restante == 0:
                proceso_actual.tiempo_finalizacion = tiempo_actual
                proceso_actual.calcular_metricas()
                self.historial_ejecucion.append(proceso_actual)
            else:
                cola_rr.append(proceso_actual)