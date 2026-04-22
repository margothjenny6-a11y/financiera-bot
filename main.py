import os
import threading
from server import app
from bot import correr_bot

port = int(os.environ.get("PORT", 5000))

hilo_servidor = threading.Thread(
    target=lambda: app.run(host="0.0.0.0", port=port)
)
hilo_servidor.daemon = True
hilo_servidor.start()

print(f"[OK] Servidor corriendo en puerto {port}")
print("[OK] Bot de Telegram activo, esperando solicitudes...")
correr_bot()

