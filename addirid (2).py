import sqlite3
import telebot
from telebot import types
import keyboards as kb
import  re
from config import token
from bot import Group,FG
conn = sqlite3.connect('server.db')
bot = telebot.TeleBot(token)
group = {}
fgroup = {}
grops = []
districts = ["Заводской", "Центральный", "Советский",
"Первомайский", "Партизанский", "Ленинский",
"Октябрьский", "Московский", "Фрунзенский"]
actions = ["🏀Баскетбол","🏐Волейбол","⚽Футбол","🏃Бег","🛼Ролики","🚴Велосипед","🏋Воркаут"]
groupes = []
dis ={}
act ={}
for i in range(0,len(districts)):
    groupes.append([])
    dis[districts[i]] = i
    for j in range(0,len(actions)):
        groupes[i].append([])
for j in range(0,len(actions)):
    act[actions[j]] = j;


@bot.message_handler( commands=['start'])
def conn_main(message):
    user_id = message.chat.id
    print(message)
    with sqlite3.connect ('server.db') as conn :
        cursor = conn.cursor()
        p  = cursor.execute(f"SELECT user_id FROM tbot WHERE user_id = {user_id}").fetchone()

        print(p)
        if p!=None:
            msg = bot.send_message(user_id, "Вы хотите пройти регистрацию заново? Да/Нет", reply_markup=kb.reg_yes_or_no)
            bot.register_next_step_handler(msg, yes_or_no)
            #conn.close()
        else:
            msg = bot.send_message(user_id, "Привет, я sport_bot. Я могу помочь вам найти компанию для занятия спортом. Для начала пройдите регистрацию. Чтобы начать регистрацию, нажмите на клавишу или отправьте мне сообщение 'Регистрация'. Для комфортной работы со мной, вы должны иметь username. Если у вас его нет, создаейте его в настройках профиля.", reply_markup=kb.reg_keyboard)
            bot.register_next_step_handler(msg, get_reg)
            #conn.close()


def yes_or_no(message):
    user_id = message.chat.id
    if "Да" in message.text:
        msg = bot.send_message(user_id, "Введите имя и фамилию ( к примеру: Иванов Иван )")
        bot.register_next_step_handler(msg, get_name)
    elif  "Нет" in message.text:
        msg = bot.send_message(user_id, "Вы перенесены в главное меню", reply_markup=kb.mein_meny_keybord)
        bot.register_next_step_handler(msg, mein_menu)
    else:
        msg = bot.send_message(user_id, "Выберите 'Да/Нет'")
        bot.register_next_step_handler(msg, yes_or_no)

def get_reg(message):
    user_id = message.chat.id
    if str(message.content_type) != "text":
        msg = bot.send_message(user_id, "Пожалуйста нажмите на кнопку или отправьте мне 'Регистрация'.", reply_markup=kb.reg_keyboard)
        bot.register_next_step_handler(msg,get_reg)
    elif message.text != 'Регистрация':
        msg = bot.send_message(user_id, "Пожалуйста нажмите на кнопку или отправьте мне 'Регистрация'.", reply_markup=kb.reg_keyboard)
        bot.register_next_step_handler(msg, get_reg)
    else:
        msg = bot.send_message(user_id, "Введите имя и фамилию ( к примеру: Иванов Иван )")
        bot.register_next_step_handler(msg,get_name)

def get_name(message):
    user_id = message.chat.id
    username = message.chat.username
    if str(message.content_type) != "text":
        msg = bot.send_message(user_id, "Вы ввели некорректные данные")
        bot.register_next_step_handler(msg, get_name)
    elif re.findall(r'\d', message.text) != [] or (' ' in message.text)==False :
        msg = bot.send_message(user_id, "В вашем сообщение присутствуют некорректные символы или данные не полные")
        bot.register_next_step_handler(msg, get_name)
    else:
        with sqlite3.connect('server.db') as conn:
            cursor = conn.cursor()
            if cursor.execute(f"""SELECT user_id FROM tbot WHERE user_id = {user_id}""").fetchone() != None:
                cursor.execute(f"""UPDATE tbot SET name = '{message.text}'""")
            else:
                cursor.execute(f"""INSERT INTO tbot (user_id,name,username) VALUES ({user_id},'{message.text}','{username}')""")
            conn.commit()
        msg = bot.send_message(user_id, "Спасибо за регистрацию. Вы перенесены в главное меню", reply_markup=kb.mein_meny_keybord)
        bot.register_next_step_handler(msg, mein_menu)

