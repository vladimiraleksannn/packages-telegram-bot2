import os
import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from flask import Flask, request, jsonify

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Используем переменную окружения для токена
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN не установлен!")
    exit(1)

# Создаем Flask приложение
app = Flask(__name__)

# Создаем приложение Telegram
application = Application.builder().token(BOT_TOKEN).build()

# База данных пакетов
PACKAGES = [
    # Пример с одним пакетом
    (250, 350, 90, "Пакет верт. д250 ш90 в350 / с ручками / Штамп 1158", "https://disk.360.yandex.ru/d/Peyk8BPpIlnZhA"),
    # Добавьте остальные пакеты по аналогии...
]

def get_package_type(description):
    if "верт." in description.lower():
        return "вертикальный"
    elif "гор." in description.lower():
        return "горизонтальный"
    elif "кв." in description.lower():
        return "квадратный"
    else:
        return "неизвестный"

def get_requested_type(length, height, width):
    if length > height:
        return "горизонтальный"
    elif height > length:
        return "вертикальный"
    else:
        return "квадратный"

def find_matching_packages_by_type(length, height, width, package_type, max_results=5):
    all_matching = []
    
    for pkg_length, pkg_height, pkg_width, desc, _ in PACKAGES:
        current_type = get_package_type(desc)
        if current_type != package_type:
            continue
            
        if (abs(pkg_length - length) <= 50 and 
            abs(pkg_height - height) <= 50 and 
            abs(pkg_width - width) <= 50):
            
            total_diff = (abs(pkg_length - length) + 
                         abs(pkg_height - height) + 
                         abs(pkg_width - width))
            
            all_matching.append((pkg_length, pkg_height, pkg_width, desc, total_diff))
    
    all_matching.sort(key=lambda x: x[4])
    return [(l, h, w, d) for l, h, w, d, _ in all_matching[:max_results]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = """
👋 Привет! Я бот для поиска пакетов.

📦 Отправьте мне размер пакета в формате:
   <b>длина высота ширина</b>
   
Например: <code>200 250 100</code>

❗ <b>Порядок размеров:</b> длина × высота × ширина

Я найду ближайшие пакеты (отклонение до 50 мм).
    """
    await update.message.reply_html(welcome_text)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        text = update.message.text.strip()
        logger.info(f"Получено сообщение: {text}")
        
        cleaned_text = re.sub(r'[^\d\s]', ' ', text)
        numbers = re.findall(r'\d+', cleaned_text)
        
        logger.info(f"Найдены числа: {numbers}")
        
        if len(numbers) < 3:
            await update.message.reply_html(
                "❌ Введите три числа: <b>длина высота ширина</b>\n"
                "Например: <code>200 250 100</code>"
            )
            return

        length, height, width = map(int, numbers[:3])
        logger.info(f"Распознаны размеры: {length}×{height}×{width}")
        
        requested_type = get_requested_type(length, height, width)
        
        context.user_data['original_sizes'] = (length, height, width)
        context.user_data['original_type'] = requested_type
        
        await show_search_results(update, context, length, height, width, requested_type)
        
    except Exception as e:
        logger.error(f"Error in handle_text: {e}")
        await update.message.reply_html(
            "❌ Ошибка. Введите размеры в формате: <code>длина высота ширина</code>\n"
            "Например: <code>400 300 150</code>"
        )

async def show_search_results(update, context, length, height, width, search_type, is_alternative=False):
    try:
        context.user_data['current_sizes'] = (length, height, width)
        context.user_data['current_type'] = search_type
        
        matching_packages = find_matching_packages_by_type(length, height, width, search_type, max_results=5)
        
        if search_type == "вертикальный":
            type_display = "вертикальные"
        elif search_type == "горизонтальный":
            type_display = "горизонтальные"
        else:
            type_display = "квадратные"
        
        if is_alternative:
            response = f"📦 <b>{type_display.capitalize()} пакеты</b> для {length}×{height}×{width} мм (д×в×ш):\n\n"
        else:
            response = f"📦 <b>{type_display.capitalize()} пакеты</b> для {length}×{height}×{width} мм (д×в×ш, отклонение ±50 мм):\n\n"
        
        if matching_packages:
            keyboard = []
            
            for i, (l, h, w, d) in enumerate(matching_packages, 1):
                response += f"😊 {i}. {l} × {h} × {w} мм\n   {d}\n\n"
                callback_data = f"package_{l}_{h}_{w}"
                keyboard.append([InlineKeyboardButton(f"📦 Пакет {i}: {l}×{h}×{w} мм", callback_data=callback_data)])
            
            alt_length, alt_height = height, length
            
            if search_type == "горизонтальный":
                alt_type_display = "вертикальные"
                alt_type = "вертикальный"
            else:
                alt_type_display = "горизонтальные"
                alt_type = "горизонтальный"
            
            alt_callback = f"alternative_{alt_length}_{alt_height}_{width}_{alt_type}"
            keyboard.append([InlineKeyboardButton(f"🔍 Показать {alt_type_display}", callback_data=alt_callback)])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if hasattr(update, 'message'):
                await update.message.reply_html(response, reply_markup=reply_markup)
            else:
                await update.edit_message_text(text=response, parse_mode='HTML', reply_markup=reply_markup)
        else:
            response += "❌ Пакеты не найдены\n\n"
            
            alt_length, alt_height = height, length
            
            if search_type == "горизонтальный":
                alt_type_display = "вертикальные"
                alt_type = "вертикальный"
            else:
                alt_type_display = "горизонтальные"
                alt_type = "горизонтальный"
            
            keyboard = [[InlineKeyboardButton(f"🔍 Показать {alt_type_display}", callback_data=f"alternative_{alt_length}_{alt_height}_{width}_{alt_type}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if hasattr(update, 'message'):
                await update.message.reply_html(response, reply_markup=reply_markup)
            else:
                await update.edit_message_text(text=response, parse_mode='HTML', reply_markup=reply_markup)
                
    except Exception as e:
        logger.error(f"Error in show_search_results: {e}")
        error_msg = "❌ Произошла ошибка при поиске пакетов. Попробуйте еще раз."
        if hasattr(update, 'message'):
            await update.message.reply_html(error_msg)
        else:
            await update.edit_message_text(text=error_msg, parse_mode='HTML')

# Регистрируем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CallbackQueryHandler(handle_package_click, pattern="^package_"))
application.add_handler(CallbackQueryHandler(handle_alternative_search, pattern="^alternative_"))
application.add_handler(CallbackQueryHandler(handle_back_to_last_search, pattern="^back_to_last_search$"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Async endpoint для webhook запросов от Telegram"""
    try:
        # Получаем JSON данные из запроса
        json_data = request.get_json()
        logger.info(f"Received webhook: {json_data}")
        
        # Создаем Update объект из полученных данных
        update = Update.de_json(json_data, application.bot)
        
        # Обрабатываем обновление через приложение
        await application.process_update(update)
        
        return jsonify({"status": "ok"})
        
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

@app.route('/')
def home():
    return "Telegram Bot is running!"

# Запуск бота
async def main():
    """Основная асинхронная функция"""
    # Инициализируем приложение
    await application.initialize()
    await application.start()
    
    # Настраиваем webhook
    render_external_url = os.getenv('RENDER_EXTERNAL_URL')
    if render_external_url:
        webhook_url = f"{render_external_url}/webhook"
        await application.bot.delete_webhook()
        await application.bot.set_webhook(
            url=webhook_url,
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
        logger.info(f"✅ Webhook установлен: {webhook_url}")
    else:
        logger.warning("❌ RENDER_EXTERNAL_URL не установлен")
    
    logger.info("🤖 Бот запущен и готов к работе!")
    
    # Запускаем Flask
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Запуск сервера на порту {port}")
    
    # Не используем app.run() в production, Render сам запустит gunicorn
    if __name__ == "__main__":
        app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
