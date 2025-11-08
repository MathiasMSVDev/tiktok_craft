# 🚀 Guía de Uso Rápido - TiktokCraft

Esta guía te mostrará paso a paso cómo iniciar una subasta y mostrar el overlay en TikTok Live Studio.

---

## 📋 Requisitos Previos

1. **Python 3.11+** instalado
2. **Dependencias instaladas**:
   ```powershell
   pip install -r requirements.txt
   ```
3. **Cuenta de TikTok** con transmisiones en vivo activas

---

## 🎯 Paso 1: Iniciar el Servidor

### Opción A: Usando Python directamente
```powershell
python main.py
```

### Opción B: Usando el script de inicio (PowerShell)
```powershell
.\start.ps1
```

**Salida esperada:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

El servidor estará disponible en: **http://localhost:8000**

---

## 🎪 Paso 2: Crear una Subasta (Estado DRAFT)

### Opción A: Usando el Panel de Administración Web

1. Abre tu navegador en: **http://localhost:8000/admin**
2. Completa el formulario "Crear Nueva Subasta":
   - **Nombre del Streamer**: Tu username de TikTok (sin @)
   - **Título de la Subasta**: Ej: "Subasta de Skins"
   - **Duración**: Tiempo en minutos (ej: 5, 10, 300)
3. Haz clic en **"Crear Subasta"**
4. La subasta se creará en estado **DRAFT** (borrador)
5. Verás la URL del overlay pero **aún no estará conectada a TikTok Live**

### Opción B: Usando cURL (API REST)

```powershell
curl -X POST "http://localhost:8000/api/auctions" `
  -H "Content-Type: application/json" `
  -d '{
    "nameStreamer": "tu_usuario_tiktok",
    "timer": 300,
    "tituloSubasta": "Subasta de Premios"
  }'
```

**Respuesta exitosa:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nameStreamer": "tu_usuario_tiktok",
  "tituloSubasta": "Subasta de Premios",
  "timerMinutes": 300,
  "status": "draft",
  "overlayUrl": "http://localhost:8000/overlay/auction/550e8400-e29b-41d4-a716-446655440000",
  "createdAt": "2025-11-07T10:30:00",
  "startedAt": null,
  "remainingSeconds": null
}
```

📌 **IMPORTANTE**: 
- El `id` se genera automáticamente (GUID único)
- La subasta está en estado **"draft"** - puedes editarla antes de iniciarla
- Guarda la `overlayUrl` para agregarla a TikTok Live Studio

---

## ✏️ Paso 2.5: Actualizar la Subasta (OPCIONAL)

Antes de iniciar la subasta, puedes modificar sus datos:

### Usando cURL:
```powershell
curl -X PUT "http://localhost:8000/api/auctions/550e8400-e29b-41d4-a716-446655440000" `
  -H "Content-Type: application/json" `
  -d '{
    "tituloSubasta": "Subasta MODIFICADA",
    "timer": 600
  }'
```

**Campos opcionales:**
- `tituloSubasta`: Cambiar el título
- `nameStreamer`: Cambiar el nombre del streamer
- `timer`: Cambiar la duración (en minutos)

⚠️ **Solo funciona en estado DRAFT** - una vez iniciada, no se puede actualizar así.

---

## 🎨 Paso 3: Agregar el Overlay a TikTok Live Studio

### 3.1 Abrir TikTok Live Studio
1. Abre **TikTok Live Studio** en tu computadora
2. Inicia sesión con tu cuenta de TikTok

### 3.2 Agregar Browser Source
1. En el panel de **Fuentes** (Sources), haz clic en el botón **➕**
2. Selecciona **"Browser Source"** o **"Navegador"**
3. Dale un nombre, por ejemplo: **"Subasta"**

### 3.3 Configurar el Browser Source
1. En el campo **URL**, pega la URL del overlay que obtuviste:
   ```
   http://localhost:8000/overlay/auction/subasta-001
   ```

2. **Configuración recomendada**:
   - **Width (Ancho)**: 1920
   - **Height (Alto)**: 1080
   - **FPS**: 30
   - ✅ Activar: "Shutdown source when not visible"
   - ✅ Activar: "Refresh browser when scene becomes active"

3. Haz clic en **"OK"** o **"Aceptar"**

### 3.4 Ajustar Posición y Tamaño
1. El overlay aparecerá en tu escena
2. Puedes **redimensionar** y **mover** el overlay arrastrándolo
3. **Posiciones recomendadas**:
   - **Esquina superior derecha**: Para mostrar el timer
   - **Centro superior**: Para destacar el título
   - **Lateral derecho**: Para el top de donadores

---

## 🎮 Paso 4: Iniciar la Subasta

Una vez creada la subasta en estado DRAFT y agregado el overlay a TikTok Live Studio, es momento de iniciarla:

### Usando cURL:
```powershell
curl -X POST "http://localhost:8000/api/auctions/550e8400-e29b-41d4-a716-446655440000/start"
```

**Respuesta exitosa:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "message": "Subasta iniciada correctamente",
  "startedAt": "2025-11-07T10:35:00"
}
```