@bot.message_handler( commands = [ 'menu'])
def mein_menu(message):
    user_id = message.chat.id
    if(str(message.content_type)!='text'):
        msg = bot.send_message(user_id, "Вы ввели некорректные данные", reply_markup=kb.mein_meny_keybord)
        bot.register_next_step_handler(msg,mein_menu)
    elif 'Создать группу' in message.text:
        msg = bot.send_message(user_id, "Выберите район места встречи (1/4)\ Чтобы вернуться в меню выберите: Назад", reply_markup=kb.distr_keybord)
        bot.register_next_step_handler(msg, get_dist)
    elif 'Найти группу' in message.text:
        msg = bot.send_message(user_id, "Выберите район в котором вы хотите найти группу (1/3)", reply_markup=kb.distr_keybord)
        bot.register_next_step_handler(msg, find_dist)
    elif '/start'== message.text:
        conn_main(message)
    else:
        msg = bot.send_message(user_id, "Я вас не понимаю, нажмите на одну из кнопок", reply_markup=kb.mein_meny_keybord)
        bot.register_next_step_handler(msg, mein_menu)

#######Создание группы########

def get_dist(message):
    user_id = message.chat.id
    if(str(message.content_type)!='text'):
        msg = bot.send_message(user_id, "Вы ввели некорректные данные", reply_markup=kb.distr_keybord)
        bot.register_next_step_handler(msg, get_dist)
    elif message.text in districts:
        gp = Group(user_id)
        gp.distr = message.text
        group[user_id] = gp
        msg = bot.send_message(user_id, "Выберите категорию группы(2/4)", reply_markup=kb.kind_ex_keybord)
        bot.register_next_step_handler(msg,get_kind)
    elif message.text=='Назад':
        msg = bot.send_message(user_id, "Вы были возвращены в главное меню", reply_markup=kb.mein_meny_keybord)
        bot.register_next_step_handler(msg,mein_menu)
    else:
        msg = bot.send_message(user_id, "Выберите район из предложенных", reply_markup=kb.distr_keybord)
        bot.register_next_step_handler(msg, get_dist)

def get_kind(message):
    user_id = message.chat.id
    if (str(message.content_type) != 'text'):
        msg = bot.send_message(user_id, "Вы ввели некорректные данные", reply_markup=kb.kind_ex_keybord)
        bot.register_next_step_handler(msg, get_kind)
    elif message.text in actions:
        group[user_id].kind = message.text
        msg = bot.send_message(user_id, "Отправьте мне геопозицию места встречи(3/4)", reply_markup=kb.vbor)
        bot.register_next_step_handler(msg, get_geo)
    elif message.text == 'Назад':
        msg = bot.send_message(user_id, "Вы были возвращены в главное меню", reply_markup=kb.mein_meny_keybord)
        bot.register_next_step_handler(msg, mein_menu)
    else:
        msg = bot.send_message(user_id, "Выберите категрию из предложенных", reply_markup=kb.kind_ex_keybord)
        bot.register_next_step_handler(msg, get_kind)

def get_geo(location):
    user_id = location.chat.id
    if (str(location.content_type) != 'location'):
        if(location.text=='Назад'):
            msg = bot.send_message(user_id, "Вы были возвращены в главное меню", reply_markup=kb.mein_meny_keybord)
            bot.register_next_step_handler(msg, mein_menu)
        else:
            msg = bot.send_message(user_id, "Вы ввели некорректные данные, вы должны отправить геопозицию.")
            bot.register_next_step_handler(msg, get_geo)
    else:
        Plong = location.location.longitude
        Plat = location.location.latitude
        group[user_id].plat = Plat
        group[user_id].plong = Plong
        msg = bot.send_message(user_id, "Отправьте мне описание группы(Адрес,время,дату и т.д)(4/4)", reply_markup=kb.vbor)
        bot.register_next_step_handler(msg, get_opis)

