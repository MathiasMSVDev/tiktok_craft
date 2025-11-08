"""
Script de prueba para verificar el funcionamiento de TiktokCraft
Ejecuta este script después de iniciar el servidor con: python main.py
"""
import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def print_separator():
    print("\n" + "="*60 + "\n")

def test_server_connection():
    """Test 1: Verificar conexión al servidor"""
    print("🔍 Test 1: Verificando conexión al servidor...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Servidor accesible")
            return True
        else:
            print(f"❌ Error: Código {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("   Asegúrate de que el servidor esté corriendo con: python main.py")
        return False

def test_create_auction():
    """Test 2: Crear una subasta"""
    print("🔍 Test 2: Creando subasta de prueba...")
    
    data = {
        "nameStreamer": "TestStreamer",
        "timer": 2,
        "tituloSubasta": "Subasta de Prueba"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auctions", json=data)
        
        if response.status_code == 201:
            auction = response.json()
            print("✅ Subasta creada exitosamente")
            print(f"   ID: {auction['id']}")
            print(f"   Estado: {auction['status']}")
            print(f"   Overlay URL: {auction['overlayUrl']}")
            return auction['id']
        else:
            print(f"❌ Error al crear subasta: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return None

def test_get_auction(auction_id):
    """Test 3: Obtener información de la subasta"""
    print("🔍 Test 3: Obteniendo información de la subasta...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/auctions/{auction_id}")
        
        if response.status_code == 200:
            auction = response.json()
            print("✅ Información obtenida correctamente")
            print(f"   Título: {auction['tituloSubasta']}")
            print(f"   Streamer: {auction['nameStreamer']}")
            print(f"   Estado: {auction['status']}")
            print(f"   Tiempo restante: {auction['remainingSeconds']} segundos")
            return True
        else:
            print(f"❌ Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def test_pause_auction(auction_id):
    """Test 4: Pausar la subasta"""
    print("🔍 Test 4: Pausando subasta...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auctions/{auction_id}/control",
            json={"action": "pause"}
        )
        
        if response.status_code == 200:
            auction = response.json()
            print(f"✅ Subasta pausada - Estado: {auction['status']}")
            return True
        else:
            print(f"❌ Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def test_add_time(auction_id):
    """Test 5: Añadir tiempo a la subasta"""
    print("🔍 Test 5: Añadiendo 60 segundos...")
    
    try:
        response = requests.patch(
            f"{BASE_URL}/api/auctions/{auction_id}/time",
            json={"seconds": 60}
        )
        
        if response.status_code == 200:
            auction = response.json()
            print(f"✅ Tiempo añadido - Tiempo restante: {auction['remainingSeconds']} segundos")
            return True
        else:
            print(f"❌ Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def test_resume_auction(auction_id):
    """Test 6: Reanudar la subasta"""
    print("🔍 Test 6: Reanudando subasta...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auctions/{auction_id}/control",
            json={"action": "resume"}
        )
        
        if response.status_code == 200:
            auction = response.json()
            print(f"✅ Subasta reanudada - Estado: {auction['status']}")
            return True
        else:
            print(f"❌ Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def test_list_auctions():
    """Test 7: Listar todas las subastas"""
    print("🔍 Test 7: Listando todas las subastas...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/auctions")
        
        if response.status_code == 200:
            auctions = response.json()
            print(f"✅ {len(auctions)} subasta(s) encontrada(s)")
            for auction in auctions:
                print(f"   - {auction['tituloSubasta']} ({auction['status']})")
            return True
        else:
            print(f"❌ Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def test_stop_auction(auction_id):
    """Test 8: Detener la subasta"""
    print("🔍 Test 8: Deteniendo subasta...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auctions/{auction_id}/control",
            json={"action": "stop"}
        )
        
        if response.status_code == 200:
            auction = response.json()
            print(f"✅ Subasta detenida - Estado: {auction['status']}")
            return True
        else:
            print(f"❌ Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def test_delete_auction(auction_id):
    """Test 9: Eliminar la subasta"""
    print("🔍 Test 9: Eliminando subasta...")
    
    try:
        response = requests.delete(f"{BASE_URL}/api/auctions/{auction_id}")
        
        if response.status_code == 204:
            print("✅ Subasta eliminada correctamente")
            return True
        else:
            print(f"❌ Error al eliminar")
            return False
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def test_api_docs():
    """Test 10: Verificar documentación API"""
    print("🔍 Test 10: Verificando documentación API...")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        
        if response.status_code == 200:
            print("✅ Documentación API accesible")
            print(f"   URL: {BASE_URL}/docs")
            return True
        else:
            print(f"❌ Error: Código {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "="*60)
    print("🎯 TiktokCraft - Suite de Pruebas")
    print("="*60)
    
    results = []
    auction_id = None
    
    # Test 1: Conexión
    print_separator()
    results.append(test_server_connection())
    
    if not results[0]:
        print("\n❌ No se puede continuar sin conexión al servidor")
        return
    
    # Test 2: Crear subasta
    print_separator()
    auction_id = test_create_auction()
    results.append(auction_id is not None)
    
    if not auction_id:
        print("\n❌ No se puede continuar sin crear una subasta")
        return
    
    # Esperar un momento
    print("\n⏳ Esperando 2 segundos...")
    time.sleep(2)
    
    # Test 3: Obtener subasta
    print_separator()
    results.append(test_get_auction(auction_id))
    
    # Test 4: Pausar
    print_separator()
    results.append(test_pause_auction(auction_id))
    
    # Test 5: Añadir tiempo
    print_separator()
    results.append(test_add_time(auction_id))
    
    # Test 6: Reanudar
    print_separator()
    results.append(test_resume_auction(auction_id))
    
    # Test 7: Listar
    print_separator()
    results.append(test_list_auctions())
    
    # Test 8: Detener
    print_separator()
    results.append(test_stop_auction(auction_id))
    
    # Test 9: Eliminar
    print_separator()
    results.append(test_delete_auction(auction_id))
    
    # Test 10: Docs
    print_separator()
    results.append(test_api_docs())
    
    # Resumen
    print_separator()
    passed = sum(results)
    total = len(results)
    
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    print(f"   Pasadas: {passed}/{total}")
    print(f"   Fallidas: {total - passed}/{total}")
    
    if passed == total:
        print("\n✅ ¡Todas las pruebas pasaron exitosamente!")
        print("\n🎉 TiktokCraft está funcionando correctamente")
        print("\n📱 Próximos pasos:")
        print(f"   1. Panel Admin: {BASE_URL}/admin")
        print(f"   2. API Docs: {BASE_URL}/docs")
        print("   3. Crear subastas y obtener enlaces de overlay")
        print("   4. Integrar overlays en TikTok Live Studio")
    else:
        print("\n❌ Algunas pruebas fallaron")
        print("   Revisa los errores arriba para más detalles")
    
    print_separator()

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⏹️  Pruebas interrumpidas por el usuario")
        sys.exit(0)
