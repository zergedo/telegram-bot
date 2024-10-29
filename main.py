#!/usr/bin/python
# pylint: disable=unused-argument

import os
import logging
import random
from typing import Dict, List

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE, FAVORITE = range(4)

jokes = {
    "Шутки про Штирлица": [
        "Штирлиц знал наверняка. Наверняк не знал Штирлица.",
        "Штирлиц стрелял вслепую. Слепая отпрыгнула и стала отстреливаться.",
        "Штирлиц вошёл в лес. Посмотрел направо нет грибов, посмотрел налево нет грибов. Наверно не сезон подумал Штирлиц и сел в сугроб.",
        "Штирлиц вошёл в комнату, из окна дуло. Штирлиц закрыл окно, дуло исчезло.",
        "В попыхах Штирлиц оставил секретные документы. На следующий день в Попыхи нагрянуло Гестапо.",
        "До Штирлица не дошло письмо из центра. Он его еще раз перечитал, но все равно не дошло.",
        "Штирлиц вёл двойную жизнь и очень надеялся, что хоть одна из них сложится удачно.",
        "Штирлиц безуспешно пытался установить личность. Личность всё время падала.",
        "Штирлиц всегда спал как убитый. Его даже пару раз обводили мелом...",
        "Штирлиц стоял над картой мира. Его неудержимо рвало на родину.",
        "Штирлиц увидел на окне 38 утюгов и понял, что явка провалена.",
    ],
    "Шутки на разные темы": [
        "Почему программисту не нравится природа? Слишком много ошибок!",
        "Опаздывать надо не спеша. Зачем торопиться опаздывать?",
        "Если бы люди могли летать как птицы, то производство рогаток резко бы возросло.",
        "Едет Путин в трамвае…",
        "Эстонские ПВО не верят в существование сверхзвуковых самолетов.",
        "Я шофеp, и мне довольно часто пpиходится встpечаться с людьми, когда езжу по тpотуаpам.",
        "Пришёл счёт за свет в конце тоннеля.",
        "На чемпионате мира группа немецких биатлонистов завоевала Польшу.",
    ],
    "Шутки про студентов": [
        "Студент Иванов завалил экзамен по математике, но так изворотливо это отрицал, что сдал экзамен по философии.",
        "Все, кого завкафедры знает лично в лицо, это либо будущие аспиранты, либо будущие солдаты.",
        "Содрал с одной работы — плагиат, с двух — реферат, с трех — аналитика на диплом.",
        "'Хорошо!' - сказал профессор и испортил студенту красный диплом.",
        "Самая большая студенческая ложь: 'Список использованной литературы'.",
        "Нравится мне позиция нашего министра образования - я тоже терпеть не могу всех этих шибко грамотных...",
        "Студент выучил все билеты по философии, но не пошёл на экзамен, потому что жизнь не имеет смысла и все люди в ней пешки.",
    ],
}

favorite_jokes: List[str] = []

reply_keyboard = [
    ["Шутки про Штирлица", "Шутки на разные темы", "Шутки про студентов"],
    ["Добавить в избранное", "Показать избранное"],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начать разговор и представить варианты выбора."""
    user = update.message.from_user
    logger.info(f"Пользователь {user.full_name} начал работу.")
    
    await update.message.reply_text(
        "Приветствую! Я, по моему скромному мнению, лучший бот для анекдотов на просторах Интернета. Прошу, выберите тему для моей невероятной шутки:",
        reply_markup=markup,
    )

    return CHOOSING

favorite_jokes: set[str] = set()

async def choose_joke(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Выбор шутки из выбранной категории."""
    category = update.message.text
    if category in jokes:
        joke = random.choice(jokes[category])
        await update.message.reply_text(f"{joke}")
        context.user_data['last_joke'] = joke  
    elif category == "Добавить в избранное":
        last_joke = context.user_data.get('last_joke')
        if last_joke and last_joke not in favorite_jokes:
            favorite_jokes.add(last_joke)
            await update.message.reply_text(f"Отличный выбор: {last_joke}")
        else:
            await update.message.reply_text("Ты его уже добавлял, разве нет?")
    elif category == "Показать избранное":
        await update.message.reply_text("Мои лучшие анекдоты:\n" + "\n".join(favorite_jokes) if favorite_jokes else "У вас пока нет любимых анекдотов, грустный вы человек:(")
    
    return CHOOSING

async def add_to_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Добавление шутки в избранное."""
    joke = update.message.text
    favorite_jokes.append(joke)
    await update.message.reply_text(f"Идеальное дополнение к коллекции: {joke}", reply_markup=markup)
    return CHOOSING

def main() -> None:
    """Запуск бота."""
    persistence = PicklePersistence(filepath="data/data", single_file=False)
    application = Application.builder().token("8122266381:AAGY-nR2Z5hyCUKK52or4jCO0BwSIswZOwg").persistence(persistence).build()

    bot_commands = [
        BotCommand("start", "Начало работы с ботом"),
    ]
    application.bot.set_my_commands(bot_commands)

    conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSING: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, choose_joke),
        ],
        FAVORITE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_to_favorites),
        ],
    },
    fallbacks=[],
)

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