**¿Qué sucede al iniciar?**
1. ✅ El estado cambia de **DRAFT** → **ACTIVE**
2. ✅ Se conecta automáticamente a **TikTok Live** del streamer
3. ✅ Comienza la cuenta regresiva del timer
4. ✅ El overlay se activa en pantalla
5. ✅ Empieza a capturar donaciones en tiempo real

---

## 🎮 Paso 5: Controlar la Subasta en Tiempo Real

### Usando el Panel de Administración Web

1. Ve a: **http://localhost:8000/admin**
2. Verás tu subasta activa con controles:

**Controles disponibles:**
- ⏸ **Pausar**: Pausa el temporizador
- ▶ **Reanudar**: Continúa desde donde se pausó
- ⏹ **Detener**: Finaliza la subasta y desconecta de TikTok Live
- ➕ **+1 min**: Agrega 60 segundos al timer
- ➖ **-1 min**: Resta 60 segundos al timer
- 🗑 **Eliminar**: Elimina la subasta

### Usando API REST

#### Pausar la subasta
```powershell
curl -X POST "http://localhost:8000/api/auctions/550e8400-e29b-41d4-a716-446655440000/pause"
```

#### Reanudar la subasta
```powershell
curl -X POST "http://localhost:8000/api/auctions/550e8400-e29b-41d4-a716-446655440000/resume"
```

#### Agregar 2 minutos (120 segundos)
```powershell
curl -X PATCH "http://localhost:8000/api/auctions/550e8400-e29b-41d4-a716-446655440000/time" `
  -H "Content-Type: application/json" `
  -d '{"seconds": 120}'
```

#### Restar 30 segundos
```powershell
curl -X PATCH "http://localhost:8000/api/auctions/550e8400-e29b-41d4-a716-446655440000/time" `
  -H "Content-Type: application/json" `
  -d '{"seconds": -30}'
```

#### Detener la subasta
```powershell
curl -X POST "http://localhost:8000/api/auctions/550e8400-e29b-41d4-a716-446655440000/stop"
```

⚠️ **Al detener**: El sistema se desconecta automáticamente de TikTok Live.

---

## 🏆 Paso 5: Visualizar Top de Donadores

El overlay muestra automáticamente el **TOP 5 de donadores** cuando los usuarios envían regalos durante tu transmisión en vivo.

### Cómo funciona:
1. **Conexión automática**: Al **iniciar** la subasta (POST /start), el sistema se conecta a tu stream de TikTok Live
2. **Captura de regalos**: Cada vez que alguien envía un regalo, se registra automáticamente
3. **Acumulación**: Las donaciones se acumulan por usuario
4. **Ranking en tiempo real**: El overlay muestra el top 5 actualizado al instante

### Ver estadísticas de donadores

#### Desde el navegador:
```
http://localhost:8000/api/auctions/550e8400-e29b-41d4-a716-446655440000/top-donors
```

#### Con cURL:
```powershell
curl -X GET "http://localhost:8000/api/auctions/550e8400-e29b-41d4-a716-446655440000/top-donors"
```

**Respuesta:**
```json
{
  "auctionId": "550e8400-e29b-41d4-a716-446655440000",
  "topDonors": [
    {
      "username": "usuario1",
      "totalAmount": 5000.0,
      "donationCount": 10,
      "lastDonation": "2025-11-07T10:35:00",
      "rank": 1
    },
    {
      "username": "usuario2",
      "totalAmount": 3500.0,
      "donationCount": 7,
      "lastDonation": "2025-11-07T10:34:00",
      "rank": 2
    }
  ],
  "totalDonations": 15000.0,
  "totalDonors": 25
}
```

---

## 📊 Paso 6: Monitorear el Estado

### Ver todas las subastas activas
```powershell
curl -X GET "http://localhost:8000/api/auctions"
```

### Ver detalles de una subasta específica
```powershell
curl -X GET "http://localhost:8000/api/auctions/550e8400-e29b-41d4-a716-446655440000"
```

### Panel de administración
Visita: **http://localhost:8000/admin**
- Visualización en tiempo real de todas las subastas
- Temporizadores actualizados cada segundo
- Controles rápidos para cada subasta

---

