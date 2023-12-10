from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler, CallbackContext

# Ваш токен бота
TOKEN = '6623459023:AAFXeS69m0lz1emLLnfgnnH-Y3W97imrzBI'

# Состояния для конечного автомата
CATEGORY, ANKETA, QUESTION, ERROR_REPORT = range(4)

# Обработка команды /start
def start(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Анкета", callback_data=str(ANKETA)),
         InlineKeyboardButton("Вопрос", callback_data=str(QUESTION))],
        [InlineKeyboardButton("Сообщить об ошибке бота", callback_data=str(ERROR_REPORT))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("Приветствую, выбери категорию своего сообщения", reply_markup=reply_markup)

    return CATEGORY

# Обработка инлайн кнопок
def button(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    category = query.data

    if category == str(ANKETA):
        query.edit_message_text(text="Отправь свою анкету")
        context.user_data['category'] = 'Анкета'
        return ANKETA
    elif category == str(QUESTION):
        query.edit_message_text(text="Отправь свой вопрос")
        context.user_data['category'] = 'Вопрос'
        return QUESTION
    elif category == str(ERROR_REPORT):
        query.edit_message_text(text="Отправь скриншот с описанием ошибки")
        context.user_data['category'] = 'Ошибка'
        return ERROR_REPORT

# Обработка текстовых сообщений
def handle_text(update: Update, context: CallbackContext) -> int:
    user_message = update.message.text
    user_category = context.user_data.get('category')

    if not user_category:
        update.message.reply_text("Извините, для начала выберите категорию.")
        return CATEGORY

    # Отправка сообщения в группу
    try:
        group_chat_id = '-1001404105612'  # ID основной группы
        context.bot.forward_message(chat_id=group_chat_id, from_chat_id=update.message.chat_id, message_id=update.message.message_id)

        # Отправка сообщения о успешной отправке
        success_message = f"{user_category} успешно отправлен(а) владельцу!"
        update.message.reply_text(success_message)

    except Exception as e:
        update.message.reply_text(f"Произошла ошибка при отправке сообщения в группу: {e}")

    # Сброс данных пользователя после успешной отправки анкеты
    context.user_data.clear()

    return ConversationHandler.END

# Обработка медиа-контента (фото, документы)
def handle_media(update: Update, context: CallbackContext) -> int:
    user_category = context.user_data.get('category')

    if not user_category:
        update.message.reply_text("Извините, для начала выберите категорию.")
        return CATEGORY

    # Отправка медиа-контента в группу
    try:
        group_chat_id = '-1001404105612'  # ID основной группы
        context.bot.forward_message(chat_id=group_chat_id, from_chat_id=update.message.chat_id, message_id=update.message.message_id)

        # Отправка сообщения о успешной отправке медиа-контента
        success_message = f"{user_category} успешно отправлен(а) владельцу!"
        update.message.reply_text(success_message)
    except Exception as e:
        update.message.reply_text(f"Произошла ошибка при отправке медиа-контента в группу: {e}")

    return ConversationHandler.END

# Главная функция
def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CATEGORY: [CallbackQueryHandler(button, pattern='^' + str(ANKETA) + '$|^' + str(QUESTION) + '$|^' + str(ERROR_REPORT) + '$')],
            ANKETA: [MessageHandler(Filters.text & ~Filters.command, handle_text)],
            QUESTION: [MessageHandler(Filters.text & ~Filters.command, handle_text)],
            ERROR_REPORT: [MessageHandler(Filters.photo | Filters.document, handle_media)],
        },
        fallbacks=[]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()