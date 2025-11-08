# 🚀 TiktokCraft - Quick Deploy en Dokploy

## ⚡ Despliegue Rápido (5 minutos)

### 1️⃣ Preparar Repositorio

```bash
git init
git add .
git commit -m "Deploy TiktokCraft to Dokploy"
git remote add origin https://github.com/tu-usuario/tiktokcraft.git
git push -u origin main
```

### 2️⃣ Crear App en Dokploy

1. **New Application** → Deploy from Git
2. **Repository:** Tu repo de GitHub/GitLab
3. **Build Type:** Dockerfile
4. **Branch:** main

### 3️⃣ Variables de Entorno

Añade en Dokploy (Environment Variables):

```env
BASE_URL=https://tiktokcraft.tu-dominio.dokploy.com
ENVIRONMENT=production
PORT=8000
```

### 4️⃣ Deploy

Click en **Deploy** y espera 2-3 minutos.

### 5️⃣ Verificar

Abre: `https://tu-url.dokploy.com/admin`

---

## ✅ URLs Importantes

| Recurso | URL |
|---------|-----|
| Panel Admin | `/admin` |
| API Docs | `/docs` |
| Health Check | `/api/auctions` |

---

## 📝 Checklist

- [ ] Código en Git
- [ ] App creada en Dokploy
- [ ] Variables de entorno configuradas
- [ ] BASE_URL apunta a dominio público
- [ ] Build exitoso
- [ ] App running
- [ ] `/admin` accesible
- [ ] Crear subasta de prueba funciona

---

## 🔧 Variables de Entorno Completas

```env
# Esenciales
BASE_URL=https://tiktokcraft.tu-dominio.com
ENVIRONMENT=production
PORT=8000

# Opcionales
CORS_ORIGINS=*
WORKERS=4
LOG_LEVEL=info
```

---

## 🐛 Solución Rápida de Problemas

**Build falla:**
- Verifica que `Dockerfile` esté en el repo
- Revisa logs de build en Dokploy

**App no inicia:**
- Verifica que `BASE_URL` esté configurada
- Revisa logs de la app

**WebSocket no funciona:**
- Asegúrate de usar `https://` en BASE_URL
- Verifica CORS_ORIGINS

---

## 📚 Documentación Completa

Ver [DEPLOY_DOKPLOY.md](DEPLOY_DOKPLOY.md) para guía detallada.

---

**¡Listo en 5 minutos!** 🎉
