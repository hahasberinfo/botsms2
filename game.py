# -*- coding: utf-8 -*-
import telebot
import datetime
from telebot import types, apihelper
import sqlite3
import random
import os
import time
import requests
import config
from datetime import timedelta,datetime


# Получаем токен бота !
bot_token=config.gamebot_token

bot = telebot.TeleBot(bot_token)

print('start')

@bot.message_handler(commands=['start'])
def start_message(message):
	userid = str(message.chat.id)
	username = str(message.from_user.username)
	connection = sqlite3.connect('database.sqlite', uri=True, check_same_thread=False)
	q = connection.cursor()
	q.execute(f"SELECT id FROM ugc_users where id = {message.chat.id}")
	bots_start = q.fetchone()
	if bots_start == None:
		q.execute("INSERT INTO ugc_users (id,name,balans,ref,ref_colvo,rules) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')"%(userid,username,'0','0','0','20'))
		connection.commit()


@bot.message_handler(content_types=['document', 'text','photo','sticker'])
def send_text(message):

	if message.chat.type == 'group' or message.chat.type == 'supergroup' :
		if message.text[:6] == '/game ':
			connection = sqlite3.connect('database.sqlite', uri=True, check_same_thread=False)
			q = connection.cursor()
			q.execute(f"SELECT id FROM ugc_users where id = {message.from_user.id}")
			bots_start = q.fetchone()
			if bots_start != None:
				if message.text[6:].isdigit() == True and str(message.text[6:]) != "0":
					q.execute(f"SELECT balans FROM ugc_users where id = '{message.from_user.id}'")
					player_balans = q.fetchone()[0]
					if int(player_balans) >= int(message.text[6:]):
						gen_id = random.randint(1,9999999)
						q.execute("INSERT INTO ugc_games (id,creater,summa) VALUES ('%s','%s','%s')"%(gen_id ,message.from_user.id,message.text[6:]))
						connection.commit()
						q.execute(f"update ugc_users set balans = balans - '{message.text[6:]}' where id = '{message.from_user.id}'")
						connection.commit()
						keyboard = types.InlineKeyboardMarkup()
						keyboard.add(types.InlineKeyboardButton(text='Играть',callback_data=f'зайти_лобби_{gen_id}'))
						bot.send_message(message.chat.id,f"🎲 Новая игра #LC{gen_id} на {message.text[6:]} руб от <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>",parse_mode='HTML',reply_markup=keyboard)
					else:
						bot.send_message(message.chat.id,f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>, баланса не хватает, пополнение баланса: @SMSKA_ROBOT",parse_mode='HTML')
				else:
					bot.send_message(message.chat.id,f'Не верно указаны аргументы',parse_mode='HTML')
			else:
				bot.send_message(message.chat.id,f'⚠️ Вы не можете играть тк не являетесь пользователем бота: @SMSKA_ROBOT',parse_mode='HTML')
	else:
		if str(message.chat.id) == '1146794357' or str(message.chat.id) == '1146794357':
			if message.text == 'инфа':
				connection = sqlite3.connect('database.sqlite', uri=True, check_same_thread=False)
				q = connection.cursor()
				q.execute(f"SELECT count(id) FROM ugc_games")
				coun = q.fetchone()[0]
				q.execute(f"select sum(summa) from ugc_games")
				ss = q.fetchone()[0]
				ssg = ss/100*15
				bot.send_message(message.chat.id,f'Всего игр: {coun}\nПолучили: {ssg}',parse_mode='HTML')


@bot.callback_query_handler(func=lambda call:True)
def callback_inline(call):
	if call.data[:12] == 'зайти_лобби_':
		connection = sqlite3.connect('database.sqlite', uri=True, check_same_thread=False)
		q = connection.cursor()
		q.execute(f"SELECT id FROM ugc_users where id = {call.from_user.id}")
		bots_start = q.fetchone()
		if bots_start != None:
			q.execute(f"SELECT balans FROM ugc_users where id = '{call.from_user.id}'")
			player_balans = q.fetchone()[0]
			q.execute(f"SELECT summa FROM ugc_games where id = '{call.data[12:]}'")
			summa_game = q.fetchone()[0]
			q.execute(f"SELECT creater FROM ugc_games where id = '{call.data[12:]}'")
			creater = q.fetchone()[0]

			if str(creater) != str(call.from_user.id):
				if int(player_balans) >= int(summa_game):
					player_creator = f"<a href='tg://user?id={creater}'>{creater}</a>"
					player_two = f"<a href='tg://user?id={call.from_user.id}'>{call.from_user.id}</a>"
					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"🎲 Игра #LC{call.data[12:]}\nИграют: {player_creator} и {player_two}",parse_mode='HTML')
					q.execute(f"update ugc_games set second_player = '{call.from_user.id}' where id = '{call.data[12:]}'")
					connection.commit()
					q.execute(f"update ugc_users set balans = balans - '{summa_game}' where id = '{call.from_user.id}'")
					connection.commit()
					bot.send_message(call.message.chat.id,f'🎲 Игра #LC{call.data[12:]}\n⌛️ Генерируем победителя',parse_mode='HTML')
					# bot.send_sticker(call.message.chat.id,"CAACAgIAAxkBAAIlm17o2MGn1xSSdTe0l-5CP8F3GYaVAAL2AAPluQga_IFE0NTtdZ4aBA")
					time.sleep(5)
					user_win = random.randint(1,2)
					adding = int(summa_game)/100*85
					adding_admin = int(summa_game)/100*15
					if user_win==1:
						q.execute(f"update ugc_users set balans = balans + '{adding}' where id = '{creater}'")
						connection.commit()
						q.execute(f"update ugc_users set balans = balans + '{summa_game}' where id = '{creater}'")
						connection.commit()
						q.execute(f"update ugc_users set balans = balans + '{adding_admin}' where id = '1031811029'")
						connection.commit()
						q.execute(f"update ugc_games set itog = '{creater}' where id = '1031811029'")
						connection.commit()
						bot.send_message(call.message.chat.id,f'🎲 Игра #LC{call.data[12:]}\nПобедил: {player_creator}',parse_mode='HTML')
					else:
						q.execute(f"update ugc_users set balans = balans + '{adding}' where id = '{call.from_user.id}'")
						connection.commit()
						q.execute(f"update ugc_users set balans = balans + '{summa_game}' where id = '{call.from_user.id}'")
						connection.commit()
						q.execute(f"update ugc_users set balans = balans + '{adding_admin}' where id = '1031811029'")
						connection.commit()
						q.execute(f"update ugc_games set itog = '{call.from_user.id}' where id = '1031811029'")
						connection.commit()
						bot.send_message(call.message.chat.id,f'🎲 Игра #LC{call.data[12:]}\nПобедил: {player_two}',parse_mode='HTML')
				else:
					bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Баланса не хватает, пополнение баланса: @SMSKA_ROBOT")
			else:
				print('ddss')
		else:
			bot.send_message(call.message.chat.id,f'⚠️ Вы не можете играть тк не являетесь пользователем бота: @SMSKA_ROBOT',parse_mode='HTML')





bot.polling(True)
