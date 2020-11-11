from dis import dis
import telebot
from telebot import types
import keyboards as kb
from config import token
import re #Для проверки текста на наличие цифр и др. https://tproger.ru/translations/regular-expression-python/
import pymysql.cursors
from adds import connect
from connection import register
bot = telebot.TeleBot(token)
connection = connect()
import math
#reg_c = 0 #Статус зарегистрирован или нет

districts = ["Заводской", "Центральный", "Советский", 
"Первомайский", "Партизанский", "Ленинский", 
"Октябрьский", "Московский", "Фрунзенский"]
actions = ["Баскетбол","Волейбол","Футбол","Бег","Ролики","Велосипед","Воркаут"]
# cursor.execute в def



def execute(user_id,what):
    try:
        with connection.cursor() as cursor:
            cursor.execute ( f"SELECT `{what}` FROM `tbot` WHERE `user_id`={user_id}" )
            qq = cursor.fetchone ()
            for o , p in qq.items () :
                name = p
            return name
    except:
        execute(user_id,what)
#def update(user_id,what,num):
 #   with connection.cursor() as cursor:
  #      cursor.execute ( f"UPDATE `tbot` SET `{what}`={num} WHERE `user_id`={user_id}" )
#        connection.commit()

# Команда /start
@bot.message_handler ( commands=[ 'start' ] )
def comm_start(message) :

    user_id = message.chat.id
    print ( user_id )
    with connection.cursor() as cursor:
        reg = cursor.execute(f"SELECT * FROM tbot WHERE user_id={user_id}")
        if reg == 0:
            msg = bot.send_message ( user_id ,"Привет человек, я помогу тебе найти компанию. Нажми на кнопку регистрации." ,reply_markup = kb.reg_keyboard )
            bot.register_next_step_handler ( msg , reg_or_no )
            register(user_id)
        else:
            msg = bot.send_message ( user_id, "Ты хочешь пройти регистрацию заново? Да/Нет", reply_markup = kb.reg_yes_or_no)
            bot.register_next_step_handler( msg, yes_or_no )

def yes_or_no(message):
    user_id = message.chat.id
    text = message.text
    if text == 'Да':
        msg = bot.send_message ( user_id ,"Тогда давай заново заполним анкету про тебя. Нажми на кнопку регистрации." , reply_markup = kb.reg_keyboard )
        bot.register_next_step_handler ( msg , reg_or_no )
    elif text == 'Нет':
        msg = bot.send_message ( user_id , "Выберите что хотите сделать." , reply_markup=kb.mein_meny_keybord )
        bot.register_next_step_handler ( msg , reaction_mein_menu_buttons )
    else:
        msg = bot.send_message ( user_id, "Пожалуйста, выберите одну из кнопок (Да/Нет)", reply_markup = kb.reg_yes_or_no )
        bot.register_next_step_handler( msg, yes_or_no)

def reg_or_no(message):
    user_id = message.chat.id
    text = message.text
    if text == 'Регистрация':
        reg(user_id)

    else:
        msg = bot.send_message( user_id, "Пожалуйста нажмите на кнопку 'Регистрация'.")
        bot.register_next_step_handler(msg, reg_or_no)

def reg(user_id):
    # Дабавлям в дб id
    msg = bot.send_message ( user_id , "Введи имя (1/3)" )
    bot.register_next_step_handler ( msg , get_name )

def get_name(message):
    name = message.text
    print ( str ( name ) ) #Отправляет сообщение в боте (Имя)
    user_id = message.chat.id
    result = re.findall(r'\d', str(name))
    if result != [] or '/' in str(name):
        msg = bot.send_message( user_id, "Введены неверные символы! Введите заново")
        bot.register_next_step_handler ( msg, get_name )
    else:
        # Дабавляем в bd имя
        msg = bot.send_message ( user_id , "Введи фамилию (2/3)" )
        bot.register_next_step_handler ( msg , get_surname )
        with connection.cursor() as cursor:
            cursor.execute ( f"UPDATE tbot SET name='{name}' WHERE user_id={user_id}" )
            connection.commit ()





def get_surname(message) :
    surname = message.text
    print ( str ( surname ) ) #Отправляет сообщение в боте (Фамилия)
    result = re.findall(r'\d', str(surname))
    user_id = message.chat.id
    if result != []:
        msg = bot.send_message( user_id, "Введены неверные символы! Введите заново")
        bot.register_next_step_handler ( msg, get_surname )
    else:
        # Дабавляем в bd фамилию
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE tbot SET surname='{surname}' WHERE user_id={user_id}")
            connection.commit()
        msg = bot.send_message ( user_id , "Введи возраст (3/3)" )
        bot.register_next_step_handler ( msg , get_age )


