# -*- coding: utf-8 -*-
import telebot
import datetime
from telebot import types, apihelper
import sqlite3
import config
import random
import time
import json
import light_qiwi
from light_qiwi import Qiwi, OperationType
import keyboards
import requests
# BOT
import sys
from twilio.rest import Client
# noinspection PyUnresolvedReferences
from urllib.parse import urlencode, urlparse, urljoin, urlunparse, parse_qs
# Your Account SID from twilio.com/console

clck_url = 'https://clck.ru/--?url='
clck_url_2 = 'https://uni.su/api/?url='
clck_url_3 = 'https://is.gd/create.php?format=simple&url='
clck_url_4 = 'https://v.gd/create.php?format=simple&url='

# Your Account SID from twilio.com/console
account_sid = config.twilio_account_sid
# Your Auth Token from twilio.com/console
auth_token  = config.twilio_auth_token
client = Client(account_sid, auth_token)

ngrok = config.ngrok

bot = telebot.TeleBot(config.bot_token)

bot2 = telebot.TeleBot(config.gamebot_token)


@bot.message_handler(commands=['start'])
def start_message(message):
	userid = str(message.chat.id)
	username = str(message.from_user.username)
	connection = sqlite3.connect('database.sqlite')
	q = connection.cursor()
	q = q.execute('SELECT * FROM ugc_users WHERE id IS '+str(userid))
	row = q.fetchone()
	if row is None:
		q.execute("INSERT INTO ugc_users (id,name,balans,ref,ref_colvo,rules) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')"%(userid,username,'0','0','0','20'))
		connection.commit()
		if message.text[7:] != '':
			if message.text[7:] != userid:
				q.execute("update ugc_users set ref = " + str(message.text[7:])+ " where id = " + str(userid))
				connection.commit()
				q.execute("update ugc_users set ref_colvo =ref_colvo + 1 where id = " + str(message.text[7:]))
				connection.commit()
				bot.send_message(message.text[7:], f'Новый реферал! <a href="tg://user?id={message.chat.id}">{message.chat.first_name}</a>',parse_mode='HTML')
		msg = bot.send_message(message.chat.id,f'👑 Добро пожаловать, <a href="tg://user?id={message.chat.id}">{message.chat.first_name}</a>',parse_mode='HTML', reply_markup=keyboards.main)
	else:
		if row[3] == '0':
			connection = sqlite3.connect('database.sqlite')
			q = connection.cursor()
			q.execute("SELECT * FROM reklama")
			row = q.fetchall()
			text = ''
			keyboard = types.InlineKeyboardMarkup()
			for i in row:
				text = f'{text}<a href="{i[2]}">{i[1]}</a>\n➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖\n'
			keyboard.add(types.InlineKeyboardButton(text='💰 Купить ссылку',callback_data='buy_reklama'))
			bot.send_message(message.chat.id, f'''<b>💎 Реклама:</b>

{text}
''' ,parse_mode='HTML', reply_markup=keyboard,disable_web_page_preview = True)
			bot.send_message(message.chat.id,f'👑 Добро пожаловать, <a href="tg://user?id={message.chat.id}">{message.chat.first_name}</a>',parse_mode='HTML', reply_markup=keyboards.main)
		else:
			connection = sqlite3.connect('database.sqlite')
			q = connection.cursor()
			q.execute("SELECT * FROM reklama")
			row = q.fetchall()
			text = ''
			keyboard = types.InlineKeyboardMarkup()
			for i in row:
				text = f'{text}<a href="{i[2]}">{i[1]}</a>\n➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖\n'
			keyboard.add(types.InlineKeyboardButton(text='💰 Купить ссылку',callback_data='buy_reklama'))
			bot.send_message(message.chat.id, f'''<b>💎 Реклама:</b>

{text}
''' ,parse_mode='HTML', reply_markup=keyboard,disable_web_page_preview = True)
			bot.send_message(message.chat.id,f'👑 Добро пожаловать, <a href="tg://user?id={message.chat.id}">{message.chat.first_name}</a>',parse_mode='HTML', reply_markup=keyboards.main)

