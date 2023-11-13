import os
import threading
import time

import zmq
import subprocess

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Global Values

IP_ADDRESS = "127.0.0.1"
PORT_SUBSCRIBER = "8888"
PORT_PUBLISHER = "9999"
CONTEXT = zmq.Context()
SUBSCRIBER = CONTEXT.socket(zmq.SUB)
SUBSCRIBER.bind(f"tcp://{IP_ADDRESS}:{PORT_SUBSCRIBER}")
SUBSCRIBER.setsockopt(zmq.SUBSCRIBE, "".encode())
PUBLISHER = CONTEXT.socket(zmq.PUB)
PUBLISHER.bind(f"tcp://{IP_ADDRESS}:{PORT_PUBLISHER}")
LOCK_MENSAJES = threading.Lock()
PID = 0


# end Global Values

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Method: Health_Checker
def health_checker(topic):
    subscriber_temp = CONTEXT.socket(zmq.SUB)
    subscriber_temp.connect(f"tcp://{IP_ADDRESS}:{PORT_PUBLISHER}")
    subscriber_temp.setsockopt(zmq.SUBSCRIBE, topic.encode())
    poller = zmq.Poller()
    poller.register(subscriber_temp, zmq.POLLIN)
    timeout = 5  # segundos
    # Si todoo inicia secuencialmente, el health checker se ejecuta
    # después de que el sensor se haya ejecutado
    time.sleep(2)

    print(f"Health checker for {topic} running...")
    while True:

        socks = dict(poller.poll(timeout * 1000))  # Convertir a milisegundos

        if subscriber_temp in socks and socks[subscriber_temp] == zmq.POLLIN:
            LOCK_MENSAJES.acquire()
            mensaje = subscriber_temp.recv_multipart()
            print(f"Mensaje recibido: {mensaje}")
            LOCK_MENSAJES.release()
            iteracion_actual = 0
            timeout = int(mensaje[1].decode()) + 2
        else:
            # No se recibió nada en el intervalo de tiempo especificado
            LOCK_MENSAJES.acquire()
            print(f"No se recibió nada en {timeout} segundos de {topic}. Tomando acciones...")
            # Nombre del archivo a ejecutar
            archivo_a_ejecutar = "monitor.py"
            # Argumentos a pasar al programa
            argumentos = ["-t", f"{topic}"]
            # Ejecutar el archivo con argumentos usando subprocess
            subproceso = subprocess.Popen(["python", archivo_a_ejecutar] + argumentos)
            PID = subproceso.pid
            print(f"ID del proceso desvinculado: {PID}")
            LOCK_MENSAJES.release()
        # Realizar otras tareas o acciones según sea necesario
        time.sleep(1)

    # end while


# end def

def sender():
    while True:
        msg = SUBSCRIBER.recv_multipart()
        # print(msg)
        PUBLISHER.send_multipart(msg)
    # end while
# end def


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Información que debo obtener:
# tipo de sensor que se dañó, intervalo en el que ese sensor estaba enviando info
# documento al que estaba vinculado
def main():
    try:
        hilo_informador = threading.Thread(target=sender)
        hilo_oxygen = threading.Thread(target=health_checker, args=("oxygen",), daemon=False)
        hilo_ph = threading.Thread(target=health_checker, args=("PH",), daemon=False)
        hilo_temperature = threading.Thread(target=health_checker, args=("temperature",), daemon=False)

        # Declaraciones explícitas sólo para hacer el código más fácil de leer
        hilo_informador.start()
        hilo_oxygen.start()
        hilo_ph.start()
        hilo_temperature.start()

        hilo_informador.join()
        hilo_oxygen.join()
        hilo_ph.join()
        hilo_temperature.join()
    except KeyboardInterrupt:
        print("Error: unable to start thread")


if __name__ == "__main__":
    main()
