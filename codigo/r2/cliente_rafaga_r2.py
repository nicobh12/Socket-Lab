#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cliente_rafaga_r2.py
Laboratorio de Sistemas Distribuidos - Reto R2
Maquina: VM-CLIENTE

Variante de cliente_rafaga.py que SI usa delimitador \n.
Envia tres mensajes sin pausa, todos delimitados, y luego lee UN solo
mensaje completo. Sirve para verificar que el servidor R2 procesa
correctamente incluso cuando los tres mensajes llegan juntos.

Ejecucion: python3 cliente_rafaga_r2.py <ip_servidor> <puerto> [pausa_segundos]
"""

import socket
import sys
import time

TAM_BUFFER = 1024
DELIMITADOR = b"\n"
MENSAJES = [b"uno", b"dos", b"tres"]


def main():
    if len(sys.argv) not in (3, 4):
        print("uso: python3 cliente_rafaga_r2.py <ip_servidor> <puerto> "
              "[pausa_segundos]")
        sys.exit(1)

    ip_servidor = sys.argv[1]
    puerto = int(sys.argv[2])
    pausa = float(sys.argv[3]) if len(sys.argv) == 4 else 0.0

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        cliente.connect((ip_servidor, puerto))
        print(f"[rafaga] conectado desde {cliente.getsockname()} "
              f"hacia {cliente.getpeername()}")
        print(f"[rafaga] pausa entre envios: {pausa} s\n")

        for m in MENSAJES:
            cliente.sendall(m + DELIMITADOR)
            print(f"[rafaga] send -> {m!r} + \\n")
            if pausa > 0:
                time.sleep(pausa)

        print(f"\n[rafaga] enviados {len(MENSAJES)} mensajes delimitados")

        # Leer los 3 mensajes completos del buffer del cliente.
        buffer = b""
        recibidos = 0
        while recibidos < len(MENSAJES):
            datos = cliente.recv(TAM_BUFFER)
            if not datos:
                print("[rafaga] conexion cerrada por el servidor")
                return
            buffer += datos
            while DELIMITADOR in buffer and recibidos < len(MENSAJES):
                mensaje, buffer = buffer.split(DELIMITADOR, 1)
                print(f"[rafaga] recv <- {mensaje!r}")
                recibidos += 1

        print("\n[rafaga] los 3 mensajes se recibieron delimitados "
              "correctamente")

    except OSError as e:
        print(f"[rafaga] ERROR de red: {e}")
    finally:
        cliente.close()


if __name__ == "__main__":
    main()

