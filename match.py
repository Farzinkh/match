import telebot
import ast
import logging
import os
import time
import sqlite3
from flask import Flask, request
from telebot import types,util
from random import seed,randint
from openpyxl import Workbook
workbook = Workbook()
sheet = workbook.active #for working on xlsx file
#telebot.logger.setLevel(logging.DEBUG) #for debugging telegram api
API_TOKEN = os.getenv("API_TOKEN")#this value will set localy on your host and will obtain from botfather
WEBHOOK_LISTEN = '0.0.0.0' #default
server = Flask(__name__)
lines=open('questions.txt','r').readlines()
count,countans,answerlist,questionsdoc,questionlist=0,5,[],{},[]
connection = sqlite3.connect('userDetails.db',check_same_thread=False)
while countans<len(lines):
	answerlist.append(int(lines[countans].rstrip("\n")))
	countans+=6
while count<len(lines):
	questionlist.append(lines[count].rstrip("\n"))
	questionsdoc[lines[count].rstrip("\n")]=[lines[count+1].rstrip("\n"),lines[count+2].rstrip("\n"),lines[count+3].rstrip("\n"),lines[count+4].rstrip("\n")]
	count+=6
seed(1)
crossIcon = u"\u274C"
bot = telebot.TeleBot(API_TOKEN,threaded=True,num_threads=10)
#bot=telebot.AsyncTeleBot(API_TOKEN) #if you want your bot respond asynchronus
markup = types.ReplyKeyboardMarkup()
itembtn1 = types.KeyboardButton('My point')
itembtn2 = types.KeyboardButton('Fight on')
itembtn3 = types.KeyboardButton('billboard')
itembtn4 = types.KeyboardButton('home')
markup.row(itembtn1)
markup.row(itembtn2)
markup.row(itembtn3)
markup.add(itembtn4)
mksighup = types.ForceReply(selective=False)
markup2=types.ReplyKeyboardMarkup()
itembtn1 = types.KeyboardButton(u"\u2160")
itembtn2 = types.KeyboardButton(u"\u2161")
itembtn3 = types.KeyboardButton(u"\u2162")
itembtn4 = types.KeyboardButton(u"\u2163")
markup2.row(itembtn1)
markup2.row(itembtn2)
markup2.row(itembtn3)
markup2.add(itembtn4)
sighuplist={}
def database(user_id,chat_id,questionnum,phone_number,username,firstname,lastname,point,state):
    connection.execute('''CREATE TABLE IF NOT EXISTS userdetails(user_id int,chat_id int,questionnum int,phone_number int,username text,firstname text,lastname text,point int,state text)''')
    connection.execute("INSERT INTO userdetails VALUES (?,?,?,?,?,?,?,?,?)",(user_id,chat_id,questionnum,phone_number,username,firstname,lastname,point,state))
    connection.commit()
def savedb(message):
	DATA =sighuplist[message.from_user.username]
	user_id=DATA['user_id']
	chat_id=DATA['chat_id']
	questionnum=DATA['questionnum']
	phone_number=DATA['phone_number']
	username=DATA['username']
	firstname=DATA['firstname']
	lastname=DATA['lastname']
	point=DATA['point']
	state=DATA['state']
	database(user_id,chat_id,questionnum,phone_number,username,firstname,lastname,point,state)

def Updatedb(task):
    sql = ''' UPDATE tasks
              SET questionnum = ? ,
                  point = ? ,
                  state = ?,
              WHERE id = ?'''
    cur = connection.cursor()
    cur.execute(sql, task)
    connection.commit()

@bot.message_handler(commands=['end'])
def surrend(message):
	try:
		sighuplist[message.from_user.username]['state']='finish'
		bot.reply_to(message, 'oh my friend {} it was so hard for you,i know'.format(message.from_user.first_name),reply_markup=markup)
	except:
		pass
