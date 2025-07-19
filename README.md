# ARPA No Root - Herramienta de Análisis y Disrupción de Red
ARPA No Root es una versión modificada de la herramienta original ARPA que **NO requiere permisos de administrador**. Utiliza técnicas de saturación de recursos en lugar de ARP spoofing para analizar y disrumpir dispositivos en redes locales.

## ⚠️ Advertencia Legal
**IMPORTANTE**: Esta herramienta está diseñada únicamente para fines educativos y pruebas de seguridad autorizadas. El uso de esta herramienta en redes sin permiso explícito puede ser ilegal y constituir un delito. El desarrollador no se hace responsable del uso indebido de esta herramienta.

## Características
- **Análisis de Red**: Escanea la red local y muestra dispositivos conectados con sus direcciones IP y MAC
- **Disrupción Multi-Vector**: Utiliza múltiples técnicas simultáneas para disrumpir dispositivos:
  - Flood de conexiones TCP en puertos comunes
  - Flood de paquetes UDP
  - Saturación de ancho de banda
  - Flood ICMP (ping)
- **Sin privilegios root**: Funciona con permisos de usuario normal
- **Ataques paralelos**: Soporte para atacar múltiples dispositivos simultáneamente
- **Control granular**: Permite atacar dispositivos específicos por IP o MAC

## Requisitos del Sistema

- **Sistema Operativo**: Linux (optimizado para distribuciones basadas en Debian/Ubuntu)
- **Python**: 3.6+
- **Permisos**: Usuario normal (no requiere root)
- **Conectividad**: Conexión a red local activa

## Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/rodolfocasan/arpa-noroot.git
   cd arpa-noroot
   ```

2. **Verificar Python**:
   ```bash
   python3 --version
   ```

3. **Ejecutar directamente** (no requiere dependencias externas):
   ```bash
   python3 main.py -h
   ```

## Uso

### Listar Dispositivos en la Red

```bash
python3 main.py -l
```
```bash
python3 main.py --list
```

Este comando escanea la red local y muestra:
- Dirección IP de cada dispositivo
- Dirección MAC asociada
- Total de dispositivos encontrados

### Disrumpir un Dispositivo Específico

**Por dirección IP**:
```bash
python3 main.py -k 192.168.1.100
```

**Por dirección MAC**:
```bash
python3 main.py -k aa:bb:cc:dd:ee:ff
```

### Disrumpir Todos los Dispositivos

```bash
python3 main.py -k all
```

Este comando iniciará ataques paralelos contra todos los dispositivos detectados en la red (excluyendo el gateway).

### Detener un Ataque

Para detener cualquier ataque en curso, presiona:
```
Ctrl+C
```


## Técnicas Implementadas

### 1. Connection Flood (TCP)
- Satura puertos TCP comunes (21, 22, 80, 443, etc.)
- Múltiples conexiones simultáneas por puerto
- Envío de datos específicos según el tipo de servicio

### 2. UDP Flood
- Bombardeo de paquetes UDP a puertos comunes
- Paquetes de 1KB para maximizar el impacto
- Múltiples threads trabajando concurrentemente

### 3. Bandwidth Saturation
- Solicitudes HTTP con headers grandes
- Consumo intensivo de ancho de banda
- Conexiones keep-alive para mantener recursos ocupados

### 4. ICMP Flood
- Paquetes ping de gran tamaño (1400 bytes)
- Múltiples threads enviando continuamente
- Saturación del stack de red del objetivo


## Limitaciones

- **Efectividad variable**: La efectividad depende de la configuración del dispositivo objetivo
- **Detección**: Los ataques pueden ser detectados por sistemas de monitoreo de red
- **Recursos**: Consume recursos significativos del sistema durante los ataques
- **Protecciones**: Dispositivos con protecciones DDoS pueden ser resistentes

## Consideraciones Éticas y Legales

### ✅ Uso Permitido
- Pruebas de penetración autorizadas
- Auditorías de seguridad con consentimiento
- Investigación académica en entornos controlados
- Pruebas en redes propias

### ❌ Uso Prohibido
- Ataques a redes sin autorización
- Disrupción de servicios críticos
- Actividades maliciosas o criminales
- Violación de términos de servicio


## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork del repositorio
2. Crea una rama para tu feature
3. Commit de tus cambios
4. Push a la rama
5. Crea un Pull Request