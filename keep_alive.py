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
    """Ручная установка webhook (для отлад