@bot.message_handler(commands=['begin'])
def beginner(message):
	if message.from_user.username in sighuplist.keys():
		if sighuplist[message.from_user.username]['state']=='finish' :
			bot.reply_to(message, 'sorry you lose your chance !!!')
		elif sighuplist[message.from_user.username]['state']=='on match':
			bot.reply_to(message,'you are in match right now!')
			getquestion(message)
		elif sighuplist[message.from_user.username]['state']=='alive':
			sighuplist[message.from_user.username]['state']='on match'
			sighuplist[message.from_user.username]['timer']=time.time()
			getquestion(message)
	else:
		bot.reply_to(message, 'signup please \n /start & /begin')

def check(message,num):
    g=questionsdoc[questionlist[sighuplist[message.from_user.username]['questionnumbers'][-2]]][num]
    if (time.time()-sighuplist[message.chat.username]['timer'])==45 or (time.time()-sighuplist[message.chat.username]['timer'])>45:
        bot.send_message(message.chat.id,'your time is finished!!!')
    elif g==questionsdoc[questionlist[sighuplist[message.chat.username]['questionnumbers'][-2]]][answerlist[sighuplist[message.chat.username]['questionnumbers'][-2]]-1]:
        sighuplist[message.chat.username]['point']+=20

def sighup(message):
    if message.reply_to_message != None:
        try:
            if message.text=='flow':
                doc = open('output.xlsx', 'rb')
                bot.send_document(message.chat.id, doc)
            elif  len(message.text) != 11:
                msg = bot.reply_to(message, 'wrong input please input your phone number correctly: \n ex:09xxxxxxxxx',reply_markup=mksighup)
            else:
                bot.send_message(message.chat.id, " Ok now enter your first name :")
                sighuplist[message.from_user.username]={'user_id':message.from_user.id,'firstname':'','lastname':'','phonenumber':message.text,'questionnumbers':[0],'state':'alive','point':0,'questionnum':0,'timer':time.time(),'chat_id':message.chat.id}
        except:
            pass
    elif  message.content_type=='text':
#        try:
            if message.text=='My point':
                bot.reply_to(message, "your point is :{}".format(sighuplist[message.from_user.username]['point']))
            elif message.text=='billboard':
                bot.send_message(message.chat.id, billboard(message))
            elif message.text=='home':
                send_welcome(message)
            elif message.text=='Fight on':
                bot.send_message(message.chat.id, "Alright you have only 30 sec for each question , 20 question and only one chance \n this are your commands\nfor surrendering /end \nfor begining /begin ")
            if sighuplist[message.from_user.username]['firstname'] =='':
                sighuplist[message.from_user.username]['firstname']=message.text
                bot.reply_to(message, "Good {} enter your lastname:".format(message.text))
            elif sighuplist[message.from_user.username]['lastname']=='':
                sighuplist[message.from_user.username]['lastname']=message.text
                savedb(message)
                bot.reply_to(message, "Well done {} {} your signup is complete".format(sighuplist[message.from_user.username]['firstname'],sighuplist[message.from_user.username]['lastname']))
                bot.send_message(message.chat.id, "Please choose from  this options", reply_markup=markup)
            elif message.from_user.username in sighuplist.keys():
               if  sighuplist[message.from_user.username]['state']=='finish':
                  pass
               elif sighuplist[message.from_user.username]['questionnum'] ==20 or sighuplist[message.from_user.username]['questionnum']>20 :
                  bot.send_message(message.chat.id,u"\u26Fe"+'congratulation you have answered to all questions\nand your point is :{} \njust take rest and relax'.format(sighuplist[message.from_user.username]['point']),reply_markup=markup)
                  sighuplist[message.from_user.username]['state']='finish'
                  Updatedb((sighuplist[message.from_user.username]['questionnum'], sighuplist[message.from_user.username]['point'],sighuplist[message.from_user.username]['state'],sighuplist[message.from_user.username]['user_id']))
               else:
                 sighuplist[message.from_user.username]['timer']=time.time()
                 sighuplist[message.from_user.username]['questionnum']+=1
                 Updatedb((sighuplist[message.from_user.username]['questionnum'], sighuplist[message.from_user.username]['point'],sighuplist[message.from_user.username]['state'],sighuplist[message.from_user.username]['user_id']))
                 if message.text==u"\u2160":
                   check(message,0)
                   getquestion(message)
                 elif message.text==u"\u2161":
                   check(message,1)
                   getquestion(message)
                 elif message.text==u"\u2162":
                   check(message,2)
                   getquestion(message)
                 elif message.text==u"\u2163":
                   check(message,3)
                   getquestion(message)
