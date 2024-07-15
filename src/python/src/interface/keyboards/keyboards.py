from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton("За останні 24 години", callback_data="action1")
    button2 = InlineKeyboardButton("За останні три дні", callback_data="action2")
    button3 = InlineKeyboardButton("За останній тиждень", callback_data="action3")
    keyboard.add(button1, button2, button3)
    return keyboard
