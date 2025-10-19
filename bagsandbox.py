import os
import logging
import re
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Загружаем переменные из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN', '8163558738:AAGIPcOHG8FyNQEe4zpP8AuT5Rm-ir-xsJE')

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN не установлен!")
    exit(1)

# Создаем приложение Telegram
application = Application.builder().token(BOT_TOKEN).build()

# База данных пакетов
PACKAGES = [
    # Вертикальные пакеты
    (250, 350, 90, "Пакет верт. д250 ш90 в350 / с ВЫРУБНЫМИ ручками / Штамп 1158", "Заказ-шаблон ....", "https://disk.360.yandex.ru/d/Peyk8BPpIlnZhA"),
    (100, 120, 90, "Пакет верт. д100 ш90 в120 / Штамп 512", "Заказ-шаблон КАСП-1460-Ц4, Мск-00055-О3", "https://disk.360.yandex.ru/d/3-yN-eN1W8_oFA"),
    (110, 360, 100, "Пакет верт. д110 ш100 в360 / дно без нахлеста / Штамп 095", "Заказ-шаблон КАСП-02473-О5", "https://disk.360.yandex.ru/d/VFv4p5Z1Kg76WQ"),
    (110, 320, 80, "Пакет верт. д110 ш80 в320 / Штамп 326", "Заказ-шаблон КАСП-01032-О4", "https://disk.360.yandex.ru/d/RkCLCQjU1lBlhg"), 
    (120, 370, 111, "Пакет верт. д120 ш111 в370 / Штамп 1092", "Заказ-шаблон .....", "https://disk.360.yandex.ru/d/Q2AR6FSw6B5znA"),
    (120, 400, 115, "Пакет верт. д120 ш115 в400 / Штамп 713", "Заказ-шаблон КАСП-07503-О4", "https://disk.360.yandex.ru/d/GHji0S2f96lCUg"),
    (120, 340, 120, "Пакет верт. д120 ш120 в340 / дно без нахлеста / Штамп 091", "Заказ-шаблон КАСП-07096-О4", "https://disk.360.yandex.ru/d/JwWNUCYVW7dppA"),
    (120, 370, 120, "Пакет верт. д120 ш120 в370 / Шато Тамань / Штамп 718", "Заказ-шаблон КАСП-04356-О5", "https://disk.360.yandex.ru/d/yaGfocdeiWf8-Q"),
    (120, 220, 90, "Пакет верт. д120 ш90 в220 / 2 на листе!! / Штамп 1079", "Заказ-шаблон Мск-00181-О5", "https://disk.360.yandex.ru/d/fsfvOIEHDjEGJA"),
    (130, 220, 130, "Пакет верт. д130 ш130 в220 / дно без нахлеста / Штамп 094", "Заказ-шаблон КАСП-03701-О4", "https://disk.360.yandex.ru/d/uk1Jb_USjMgpgA"),
    (140, 160, 60, "Пакет верт. д140 ш60 в160 / ПОД ЛЕНТЫ / Штамп 619", "Заказ-шаблон КАСП-00241-О4", "https://disk.360.yandex.ru/d/S5RwXnfNWPG0ng"),
    (140, 180, 70, "Пакет верт. д140 ш70 в180 / Штамп 559", "Заказ-шаблон КАСП-02206-О4", "https://disk.360.yandex.ru/d/W-FTwGSHlv2pgw"),
    (170, 260, 40, "Пакет верт. д170 ш40 в260 / Штамп 925", "Заказ-шаблон КАСП-05365-Ц5", "https://disk.360.yandex.ru/d/6XnGQP2t-zxuUw"),
    (170, 280, 90, "Пакет верт. д170 ш90 в280 / Штамп 042", "Заказ-шаблон ЗКАСП-04184-О5", "https://disk.360.yandex.ru/d/GYTxXr6rdCaOoA"),
    (180, 230, 90, "Пакет верт. д180 ш90 в230 / Штамп 164", "Заказ-шаблон КАСП-04090-О5", "https://disk.360.yandex.ru/d/QvlEFYLggsEAAw"),
    (190, 250, 70, "Пакет верт. д190 ш70 в250 / Штамп 927", "Заказ-шаблон КАСП-07610-Ц4, ЗКАСП-06274-О4", "https://disk.360.yandex.ru/d/Ii-ZsU9VPFf1mA"),
    (200, 250, 100, "Пакет верт. д200 ш100 в250 / Штамп 892", "Заказ-шаблон КАСП-03954-О5", "https://disk.360.yandex.ru/d/3kzW0mZl-wk9TA"),
    (200, 250, 100, "Пакет верт. д200 ш100 в250 / с ВЫРУБНЫМИ ручками / Штамп 1032", "Заказ-шаблон ЗКАСП-10081-О4", "https://disk.360.yandex.ru/d/oEDrzOgWHlOkXw"),
    (200, 250, 80, "Пакет верт. д200 ш80 в250 / ПОД ЛЕНТЫ / Штамп 758", "Заказ-шаблон КАСП-06610-О4", "https://disk.360.yandex.ru/d/dLI00bXytUo9cA"),
    (220, 300, 120, "Пакет верт. д220 ш120 в300 / с ВЫРУБНЫМИ ручками / Штамп 1046", "Заказ-шаблон КАСП-06290-О4", "https://disk.360.yandex.ru/d/y2yr572Pvv2YPw"),
    (220, 320, 80, "Пакет верт. д220 ш80 в320 / Штамп 093", "Заказ-шаблон КАСП-02882-О5", "https://disk.360.yandex.ru/d/F17zyggakb0LJA"),
    (250, 320, 150, "Пакет верт. д250 ш150 в320 / Половинка пакета Владимир / Штамп 950", "Заказ-шаблон ЗКАСП-07997-О5", "https://disk.360.yandex.ru/d/gm-Si78cmkM9qA"),
    (250, 360, 90, "Пакет верт. д250 ш90 в360 / КАСП средний / Штамп 394", "Заказ-шаблон КАСП-05512-О5", "https://disk.360.yandex.ru/d/viC1RXxAFpOUFw"),
    (250, 380, 90, "Пакет верт. д250 ш90 в380 / Штамп 768", "Заказ-шаблон КАСП-06569-О4", "https://disk.360.yandex.ru/d/1B_qrpgk-23ZqA"),
    (270, 350, 120, "Пакет верт. д270 ш120 в350 / половинка пакета / Штамп 692", "Заказ-шаблон КАСП-03745-О5", "https://disk.360.yandex.ru/d/d0yG6vp6gASvaA"),
    (270, 350, 140, "Пакет верт. д270 ш140 в350 / Половинка пакета Владимир / Штамп 951", "", "https://disk.360.yandex.ru/d/Tb_ApuI4ul8wgA"),
    (290, 370, 50, "Пакет верт. д290 ш50 в370 / Штамп 908", "Заказ-шаблон КАСП-03240-О4", "https://disk.360.yandex.ru/d/FNU-ltQ5vZKssQ"),
    (300, 400, 120, "Пакет верт. д300 ш120 в400 / половинка пакета / Штамп 655", "Заказ-шаблон КАСП-03474-О5", "https://disk.360.yandex.ru/d/DvRSRcuu_vTVzQ"),
    (300, 460, 120, "Пакет верт. д300 ш120 в460 / половинка пакета / Штамп 097", "Заказ-шаблон КАСП-08027-О4", "https://disk.360.yandex.ru/d/xHRnjFuNSM-rUQ"),
    (300, 350, 135, "Пакет верт. д300 ш135 в350 / половинка пакета / Штамп 570", "Заказ-шаблон КАСП-06330-О4", "https://disk.360.yandex.ru/d/3hAmNimaQ0ofDA"),
    (300, 400, 150, "Пакет верт. д300 ш150 в400 / половинка пакета / Штамп 769", "Заказ-шаблон КАСП-05163-О5", "https://disk.360.yandex.ru/d/EeiPrlgFutVcGw"),
    (340, 480, 150, "Пакет верт. д340 ш150 в480 / половинка пакета / Штамп 772", "Заказ-шаблон КАСП-01567-О5", "https://disk.360.yandex.ru/d/72Rbqxbljdez2A"),
    (350, 450, 100, "Пакет верт. д350 ш100 в450 / половинка пакета / Штамп 478", "Заказ-шаблон КАСП-01159-О5", "https://disk.360.yandex.ru/d/kyEe7JWJl071UQ"),
    
    # Горизонтальные пакеты
    (160, 140, 80, "Пакет гор. д160 ш80 в140 / 3 НА ЛИСТЕ / Штамп 980", "Заказ-шаблон ЗКАСП-00127-О5", "https://disk.360.yandex.ru/d/_0Qx-vmY5-ImbQ"),
    (220, 180, 125, "Пакет гор. д220 ш125 в180 / ПОД ЛЕНТЫ / Штамп 919", "Заказ-шаблон КАСП-07909-О4", "https://disk.360.yandex.ru/d/CGStQuXiiw4U-g"),
    (230, 180, 90, "Пакет гор. д230 ш90 в180 / Штамп 096", "Заказ-шаблон КАСП-04522-Ц5, КАСП-04145-О5", "https://disk.360.yandex.ru/d/BzRmOcxFebIJzg"),
    (248, 230, 108, "Пакет гор. д248 ш108 в230 / Штамп 565", "Заказ-шаблон КАСП-04391-Ц5, КАСП-02744-О5", "https://disk.360.yandex.ru/d/tJmxsPZaOTunyw"),
    (280, 220, 100, "Пакет гор. д280 ш100 в220 / Половинка пакета Владимир / Штамп 949", "Заказ-шаблон ЗКАСП-07472-О5", "https://disk.360.yandex.ru/d/w92NUZFaOIpiyw"),
    (280, 240, 70, "Пакет гор. д280 ш70 в240 / Штамп 133", "Заказ-шаблон КАСП-01931-Ц5, КАСП-04201-О5", "https://disk.360.yandex.ru/d/74TMziAk6zsEgw"),
    (300, 290, 140, "Пакет гор. д300 ш140 в290 / 1 половина / Штамп 933", "Заказ-шаблон КАСП-04766-О5", "https://disk.360.yandex.ru/d/08q6eprjImYlPg"),
    (335, 165, 75, "Пакет гор. д335 ш75 в165 / 2 половинки на штампе / Штамп 1136", "Заказ-шаблон ....", "https://disk.360.yandex.ru/d/NmwI1In9LLPrNw"),
    (380, 240, 130, "Пакет гор. д380 ш130 в240 / половинка пакета / Штамп 916", "Заказ-шаблон КАСП-005517-О4", "https://disk.360.yandex.ru/d/q20e5ug5OvMknQ"),
    (390, 300, 150, "Пакет гор. д390 ш150 в300 / половинка пакета / Штамп 770", "Заказ-шаблон КАСП-01206-О5", "https://disk.360.yandex.ru/d/cTe1E-2zTdVO9g"),
    (400, 250, 120, "Пакет гор. д400 ш120 в250 мм / половинка пакета/Штамп 092", "Заказ-шаблон КАСП-07141-О4", "https://disk.360.yandex.ru/d/c04m8A23_hcR_Q"),
    (400, 300, 120, "Пакет гор. д400 ш120 в300 / половинка пакета / Штамп 430", "Заказ-шаблон КАСП-01211-О5", "https://disk.360.yandex.ru/d/ddmj-2Q7tbjeFg"),
    (400, 300, 150, "Пакет гор. д400 ш150 в300 / половинка пакета / Штамп 531", "Заказ-шаблон КАСП-04345-О5", "https://disk.360.yandex.ru/d/EmxhEKA4-o57Rw"),
    (400, 300, 200, "Пакет гор. д400 ш200 в300 / половинка пакета / Штамп 090", "Заказ-шаблон КАСП-07154-О4", "https://disk.360.yandex.ru/d/-Zf8EzAR8ODk0A"),
    (410, 280, 280, "Пакет гор. д410 ш280 в280 / половинка пакета / Штамп 915", "Заказ-шаблон ЗКАСП-02483-О5", "https://disk.360.yandex.ru/d/yIBD0zOo_tXX9w"),
    (420, 400, 200, "Пакет гор. д420 ш200 в400 / половинка пакета / нужна ЗАПЛАТКА на дно / Штамп 508", "Заказ-шаблон КАСП-07377-О4", "https://disk.360.yandex.ru/d/SIdLisRNGL4Kcw"),
    (450, 300, 140, "Пакет гор. д450 ш140 в300 / половинка пакета / Штамп 928", "Заказ-шаблон КАСП-04481-О5", "https://disk.360.yandex.ru/d/pb5w0BGlBWd_PQ"),
    (460, 390, 150, "Пакет гор. д460 ш150 в390 / половинка пакета / Штамп 914", "Заказ-шаблон КАСП-00996-О5", "https://disk.360.yandex.ru/d/8f-sJ4k69YsoUQ"),
    (480, 340, 140, "Пакет гор. д480 ш140 в340 / половинка пакета / Штамп 771", "Заказ-шаблон КАСП-05331-О5", "https://disk.360.yandex.ru/d/8eOb9ha0yo-9rQ"),
    (490, 390, 73, "Пакет гор. д490 ш73 в390 / половинка пакета / пуансоны под ручки на штампе / Штамп 532", "Заказ-шаблон ....", "https://disk.360.yandex.ru/d/rIhAn9GP19JScA"),
    (500, 350, 100, "Пакет гор. д500 ш100 в350 / половинка пакета / Штамп 376", "Заказ-шаблон КАСП-03423-О5", "https://disk.360.yandex.ru/d/2aYmmPwpmkqn5A"),
    (500, 400, 200, "Пакет гор. д500 ш200 в400 / половинка пакета / нужна ЗАПЛАТКА на дно / Штамп 533", "Заказ-шаблон КАСП-03461-О5", "https://disk.360.yandex.ru/d/C9We9YAafSvSHw"),
    (530, 340, 170, "Пакет гор. д530 ш170 в340 / половинка пакета / Штамп 379", "Заказ-шаблон КАСП-08220-О4", "https://disk.360.yandex.ru/d/9VchoXrY3U0JPA"),
    
    # Квадратные пакеты
    (150, 150, 80, "Пакет д150 ш80 в150 / Штамп 230", "Заказ-шаблон КАСП-07911-Ц4, КАСП 01464-О5", "https://disk.360.yandex.ru/d/C81M3tOCOslx4g"),
    (220, 220, 120, "Пакет д220 ш120 в220 / Штамп 427", "Заказ-шаблон КАСП-04928-О5", "https://disk.360.yandex.ru/d/69V_z4FbsvDiag"),
    (220, 220, 120, "Пакет д220 ш120 в220 / ПОД ЛЕНТЫ / Штамп 846", "Заказ-шаблон КАСП-05022-О4", "https://disk.360.yandex.ru/d/P2TtXuwkP1MpAQ"),
    (250, 250, 250, "Пакет д 250 ш 250 в 250/ половинка пакета / дно без нахлеста/ Штамп 465", "Заказ-шаблон КАСП-04929-О5", "https://disk.360.yandex.ru/d/V_iXzgYmyl8hJw"),
]

