import telebot
import time
import os

TOKEN = "8736887321:AAGwDSwToesQckd_Q4noE6vLi252_gsGk18"
bot = telebot.TeleBot(TOKEN)

suscripciones = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if suscripciones.get(user_id, {}).get("activo", False):
        bot.send_message(user_id, "❌ Ya estás suscrito.")
        return

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("⭐ Comprar por 10 Stars", callback_data="comprar"))
    bot.send_message(user_id, "🔥 Suscríbete a Yeiks VPN Premium:\n\n💰 Precio: 10 Stars (pago único).", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "comprar")
def handle_comprar(call):
    user_id = call.from_user.id
    try:
        bot.send_invoice(
            chat_id=user_id,
            title="Yeiks VPN Premium",
            description="Suscripción mensual a Yeiks VPN.",
            payload="suscripcion_mensual",
            provider_token="",
            currency="XTR",
            prices=[{"label": "Suscripción", "amount": 10}],
            start_parameter="test"
        )
    except Exception as e:
        bot.send_message(user_id, f"❌ Error: {e}")

@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_pre_checkout(query):
    try:
        bot.answer_pre_checkout_query(query.id, ok=True)
    except Exception as e:
        bot.answer_pre_checkout_query(query.id, ok=False, error_message=f"Error: {e}")

@bot.message_handler(content_types=['successful_payment'])
def handle_payment(message):
    user_id = message.from_user.id
    suscripciones[user_id] = {"activo": True}
    bot.send_message(user_id, "✅ ¡Suscripción activada! 🎉")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