def get_opis(message):
    user_id = message.chat.id
    if (str(message.content_type) != 'text'):
        msg = bot.send_message(user_id, "Вы ввели некорректные данные")
        bot.register_next_step_handler(msg, get_opis)
    elif message.text == 'Назад':
        msg = bot.send_message(user_id, "Вы были возвращены в главное меню", reply_markup=kb.mein_meny_keybord)
        bot.register_next_step_handler(msg, mein_menu)
    else:
        group[user_id].opis = message.text
        gp = group[user_id]
        n1 = dis[str(gp.distr)]
        n2 = act[str(gp.kind)]
        groupes[n1][n2].append(gp.groupid)
        print(groupes)
        del group[user_id]
        with sqlite3.connect('server.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"""INSERT INTO groups (groupid,distr,kind,plat,plong,opis) VALUES ({gp.groupid},'{gp.distr}','{gp.kind}',{gp.plat},{gp.plong},'{gp.opis}')""")
            cursor.execute(f"""UPDATE tbot SET groupid = {user_id} WHERE user_id={user_id}""")
            conn.commit()
        msg = bot.send_message(user_id, "Ваша группа успешно зарегистрирована. Вы перенесены в лобби группы.", reply_markup=kb.wait_room)
        bot.register_next_step_handler(msg,group_wait)

def group_wait(message):
    user_id = message.chat.id
    print(message.text)
    if (str(message.content_type) != 'text'):
        msg = bot.send_message(user_id, "Вы ввели некорректные данные", reply_markup=kb.wait_room)
        bot.register_next_step_handler(msg, group_wait)
    elif message.text == "📃Список участников":
        mas = "Список участников: "
        with sqlite3.connect('server.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"""SELECT name,username FROM tbot WHERE groupid = {user_id}""")
            qq = cursor.fetchall()
            if len(qq) == 1:
                msg = bot.send_message(user_id, "К вашей группе еще никто не присоединился", reply_markup=kb.wait_room)
                bot.register_next_step_handler(msg,group_wait)
            else:
                col = 0
                for a,b in qq:
                    col += 1
                    mas = mas + "\n" + str(col) + ". " + str(a) +" @"+  str(b)
                msg = bot.send_message(user_id,mas,reply_markup=kb.wait_room)
                bot.register_next_step_handler(msg, group_wait)
    elif message.text == "❌Удалить группу":

        with sqlite3.connect('server.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"""SELECT distr,kind FROM groups WHERE groupid = {user_id}""")
            qq = cursor.fetchall()
            for a in qq:
                n1 = dis[str(a[0])]
                n2 = act[str(a[1])]
                groupes[n1][n2].remove(user_id)
            print(groupes)
            cursor.execute(f"""SELECT user_id FROM tbot WHERE groupid = {user_id}""")
            qq = cursor.fetchall()
            for a in qq:
                print(a[0])
                cursor.execute(f"UPDATE tbot SET groupid=NULL WHERE user_id = {a[0]}")
                msg = bot.send_message(a[0],"Группа была удалена, вы возвращены в главное меню", reply_markup=kb.mein_meny_keybord)
                bot.register_next_step_handler(msg,mein_menu)
            cursor.execute(f"""DELETE FROM groups WHERE groupid={user_id}""")
            conn.commit()
    else:
        msg = bot.send_message(user_id,"Я не понимаю вас")
        bot.register_next_step_handler(msg,group_wait)

#########ПОИСК ГРУППЫ#########

def find_dist(message):
    user_id = message.chat.id
    if (str(message.content_type) != 'text'):
        msg = bot.send_message(user_id, "Вы ввели некорректные данные", reply_markup=kb.distr_keybord)
        bot.register_next_step_handler(msg, find_dist)
    elif message.text in districts:
        gp = FG(user_id)
        gp.distr = message.text
        fgroup[user_id] = gp
        msg = bot.send_message(user_id, "Выберите категрию для поиска группы(2/3)", reply_markup=kb.kind_ex_keybord)
        bot.register_next_step_handler(msg, find_kind)
    elif message.text == 'Назад':
        msg = bot.send_message(user_id, "Вы были возвращены в главное меню", reply_markup=kb.mein_meny_keybord)
        bot.register_next_step_handler(msg, mein_menu)
    else:
        msg = bot.send_message(user_id, "Выберите район из предложенных", reply_markup=kb.distr_keybord)
        bot.register_next_step_handler(msg, find_dist)

def find_kind(message):
    user_id = message.chat.id
    if (str(message.content_type) != 'text'):
        msg = bot.send_message(user_id, "Вы ввели некорректные данные", reply_markup=kb.kind_ex_keybord)
        bot.register_next_step_handler(msg, find_kind)
    elif message.text in actions:
        fgroup[user_id].kind = message.text
        msg = bot.send_message(user_id, "Отправьте мне геопозицию, чтобы я рассчитал примерное расстояние до места встречи(3/3)", reply_markup=kb.vbor)
        bot.register_next_step_handler(msg, find_geo)
    elif message.text == 'Назад':
        msg = bot.send_message(user_id, "Вы были возвращены в главное меню", reply_markup=kb.mein_meny_keybord)
        bot.register_next_step_handler(msg, mein_menu)
    else:
        msg = bot.send_message(user_id, "Выберите категорию из предложенных", reply_markup=kb.kind_ex_keybord)
        bot.register_next_step_handler(msg, find_kind)

def find_geo(location):
    user_id = location.chat.id
    if (str(location.content_type) != 'location'):
        if(location.text=='Назад'):
            msg = bot.send_message(user_id, "Вы были возвращены в главное меню", reply_markup=kb.mein_meny_keybord)
            bot.register_next_step_handler(msg, mein_menu)
        else:
            msg = bot.send_message(user_id, "Вы ввели некорректные данные, вы должны отправить геопозицию.")
            bot.register_next_step_handler(msg, find_geo)
    else:
        Plong = location.location.longitude
        Plat = location.location.latitude
        fgroup[user_id].plat = Plat
        fgroup[user_id].plong = Plong

        n1 = dis[str(fgroup[user_id].distr)]
        n2 = act[str(fgroup[user_id].kind)]
        if len(groupes[n1][n2]) == 0:
            msg = bot.send_message(user_id, "По вашему запросу групп не найдено", reply_markup=kb.mein_meny_keybord)
            bot.register_next_step_handler(msg,mein_menu)
        else:
            bot.send_message(user_id, "Выберите группу или смотрите следующую")
            send_mes(user_id,0,n1,n2)

def send_mes(user_id,pos,n1,n2):
    ln = len(groupes[n1][n2])
    if pos>=ln:
        bot.send_message(user_id,"Группы закончились, при дальнейшем поиске вы будете видеть уже просмотренные группы")
        pos = 0
    groupid = groupes[n1][n2][pos]
    mas = ""
    with sqlite3.connect('server.db') as conn:
        cursor = conn.cursor()
        cursor.execute( f"SELECT opis,plat,plong FROM groups WHERE groupid = {groupid}")
        qq = cursor.fetchone()
        cursor.execute( f"SELECT username,name FROM tbot WHERE user_id = {groupid}")
        bq = cursor.fetchone()
        print(qq)
        print(bq)
        mas+='@'+bq[0]+' '+bq[1]+'\n'+"Описание: \n"+qq[0]
        bot.send_message(user_id, mas)
        bot.send_location(user_id, qq[1], qq[2], reply_markup=make_kb(groupid))

def make_kb(user_id):
    ikb = types.InlineKeyboardMarkup()
    ib1 = types.InlineKeyboardButton(text='Войти', callback_data=str(user_id))
    ib2 = types.InlineKeyboardButton(text='Далее', callback_data='d')
    ib3 = types.InlineKeyboardButton(text='В главное меню', callback_data='m')
    ikb.add(ib1,ib2).add(ib3)
    return ikb

@bot.callback_query_handler(func =lambda call: True)
def get_call(call):
    user_id = call.message.chat.id
    if 'm' in call.data:
        with sqlite3.connect('server.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"""SELECT groupid FROM tbot WHERE user_id={user_id}""")
            a = cursor.fetchone()
            if a[0] != None:
                msg = bot.send_message(user_id, "Вы не можете этого сделать",reply_markup=kb.invite_room)
                return 
        msg=  bot.send_message(user_id, "Вы вернулись в главное меню", reply_markup=kb.mein_meny_keybord)
        bot.register_next_step_handler(msg,mein_menu)
    elif 'd' in call.data:
        with sqlite3.connect('server.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"""SELECT groupid FROM tbot WHERE user_id={user_id}""")
            a = cursor.fetchone()
            if a[0] != None:
                msg = bot.send_message(user_id, "Вы не можете этого сделать", reply_markup=kb.invite_room)
                return
        fgroup[user_id].pos+=1
        n1 = dis[str(fgroup[user_id].distr)]
        n2 = act[str(fgroup[user_id].kind)]
        send_mes(user_id,fgroup[user_id].pos,n1,n2)
    else:
        groupid = int(call.data)

        with sqlite3.connect('server.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"""SELECT groupid FROM tbot WHERE user_id={user_id}""")
            a = cursor.fetchone()
            if a[0] != None:
                msg = bot.send_message(user_id, "Вы уже состоите в группе и не можете присоединиться к этой группе",reply_markup=kb.invite_room)
                return
            else:
                cursor.execute(f"""SELECT groupid FROM groups WHERE groupid={groupid}""")
                b = cursor.fetchone()
                if b != []:
                    cursor.execute(f"""SELECT username,name FROM tbot WHERE user_id={groupid}""")
                    qq = cursor.fetchone()
                    cursor.execute(f"""SELECT username,name FROM tbot WHERE user_id={user_id}""")
                    qb = cursor.fetchone()
                    cursor.execute(f"""SELECT user_id FROM tbot WHERE groupid={groupid}""")
                    qp = cursor.fetchall()
                    cursor.execute(f"""UPDATE tbot SET groupid = {groupid} WHERE user_id={user_id}""")
                    conn.commit()
                    for a in qp:
                        bot.send_message(a[0],'@'+qb[0]+' '+qb[1]+' вошел в группу')
                    msg = bot.send_message(user_id,'Вы вошли в группу к ' + '@' + qq[0]+' '+qq[1],reply_markup=kb.invite_room)
                    bot.register_next_step_handler(msg,invite_room)
                else:
                    msg = bot.send_message(user_id, "Такой группы уже не существует, вы возвращены в главное меню", reply_markup=kb.mein_meny_keybord)
                    bot.register_next_step_handler(msg,mein_menu)

def invite_room(message):
    user_id = message.chat.id
    if (str(message.content_type) != 'text'):
        msg = bot.send_message(user_id, "Вы ввели некорректные данные", reply_markup=kb.invite_room)
        bot.register_next_step_handler(msg, invite_room)
    elif message.text=="📃Список участников":
        with sqlite3.connect('server.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"""SELECT groupid FROM tbot WHERE user_id = {user_id}""")
            qb = cursor.fetchone()
            groupid = qb[0]
            cursor.execute(f"""SELECT name,username FROM tbot WHERE groupid = {groupid}""")
            qq = cursor.fetchall()
            col = 0
            mas = ""
            for a, b in qq:
                col += 1
                mas = mas + "\n" + str(col) + ". " + str(a) + " @" + str(b)
            msg = bot.send_message(user_id, mas, reply_markup=kb.invite_room)
            bot.register_next_step_handler(msg, invite_room)
    elif message.text=="❌Покинуть группу":
        with sqlite3.connect('server.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"""SELECT groupid FROM tbot WHERE user_id ={user_id}""")
            qq = cursor.fetchone()
            groupid = qq[0]
            cursor.execute(f"""UPDATE tbot SET groupid = NULL WHERE user_id={user_id}""")
            cursor.execute(f"""SELECT user_id FROM tbot WHERE groupid ={groupid}""")
            qp = cursor.fetchall()
            cursor.execute(f"""SELECT username,name FROM tbot WHERE user_id ={user_id}""")
            qb = cursor.fetchone()
            del fgroup[user_id]
            conn.commit()
            for a in qp:
                bot.send_message(a[0],'@'+qb[0]+' '+qb[1]+' вышел из группы')
        msg = bot.send_message(user_id, "Вы успешно вышли из группы",reply_markup=kb.mein_meny_keybord)
        bot.register_next_step_handler(msg, mein_menu)
    else:
        msg = bot.send_message(user_id, "Я вас не понимаю, нажмите на одну из кнопок", reply_markup=kb.invite_room)
        bot.register_next_step_handler(msg, invite_room)






if __name__ == '__main__':
    bot.infinity_polling()