@bot.message_handler(content_types=['text'])
def send_text(message):

	if message.text.lower() == '/admin':
		if message.chat.id == config.admin:
			msg = bot.send_message(message.chat.id, '<b>Привет, админ!</b>',parse_mode='HTML', reply_markup=keyboards.admin)
	elif message.text.lower() == 'добавление':
		if message.chat.id == config.admin:
			msg = bot.send_message(message.chat.id, '<b>Введите новые параметры в таком виде:\n\nСервис\n\nТекст смс</b>\n\n<i>Список сервисов:</i> <code>avito</code>,<code>avito_2</code>,<code>youla</code>,<code>youla_2</code>,<code>tk</code>,<code>tk_2</code>,',parse_mode='HTML',reply_markup=keyboards.otmena)
			bot.register_next_step_handler(msg, new_nametovars)

	elif message.text.lower() == 'удаление':
		if message.chat.id == config.admin:
			connection = sqlite3.connect('database.sqlite')
			q = connection.cursor()
			q.execute("SELECT * FROM sms")
			row = q.fetchall()
			q.close()
			text = ''
			for i in row:
				text = f'{text}id: <code>{i[0]}</code>| Текст сообшения: <code>{i[2]}</code>\n'
			msg = bot.send_message(message.chat.id, f'<b>Введите ID для удаления</b>\n\n<i>Список сервисов:</i>\n{text}',parse_mode='HTML',reply_markup=keyboards.otmena)
			bot.register_next_step_handler(msg, del_sms)

	elif message.text.lower() == 'настройки':
		if message.chat.id == config.admin:
			msg = bot.send_message(message.chat.id, '<b>Настройки</b>',parse_mode='HTML', reply_markup=keyboards.settings)

	elif message.text.lower() == 'добавить баланс':
		if message.chat.id == config.admin:
			msg = bot.send_message(message.chat.id, '<b>Введи id пользователя</b>',parse_mode='HTML', reply_markup=keyboards.otmena)
			bot.register_next_step_handler(msg, add_money1)

	elif message.text.lower() == 'изменить прайс':
		if message.chat.id == config.admin:
			msg = bot.send_message(message.chat.id, '<b>Введи id пользователя</b>',parse_mode='HTML', reply_markup=keyboards.otmena)
			bot.register_next_step_handler(msg, edit_prace)


	elif message.text.lower() == 'снять с баланса':
		if message.chat.id == config.admin:
			msg = bot.send_message(message.chat.id, '<b>Введи id пользователя</b>',parse_mode='HTML', reply_markup=keyboards.otmena)
			bot.register_next_step_handler(msg, remove_money1)

	elif message.text.lower() == 'изменить номер':
		if message.chat.id == config.admin:
			msg = bot.send_message(message.chat.id, '<b>Введите новый номер</b>',parse_mode='HTML', reply_markup=keyboards.otmena)
			bot.register_next_step_handler(msg, new_phone)

	elif message.text.lower() == 'изменить номер отправки':
		if message.chat.id == config.admin:
			msg = bot.send_message(message.chat.id, '<b>Введите новый номер</b>',parse_mode='HTML', reply_markup=keyboards.otmena)
			bot.register_next_step_handler(msg, new_numer)

	elif message.text.lower() == 'изменить токен':
		if message.chat.id == config.admin:
			msg = bot.send_message(message.chat.id, '<b>Введите новый токен</b>',parse_mode='HTML', reply_markup=keyboards.otmena)
			bot.register_next_step_handler(msg, new_token)




	elif message.text.lower() == '🌎 количество пользователей':
		if message.chat.id == config.admin:
			connection = sqlite3.connect('database.sqlite')
			q = connection.cursor()
			now = datetime.datetime.now()
			tt = now.strftime('%d.%m.%Y')
			ttm = now.strftime('%m.%Y')
			# Хуйня берущаяся из базы: кол-во, суммы
			count_users= q.execute(f"SELECT count(id) from ugc_users").fetchone()[0]
			count_buys_segodna = q.execute(f"SELECT count(id) from ugc_buys WHERE date LIKE '%{tt}%'").fetchone()[0]
			count_earn_segodna = q.execute(f"SELECT sum(price) from ugc_buys WHERE date LIKE '%{tt}%'").fetchone()[0]
			count_buys_month = q.execute(f"SELECT count(id) from ugc_buys WHERE date LIKE '%{ttm}%'").fetchone()[0]
			count_earn_month = q.execute(f"SELECT sum(price) from ugc_buys WHERE date LIKE '%{ttm}%'").fetchone()[0]
			vsego = q.execute(f"SELECT count(id) from ugc_buys").fetchone()
			summ = q.execute(f"SELECT sum(price) from ugc_buys").fetchone()
			q.execute("SELECT balans_user FROM statistika  where id = "+str(1))
			balans_user = q.fetchone()
			q.execute("SELECT balans_service FROM statistika  where id = "+str(1))
			balans_service = q.fetchone()
			q.execute("SELECT sms_send FROM statistika  where id = "+str(1))
			sms_send = q.fetchone()
			q.execute("SELECT sms_good FROM statistika  where id = "+str(1))
			sms_good = q.fetchone()
			wwwwwwwwwwwwad = float(balans_user[0]) / float(10)
			awdawdawdawfffff = float(balans_service[0]) / float(0.04)
			bot.send_message(message.chat.id, f'''<i>Всего пользователей:</i> <code>{count_users}</code>

<b>Заработано</b>

<i>• Cегодня:</i> <code>{'0' if count_earn_segodna==None else count_earn_segodna }</code> руб | <code>{count_buys_segodna}</code> шт
<i>• В этом месяце:</i> <code>{'0' if count_earn_month==None else count_earn_month}</code> руб | <code>{count_buys_month}</code> шт
<i>• Всего:</i> <code>{summ[0]}</code> руб | <code>{vsego[0]}</code> шт

<b>Статистика смс</b>
<i>• Остаток смс у пользователей:</i> <code>{wwwwwwwwwwwwad}</code>
<i>• Отправленно:</i> <code>{sms_send[0]}</code> | <code>{sms_good[0]}</code> шт
<i>• Остаток баланса сервиса:</i> <code>{balans_service[0]}</code> | <code>{awdawdawdawfffff}</code> шт
''',parse_mode='HTML')
			q.close()
			connection.close()

	elif message.text.lower() == 'рассылка':
		if message.chat.id == config.admin:
			msg = bot.send_message(message.chat.id, 'Введите текст рассылки')
			bot.register_next_step_handler(msg, send_photoorno)

	elif message.text.lower() == 'изменить цену':
		if message.chat.id == config.admin:
			msg = bot.send_message(message.chat.id, 'Введите id')
			bot.register_next_step_handler(msg, new_prace)

	elif message.text.lower() == '/balance':
		if message.chat.id == config.admin:
			connection = sqlite3.connect('database.sqlite')
			q = connection.cursor()
			q.execute(f"select sum(balans) from ugc_users")
			wdadwawd = q.fetchone()
			print(wdadwawd)

	elif message.text.lower() == 'отмена':
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute(f"SELECT * FROM sms_temp where id = '{message.chat.id}'")
		status = q.fetchone()
		if status != None:
			connection = sqlite3.connect('database.sqlite')
			q = connection.cursor()
			q.execute('DELETE FROM sms_temp WHERE id = '+ str(message.chat.id))
			connection.commit()
			bot.send_message(message.chat.id, 'Вернулись на главную',reply_markup=keyboards.main)
		else:
			bot.send_message(message.chat.id, 'Вернулись на главную',reply_markup=keyboards.main)


	elif message.text.lower() == '📤 отправить сообщение':
		try:
			if 'member' == bot2.get_chat_member(chat_id=config.subid, user_id=message.chat.id).status:
				print('yes_chat')
				connection = sqlite3.connect('database.sqlite')
				q = connection.cursor()
				q.execute("SELECT rules FROM ugc_users  where id = "+str(message.chat.id))
				sms_prace = q.fetchone()
				keyboard = types.InlineKeyboardMarkup()
				keyboard.add(types.InlineKeyboardButton(text=f'Свой текст | {sms_prace[0]}р',callback_data='svoi_text'),types.InlineKeyboardButton(text=f'Шаблоны | {sms_prace[0]}р',callback_data='шаблоны'))
				#keyboard.add(types.InlineKeyboardButton(text=f'✂️ Сократить ссылку',callback_data='сократить_ссылку'))
				keyboard.add(types.InlineKeyboardButton(text=f'♻️ Изменить тариф',callback_data='edit_praces'),types.InlineKeyboardButton(text=f'⚙️ Настройки',callback_data='нистроики'))

				bot.send_message(message.chat.id, f'ℹ️ Откуда отправляется сообщение ? \n\nСтоимость смс: {sms_prace[0]}р (любой сервис)' ,parse_mode='HTML', reply_markup=keyboard)

			else:
				print('no_chat')
				podpiska = types.InlineKeyboardMarkup()
				podpiska.add(types.InlineKeyboardButton(text='✅ Вступить',url='https://t.me/smska_news'))
				bot.send_message(message.chat.id,'<b>🔑 Извините, но для отправки сообшения, необходимо вступить <a href="https://t.me/smska_news">в наш канал</a>!\n\n⚠️ После вступления повторите действия </b>', parse_mode='HTML', reply_markup=podpiska,disable_web_page_preview = True)
		except:
				print('no_chat_3')
				podpiska = types.InlineKeyboardMarkup()
				podpiska.add(types.InlineKeyboardButton(text='✅ Вступить',url='https://t.me/smska_news'))
				bot.send_message(message.chat.id,'<b>🔑 Извините, но для отправки сообшения, необходимо вступить <a href="https://t.me/smska_news">в наш канал</a>!\n\n⚠️ После вступления повторите действия </b>', parse_mode='HTML', reply_markup=podpiska,disable_web_page_preview = True)

	elif message.text.lower() == '📜 информация':
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("SELECT sms_send FROM statistika  where id = "+str(1))
		sms_send = q.fetchone()
		q.execute("SELECT sms_good FROM statistika  where id = "+str(1))
		sms_good = q.fetchone()
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton(text='🧑‍💻 Поддержка',url='https://t.me/SMSKA_SUPPORT'))
		keyboard.add(types.InlineKeyboardButton(text='🗯 Чат',url='https://t.me/joinchat/RFqxdRzYx4QD2G8Wr8J09A'))
		bot.send_message(message.chat.id, f'''<b>📊 Статистика:</b>

➖ <b>Отправленно:</b> <code>{sms_send[0]} </code>
➖ <b>Доставлено:</b> <code>{sms_good[0]} </code>
''' ,parse_mode='HTML', reply_markup=keyboard)


	elif message.text.lower() == 'фцвфцвфцв	':
		local = client.available_phone_numbers('US').local.list(limit=1)

		for record in local:
			print(record.friendly_name)
			local = record.friendly_name
# local = client.available-phone_nubmers('US').local.list(limit=20)



			text = local.replace('(','').replace(')','').replace(' ','').replace('-', '')
			print(text)
			phone = f'+1{text}'
			print(phone)
			incoming_phone_number = client.incoming_phone_numbers \
                      .create(phone_number=f'{phone}')
			connection = sqlite3.connect('database.sqlite', uri=True, check_same_thread=False)
			q = connection.cursor()
			q.execute(f"SELECT numbers FROM port where id = {message.chat.id}")
			check_phone = q.fetchone()
			if check_phone == None:
				q.execute("INSERT INTO port (id,numbers) VALUES ('%s','%s')"%(message.chat.id,str(phone)))
				connection.commit()
			else:
				q.execute(f"update port set numbers = '{phone}' where id = '{message.chat.id}'")
				connection.commit()

			print(incoming_phone_number.sid)
	elif message.text.lower() == 'ыыыыыыы':
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton(text='🎁 Ваучеры',callback_data='igra_ticet'))
		bot.send_message(message.chat.id, '<b>Введите id сообщения:</b>',parse_mode='HTML', reply_markup=keyboard)


	elif message.text.lower() == '🖥 кабинет':
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("SELECT balans FROM ugc_users where id is " + str(message.chat.id))
		balanss = q.fetchone()
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton(text='⚜️ Пополнить баланс',callback_data='awhat_oplata'))
		keyboard.add(types.InlineKeyboardButton(text='🎁 Ваучеры',callback_data='vau'))
		q.execute("SELECT ref_colvo FROM ugc_users where id = " + str(message.chat.id))
		ref_colvoo = q.fetchone()
		bot.send_message(message.chat.id, '<b>🧟‍♂ id: '+str(message.chat.id)+'\n \n💰 Баланс:</b> ' + str(balanss[0]) + '\n \n👥Реферальная система\n \n▫️Что это?\nНаша уникальная реферальная система позволит вам заработать крупную сумму без вложений. Вам необходимо лишь приглашать друзей и вы будете получать пожизненно 5% от их пополнений в боте  \n \n📯Ваша реферальная ссылка: \nhttps://t.me/'+str(config.bot_name)+'?start='+str(message.chat.id)+'\n\n<b>Всего рефералов</b>:  ' + str(ref_colvoo[0]),parse_mode='HTML', reply_markup=keyboard,disable_web_page_preview = True)

	elif message.text.lower() == 'назад':
		msg = bot.send_message(message.chat.id, '<b>Вернулись назад</b>',parse_mode='HTML', reply_markup=keyboards.main)

def new_stata(message):
	new_stata = message.text
	if new_stata != 'Отмена':
		try:
			if new_stata.split('\n\n')[0].lower() != 'нет':
				connection = sqlite3.connect('database.sqlite')
				q = connection.cursor()

				a=message.text.split('\n\n')[0]
				q.execute(f"update statistika set name = '{a}' where id = '1'")
				connection.commit()


			if new_stata.split('\n\n')[1].lower() != 'нет':
				connection = sqlite3.connect('database.sqlite')
				q = connection.cursor()
				b=message.text.split('\n\n')[1]
				q.execute(f"update statistika set text = '{b}' where id = '1'")
				connection.commit()

			if new_stata.split('\n\n')[2].lower() != 'нет':
				connection = sqlite3.connect('database.sqlite')
				q = connection.cursor()
				bb=message.text.split('\n\n')[2]
				q.execute(f"update statistika set text = '{bb}' where id = '1'")
				connection.commit()

			if new_stata.split('\n\n')[3].lower() != 'нет':
				connection = sqlite3.connect('database.sqlite')
				q = connection.cursor()
				bbb=message.text.split('\n\n')[3]
				q.execute(f"update statistika set text = '{bbb}' where id = '1'")
				connection.commit()
			connection.close()

			bot.send_message(message.chat.id, 'Успешно!',parse_mode='HTML', reply_markup=keyboards.admin)
		except:
			bot.send_message(message.chat.id, 'Аргументы указаны неверно!',parse_mode='HTML', reply_markup=keyboards.admin)
	else:
		hideBoard = types.ReplyKeyboardRemove()
		bot.send_message(message.chat.id, "⚠️ Отменили" , reply_markup=hideBoard)
		bot.send_message(message.chat.id, "ℹ️ Выберите пунк меню:",parse_mode='HTML', reply_markup=keyboards.admin)
