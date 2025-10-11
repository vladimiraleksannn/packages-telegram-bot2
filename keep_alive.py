from flask import Flask, request, jsonify
import logging
import asyncio
import threading

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
        # Создаем новое событийное loop для асинхронной обработки
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from bot import webhook_handler
        result = loop.run_until_complete(webhook_handler(request))
        loop.close()
        
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
        
       
