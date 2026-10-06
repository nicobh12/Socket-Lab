#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
servidor_threading.py
Laboratorio de Sistemas Distribuidos - Reto R4
Maquina: VM-SERVIDOR

Servidor concurrente con threading: lanza un hilo por cada cliente
aceptado. El contador de ESTADISTICAS es compartido y protegido con
un lock para evitar race conditions entre hilos.

Combina R3 (comandos) con R4 (threading).
"""

import socket
import datetime
import threading

HOST = "0.0.0.0"
PUERTO = 5000
TAM_BUFFER = 1024
DELIMITADOR = b"\n"

# Recurso compartido entre hilos: el contador de mensajes atendidos.
# El lock garantiza que solo un hilo lo modifique a la vez.
contador = [0]
lock = threading.Lock()


def procesar_comando(linea):
    try:
        texto = linea.decode("utf-8").strip()
    except UnicodeDecodeError:
        return b"ERROR comando desconocido"

    if texto == "HORA":
        ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"HORA {ahora}".encode("utf-8")

    if texto.startswith("ECO "):
        return b"ECO " + texto[4:].encode("utf-8")

    if texto == "ESTADISTICAS":
        # Leer el contador tambien dentro del lock para consistencia.
        with lock:
            valor = contador[0]
        return f"ESTADISTICAS mensajes={valor}".encode("utf-8")

    if texto == "ADIOS":
        return b"ADIOS"

    return b"ERROR comando desconocido"


def atender_cliente(conexion, direccion):
    """Funcion que corre en un hilo por cada cliente."""
    print(f"[hilo {threading.current_thread().name}] "
          f"atendiendo a {direccion[0]}:{direccion[1]}")

    with conexion:
        buffer = b""
        adios = False

        while not adios:
            datos = conexion.recv(TAM_BUFFER)
            if not datos:
                print(f"[hilo {threading.current_thread().name}] "
                      f"cliente {direccion[0]}:{direccion[1]} cerro")
                break

            buffer += datos

            while DELIMITADOR in buffer:
                linea, buffer = buffer.split(DELIMITADOR, 1)
                if linea == b"":
                    continue

                # Incrementar el contador dentro del lock.
                # Esto es lo que evita la race condition.
                with lock:
                    contador[0] += 1

                respuesta = procesar_comando(linea)
                conexion.sendall(respuesta + DELIMITADOR)
                print(f"[hilo {threading.current_thread().name}] "
                      f"{linea!r} -> {respuesta!r}")

                if linea.decode("utf-8", errors="ignore").strip() == "ADIOS":
                    print(f"[hilo {threading.current_thread().name}] "
                          f"ADIOS recibido")
                    adios = True
                    break

    print(f"[hilo {threading.current_thread().name}] "
          f"conexion con {direccion[0]}:{direccion[1]} terminada")


def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PUERTO))
    servidor.listen(5)

    print(f"[servidor] socket de escucha en {servidor.getsockname()}")
    print("[servidor] modo concurrente (threading)")
    print("[servidor] esperando conexiones... (Ctrl+C para terminar)")

    try:
        while True:
            conexion, direccion = servidor.accept()
            hilo = threading.Thread(
                target=atender_cliente,
                args=(conexion, direccion),
                daemon=True,
            )
            hilo.start()

    except KeyboardInterrupt:
        print("\n[servidor] interrumpido por el usuario")
    finally:
        servidor.close()
        print("[servidor] socket de escucha cerrado")


if __name__ == "__main__":
    main()
