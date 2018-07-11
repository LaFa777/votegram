import settings

from telegram.ext import Updater

from src import Application

if __name__ == "__main__":
    # Create the Updater and pass it your bot's token.
    updater = Updater(settings.TOKEN, request_kwargs={
        "proxy_url": settings.SOCKS_URL,
        "urllib3_proxy_kwargs": {
            'username': settings.SOCKS_USER,
            'password': settings.SOCKS_PASS,
            },
        })

    app = Application(updater)
    app.run()