#        except:
#            pass
    else:
        bot.reply_to(message, "wrong input!!!")

def getquestion(message):
    s=questionlist[sighuplist[message.from_user.username]['questionnumbers'][-1]]
    g=questionsdoc[s]
    for text in util.split_string('{}\n{}\n{}\n{}\n{}'.format("".join([str(sighuplist[message.from_user.username]['questionnum']),':',s]),"".join([u"\u2160",":",g[0]]),"".join([u"\u2161",":",g[1]]),"".join([u"\u2162",":",g[2]]),"".join([u"\u2163",":",g[3]])), 3000):
        bot.send_message(message.chat.id,text=text,reply_markup=markup2)
    number=randint(0,len(questionlist)-1)
    while number in sighuplist[message.chat.username]['questionnumbers']:
        number=randint(0,len(questionlist)-1)
        pass
    sighuplist[message.from_user.username]['questionnumbers'].append(number)
    return None

def billboard(message):
	champions,first,second,third=['','',''],0,0,0
	connection.row_factory = sqlite3.Row
	cur = connection.cursor()
	cur.execute('SELECT username,point FROM userdetails')
	result = cur.fetchone()
	for i in result:
		if i[1]==first or i[1]>first:
			first=i[1]
			champions[0]='{} : {}'.format(i[0],i[1])
			continue
		if i[1]==second or i[1]>second:
			second=i[1]
			champions[1]='{} : {}'.format(i[0],i[1])
			continue
		if	i[1]==third or i[1]>third:
			third=i[1]
			champions[2]='{} : {}'.format(i[0],i[1])
			continue
	return '{}\n{}\n{}'.format(champions[0],champions[1],champions[2])

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
	try:
		if message.from_user.username==None:
			bot.send_message(message.chat.id,"hmmm it seems like that you dont have username account so go to telegram setting and set one to continue!")
		elif sighuplist.get(message.from_user.username)!=None:
			bot.send_message(message.chat.id, "Please choose from  this options", reply_markup=markup)
		else:
			bot.reply_to(message,'hi {} Welcome to home we have examination hear'.format(message.from_user.first_name))
			bot.reply_to(message, "Enter your phone number:", reply_markup=mksighup)
	except:
		pass
@bot.message_handler(func=sighup)
def startmatch(message):
	if sighuplist[message.from_user.username]['firstname'] !='':
		bot.reply_to(message, "Please choose from options", reply_markup=markup)

@bot.message_handler(content_types=['document', 'audio'])
def handle_docs_audio(message):
	pass

@bot.message_handler(commands=['alpha'])
def output(message):
	print(message.from_user.first_name," is in alpha office")
	bot.reply_to(message, "Hi mr/mis {} you are in alpha office enter password to receive results".format(message.from_user.first_name),reply_markup=mksighup)
	row=1
	for key , value in sighuplist.items():
		sheet["A{}".format(row)]=key
		sheet["b{}".format(row)]=value['firstname']
		sheet["c{}".format(row)]=value['lastname']
		sheet["d{}".format(row)]=value['phonenumber']
		sheet["e{}".format(row)]=value['point']
		sheet["f{}".format(row)]=value['state']
		row+=1
	workbook.save(filename="output.xlsx")

@server.route('/' + API_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200
@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://civilmatch.herokuapp.com/{}".format(API_TOKEN)) #this will create by heroku create command
    return "!", 200

if __name__ == "__main__":
    server.run(host=WEBHOOK_LISTEN, port=int(os.environ.get("PORT", "8443")))
