# proceso.py
import math

class Proceso:
    siguiente_pid = 1
    
    def __init__(self, nombre, tiempo_cpu, instante_llegada):
        self.pid = Proceso.siguiente_pid
        Proceso.siguiente_pid += 1
        self.nombre = nombre
        self.tiempo_cpu_total = tiempo_cpu       # Tiempo de CPU original requerido (T_CPU)
        self.instante_llegada = instante_llegada # Instante de llegada (T_l)
        self.tiempo_restante = tiempo_cpu        # Tiempo de CPU restante para la simulación
        
        self.tiempo_inicio_ejecucion = -1
        self.tiempo_finalizacion = -1            # Instante de finalización (T_f)
        
        self.tiempo_retorno = 0                  # Tiempo de retorno (T_r)
        self.tiempo_espera = 0                   # Tiempo de espera (T_e)
        self.indice_servicio = 0.0               # Índice de servicio (I)

    def calcular_metricas(self):
        """Calcula el tiempo de retorno, espera e índice de servicio una vez finalizado el proceso."""
        
        if self.tiempo_finalizacion > -1:
            # T_r = T_f - T_l
            self.tiempo_retorno = self.tiempo_finalizacion - self.instante_llegada
            
            # T_e = T_r - T_CPU
            self.tiempo_espera = self.tiempo_retorno - self.tiempo_cpu_total
            if self.tiempo_espera < 0: # Para evitar errores de redondeo o lógica, aunque no debería ser negativo
                self.tiempo_espera = 0
            
            # I = T_CPU / T_r
            if self.tiempo_retorno > 0: 
                self.indice_servicio = self.tiempo_cpu_total / self.tiempo_retorno
            else:
                self.indice_servicio = 0.0

# Restablecer el contador de PID después de la definición, listo para ser importado
Proceso.siguiente_pid = 1