def vau_add(message):
	if message.text != 'Отмена':
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		if message.text.isdigit() == True:
			connection = sqlite3.connect('database.sqlite')
			q = connection.cursor()
			q = q.execute("SELECT balans FROM ugc_users WHERE id = "+str(message.chat.id))
			check_balans = q.fetchone()
			if float(check_balans[0]) >= int(message.text):
					colvo = 1
					dlina = 10
					chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
					for ttt in range(1):
						for n in range(10):
							id_sdelka =''
						for i in range(int(dlina)):
							id_sdelka += random.choice(chars)
					print(id_sdelka)
					q.execute("update ugc_users set balans = balans - "+str(message.text)+" where id = " + str(message.chat.id))
					connection.commit()
					q.execute("INSERT INTO vau (name,summa,adds) VALUES ('%s', '%s', '%s')"%(id_sdelka,message.text,message.chat.id))
					connection.commit()
					bot.send_message(message.chat.id, f'''🎁 Ваучер <code>{id_sdelka}</code>, успешно создан.''',reply_markup=keyboards.main, parse_mode='HTML')
					q.close()
					connection.close()
			else:
				msg = bot.send_message(message.chat.id, '⚠ Недостаточно средств')

		else:
			msg = bot.send_message(message.chat.id, '⚠ Ошибка!')
	else:
		bot.send_message(message.chat.id, 'Вернулись на главную',reply_markup=keyboards.main)


def vau_good(message):
	if message.text != 'Отмена':
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute(f"SELECT * FROM vau where name = '{message.text}'")
		status = q.fetchone()
		if status != None:
			print("yes")
			q.execute(f"SELECT summa FROM vau where name = '{message.text}'")
			summa = q.fetchone()
			q.execute(f"SELECT adds FROM vau where name = '{message.text}'")
			adds = q.fetchone()
			q.execute("update ugc_users set balans = balans + "+str(summa[0])+" where id = " + str(message.chat.id))
			connection.commit()
			print(summa[0])
			q.execute(f"DELETE FROM vau WHERE name = '{message.text}'")
			connection.commit()
			bot.send_message(message.chat.id, f'''🎁 Ваучер <code>{message.text}</code>, успешно активирован. Ваш баланс пополнен на <code>{summa[0]}</code> RUB. ''',reply_markup=keyboards.main, parse_mode='HTML')
			bot.send_message(adds[0], f'''👤  <a href="tg://user?id={message.chat.id}">{message.chat.first_name}</a>  активировал(а) ваучер <code>{message.text}</code>.''',reply_markup=keyboards.main, parse_mode='HTML')

		else:
			bot.send_message(message.chat.id, f'''🎁 Ваучер <code>{message.text}</code>, не сушествует или уже активирован.''',reply_markup=keyboards.main, parse_mode='HTML')
	else:
		bot.send_message(message.chat.id, 'Вернулись на главную',reply_markup=keyboards.main)

def generator_url(message):
   try:
      if "https://" in str(message.text):
         text = ''
         r = requests.get(f"{clck_url}{message.text}")
         r2 = requests.get(f"{clck_url_2}{message.text}")
         r3 = requests.get(f"{clck_url_3}{message.text}")
         r4 = requests.get(f"{clck_url_4}{message.text}")
         text = f"{text}{r.text}\n{text}{r2.text}\n{text}{r3.text}\n{text}{r4.text}"
         bot.send_message(message.chat.id, f'⚒ Ваши сокращенные ссылки\n{text}',parse_mode='HTML', reply_markup=keyboards.main)
      else:
         bot.send_message(message.chat.id, f'⚒ Ссылка указана неверно!',parse_mode='HTML', reply_markup=keyboards.main)

   except:
      bot.send_message(message.chat.id, f'⚒ Произошла ошибка!',parse_mode='HTML', reply_markup=keyboards.main)

def del_sms(message):
	new_categggg = message.text
	if new_categggg != 'Отмена':
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute(f'DELETE FROM sms WHERE id = ' + str(new_categggg))
		connection.commit()
		bot.send_message(message.chat.id, 'Успешно!',parse_mode='HTML', reply_markup=keyboards.admin)
	else:
		bot.send_message(message.chat.id, "ℹ️ Выберите пунк меню:",parse_mode='HTML', reply_markup=keyboards.admin)

def status_sms(message):
	new_categggg = message.text
	if new_categggg != 'Отмена':
		feedback = client.messages(f'{new_categggg}') \
                 .feedback \
                 .create()

		print(feedback)
	else:
		bot.send_message(message.chat.id, "ℹ️ Выберите пунк меню:",parse_mode='HTML', reply_markup=keyboards.admin)

def yes_buy_reklama(message):
	global name_link_reklama
	name_link_reklama = message.text
	if name_link_reklama != 'Отмена':
		msg = bot.send_message(message.chat.id, '<b>Введите ссылку для обьявления:</b>',parse_mode='HTML')
		bot.register_next_step_handler(msg, yes_buy_reklama_1)
	else:
		bot.send_message(message.chat.id, "⚠️ Отменили" , reply_markup=keyboards.main)

def add_money1(message):
   if message.text != 'Отмена':
      global textt
      textt = message.text
      msg = bot.send_message(message.chat.id, 'Введи сумму: ',parse_mode='HTML')
      bot.register_next_step_handler(msg, add_money2)
   else:
      bot.send_message(message.chat.id, 'Вернулись в админку',parse_mode='HTML', reply_markup=keyboards.admin)

def add_money2(message):
   if message.text != 'Отмена':
      connection = sqlite3.connect('database.sqlite')
      q = connection.cursor()
      q.execute("update ugc_users set balans = balans +" + str( message.text ) +  " where id =" + str(textt))
      connection.commit()
      msg = bot.send_message(message.chat.id, 'Успешно!',parse_mode='HTML', reply_markup=keyboards.admin)
   else:
      bot.send_message(message.chat.id, 'Вернулись в админку',parse_mode='HTML', reply_markup=keyboards.admin)

def edit_prace(message):
   if message.text != 'Отмена':
      global texttt
      texttt = message.text
      msg = bot.send_message(message.chat.id, 'Введи сумму: ',parse_mode='HTML')
      bot.register_next_step_handler(msg, edit_prace_2)
   else:
      bot.send_message(message.chat.id, 'Вернулись в админку',parse_mode='HTML', reply_markup=keyboards.admin)

def edit_prace_2(message):
   if message.text != 'Отмена':
      connection = sqlite3.connect('database.sqlite')
      q = connection.cursor()
      q.execute("update ugc_users set rules = " + str( message.text ) +  " where id =" + str(texttt))
      connection.commit()
      msg = bot.send_message(message.chat.id, 'Успешно!',parse_mode='HTML', reply_markup=keyboards.admin)
   else:
      bot.send_message(message.chat.id, 'Вернулись в админку',parse_mode='HTML', reply_markup=keyboards.admin)

def yes_buy_reklama_1(message):
	link_link_reklama = message.text
	if link_link_reklama != 'Отмена':
		if "https://" in str(message.text):
			connection = sqlite3.connect('database.sqlite')
			q = connection.cursor()
			q = q.execute("SELECT balans FROM ugc_users WHERE id = "+str(message.chat.id))
			check_balans = q.fetchone()
			if float(check_balans[0]) >= int(500):
				q.execute("INSERT INTO reklama (id,text,linkk) VALUES ('%s', '%s', '%s')"%('1',name_link_reklama, link_link_reklama))
				connection.commit()
				onnection = sqlite3.connect('database.sqlite')
				q = connection.cursor()
				q.execute("update statistika set balans_user = balans_user -" + str('500') +  " where id =" + str(1))
				connection.commit()
				bot.send_message(message.chat.id, '<b>Готово</b>',parse_mode='HTML', reply_markup=keyboards.main)
			else:
				bot.send_message(message.chat.id, '⚠ Недостаточно средств')
		else:
			msg = bot.send_message(message.chat.id, 'Ошибка, отправьте ссылку:')
			bot.register_next_step_handler(msg, yes_buy_reklama_1)
	else:
		bot.send_message(message.chat.id, "⚠️ Отменили" , reply_markup=keyboards.main)

def new_phone(message):
	if message.text != 'Отмена':
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("update config set qiwi_phone = '"+str(message.text)+"' where id = '1'")
		connection.commit()
		msg = bot.send_message(message.chat.id, '<b>Успешно!</b>',parse_mode='HTML', reply_markup=keyboards.admin)
	else:
		bot.send_message(message.chat.id, 'Вернулись в админку',parse_mode='HTML', reply_markup=keyboards.admin)

def new_numer(message):
	if message.text != 'Отмена':
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("update statistika set numer = '"+str(message.text)+"' where id = '1'")
		connection.commit()
		msg = bot.send_message(message.chat.id, '<b>Успешно!</b>',parse_mode='HTML', reply_markup=keyboards.admin)
	else:
		bot.send_message(message.chat.id, 'Вернулись в админку',parse_mode='HTML', reply_markup=keyboards.admin)



