#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
servidor_rtt.py
Laboratorio de Sistemas Distribuidos - Reto R5
Maquina: VM-SERVIDOR

Servidor de eco simple con protocolo delimitado por \n.
Se usa para medir RTT desde el cliente.
"""

import socket

HOST = "0.0.0.0"
PUERTO = 5000
TAM_BUFFER = 16384
DELIMITADOR = b"\n"


def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PUERTO))
    servidor.listen(5)

    print(f"[servidor] socket de escucha en {servidor.getsockname()}")
    print("[servidor] listo para medir RTT")

    try:
        while True:
            conexion, direccion = servidor.accept()
            print(f"[servidor] conexion desde {direccion[0]}:{direccion[1]}")

            with conexion:
                buffer = b""
                while True:
                    datos = conexion.recv(TAM_BUFFER)
                    if not datos:
                        break
                    buffer += datos
                    while DELIMITADOR in buffer:
                        mensaje, buffer = buffer.split(DELIMITADOR, 1)
                        conexion.sendall(mensaje + DELIMITADOR)

            print("[servidor] conexion cerrada")

    except KeyboardInterrupt:
        print("\n[servidor] interrumpido")
    finally:
        servidor.close()


if __name__ == "__main__":
    main()
