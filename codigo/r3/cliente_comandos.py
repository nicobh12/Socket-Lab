#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cliente_comandos.py
Laboratorio de Sistemas Distribuidos - Reto R3
Maquina: VM-CLIENTE

Cliente que envia comandos al servidor R3:
  HORA
  ECO <texto>
  ESTADISTICAS
  ADIOS
"""

import socket
import sys

TAM_BUFFER = 1024
DELIMITADOR = b"\n"


def enviar_comando(cliente, buffer, comando):
    """Envia un comando y devuelve (respuesta, buffer_actualizado).
    Mantiene el buffer entre llamadas para manejar respuestas partidas.
    """
    mensaje = comando.encode("utf-8") + DELIMITADOR
    cliente.sendall(mensaje)

    while DELIMITADOR not in buffer:
        datos = cliente.recv(TAM_BUFFER)
        if not datos:
            return None, buffer
        buffer += datos

    respuesta, buffer = buffer.split(DELIMITADOR, 1)
    return respuesta.decode("utf-8"), buffer


def main():
    if len(sys.argv) != 3:
        print("uso: python3 cliente_comandos.py <ip_servidor> <puerto>")
        sys.exit(1)

    ip_servidor = sys.argv[1]
    puerto = int(sys.argv[2])

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        cliente.connect((ip_servidor, puerto))
        print(f"[cliente] conectado a {ip_servidor}:{puerto}")
        print("[cliente] comandos: HORA | ECO <texto> | ESTADISTICAS | ADIOS\n")

        buffer = b""

        while True:
            comando = input("> ").strip()
            if comando == "":
                continue

            respuesta, buffer = enviar_comando(cliente, buffer, comando)
            if respuesta is None:
                print("[cliente] el servidor cerro la conexion")
                break

            print(f"[servidor] {respuesta}")

            if comando.upper() == "ADIOS":
                break

    except ConnectionRefusedError:
        print(f"[cliente] ERROR: conexion rechazada")
    except OSError as e:
        print(f"[cliente] ERROR de red: {e}")
    except KeyboardInterrupt:
        print("\n[cliente] interrumpido")
    finally:
        cliente.close()
        print("[cliente] socket cerrado")


if __name__ == "__main__":
    main()

