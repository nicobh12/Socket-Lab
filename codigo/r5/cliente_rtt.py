#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cliente_rtt.py
Laboratorio de Sistemas Distribuidos - Reto R5
Maquina: VM-CLIENTE

Mide el RTT (round-trip time) de cada mensaje.
Envia 100 mensajes de 10 bytes y 100 de 8000 bytes.
Presenta min, max y promedio de cada serie.
"""

import socket
import sys
import time
import statistics

TAM_BUFFER = 16384
DELIMITADOR = b"\n"


def medir_serie(cliente, tam_mensaje, cantidad):
    """Envia 'cantidad' mensajes de tam_mensaje bytes y mide el RTT de cada uno.
    Devuelve la lista de RTTs en milisegundos.
    """
    rtts = []
    payload = b"x" * tam_mensaje
    buffer = b""

    print(f"\n[test] enviando {cantidad} mensajes de {tam_mensaje} bytes...")

    for i in range(cantidad):
        mensaje = payload + DELIMITADOR

        t_inicio = time.perf_counter()
        cliente.sendall(mensaje)

        # Leer hasta tener la respuesta completa.
        while DELIMITADOR not in buffer:
            datos = cliente.recv(TAM_BUFFER)
            if not datos:
                raise ConnectionError("el servidor cerro la conexion")
            buffer += datos

        respuesta, buffer = buffer.split(DELIMITADOR, 1)
        t_fin = time.perf_counter()

        rtt_ms = (t_fin - t_inicio) * 1000
        rtts.append(rtt_ms)

    return rtts


def main():
    if len(sys.argv) != 3:
        print("uso: python3 cliente_rtt.py <ip_servidor> <puerto>")
        sys.exit(1)

    ip_servidor = sys.argv[1]
    puerto = int(sys.argv[2])

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        cliente.connect((ip_servidor, puerto))
        print(f"[cliente] conectado a {ip_servidor}:{puerto}")

        # Serie 1: 100 mensajes de 10 bytes
        rtts_pequenos = medir_serie(cliente, 10, 100)

        # Serie 2: 100 mensajes de 8000 bytes
        rtts_grandes = medir_serie(cliente, 8000, 100)

        # Tabla de resultados
        print("\n" + "=" * 60)
        print(f"{'Serie':<20} {'Min (ms)':<12} {'Max (ms)':<12} {'Prom (ms)':<12}")
        print("=" * 60)
        print(f"{'10 bytes':<20} {min(rtts_pequenos):<12.3f} "
              f"{max(rtts_pequenos):<12.3f} {statistics.mean(rtts_pequenos):<12.3f}")
        print(f"{'8000 bytes':<20} {min(rtts_grandes):<12.3f} "
              f"{max(rtts_grandes):<12.3f} {statistics.mean(rtts_grandes):<12.3f}")
        print("=" * 60)
        print(f"\nDiferencia promedio: "
              f"{statistics.mean(rtts_grandes) - statistics.mean(rtts_pequenos):.3f} ms")

    except OSError as e:
        print(f"[cliente] ERROR de red: {e}")
    except KeyboardInterrupt:
        print("\n[cliente] interrumpido")
    finally:
        cliente.close()
        print("[cliente] socket cerrado")


if __name__ == "__main__":
    main()