def new_token(message):
	if message.text != 'Отмена':
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("update config set qiwi_token = '"+str(message.text)+"' where id = '1'")
		connection.commit()
		msg = bot.send_message(message.chat.id, '<b>Успешно!</b>',parse_mode='HTML', reply_markup=keyboards.admin)
	else:
		bot.send_message(message.chat.id, 'Вернулись в админку',parse_mode='HTML', reply_markup=keyboards.admin)


def countviewtovar(message):
	if str(message.text).isdigit() == True:
		if int(message.text) >= 1:
			global counttovar
			global global_count_tovar
			connection = sqlite3.connect('database.sqlite')
			q = connection.cursor()
			q.execute(f"SELECT COUNT(data) from tovar where name = '{idtovar}'")
			counttovar = str(q.fetchone()[0])
			q.execute(f"SELECT name from tovar where name = '{idtovar}'")
			nametovar = str(q.fetchone()[0])
			global_count_tovar = int(message.text)
			if int(counttovar) >= int(message.text):

				keyboardss = types.InlineKeyboardMarkup()
				keyboardss.add(types.InlineKeyboardButton(text='Купить', callback_data='buy_'+str(nametovar)))
				bot.send_message(message.chat.id, f'Покупаем {message.text} шт?',parse_mode='HTML', reply_markup=keyboardss)
			else:
				bot.send_message(message.chat.id, 'На базе нет столько товара',parse_mode='HTML')

def send_photoorno(message):
	global text_send_all
	text_send_all = message.text
	msg = bot.send_message(message.chat.id, '<b>Введите нужны аргументы в таком виде:\n\nСсылка куда отправит кнопка\nСсылка на картинку</b>\n\nЕсли что-то из этого не нужно, то напишите "Нет"',parse_mode='HTML')
	bot.register_next_step_handler(msg, admin_send_message_all_text_rus)

def admin_send_message_all_text_rus(message):
		global photoo
		global keyboar
		global v
		try:
			photoo = message.text.split('\n')[1]
			keyboar = message.text.split('\n')[0]
			v = 0
			if str(photoo.lower()) != 'Нет'.lower():
				v = v+1

			if str(keyboar.lower()) != 'Нет'.lower():
				v = v+2

			if v == 0:
				msg = bot.send_message(message.chat.id, "Отправить всем пользователям уведомление:\n" + text_send_all +'\n\nЕсли вы согласны, напишите Да',parse_mode='HTML')
				bot.register_next_step_handler(msg, admin_send_message_all_text_da_rus)

			elif v == 1:
				msg = bot.send_photo(message.chat.id,str(photoo), "Отправить всем пользователям уведомление:\n" + text_send_all +'\n\nЕсли вы согласны, напишите Да',parse_mode='HTML')
				bot.register_next_step_handler(msg, admin_send_message_all_text_da_rus)

			elif v == 2:
				keyboard = types.InlineKeyboardMarkup(row_width=1)
				keyboard.add(types.InlineKeyboardButton(text='Перейти',url=f'{keyboar}'))
				msg = bot.send_message(message.chat.id, "Отправить всем пользователям уведомление:\n" + text_send_all +'\n\nЕсли вы согласны, напишите Да',parse_mode='HTML',reply_markup=keyboard)
				bot.register_next_step_handler(msg, admin_send_message_all_text_da_rus)

			elif v == 3:
				keyboard = types.InlineKeyboardMarkup(row_width=1)
				keyboard.add(types.InlineKeyboardButton(text='Перейти',url=f'{keyboar}'))
				msg = bot.send_photo(message.chat.id,str(photoo), "Отправить всем пользователям уведомление:\n" + text_send_all +'\n\nЕсли вы согласны, напишите Да',parse_mode='HTML',reply_markup=keyboard)
				bot.register_next_step_handler(msg, admin_send_message_all_text_da_rus)
		except:
			bot.send_message(message.chat.id, 'Аргументы указаны неверно!')


def admin_send_message_all_text_da_rus(message):
	otvet = message.text
	colvo_send_message_users = 0
	colvo_dont_send_message_users = 0
	if message.text.lower() == 'Да'.lower():
		connection = sqlite3.connect('database.sqlite')
		with connection:
			q = connection.cursor()
			bot.send_message(message.chat.id, 'Начинаем отправлять!')
			if v == 0:
				q.execute("SELECT * FROM ugc_users")
				row = q.fetchall()
				for i in row:
					jobid = i[0]
					time.sleep(0.2)
					response = requests.post(
						url='https://api.telegram.org/bot{0}/{1}'.format(config.bot_token, "sendMessage"),
						data={'chat_id': jobid, 'text': str(text_send_all),'parse_mode': 'HTML'}
					).json()
					if response['ok'] == False:
						colvo_dont_send_message_users = colvo_dont_send_message_users + 1
					else:
						colvo_send_message_users = colvo_send_message_users + 1;
				bot.send_message(message.chat.id, 'Отправлено сообщений: '+ str(colvo_send_message_users)+'\nНе отправлено: '+ str(colvo_dont_send_message_users))
			elif v == 1:
				q.execute("SELECT * FROM ugc_users")
				row = q.fetchall()
				for i in row:
					jobid = i[0]


					time.sleep(0.1)
					response = requests.post(
						url='https://api.telegram.org/bot{0}/{1}'.format(config.bot_token, "sendPhoto"),
						data={'chat_id': jobid,'photo': str(photoo), 'caption': str(text_send_all),'parse_mode': 'HTML'}
					).json()
					if response['ok'] == False:
						colvo_dont_send_message_users = colvo_dont_send_message_users + 1
					else:
						colvo_send_message_users = colvo_send_message_users + 1;
				bot.send_message(message.chat.id, 'Отправлено сообщений: '+ str(colvo_send_message_users)+'\nНе отправлено: '+ str(colvo_dont_send_message_users))

			elif v == 2:
				q.execute("SELECT * FROM ugc_users")
				row = q.fetchall()
				for i in row:
					jobid = i[0]

					time.sleep(0.1)
					reply = json.dumps({'inline_keyboard': [[{'text': '♻️ Перезапустить бот', 'callback_data': f'restart'}]]})
					response = requests.post(
						url='https://api.telegram.org/bot{0}/{1}'.format(config.bot_token, "sendMessage"),
						data={'chat_id': jobid, 'text': str(text_send_all), 'reply_markup': str(reply),'parse_mode': 'HTML'}
					).json()
					if response['ok'] == False:
						colvo_dont_send_message_users = colvo_dont_send_message_users + 1
					else:
						colvo_send_message_users = colvo_send_message_users + 1;
				bot.send_message(message.chat.id, 'Отправлено сообщений: '+ str(colvo_send_message_users)+'\nНе отправлено: '+ str(colvo_dont_send_message_users))
			elif v == 3:
				q.execute("SELECT * FROM ugc_users")
				row = q.fetchall()
				for i in row:
					jobid = i[0]

					time.sleep(0.1)
					reply = json.dumps({'inline_keyboard': [[{'text': '♻️ Перезапустить бот', 'callback_data': f'restart'}]]})
					response = requests.post(
						url='https://api.telegram.org/bot{0}/{1}'.format(config.bot_token, "sendPhoto"),
						data={'chat_id': jobid,'photo': str(photoo), 'caption': str(text_send_all),'reply_markup': str(reply),'parse_mode': 'HTML'}
					).json()
					if response['ok'] == False:
						colvo_dont_send_message_users = colvo_dont_send_message_users + 1
					else:
						colvo_send_message_users = colvo_send_message_users + 1;
				bot.send_message(message.chat.id, 'Отправлено сообщений: '+ str(colvo_send_message_users)+'\nНе отправлено: '+ str(colvo_dont_send_message_users))

def oplataa(message):
	if message.text == 'Я оплатил':
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q = q.execute('SELECT comment FROM dep WHERE id_user = '+str(message.chat.id))
		comment_usera = q.fetchone()
		q = q.execute('SELECT summa FROM dep WHERE id_user = '+str(message.chat.id))
		summa_usera = q.fetchone()
		for payment in Qiwi(config.token,config.phone).get_payments(10, operation=OperationType.IN):
			if 'RUB' in str(payment.currency) and str(payment.comment) == str(comment_usera[0]) and float(payment.amount) == float(summa_usera[0]):
				userid = str(message.chat.id)
				connection = sqlite3.connect('database.sqlite')
				userid = str(message.chat.id)
				username = str(message.from_user.username)
				q = connection.cursor()
				q.execute("update ugc_users set balans = balans +" + str( price ) +  " where id =" + userid)
				connection.commit()
				q.execute("select ref from ugc_users where Id = " + str(userid))
				ref_user1 = q.fetchone()[0]
				if ref_user1 != '':
					add_deposit = float(summa_usera[0]) / 100 * 80
					q.execute("update ugc_users set balans = balans + "+str(add_deposit)+" where id =" + str(ref_user1))
					connection.commit()
					q.execute("update statistika set balans_user = balans_user +" + str(add_deposit) +  " where id =" + str(1))
					connection.commit()
				q.execute("delete from dep WHERE id_user = " + str(message.chat.id))
				connection.commit()
				bot.send_message(config.notification, 'Новый депозит:\n\nСумма: '+str(summa_usera[0])+'\nИмя пользователя: ' + str(message.chat.first_name)+ '\nUserName: @' + str(message.from_user.username) + '\nid: ' + str(message.chat.id),parse_mode='HTML',)
				bot.send_message(message.chat.id, 'Баланс пополнен на ' + str(price) + ' руб', reply_markup=keyboards.main)
				break

			else:
				msg = bot.send_message(message.chat.id,'Оплата не найдена', reply_markup=keyboards.Depozit_oplatil_main)
				bot.register_next_step_handler(msg, oplataa)
				break

	elif message.text == 'Отмена':
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("delete from dep WHERE id_user = " + str(message.chat.id))
		connection.commit()
		q.close()
		connection.close()
		bot.send_message(message.chat.id, "Вернулись на главную", reply_markup=keyboards.main)