def get_age(message) :
    username = message.chat.username
    age = message.text
    print ( str ( age ) ) #Отправляет сообщение в боте (Возраст)
    user_id = message.chat.id
    result = re.findall( r'\D', age)
    if result != [] or int(age)<0 or int(age)>99:
        msg = bot.send_message( user_id, "Введены неверные символы! Введите заново")
        bot.register_next_step_handler ( msg, get_age )
    else:
    # Дабавляем в bd возраст
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE `tbot` SET `age`={age},`reg`=1, `username`='{str(username)}' WHERE `user_id`={user_id}")
            connection.commit()
        msg = bot.send_message ( user_id , "Спасибо за регистрацию. Выберите, что хотите сделать.",reply_markup = kb.mein_meny_keybord)
        bot.register_next_step_handler(msg, reaction_mein_menu_buttons)


#################################################################################################################
########## ВСЕ СВЯЗАННОЕ С МЕНЮ #################################################################################
#################################################################################################################


@bot.message_handler( commands = ['menu'] )

def reaction_mein_menu_buttons(message):
    user_id = message.chat.id
    text = message.text
    if text == 'Найти группу 🔍' :
        find_group(user_id)

    elif text == 'Создать группу ➕' :
        make_group(user_id)
    
    else:
        msg = bot.send_message(user_id, "Пожалуйста, нажмите на одну из кнопок!",
        reply_markup = kb.mein_meny_keybord)
        bot.register_next_step_handler( msg, reaction_mein_menu_buttons)


#################################################################################################################
######################################### Создание группы #######################################################
#################################################################################################################


def make_group(user_id): #Создание группы
    msg = bot.send_message(user_id, "Выбери район места встречи \ Чтобы вернуться в меню выберите: Назад",
    reply_markup = kb.distr_keybord)
    bot.register_next_step_handler(msg, get_dist)

def get_dist(message):
    text = message.text
    user_id = message.chat.id
    if text in districts:
        with connection.cursor () as cursor : #Добавление в бд выбранный район
            col = 0
            for i in districts:
                col =+ 1
                if text == i:
                    cursor.execute(f"UPDATE `tbot` SET `group`={col} WHERE `user_id`={user_id}")
            connection.commit ()

        msg = bot.send_message( user_id, "Отправь мне геопозицию места встречи")
        bot.register_next_step_handler_by_chat_id(user_id , get_geopos)
    elif text == "Назад": #Возвращает назад в меню
        msg = bot.send_message( user_id, "Вы вернулись в меню" , reply_markup = kb.mein_meny_keybord)
        bot.register_next_step_handler( msg, reaction_mein_menu_buttons)
    else: #Активируется если пользователь написал не то, что нужно
        msg = bot.send_message( user_id, "Нажми на одну из кнопок или выйди в меню" , 
        reply_markup = kb.distr_keybord)
        bot.register_next_step_handler( msg, get_dist)

def get_geopos(Location): #Геопозиция
    user_id = Location.chat.id
    try:
        loc = Location.location
        plong = Location.location.longitude
        plat = Location.location.latitude
        with connection.cursor () as cursor :
            cursor.execute ( f"UPDATE tbot SET plong={plong},plat={plat} WHERE user_id={user_id} " )
            connection.commit()
        msg  = bot.send_message( user_id, "Выбери категрию", reply_markup= kb.kind_ex_keybord)
        bot.register_next_step_handler( msg, get_kind_of_act)
        #Сохранить в BD значение plat и plong /|\
    except:
        if Location.text == "Назад":
            msg = bot.send_message ( user_id , "Вы вернулись в меню" , reply_markup=kb.mein_meny_keybord )
            bot.register_next_step_handler ( msg , reaction_mein_menu_buttons )
        else:
            msg = bot.send_message( user_id, "Оправь мне пожалуста геопозицию, а не это!")
            bot.register_next_step_handler( msg, get_geopos)

