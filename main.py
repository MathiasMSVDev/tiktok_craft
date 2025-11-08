"""
Aplicación principal FastAPI - TiktokCraft
Sistema modular de overlays para TikTok Live Studio
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import asyncio
import os
from typing import Optional

# Importar módulos
from src.modules.auction.application.service import AuctionService
from src.modules.auction.infrastructure.repository import AuctionRepository
from src.modules.auction.infrastructure.controller import AuctionController
from src.shared.websocket_manager import websocket_manager
from src.shared.tiktok_connector import tiktok_connector


# Configuración desde variables de entorno
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Crear aplicación
app = FastAPI(
    title="TiktokCraft",
    description="Sistema modular de overlays para TikTok Live Studio",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar directorio de overlays
overlays_dir = Path(__file__).parent / "overlays"
app.mount("/static", StaticFiles(directory=str(overlays_dir)), name="static")

# Inicializar servicios y controladores
auction_repository = AuctionRepository()
auction_service = AuctionService(auction_repository, tiktok_connector, base_url=BASE_URL)
auction_service.set_websocket_manager(websocket_manager)
auction_controller = AuctionController(auction_service)

# Registrar rutas del módulo de subastas
app.include_router(auction_controller.router)


# Ruta raíz - Dashboard
@app.get("/", response_class=HTMLResponse)
async def root():
    """Página de inicio con información del sistema"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TiktokCraft - Sistema de Overlays</title>
        <meta charset="utf-8">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 800px;
                width: 100%;
                padding: 40px;
            }
            h1 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            .section {
                margin: 30px 0;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            .section h2 {
                color: #333;
                margin-bottom: 15px;
                font-size: 1.5em;
            }
            .endpoint {
                background: white;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border: 1px solid #ddd;
            }
            .method {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 0.85em;
                margin-right: 10px;
            }
            .method.post { background: #49cc90; color: white; }
            .method.get { background: #61affe; color: white; }
            .method.patch { background: #fca130; color: white; }
            .method.delete { background: #f93e3e; color: white; }
            .path {
                font-family: 'Courier New', monospace;
                color: #333;
                font-weight: 500;
            }
            .description {
                color: #666;
                margin-top: 8px;
                font-size: 0.95em;
            }
            .btn {
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 12px 30px;
                border-radius: 8px;
                text-decoration: none;
                margin: 10px 10px 10px 0;
                transition: all 0.3s;
                font-weight: 500;
            }
            .btn:hover {
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            .feature {
                background: white;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                border: 2px solid #667eea;
            }
            .feature-icon {
                font-size: 2em;
                margin-bottom: 10px;
            }
            .feature-title {
                color: #333;
                font-weight: 600;
                margin-bottom: 5px;
            }
            .feature-desc {
                color: #666;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 TiktokCraft</h1>
            <p class="subtitle">Sistema modular de overlays para TikTok Live Studio</p>
            
            <div class="section">
                <h2>✨ Características</h2>
                <div class="features">
                    <div class="feature">
                        <div class="feature-icon">⚡</div>
                        <div class="feature-title">Tiempo Real</div>
                        <div class="feature-desc">WebSocket para control instantáneo</div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🎨</div>
                        <div class="feature-title">Modular</div>
                        <div class="feature-desc">Arquitectura escalable</div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🔧</div>
                        <div class="feature-title">API REST</div>
                        <div class="feature-desc">Control total vía endpoints</div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">📱</div>
                        <div class="feature-title">Responsive</div>
                        <div class="feature-desc">Overlays adaptativos</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>📡 Endpoints Disponibles</h2>
                
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <span class="path">/api/auctions</span>
                    <div class="description">Crear una nueva subasta y obtener el enlace del overlay</div>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="path">/api/auctions</span>
                    <div class="description">Listar todas las subastas</div>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="path">/api/auctions/{id}</span>
                    <div class="description">Obtener detalles de una subasta</div>
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <span class="path">/api/auctions/{id}/control</span>
                    <div class="description">Controlar subasta (start, pause, resume, stop)</div>
                </div>
                
                <div class="endpoint">
                    <span class="method patch">PATCH</span>
                    <span class="path">/api/auctions/{id}/time</span>
                    <div class="description">Modificar tiempo de la subasta</div>
                </div>
                
                <div class="endpoint">
                    <span class="method delete">DELETE</span>
                    <span class="path">/api/auctions/{id}</span>
                    <div class="description">Eliminar una subasta</div>
                </div>
            </div>
            
            <div style="margin-top: 30px; text-align: center;">
                <a href="/docs" class="btn">📚 Ver Documentación API</a>
                <a href="/admin" class="btn">🎛️ Panel de Control</a>
            </div>
        </div>
    </body>
    </html>
    """


# Ruta del overlay de subasta
@app.get("/overlay/auction/{auction_id}", response_class=HTMLResponse)
async def auction_overlay(auction_id: str):
    """Devuelve el overlay de subasta para un ID específico"""
    # Verificar que la subasta existe
    auction = auction_service.get_auction(auction_id)
    if not auction:
        return HTMLResponse(
            content="<h1>Subasta no encontrada</h1>",
            status_code=404
        )
    
    # Devolver el HTML del overlay
    overlay_path = overlays_dir / "auction" / "index.html"
    if overlay_path.exists():
        with open(overlay_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        return HTMLResponse(
            content="<h1>Overlay no encontrado</h1>",
            status_code=404
        )


# WebSocket para comunicación en tiempo real
@app.websocket("/ws/auction/{auction_id}")
async def websocket_endpoint(websocket: WebSocket, auction_id: str):
    """
    WebSocket endpoint para recibir actualizaciones en tiempo real de una subasta
    """
    await websocket_manager.connect(websocket, auction_id)
    
    # Enviar datos iniciales de la subasta
    auction = auction_service.get_auction(auction_id)
    if auction:
        await websocket_manager.send_personal_message({
            "type": "initial_data",
            "auctionId": auction_id,
            "data": {
                "nameStreamer": auction.nameStreamer,
                "tituloSubasta": auction.tituloSubasta,
                "status": auction.status,
                "remainingSeconds": auction.remainingSeconds,
                "timerMinutes": auction.timerMinutes
            }
        }, websocket)
    
    try:
        # Mantener la conexión abierta y gestionar el timer
        while True:
            # Verificar el estado de la subasta cada segundo
            auction = auction_service.get_auction(auction_id)
            
            if auction and auction.status == "active" and auction.remainingSeconds is not None:
                if auction.remainingSeconds > 0:
                    # Decrementar el tiempo
                    new_time = auction.remainingSeconds - 1
                    auction_service.update_remaining_time(auction_id, new_time)
                    
                    # Broadcast a todos los clientes
                    await websocket_manager.broadcast_time_update(auction_id, new_time)
                    
                    # Si el tiempo llegó a 0, marcar como completada
                    if new_time == 0:
                        await websocket_manager.broadcast_status_change(auction_id, "completed")
                        
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, auction_id)
    except Exception as e:
        print(f"Error en WebSocket: {e}")
        websocket_manager.disconnect(websocket, auction_id)


# Panel de administración
@app.get("/admin", response_class=HTMLResponse)
async def admin_panel():
    """Panel de administración web para gestionar subastas"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TiktokCraft - Panel de Administración</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f5f6fa;
                padding: 20px;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 15px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .header h1 {
                margin-bottom: 10px;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            .grid {
                display: grid;
                grid-template-columns: 1fr 2fr;
                gap: 20px;
                margin-bottom: 20px;
            }
            .panel {
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .panel h2 {
                color: #667eea;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #f0f0f0;
            }
            .form-group {
                margin-bottom: 20px;
            }
            .form-group label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 500;
            }
            .form-group input {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                transition: border-color 0.3s;
            }
            .form-group input:focus {
                outline: none;
                border-color: #667eea;
            }
            .btn {
                background: #667eea;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                transition: all 0.3s;
                width: 100%;
            }
            .btn:hover {
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            .btn-small {
                padding: 8px 15px;
                font-size: 12px;
                width: auto;
                margin: 0 5px;
            }
            .btn-danger { background: #f93e3e; }
            .btn-danger:hover { background: #e02d2d; }
            .btn-warning { background: #fca130; }
            .btn-warning:hover { background: #e89020; }
            .btn-success { background: #49cc90; }
            .btn-success:hover { background: #38b57d; }
            .auction-list {
                margin-top: 20px;
            }
            .auction-item {
                background: #f8f9fa;
                padding: 20px;
                margin-bottom: 15px;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            .auction-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }
            .auction-title {
                font-weight: 600;
                color: #333;
                font-size: 1.1em;
            }
            .auction-status {
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: 600;
            }
            .status-active { background: #49cc90; color: white; }
            .status-paused { background: #fca130; color: white; }
            .status-pending { background: #61affe; color: white; }
            .status-completed { background: #999; color: white; }
            .status-stopped { background: #f93e3e; color: white; }
            .auction-info {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 10px;
                margin-bottom: 15px;
            }
            .info-item {
                font-size: 0.9em;
                color: #666;
            }
            .info-label {
                font-weight: 600;
                color: #333;
            }
            .auction-controls {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }
            .overlay-link {
                background: white;
                padding: 10px;
                border-radius: 6px;
                border: 1px solid #ddd;
                margin-top: 10px;
                word-break: break-all;
                font-family: monospace;
                font-size: 0.85em;
            }
            .timer-display {
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
                text-align: center;
                margin: 10px 0;
            }
            .alert {
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            .alert-success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .alert-error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎛️ Panel de Administración</h1>
                <p>Gestiona y controla tus subastas en tiempo real</p>
            </div>
            
            <div id="alert" style="display: none;"></div>
            
            <div class="grid">
                <div class="panel">
                    <h2>➕ Crear Nueva Subasta</h2>
                    <form id="createForm">
                        <div class="form-group">
                            <label>Nombre del Streamer</label>
                            <input type="text" id="nameStreamer" required placeholder="Ej: santiago">
                        </div>
                        <div class="form-group">
                            <label>Título de la Subasta</label>
                            <input type="text" id="tituloSubasta" required placeholder="Ej: Subasta online">
                        </div>
                        <div class="form-group">
                            <label>Duración (minutos)</label>
                            <input type="number" id="timer" min="1" max="120" required placeholder="Ej: 5">
                        </div>
                        <button type="submit" class="btn">Crear Subasta</button>
                    </form>
                </div>
                
                <div class="panel">
                    <h2>📋 Subastas Activas</h2>
                    <div id="auctionsList" class="auction-list">
                        <p style="text-align: center; color: #999;">Cargando subastas...</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let auctions = [];
            
            // Cargar subastas
            async function loadAuctions() {
                try {
                    const response = await fetch('/api/auctions');
                    auctions = await response.json();
                    renderAuctions();
                } catch (error) {
                    showAlert('Error al cargar subastas', 'error');
                }
            }
            
            // Renderizar lista de subastas
            function renderAuctions() {
                const container = document.getElementById('auctionsList');
                
                if (auctions.length === 0) {
                    container.innerHTML = '<p style="text-align: center; color: #999;">No hay subastas creadas</p>';
                    return;
                }
                
                container.innerHTML = auctions.map(auction => `
                    <div class="auction-item">
                        <div class="auction-header">
                            <div class="auction-title">${auction.tituloSubasta}</div>
                            <div class="auction-status status-${auction.status}">${auction.status.toUpperCase()}</div>
                        </div>
                        <div class="auction-info">
                            <div class="info-item">
                                <span class="info-label">Streamer:</span> ${auction.nameStreamer}
                            </div>
                            <div class="info-item">
                                <span class="info-label">Duración:</span> ${auction.timerMinutes} min
                            </div>
                            <div class="info-item">
                                <span class="info-label">ID:</span> ${auction.id.substring(0, 8)}...
                            </div>
                        </div>
                        ${auction.remainingSeconds !== null ? `
                            <div class="timer-display">
                                ${Math.floor(auction.remainingSeconds / 60)}:${String(auction.remainingSeconds % 60).padStart(2, '0')}
                            </div>
                        ` : ''}
                        <div class="auction-controls">
                            ${auction.status === 'active' ? `
                                <button class="btn btn-small btn-warning" onclick="controlAuction('${auction.id}', 'pause')">⏸ Pausar</button>
                                <button class="btn btn-small btn-danger" onclick="controlAuction('${auction.id}', 'stop')">⏹ Detener</button>
                                <button class="btn btn-small btn-success" onclick="addTime('${auction.id}', 60)">➕ 1 min</button>
                                <button class="btn btn-small btn-danger" onclick="addTime('${auction.id}', -60)">➖ 1 min</button>
                            ` : ''}
                            ${auction.status === 'paused' ? `
                                <button class="btn btn-small btn-success" onclick="controlAuction('${auction.id}', 'resume')">▶ Reanudar</button>
                                <button class="btn btn-small btn-danger" onclick="controlAuction('${auction.id}', 'stop')">⏹ Detener</button>
                            ` : ''}
                            ${auction.status === 'pending' ? `
                                <button class="btn btn-small btn-success" onclick="controlAuction('${auction.id}', 'start')">▶ Iniciar</button>
                            ` : ''}
                            <button class="btn btn-small btn-danger" onclick="deleteAuction('${auction.id}')">🗑 Eliminar</button>
                        </div>
                        <div class="overlay-link">
                            <strong>Overlay URL:</strong> ${auction.overlayUrl}
                        </div>
                    </div>
                `).join('');
            }
            
            // Crear subasta
            document.getElementById('createForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const data = {
                    nameStreamer: document.getElementById('nameStreamer').value,
                    tituloSubasta: document.getElementById('tituloSubasta').value,
                    timer: parseInt(document.getElementById('timer').value)
                };
                
                try {
                    const response = await fetch('/api/auctions', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    
                    if (response.ok) {
                        showAlert('Subasta creada exitosamente', 'success');
                        document.getElementById('createForm').reset();
                        await loadAuctions();
                    } else {
                        const error = await response.json();
                        showAlert(error.detail || 'Error al crear subasta', 'error');
                    }
                } catch (error) {
                    showAlert('Error de conexión', 'error');
                }
            });
            
            // Controlar subasta
            async function controlAuction(id, action) {
                try {
                    const response = await fetch(`/api/auctions/${id}/control`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ action })
                    });
                    
                    if (response.ok) {
                        showAlert(`Acción "${action}" ejecutada`, 'success');
                        await loadAuctions();
                    } else {
                        const error = await response.json();
                        showAlert(error.detail || 'Error al ejecutar acción', 'error');
                    }
                } catch (error) {
                    showAlert('Error de conexión', 'error');
                }
            }
            
            // Modificar tiempo
            async function addTime(id, seconds) {
                try {
                    const response = await fetch(`/api/auctions/${id}/time`, {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ seconds })
                    });
                    
                    if (response.ok) {
                        showAlert(`Tiempo ${seconds > 0 ? 'añadido' : 'restado'}`, 'success');
                        await loadAuctions();
                    } else {
                        const error = await response.json();
                        showAlert(error.detail || 'Error al modificar tiempo', 'error');
                    }
                } catch (error) {
                    showAlert('Error de conexión', 'error');
                }
            }
            
            // Eliminar subasta
            async function deleteAuction(id) {
                if (!confirm('¿Estás seguro de eliminar esta subasta?')) return;
                
                try {
                    const response = await fetch(`/api/auctions/${id}`, {
                        method: 'DELETE'
                    });
                    
                    if (response.ok) {
                        showAlert('Subasta eliminada', 'success');
                        await loadAuctions();
                    } else {
                        showAlert('Error al eliminar subasta', 'error');
                    }
                } catch (error) {
                    showAlert('Error de conexión', 'error');
                }
            }
            
            // Mostrar alerta
            function showAlert(message, type) {
                const alert = document.getElementById('alert');
                alert.className = `alert alert-${type}`;
                alert.textContent = message;
                alert.style.display = 'block';
                
                setTimeout(() => {
                    alert.style.display = 'none';
                }, 3000);
            }
            
            // Cargar subastas al inicio y cada 5 segundos
            loadAuctions();
            setInterval(loadAuctions, 5000);
if __name__ == "__main__":
    import uvicorn
    
    # Obtener configuración desde variables de entorno
    port = int(os.getenv("PORT", 8000))
    workers = int(os.getenv("WORKERS", 1))
    log_level = os.getenv("LOG_LEVEL", "info")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level=log_level
    )
    """


if __name__ == "__main__":
    import uvicorn
    
    # Obtener configuración desde variables de entorno
    port = int(os.getenv("PORT", 8000))
    log_level = os.getenv("LOG_LEVEL", "info")
    
    # Cleanup handler para desconectar de TikTok Live al cerrar
    import signal
    import sys
    
    def cleanup_handler(signum, frame):
        """Limpieza al cerrar la aplicación"""
        print("\n🛑 Cerrando aplicación...")
        import asyncio
        asyncio.run(tiktok_connector.disconnect_all())
        print("✅ Desconectado de TikTok Live")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, cleanup_handler)
    signal.signal(signal.SIGTERM, cleanup_handler)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level=log_level
    )