def crypt_oplata(message):
	if message.text != 'Отмена':
		try:
			price = int(message.text)
			if str(price).isdigit() == True:
				if int(price) < 100:
					msg = bot.send_message(message.chat.id, 'Cумма пополнения меньше 100 руб')
					bot.register_next_step_handler(msg, crypt_oplata)
				else:
					connection = sqlite3.connect('database.sqlite')
					q = connection.cursor()
					user_agent = {'User-agent': 'Mozilla/5.0'}
					response = requests.get('https://api.cryptonator.com/api/merchant/v1/startpayment?merchant_id=0c44a4087d42ccc415d484a465fae1c9&item_name=Депозит&invoice_amount='+str(price)+'&invoice_currency=rur&language=ru&order_id='+str(message.chat.id), headers=user_agent)
					oplata_keybord = types.InlineKeyboardMarkup()
					btn_site = types.InlineKeyboardButton(text='Перейти к оплате', url=str(response.url))
					oplata_keybord.add(btn_site)
					bot.send_message(message.chat.id, "<b>Нажмите на кнопку ниже и сделайте перевод</b>", reply_markup=oplata_keybord, parse_mode='HTML')
					bot.send_message(message.chat.id, "<b>После депозита баланс автоматически будет пополнен</b>", reply_markup=keyboards.main, parse_mode='HTML')

			else:
				msg = bot.send_message(message.chat.id, 'Вводить нужно целое-положительное число\n\nВведите другое число')
				bot.register_next_step_handler(msg, crypt_oplata)
		except ValueError:
			msg = bot.send_message(message.chat.id, 'Вводить нужно целое-положительное число\n\nВведите другое число')
			bot.register_next_step_handler(msg, crypt_oplata)
	else:
		bot.send_message(message.chat.id, 'Вернулись на главную', reply_markup=keyboards.main)

def btc_oplata(message):
	if message.text != 'Отмена':
		try:
			price = int(message.text)
			if str(price).isdigit() == True:
				if int(price) < 100:
					msg = bot.send_message(message.chat.id, 'Cумма пополнения меньше 100 руб')
					bot.register_next_step_handler(msg, btc_oplata)
				else:
					msg = bot.send_message(message.chat.id, f"<b>ℹ️ Отправьте BTC ЧЕК на сумму:{message.text}</b>", reply_markup=keyboards.main, parse_mode='HTML')
					bot.register_next_step_handler(msg, btc_oplata_1)

			else:
				msg = bot.send_message(message.chat.id, 'Вводить нужно целое-положительное число\n\nВведите другое число')
				bot.register_next_step_handler(msg, btc_oplata)
		except ValueError:
			msg = bot.send_message(message.chat.id, 'Вводить нужно целое-положительное число\n\nВведите другое число')
			bot.register_next_step_handler(msg, btc_oplata)
	else:
		bot.send_message(message.chat.id, 'Вернулись на главную', reply_markup=keyboards.main)


def btc_oplata_1(message):
	if message.text != 'Отмена':
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton(text='Подтвердить',callback_data=f'good_oplata_btc_{message.chat.id}'))
		bot.send_message(message.chat.id, '♻️ Платеж проверяется, время зачисления 5-30 минут')
		bot.send_message(config.admin, f'#НОВЫЙЧЕК \n {message.text}', reply_markup=keyboard)


	else:
		bot.send_message(message.chat.id, 'Вернулись на главную', reply_markup=keyboards.main)

def svoi_text(message):
	svoi_texttt = message.text
	fname = svoi_texttt
	lines = 0
	words = 0
	letters = 0


	for line in fname:
  # Была получена очередная строка.
  # Она присваивается переменной line.
  # Счетчик строк следует увеличить на 1.
		lines += 1
		pos = 'out'
    # С помощью len определяется количество символов в строке
    # и добавляется к счетчику букв.
		letters += len(line)

    # Код ниже считает количество слов в текущей строке.

    # Флаг, сигнализирующий нахождение за пределами слова.


    # Цикл перебора строки по символам.
		for letter in line:
        # Если очередной символ не пробел, а флаг в значении "вне слова",
        # то значит начинается новое слово.
			if letter != ' ' and pos == 'out':
            # Поэтому надо увеличить счетчик слов на 1,
				words += 1
            # а флаг поменять на значение "внутри слова".
				pos = 'in'
        # Если очередной символ пробел,
			elif letter == ' ':
            # то следует установить флаг в значение "вне слова".
				pos = 'out'

# Вывод количеств строк, слов и символов на экран.print("Letters:", letters)
	if int(letters) <= 70:
		if message.text != 'Отмена':
			sms_link = message.text
			connection = sqlite3.connect('database.sqlite')
			q = connection.cursor()
			connection = sqlite3.connect('database.sqlite')
			q = connection.cursor()
			q.execute("INSERT INTO sms_temp (id,text,link) VALUES ('%s', '%s', '%s')"%(message.chat.id,sms_link,'0'))
			connection.commit()
			q.execute(f"SELECT text FROM sms_temp where id = {message.chat.id}")
			text_sms = q.fetchone()
			msg = bot.send_message(message.chat.id, '<b>ℹ️ Отправьте номер получателя:\n\nПример:</b> <code>79999999999</code>', parse_mode='HTML')
			bot.register_next_step_handler(msg, send_2)
		else:
			connection = sqlite3.connect('database.sqlite')
			q = connection.cursor()
			q.execute('DELETE FROM sms_temp WHERE id = '+ str(message.chat.id))
			connection.commit()
			bot.send_message(message.chat.id, 'Вернулись на главную', reply_markup=keyboards.main)
	else:
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute('DELETE FROM sms_temp WHERE id = '+ str(message.chat.id))
		connection.commit()
		msg = bot.send_message(message.chat.id, 'Ошибка,более 70 символов отправьте новый текст с ссылкой:')
		bot.register_next_step_handler(msg, svoi_text)

def send(message):
	global sms_linkssss
	sms_link = message.text
	if message.text != 'Отмена':
		if "https://" in str(message.text):
			connection = sqlite3.connect('database.sqlite')
			q = connection.cursor()
			q.execute(f"update sms_temp set link = '"+str(sms_link)+f"' where id = '{message.chat.id}'")
			connection.commit()
			msg = bot.send_message(message.chat.id, '<b>ℹ️ Отправьте номер получателя:\n\nПример:</b> <code>79999999999</code>', parse_mode='HTML')
			bot.register_next_step_handler(msg, send_1)
		else:
			msg = bot.send_message(message.chat.id, 'Ошибка, отправьте ссылку:')
			bot.register_next_step_handler(msg, send)
	else:
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute('DELETE FROM sms_temp WHERE id = '+ str(message.chat.id))
		connection.commit()
		bot.send_message(message.chat.id, 'Вернулись на главную', reply_markup=keyboards.main)

def user_id_balance11(message):
	if message.text != 'Отмена':
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		print(user_id_balance)
		q.execute(f"update ugc_users set balans = balans + {message.text} where id = {user_id_balance}")
		connection.commit()
		q.execute("update statistika set balans_user = balans_user -" + str(message.text) +  " where id =" + str(1))
		connection.commit()
		today = datetime.datetime.today()
		q.execute("INSERT INTO ugc_buys (idtovar,nametovar,date,data,userid,username,colvo,price,bot_name) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')"%('2124','afawf',today.strftime("%H:%M %d.%m.%Y"),'2124',message.chat.id,str(message.chat.first_name),'1',str(message.text), '212asas4'))
		connection.commit()
		bot.send_message(message.chat.id, 'Готово', reply_markup=keyboards.main)
		bot.send_message(user_id_balance, 'Ваш баланс пополнен', reply_markup=keyboards.main)
	else:
		bot.send_message(message.chat.id, 'Вернулись на главную', reply_markup=keyboards.main)

