import os
import logging
import re
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler

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

# Состояния для ConversationHandler
WAITING_ALTERNATIVE = 1

# Обновленная база данных пакетов ТОЛЬКО с теми, что на скринах
PACKAGES = [
    # Вертикальные пакеты с первого скрина
    (250, 350, 90, "Пакет верт. д250 ш90 в350 / с ручками / Штамп 1158"),
    (100, 120, 90, "Пакет верт. д100 ш90 в120 / Штамп 512"),
    (110, 360, 100, "Пакет верт. д110 ш100 в360 / дно без нахлеста / Штамп 095"),
    (110, 320, 90, "Пакет верт. д110 ш90 в320 / Штамп 326"),
    (120, 370, 115, "Пакет верт. д120 ш115 в370 / Штамп 1092"),
    (120, 400, 115, "Пакет верт. д120 ш115 в400 / Штамп 713"),
    (120, 340, 120, "Пакет верт. д120 ш120 в340 / дно без нахлеста / Штамп 091"),
    (120, 370, 120, "Пакет верт. д120 ш120 в370 / Шато Тамань / Штамп 718"),
    (120, 220, 90, "Пакет верт. д120 ш90 в220 / 2 на листе / Штамп 1079"),
    (130, 220, 30, "Пакет верт. д130 ш30 в220 / дно без нахлеста / Штамп 094"),
    (140, 160, 60, "Пакет верт. д140 ш60 в160 / с прорезями под ленты / Штамп 619"),
    (140, 180, 70, "Пакет верт. д140 ш70 в180 / Штамп 559"),
    (170, 260, 40, "Пакет верт. д170 ш40 в260 / Штамп 325"),
    (170, 280, 90, "Пакет верт. д170 ш90 в280 / Штамп 042"),
    (180, 230, 90, "Пакет верт. д180 ш90 в230 / Штамп 164"),
    (190, 250, 70, "Пакет верт. д190 ш70 в250 / Штамп 927"),
    (200, 250, 100, "Пакет верт. д200 ш100 в250 / Штамп 892"),
    (200, 250, 100, "Пакет верт. д200 ш100 в250 / с вырубкой ручкой / Штамп 1032"),
    (200, 250, 80, "Пакет верт. д200 ш80 в250 / отверстия под ленты/ Штамп 758"),
    (220, 300, 120, "Пакет верт. д220 ш120 в300 / с ручками / Штамп 1046"),
    (220, 320, 80, "Пакет верт. д220 ш80 в320 / Штамп 093"),
    (250, 320, 50, "Пакет верт. д250 ш50 в320 / Половинка пакета Владимир / Штамп 950"),
    (250, 360, 90, "Пакет верт. д250 ш90 в360 / КАСП средний / Штамп 394"),
    (250, 380, 90, "Пакет верт. д250 ш90 в380 / Штамп 768"),
    (270, 350, 120, "Пакет верт. д270 ш120 в350 / половинка пакета / Штамп 692"),
    (270, 350, 140, "Пакет верт. д270 ш140 в350 / Половинка пакета Владимир / Штамп 951"),
    (290, 370, 60, "Пакет верт. д290 ш60 в370 / Штамп 908"),
    (300, 400, 120, "Пакет верт. д300 ш120 в400 / половинка пакета / Штамп 655"),
    (300, 460, 120, "Пакет верт. д300 ш120 в460 / половинка пакета / Штамп 097"),
    (300, 350, 135, "Пакет верт. д300 ш135 в350 / половинка пакета / Штамп 570"),
    (300, 400, 150, "Пакет верт. д300 ш150 в400 / половинка пакета / Штамп 769"),
    (340, 480, 150, "Пакет верт. д340 ш150 в480 / половинка пакета / Штамп 772"),
    
    # Вертикальные пакеты со второго скрина
    (350, 450, 100, "Пакет верт. д350 ш100 в450 / половинка пакета / Штамп 478"),
    
    # Горизонтальные пакеты со второго скрина
    (160, 140, 80, "Пакет гор. д160 ш80 в140 / 3 на листе / Штамп 980"),
    (220, 180, 125, "Пакет гор. д220 ш125 в180 / отверстия под ленты / Штамп 919"),
    (230, 180, 90, "Пакет гор. д230 ш90 в180 / Штамп 096"),
    (248, 230, 108, "Пакет гор. д248 ш108 в230 / Штамп 565"),
    (280, 220, 100, "Пакет гор. д280 ш100 в220 / Половинка пакета Владимир / Штамп 949"),
    (280, 240, 70, "Пакет гор. д280 ш70 в240 / Штамп 133"),
    (300, 290, 140, "Пакет гор. д300 ш140 в290 / 1 половина / Штамп 933"),
    (335, 165, 75, "Пакет гор. д335 ш75 в165 / 2 половинки на штампе / Штамп 1136"),
    (300, 240, 130, "Пакет гор. д300 ш130 в240 / половинка пакета / Штамп 316"),
    (390, 300, 150, "Пакет гор. д390 ш150 в300 / половинка пакета / Штамп 770"),
    (400, 250, 120, "Пакет гор. д400 ш120 в250 мм / половинка пакета/Штамп 092"),
    (400, 300, 120, "Пакет гор. д400 ш120 в300 / половинка пакета / Штамп 430"),
    (400, 300, 150, "Пакет гор. д400 ш150 в300 / половинка пакета / Штамп 531"),
    (400, 300, 200, "Пакет гор. д400 ш200 в300 / половинка пакета / Штамп 090"),
    (410, 280, 280, "Пакет гор. д410 ш280 в280 / половинка пакета / Штамп 915"),
    (420, 400, 200, "Пакет гор. д420 ш200 в400 / половинка пакета / нужна 'заплатка' на дно / Штамп 508"),
    (450, 300, 140, "Пакет гор. д450 ш140 в300 / половинка пакета / Штамп 328"),
    (460, 390, 150, "Пакет гор. д460 ш150 в390 / половинка пакета / Штамп 914"),
    (480, 340, 140, "Пакет гор. д480 ш140 в340 / половинка пакета / Штамп 771"),
    (490, 390, 73, "Пакет гор. д490 ш73 в390 / половинка пакета / пуансоны под ручки на штампе / Штамп 532"),
    (500, 550, 100, "Пакет гор. д500 ш100 в550 / половинка пакета / Штамп 376"),
    (500, 400, 200, "Пакет гор. д500 ш200 в400 / половинка пакета / нужна 'заплатка' на дно / Штамп 533"),
    (530, 340, 170, "Пакет гор. д530 ш170 в340 / половинка пакета / Штамп 379"),
    
    # Квадратные/универсальные пакеты со второго скрина
    (150, 150, 80, "Пакет д150 ш80 в150 / Штамп 230"),
    (220, 220, 120, "Пакет д220 ш120 в220 / Штамп 427"),
    (220, 220, 120, "Пакет д220 ш120 в220 / отверстия под ленты / Штамп 846"),
    (630, 260, 260, "Пакет д630 ш260 в260 / половинка пакета / дно без нахлеста / Штамп 465"),
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
    
    for pkg_length, pkg_height, pkg_width, desc in PACKAGES:
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
    # Специальный пакет с деталями
    if length == 400 and height == 300 and width == 150 and "Штамп 531" in description:
        details = (
            "📋 <b>Детали пакета</b>\n\n"
            f"📦 Размер: {length} × {height} × {width} мм\n"
            f"📝 Описание: {description}\n\n"
            "📄 <b>Номер заказа-шаблона:</b> КАСП-03034-О5\n"
            "🔗 <b>Ссылка на чертеж:</b> https://disk.360.yandex.ru/d/EmxhEKA4-o57Rw"
        )
        drawing_url = "https://disk.360.yandex.ru/d/EmxhEKA4-o57Rw"
    else:
        details = (
            "📋 <b>Детали пакета</b>\n\n"
            f"📦 Размер: {length} × {height} × {width} мм\n"
            f"📝 Описание: {description}\n\n"
            "⏳ <i>Здесь скоро появится номер заказа-шаблона и ссылка на чертеж пакета</i>"
        )
        drawing_url = None
    
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

async def handle_size(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        text = update.message.text.strip()
        numbers = re.findall(r'\d+', text)

        if len(numbers) < 3:
            await update.message.reply_html(
                "❌ Введите три числа: <b>длина высота ширина</b>\n"
                "Например: <code>200 250 100</code>"
            )
            return ConversationHandler.END

        length, height, width = map(int, numbers[:3])
        requested_type = get_requested_type(length, height, width)
        
        # Сохраняем оригинальные размеры и тип
        context.user_data['original_sizes'] = (length, height, width)
        context.user_data['original_type'] = requested_type
        
        # Вызываем функцию для отображения результатов
        await show_search_results(update, context, length, height, width, requested_type)
        
        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_html(
            "❌ Ошибка. Введите размеры в формате: <code>длина высота ширина</code>",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

async def show_search_results(update, context, length, height, width, search_type, is_alternative=False):
    """Показывает результаты поиска с кнопками"""
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

async def handle_package_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает клик по пакету"""
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
            for pkg_length, pkg_height, pkg_width, desc in PACKAGES:
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

async def handle_alternative_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает запрос на альтернативный поиск"""
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

async def handle_back_to_last_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает возврат к последнему результату поиска из деталей пакета"""
    query = update.callback_query
    await query.answer()
    
    # Получаем сохраненные данные о последнем поиске
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

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отменяет диалог"""
    await update.message.reply_html(
        "✅ Диалог завершен. Введите новые размеры для поиска пакетов.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

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

def main() -> None:
    # Используем токен из переменных окружения
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Создаем ConversationHandler для обработки диалога
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_size)],
        states={},
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(handle_package_click, pattern="^package_"))
    application.add_handler(CallbackQueryHandler(handle_alternative_search, pattern="^alternative_"))
    application.add_handler(CallbackQueryHandler(handle_back_to_last_search, pattern="^back_to_last_search$"))
    application.add_handler(conv_handler)
    
    logger.info("🤖 Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()