# TiktokCraft 🎯

Sistema modular de overlays para TikTok Live Studio con control en tiempo real.

## 🌟 Características

- ✅ **API REST completa** para gestionar overlays de subastas
- ✅ **WebSocket en tiempo real** para actualizaciones instantáneas
- ✅ **Panel de administración web** intuitivo y responsive
- ✅ **Arquitectura modular y escalable** - fácil añadir nuevos tipos de overlays
- ✅ **Control total**: pausar, reanudar, modificar tiempo en vivo
- ✅ **Overlay visual personalizable** listo para integrar en TikTok Live Studio

## 📋 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🚀 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd TiktokCraft
```

### 2. Instalar dependencias

#### Windows (PowerShell)
```powershell
python -m pip install -r requirements.txt
```

#### Linux/Mac
```bash
pip install -r requirements.txt
```

### 3. Iniciar el servidor

#### Windows (PowerShell)
```powershell
python main.py
```

#### Linux/Mac
```bash
python main.py
```

El servidor se iniciará en `http://localhost:8000`

## 📖 Uso Rápido

### 1. Acceder al Panel de Administración

Abre tu navegador y ve a: `http://localhost:8000/admin`

### 2. Crear una Subasta

En el panel de administración:
- Nombre del Streamer: `santiago`
- Título de la Subasta: `Subasta online`
- Duración: `5` minutos
- Click en **Crear Subasta**

### 3. Obtener el enlace del Overlay

Después de crear la subasta, se generará automáticamente un enlace como:
```
http://localhost:8000/overlay/auction/550e8400-e29b-41d4-a716-446655440000
```

### 4. Integrar en TikTok Live Studio

1. Abre TikTok Live Studio
2. Añade una nueva fuente → **Browser**
3. Pega el enlace del overlay
4. Ajusta el tamaño y posición según necesites
5. ¡Listo! El overlay se actualizará en tiempo real

## 🎛️ API REST Endpoints

### Crear Subasta
```http
POST /api/auctions
Content-Type: application/json

{
  "nameStreamer": "santiago",
  "timer": 5,
  "tituloSubasta": "Subasta online",
  "id": "opcional-guid"
}
```

**Respuesta:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nameStreamer": "santiago",
  "tituloSubasta": "Subasta online",
  "timerMinutes": 5,
  "status": "active",
  "overlayUrl": "http://localhost:8000/overlay/auction/550e8400-...",
  "createdAt": "2025-11-07T10:30:00",
  "startedAt": "2025-11-07T10:30:00",
  "remainingSeconds": 300
}
```

### Listar todas las Subastas
```http
GET /api/auctions
```

### Obtener una Subasta específica
```http
GET /api/auctions/{auction_id}
```

### Controlar Subasta
```http
POST /api/auctions/{auction_id}/control
Content-Type: application/json

{
  "action": "pause"  // start | pause | resume | stop
}
```

### Modificar Tiempo
```http
PATCH /api/auctions/{auction_id}/time
Content-Type: application/json

{
  "seconds": 60  // Positivo para añadir, negativo para restar
}
```

### Eliminar Subasta
```http
DELETE /api/auctions/{auction_id}
```

## 🔌 WebSocket

Los overlays se conectan automáticamente vía WebSocket para recibir actualizaciones en tiempo real:

```javascript
ws://localhost:8000/ws/auction/{auction_id}
```

### Mensajes que se reciben:

**Datos Iniciales:**
```json
{
  "type": "initial_data",
  "auctionId": "550e8400-...",
  "data": {
    "nameStreamer": "santiago",
    "tituloSubasta": "Subasta online",
    "status": "active",
    "remainingSeconds": 300
  }
}
```

**Actualización de Tiempo:**
```json
{
  "type": "time_update",
  "auctionId": "550e8400-...",
  "data": {
    "remainingSeconds": 240
  }
}
```

**Cambio de Estado:**
```json
{
  "type": "status_change",
  "auctionId": "550e8400-...",
  "data": {
    "status": "paused"
  }
}
```

## 🏗️ Arquitectura del Proyecto

```
TiktokCraft/
├── main.py                          # Aplicación FastAPI principal
├── requirements.txt                 # Dependencias
├── overlays/                        # Archivos HTML de overlays
│   └── auction/
│       └── index.html              # Overlay de subasta
└── src/
    ├── modules/                     # Módulos de overlays
    │   └── auction/                 # Módulo de subasta
    │       ├── domain/              # Lógica de negocio
    │       │   └── auction.py      # Entidad Auction
    │       ├── application/         # Casos de uso
    │       │   ├── dtos.py         # Data Transfer Objects
    │       │   └── service.py      # AuctionService
    │       └── infrastructure/      # Implementaciones técnicas
    │           ├── repository.py   # Persistencia
    │           └── controller.py   # API REST endpoints
    └── shared/                      # Código compartido
        └── websocket_manager.py    # Gestor WebSocket