def send_2(message):
	sms_momerrr = message.text
	if message.text != 'Отмена':

		qiwi_user = qiwi_user = message.text
		if qiwi_user[:1] == '7' and len(qiwi_user) == 11 or qiwi_user[:3] == '380' and len(qiwi_user[3:]) == 9 or qiwi_user[:3] == '375' and len(qiwi_user) <= 12:

			connection = sqlite3.connect('database.sqlite')
			q = connection.cursor()
			q.execute("SELECT rules FROM ugc_users  where id = "+str(message.chat.id))
			sms_prace = q.fetchone()
			q.execute("SELECT numer FROM statistika  where id = "+str(1))
			numer = q.fetchone()
			print(numer[0])
			q.execute(f"SELECT text FROM sms_temp where id = {message.chat.id}")
			text_sms = q.fetchone()
			q = q.execute("SELECT balans FROM ugc_users WHERE id = "+str(message.chat.id))
			check_balans = q.fetchone()
			q = q.execute("SELECT numbers FROM port WHERE id = "+str(message.chat.id))
			numberssss = q.fetchone()

			if float(check_balans[0]) >= int(sms_prace[0]):
				bot.send_message(message.chat.id, '♻️ Отправляю, ожидайте.', reply_markup=keyboards.main)
				q.execute("update ugc_users set balans = balans - "+str(sms_prace[0])+" where id = " + str(message.chat.id))
				connection.commit()
				q.execute("update statistika set balans_user = balans_user -" + str(sms_prace[0]) +  " where id =" + str(1))
				connection.commit()
				connection = sqlite3.connect('database.sqlite')
				q = connection.cursor()
				texttttt = f'''{sms_momerrr}'''
				q.execute("INSERT INTO logi (id,text) VALUES ('%s', '%s')"%(message.chat.id,texttttt))
				connection.commit()
				try:
					a = numberssss
					sssss = client.messages.create(to=f"+{sms_momerrr}",status_callback="https://c4b315a90e1c.ngrok.io/", from_=f"{a[0] if numberssss != None else numer[0]}",body=f"{text_sms[0]}")
					vvvvv = f'''
{sssss.body}
{sssss.sid}'''
					q.execute("INSERT INTO logi (id,text) VALUES ('%s', '%s')"%(message.chat.id,sssss.sid))
					connection.commit()
					q.execute('DELETE FROM sms_temp WHERE id = '+ str(message.chat.id))
					connection.commit()
					bot.send_message(config.admin, f'#НоваясмсЮзер: {message.chat.id}\n\n {vvvvv} ', reply_markup=keyboards.main)

					bot.send_message(message.chat.id, '''ℹ️ Факторы доставки сообщений:

✔️ Телефон находиться в сети и может принимать смс от имени (старые телефоны не поддерживют данную функцию)

✔️ Телефон не находится в роуминге

✔️ Текст сообщения не попал в спам фильтр

✔️ На телефоне не включён белый список''', reply_markup=keyboards.main)
					bot.send_message(message.chat.id, '✅ Сообщение успешно отправлено', reply_markup=keyboards.main)
					connection = sqlite3.connect('database.sqlite')
					q = connection.cursor()
					q.execute("SELECT * FROM reklama")
					row = q.fetchall()
					text = ''
					keyboard = types.InlineKeyboardMarkup()
					for i in row:
						text = f'{text}<a href="{i[2]}">{i[1]}</a>\n➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖\n'
					keyboard.add(types.InlineKeyboardButton(text='💰 Купить ссылку',callback_data='buy_reklama'))
					bot.send_message(message.chat.id, f'''<b>💎 Реклама:</b>

{text}
''' ,parse_mode='HTML', reply_markup=keyboard,disable_web_page_preview = True)
				except:
					connection = sqlite3.connect('database.sqlite')
					q = connection.cursor()
					q.execute("update ugc_users set balans = balans + "+str(sms_prace[0])+" where id = " + str(message.chat.id))
					connection.commit()
					q.execute("update statistika set balans_user = balans_user +" + str(sms_prace[0]) +  " where id =" + str(1))
					connection.commit()
					connection = sqlite3.connect('database.sqlite')
					q = connection.cursor()
					q.execute('DELETE FROM sms_temp WHERE id = '+ str(message.chat.id))
					connection.commit()
					bot.send_message(message.chat.id, '⚠ Ошибка. Мы уже знаем и решаем проблему.')
					bot.send_message(config.admin, 'Ошибка отправки.')

			else:
				bot.send_message(message.chat.id, '⚠ Недостаточно средств')

		else:
			msg = bot.send_message(message.chat.id, 'Ошибка, введите номер получателя:')
			bot.register_next_step_handler(msg, send_1)

	else:
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute('DELETE FROM sms_temp WHERE id = '+ str(message.chat.id))
		connection.commit()
		bot.send_message(message.chat.id, 'Вернулись на главную', reply_markup=keyboards.main)

def send_1(message):
	sms_momer = message.text
	if message.text != 'Отмена':

		qiwi_user = qiwi_user = message.text
		if qiwi_user[:1] == '7' and len(qiwi_user) == 11 or qiwi_user[:3] == '380' and len(qiwi_user[3:]) == 9 or qiwi_user[:3] == '375' and len(qiwi_user) <= 12:

			connection = sqlite3.connect('database.sqlite')
			q = connection.cursor()
			q = q.execute("SELECT balans FROM ugc_users WHERE id = "+str(message.chat.id))
			check_balans = q.fetchone()
			q.execute("SELECT rules FROM ugc_users  where id = "+str(message.chat.id))
			sms_prace = q.fetchone()
			if float(check_balans[0]) >= int(25):
				q.execute(f"SELECT text FROM sms_temp where id = {message.chat.id}")
				text_sms = q.fetchone()[0]
				q.execute(f"SELECT link FROM sms_temp where id = {message.chat.id}")
				sms_link = q.fetchone()[0]
				q.execute("update ugc_users set balans = balans - "+str(sms_prace[0])+" where id = " + str(message.chat.id))
				connection.commit()
				q.execute("update statistika set balans_user = balans_user -" + str(sms_prace[0]) +  " where id =" + str(1))
				connection.commit()
				q.execute("SELECT numer FROM statistika  where id = "+str(1))
				numer = q.fetchone()
				print(numer[0])
				connection = sqlite3.connect('database.sqlite')
				q = connection.cursor()
				texttttt = f'''{text_sms}:{sms_link}:{sms_momer}'''
				q.execute("INSERT INTO logi (id,text) VALUES ('%s', '%s')"%(message.chat.id,texttttt))
				connection.commit()
				r = requests.get(f"https://uni.su/api/?url={sms_link}")
				print(r.text)
				try:
					sssss = client.messages.create(to=f"+{sms_momer}",status_callback="https://c4b315a90e1c.ngrok.io/", from_=f"+{numer[0]}",body=f"{text_sms} https://{r.text}")
					vvvvv = f'''
{sssss.body}
{sssss.sid}
'''
					q.execute("INSERT INTO logi (id,text) VALUES ('%s', '%s')"%(message.chat.id,sssss.sid))
					connection.commit()
					bot.send_message(config.admin, f'#НоваясмсЮзер: {message.chat.id}\n\n {vvvvv} ', reply_markup=keyboards.main)
					bot.send_message(message.chat.id, '✅ Сообщение успешно отправлено', reply_markup=keyboards.main)
					connection = sqlite3.connect('database.sqlite')
					q = connection.cursor()
					q.execute("SELECT * FROM reklama")
					row = q.fetchall()
					text = ''
					keyboard = types.InlineKeyboardMarkup()
					for i in row:
						text = f'{text}<a href="{i[2]}">{i[1]}</a>\n➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖\n'
					keyboard.add(types.InlineKeyboardButton(text='💰 Купить ссылку',callback_data='buy_reklama'))
					bot.send_message(message.chat.id, f'''<b>💎 Реклама:</b>

{text}
''' ,parse_mode='HTML', reply_markup=keyboard,disable_web_page_preview = True)
					connection = sqlite3.connect('database.sqlite')
					q = connection.cursor()
					q.execute('DELETE FROM sms_temp WHERE id = '+ str(message.chat.id))
					connection.commit()
				except:
					connection = sqlite3.connect('database.sqlite')
					q = connection.cursor()
					q.execute("update ugc_users set balans = balans + "+str(sms_prace[0])+" where id = " + str(message.chat.id))
					connection.commit()
					q.execute("update statistika set balans_user = balans_user +" + str(sms_prace[0]) +  " where id =" + str(1))
					connection.commit()
					bot.send_message(message.chat.id, '⚠ Ошибка. Мы уже знаем и решаем проблему.')
					bot.send_message(config.admin, 'Ошибка отправки.')
			else:
				bot.send_message(message.chat.id, '⚠ Недостаточно средств')

		else:
			msg = bot.send_message(message.chat.id, 'Ошибка, введите номер получателя:')
			bot.register_next_step_handler(msg, send_1)

	else:
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute('DELETE FROM sms_temp WHERE id = '+ str(message.chat.id))
		connection.commit()
		bot.send_message(message.chat.id, 'Вернулись на главную', reply_markup=keyboards.main)