def get_kind_of_act(message):
    text = message.text
    C = True
    user_id = message.chat.id
    with connection.cursor() as cursor:
        col = 0
        if text in actions:
            for i in actions:
                col += 1
                if text == i:
                    cursor.execute ( f"UPDATE `tbot` SET `groupa`={col} WHERE `user_id`={user_id}" )

        elif text == "Назад":
            C = False
            msg = bot.send_message ( user_id , "Вы вернулись в меню" , reply_markup=kb.mein_meny_keybord )
            bot.register_next_step_handler ( msg , reaction_mein_menu_buttons )
        else:
            C = False
            msg = bot.send_message(user_id, "Нажми на одну из кнопок", reply_markup= kb.kind_ex_keybord)
            bot.register_next_step_handler( msg, get_kind_of_act)
        if(C == True):
            msg = bot.send_message(user_id,"Пришли мне точное время и дату / Например: 18:00 04.10")
            bot.register_next_step_handler( msg, discr)
            connection.commit()

def discr(message):  #Описание группы это время
    user_id = message.chat.id 
    text = message.text
    if '.' in text and ':' in text:
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE `tbot` SET `group_text`='{str(text)}', `group_reg`=1 WHERE `user_id`={user_id}")
            groupnum = execute(user_id, "group")
            cursor.execute ( f"SELECT `group` FROM `tbot` WHERE `group`={groupnum}" )
            qq = cursor.fetchall ()
            col = len(qq)
            connection.commit()
        msg = bot.send_message ( user_id , "Вы создали группу. Всего групп в вашем районе "+str(col), reply_markup=kb.wait_room ) #Колличество групп в одном районе
        bot.register_next_step_handler ( msg , group_wait )
    else:
        msg = bot.send_message(user_id, "Отправь так, как написанно в примере / Например: 18:00 04.10")
        bot.register_next_step_handler( msg, discr)

def group_wait(message):
    #  user Комната ожидания, человек не может использовать кнопки кроме как удалить группу! Если кто то присоединяется к нему то его оповещают об этом
    user_id = message.chat.id
    text = message.text
    count = 0
    count = execute(user_id, "groupid")

    if text == "Удалить группу":
        msg = bot.send_message( user_id, "Вы точно хотите удалить группу? Да/Нет")
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE tbot SET groupid = 1 WHERE user_id = {user_id}")
            connection.commit()
        bot.register_next_step_handler( msg, group_wait)

    elif text == "Да" and count == 1:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT user_id FROM tbot WHERE groupid={user_id}")
            qq = cursor.fetchall()
            if qq != ():
                for i in qq:
                    for b,c in i.items():
                        cursor.execute(f"UPDATE `tbot` SET `groupid`=0, `group`=0, `groupa`=0, `plat`=NULL,`plong`=NULL WHERE `user_id`={c}")
                        msg = bot.send_message( c, "Группа была удалена её создателем",reply_markup=kb.mein_meny_keybord)
                        bot.register_next_step_handler(msg, reaction_mein_menu_buttons)
            cursor.execute(f"UPDATE `tbot` SET `group_reg`=0, `group`=NULL, `groupa`=NULL, `groupid`=0, `group_text`=NULL, `plat`=NULL, `plong`=NULL  WHERE `user_id`={user_id}")
            connection.commit()
            msg = bot.send_message( user_id, "Вы успешно удалили группу и были возвращены в меню", reply_markup=kb.mein_meny_keybord)
            bot.register_next_step_handler ( msg , reaction_mein_menu_buttons )

    elif text == "Список участников":
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT user_id FROM tbot WHERE groupid={user_id}")
            qq = cursor.fetchall()
            print(qq)
            textl = "Ваш список участников:"
            names = execute(user_id , "name")
            surnames = execute(user_id, "surname")
            usernames = execute(user_id, "username")
            col = 1
            textl = textl + "\n" + str(col) + ". @" + str(usernames) + " " + str(names) + " " + str(surnames)

            if qq == ():
                msg = bot.send_message( user_id, "Никто еще не присоединился к вашей группе")
            else:
                for i in qq:
                    for b,c in i.items():
                        col += 1
                        name = execute(c, "name")
                        surname = execute(c, "surname")
                        username = execute(c, "username")

                        textl = textl + "\n" + str(col) + ". @" + str(username) + " " + str(name) + " " + str(surname) + '\n'
                msg = bot.send_message( user_id, textl )
            bot.register_next_step_handler( msg, group_wait)
    elif count == 1 and text != "Да" and text != "Нет":
        msg = bot.send_message( user_id, "Вы вроде хотели удалить группу. Напишите: Да/Нет ")
        bot.register_next_step_handler( msg, group_wait)
    elif count == 1 and text == "Нет":
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE tbot SET groupid=0 WHERE user_id={user_id}")
            connection.commit()
        msg = bot.send_message( user_id, "Вы были возвращены в меню вашей группы", reply_markup= kb.wait_room)
        bot.register_next_step_handler( msg, group_wait)
    else:
        msg = bot.send_message( user_id, "Я не знаю, что вы от меня хотите", reply_markup= kb.wait_room)
        bot.register_next_step_handler( msg, group_wait)

