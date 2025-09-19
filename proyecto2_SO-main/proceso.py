# Definición de la clase Proceso
class Proceso:
    """
    Esta clase representa un proceso en el simulador del sistema operativo.
    Contiene todos los atributos necesarios para la gestión y planificación.
    """

    # Variable de clase para generar automáticamente el PID
    siguiente_pid = 1

    def __init__(self, nombre, tiempo_cpu, instante_llegada):
        """
        Constructor de la clase Proceso.

        Args:
            nombre (str): Nombre descriptivo del proceso.
            tiempo_cpu (int): El tiempo total de CPU que el proceso necesita para completarse.
            instante_llegada (int): La unidad de tiempo en la que el proceso ingresa al sistema.
        """
        # Generación automática del PID. Se asigna el valor actual de siguiente_pid y se incrementa para el próximo proceso.
        self.pid = Proceso.siguiente_pid
        Proceso.siguiente_pid += 1

        # Atributos del proceso
        self.nombre = nombre
        self.tiempo_cpu = tiempo_cpu  # Tiempo total de ejecución (inicial)
        self.tiempo_restante = tiempo_cpu  # Tiempo de ejecución restante, se actualiza durante la simulación
        self.instante_llegada = instante_llegada  # Momento en que el proceso llega a la cola de listos
        self.estado = 'listo'  # Estado inicial del proceso: 'listo', 'ejecutándose', 'terminado'
        self.quantum_tiempo = 0  # Atributo para el quantum de tiempo (específico para Round Robin)
        self.tiempo_inicio_ejecucion = -1 # Guarda el momento en que el proceso se ejecuta por primera vez
        self.tiempo_terminacion = -1 # Guarda el momento en que el proceso finaliza su ejecución