## 🎭 Elementos del Overlay

El overlay muestra los siguientes elementos en tiempo real:

### 1. **Header**
- Nombre del streamer
- Título de la subasta

### 2. **Temporizador**
- Cuenta regresiva en formato MM:SS
- Cambia de color según el tiempo restante:
  - **Blanco**: > 30 segundos
  - **Amarillo** (pulsante): 11-30 segundos
  - **Rojo** (pulsante rápido): ≤ 10 segundos

### 3. **Estado de la Subasta**
- 🟢 **EN VIVO**: Subasta activa
- 🟠 **PAUSADA**: Temporalmente detenida
- ⚪ **FINALIZADA**: Completada por tiempo
- 🔴 **DETENIDA**: Detenida manualmente

### 4. **Top Donadores**
- 🏆 TOP 5 de donadores
- Muestra username, total de coins y número de donaciones
- Rankings visuales (#1, #2, #3, #4, #5)
- Actualización en tiempo real con animaciones

### 5. **Indicador de Conexión**
- 🟢 **Conectado**: WebSocket activo
- 🔴 **Desconectado**: Sin conexión (intenta reconectar automáticamente)

---

## 🔧 Solución de Problemas

### ❌ Problema: El overlay no se muestra
**Solución:**
1. Verifica que el servidor esté corriendo en `http://localhost:8000`
2. Asegúrate de que la URL del overlay sea correcta
3. Revisa que el Browser Source tenga las dimensiones correctas (1920x1080)
4. Refresca el Browser Source en TikTok Live Studio

### ❌ Problema: El temporizador no se actualiza
**Solución:**
1. Verifica el indicador de conexión (debe estar verde 🟢)
2. Revisa la consola del servidor para errores de WebSocket
3. Refresca el overlay (F5 en el Browser Source)

### ❌ Problema: No se muestran las donaciones
**Solución:**
1. Asegúrate de que el **nombre del streamer** sea correcto (sin @)
2. Verifica que tu cuenta de TikTok esté en transmisión en vivo
3. Revisa los logs del servidor para ver si hay errores de conexión a TikTok Live
4. Verifica que TikTokLive esté instalado: `pip install "TikTokLive>=1.0.11"`

### ❌ Problema: Error al crear subasta
**Solución:**
1. Verifica que el timer esté entre 1 y 1440 minutos
2. Asegúrate de que el ID de la subasta sea único
3. Revisa los logs del servidor para ver el error específico

---

## 📝 Flujo Completo de Ejemplo

```powershell
# 1. Iniciar el servidor
python main.py

# 2. Crear una subasta de 5 minutos (estado DRAFT)
curl -X POST "http://localhost:8000/api/auctions" `
  -H "Content-Type: application/json" `
  -d '{
    "nameStreamer": "mi_usuario",
    "timer": 5,
    "tituloSubasta": "Subasta Especial"
  }'

# Respuesta: id generado automáticamente
# {
#   "id": "550e8400-e29b-41d4-a716-446655440000",
#   "status": "draft",
#   "overlayUrl": "http://localhost:8000/overlay/auction/550e8400-e29b-41d4-a716-446655440000"
# }

# 3. (OPCIONAL) Actualizar la subasta antes de iniciarla
curl -X PUT "http://localhost:8000/api/auctions/550e8400-e29b-41d4-a716-446655440000" `
  -H "Content-Type: application/json" `
  -d '{
    "tituloSubasta": "Subasta MODIFICADA",
    "timer": 10
  }'

# 4. Copiar la overlayUrl de la respuesta y agregarla a TikTok Live Studio
# Ejemplo: http://localhost:8000/overlay/auction/550e8400-e29b-41d4-a716-446655440000

# 5. Iniciar la subasta (conecta con TikTok Live)
curl -X POST "http://localhost:8000/api/auctions/550e8400-e29b-41d4-a716-446655440000/start"

# 6. Controlar la subasta desde el panel de admin
# http://localhost:8000/admin

# 7. Ver donaciones en tiempo real
curl -X GET "http://localhost:8000/api/auctions/550e8400-e29b-41d4-a716-446655440000/top-donors"

# 8. Cuando termine, detener la subasta (desconecta de TikTok)
curl -X POST "http://localhost:8000/api/auctions/550e8400-e29b-41d4-a716-446655440000/stop"

# 9. (OPCIONAL) Eliminar la subasta
curl -X DELETE "http://localhost:8000/api/auctions/550e8400-e29b-41d4-a716-446655440000"
```

---

## 🔄 Estados de la Subasta

La subasta pasa por diferentes estados durante su ciclo de vida:

1. **DRAFT** (Borrador)
   - ✏️ Se puede editar (título, streamer, timer)
   - ❌ NO conectada a TikTok Live
   - ❌ NO captura donaciones
   - ✅ Overlay disponible pero inactivo

2. **ACTIVE** (Activa)
   - ✅ Conectada a TikTok Live
   - ✅ Captura donaciones en tiempo real
   - ✅ Timer en cuenta regresiva
   - ⏸ Se puede pausar/reanudar

3. **PAUSED** (Pausada)
   - ✅ Aún conectada a TikTok Live
   - ✅ Sigue capturando donaciones
   - ⏸ Timer detenido temporalmente
   - ▶ Se puede reanudar

4. **COMPLETED** (Completada)
   - ⏰ Timer llegó a 0
   - 🔌 Desconectada de TikTok Live
   - 🔒 Estado final (no reversible)

5. **STOPPED** (Detenida)
   - ⏹ Detenida manualmente
   - 🔌 Desconectada de TikTok Live
   - 🔒 Estado final (no reversible)

---

## 🎯 Consejos Avanzados

### 1. **Flujo Recomendado**
```
CREAR (DRAFT) → EDITAR (si es necesario) → AGREGAR OVERLAY → INICIAR → CONTROLAR → DETENER
```

### 2. **Múltiples Subastas Simultáneas**
Puedes tener varias subastas activas al mismo tiempo con diferentes streamers:
```powershell
# Subasta 1
curl -X POST "http://localhost:8000/api/auctions" -H "Content-Type: application/json" -d '{"nameStreamer": "usuario1", "timer": 10, "tituloSubasta": "Subasta 1"}'

# Subasta 2
curl -X POST "http://localhost:8000/api/auctions" -H "Content-Type: application/json" -d '{"nameStreamer": "usuario2", "timer": 15, "tituloSubasta": "Subasta 2"}'
```

### 3. **Editar Antes de Iniciar**
Aprovecha el estado DRAFT para hacer ajustes sin tener que recrear la subasta:
```powershell
# Crear
curl -X POST "http://localhost:8000/api/auctions" -H "Content-Type: application/json" -d '{"nameStreamer": "user1", "timer": 5, "tituloSubasta": "Test"}'

# Cambiar de opinión - actualizar
curl -X PUT "http://localhost:8000/api/auctions/[ID]" -H "Content-Type: application/json" -d '{"timer": 10, "tituloSubasta": "Subasta Real"}'

# Ahora sí, iniciar
curl -X POST "http://localhost:8000/api/auctions/[ID]/start"
```

### 4. **Cambiar Entre Subastas**
Simplemente cambia la URL del Browser Source para alternar entre overlays.

### 5. **Personalizar Duración en Vivo**
Puedes agregar o restar tiempo mientras la subasta está activa:
```powershell
# Agregar 5 minutos (300 segundos)
curl -X PATCH "http://localhost:8000/api/auctions/[ID]/time" -H "Content-Type: application/json" -d '{"seconds": 300}'
```

### 6. **Guardar la URL del Overlay**
Una vez creada la subasta, la URL del overlay no cambia. Puedes:
- Crear la subasta (DRAFT)
- Configurar el overlay en TikTok Live Studio
- Iniciar cuando estés listo para el stream

### 7. **Reutilización de Subastas**
Una vez que una subasta está en estado COMPLETED o STOPPED, no se puede reiniciar. Debes crear una nueva:
```powershell
# Eliminar la anterior
curl -X DELETE "http://localhost:8000/api/auctions/[ID_VIEJO]"

# Crear una nueva
curl -X POST "http://localhost:8000/api/auctions" -H "Content-Type: application/json" -d '{"nameStreamer": "user1", "timer": 10, "tituloSubasta": "Nueva Subasta"}'
```

---

## 📚 Recursos Adicionales

- **Documentación API**: http://localhost:8000/docs
- **Panel de Administración**: http://localhost:8000/admin
- **Página Principal**: http://localhost:8000

---

## ⚙️ Variables de Entorno (Opcional)

Para configuración avanzada, crea un archivo `.env`:

```env
# URL base del servidor
BASE_URL=http://localhost:8000

# Orígenes CORS permitidos
CORS_ORIGINS=*

# Entorno de ejecución
ENVIRONMENT=development

# Puerto del servidor
PORT=8000

# Nivel de logs
LOG_LEVEL=info
```

---

## 🎉 ¡Listo!

Ahora tienes todo configurado para usar subastas con overlays en TikTok Live Studio, con seguimiento de donaciones en tiempo real y control total desde el panel de administración.

**¿Necesitas ayuda?** Revisa la sección de solución de problemas o consulta los logs del servidor.
