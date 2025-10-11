from flask import Flask, request, jsonify
import threading
import asyncio
import logging
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask('')

@app.route('/')
def home():
    return "Telegram Bot is running!"

@app.route('/health')
def health():
    return "OK"

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Endpoint для webhook запросов от Telegram"""
    try:
        from bot import webhook_handler
        return await webhook_handler(request)
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/set_webhook', methods=['GET'])
async def set_webhook():
    """Ручная установка webhook (для отладки)"""
    try:
        from telegram import Bot
        
        bot_token = os.getenv('BOT_TOKEN')
        render_external_url = os.getenv('RENDER_EXTERNAL_URL')
        
        if not bot_token or not render_external_url:
            return "❌ BOT_TOKEN или RENDER_EXTERNAL_URL не установлены"
        
        bot = Bot(token=bot_token)
        webhook_url = f"{render_external_url}/webhook"
        
        # Удаляем старый webhook и устанавливаем новый
        await bot.delete_webhook()
        result = await bot.set_webhook(
            url=webhook_url,
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
        
        return f"✅ Webhook установлен: {webhook_url}<br>Результат: {result}"
        
    except Exception as e:
        return f"❌ Ошибка установки webhook: {e}"

def run():
    """Запускает Flask сервер"""
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Запускает веб-сервер в отдельном потоке"""
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()
    logger.info("🌐 Веб-сервер запущен на порту 8080")
