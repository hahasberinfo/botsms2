import telebot
from telebot import types

admin = telebot.types.ReplyKeyboardMarkup(True)
admin.row('🌎 Количество пользователей','Рассылка')
admin.row('Добавить баланс','Изменить прайс')
admin.row('Добавление','Удаление')
admin.row('Изменить номер','Изменить токен')
admin.row('Изменить номер отправки')


main = telebot.types.ReplyKeyboardMarkup(True)
main.row('📤 Отправить сообщение')
main.row('🖥 Кабинет','📜 Информация')


otmena = telebot.types.ReplyKeyboardMarkup(True)
otmena.row('Отмена')

otziv = telebot.types.ReplyKeyboardMarkup(True)
otziv.row('Да', 'Нет')
