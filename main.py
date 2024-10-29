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
    ],
    "Шутки на разные темы": [
        "Почему программисту не нравится природа? Слишком много ошибок!",
        "Опаздывать надо не спеша. Зачем торопиться опаздывать?",
        "Если бы люди могли летать как птицы, то производство рогаток резко бы возросло.",
        "Едет Путин в трамвае…",
        "Эстонские ПВО не верят в существование сверхзвуковых самолетов.",
    ],
    "Шутки про студентов": [
        "Студент Иванов завалил экзамен по математике, но так изворотливо это отрицал, что сдал экзамен по философии.",
        "Все, кого завкафедры знает лично в лицо, это либо будущие аспиранты, либо будущие солдаты.",
        "Содрал с одной работы — плагиат, с двух — реферат, с трех — аналитика на диплом.",
        "'Хорошо!' - сказал профессор и испортил студенту красный диплом.",
    ],
}

favorite_jokes: List[str] = []

reply_keyboard = [
    ["Шутки про Штирлица", "Шутки про программистов", "Шутки про студентов"],
    ["Добавить в избранное", "Показать избранное", "Закончить"],
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


async def choose_joke(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Выбор шутки из выбранной категории."""
    category = update.message.text
    if category in jokes:
        joke = random.choice(jokes[category])
        await update.message.reply_text(f"Внимание, анекдот: {joke}")
    elif category == "Добавить в избранное":
        await update.message.reply_text("Выберите мою великолепную шутку, которая не оставила вас равнодущным (добавить в избранное).")
        return FAVORITE
    elif category == "Показать избранное":
        await update.message.reply_text("Мои лучщие анекдоты:\n" + "\n".join(favorite_jokes) if favorite_jokes else "У вас пока нет любимых анекдотов, грустный вы человек:(")
    
    return CHOOSING


async def add_to_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Добавление шутки в избранное."""
    joke = update.message.text
    favorite_jokes.append(joke)
    await update.message.reply_text(f"Идеальное дополнение к коллекции: {joke}")
    return CHOOSING


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершить разговор."""
    await update.message.reply_text("Я ещё многое мог, но доказать мне не дали...", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main() -> None:
    """Запуск бота."""
    persistence = PicklePersistence(filepath="data/data", single_file=False)
    application = Application.builder().token("8122266381:AAGY-nR2Z5hyCUKK52or4jCO0BwSIswZOwg").persistence(persistence).build()

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
        fallbacks=[MessageHandler(filters.Regex("^Закончить$"), done)],
    )

    application.add_handler(conv_handler)

    async def post_init(application: Application) -> None:
        bot_commands = [
            BotCommand("start", "Начало работы с ботом"),
        ]
        await application.bot.set_my_commands(bot_commands)

    application.post_init(post_init)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()