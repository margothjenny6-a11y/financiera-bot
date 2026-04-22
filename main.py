import os
import asyncio
import time
import threading
from telegram import Bot
from config import TOKEN
from server import app
from bot import correr_bot

async def limpiar_sesion():
    bot = Bot(token=TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    print("[OK] Sesion de Telegram limpiada")

asyncio.run(limpiar_sesion())
asyncio.set_event_loop(asyncio.new_event_loop())   # ← agregar esta línea
time.sleep(3)


port = int(os.environ.get("PORT", 5000))

hilo_servidor = threading.Thread(
    target=lambda: app.run(host="0.0.0.0", port=port)
)
hilo_servidor.daemon = True
hilo_servidor.start()

print(f"[OK] Servidor corriendo en puerto {port}")
print("[OK] Bot de Telegram activo, esperando solicitudes...")
correr_bot()
