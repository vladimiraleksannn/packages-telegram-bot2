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

# Создаем Flask приложение
app = Flask(__name__)

# Создаем приложение Telegram
application = Application.builder().token(BOT_TOKEN).build()

# База данных пакетов
PACKAGES = [
    # Вертикальные пакеты
    (250, 350, 90, "Пакет верт. д250 ш90 в350 / с ручками / Штамп 1158", "https://disk.360.yandex.ru/d/Peyk8BPpIlnZhA"),
    (100, 120, 90, "Пакет верт. д100 ш90 в120 / Штамп 512", "https://disk.360.yandex.ru/d/3-yN-eN1W8_oFA"),
    (110, 360, 100, "Пакет верт. д110 ш100 в360 / дно без нахлеста / Штамп 095", "https://disk.360.yandex.ru/d/VFv4p5Z1Kg76WQ"),
    (110, 320, 90, "Пакет верт. д110 ш90 в320 / Штамп 326", "https://disk.360.yandex.ru/d/RkCLCQjU1lBlhg"),
    (120, 370, 115, "Пакет верт. д120 ш115 в370 / Штамп 1092", "https://disk.360.yandex.ru/d/Q2AR6FSw6B5znA"),
    (120, 400, 115, "Пакет верт. д120 ш115 в400 / Штамп 713", "https://disk.360.yandex.ru/d/GHji0S2f96lCUg"),
    (120, 340, 120, "Пакет верт. д120 ш120 в340 / дно без нахлеста / Штамп 091", "https://disk.360.yandex.ru/d/JwWNUCYVW7dppA"),
    (120, 370, 120, "Пакет верт. д120 ш120 в370 / Шато Тамань / Штамп 718", "https://disk.360.yandex.ru/d/yaGfocdeiWf8-Q"),
    (120, 220, 90, "Пакет верт. д120 ш90 в220 / 2 на листе / Штамп 1079", "https://disk.360.yandex.ru/d/fsfvOIEHDjEGJA"),
    (130, 220, 30, "Пакет верт. д130 ш30 в220 / дно без нахлеста / Штамп 094", "https://disk.360.yandex.ru/d/uk1Jb_USjMgpgA"),
    (140, 160, 60, "Пакет верт. д140 ш60 в160 / с прорезями под ленты / Штамп 619", "https://disk.360.yandex.ru/d/S5RwXnfNWPG0ng"),
    (140, 180, 70, "Пакет верт. д140 ш70 в180 / Штамп 559", "https://disk.360.yandex.ru/d/W-FTwGSHlv2pgw"),
    (170, 260, 40, "Пакет верт. д170 ш40 в260 / Штамп 325", "https://disk.360.yandex.ru/d/mWRLkrx0uTtnOA"),
    (170, 280, 90, "Пакет верт. д170 ш90 в280 / Штамп 042", "https://disk.360.yandex.ru/d/GYTxXr6rdCaOoA"),
    (180, 230, 90, "Пакет верт. д180 ш90 в230 / Штамп 164", "https://disk.360.yandex.ru/d/QvlEFYLggsEAAw"),
    (190, 250, 70, "Пакет верт. д190 ш70 в250 / Штамп 927", "https://disk.360.yandex.ru/d/Ii-ZsU9VPFf1mA"),
    (200, 250, 100, "Пакет верт. д200 ш100 в250 / Штамп 892", "https://disk.360.yandex.ru/d/3kzW0mZl-wk9TA"),
    (200, 250, 100, "Пакет верт. д200 ш100 в250 / с вырубкой ручкой / Штамп 1032", "https://disk.360.yandex.ru/d/oEDrzOgWHlOkXw"),
    (200, 250, 80, "Пакет верт. д200 ш80 в250 / отверстия под ленты/ Штамп 758", "https://disk.360.yandex.ru/d/dLI00bXytUo9cA"),
    (220, 300, 120, "Пакет верт. д220 ш120 в300 / с ручками / Штамп 1046", "https://disk.360.yandex.ru/d/y2yr572Pvv2YPw"),
    (220, 320, 80, "Пакет верт. д220 ш80 в320 / Штамп 093", "https://disk.360.yandex.ru/d/F17zyggakb0LJA"),
    (250, 320, 50, "Пакет верт. д250 ш50 в320 / Половинка пакета Владимир / Штамп 950", "https://disk.360.yandex.ru/d/gm-Si78cmkM9qA"),
    (250, 360, 90, "Пакет верт. д250 ш90 в360 / КАСП средний / Штамп 394", "https://disk.360.yandex.ru/d/viC1RXxAFpOUFw"),
    (250, 380, 90, "Пакет верт. д250 ш90 в380 / Штамп 768", "https://disk.360.yandex.ru/d/1B_qrpgk-23ZqA"),
    (270, 350, 120, "Пакет верт. д270 ш120 в350 / половинка пакета / Штамп 692", "https://disk.360.yandex.ru/d/d0yG6vp6gASvaA"),
    (270, 350, 140, "Пакет верт. д270 ш140 в350 / Половинка пакета Владимир / Штамп 951", "https://disk.360.yandex.ru/d/Tb_ApuI4ul8wgA"),
    (290, 370, 60, "Пакет верт. д290 ш60 в370 / Штамп 908", "https://disk.360.yandex.ru/d/FNU-ltQ5vZKssQ"),
    (300, 400, 120, "Пакет верт. д300 ш120 в400 / половинка пакета / Штамп 655", "https://disk.360.yandex.ru/d/DvRSRcuu_vTVzQ"),
    (300, 460, 120, "Пакет верт. д300 ш120 в460 / половинка пакета / Штамп 097", "https://disk.360.yandex.ru/d/xHRnjFuNSM-rUQ"),
    (300, 350, 135, "Пакет верт. д300 ш135 в350 / половинка пакета / Штамп 570", "https://disk.360.yandex.ru/d/3hAmNimaQ0ofDA"),
    (300, 400, 150, "Пакет верт. д300 ш150 в400 / половинка пакета / Штамп 769", "https://disk.360.yandex.ru/d/EeiPrlgFutVcGw"),
    (340, 480, 150, "Пакет верт. д340 ш150 в480 / половинка пакета / Штамп 772", "https://disk.360.yandex.ru/d/72Rbqxbljdez2A"),
    (350, 450, 100, "Пакет верт. д350 ш100 в450 / половинка пакета / Штамп 478", "https://disk.360.yandex.ru/d/kyEe7JWJl071UQ"),
    
    # Горизонтальные пакеты
    (160, 140, 80, "Пакет гор. д160 ш80 в140 / 3 на листе / Штамп 980", "https://disk.360.yandex.ru/d/_0Qx-vmY5-ImbQ"),
    (220, 180, 125, "Пакет гор. д220 ш125 в180 / отверстия под ленты / Штамп 919", "https://disk.360.yandex.ru/d/CGStQuXiiw4U-g"),
    (230, 180, 90, "Пакет гор. д230 ш90 в180 / Штамп 096", "https://disk.360.yandex.ru/d/BzRmOcxFebIJzg"),
    (248, 230, 108, "Пакет гор. д248 ш108 в230 / Штамп 565", "https://disk.360.yandex.ru/d/tJmxsPZaOTunyw"),
    (280, 220, 100, "Пакет гор. д280 ш100 в220 / Половинка пакета Владимир / Штамп 949", "https://disk.360.yandex.ru/d/w92NUZFaOIpiyw"),
    (280, 240, 70, "Пакет гор. д280 ш70 в240 / Штамп 133", "https://disk.360.yandex.ru/d/74TMziAk6zsEgw"),
    (300, 290, 140, "Пакет гор. д300 ш140 в290 / 1 половина / Штамп 933", "https://disk.360.yandex.ru/d/08q6eprjImYlPg"),
    (335, 165, 75, "Пакет гор. д335 ш75 в165 / 2 половинки на штампе / Штамп 1136", "https://disk.360.yandex.ru/d/NmwI1In9LLPrNw"),
    (300, 240, 130, "Пакет гор. д300 ш130 в240 / половинка пакета / Штамп 316", None),
    (390, 300, 150, "Пакет гор. д390 ш150 в300 / половинка пакета / Штамп 770", "https://disk.360.yandex.ru/d/cTe1E-2zTdVO9g"),
    (400, 250, 120, "Пакет гор. д400 ш120 в250 мм / половинка пакета/Штамп 092", "https://disk.360.yandex.ru/d/c04m8A23_hcR_Q"),
    (400, 300, 120, "Пакет гор. д400 ш120 в300 / половинка пакета / Штамп 430", "https://disk.360.yandex.ru/d/ddmj-2Q7tbjeFg"),
    (400, 300, 150, "Пакет гор. д400 ш150 в300 / половинка пакета / Штамп 531", "https://disk.360.yandex.ru/d/EmxhEKA4-o57Rw"),
    (400, 300, 200, "Пакет гор. д400 ш200 в300 / половинка пакета / Штамп 090", "https://disk.360.yandex.ru/d/-Zf8EzAR8ODk0A"),
    (410, 280, 280, "Пакет гор. д410 ш280 в280 / половинка пакета / Штамп 915", "https://disk.360.yandex.ru/d/yIBD0zOo_tXX9w"),
    (420, 400, 200, "Пакет гор. д420 ш200 в400 / половинка пакета / нужна 'заплатка' на дно / Штамп 508", "https://disk.360.yandex.ru/d/SIdLisRNGL4Kcw"),
    (450, 300, 140, "Пакет гор. д450 ш140 в300 / половинка пакета / Штамп 328", None),
    (460, 390, 150, "Пакет гор. д460 ш150 в390 / половинка пакета / Штамп 914", "https://disk.360.yandex.ru/d/8f-sJ4k69YsoUQ"),
    (480, 340, 140, "Пакет гор. д480 ш140 в340 / половинка пакета / Штамп 771", "https://disk.360.yandex.ru/d/8eOb9ha0yo-9rQ"),
    (490, 390, 73, "Пакет гор. д490 ш73 в390 / половинка пакета / пуансоны под ручки на штампе / Штамп 532", "https://disk.360.yandex.ru/d/rIhAn9GP19JScA"),
    (500, 550, 100, "Пакет гор. д500 ш100 в550 / половинка пакета / Штамп 376", "https://disk.360.yandex.ru/d/2aYmmPwpmkqn5A"),
    (500, 400, 200, "Пакет гор. д500 ш200 в400 / половинка пакета / нужна 'заплатка' на дно / Штамп 533", "https://disk.360.yandex.ru/d/C9We9YAafSvSHw"),
    (530, 340, 170, "Пакет гор. д530 ш170 в340 / половинка пакета / Штамп 379", "https://disk.360.yandex.ru/d/9VchoXrY3U0JPA"),
    
    # Квадратные пакеты
    (150, 150, 80, "Пакет д150 ш80 в150 / Штамп 230", "https://disk.360.yandex.ru/d/C81M3tOCOslx4g"),
    (220, 220, 120, "Пакет д220 ш120 в220 / Штамп 427", "https://disk.360.yandex.ru/d/69V_z4FbsvDiag"),
    (220, 220, 120, "Пакет д220 ш120 в220 / отверстия под ленты / Штамп 846", "https://disk.360.yandex.ru/d/P2TtXuwkP1MpAQ"),
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

def get_package_details(length, height, width, description):
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

async def handle_package_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data.startswith("package_"):
            parts = callback_data.split("_")
            if len(parts) == 4:
                length = int(parts[1])
                height = int(parts[2])
                width = int(parts[3])
                
                description = ""
                for pkg_length, pkg_height, pkg_width, desc, _ in PACKAGES:
                    if pkg_length == length and pkg_height == height and pkg_width == width:
                        description = desc
                        break
                
                details, drawing_url = get_package_details(length, height, width, description)
                
                keyboard = []
                
                current_sizes = context.user_data.get('current_sizes', (0, 0, 0))
                current_type = context.user_data.get('current_type', 'горизонтальный')
                
                if current_type == "вертикальный":
                    back_text = "⬅️ Назад к вертикальным"
                else:
                    back_text = "⬅️ Назад к горизонтальным"
                    
                context.user_data['last_search_sizes'] = current_sizes
                context.user_data['last_search_type'] = current_type
                
                keyboard.append([InlineKeyboardButton(back_text, callback_data="back_to_last_search")])
                
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
    try:
        query = update.callback_query
        await query.answer()
        
        parts = query.data.split("_")
        if len(parts) == 5:
            length = int(parts[1])
            height = int(parts[2])
            width = int(parts[3])
            search_type = parts[4]
            
            await show_search_results(query, context, length, height, width, search_type, is_alternative=True)
    except Exception as e:
        logger.error(f"Error in handle_alternative_search: {e}")

async def handle_back_to_last_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        query = update.callback_query
        await query.answer()
        
        last_sizes = context.user_data.get('last_search_sizes')
        last_type = context.user_data.get('last_search_type')
        
        if last_sizes and last_type:
            length, height, width = last_sizes
            is_alternative = (last_sizes != context.user_data.get('original_sizes', last_sizes))
            
            await show_search_results(query, context, length, height, width, last_type, is_alternative=is_alternative)
        else:
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

# Регистрируем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CallbackQueryHandler(handle_package_click, pattern="^package_"))
application.add_handler(CallbackQueryHandler(handle_alternative_search, pattern="^alternative_"))
application.add_handler(CallbackQueryHandler(handle_back_to_last_search, pattern="^back_to_last_search$"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# Глобальная переменная для хранения задачи
update_task = None

async def process_update_async(update):
    """Асинхронная обработка обновления"""
    try:
        await application.process_update(update)
    except Exception as e:
        logger.error(f"Error processing update: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint для webhook запросов от Telegram"""
    try:
        # Получаем JSON данные из запроса
        json_data = request.get_json()
        logger.info(f"Received webhook: {json_data}")
        
        if json_data is None:
            logger.error("Empty webhook received")
            return jsonify({"status": "error", "message": "Empty data"}), 400
        
        # Создаем Update объект из полученных данных
        update = Update.de_json(json_data, application.bot)
        
        # Запускаем обработку обновления в event loop
        if update_task:
            asyncio.run_coroutine_threadsafe(process_update_async(update), update_task)
        
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

async def setup_webhook():
    """Настройка webhook"""
    render_external_url = os.getenv('RENDER_EXTERNAL_URL')
    if render_external_url:
        webhook_url = f"{render_external_url}/webhook"
        try:
            await application.bot.delete_webhook()
            await application.bot.set_webhook(
                url=webhook_url,
                allowed_updates=["message", "callback_query"],
                drop_pending_updates=True
            )
            logger.info(f"✅ Webhook установлен: {webhook_url}")
        except Exception as e:
            logger.error(f"❌ Ошибка настройки webhook: {e}")
    else:
        logger.warning("❌ RENDER_EXTERNAL_URL не установлен")

async def main():
    """Основная асинхронная функция"""
    global update_task
    update_task = asyncio.get_event_loop()
    
    # Настраиваем webhook
    await setup_webhook()
    
    # Инициализируем приложение
    await application.initialize()
    await application.start()
    
    logger.info("🤖 Бот запущен и готов к работе!")
    
    # Запускаем Flask в отдельном потоке
    from threading import Thread
    def run_flask():
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Бесконечный цикл для поддержания работы бота
    while True:
        await asyncio.sleep(3600)  # Спим 1 час

if __name__ == "__main__":
    # Запускаем основную асинхронную функцию
    asyncio.run(main())