```

### Diseño Modular

El proyecto está diseñado para **escalar fácilmente**. Para añadir un nuevo tipo de overlay:

1. Crear nuevo módulo en `src/modules/nuevo_overlay/`
2. Implementar `domain/`, `application/`, `infrastructure/`
3. Crear el archivo HTML en `overlays/nuevo_overlay/`
4. Registrar las rutas en `main.py`

**Ejemplo:** Para añadir un overlay de "Top Donadores":

```
src/modules/top_donors/
├── domain/
│   └── top_donor.py
├── application/
│   ├── dtos.py
│   └── service.py
└── infrastructure/
    ├── repository.py
    └── controller.py
```

## 🎨 Personalización del Overlay

El overlay está en `overlays/auction/index.html` y puedes personalizarlo:

- **Colores**: Modifica los gradientes y colores en el CSS
- **Fuentes**: Cambia las familias tipográficas
- **Animaciones**: Ajusta las animaciones y transiciones
- **Layout**: Reorganiza los elementos según tu diseño

## 🔧 Configuración Avanzada

### Cambiar Puerto

En `main.py`, última línea:

```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Cambia el puerto aquí
```

### Configurar URL Base

Si vas a exponer el servidor públicamente (con ngrok, por ejemplo):

```python
# En main.py, línea ~40
auction_service = AuctionService(
    auction_repository, 
    base_url="https://tu-dominio.ngrok.io"  # Cambiar aquí
)
```

### Persistencia en Base de Datos

Actualmente usa almacenamiento en memoria. Para usar base de datos:

1. Implementa un nuevo `AuctionRepository` en `infrastructure/repository.py`
2. Usa SQLAlchemy, MongoDB, o cualquier ORM
3. Inyecta el nuevo repositorio en `main.py`

## 📚 Documentación API Interactiva

Una vez iniciado el servidor, accede a:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🐛 Solución de Problemas

### Error: "Port already in use"
Otro proceso está usando el puerto 8000. Cámbialo en `main.py` o detén el proceso:

```powershell
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### WebSocket no conecta
- Verifica que el servidor esté corriendo
- Revisa la consola del navegador para errores
- Asegúrate de que no haya firewall bloqueando

### Overlay no se ve en TikTok Live Studio
- Verifica que la URL sea accesible desde tu navegador
- Si usas localhost, asegúrate de que TikTok Live Studio esté en la misma máquina
- Para acceso remoto, usa ngrok o similar

## 🚀 Producción

### Despliegue en Dokploy (Recomendado)

TiktokCraft está listo para desplegarse en **Dokploy** con un solo click.

**Guía completa:** Ver [DEPLOY_DOKPLOY.md](DEPLOY_DOKPLOY.md)

**Pasos rápidos:**

1. Sube el código a Git (GitHub/GitLab)
2. Crea una app en Dokploy conectada a tu repositorio
3. Configura variables de entorno:
   ```
   BASE_URL=https://tiktokcraft.tu-dominio.com
   ENVIRONMENT=production
   PORT=8000
   ```
4. Despliega!

El proyecto incluye:
- ✅ `Dockerfile` optimizado
- ✅ `docker-compose.yml` para orquestación
- ✅ `.dockerignore` para builds eficientes
- ✅ Variables de entorno configurables

### Con Docker (Local o Servidor)

```bash
# Build de la imagen
docker build -t tiktokcraft .

# Ejecutar contenedor
docker run -d \
  -p 8000:8000 \
  -e BASE_URL=http://tu-servidor:8000 \
  -e ENVIRONMENT=production \
  --name tiktokcraft \
  tiktokcraft
```

### Con Docker Compose

```bash
# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# Iniciar servicios
docker-compose up -d
```

### Con Gunicorn (Linux)

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🤝 Contribuir

Este proyecto está diseñado para ser extensible. Algunas ideas para contribuir:

- Nuevos tipos de overlays (top donadores, alertas, encuestas)
- Temas y estilos personalizables
- Integración con servicios de donaciones
- Dashboard mejorado con gráficos
- Autenticación y multi-usuario

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 👨‍💻 Autor

Creado con ❤️ para la comunidad de streamers de TikTok

---

**¿Necesitas ayuda?** Abre un issue en el repositorio o contacta al desarrollador.

**¿Te gusta el proyecto?** ⭐ Dale una estrella al repositorio!
