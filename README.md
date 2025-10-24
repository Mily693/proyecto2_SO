# Simulador de Planificación de Procesos

Este proyecto es una herramienta de simulación con una interfaz gráfica (GUI) para visualizar y comparar el rendimiento de diferentes algoritmos de planificación de procesos en sistemas operativos. Implementa distintos algoritmos de planificación de CPU, tanto expropiativos como no expropiativos. El objetivo es simular cómo un sistema operativo gestiona la cola de procesos y asigna la CPU según la política de planificación seleccionada.

## Características
- **Gestión de Procesos:**
  Cada proceso incluye:
  - **PID:** Identificador numérico único generado automáticamente.
  - **Nombre:** Nombre del proceso.
  - **Tiempo en CPU:** Cantidad de unidades de tiempo necesarias para ejecutarse.
  - **Instante de llegada:** Momento en que el proceso entra al sistema.
  - **Quantum de tiempo:** Tiempo asignado para el algoritmo Round Robin.


- **Algoritmos de Planificación:**
    - **FCFS** (First Come, First Served) – No expropiativo.
    - **SJF** (Shortest Job First) – No expropiativo.
    - **SRTF** (Shortest Remaining Time First) – Expropiativo.
    - **Round Robin** – Expropiativo, con quantum configurable.

- **Métricas de Rendimiento:**
    - Tiempo de Retorno Promedio
    - Tiempo de Espera Promedio

- **Simulación en Tiempo Discreto:**
  - Una CPU disponible para ejecutar procesos.
  - Cada unidad de tiempo equivale a 5 segundos reales.

- **Interfaz de Usuario:**
  - Permite agregar procesos antes de iniciar la simulación.
  - Botón para iniciar simulación según el algoritmo seleccionado.
  - Visualización de la cola de procesos y el historial de ejecución.

- **Visualización:**
    - Diagrama de Gantt animado que muestra la ejecución de los procesos en la CPU.
    - Marcadores visuales para el instante de llegada y el tiempo de finalización de cada proceso.
    - Histograma comparativo de los tiempos de espera entre los algoritmos.

## Requisitos

- Para ejecutar este proyecto, necesitas tener Python instalado. 
- Adicionalmente, debes instalar la librería `matplotlib`.

## Estructura del Proyecto

  - **main.py:** Contiene la interfaz gráfica de usuario (GUI) y la lógica principal de la aplicación.

  - **simulador.py:** Contiene la lógica de los algoritmos de planificación y el cálculo de las métricas.

  - **proceso.py:** Define la clase Proceso utilizada para representar cada proceso en la simulación.

## Uso

**1. Agregar procesos:**
  - Ingresa nombre, tiempo en CPU, instante de llegada y quantum (si aplica).
  - Los procesos reciben automáticamente un PID único.

**2. Seleccionar algoritmo de planificación:**
  - Elige entre FCFS, SJF, SRTF o Round Robin.

**3. Iniciar simulación:**
  - Presiona el botón Iniciar Simulación.
  - Se mostrará en pantalla la cola de procesos y su orden de ejecución.

**4. Observar resultados:**
  - Visualiza la ejecución en tiempo discreto (cada unidad = 5 segundos).
  - Revisa el historial de procesos finalizados.

<img width="1358" height="698" alt="Captura de pantalla (1270)" src="https://github.com/user-attachments/assets/5f1832ea-59dc-4594-992d-d546798b00d5" />

<img width="1357" height="693" alt="Captura de pantalla (1285)" src="https://github.com/user-attachments/assets/85954480-5e8d-4281-aa1b-4bb2e29a10e5" />

<img width="1142" height="754" alt="Captura de pantalla (1286)" src="https://github.com/user-attachments/assets/cf77f063-0d49-4cad-b101-11ab2151ffac" />

