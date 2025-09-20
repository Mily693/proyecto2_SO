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
    def ejecutar_fcfs(self):
        tiempo_actual = 0
        cola_listos = sorted(self.cola_llegadas, key=lambda p: p.instante_llegada)
        
        while cola_listos:
            proceso_actual = cola_listos.pop(0)

            if tiempo_actual < proceso_actual.instante_llegada:
                self.historial_ejecucion_visual.update({i: "Inactivo" for i in range(tiempo_actual, proceso_actual.instante_llegada)})
                tiempo_actual = proceso_actual.instante_llegada

            proceso_actual.tiempo_inicio_ejecucion = tiempo_actual
            tiempo_actual += proceso_actual.tiempo_cpu
            proceso_actual.tiempo_finalizacion = tiempo_actual
            
            proceso_actual.tiempo_retorno = proceso_actual.tiempo_finalizacion - proceso_actual.instante_llegada
            proceso_actual.tiempo_espera = proceso_actual.tiempo_retorno - proceso_actual.tiempo_cpu
            
            self.historial_ejecucion.append(proceso_actual)
            self.historial_ejecucion_visual.update({i: proceso_actual.nombre for i in range(proceso_actual.tiempo_inicio_ejecucion, proceso_actual.tiempo_finalizacion)})



    def ejecutar_sjf(self):
        tiempo_actual = 0
        procesos_pendientes = sorted(self.cola_llegadas, key=lambda p: p.instante_llegada)
        cola_listos = []
        
        while procesos_pendientes or cola_listos:
            while procesos_pendientes and procesos_pendientes[0].instante_llegada <= tiempo_actual:
                cola_listos.append(procesos_pendientes.pop(0))
            
            if cola_listos:
                cola_listos.sort(key=lambda p: p.tiempo_cpu)
                proceso_ejecutandose = cola_listos.pop(0)

                if tiempo_actual < proceso_ejecutandose.instante_llegada:
                    self.historial_ejecucion_visual.update({i: "Inactivo" for i in range(tiempo_actual, proceso_ejecutandose.instante_llegada)})
                    tiempo_actual = proceso_ejecutandose.instante_llegada

                proceso_ejecutandose.tiempo_inicio_ejecucion = tiempo_actual
                tiempo_actual += proceso_ejecutandose.tiempo_cpu
                proceso_ejecutandose.tiempo_finalizacion = tiempo_actual
                
                proceso_ejecutandose.tiempo_retorno = proceso_ejecutandose.tiempo_finalizacion - proceso_ejecutandose.instante_llegada
                proceso_ejecutandose.tiempo_espera = proceso_ejecutandose.tiempo_retorno - proceso_ejecutandose.tiempo_cpu

                self.historial_ejecucion.append(proceso_ejecutandose)
                self.historial_ejecucion_visual.update({i: proceso_ejecutandose.nombre for i in range(proceso_ejecutandose.tiempo_inicio_ejecucion, proceso_ejecutandose.tiempo_finalizacion)})
            else:
                tiempo_actual += 1
                self.historial_ejecucion_visual.update({tiempo_actual - 1: "Inactivo"})

    def ejecutar_srtf(self):
        tiempo_actual = 0
        procesos_pendientes = sorted(self.cola_llegadas, key=lambda p: p.instante_llegada)
        cola_listos = []
        proceso_ejecutandose = None

        while procesos_pendientes or cola_listos or proceso_ejecutandose:
            while procesos_pendientes and procesos_pendientes[0].instante_llegada <= tiempo_actual:
                cola_listos.append(procesos_pendientes.pop(0))
            
            cola_listos.sort(key=lambda p: p.tiempo_restante)
            
            proximo_proceso = cola_listos[0] if cola_listos else None
            
            if proceso_ejecutandose is None or (proximo_proceso and proximo_proceso.tiempo_restante < proceso_ejecutandose.tiempo_restante):
                if proceso_ejecutandose:
                    cola_listos.append(proceso_ejecutandose)
                    cola_listos.sort(key=lambda p: p.tiempo_restante)
                
                if cola_listos:
                    proceso_ejecutandose = cola_listos.pop(0)
                else:
                    proceso_ejecutandose = None

            if proceso_ejecutandose:
                self.historial_ejecucion_visual[tiempo_actual] = proceso_ejecutandose.nombre
                proceso_ejecutandose.tiempo_restante -= 1
                
                if proceso_ejecutandose.tiempo_restante == 0:
                    proceso_ejecutandose.tiempo_finalizacion = tiempo_actual + 1
                    proceso_ejecutandose.tiempo_retorno = proceso_ejecutandose.tiempo_finalizacion - proceso_ejecutandose.instante_llegada
                    proceso_ejecutandose.tiempo_espera = proceso_ejecutandose.tiempo_retorno - proceso_ejecutandose.tiempo_cpu
                    self.historial_ejecucion.append(proceso_ejecutandose)
                    proceso_ejecutandose = None
            else:
                self.historial_ejecucion_visual[tiempo_actual] = "Inactivo"

            tiempo_actual += 1

    def ejecutar_round_robin(self, quantum):
        tiempo_actual = 0
        procesos_pendientes = sorted(self.cola_llegadas, key=lambda p: p.instante_llegada)
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

            for _ in range(tiempo_ejecucion):
                self.historial_ejecucion_visual[tiempo_actual] = proceso_actual.nombre
                tiempo_actual += 1
                proceso_actual.tiempo_restante -= 1

            if proceso_actual.tiempo_restante == 0:
                proceso_actual.tiempo_finalizacion = tiempo_actual
                proceso_actual.tiempo_retorno = proceso_actual.tiempo_finalizacion - proceso_actual.instante_llegada
                proceso_actual.tiempo_espera = proceso_actual.tiempo_retorno - proceso_actual.tiempo_cpu
                self.historial_ejecucion.append(proceso_actual)
            else:
                cola_rr.append(proceso_actual)
                