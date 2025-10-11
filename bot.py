import os
import logging
import re
import asyncio
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

# Создаем Flask приложение для webhook
app = Flask(__name__)

# Глобальная переменная для приложения
application = None

# База данных пакетов с ссылками на чертежи
PACKAGES = [
    # Вертикальные пакеты с первого скрина
    (250, 350, 90, "Пакет верт. д250 ш90 в350 / с ручками / Штамп 1158", "https://disk.360.yandex.ru/d/Peyk8BPpIlnZhA"),
    (100, 120, 90, "Пакет верт. д100 ш90 в120 / Штамп 512", "https://disk.360.yandex.ru/d/3-yN-eN1W8_oFA"),
    # ... (остальные пакеты остаются без изменений)
    (220, 220, 120, "Пакет д220 ш120 в220 / отверстия под ленты / Штамп 846", "https://disk.360.yandex.ru/d/P2TtXuwkP1MpAQ"),
]

def get_package_type(description):
    """Определяет тип пакета по описанию"""
    if "верт." in description.lower():
        return "вертикальный"
    elif "гор." in description.lower():
        return "горизонтальный"
    elif "кв." in description.lower():
        return "квадратный"
    else:
        return "неизвестный"

def get_requested_type(length, height, width):
    """Определяет тип запрашиваемого пакета"""
    if length > height:
        return "горизонтальный"
    elif height > length:
        return "вертикальный"
    else:
        return "квадратный"

def find_matching_packages_by_type(length, height, width, package_type, max_results=5):
    """Находит пакеты определенного типа, соответствующие размерам с допуском 50мм"""
    all_matching = []
    
    for pkg_length, pkg_height, pkg_width, desc, _ in PACKAGES:
        # Проверяем тип пакета
        current_type = get_package_type(desc)
        if current_type != package_type:
            continue
            
        # Проверяем соответствие размеров с допуском 50мм
        if (abs(pkg_length - length) <= 50 and 
            abs(pkg_height - height) <= 50 and 
            abs(pkg_width - width) <= 50):
            
            # Вычисляем общее отклонение для сортировки
            total_diff = (abs(pkg_length - length) + 
                         abs(pkg_height - height) + 
                         abs(pkg_width - width))
            
            all_matching.append((pkg_length, pkg_height, pkg_width, desc, total_diff))
    
    # Сортируем по общему отклонению
    all_matching.sort(key=lambda x: x[4])
    
    return [(l, h, w, d) for l, h, w, d, _ in all_matching[:max_results]]

def get_package_details(length, height, width, description):
    """Возвращает детали пакета для отображения при клике"""
    # Находим пакет в базе данных
    drawing_url = None
    for pkg_length, pkg_height, pkg_width, desc, url in PACKAGES:
        if (pkg_length == length and pkg_height == height and 
            pkg_width == width and desc == description):
            drawing_url = url
            break
    
    if drawing_url:
        details = (
            "📋 <b>Детали пакета</b>\n\n"
            f"📦 Размер: {length} × {height} × {width} мм\n"
            f"📝 Описание: {description}\n\n"
            "🔗 <b>Ссылка на чертеж:</b>\n"
            f"{drawing_url}"
        )
    else:
        details = (
            "📋 <b>Детали пакета</b>\n\n"
            f"📦 Размер: {length} × {height} × {width} мм\n"
            f"📝 Описание: {description}\n\n"
            "⏳ <i>Информация о номере заказа-шаблона и ссылка на чертеж скоро появятся</i>"
        )
    
    return details, drawing_url

async def create_application():
    """Создает и настраивает приложение"""
    global application
    if application is None:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Регистрируем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CallbackQueryHandler(handle_package_click, pattern="^package_"))
        application.add_handler(CallbackQueryHandler(handle_alternative_search, pattern="^alternative_"))
        application.add_handler(CallbackQueryHandler(handle_back_to_last_search, pattern="^back_to_last_search$"))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        # Инициализируем приложение
        await application.initialize()
        await application.start()
    
    return application

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
    """Обрабатывает все текстовые сообщения"""
    try:
        text = update.message.text.strip()
        logger.info(f"Получено сообщение: {text}")
        
        # Убираем все лишние символы и оставляем только цифры и пробелы
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
        
        # Сохраняем оригинальные размеры и тип
        context.user_data['original_sizes'] = (length, height, width)
        context.user_data['original_type'] = requested_type
        
        # Вызываем функцию для отображения результатов
        await show_search_results(update, context, length, height, width, requested_type)
        
    except Exception as e:
        logger.error(f"Error in handle_text: {e}")
        await update.message.reply_html(
            "❌ Ошибка. Введите размеры в формате: <code>длина высота ширина</code>\n"
            "Например: <code>400 300 150</code>"
        )

