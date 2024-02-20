import logging

from aiogram import executor

from create_bot import dp
from handlers import users, colors, choose_dialog, add_dialog

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s",
                    force=True)

users.register_user_handlers(dp)
colors.register_colors_handler(dp)
choose_dialog.register_choose_dialog_handlers(dp)
add_dialog.register_add_handlers(dp)

async def on_startup(_):
    logging.info('Bot is online!')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