@bot.callback_query_handler(func=lambda call:True)
def podcategors(call):

	if call.data[:12] == 'awhat_oplata':
		what_oplata = types.InlineKeyboardMarkup(row_width=2)
		what_oplata_qiwi = types.InlineKeyboardButton(text='🥝 Qiwi', callback_data='Depoziit_qiwi')
		what_oplataa_crypta = types.InlineKeyboardButton(text='💲 Криптовалюта', callback_data='crypt_oplata')
		what_oplataa_btc = types.InlineKeyboardButton(text='🎁 BTC ЧЕК', callback_data='btc_oplata')
		what_oplata.add(what_oplata_qiwi,what_oplataa_crypta,what_oplataa_btc)
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("SELECT * FROM reklama")
		row = q.fetchall()
		text = ''
		keyboard = types.InlineKeyboardMarkup()
		for i in row:
			text = f'{text}<a href="{i[2]}">{i[1]}</a>\n➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖\n'
		keyboard.add(types.InlineKeyboardButton(text='💰 Купить ссылку',callback_data='buy_reklama'))
		bot.send_message(call.message.chat.id, f'''<b>💎 Реклама:</b>

{text}
''' ,parse_mode='HTML', reply_markup=keyboard,disable_web_page_preview = True)
		bot.send_message(call.message.chat.id, 'Выбери способ для депозита', reply_markup=what_oplata)

	if call.data == 'crypt_oplata':
		bot.send_message(call.from_user.id,  '👁‍🗨 Временно не доступно')

	if call.data[:12] == 'btc_oplata':
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		msg = bot.send_message(call.from_user.id,  '👁‍🗨 Введите сумму для пополнения\n💵 Минимальный депозит - 100 руб', reply_markup=keyboards.otmena)
		bot.register_next_step_handler(msg, btc_oplata)


	if call.data[:13] == 'Depoziit_qiwi':
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton(text='✅ Проверить',callback_data='Check_Depozit_qiwi_'))
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("SELECT qiwi_phone FROM config where id = '1'")
		qiwi_phone = q.fetchone()
		qiwi_oplata_url = "https://qiwi.com/payment/form/99?extra['account']="+str(qiwi_phone[0])+"&extra['comment']="+str(call.message.chat.id)+"&amountInteger=100&amountFraction=0&currency=643&blocked[1]=account&blocked[2]=comment"
		keyboard.add(types.InlineKeyboardButton(text='💳 Перейти к оплате',url=qiwi_oplata_url))
		bot.send_message(call.message.chat.id, "📥 <b>Для совершения пополнения через QIWI кошелёк, переведите нужную сумму средств (минимум </b><code>100</code><b> руб) на номер кошелька указанный ниже, оставив при этом индивидуальный комментарий перевода:\n\n💳 Номер кошелька:</b> <code>%s</code>\n💬 <b>Коментарий к переводу:</b> <code>%s</code>" % (str(qiwi_phone[0]), str(call.message.chat.id)),parse_mode='HTML', reply_markup=keyboard)
		bot.send_message(call.message.chat.id, '⚠️  Депозит меньше 100р = подарок проекту !')

	if call.data[:19] == 'Check_Depozit_qiwi_':
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("SELECT qiwi_phone FROM config where id = 1")
		qiwi_phone = str(q.fetchone()[0])
		q.execute("SELECT qiwi_token FROM config where id = 1")
		qiwi_token = str(q.fetchone()[0])
		for payment in Qiwi(qiwi_token,qiwi_phone).get_payments(10, operation=OperationType.IN):
			q = q.execute('SELECT id FROM temp_pay WHERE txnid = ' + str(payment.raw['txnId']))
			temp_pay = q.fetchone()
			if 'RUB' in str(payment.currency) and str(payment.comment) == str(call.message.chat.id) and temp_pay == None and float(payment.amount) >= 100:
				q.execute("INSERT INTO temp_pay (txnid) VALUES ('%s')"%(payment.raw['txnId']))
				connection.commit()
				bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
				connection = sqlite3.connect('database.sqlite')
				q = connection.cursor()
				q.execute("update ugc_users set balans = balans + "+str(payment.amount)+" where id = " + str(call.message.chat.id))
				connection.commit()

				today = datetime.datetime.today()
				q.execute("INSERT INTO ugc_buys (idtovar,nametovar,date,data,userid,username,colvo,price,bot_name) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')"%('2124','afawf',today.strftime("%H:%M %d.%m.%Y"),'2124',call.message.chat.id,str(call.message.chat.first_name),'1',str(payment.amount), '212asas4'))
				connection.commit()
				q.execute("select ref from ugc_users where Id = " + str(call.message.chat.id))
				ref_user1 = q.fetchone()[0]
				if ref_user1 != '':
					add_deposit = int(payment.amount) / 100 * 5
					q.execute("update ugc_users set balans = balans + "+str(add_deposit)+" where id =" + str(ref_user1))
					connection.commit()
					bot.send_message(ref_user1, f'Реферал пополнил баланс и вам зачислинно {add_deposit} RUB',parse_mode='HTML')

				bot.send_message(config.admin, "<b>Новый депозит!</b>\nId Пользователя: " + str(call.message.chat.id)+"\nСумма: " + str(payment.amount),parse_mode='HTML')
				bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="✅ На ваш баланс зачислено "+str(payment.amount) +' руб')
				break
			else:
				bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="⚠ Оплата не найдена!")

	elif call.data == 'edit_praces':
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("SELECT rules FROM ugc_users  where id = "+str(call.message.chat.id))
		sms_prace = q.fetchone()
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		keyboard = types.InlineKeyboardMarkup()

		keyboard.add(types.InlineKeyboardButton(text=f'VIP | 1000р',callback_data='vip_1'),types.InlineKeyboardButton(text=f'Premium | 10000р',callback_data='vip_3'))
		keyboard.add(types.InlineKeyboardButton(text=f'VIP+ | 5000р',callback_data='vip_2'),types.InlineKeyboardButton(text=f'Premium+ | 30000р',callback_data='vip_4'))
		bot.send_message(call.message.chat.id, f'''➖ VIP: цена смс 12р
➖ VIP+: цена смс 10р
➖ Premium: цена смс 7р
➖ Premium+: цена смс 5р

⚠️ Все тарифы подключатся бесплатно, необходимо только наличие баланса на счету.''' ,parse_mode='HTML', reply_markup=keyboard)

	elif call.data == 'vip_1':
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q = q.execute("SELECT balans FROM ugc_users WHERE id = "+str(call.message.chat.id))
		check_balans = q.fetchone()
		if float(check_balans[0]) >= int(1000):
			q.execute("update ugc_users set rules = " + str(12) +  " where id =" + str(call.message.chat.id))
			connection.commit()
			bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="✅ Вы успешно сменили тариф")

		else:
			bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="⚠ Недостаточно средств")

	elif call.data == 'vip_2':
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q = q.execute("SELECT balans FROM ugc_users WHERE id = "+str(call.message.chat.id))
		check_balans = q.fetchone()
		if float(check_balans[0]) >= int(5000):
			q.execute("update ugc_users set rules = " + str(10) +  " where id =" + str(call.message.chat.id))
			connection.commit()
			bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="✅ Вы успешно сменили тариф")

		else:
			bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="⚠ Недостаточно средств")

	elif call.data == 'vip_3':
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q = q.execute("SELECT balans FROM ugc_users WHERE id = "+str(call.message.chat.id))
		check_balans = q.fetchone()
		if float(check_balans[0]) >= int(10000):
			q.execute("update ugc_users set rules = " + str(7) +  " where id =" + str(call.message.chat.id))
			connection.commit()
			bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="✅ Вы успешно сменили тариф")

		else:
			bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="⚠ Недостаточно средств")

	elif call.data == 'vip_4':
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q = q.execute("SELECT balans FROM ugc_users WHERE id = "+str(call.message.chat.id))
		check_balans = q.fetchone()
		if float(check_balans[0]) >= int(30000):
			q.execute("update ugc_users set rules = " + str(5) +  " where id =" + str(call.message.chat.id))
			connection.commit()
			bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="✅ Вы успешно сменили тариф")

		else:
			bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="⚠ Недостаточно средств")

	elif call.data == 'шаблоны':
			connection = sqlite3.connect('database.sqlite')
			q = connection.cursor()
			q.execute("SELECT rules FROM ugc_users  where id = "+str(call.message.chat.id))
			sms_prace = q.fetchone()
			keyboard = types.InlineKeyboardMarkup()
			keyboard.add(types.InlineKeyboardButton(text=f'Avito | {sms_prace[0]}р',callback_data='Avito'),types.InlineKeyboardButton(text=f'Avito 2.0 | {sms_prace[0]}р',callback_data='Avito_2'))
			keyboard.add(types.InlineKeyboardButton(text=f'Youla | {sms_prace[0]}р',callback_data='Youla'),types.InlineKeyboardButton(text=f'Youla 2.0 | {sms_prace[0]}р',callback_data='Youla_2'))
			keyboard.add(types.InlineKeyboardButton(text=f'TK | {sms_prace[0]}р',callback_data='TK'),types.InlineKeyboardButton(text=f'TK 2.0 | {sms_prace[0]}р',callback_data='TK_2'))
			bot.send_message(call.message.chat.id, f'ℹ️ Временно недоступно' ,parse_mode='HTML')

	elif call.data == 'Avito':
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("SELECT * FROM sms where servis = 'avito'")
		row = q.fetchall()
		q.close()
		text = ''
		keyboard = types.InlineKeyboardMarkup()
		for i in row:
			keyboard.add(types.InlineKeyboardButton(text=f'{i[0]}',callback_data=f'send_{i[0]}'))
			text = f'{text}id: <code>{i[0]}</code>| Текст сообшения: <code>{i[2]}</code>\n'
		msg = bot.send_message(call.message.chat.id, '<b>ℹ️Выберите id сообщения:</b>\n\n'+str(text),parse_mode='HTML', reply_markup=keyboard)

	elif call.data == 'сократить_ссылку':
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		msg = bot.send_message(call.message.chat.id, '<b>ℹ️ Отправьте ссылку:\n\nПример:</b> <code>https://yandex.ru/</code>',parse_mode='HTML', reply_markup=keyboards.otmena)
		bot.register_next_step_handler(msg,generator_url)

	elif call.data == 'Avito_2':
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("SELECT * FROM sms where servis = 'avito_2'")
		row = q.fetchall()
		q.close()
		text = ''
		keyboard = types.InlineKeyboardMarkup()
		for i in row:
			keyboard.add(types.InlineKeyboardButton(text=f'{i[0]}',callback_data=f'send_{i[0]}'))
			text = f'{text}id: <code>{i[0]}</code>| Текст сообшения: <code>{i[2]}</code>\n'
		msg = bot.send_message(call.message.chat.id, '<b>ℹ️Выберите id сообщения:</b>\n\n'+str(text),parse_mode='HTML', reply_markup=keyboard)

	elif call.data == 'Youla':
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("SELECT * FROM sms where servis = 'youla'")
		row = q.fetchall()
		q.close()
		text = ''
		keyboard = types.InlineKeyboardMarkup()
		for i in row:
			keyboard.add(types.InlineKeyboardButton(text=f'{i[0]}',callback_data=f'send_{i[0]}'))
			text = f'{text}id: <code>{i[0]}</code>| Текст сообшения: <code>{i[2]}</code>\n'
		msg = bot.send_message(call.message.chat.id, '<b>ℹ️Выберите id сообщения:</b>\n\n'+str(text),parse_mode='HTML', reply_markup=keyboard)

	elif call.data == 'Youla_2':
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("SELECT * FROM sms where servis = 'youla_2'")
		row = q.fetchall()
		q.close()
		text = ''
		keyboard = types.InlineKeyboardMarkup()
		for i in row:
			keyboard.add(types.InlineKeyboardButton(text=f'{i[0]}',callback_data=f'send_{i[0]}'))
			text = f'{text}id: <code>{i[0]}</code>| Текст сообшения: <code>{i[2]}</code>\n'
		msg = bot.send_message(call.message.chat.id, '<b>ℹ️Выберите id сообщения:</b>\n\n'+str(text),parse_mode='HTML', reply_markup=keyboard)

	elif call.data == 'TK':
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("SELECT * FROM sms where servis = 'tk'")
		row = q.fetchall()
		q.close()
		text = ''
		keyboard = types.InlineKeyboardMarkup()
		for i in row:
			keyboard.add(types.InlineKeyboardButton(text=f'{i[0]}',callback_data=f'send_{i[0]}'))
			text = f'{text}id: <code>{i[0]}</code>| Текст сообшения: <code>{i[2]}</code>\n'
		msg = bot.send_message(call.message.chat.id, '<b>ℹ️Выберите id сообщения:</b>\n\n'+str(text),parse_mode='HTML', reply_markup=keyboard)

	elif call.data == 'TK_2':
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("SELECT * FROM sms where servis = 'tk_2'")
		row = q.fetchall()
		q.close()
		text = ''
		keyboard = types.InlineKeyboardMarkup()
		for i in row:
			keyboard.add(types.InlineKeyboardButton(text=f'{i[0]}',callback_data=f'send_{i[0]}'))
			text = f'{text}id: <code>{i[0]}</code>| Текст сообшения: <code>{i[2]}</code>\n'
		msg = bot.send_message(call.message.chat.id, '<b>ℹ️Выберите id сообщения:</b>\n\n'+str(text),parse_mode='HTML', reply_markup=keyboard)

	elif call.data[:5] == 'send_':
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute(f"SELECT text FROM sms where id = {call.data[5:]}")
		row = q.fetchone()
		text_sms = row[0]
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("INSERT INTO sms_temp (id,text,link) VALUES ('%s', '%s', '%s')"%(call.message.chat.id,text_sms,'0'))
		connection.commit()
		msg = bot.send_message(call.message.chat.id, '<b>ℹ️ Отправьте ссылку:\n\nПример:</b> <code>https://yandex.ru/</code>',parse_mode='HTML', reply_markup=keyboards.otmena)
		bot.register_next_step_handler(msg,send)

	elif call.data == 'svoi_text':
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		msg = bot.send_message(call.message.chat.id, '<b>ℹ️ Отправьте текст сообщения:</b> \n\nМаксимум 70 символов',parse_mode='HTML', reply_markup=keyboards.otmena)
		bot.register_next_step_handler(msg,svoi_text)

	elif call.data[:16] == 'good_oplata_btc_':
		global user_id_balance
		user_id_balance = call.data[16:]
		#bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		msg = bot.send_message(call.message.chat.id, '<b>ℹ️ Введите сумму:</b>',parse_mode='HTML', reply_markup=keyboards.otmena)
		bot.register_next_step_handler(msg,user_id_balance11)

	elif call.data == "vau":
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton(text='➕ Создать',callback_data=f'vau_add'),types.InlineKeyboardButton(text=' ✔️ Активировать',callback_data=f'vau_good'))
		bot.send_message(call.message.chat.id, "<b>Что вы бы хотели сделать?</b>",parse_mode='HTML', reply_markup=keyboard)

	elif call.data == "нистроики":
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton(text='🔄 Сменить | 70р',callback_data=f'смена_порта'))
		keyboard.add(types.InlineKeyboardButton(text='ℹ️ Информация',callback_data=f'инфо_номер'))
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q = q.execute("SELECT numbers FROM port WHERE id = "+str(call.message.chat.id))
		numberssss = q.fetchone()
		bot.send_message(call.message.chat.id,  f'''➖ Порт для отправки: {'Личный' if numberssss != None else 'Публичный'}

⚠️ Для стабильной работы необходимо сменить порт''',parse_mode='HTML', reply_markup=keyboard)

	elif call.data == "смена_порта":
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="✅ Ожидайте")
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q = q.execute("SELECT balans FROM ugc_users WHERE id = "+str(call.message.chat.id))
		check_balans = q.fetchone()
		if float(check_balans[0]) >= int(70):
			connection = sqlite3.connect('database.sqlite')
			q = connection.cursor()
			q.execute("update ugc_users set balans = balans - "+str(70)+" where id = " + str(call.message.chat.id))
			connection.commit()
			local = client.available_phone_numbers('US').local.list(limit=1)

			for record in local:
				print(record.friendly_name)
				local = record.friendly_name
