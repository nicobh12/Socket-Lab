#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
servidor_eco_r2.py
Laboratorio de Sistemas Distribuidos - Reto R2
Maquina: VM-SERVIDOR

Servidor de eco con protocolo delimitado por salto de linea (\n).
Resuelve el problema de E4: TCP no conserva las fronteras de los mensajes.
Ahora cada mensaje viaja terminado en \n y el servidor procesa exactamente
un mensaje por vez, sin importar como se agrupen los bytes en la red.

Ejecucion: python3 servidor_eco_r2.py
"""

import socket

HOST = "0.0.0.0"
PUERTO = 5000
TAM_BUFFER = 1024
DELIMITADOR = b"\n"   # los mensajes terminan con un salto de linea


def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PUERTO))
    servidor.listen(1)

    print(f"[servidor] socket de escucha en {servidor.getsockname()}")
    print("[servidor] protocolo: mensajes delimitados por \\n")
    print("[servidor] esperando conexiones... (Ctrl+C para terminar)")

    try:
        while True:
            conexion, direccion = servidor.accept()
            print("\n[servidor] ---- conexion aceptada ----")
            print(f"[servidor] cliente remoto : {direccion[0]}:{direccion[1]}")
            print(f"[servidor] extremo local  : {conexion.getsockname()}")
            print(f"[servidor] extremo remoto : {conexion.getpeername()}")

            with conexion:
                # El buffer se declara FUERA del bucle de recv().
                # Asi conserva el fragmento parcial entre llamadas.
                buffer = b""

                while True:
                    datos = conexion.recv(TAM_BUFFER)
                    if not datos:
                        print("[servidor] recv() devolvio 0 bytes -> "
                              "el cliente cerro la conexion")
                        break

                    # Sumar lo nuevo a lo que ya teniamos pendiente.
                    buffer += datos

                    # Puede haber 0, 1 o VARIOS mensajes completos en el buffer.
                    # Se usa while (no if) porque un solo recv() puede traer
                    # varios mensajes completos de una vez.
                    while DELIMITADOR in buffer:
                        mensaje, buffer = buffer.split(DELIMITADOR, 1)
                        print(f"[servidor] mensaje completo: {mensaje!r}")

                        respuesta = mensaje.upper() + DELIMITADOR
                        conexion.sendall(respuesta)
                        print(f"[servidor] respuesta: {respuesta!r}")

                    # Si queda algo en el buffer sin \n, es un mensaje PARCIAL.
                    # No se procesa y NO se descarta: espera al proximo recv().

            print("[servidor] conexion cerrada. Vuelvo a accept()\n")

    except KeyboardInterrupt:
        print("\n[servidor] interrumpido por el usuario")
    finally:
        servidor.close()
        print("[servidor] socket de escucha cerrado")


if __name__ == "__main__":
    main()
