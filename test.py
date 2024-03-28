import os
from tgbotzero import*
from random import choice

TOKEN = '6889583474:AAG0c0OJJN6nerPrIxhUjBdWt9QNUamldiI'

d = dict()
r = dict()
r_old = dict()
j = dict()
f = dict()

afrika = []
with open('afrika.txt') as afrika_file:
    lines = afrika_file.readlines()
    for line in lines:
        domen = line.split(': .')[1]
        afrika.append(domen)

#h = open('africa.txt','r',encoding='UTF-8')
#afrika = h.readlines()
#for i in afrika:
#    afrika[i].replace(afrika[i],afrika[-1:-2])
#hh = open('countrs.txt','r',encoding='UTF-8')
#jj = hh.readlines()

with open('countrs.txt') as file:
    lines = file.readlines()
    for line in lines:
        domen = line[1:3]
        if domen in afrika and os.path.isfile(f'flags/{domen}.png'):
            cntrnm = line.split(' — ')[1].replace('\n','')
            d[domen] = cntrnm

countries = list(d.keys())

def on_command_start(msg, chat_id):
    r[chat_id] = choice(countries)
    f[chat_id] = 0
    j[chat_id] = 0

    return [Image('flags/' + str(r[chat_id]) + '.png'), 'назови страну']

def on_message(msg, chat_id):
    if f[chat_id] != 7:
        r_old[chat_id] = r[chat_id]
        countries.remove(r[chat_id])
        r[chat_id] = choice(countries)
        f[chat_id] += 1
        if msg.title() == r[chat_id]:
            j[chat_id] += 1
        return [Image('flags/' + str(r[chat_id]) + '.png'), 'назови страну']
    else:
        return 'твой результат: ' + str(j[chat_id])

run_bot()