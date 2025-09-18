import os
from flask import Flask
from telebot import TeleBot, types

from config import BOT_TOKEN, PORT, HOST, BASE_PATH
from models import db

bot = TeleBot(BOT_TOKEN)


def create_app():
    app = Flask(
        "TG Pass",
        template_folder=os.path.join(BASE_PATH, "templates"),
        static_folder=os.path.join(BASE_PATH, "static"),
    )

    from routes import blueprint

    app.register_blueprint(blueprint)

    @app.before_request
    def _db_connect():
        if db.is_closed():
            db.connect()

    @app.teardown_request
    def _db_close(exc):
        if not db.is_closed():
            db.close()

    return app


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(
        text="Open Mini App",
        url=f"https://ruzzia.app/?telegram_id={message.chat.id}",
    )
    markup.add(btn)
    bot.send_message(
        message.chat.id,
        "Click the button below to open the mini app:",
        reply_markup=markup,
    )


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host=HOST, port=PORT)