async def show_search_results(update, context, length, height, width, search_type, is_alternative=False):
    """Показывает результаты поиска с кнопками"""
    try:
        # Сохраняем текущий контекст
        context.user_data['current_sizes'] = (length, height, width)
        context.user_data['current_type'] = search_type
        
        # Находим пакеты для запрошенного типа
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
            # Создаем inline клавиатуру для каждого пакета
            keyboard = []
            
            for i, (l, h, w, d) in enumerate(matching_packages, 1):
                response += f"😊 {i}. {l} × {h} × {w} мм\n   {d}\n\n"
                # Создаем callback_data в формате: package_L_H_W
                callback_data = f"package_{l}_{h}_{w}"
                keyboard.append([InlineKeyboardButton(f"📦 Пакет {i}: {l}×{h}×{w} мм", callback_data=callback_data)])
            
            # Определяем альтернативный тип для кнопки
            alt_length, alt_height = height, length  # Меняем местами длину и высоту
            
            if search_type == "горизонтальный":
                alt_type_display = "вертикальные"
                alt_type = "вертикальный"
            else:
                alt_type_display = "горизонтальные"
                alt_type = "горизонтальный"
            
            # Добавляем кнопку для альтернативного поиска
            alt_callback = f"alternative_{alt_length}_{alt_height}_{width}_{alt_type}"
            keyboard.append([InlineKeyboardButton(f"🔍 Показать {alt_type_display}", callback_data=alt_callback)])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if hasattr(update, 'message'):
                await update.message.reply_html(response, reply_markup=reply_markup)
            else:
                await update.edit_message_text(text=response, parse_mode='HTML', reply_markup=reply_markup)
        else:
            response += "❌ Пакеты не найдены\n\n"
            
            # Определяем альтернативный тип для кнопки
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

async def handle_package_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает клик по пакету"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Извлекаем данные из callback_data
        callback_data = query.data
        
        if callback_data.startswith("package_"):
            # Формат: package_L_H_W
            parts = callback_data.split("_")
            if len(parts) == 4:
                length = int(parts[1])
                height = int(parts[2])
                width = int(parts[3])
                
                # Находим описание пакета в базе данных
                description = ""
                for pkg_length, pkg_height, pkg_width, desc, _ in PACKAGES:
                    if pkg_length == length and pkg_height == height and pkg_width == width:
                        description = desc
                        break
                
                # Получаем детали пакета и ссылку
                details, drawing_url = get_package_details(length, height, width, description)
                
                # Создаем клавиатуру с кнопками "Назад" и "Скопировать ссылку" (если есть ссылка)
                keyboard = []
                
                # Кнопка "Назад" - возвращаемся к текущему результату поиска
                current_sizes = context.user_data.get('current_sizes', (0, 0, 0))
                current_type = context.user_data.get('current_type', 'горизонтальный')
                
                if current_type == "вертикальный":
                    back_text = "⬅️ Назад к вертикальным"
                else:
                    back_text = "⬅️ Назад к горизонтальным"
                    
                # Сохраняем данные для возврата
                context.user_data['last_search_sizes'] = current_sizes
                context.user_data['last_search_type'] = current_type
                
                keyboard.append([InlineKeyboardButton(back_text, callback_data="back_to_last_search")])
                
                # Кнопка "Скопировать ссылку" если есть ссылка
                if drawing_url:
                    keyboard.append([InlineKeyboardButton("📋 Скопировать ссылку", url=drawing_url)])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text=details,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
    except Exception as e:
        logger.error(f"Error in handle_package_click: {e}")

async def handle_alternative_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает запрос на альтернативный поиск"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Формат: alternative_L_H_W_type
        parts = query.data.split("_")
        if len(parts) == 5:
            length = int(parts[1])
            height = int(parts[2])
            width = int(parts[3])
            search_type = parts[4]  # "вертикальный" или "горизонтальный"
            
            # Показываем результаты альтернативного поиска
            await show_search_results(query, context, length, height, width, search_type, is_alternative=True)
    except Exception as e:
        logger.error(f"Error in handle_alternative_search: {e}")

async def handle_back_to_last_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает возврат к последнему результату поиска из деталей пакета"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Получаем сохраненные данные о последнем поиска
        last_sizes = context.user_data.get('last_search_sizes')
        last_type = context.user_data.get('last_search_type')
        
        if last_sizes and last_type:
            length, height, width = last_sizes
            # Определяем, был ли это альтернативный поиск
            is_alternative = (last_sizes != context.user_data.get('original_sizes', last_sizes))
            
            # Показываем результаты поиска
            await show_search_results(query, context, length, height, width, last_type, is_alternative=is_alternative)
        else:
            # Если данных нет, возвращаем к началу
            await query.edit_message_text(
                text="❌ Не удалось вернуться к результатам поиска. Введите новые размеры.",
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Error in handle_back_to_last_search: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html("""
📋 <b>Как пользоваться ботом:</b>

1️⃣ Отправьте размер пакета: <code>длина высота ширина</code>  
2️⃣ Порядок важен — длина × высота × ширина  
3️⃣ Бот подберёт ближайшие пакеты (±50 мм)
4️⃣ Нажмите на любой пакет, чтобы увидеть детали
5️⃣ Используйте кнопки для навигации и альтернативного поиска

<b>Примеры:</b>  
<code>200 250 100</code>  
<code>300 400 150</code>  
<code>400 300 150</code>

Бот автоматически определит тип пакета и предложит альтернативные варианты!
    """)

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Async endpoint для webhook запросов от Telegram"""
    try:
        # Получаем JSON данные из запроса
        json_data = request.get_json()
        
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
    return "OK"

@app.route('/')
def home():
    return "Telegram Bot is running!"

async def setup_webhook():
    """Настраивает webhook при запуске"""
    global application
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(handle_package_click, pattern="^package_"))
    application.add_handler(CallbackQueryHandler(handle_alternative_search, pattern="^alternative_"))
    application.add_handler(CallbackQueryHandler(handle_back_to_last_search, pattern="^back_to_last_search$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Инициализируем и запускаем приложение
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
        logger.warning("❌ RENDER_EXTERNAL_URL не установлен, webhook не настроен")

def run_bot():
    """Запускает бота синхронно"""
    # Запускаем настройку webhook
    asyncio.run(setup_webhook())
    
    # Запускаем Flask приложение
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Запуск бота на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    run_bot()
