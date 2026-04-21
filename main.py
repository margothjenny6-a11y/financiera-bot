import threading
from server import app
from bot import correr_bot

hilo_servidor = threading.Thread(
    target=lambda: app.run(port=5000)
)
hilo_servidor.daemon = True
hilo_servidor.start()

print("[OK] Servidor corriendo en http://localhost:5000")
print("[OK] Bot de Telegram activo, esperando solicitudes...")
correr_bot()
