import os
from server import app
from bot import iniciar_bot

port = int(os.environ.get("PORT", 5000))
WEBHOOK_URL = "https://blissful-connection-production-a81d.up.railway.app/webhook"

iniciar_bot(WEBHOOK_URL)

print(f"[OK] Servidor corriendo en puerto {port}")
print("[OK] Bot de Telegram activo")
app.run(host="0.0.0.0", port=port)

