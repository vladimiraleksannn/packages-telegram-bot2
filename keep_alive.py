from flask import Flask, request, jsonify
import logging

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
def webhook():
    """Endpoint для webhook запросов от Telegram"""
    try:
        from bot import webhook_handler
        
        # Получаем JSON данные из запроса
        json_data = request.get_json()
        
        # Обрабатываем обновление
        result = webhook_handler(json_data)
        return result
        
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Ручная установка webhook (для отладки)"""
    try:
        import os
        from telegram import Bot
        import asyncio
        
        bot_token = os.getenv('BOT_TOKEN')
        render_external_url = os.getenv('RENDER_EXTERNAL_URL')
        
        if not bot_token or not render_external_url:
            return "❌ BOT_TOKEN или RENDER_EXTERNAL_URL не установлены"
        
        # Создаем новое событийное loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        bot = Bot(token=bot_token)
        webhook_url = f"{render_external_url}/webhook"
        
        # Удаляем старый webhook и устанавливаем новый
        loop.run_until_complete(bot.delete_webhook())
        result = loop.run_until_complete(bot.set_webhook(
            url=webhook_url,
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        ))
        
        loop.close()
        
        return f"✅ Webhook установлен: {webhook_url}<br>Результат: {result}"
        
    except Exception as e:
        return f"❌ Ошибка установки webhook: {e}"

def run():
    """Запускает Flask сервер"""
    app.run(host='0.0.0.0', port=8080, debug=False)

def keep_alive():
    """Запускает веб-сервер в отдельном потоке"""
    import threading
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()
    logger.info("🌐 Веб-сервер запущен на порту 8080")