#################################################################################################################
######################################### Поиск группы ##########################################################
#################################################################################################################

def find_group(user_id):
    msg = bot.send_message( user_id, "Выбери свой район (1/3)", reply_markup= kb.distr_keybord)
    bot.register_next_step_handler( msg, find_cat)

def find_cat(message):
    text = message.text
    user_id = message.chat.id
    if text in districts:
        with connection.cursor () as cursor :  # Добавление в бд выбранный район
            col = 0
            for i in districts:
                col += 1
                if text == i:
                    cursor.execute ( f"UPDATE `tbot` SET `group`={col} WHERE `user_id`={user_id}" )
            connection.commit ()
        msg = bot.send_message( user_id, "Для того что бы определить группу, которая находится ближе к вам отправьте вашу геолокацию (2/3)")
        bot.register_next_step_handler( msg, geo_find)
    elif text == "Назад":
        msg = bot.send_message ( user_id , "Вы вернулись в меню" , reply_markup=kb.mein_meny_keybord )
        bot.register_next_step_handler ( msg , reaction_mein_menu_buttons )
    else:
        msg = bot.send_message( user_id, "Выбери один из районов", reply_markup= kb.distr_keybord)
        bot.register_next_step_handler( msg, find_cat)

def geo_find(Location):
    user_id = Location.chat.id
    try :
        loc = Location.location
        plong = Location.location.longitude
        plat = Location.location.latitude
        with connection.cursor () as cursor :
            cursor.execute ( f"UPDATE `tbot` SET `plong`={plong},`plat`={plat} WHERE `user_id`={user_id}" )
            connection.commit ()
        msg = bot.send_message ( user_id , "Выбери категорию для поиска (3/3)" , reply_markup=kb.kind_ex_keybord )
        bot.register_next_step_handler ( msg , act_find )
        # Сохранить в BD значение plat и plong /|\
    except :
        if Location.text == "Назад":
            msg = bot.send_message ( user_id , "Вы вернулись в меню" , reply_markup=kb.mein_meny_keybord )
            bot.register_next_step_handler ( msg , reaction_mein_menu_buttons )
        else:
            msg = bot.send_message ( user_id , "Оправь мне пожалуста геопозицию, а не это!" )
            bot.register_next_step_handler ( msg , geo_find )

def act_find(message):
    text = message.text
    C = True
    user_id = message.chat.id
    seachid = []
    texta = ""
    con = 0
    with connection.cursor () as cursor :
        col = 0
        if text in actions:
            for i in actions:
                col += 1
                if text == i:
                    cursor.execute ( f"UPDATE `tbot` SET `groupa`={col} WHERE `user_id`={user_id}" )
            
        elif text == "Назад" :
            C = False
            msg = bot.send_message ( user_id , "Вы вернулись в меню" , reply_markup=kb.mein_meny_keybord )
            bot.register_next_step_handler ( msg , reaction_mein_menu_buttons )
        else :
            C = False
            msg = bot.send_message ( user_id , "Нажми на одну из кнопок" , reply_markup=kb.kind_ex_keybord )
            bot.register_next_step_handler ( msg , get_kind_of_act )

        if C == True:
            group = execute(user_id,"group")
            groupa = execute(user_id, "groupa")
            plat = execute(user_id, "plat")
            plong = execute(user_id,"plong")
            cursor.execute ( f"SELECT `user_id` FROM `tbot` WHERE `group`={group} and `groupa`={groupa} and `group_reg`=1" )
            qq = cursor.fetchall ()
            for i in qq :
                for b , c in i.items () :
                    seachid.append ( c )
            if seachid == [ ] :
                msg = bot.send_message ( user_id ,"В вашем районе нету группы с такой категорией, вы были возвращены в главное меню" , reply_markup=kb.mein_meny_keybord)
                bot.register_next_step_handler ( msg , reaction_mein_menu_buttons )
            else :
                for i in seachid :
                    print ( i )
                    name = execute(i, "name")
                    surname = execute(i,"surname")
                    con +=1
                    platid = execute(i, "plat")
                    plongid = execute(i,"plong")
                    grouptext = execute(i,"group_text")
                    #-----------------ВЫЧИСЛЕНИЯ-----------------
                    delplong = plong - plongid
                    delplat = plat - platid
                    traectory = math.sqrt ( delplong ** 2 + delplat ** 2 )
                    traectory = traectory*10000
                    traectory = int(traectory)
                    #---------------------------------------------

                    texta = texta +str(con)+ ". " + str ( name ) + " " + str ( surname ) + " в "+str(traectory)+" метрах от вас" + "\nОписание: " + str(grouptext) + "\n"
                    msg = bot.send_message ( user_id , "Выберите группу к которой хотите присоединится:\n" + texta + "Например: 1", reply_markup=kb.vbor)
                    bot.register_next_step_handler(msg, search)
            connection.commit()

