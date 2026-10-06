#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
servidor_eco_r1.py
Laboratorio de Sistemas Distribuidos - Reto R1
Maquina: VM-SERVIDOR

Servidor de eco con bitacora. Ademas de hacer eco, escribe en bitacora.log
una linea por cada conexion atendida, con:
  - marca de tiempo
  - IP y puerto del cliente
  - numero de mensajes intercambiados
  - total de bytes enviados y recibidos

Ejecucion: python3 servidor_eco_r1.py
"""

import socket
import datetime

HOST = "0.0.0.0"
PUERTO = 5000
TAM_BUFFER = 1024
ARCHIVO_BITACORA = "bitacora.log"


def registrar_conexion(ip_cliente, puerto_cliente, num_mensajes,
                       bytes_recibidos, bytes_enviados, duracion):
    """Escribe una linea en el archivo bitacora.log con los datos
    de una conexion ya terminada."""
    marca = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = (
        f"{marca} | "
        f"cliente={ip_cliente}:{puerto_cliente} | "
        f"mensajes={num_mensajes} | "
        f"bytes_recibidos={bytes_recibidos} | "
        f"bytes_enviados={bytes_enviados} | "
        f"duracion={duracion:.2f}s\n"
    )
    # "a" abre el archivo en modo append: agrega al final sin borrar.
    with open(ARCHIVO_BITACORA, "a", encoding="utf-8") as archivo:
        archivo.write(linea)


def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PUERTO))
    servidor.listen(1)

    print(f"[servidor] socket de escucha en {servidor.getsockname()}")
    print(f"[servidor] bitacora: {ARCHIVO_BITACORA}")
    print("[servidor] esperando conexiones... (Ctrl+C para terminar)")

    try:
        while True:
            conexion, direccion = servidor.accept()
            ip_cliente, puerto_cliente = direccion

            # Contadores por conexion
            num_mensajes = 0
            bytes_recibidos = 0
            bytes_enviados = 0
            hora_inicio = datetime.datetime.now()

            print("\n[servidor] ---- conexion aceptada ----")
            print(f"[servidor] cliente remoto : {ip_cliente}:{puerto_cliente}")
            print(f"[servidor] extremo local  : {conexion.getsockname()}")
            print(f"[servidor] extremo remoto : {conexion.getpeername()}")

            with conexion:
                while True:
                    datos = conexion.recv(TAM_BUFFER)
                    if not datos:
                        print("[servidor] recv() devolvio 0 bytes -> "
                              "el cliente cerro la conexion")
                        break

                    num_mensajes += 1
                    bytes_recibidos += len(datos)
                    print(f"[servidor] recibidos {len(datos)} bytes: {datos!r}")

                    respuesta = datos.upper()
                    conexion.sendall(respuesta)
                    bytes_enviados += len(respuesta)
                    print(f"[servidor] enviados {len(respuesta)} bytes: "
                          f"{respuesta!r}")

            # La conexion termino: calculamos duracion y registramos.
            hora_fin = datetime.datetime.now()
            duracion = (hora_fin - hora_inicio).total_seconds()

            registrar_conexion(ip_cliente, puerto_cliente, num_mensajes,
                               bytes_recibidos, bytes_enviados, duracion)
            print(f"[servidor] bitacora actualizada: "
                  f"{num_mensajes} mensajes, "
                  f"{bytes_recibidos} bytes recibidos, "
                  f"{bytes_enviados} bytes enviados, "
                  f"{duracion:.2f}s")
            print("[servidor] conexion cerrada. Vuelvo a accept()\n")

    except KeyboardInterrupt:
        print("\n[servidor] interrumpido por el usuario")
    finally:
        servidor.close()
        print("[servidor] socket de escucha cerrado")


if __name__ == "__main__":
    main()
