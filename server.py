# -*- coding: utf-8 -*-
from flask import Flask, request
import logging
import telebot
import datetime
from telebot import types, apihelper
import config
import sqlite3
from flask import Flask,request

bot = telebot.TeleBot(config.bot_token)
app = Flask(__name__)

@app.route('/', methods=['POST'])
def hello_world():
	message_sid = request.values.get('MessageSid', None)
	message_status = request.values.get('MessageStatus', None)
	connection = sqlite3.connect('database.sqlite')
	q = connection.cursor()
	q.execute(f"SELECT id FROM logi where text = '{message_sid}'")
	qiwi_phone = q.fetchone()
	print(message_sid)
	print(message_status)
	if message_status == 'delivered':
		bot.send_message(qiwi_phone[0], '✔️ Сообщение доставленно',parse_mode='HTML')
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("update statistika set sms_good = sms_good +" + str(1) +  " where id =" + str(1))
		connection.commit()

	if message_status == 'sent':
		connection = sqlite3.connect('database.sqlite')
		q = connection.cursor()
		q.execute("update statistika set sms_send = sms_send +" + str(1) +  " where id =" + str(1))
		connection.commit()
		q.execute("update statistika set balans_service = balans_service -" + str('0.04') +  " where id =" + str(1))
		connection.commit()
	
	return 'HTTP 200 OK'
if __name__ == '__main__':
	app.run()