def search(message):
    text = message.text
    user_id = message.chat.id
    seachid = []
    texta = ""
    C = False
    with connection.cursor() as cursor:
        group = execute(user_id, "group")
        groupa = execute(user_id, "groupa")
        plat = execute(user_id, "plat")
        plong = execute(user_id, "plong")
        name = execute(user_id,"name")
        surname = execute(user_id, "surname")

        cursor.execute(f"SELECT `user_id` FROM `tbot` WHERE `group`={group} and `groupa`={groupa} and `group_reg`=1")
        qq = cursor.fetchall()
        for i in qq:
            for b,c in i.items():
                seachid.append(c)
        print(seachid)
        if seachid == []:
            msg = bot.send_message( user_id, "В вашем районе нету группы с такой категорией, вы были возвращены в главное меню", reply_markup=kb.mein_meny_keybord)
            bot.register_next_step_handler( msg, reaction_mein_menu_buttons)
            C = True
        elif text == "Назад":
            msg = bot.send_message( user_id, "Вы вернулись в меню", reply_markup=kb.mein_meny_keybord )
            bot.register_next_step_handler( msg, reaction_mein_menu_buttons)
        else:
            if text.isdigit() == True:
                for i in seachid:
                    if seachid[int(text)-1] == i:
                        print("ВЫ ВСТУПИЛИ В ГРУППУ")
                        cursor.execute(f"UPDATE `tbot` SET `groupid`={i} WHERE `user_id`={user_id}")
                        bot.send_message( i, name + " "+ surname + " присоединил(ся/ась) к вашей группе")
                        #-----Получение данных у пользователя к которому присоединились
                        namepar = execute(i,"name")
                        surnamepar = execute(i,"surname")
                        connection.commit()
                        C = True
                        #------------------------------------------------------------------

                        msg = bot.send_message( user_id, "Вы вступили в группу к " + namepar + " " + surnamepar, reply_markup=kb.invite_room)
                        bot.register_next_step_handler( msg, invite_room )
        if C == False:
            msg = bot.send_message( user_id, "Выбери группу из списка выше или `Назад` что бы выйти", reply_markup=kb.vbor)
            bot.register_next_step_handler( msg, search)

def invite_room(message):
    text = message.text
    user_id = message.chat.id
    texta = "Список участников: \n"
    if text == "Список участников":
        with connection.cursor() as cursor:
            groupid = execute(user_id,"groupid")
            cursor.execute(f"SELECT `user_id` FROM `tbot` WHERE `groupid` = {groupid}")
            qq = cursor.fetchall()
            print(qq)
            for i in qq:
                for b,c in i.items():
                    con = c
                    col = 0
                    print(con)
                    name = execute(con, "name")
                    surname = execute(con, "surname")
                    username = execute(con, "username")
                    col += 1
                    texta = texta + str(col) + ". @"+ str(username) + " " + str(name) + " " + str(surname) + " \n"
            
            nameow = execute(groupid, "name")
            surnameow = execute(groupid, "surname")
            usernameoo = execute(groupid,"username")
            texta = texta + str(col+1)+". @"+ str(usernameoo)+ " " + str(nameow) + " " + str(surnameow)
            msg = bot.send_message( user_id, texta)
            bot.register_next_step_handler( msg, invite_room)

    elif text == "Покинуть группу":
        with connection.cursor() as cursor:
            name = execute(user_id, "name")
            surname = execute(user_id, "surname")
            groupid = execute(user_id, "groupid")
            cursor.execute(f"UPDATE `tbot` SET `groupid`=0,`group`=NULL,`groupa`=0,`plat`=NULL,`plong`=NULL WHERE user_id={user_id}")
            connection.commit()

        bot.send_message( groupid, name + " " + surname + " вышел из вашей группы")
        msg = bot.send_message( user_id, "Вы вышли из группы и вернулись в меню", reply_markup=kb.mein_meny_keybord)
        bot.register_next_step_handler( msg, reaction_mein_menu_buttons)
#########################################
if __name__ == '__main__' :
    bot.infinity_polling ()
