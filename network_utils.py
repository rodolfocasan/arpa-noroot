#!/usr/bin/env python3
# network_utils.py
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed





def get_gateway_ip():
    """ Obtiene la IP del gateway usando métodos específicos de Linux """
    try:
        # Método principal: usar comando ip route (más moderno)
        result = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True, text=True, timeout=5
        )
        
        if result.returncode == 0 and result.stdout:
            # Parsear salida: default via 192.168.1.1 dev wlan0 proto dhcp metric 600
            for line in result.stdout.splitlines():
                if "default" in line and "via" in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        return parts[2]
    except Exception as e:
        print(f"[!] Error obteniendo gateway con ip route: {e}")
    
    try:
        # Método alternativo: leer /proc/net/route (más universal)
        with open('/proc/net/route', 'r') as f:
            next(f)  # Saltar header
            for line in f:
                parts = line.split()
                if len(parts) >= 3 and parts[1] == '00000000':  # Ruta por defecto
                    gateway_hex = parts[2]
                    # Convertir hexadecimal little-endian a IP
                    gateway_ip = '.'.join(str(int(gateway_hex[i:i+2], 16))
                                        for i in range(6, -1, -2))
                    return gateway_ip
    except Exception as e:
        print(f"[!] Error leyendo /proc/net/route: {e}")
    
    try:
        # Método de respaldo: usar route command (legacy)
        result = subprocess.run(
            ["route", "-n"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("0.0.0.0"):
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[1]
    except Exception as e:
        print(f"[!] Error con comando route: {e}")
    return None



def get_network_interface():
    """ Obtiene la interfaz de red principal activa """
    try:
        # Obtener la interfaz de la ruta por defecto
        result = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout:
            for line in result.stdout.splitlines():
                if "default" in line and "dev" in line:
                    parts = line.split()
                    dev_index = parts.index("dev")
                    if dev_index + 1 < len(parts):
                        return parts[dev_index + 1]
    except:
        pass
    
    # Fallback: buscar interfaces activas
    try:
        result = subprocess.run(
            ["ip", "link", "show", "up"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            if "state UP" in line and "lo:" not in line:
                interface = line.split(":")[1].strip()
                return interface
    except:
        pass
    return None



def ping_sweep(network_base):
    """ Escaneo de red usando ping paralelo optimizado para Linux """
    alive_hosts = []

    def ping_host(ip):
        """ Función para hacer ping a un host específico usando ping de Linux """
        try:
            # Usar ping optimizado para Linux: -c 1 (count), -W 1 (timeout), -q (quiet)
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", "-q", ip],
                capture_output=True, timeout=2, text=True
            )
            if result.returncode == 0:
                return ip
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass
        return None

    print(f"[*] Ejecutando ping sweep en {network_base}.0/24...")
    
    # Usar ThreadPoolExecutor para paralelizar el ping
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        # Escanear todas las IPs del rango (1-254)
        for i in range(1, 255):
            ip = f"{network_base}.{i}"
            futures.append(executor.submit(ping_host, ip))

        # Recopilar resultados con progreso
        completed = 0
        for future in as_completed(futures):
            completed += 1
            if completed % 50 == 0:
                print(f"[*] Progreso: {completed}/254 hosts escaneados")
            result = future.result()
            if result:
                alive_hosts.append(result)
    
    print(f"[*] Ping sweep completado. Hosts activos: {len(alive_hosts)}")
    return alive_hosts



def get_arp_table():
    """ Obtiene la tabla ARP usando métodos específicos de Linux """
    arp_table = {}
    
    try:
        # Método principal: usar comando arp
        result = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                # Formato: hostname (192.168.1.1) at aa:bb:cc:dd:ee:ff [ether] on eth0
                if "(" in line and ")" in line and " at " in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        ip = parts[1].strip("()")
                        mac = parts[3]
                        # Validar formato de MAC
                        if re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', mac):
                            arp_table[ip] = mac
    except Exception as e:
        print(f"[!] Error obteniendo ARP con comando arp: {e}")
    
    try:
        # Método alternativo: leer /proc/net/arp
        with open('/proc/net/arp', 'r') as f:
            next(f)  # Saltar header
            for line in f:
                parts = line.split()
                if len(parts) >= 4:
                    ip = parts[0]
                    mac = parts[3]
                    # Validar que no sea una entrada incompleta
                    if mac != "00:00:00:00:00:00" and ":" in mac:
                        arp_table[ip] = mac
    except Exception as e:
        print(f"[!] Error leyendo /proc/net/arp: {e}")
    
    try:
        # Método adicional: usar ip neighbor (más moderno)
        result = subprocess.run(["ip", "neighbor"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                # Formato: 192.168.1.1 dev eth0 lladdr aa:bb:cc:dd:ee:ff REACHABLE
                parts = line.split()
                if len(parts) >= 5 and "lladdr" in parts:
                    ip = parts[0]
                    lladdr_index = parts.index("lladdr")
                    if lladdr_index + 1 < len(parts):
                        mac = parts[lladdr_index + 1]
                        if re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', mac):
                            arp_table[ip] = mac
    except Exception as e:
        print(f"[!] Error obteniendo neighbors con ip neighbor: {e}")
    return arp_table



def scan_network():
    """ Escanea la red usando métodos específicos de Linux """
    gateway = get_gateway_ip()
    if not gateway:
        print("[!] No se pudo obtener el gateway")
        return []

    # Obtener la base de red (ej: 192.168.1 de 192.168.1.1)
    network_base = '.'.join(gateway.split('.')[:-1])
    interface = get_network_interface()
    
    print(f"[*] Gateway detectado: {gateway}")
    print(f"[*] Interfaz de red: {interface if interface else 'No detectada'}")
    print(f"[*] Escaneando red {network_base}.0/24...")

    # Combinar ping sweep con tabla ARP para obtener IP y MAC
    alive_hosts = ping_sweep(network_base)
    
    # Obtener tabla ARP después del ping sweep para tener más entradas
    print("[*] Obteniendo tabla ARP...")
    arp_table = get_arp_table()
    
    # Forzar actualización de ARP para hosts vivos
    print("[*] Actualizando entradas ARP...")
    for ip in alive_hosts:
        try:
            # Hacer ping adicional para forzar entrada ARP
            subprocess.run(["ping", "-c", "1", "-W", "1", ip], capture_output=True, timeout=1)
        except:
            pass
    
    # Obtener tabla ARP actualizada
    arp_table.update(get_arp_table())

    devices = []
    for ip in alive_hosts:
        mac = arp_table.get(ip, "Desconocido")
        devices.append({"ip": ip, "mac": mac})
    return devices



def es_ip(target):
    """ Verifica si el objetivo es una dirección IP válida """
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    
    if re.match(pattern, target):
        parts = target.split(".")
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        return True
    return False



def es_mac(target):
    """ Verifica si el objetivo es una dirección MAC válida """
    pattern = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
    return bool(re.match(pattern, target))



def get_ip_from_mac(mac, devices):
    """ Obtiene la IP asociada a una MAC de la lista de dispositivos """
    for device in devices:
        if device["mac"].lower() == mac.lower():
            return device["ip"]
    return None