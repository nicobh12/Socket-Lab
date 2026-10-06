#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cliente_eco_r2.py
Laboratorio de Sistemas Distribuidos - Reto R2
Maquina: VM-CLIENTE

Cliente de eco con protocolo delimitado por \n.
Cada mensaje que se envia termina en \n. La respuesta del servidor
tambien viene terminada en \n, y el cliente la recibe completa.

Ejecucion: python3 cliente_eco_r2.py <ip_servidor> <puerto>
Ejemplo : python3 cliente_eco_r2.py 192.168.56.10 5000
"""

import socket
import sys

TAM_BUFFER = 1024
DELIMITADOR = b"\n"


def main():
    if len(sys.argv) != 3:
        print("uso: python3 cliente_eco_r2.py <ip_servidor> <puerto>")
        sys.exit(1)

    ip_servidor = sys.argv[1]
    puerto = int(sys.argv[2])

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print(f"[cliente] conectando a {ip_servidor}:{puerto} ...")
        cliente.connect((ip_servidor, puerto))
        print(f"[cliente] conectado")
        print(f"[cliente] extremo local  : {cliente.getsockname()}")
        print(f"[cliente] extremo remoto : {cliente.getpeername()}")
        print("[cliente] escriba un texto. Escriba 'salir' para terminar.\n")

        buffer = b""

        while True:
            texto = input("> ")
            if texto == "":
                continue
            if texto.lower() == "salir":
                break

            # Codificar y AGREGAR el delimitador al final.
            mensaje = texto.encode("utf-8") + DELIMITADOR
            cliente.sendall(mensaje)
            print(f"[cliente] enviados {len(mensaje)} bytes: {mensaje!r}")

            # Leer hasta tener al menos un mensaje completo (con \n).
            # Puede requerir varios recv() si la respuesta llega partida.
            while DELIMITADOR not in buffer:
                datos = cliente.recv(TAM_BUFFER)
                if not datos:
                    print("[cliente] recv() devolvio 0 bytes -> "
                          "el servidor cerro la conexion")
                    return
                buffer += datos

            # Extraer un mensaje completo del buffer.
            respuesta, buffer = buffer.split(DELIMITADOR, 1)
            print(f"[cliente] recibidos {len(respuesta)} bytes: "
                  f"{respuesta.decode('utf-8')}")

    except ConnectionRefusedError:
        print(f"[cliente] ERROR: conexion rechazada. "
              f"Nadie escucha en {ip_servidor}:{puerto}")
    except OSError as e:
        print(f"[cliente] ERROR de red: {e}")
    except KeyboardInterrupt:
        print("\n[cliente] interrumpido por el usuario")
    finally:
        cliente.close()
        print("[cliente] socket cerrado")


if __name__ == "__main__":
    main()
