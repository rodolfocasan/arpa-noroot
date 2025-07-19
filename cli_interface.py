#!/usr/bin/env python3
# cli_interface.py
import argparse





def get_arguments():
    """ Obtiene y procesa los argumentos de la línea de comandos """
    parser = argparse.ArgumentParser(description="Herramienta para desconectar dispositivos de red sin privilegios root - Linux")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-l", "--list", action="store_true", help="Listar dispositivos conectados en la red")
    group.add_argument("-k", "--kick", dest="target", help="Desconectar dispositivo(s) de la red (IP, MAC o 'all' para todos)")
    args = parser.parse_args()
    return args





def display_devices(devices):
    """ Muestra la lista de dispositivos encontrados """
    if not devices:
        print("[-] No se encontraron dispositivos en la red.")
        print("[*] Verifica tu conexión de red y permisos")
        return

    print('\n')
    print(f"[+] Dispositivos encontrados: {len(devices)}")
    print("=" * 60)
    for i, device in enumerate(devices, 1):
        print(f"{i:2d}. IP: {device['ip']:<15} MAC: {device['mac']}")
    print("=" * 60)


def display_targets(targets):
    """ Muestra la lista de dispositivos objetivo para ataque masivo """
    print('\n')
    print(f"[+] Dispositivos objetivo: {len(targets)}")
    for i, device in enumerate(targets, 1):
        print(f"  {i}. {device['ip']} - {device['mac']}")