# local = client.available-phone_nubmers('US').local.list(limit=20)



				text = local.replace('(','').replace(')','').replace(' ','').replace('-', '')
				print(text)
				phone = f'+1{text}'
				print(phone)
				incoming_phone_number = client.incoming_phone_numbers \
            	          .create(phone_number=f'{phone}')
				connection = sqlite3.connect('database.sqlite', uri=True, check_same_thread=False)
				q = connection.cursor()
				q.execute(f"SELECT numbers FROM port where id = {call.message.chat.id}")
				check_phone = q.fetchone()
				if check_phone == None:
					q.execute("INSERT INTO port (id,numbers) VALUES ('%s','%s')"%(call.message.chat.id,str(phone)))
					connection.commit()
				else:
					q.execute(f"update port set numbers = '{phone}' where id = '{call.message.chat.id}'")
					connection.commit()

				print(incoming_phone_number.sid)
			#смена номера
			#смена номера
			#смена номера
			#смена номера
				bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="✅ Вы успешно сменили порт")

		else:
			bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="⚠ Недостаточно средств")


	elif call.data == "инфо_номер":
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton(text='⬅️ Назад',callback_data=f'нистроики'))
		bot.send_message(call.message.chat.id, '''➖ Порты служат для отправки сообщений и если вы работаете на публичном то ответственность за доставку на мтс, билайн мы не несём.

➖ Время жизни 1 порта примерно 100 сообщений на мтс и билайн. Остольные операторы связи пропустят и 10000 сообщений''',parse_mode='HTML', reply_markup=keyboard)

	elif call.data == "vau_add":
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("SELECT balans FROM ugc_users where id is " + str(call.message.chat.id))
		balanss = q.fetchone()
		msg = bot.send_message(call.message.chat.id, f'''На какую сумму RUB выписать Ваучер ? (Его сможет обналичить любой пользователь, знающий код).

Доступно: {balanss[0]} RUB''',parse_mode='HTML', reply_markup=keyboards.otmena)
		bot.register_next_step_handler(msg, vau_add)

	elif call.data == "vau_good":
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		msg = bot.send_message(call.message.chat.id, '''Для активации ваучера отправьте его код:''',parse_mode='HTML', reply_markup=keyboards.otmena)
		bot.register_next_step_handler(msg, vau_good)

	elif call.data == "lotosca":
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton(text=f'⭐️ Lite',callback_data=f'igra_ticet'))
		keyboard.add(types.InlineKeyboardButton(text=f'💎 Gold',callback_data=f'igra_ticet_vip'))
		bot.send_message(call.message.chat.id, '''В какое играем ?''',parse_mode='HTML', reply_markup=keyboard)

	elif call.data[:16] == 'restart':
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		bot.send_message(call.message.chat.id,f'👑 Добро пожаловать, <a href="tg://user?id={call.message.chat.id}">{call.message.chat.first_name}</a>',parse_mode='HTML', reply_markup=keyboards.main)


	elif call.data == 'buy_reklama':
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton(text=f'✔️ Согласен, купить| 500 RUB',callback_data=f'yes_buy_reklama'))
		bot.send_message(call.message.chat.id, '''<b>В витрине отображается 5 добавленных ссылок.
Добавленная ссылка, будет отображена первой, а последняя будет удалена.

Ссылку увидят:
➖В приветствие.
➖При депозите.
➖После отправки сообщений.
➖В выборе сервиса отправки.</b>''',parse_mode='HTML', reply_markup=keyboard)

	elif call.data == 'yes_buy_reklama':
		bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
		msg = bot.send_message(call.message.chat.id, '<b>ℹ️ Введите текст ссылки:</b>',parse_mode='HTML', reply_markup=keyboards.otmena)
		bot.register_next_step_handler(msg, yes_buy_reklama)









bot.polling(True)
