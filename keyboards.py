import telebot
from telebot import types

back_button = types.KeyboardButton("Назад")

reg_keyboard = types.ReplyKeyboardMarkup( one_time_keyboard=True, resize_keyboard=True)
reg_yes_or_no = types.ReplyKeyboardMarkup( one_time_keyboard=True, resize_keyboard=True)
reg_button = types.KeyboardButton("Регистрация")
reg_reloginA = types.KeyboardButton("Да🟢")
reg_reloginB = types.KeyboardButton("Нет❌")

reg_yes_or_no.add(reg_reloginA,reg_reloginB)
reg_keyboard.add(reg_button)

mein_meny_keybord = types.ReplyKeyboardMarkup( one_time_keyboard=True, resize_keyboard=True)
creat_group_button = types.KeyboardButton("Создать группу ➕")
find_group_button = types.KeyboardButton("Найти группу 🔍") 
mein_meny_keybord.add(find_group_button).add(creat_group_button)

distr_keybord = types.ReplyKeyboardMarkup( one_time_keyboard=True)
d1_button = types.KeyboardButton("Заводской") 
d2_button = types.KeyboardButton("Центральный")
d3_button = types.KeyboardButton("Советский")
d4_button = types.KeyboardButton("Первомайский")
d5_button = types.KeyboardButton("Партизанский")
d6_button = types.KeyboardButton("Ленинский")
d7_button = types.KeyboardButton("Октябрьский")
d8_button = types.KeyboardButton("Московский")
d9_button = types.KeyboardButton("Фрунзенский")
distr_keybord.add(d1_button,d2_button,d3_button).add(d4_button,d5_button,d6_button).add(d7_button,d8_button,d9_button).add(back_button)

kind_ex_keybord = types.ReplyKeyboardMarkup( one_time_keyboard=True, resize_keyboard=True)
k1_button = types.KeyboardButton("🏀Баскетбол")
k2_button = types.KeyboardButton("🏐Волейбол")
k3_button = types.KeyboardButton("⚽Футбол")
k4_button = types.KeyboardButton("🏃Бег")
k5_button = types.KeyboardButton("🛼Ролики")
k6_button = types.KeyboardButton("🚴Велосипед")
k7_button = types.KeyboardButton("🏋Воркаут")
kind_ex_keybord.add(k1_button , k4_button, k2_button).add(k3_button, k5_button, k6_button).add(k7_button,back_button)

wait_room = types.ReplyKeyboardMarkup( one_time_keyboard=True, resize_keyboard=True)
wait_but1 = types.KeyboardButton("📃Список участников")
wait_but2 = types.KeyboardButton("❌Удалить группу")
wait_room.add(wait_but1).add(wait_but2)

vbor = types.ReplyKeyboardMarkup( one_time_keyboard=True, resize_keyboard=True)
vbor.add(back_button)

invite_room = types.ReplyKeyboardMarkup( one_time_keyboard=True, resize_keyboard=True)
invite_but1 = types.KeyboardButton("📃Список участников")
invite_but2 = types.KeyboardButton("❌Покинуть группу")
invite_room.add(invite_but1).add(invite_but2)
