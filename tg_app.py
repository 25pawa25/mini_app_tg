import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext, Application
import json
from dotenv import load_dotenv


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def load_discounts(filename="psn_discounts.json"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл {filename} не найден.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Ошибка декодирования JSON в файле {filename}: {e}")


async def start(update: Update, context: CallbackContext):
    games = load_discounts()
    buttons = []

    for game in games:
        buttons.append([
            InlineKeyboardButton(
                f"{game['title']} - {game['discount']}%",
                callback_data=f"details_{games.index(game)}"
            )
        ])

    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Скидки на игры в PSN Store:", reply_markup=keyboard)


async def show_details(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    game_index = int(query.data.split("_")[1])
    games = load_discounts()
    game = games[game_index]

    details = (
        f"Название: {game['title']}\n"
        f"Текущая цена: {game['current_price']}\n"
        f"Старая цена: {game['old_price']}\n"
        f"Скидка: {game['discount']}\n"
        f"Дата окончания: {game['end_date']}\n"
        f"[Ссылка на игру]({game['link']})"
    )

    await query.edit_message_text(details, parse_mode="Markdown")


async def filter_discounts(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        await update.message.reply_text("Использование: /filter <процент_скидки>")
        return

    try:
        min_discount = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Введите число для фильтрации.")
        return

    games = load_discounts()
    filtered_games = [game for game in games if int(game['discount'].replace('%', '')) >= min_discount]

    if not filtered_games:
        await update.message.reply_text(f"Нет игр со скидкой выше {min_discount}%.")
        return

    buttons = []
    for game in filtered_games:
        buttons.append([
            InlineKeyboardButton(
                f"{game['title']} - {game['discount']}%",
                callback_data=f"details_{games.index(game)}"
            )
        ])

    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Игры с заданным уровнем скидки:", reply_markup=keyboard)


def main():
    TOKEN = os.getenv("BOT_API_KEY", "key")
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(show_details, pattern="^details_"))
    application.add_handler(CommandHandler("filter", filter_discounts))

    application.run_polling()


if __name__ == "__main__":
    main()
