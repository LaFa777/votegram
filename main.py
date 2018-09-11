import logging

from telegram.ext import Updater

import settings

from votegram import Application

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

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
