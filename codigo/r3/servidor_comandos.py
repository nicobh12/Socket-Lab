#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
servidor_comandos.py
Laboratorio de Sistemas Distribuidos - Reto R3
Maquina: VM-SERVIDOR

Servidor de comandos:
  HORA            -> devuelve la hora del servidor
  ECO <texto>     -> devuelve el texto tal cual
  ESTADISTICAS    -> mensajes atendidos desde el arranque
  ADIOS           -> cierra la conexion

Protocolo: mensajes delimitados por \n.
"""

import socket
import datetime

HOST = "0.0.0.0"
PUERTO = 5000
TAM_BUFFER = 1024
DELIMITADOR = b"\n"


def procesar_comando(linea, contador):
    """Recibe una linea de comando (bytes) y devuelve la respuesta (bytes).
    El contador se pasa como argumento para poder modificarlo sin usar global.
    """
    try:
        texto = linea.decode("utf-8").strip()
    except UnicodeDecodeError:
        return b"ERROR comando desconocido"

    if texto == "HORA":
        ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"HORA {ahora}".encode("utf-8")

    if texto.startswith("ECO "):
        # Devuelve lo que viene despues de "ECO "
        return b"ECO " + texto[4:].encode("utf-8")

    if texto == "ESTADISTICAS":
        return f"ESTADISTICAS mensajes={contador[0]}".encode("utf-8")

    if texto == "ADIOS":
        return b"ADIOS"

    return b"ERROR comando desconocido"


def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PUERTO))
    servidor.listen(5)

    # Lista de un solo elemento para poder modificar el valor desde dentro
    # de las funciones. Es una tecnica simple de mutable state en Python.
    contador = [0]

    print(f"[servidor] socket de escucha en {servidor.getsockname()}")
    print("[servidor] comandos: HORA, ECO <texto>, ESTADISTICAS, ADIOS")
    print("[servidor] esperando conexiones... (Ctrl+C para terminar)")

    try:
        while True:
            conexion, direccion = servidor.accept()
            print(f"\n[servidor] conexion desde {direccion[0]}:{direccion[1]}")

            with conexion:
                buffer = b""
                while True:
                    datos = conexion.recv(TAM_BUFFER)
                    if not datos:
                        print("[servidor] cliente cerro la conexion")
                        break

                    buffer += datos

                    # Procesar TODOS los comandos completos que haya.
                    while DELIMITADOR in buffer:
                        linea, buffer = buffer.split(DELIMITADOR, 1)
                        if linea == b"":
                            # Ignorar lineas vacias
                            continue

                        print(f"[servidor] comando: {linea!r}")
                        contador[0] += 1

                        respuesta = procesar_comando(linea, contador)
                        conexion.sendall(respuesta + DELIMITADOR)
                        print(f"[servidor] respuesta: {respuesta!r}")

                        # Si el comando fue ADIOS, cerrar la conexion.
                        if linea.decode("utf-8", errors="ignore").strip() == "ADIOS":
                            print("[servidor] ADIOS recibido, cerrando conexion")
                            conexion.close()
                            break
                    else:
                        # El while interno termino sin break.
                        # Verificar si el cliente pidio ADIOS.
                        continue
                    # Si llegamos aqui fue porque el while interno hizo break.
                    break

            print("[servidor] conexion terminada\n")

    except KeyboardInterrupt:
        print("\n[servidor] interrumpido por el usuario")
    finally:
        servidor.close()
        print("[servidor] socket de escucha cerrado")


if __name__ == "__main__":
    main()

