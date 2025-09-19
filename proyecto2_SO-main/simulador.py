import sys
import math

class Proceso:
    """Clase para representar un proceso en el simulador del sistema operativo."""

    siguiente_pid = 1

    def __init__(self, nombre, tiempo_cpu, instante_llegada):
        self.pid = Proceso.siguiente_pid
        Proceso.siguiente_pid += 1

        self.nombre = nombre
        self.tiempo_cpu = tiempo_cpu
        self.instante_llegada = instante_llegada
        self.tiempo_restante = tiempo_cpu
        self.estado = "Listo"
        self.tiempo_inicio_ejecucion = -1
        self.tiempo_finalizacion = -1
        self.tiempo_espera = -1
        self.tiempo_retorno = -1
        self.instante_salida_cola = -1
        self.quantum_tiempo_inicio = -1

class Simulador:
    """Clase principal del simulador de planificación de procesos."""

    def __init__(self):
        self.cola_llegadas = []
        self.historial_ejecucion = []
        self.historial_ejecucion_visual = {}

    def agregar_proceso(self, nombre, tiempo_cpu, instante_llegada):
        proceso = Proceso(nombre, tiempo_cpu, instante_llegada)
        self.cola_llegadas.append(proceso)

    def calcular_metricas(self):
        total_tiempo_retorno = sum(p.tiempo_retorno for p in self.historial_ejecucion)
        total_tiempo_espera = sum(p.tiempo_espera for p in self.historial_ejecucion)

        num_procesos = len(self.historial_ejecucion)
        
        promedio_retorno = total_tiempo_retorno / num_procesos if num_procesos > 0 else 0
        promedio_espera = total_tiempo_espera / num_procesos if num_procesos > 0 else 0

        return promedio_retorno, promedio_espera
    
    