# База данных коробок (однослойные пачки) - ОБНОВЛЕННАЯ БАЗА ИЗ EXCEL
BOXES = [
    (58, 38, 100, "Коробка пачка д58 ш38 в100 / с ложементом внутри 2 склейки / Штамп 1086", "КАСП-00348-О5", "https://disk.yandex.ru/d/3cJRuqiQlFb7kQ", "https://disk.yandex.ru/i/UtnXJGfcE-rJsQ"),
    (100, 100, 100, "Коробка пачка д100 ш100 в100 мм / 1 склейка / Штамп 410", "-", "https://disk.yandex.ru/d/C2aR5Rcy_b5beg", "https://disk.yandex.ru/i/vxZcdPrZo1z2WA"),
    (100, 100, 260, "Коробка пачка д100 ш100 в260 / 1 склейка / Штамп 1156", "-", "https://disk.yandex.ru/d/PQp-E92lB9ZmMA", "https://disk.yandex.ru/i/oKg91R_Nssu9xQ"),
    (100, 100, 330, "Коробка пачка д100 ш100 в330 мм / 1 склейка / Штамп 323", "-", "https://disk.yandex.ru/d/k19_rAaIlovuPw", "https://disk.yandex.ru/i/9Bnl29238B4ZkA"),
    (100, 6, 100, "Коробка пачка д100 ш6 в100 мм (Ц) / с еврослотом / Штамп 714", "КАСП-02212-Ц4", "https://disk.yandex.ru/d/Z55OvQgzDalP1g", "https://disk.yandex.ru/d/3UrNknI76K4r5Q"),
    (25, 25, 100, "Коробка пачка д25 ш25 в100 мм (Ц) / 1 склейка / Штамп 763", "КАСП-03831-Ц3", "https://disk.yandex.ru/d/dpXqnwGi82uiBw", "https://disk.yandex.ru/i/5yodvNuJqycDkQ"),
    (100, 60, 130, "Коробка пачка д100 ш60 в130 / 3 точки склейки / Штамп 1126", "КАСП-02870-У5", "https://disk.yandex.ru/d/rYosmkXEntnhIQ", "https://disk.yandex.ru/i/9D3uc0JLn2iTiQ"),
    (100, 60, 200, "Коробка пачка д100 ш60 в200 / Иммуновит Травы Кавказа с отрывной перфорацией / Штамп 680", "КАСП-02385-О5", "https://disk.yandex.ru/d/XKIj2CIcjpEhFQ", "https://disk.yandex.ru/i/4PLI78Uu4ufkkg"),
    (68, 19, 100, "Коробка пачка д68 ш19 в100 мм / 1 склейка / Штамп 761", "КАСП-00137-О5", "https://disk.yandex.ru/d/LsyXTH-eMrtRRw", "https://disk.yandex.ru/i/wzAEq_pFbpuOcA"),
    (100, 80, 150, "Коробка пачка д100 ш80 в150 / 3 склейки с зип перфорацией / Штамп 1093", "-", "https://disk.yandex.ru/d/PU70NcjYRgQn3Q", "https://disk.yandex.ru/i/JiEc5jWxlBgh4A"),
    (102, 102, 102, "Коробка пачка д102 ш102 в102 мм / 1 склейка / с окошком / Штамп 677", "КАСП-03540-О3", "https://disk.yandex.ru/d/6yW-H3oJ9UJbkw", "https://disk.yandex.ru/d/SyADfadorgI7Mw"),
    (102, 82, 62, "Коробка пачка д102 ш82 в62 / 1 склейка / Штамп 1094", "-", "https://disk.yandex.ru/d/jGaAds1T845XSg", "https://disk.yandex.ru/i/rw8YCsb8F_kYHQ"),
    (48, 48, 104, "Коробка пачка д48 ш48 в104 мм / 1 склейка / Штамп 868", "КАСП-02003-О4", "https://disk.yandex.ru/d/i5D5xgOVhqxelg", "https://disk.yandex.ru/i/tjXCILz7WZ-URw"),
    (118, 48, 150, "Коробка пачка д118 ш48 в150 мм (Ц) / 1 склейка /Штамп 336", "-", "https://disk.yandex.ru/d/6mNPdWEFugAQzg", "https://disk.yandex.ru/d/DPdI20xDL0fz6w"),
    (56, 25, 105, "Коробка пачка д56 ш25 в105 мм / 1 склейка с окошком / Штамп 786", "КАСП-00307-О4", "https://disk.yandex.ru/d/j_TT1gYC2m58VA", "https://disk.yandex.ru/i/E8_dLxb3nw_8QA"),
    (73, 19, 105, "Коробка пачка д73 ш19 в105 мм (Ц) / 1 склейка / Штамп 731", "КАСП-02417-О3", "https://disk.yandex.ru/d/vlcFt_LQWXDc8w", "https://disk.yandex.ru/d/qhzBf5SmskQp7g"),
    (108, 73, 81, "Коробка пачка д108 ш73 в81 мм / 1 склейка / Штамп 782", "-", "https://disk.yandex.ru/d/NUZNZgiiWJX8nQ", "https://disk.yandex.ru/i/SL92A8dUd579vQ"),
    (108, 82, 135, "Коробка пачка д108 ш82 в135 мм / 1 склейка / Штамп 598", "КАСП-07103-О4", "https://disk.yandex.ru/d/_lD9ppcfeZvT-Q", "https://disk.yandex.ru/i/RIu7cC9t6NbYfQ"),
    (110, 32, 180, "Коробка пачка д110 ш32 в180 (Ц) / под шприцы с перфорацией 4-2 / Штамп 979", "КАСП-02594-О5", "https://disk.yandex.ru/d/embHtx__dJMAaA", "https://disk.yandex.ru/i/hIUcSS3qOAMRNw"),
    (110, 40, 180, "Коробка пачка д110 ш40 в180 / под шприцы / Штамп 939", "КАСП-00399-О4", "https://disk.yandex.ru/d/TDPF6Xej-e6F-g", "https://disk.yandex.ru/i/Lb3pvuffL8M8xg"),
    (110, 50, 125, "Коробка пачка д110 ш50 в125 / 1 склейка / Штамп 1172", "-", "https://disk.yandex.ru/i/Lb3pvuffL8M8xg", "https://disk.yandex.ru/i/z7rKGB1BEaAQIQ"),
    (110, 60, 110, "Коробка пачка д110 ш60 в110 мм /1 склейка / Штамп 694", "КАСП-02637-О2", "https://disk.yandex.ru/d/iXTB21R16gSeTA", "https://disk.yandex.ru/d/Dld4TpSsBjJzEA"),
    (117, 45, 178, "Коробка пачка д117 ш45 в178 / 1 склейка с европодвесом / Штамп 1001", "-", "https://disk.yandex.ru/d/25K98JVgkvt6PQ", "https://disk.yandex.ru/i/128caGKNL1eOfw"),
    (119, 57, 148, "Коробка пачка д119 ш57 в148 / для сыпучего с перфорацией 3 склейки / Штамп 1164", "Врн-00060-О5", "https://disk.yandex.ru/d/RRT3KU_F5fljww", "https://disk.yandex.ru/i/TpzbZBN2JAmpvQ"),
    (120, 120, 155, "Коробка пачка д120 ш120 в155 / 1 склейка / Штамп 1169", "КАСП-05058-О5", "https://disk.yandex.ru/d/kaNWFihW5duiDA", "https://disk.yandex.ru/i/0CBeOU2W59sRCQ"),
    (120, 58, 150, "Коробка пачка д120 ш58 в150 мм (Ц) / 1 склейка / перфорация под сыпучие / Штамп 339", "-", "https://disk.yandex.ru/d/PoKng_GJrLsXSg", "https://disk.yandex.ru/d/K4BgRLxR6IYLpQ"),
    (85, 40, 120, "Коробка пачка д85 ш40 в120 мм (Ц) / 1 склейка / Штамп 065", "-", "https://disk.yandex.ru/d/K4BgRLxR6IYLpQ", "https://disk.yandex.ru/i/KLftgthyrhamOQ"),
    (68, 25, 122, "Коробка пачка д68 ш25 в122 мм (Ц) / 1 склейка / Штамп 792", "КАСП-07864-О3", "https://disk.yandex.ru/d/DOhNpIaRung4Rw", "https://disk.yandex.ru/i/zdLz-0U2kPPw_A"),
    (125, 85, 122, "Коробка пачка д125 ш85 в122 мм / 1 склейка / Штамп 783", "-", "https://disk.yandex.ru/d/g-4Vye0whyuh5Q", "https://disk.yandex.ru/i/l6C_ShecLmqNxQ"),
    (123, 50, 183, "Коробка пачка д123 ш50 в183 мм / 1 склейка / Штамп 621", "КАСП-01086-О2", "https://disk.yandex.ru/d/8ItZxfiszrXdOQ", "https://disk.yandex.ru/i/VebQjW7kZG056g"),
    (125, 50, 185, "Коробка пачка д125 ш50 в185 мм / 1 склейка / Штамп 611", "КАСП-00052-О2", "https://disk.yandex.ru/d/adkFvDbv1U2ZjA", "https://disk.yandex.ru/i/I1QUU1-0AEYtmg"),
    (130, 100, 65, "Коробка пачка д130 ш100 в65 мм / 1 склейка / Штамп 753", "-", "https://disk.yandex.ru/i/jM7XaemdT_grzg", "https://disk.yandex.ru/i/jM7XaemdT_grzg"),
    (130, 130, 130, "Коробка пачка д130 ш130 в130 мм / 1 склейка / Штамп 610", "-", "https://disk.yandex.ru/d/jF3iqElpZdHT-g", "https://disk.yandex.ru/i/z2qpfFVqATNqhA"),
    (130, 80, 130, "Коробка пачка д130 ш80 в130 (Ц) / с европодвесом 1 склейка / Штамп 1018", "-", "https://disk.yandex.ru/d/NZDAJ6NC_YU7hA", "https://disk.yandex.ru/i/jV0J9AkcRBKNag"),
    (135, 30, 255, "Коробка пачка д135 ш30 в255 / для пластырей 1 склейка / Штамп 990", "КАСП-02718-О4", "https://disk.yandex.ru/d/A_RSdN7rBKviIw", "https://disk.yandex.ru/i/MD-v87u8FhfOcg"),
    (85, 23, 135, "Коробка пачка д85 ш23 в135 мм (Ц) / 1 склейка / ложемент / Штамп 810", "-", "https://disk.yandex.ru/d/eo-gjwoGoT1q9Q", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (140, 110, 95, "Коробка пачка д140 ш110 в95 мм (Ц) / 1 склейка / Штамп 581", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (140, 45, 190, "Коробка пачка д140 ш45 в190 / 1 склейка / Штамп 1091", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (140, 49, 112, "Коробка пачка д140 ш49 в112 мм / 1 склейка / Штамп 780", "КАСП-00930-О3", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (140, 85, 60, "Коробка пачка д140 ш85 в60 мм / под картофель фри Сицилия / Штамп 567", "КАСП-05855-О1", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (45, 45, 141, "Коробка пачка д45 ш45 в141 мм / 1 склейка / Штамп 543", "КАСП-07876-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (57, 57, 145, "Коробка пачка д57 ш57 в145 мм (Ц) / 1 склейка / Штамп 716", "КАСП-00731-О3", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (15, 15, 120, "Коробка пачка д15 ш15 в120 мм (Ц) / 1 склейка / Штамп 1026", "КАСП-05258-Ц5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (100, 50, 150, "Коробка пачка д100 ш50 в150 мм / самосборная / Штамп 052", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (105, 80, 150, "Коробка пачка д105 ш80 в150 мм / 1 склейка / Штамп 743", "КАСП-04258-О2", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (120, 58, 150, "Коробка пачка д120 ш58 в150 мм / 1 склейка и перфорация под сыпучие / Штамп 010", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (41, 41, 150, "Коробка пачка д41 ш41 в150 мм / 1 склейка / Штамп 679", "КАСП-03757-О2", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (150, 65, 70, "Коробка пачка д150 ш65 в70 мм / под чай пакетированный / Штамп 050", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (80, 65, 150, "Коробка пачка д80 ш65 в150 мм (Ц) / 1 склейка / Штамп 048", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (90, 25, 150, "Коробка пачка д90 ш25 в150 мм (Ц) / 1 склейка / европодвес / Штамп 732", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (150, 91, 70, "Коробка пачка д150 ш91 в70 / 1 склейка / Штамп 1135", "КАСП-05494-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (152, 57, 178, "Коробка пачка д152 ш57 в178 мм / комплект к лоток 947 Ярош / Штамп 948", "КАСП-00580-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (20, 20, 157, "Коробка пачка д20 ш20 в157 мм (Ц) / 1 склейка / Штамп 877", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (142, 28, 159, "Коробка пачка д142 ш28 в159 мм / Штамп 693", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (16, 16, 130, "Коробка пачка д16 ш16 в130 мм (Ц) / 1 склейка / Штамп 1119", "КАСП-05374-О5, КАСП-06154-Ц5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (110, 60, 160, "Коробка пачка д110 ш60 в160 мм / 1 склейка / Штамп 041", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (160, 15, 160, "Коробка пачка д160 ш15 в160 / Штамп 1057", "КАСП-05562-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (123, 50, 164, "Коробка пачка д123 д50 в164 мм / 1 склейка / Штамп 725", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (165, 55, 60, "Коробка пачка д165 ш55 в60 мм / под чай пакетированный / Штамп 060", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (150, 166, 63, "Коробка пачка д150 ш166 в63 мм / 1 склейка / Штамп 529", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (170, 90, 230, "Коробка пачка д170 ш90 в230 мм (Ц) / треугольный верх / отверстия под ручки / Штамп 620", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (176, 60, 260, "Коробка пачка д176 ш60 в260 мм / треугольный верх / Штамп 449", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (18, 18, 132, "Коробка пачка д18 ш18 в132 мм (Ц) / 1 склейка / Штамп 1152", "КАСП-03479-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (180, 120, 50, "Коробка пачка д180 ш120 в50 мм (Ц) / 1 склейка под сыпучие / Штамп 168", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (180, 50, 60, "Коробка пачка д180 ш50 в60 мм / 1 склейка / Штамп 1098", "КАСП-01541-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (85, 65, 180, "Коробка пачка д85 ш65 в180 мм / треугольный верх / 1 склейка / Штамп 049", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (83, 14, 183, "Коробка пачка д83 ш14 в183 мм / с ложементом / 1 склейка / под стекла на тел / Штамп 593", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (125, 37, 185, "Коробка пачка д125 ш37 в185 мм / 1 склейка / Штамп 589", "КАСП-00052-О2", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (120, 60, 190, "Коробка пачка д120 ш60 в190 мм / 3 склейки / Штамп 057", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (190, 16, 190, "Коробка пачка д190 ш16 в190 / 1 склейка / Штамп 1081", "КАСП-04011-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (190, 20, 190, "Коробка пачка д190 ш20 в190 / 1 склейка / с европодвесом / Штамп 1023", "КАСП-05138-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (79, 31, 191, "Коробка пачка д79 ш31 в191 мм / 1 склейка / Штамп 597", "КАСП-01196-О3", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (120, 40, 200, "Коробка пачка д120 ш40 в200 мм / 3 склейки / Штамп 056", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (201, 120, 76, "Коробка пачка д201 ш120 в76 мм / под салфетки / Штамп 012", "КАСП-00477-О3", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (100, 14, 205, "Коробка пачка д100 ш14 в205 мм (Ц) / с окошком / еврослот / Штамп 633", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (110, 45, 205, "Коробка пачка д110 ш45 в205 мм (Ц) / 3 склейки / Штамп 066", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (205, 70, 205, "Коробка пачка д205 ш70 в205 / 1 склейка с окном / Штамп 1030", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (21, 21, 88, "Коробка пачка д21 ш21 в88 мм (Ц) / 1 склейка / Штамп 1153", "КАСП-00645-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (115, 70, 222, "Коробка пачка д115 ш70 в222 мм / 2 окошка / под перчатки / Штамп 576", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (150, 70, 222, "Коробка пачка д150 ш70 в222 мм / 2 окошка / коробка под перчатки / Штамп 579", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (96, 96, 223, "Коробка пачка д96 ш96 в223 мм / 1 склейка / Штамп 025", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (25, 25, 100, "Коробка пачка д25 ш25 в100 мм (Ц) / 1 склейка / Штамп 1072", "КАСП-05770-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (27, 27, 98, "Коробка пачка д27 ш27 в98 мм (Ц) / 1 склейка / Штамп 1140", "КАСП-03576-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (28, 28, 80, "Коробка пачка д28 ш28 в80 мм (Ц) / 1 склейка / Штамп 840", "КАСП-06431-О4, КАСП-04419-Ц5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (103, 12, 283, "Коробка пачка д103 ш12 в283 мм (Ц) / 1 склейка с окошком / Штамп 140", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (190, 80, 297, "Коробка пачка д190 ш80 в297 мм / 1 склейка с язычком для фиксации / Штамп 431", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (30, 30, 68, "Коробка пачка д30 ш30 в68 мм / 1 склейка / Штамп 857", "КАСП-04844-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (30, 30, 80, "Коробка пачка д30 ш30 в80 / 1 склейка / Штамп 1084", "Мск-00830-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (30, 30, 80, "Коробка пачка д30 ш30 в80 мм (Ц) / 1 склейка / Штамп 700", "КАСП-08194-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (30, 30, 83, "Коробка пачка д30 ш30 в83 мм / 1 склейка / Штамп 874", "КАСП-03616-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (33, 23, 122, "Коробка пачка д33 ш23 в122 мм (Ц) / 1 склейка Суфле / Штамп 1014", "КАСП-03514-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (33, 23, 165, "Коробка пачка д33 ш23 в165 / 1 склейка Стекло / Штамп 1015", "Сочи-00890-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (34, 34, 105, "Коробка пачка д34 ш34 в105 (Ц) / 1 склейка / Штамп 1121", "Мск-00855-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (34, 34, 108, "Коробка пачка д34 ш34 в108мм (Ц) / 1 склейка /Владимир./ Штамп 956", "КАСП-03590-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (37, 37, 101, "Коробка пачка д37 ш37 в101 / Гераника / Штамп 1010", "КАСП-04592-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (37, 37, 120, "Коробка пачка д37 ш37 в120 (Ц) / 1 склейка / Штамп 1118", "КАСП-05770-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (37, 37, 127, "Коробка пачка д37 ш37 в127 / 1 склейка / Штамп 986", "КАСП-04592-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (37, 37, 87, "Коробка пачка д37 ш37 в87 / 1 склейка / Штамп 1088", "Рнд-00001-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (250, 90, 385, "Коробка пачка д250 ш90 в385 мм / 1 склейка / Штамп 434", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (40, 40, 105, "Коробка пачка д40 ш40 в105 мм / 1 склейка / Штамп 921", "КАСП-06943-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (40, 40, 110, "Коробка пачка д40 ш40 в110 / Д3 Ярош 1 склейка / Штамп 954", "КАСП-05041-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (40, 40, 120, "Коробка пачка д40 ш40 в120 (Ц) / 1 склейка / Штамп 1139", "Мск-00930-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (40, 40, 130, "Коробка пачка д40 ш40 в130 (Ц) / 1 склейка / Штамп 1099", "КАСП-04188-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (40, 40, 145, "Коробка пачка д40 ш40 в145 / 1 склейка и ложемент / Штамп 1107", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (40, 40, 220, "Коробка пачка д40 ш40 в220 (Ц) / 1 склейка с окном / Штамп 1049", "КАСП-06441-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (41, 41, 90, "Коробка пачка д41 ш41 в90 мм (Ц) / 1 склейка / Штамп 412", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (42, 42, 106, "Коробка пачка д42 ш42 в106 (Ц) / 1 склейка / Штамп 1167", "КАСП-05059-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (42, 42, 165, "Коробка пачка д42 ш42 в165 / со встроенным ложементом 1 склейка / Штамп 985", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (45, 25, 90, "Коробка пачка д45 ш25 в90 / 1 склейка / Штамп 1116", "КАСП-01011-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (45, 35, 90, "Коробка пачка д45 ш35 в90 / 1 склейка / Штамп 1149", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (46, 46, 106, "Коробка пачка д46 ш46 в106 мм / 1 склейка / Штамп 791", "КАСП-06232-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (46, 46, 110, "Коробка пачка д46 ш46 в110 / 1 склейка / Штамп 1075", "КАСП-05201-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (46, 46, 134, "Коробка пачка д46 ш46 в134 (Ц) / 1 склейка / Штамп 1176", "Мск-00867-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (48, 48, 125, "Коробка пачка д48 ш48 в125 мм / с ложементом / Штамп 600", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (48.6, 16.6, 47.6, "Коробка пачка д48,6 ш16,6 в47,6 (Ц) / 1 склейка / Штамп 1115", "КАСП-04366-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (49, 49, 108, "Коробка пачка д49 ш49 в108 / 1 склейка / Штамп 1177", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (50, 17, 50, "Коробка пачка д50 ш17 в50 / 1 склейка / Штамп 1019", "Сочи-00806-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (50, 20, 160, "Коробка пачка д50 ш20 в160 / 1 склейка с европодвесом / Штамп 1082", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (50, 30, 100, "Коробка пачка д50 ш30 в100 мм (Ц) / треугольный верх / Штамп 830", "Сочи-00167-О3", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (50, 30, 200, "Коробка пачка д50 ш30 в200 мм (Ц) / треугольный верх / Штамп 829", "Сочи-00167-О3", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (50, 50, 165, "Коробка пачка д50 ш50 в165 / 1 склейка / Штамп 1180", "КАСП-05614-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (50, 50, 205, "Коробка пачка д50 ш50 в205 / 1 склейка / Штамп 966", "КАСП-01607-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (50, 50, 50, "Коробка пачка д50 ш50 в50/ 1 склейка / Штамп 1059", "Мск-00339-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (50, 50, 95, "Коробка пачка д50 ш50 в95 мм / 1 склейка / Штамп 862", "КАСП-03919-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (51, 51, 105, "Коробка пачка д51 ш51 в105 мм (Ц) / 1 склейка / Штамп 438", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (51, 51, 55, "Коробка пачка д51 ш51 в55 / 1 склейка / Штамп 1168", "КАСП-05060-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (52, 52, 75, "Коробка пачка д52 ш52 в75 / Тецентрик / Штамп 983", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (53, 53, 75, "Коробка пачка д53 ш53 в75 / с ложементом 1 склейка / Штамп 1062", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (53.6, 17.6, 52.6, "Коробка пачка д53,6 ш17,6 в52,6 (Ц) / 1 склейка / Штамп 1114", "КАСП-04366-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (55, 28, 70, "Коробка пачка д55 ш28 в70 мм (Ц) / 1 склейка / Штамп 569", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (55, 55, 46, "Коробка пачка д55 ш55 в46 (Ц) / 1 склейка / Штамп 1151", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (58, 24, 58, "Коробка пачка д58 ш24 в58 (Ц) / 1 склейка / Штамп 1179 ШТАМП ЗАБРАЛ ЗАКАЗЧИК", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (59, 59, 47, "Коробка пачка д59 ш59 в47 (Ц) / 1 склейка Горячева / Штамп 962", "КАСП-01002-Ц4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (60, 32, 100, "Коробка пачка д60 ш32 в100 мм (Ц) / 1 склейка / Штамп 571", "КАСП-01590-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (63, 30, 103, "Коробка пачка д63 ш30 в103 / 6 точек склейки / Штамп 1040", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (63, 63, 256, "Коробка пачка д63 ш63 в256 / Для диффузора, ложемент 30 мл (969), 50 мл (970), 100 мл (971)/ Штамп 968", "Мск-00841-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (63.6, 18.6, 62.6, "Коробка пачка д63,6 ш18,6 в62,6 (Ц) / 1 склейка / Штамп 1113", "КАСП-04366-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (65, 30, 240, "Коробка пачка д65 ш30 в240 / с окном / Штамп 1048", "КАСП-00124-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (68, 43, 122, "Коробка пачка д68 ш43 в122 / 1 склейка / Штамп 1101", "КАСП-04980-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (68, 18, 50, "Коробка пачка д68 ш18 в50 мм / 1 склейка / Штамп 760", "КАСП-00137-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (68, 68, 46, "Коробка пачка д68 ш68 в46 мм (Ц) / 1 склейка / Штамп 726", "КАСП-00720-Ц4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (70, 20, 70, "Коробка пачка д70 ш20 в70 (Ц) / 1 склейка / Штамп 1166", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (70, 21, 80, "Коробка пачка д70 ш21 в80 (Ц) / 1 склейка / Штамп 1077", "КАСП-00017-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (70, 30, 113, "Коробка пачка д70 ш30 в113 / треугольный верх / Штамп 1058", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (70, 60, 120, "Коробка пачка д70 ш60 в120 (Ц) / под духи Ярош / Штамп 957", "КАСП-01196-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (70, 70, 80, "Коробка пачка д70 ш70 в80 мм (Ц) / 1 склейка / Штамп 865", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (71, 15, 120, "Коробка пачка д71 ш15 в120 (Ц) / под карты 1 склейка / Штамп 991", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (71, 15, 80, "Коробка пачка д71 ш15 в80 (Ц) / Владимир / Штамп 1007", "КАСП-04364-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (72, 72, 175, "Коробка пачка д72 ш72 в175 / 3 точки склейки / Штамп 1066", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (72, 72, 85, "Коробка пачка д72 ш72 в85 мм (Ц) / под новогодние шары / Штамп 062", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (73, 24, 153, "Коробка пачка д73 ш24 в153 / 1 склейка / Штамп 1078", "КАСП-06119-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (73, 25, 153, "Коробка пачка д73 ш25 в153 / 1 склейка / Штамп 1100", "КАСП-01166-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (74, 16, 74, "Коробка пачка д74 ш16 в74 / 1 склейка / Штамп 994", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (74, 40, 130, "Коробка пачка д74 ш40 в130 мм (Ц) / 1 склейка / Штамп 572", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (75, 25, 110, "Коробка пачка д75 ш25 в110 / 1 склейка с европодвесом / Штамп 1013", "КАСП-04725-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (75, 30, 115, "Коробка пачка д75 ш30 в115 / Ангелочки Ярош / Штамп 1003", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (75, 75, 100, "Коробка пачка д75 ш75 в100 мм (Ц) / 1 склейка / Штамп 848", "Мск-00474-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (75, 75, 50, "Коробка пачка д75 ш75 в50 мм (Ц) / 1 склейка / Штамп 1146", "КАСП-04066-Ц5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (77, 40, 77, "Коробка пачка д77 ш40 в77 мм (Ц) / 1 склейка / Штамп 867", "КАСП-03265-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (77, 53, 350, "Коробка пачка д77 ш53 в350 / 3 склейки / Штамп 1120", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (78, 52, 78, "Коробка пачка д78 ш52 в78 мм (Ц) / 1 склейка / Штамп 697", "КАСП-01109-О3", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (80, 40, 152, "Коробка пачка д80 ш40 в152 мм / треугольный верх / окошко / Штамп 548", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (80, 40, 80, "Коробка пачка д80 ш40 в80 мм / 1 склейка / Штамп 860", "КАСП-04578-О3", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (80, 42, 200, "Коробка пачка д80 ш42 в200 мм / треугольный верх / окошко / Штамп 580", "КАСП-00297-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (80, 45, 190, "Коробка пачка д80 ш45 в190 мм (Ц) / 1 склейка треугольный верх / Штамп 1154", "КАСП-05460-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (80, 46, 165, "Коробка пачка д80 ш46 в165 мм (Ц) / 1 склейка с замком и двойной крышкой / Штамп 1150", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (80, 50, 220, "Коробка пачка д80 ш50 в220 мм / 1 склейка (ПОД ПЕЧЕНЬЕ) / Штамп 1022", "Мск-00400-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (80, 80, 100, "Коробка пачка д80 ш80 в100 мм (Ц) / 1 склейка / Штамп 861", "КАСП-01208-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (80, 80, 207, "Коробка пачка д80 ш80 в207 / 1 склейка / Штамп 1155", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (80, 80, 41.5, "Коробка пачка д80 ш80 в41,5 / с ложементом / Штамп 1071", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (80, 80, 60, "Коробка пачка д80 ш80 в60 / сундук под чай / Штамп 1047", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (80, 80, 80, "Коробка пачка д80 ш80 в80 / с окном одна склейка / Штамп 1123 ШТАМП ЗАБРАЛ ЗАКАЗЧИК!!!!", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (80, 80, 80, "Коробка пачка д80 ш80 в80/ 1 склейка / Штамп 1060", "Мск-00338-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (80, 80, 94, "Коробка пачка д80 ш80 в94 / 1 склейка / Штамп 1157", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (85, 25, 125, "Коробка пачка д85 ш25 в125 / для пластырей 1 склейка / Штамп 987", "КАСП-02713-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (85, 85, 76, "Коробка пачка д85 ш85 в76 / 3 точки склейки / Штамп 1068", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (81, 86, 91, "Коробка пачка д81 ш86 в91 мм / 1 склейка Нас泵 Askoll / Штамп 818", "КАСП-05170-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (32, 32, 88, "Коробка пачка д32 ш32 в88 мм (Ц) / 1 склейка / Штамп 756", "КАСП-02465-Ц5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (90, 50, 135, "Коробка пачка д90 ш50 в135 / 3 склейки / Штамп 1065", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (90, 50, 185, "Коробка пачка д90 ш50 в185 мм / 4 склейки / треугольный верх / Штамп 784", "КАСП-07952-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (95, 25, 155, "Коробка пачка д95 ш25 в155 / для пластырей 1 склейка / Штамп 988", "КАСП-02714-О4", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (95, 57, 55, "Коробка пачка д95 ш57 в55 мм / 1 склейка / Штамп 838", "Сочи-00162-О3", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (95, 65, 75, "Коробка пачка д95 ш65 в75 мм (Ц) / 1 склейка / Штамп 691", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (95, 95, 237, "Коробка пачка д95 ш95 в237 / 1 склейка / Штамп 1142", "КАСП-04832-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (50, 50, 90, "Коробка пачка+ложемент д50 ш50 в90 / Штамп 978", "-", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
    (34, 34, 108, "Корокба пачка д34 ш34 в108мм (Ц) / 1 слейка / Штамп 678", "Мск-00210-О5", "https://disk.yandex.ru/d/4FyVnQKvQ6h1RA", "https://disk.yandex.ru/i/9mJ3hVxQvQ1B3g"),
]

def get_package_type(description):
    """Определяет тип пакета по описанию"""
    desc_lower = description.lower()
    
    if "верт." in desc_lower or "вер." in desc_lower:
        return "вертикальный"
    elif "гор." in desc_lower:
        return "горизонтальный"
    elif "кв." in desc_lower:
        return "квадратный"
    else:
        # Если в описании нет указания типа, определяем по формату описания
        # Пакеты, которые начинаются с "Пакет д..." обычно квадратные
        if desc_lower.startswith("пакет д") and "ш" in desc_lower and "в" in desc_lower:
            # Проверяем, есть ли в описании указания на другие типы
            if "верт" not in desc_lower and "гор" not in desc_lower:
                return "квадратный"
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
    
    logger.info(f"🔍 Поиск {package_type} пакетов для {length}×{height}×{width} мм")
    
    for pkg_length, pkg_height, pkg_width, desc, _, _ in PACKAGES:
        current_type = get_package_type(desc)
        
        # Отладочная информация для квадратных пакетов
        if (pkg_length, pkg_height, pkg_width) in [(250, 250, 250), (220, 220, 120), (150, 150, 80)]:
            logger.info(f"🔍 Квадратный пакет {pkg_length}×{pkg_height}×{pkg_width}: '{desc}' -> тип='{current_type}'")
        
        if current_type != package_type:
            continue
            
        # Упрощенная логика поиска - проверяем каждый размер отдельно
        length_ok = abs(pkg_length - length) <= 50
        height_ok = abs(pkg_height - height) <= 50  
        width_ok = abs(pkg_width - width) <= 50
        
        if length_ok and height_ok and width_ok:
            total_diff = (abs(pkg_length - length) + 
                         abs(pkg_height - height) + 
                         abs(pkg_width - width))
            
            all_matching.append((pkg_length, pkg_height, pkg_width, desc, total_diff))
            
            logger.info(f"✅ Найден подходящий пакет: {pkg_length}×{pkg_height}×{pkg_width} - {desc}")
    
    logger.info(f"📊 Найдено {len(all_matching)} подходящих пакетов типа {package_type}")
    
    all_matching.sort(key=lambda x: x[4])
    return [(l, h, w, d) for l, h, w, d, _ in all_matching[:max_results]]

def find_matching_boxes(length, height, width, max_results=5):
    """Поиск коробок с отклонением до 30 мм"""
    all_matching = []
    
    logger.info(f"🔍 Поиск коробок для {length}×{height}×{width} мм")
    
    for box_length, box_height, box_width, desc, _, _, _ in BOXES:
        # Проверяем каждый размер отдельно с отклонением 30 мм
        length_ok = abs(box_length - length) <= 30
        height_ok = abs(box_height - height) <= 30  
        width_ok = abs(box_width - width) <= 30
        
        if length_ok and height_ok and width_ok:
            total_diff = (abs(box_length - length) + 
                         abs(box_height - height) + 
                         abs(box_width - width))
            
            all_matching.append((box_length, box_height, box_width, desc, total_diff))
            
            logger.info(f"✅ Найден подходящая коробка: {box_length}×{box_height}×{box_width} - {desc}")
    
    logger.info(f"📊 Найдено {len(all_matching)} подходящих коробок")
    
    all_matching.sort(key=lambda x: x[4])
    return [(l, h, w, d) for l, h, w, d, _ in all_matching[:max_results]]

def find_boxes_by_keyword(keyword, max_results=10):
    """Поиск коробок по ключевому слову или номеру штампа"""
    matching_boxes = []
    keyword_lower = keyword.lower()
    
    logger.info(f"🔍 Поиск коробок по ключевому слову: {keyword}")
    
    for box_length, box_height, box_width, desc, order_template, drawing_url, image_url in BOXES:
        # Ищем в описании и номере штампа
        if (keyword_lower in desc.lower() or 
            keyword in desc or  # для поиска номеров штампов
            (keyword_lower.isdigit() and f"штамп {keyword}" in desc.lower())):
            
            matching_boxes.append((box_length, box_height, box_width, desc, order_template, drawing_url, image_url))
            logger.info(f"✅ Найдена коробка по ключевому слову: {box_length}×{box_height}×{box_width} - {desc}")
    
    logger.info(f"📊 Найдено {len(matching_boxes)} коробок по ключевому слову '{keyword}'")
    
    return matching_boxes[:max_results]

def get_package_details(length, height, width, description):
    drawing_url = None
    order_template = ""
    for pkg_length, pkg_height, pkg_width, desc, order, url in PACKAGES:
        if (pkg_length == length and pkg_height == height and 
            pkg_width == width and desc == description):
            drawing_url = url
            order_template = order
            break
    
    if drawing_url:
        details = (
            "📋 <b>Детали пакета</b>\n\n"
            f"👜 Размер: {length} × {height} × {width} мм\n"
            f"📝 Описание: {description}\n"
            f"✅ <b>Заказ-шаблон</b>\n"
            f"{order_template}\n\n"
            "🔗 <b>Ссылка на чертеж:</b>\n"
            f"{drawing_url}"
        )
    else:
        details = (
            "📋 <b>Детали пакета</b>\n\n"
            f"👜 Размер: {length} × {height} × {width} мм\n"
            f"📝 Описание: {description}\n"
            f"✅ <b>Заказ-шаблон</b>\n"
            f"{order_template}\n\n"
            "⏳ <i>Информация о номере заказа-шаблона и ссылка на чертеж скоро появятся</i>"
        )
    
    return details, drawing_url

def get_box_details(length, height, width, description):
    drawing_url = None
    order_template = ""
    image_url = ""
    
    for box_length, box_height, box_width, desc, order, url, img_url in BOXES:
        if (box_length == length and box_height == height and 
            box_width == width and desc == description):
            drawing_url = url
            order_template = order
            image_url = img_url
            break
    
    # Добавляем (Ц) к названию если есть в описании
    display_name = description
    if "(Ц)" in description and " (Ц)" not in description:
        display_name = description.replace("(Ц)", " (Ц)")
    
    details = (
        "📋 <b>Детали коробки</b>\n\n"
        f"📦 Размер: {length} × {height} × {width} мм\n"
        f"📝 Описание: {display_name}\n"
    )
    
    if order_template and order_template != "-":
        details += f"✅ <b>Заказ-шаблон</b>\n{order_template}\n\n"
    else:
        details += "\n"
    
    if drawing_url:
        details += "🔐 <b>Чертеж доступен по паролю</b>"
    else:
        details += "⏳ <i>Информация о номере заказа-шаблона и ссылка на чертеж скоро появятся</i>"
    
    return details, drawing_url, image_url

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = """
👋 Привет! Я бот для поиска пакетов и коробок.

Выберите что вас интересует:
    """
    
    keyboard = [
        [InlineKeyboardButton("📦 Пакеты", callback_data="mode_packages")],
        [InlineKeyboardButton("📋 Коробки", callback_data="mode_boxes")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(welcome_text, reply_markup=reply_markup)

async def show_boxes_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает меню выбора типа коробок"""
    menu_text = """
📋 <b>Выберите тип коробок:</b>
    """
    
    keyboard = [
        [InlineKeyboardButton("📦 Однослойные пачки", callback_data="box_type_single_layer_packs")],
        [InlineKeyboardButton("📦 МГК самосборные", callback_data="box_type_mgk_self_assembly")],
        [InlineKeyboardButton("📦 МГК пачка", callback_data="box_type_mgk_pack")],
        [InlineKeyboardButton("📦 Однослойные самосборные", callback_data="box_type_single_layer_self_assembly")],
        [InlineKeyboardButton("📦 Однослойные крышка-дно", callback_data="box_type_single_layer_lid_bottom")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update, 'message'):
        await update.message.reply_html(menu_text, reply_markup=reply_markup)
    else:
        await update.edit_message_text(text=menu_text, parse_mode='HTML', reply_markup=reply_markup)

async def handle_single_layer_packs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик для однослойных пачек"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Сохраняем текущий тип коробок
        context.user_data['current_box_type'] = 'single_layer_packs'
        context.user_data['current_mode'] = 'boxes'
        
        instruction_text = """
📦 <b>Однослойные пачки</b>

📏 Отправьте мне размер коробки в формате:
   <b>длина ширина высота</b>
   
Например: <code>100 100 100</code>

❗ <b>Порядок размеров:</b> длина × ширина × высота

Я найду ближайшие коробки (отклонение до 30 мм).

Либо введите номер штампа или ключевое слово.
К примеру "с окном" или "с европодвесом"
        """
        
        # Добавляем изображение в то же сообщение (встроенное)
        image_url = "https://disk.yandex.ru/i/ord28hnNORnJDg"
        
        keyboard = [
            [InlineKeyboardButton("⬅️ Назад к типам коробок", callback_data="back_to_box_types")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем сообщение с изображением
        await query.message.reply_photo(
            photo=image_url,
            caption=instruction_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        
        # Удаляем предыдущее сообщение с меню
        await query.message.delete()
        
    except Exception as e:
        logger.error(f"Error in handle_single_layer_packs: {e}")

async def handle_box_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстового ввода для коробок"""
    try:
        text = update.message.text.strip()
        logger.info(f"Получено сообщение для коробок: {text}")
        
        # Проверяем, что пользователь в режиме коробок
        if context.user_data.get('current_mode') != 'boxes':
            return
        
        # Проверяем, является ли ввод ключевым словом (не только цифры)
        if not re.match(r'^\d+\s+\d+\s+\d+$', text):
            # Это ключевое слово, а не три числа
            await handle_box_keyword_search(update, context, text)
            return
        
        # Оригинальная логика для размеров
        cleaned_text = re.sub(r'[^\d\s]', ' ', text)
        numbers = re.findall(r'\d+', cleaned_text)
        
        logger.info(f"Найдены числа для коробок: {numbers}")
        
        if len(numbers) < 3:
            await update.message.reply_html(
                "❌ Введите три числа: <b>длина ширина высота</b>\n"
                "Например: <code>100 100 100</code>\n\n"
                "Либо введите номер штампа или ключевое слово."
            )
            return

        length, width, height = map(int, numbers[:3])
        logger.info(f"Распознаны размеры коробки: {length}×{width}×{height}")
        
        context.user_data['original_box_sizes'] = (length, width, height)
        
        await show_box_search_results(update, context, length, width, height)
        
    except Exception as e:
        logger.error(f"Error in handle_box_text_input: {e}")
        await update.message.reply_html(
            "❌ Ошибка. Введите размеры в формате: <code>длина ширина высота</code>\n"
            "Например: <code>100 100 100</code>\n\n"
            "Либо введите номер штампа или ключевое слово."
        )

async def handle_box_keyword_search(update: Update, context: ContextTypes.DEFAULT_TYPE, keyword: str):
    """Обработчик поиска коробок по ключевому слову"""
    try:
        matching_boxes = find_boxes_by_keyword(keyword, max_results=10)
        
        if matching_boxes:
            response = f"<b>📦 Результаты поиска по запросу:</b> \"{keyword}\"\n\n"
            
            keyboard = []
            
            for i, (length, height, width, desc, _, _, _) in enumerate(matching_boxes, 1):
                # Форматируем описание для отображения
                display_desc = desc
                if "(Ц)" in desc and " (Ц)" not in desc:
                    display_desc = desc.replace("(Ц)", " (Ц)")
                
                response += f"{i}. {length} × {width} × {height} мм\n   {display_desc}\n\n"
                
                # Создаем кнопку с указанием (Ц) если есть
                button_text = f"📦 Коробка {i}: {length}×{width}×{height} мм"
                if "(Ц)" in desc:
                    button_text += " (Ц)"
                    
                callback_data = f"box_{length}_{width}_{height}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
            
            keyboard.append([InlineKeyboardButton("⬅️ Назад к типам коробок", callback_data="back_to_box_types")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_html(response, reply_markup=reply_markup)
        else:
            response = f"❌ По запросу \"{keyword}\" коробки не найдены.\n\n"
            response += "Попробуйте другой запрос или введите размеры в формате: <code>длина ширина высота</code>"
            
            keyboard = [[InlineKeyboardButton("⬅️ Назад к типам коробок", callback_data="back_to_box_types")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_html(response, reply_markup=reply_markup)
            
    except Exception as e:
        logger.error(f"Error in handle_box_keyword_search: {e}")
        await update.message.reply_html("❌ Произошла ошибка при поиске. Попробуйте еще раз.")

async def show_box_search_results(update, context, length, width, height):
    """Показывает результаты поиска коробок"""
    try:
        context.user_data['current_box_sizes'] = (length, width, height)
        
        matching_boxes = find_matching_boxes(length, width, height, max_results=5)
        
        response = f"<b>📦 Однослойные пачки</b> для {length}×{width}×{height} мм (Д×Ш×В, отклонение ±30 мм):\n\n"
        
        if matching_boxes:
            keyboard = []
            
            for i, (l, w, h, d) in enumerate(matching_boxes, 1):
                # Форматируем описание для отображения
                display_desc = d
                if "(Ц)" in d and " (Ц)" not in d:
                    display_desc = d.replace("(Ц)", " (Ц)")
                
                response += f"{i}. {l} × {w} × {h} мм\n   {display_desc}\n\n"
                
                # Создаем кнопку с указанием (Ц) если есть
                button_text = f"📦 Коробка {i}: {l}×{w}×{h} мм"
                if "(Ц)" in d:
                    button_text += " (Ц)"
                    
                callback_data = f"box_{l}_{w}_{h}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
            
            keyboard.append([InlineKeyboardButton("⬅️ Назад к типам коробок", callback_data="back_to_box_types")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if hasattr(update, 'message'):
                await update.message.reply_html(response, reply_markup=reply_markup)
            else:
                await update.edit_message_text(text=response, parse_mode='HTML', reply_markup=reply_markup)
        else:
            response += "❌ Коробки не найдены\n\n"
            response += "Попробуйте ввести другой размер или поискать по ключевому слову."
            
            keyboard = [[InlineKeyboardButton("⬅️ Назад к типам коробок", callback_data="back_to_box_types")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if hasattr(update, 'message'):
                await update.message.reply_html(response, reply_markup=reply_markup)
            else:
                await update.edit_message_text(text=response, parse_mode='HTML', reply_markup=reply_markup)
                
    except Exception as e:
        logger.error(f"Error in show_box_search_results: {e}")
        error_msg = "❌ Произошла ошибка при поиске коробок. Попробуйте еще раз."
        if hasattr(update, 'message'):
            await update.message.reply_html(error_msg)
        else:
            await update.edit_message_text(text=error_msg, parse_mode='HTML')

async def handle_box_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик клика по коробке - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    try:
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data.startswith("box_"):
            parts = callback_data.split("_")
            if len(parts) == 4:
                length = int(parts[1])
                width = int(parts[2])
                height = int(parts[3])
                
                description = ""
                image_url = ""
                drawing_url = ""
                
                # Ищем коробку по размерам - ИСПРАВЛЕННАЯ ЛОГИКА
                for box_length, box_width, box_height, desc, _, draw_url, img_url in BOXES:
                    if (box_length == length and 
                        box_width == width and 
                        box_height == height):
                        description = desc
                        image_url = img_url
                        drawing_url = draw_url
                        break
                
                if not description:
                    await query.answer("❌ Коробка не найдена", show_alert=True)
                    return
                
                details, _, _ = get_box_details(length, width, height, description)
                
                keyboard = []
                
                # Сохраняем последний поиск для кнопки "Назад"
                current_sizes = context.user_data.get('current_box_sizes', (0, 0, 0))
                context.user_data['last_box_search_sizes'] = current_sizes
                
                # Сохраняем информацию о коробке для скачивания
                context.user_data['last_box_details'] = {
                    'length': length,
                    'width': width,
                    'height': height,
                    'description': description,
                    'drawing_url': drawing_url
                }
                
                keyboard.append([InlineKeyboardButton("⬅️ Вернуться к коробкам пачкам", callback_data="back_to_last_box_search")])
                
                # ВСЕГДА показываем кнопку скачивания чертежа если есть чертеж
                if drawing_url and drawing_url.strip():
                    keyboard.append([InlineKeyboardButton("🔐 Скачать чертеж коробки", callback_data=f"download_box_{length}_{width}_{height}")])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Если есть изображение, отправляем его встроенным
                if image_url and image_url.strip():
                    await query.message.reply_photo(
                        photo=image_url,
                        caption=details,
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
                else:
                    await query.message.reply_html(
                        text=details,
                        reply_markup=reply_markup
                    )
                    
                # Удаляем предыдущее сообщение с результатами поиска
                await query.message.delete()
                        
    except Exception as e:
        logger.error(f"Error in handle_box_click: {e}")

async def handle_box_download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик скачивания чертежа коробки с паролем"""
    try:
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data.startswith("download_box_"):
            parts = callback_data.split("_")
            if len(parts) == 5:
                length = int(parts[2])
                width = int(parts[3])
                height = int(parts[4])
                
                # Находим информацию о коробке
                box_info = None
                for box_length, box_width, box_height, desc, _, draw_url, img_url in BOXES:
                    if box_length == length and box_width == width and box_height == height:
                        box_info = {
                            'length': length,
                            'width': width,
                            'height': height,
                            'description': desc,
                            'drawing_url': draw_url
                        }
                        break
                
                if not box_info:
                    await query.answer("❌ Информация о коробке не найдена", show_alert=True)
                    return
                
                # Сохраняем информацию о коробке для проверки пароля
                context.user_data['pending_download'] = box_info
                
                # Запрашиваем пароль
                password_text = """
🔐 <b>Для доступа к чертежу введите пароль:</b>

Введите пароль в текстовом сообщении.
                """
                
                keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_box_details")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Отправляем новое сообщение вместо редактирования
                await query.message.reply_html(
                    text=password_text,
                    reply_markup=reply_markup
                )
            
    except Exception as e:
        logger.error(f"Error in handle_box_download: {e}")

async def handle_password_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ввода пароля для коробок"""
    try:
        text = update.message.text.strip()
        
        # Проверяем, есть ли ожидаемая загрузка
        pending_download = context.user_data.get('pending_download')
        if not pending_download:
            return
        
        if text == "2233":
            # Пароль верный
            length = pending_download['length']
            width = pending_download['width']
            height = pending_download['height']
            description = pending_download['description']
            drawing_url = pending_download['drawing_url']
            
            if drawing_url and drawing_url.strip():
                success_text = f"""
✅ <b>Пароль верный!</b>

📦 <b>Коробка:</b> {length}×{width}×{height} мм
📝 <b>Описание:</b> {description}

🔗 <b>Ссылка на чертеж:</b>
{drawing_url}
                """
                
                keyboard = [
                    [InlineKeyboardButton("⬅️ Вернуться к коробкам пачкам", callback_data="back_to_last_box_search")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_html(success_text, reply_markup=reply_markup)
                
                # Очищаем ожидаемую загрузку
                context.user_data.pop('pending_download', None)
            else:
                await update.message.reply_html("❌ Чертеж для этой коробки не найден.")
        else:
            await update.message.reply_html("❌ Неверный пароль. Попробуйте еще раз.")
            
    except Exception as e:
        logger.error(f"Error in handle_password_input: {e}")

async def handle_back_to_box_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Возврат к деталям коробки"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Восстанавливаем детали коробки из сохраненных данных
        last_box_details = context.user_data.get('last_box_details')
        if last_box_details:
            length = last_box_details['length']
            width = last_box_details['width']
            height = last_box_details['height']
            description = last_box_details['description']
            drawing_url = last_box_details['drawing_url']
            
            # Находим изображение
            image_url = ""
            for box_length, box_width, box_height, desc, _, _, img_url in BOXES:
                if box_length == length and box_width == width and box_height == height and desc == description:
                    image_url = img_url
                    break
            
            details, _, _ = get_box_details(length, width, height, description)
            
            keyboard = []
            keyboard.append([InlineKeyboardButton("⬅️ Вернуться к коробкам пачкам", callback_data="back_to_last_box_search")])
            
            # ВСЕГДА показываем кнопку скачивания чертежа если есть чертеж
            if drawing_url and drawing_url.strip():
                keyboard.append([InlineKeyboardButton("🔐 Скачать чертеж коробки", callback_data=f"download_box_{length}_{width}_{height}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Если есть изображение, отправляем его встроенным
            if image_url and image_url.strip():
                await query.message.reply_photo(
                    photo=image_url,
                    caption=details,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            else:
                await query.message.reply_html(
                    text=details,
                    reply_markup=reply_markup
                )
            
    except Exception as e:
        logger.error(f"Error in handle_back_to_box_details: {e}")

async def handle_back_to_last_box_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Возврат к последнему поиску коробок"""
    try:
        query = update.callback_query
        await query.answer()
        
        last_sizes = context.user_data.get('last_box_search_sizes')
        
        if last_sizes:
            length, width, height = last_sizes
            await show_box_search_results(query, context, length, width, height)
        else:
            await show_boxes_menu(query, context)
            
    except Exception as e:
        logger.error(f"Error in handle_back_to_last_box_search: {e}")

async def handle_mode_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик выбора режима (пакеты/коробки)"""
    try:
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data == "mode_packages":
            context.user_data['current_mode'] = 'packages'
            welcome_text = """
📦 <b>Режим поиска пакетов</b>

📏 Отправьте мне размер пакета в формате:
   <b>длина высота ширина</b>
   
Например: <code>200 250 100</code>

❗ <b>Порядок размеров:</b> длина × высота × ширина

Я найду ближайшие пакеты (отклонение до 50 мм).
            """
            keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text=welcome_text, parse_mode='HTML', reply_markup=reply_markup)
            
        elif callback_data == "mode_boxes":
            context.user_data['current_mode'] = 'boxes'
            await show_boxes_menu(query, context)
            
    except Exception as e:
        logger.error(f"Error in handle_mode_selection: {e}")

async def handle_back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Возврат в главное меню"""
    try:
        query = update.callback_query
        await query.answer()
        
        await start(query, context)
        
    except Exception as e:
        logger.error(f"Error in handle_back_to_main: {e}")

async def handle_back_to_box_types(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Возврат к выбору типа коробок"""
    try:
        query = update.callback_query
        await query.answer()
        
        await show_boxes_menu(query, context)
        
    except Exception as e:
        logger.error(f"Error in handle_back_to_box_types: {e}")

# Оригинальные функции для пакетов (без изменений)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Проверяем режим работы
        current_mode = context.user_data.get('current_mode', 'packages')
        
        if current_mode == 'boxes':
            await handle_box_text_input(update, context)
        else:
            # Оригинальная логика для пакетов
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
            response = f"<b>{type_display.capitalize()} пакеты</b> для {length}×{height}×{width} мм (Д×В×Ш):\n\n"
        else:
            response = f"<b>{type_display.capitalize()} пакеты</b> для {length}×{height}×{width} мм (Д×В×Ш, отклонение ±50 мм):\n\n"
        
        if matching_packages:
            keyboard = []
            
            for i, (l, h, w, d) in enumerate(matching_packages, 1):
                response += f"{i}. {l} × {h} × {w} мм\n   {d}\n\n"
                callback_data = f"package_{l}_{h}_{w}"
                keyboard.append([InlineKeyboardButton(f"👜 Пакет {i}: {l}×{h}×{w} мм", callback_data=callback_data)])
            
            alt_length, alt_height = height, length
            
            if search_type == "горизонтальный":
                alt_type_display = "вертикальные"
                alt_type = "вертикальный"
            else:
                alt_type_display = "горизонтальные"
                alt_type = "горизонтальный"
            
            alt_callback = f"alternative_{alt_length}_{alt_height}_{width}_{alt_type}"
            keyboard.append([InlineKeyboardButton(f"🔍 Показать {alt_type_display}", callback_data=alt_callback)])
            keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")])
            
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
            
            keyboard = [
                [InlineKeyboardButton(f"🔍 Показать {alt_type_display}", callback_data=f"alternative_{alt_length}_{alt_height}_{width}_{alt_type}")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
            ]
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
                for pkg_length, pkg_height, pkg_width, desc, _, _ in PACKAGES:
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
                keyboard.append([InlineKeyboardButton("⬅️ В главное меню", callback_data="back_to_main")])
                
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

1️⃣ Отправьте /start для выбора режима (пакеты/коробки)
2️⃣ Для пакетов: отправьте размер в формате <code>длина высота ширина</code>  
3️⃣ Для коробок: выберите тип коробок и введите размеры
4️⃣ Бот подберёт ближайшие варианты
5️⃣ Нажмите на любой вариант, чтобы увидеть детали
6️⃣ Используйте кнопки для навигации

<b>Примеры для пакетов:</b>  
<code>200 250 100</code>  
<code>300 400 150</code>  

<b>Примеры для коробок:</b>
<code>100 100 100</code>
<code>120 58 150</code>

Бот автоматически определит тип пакета и предложит альтернативные варианты!
    """)

# Регистрируем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))

# Обработчики callback запросов
application.add_handler(CallbackQueryHandler(handle_mode_selection, pattern="^mode_"))
application.add_handler(CallbackQueryHandler(handle_back_to_main, pattern="^back_to_main$"))
application.add_handler(CallbackQueryHandler(handle_back_to_box_types, pattern="^back_to_box_types$"))
application.add_handler(CallbackQueryHandler(handle_single_layer_packs, pattern="^box_type_single_layer_packs$"))
application.add_handler(CallbackQueryHandler(handle_box_click, pattern="^box_"))
application.add_handler(CallbackQueryHandler(handle_box_download, pattern="^download_box_"))
application.add_handler(CallbackQueryHandler(handle_back_to_box_details, pattern="^back_to_box_details$"))
application.add_handler(CallbackQueryHandler(handle_back_to_last_box_search, pattern="^back_to_last_box_search$"))

# Обработчики для неактивных кнопок коробок
application.add_handler(CallbackQueryHandler(lambda u, c: u.callback_query.answer("🚧 Этот раздел скоро будет доступен!", show_alert=True), 
                                           pattern="^box_type_mgk_"))
application.add_handler(CallbackQueryHandler(lambda u, c: u.callback_query.answer("🚧 Этот раздел скоро будет доступен!", show_alert=True), 
                                           pattern="^box_type_single_layer_"))

# Оригинальные обработчики пакетов
application.add_handler(CallbackQueryHandler(handle_package_click, pattern="^package_"))
application.add_handler(CallbackQueryHandler(handle_alternative_search, pattern="^alternative_"))
application.add_handler(CallbackQueryHandler(handle_back_to_last_search, pattern="^back_to_last_search$"))

# Обработчики текстовых сообщений - ОСНОВНОЙ обработчик
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# Обработчик ввода пароля для коробок - В ОТДЕЛЬНОЙ ГРУППЕ с более высоким приоритетом
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password_input), group=1)

# Запуск бота
async def main():
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    logger.info("✅ Бот запущен в режиме polling!")
    
    # Бесконечный цикл
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())