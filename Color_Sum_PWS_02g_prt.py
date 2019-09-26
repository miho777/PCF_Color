########################################
# 01e for Debug
# 01f for Piper output(Bold,JST)
# 02g for Redis PWS
#
########################################

import os
import uuid             
import redis            # Redis
import datetime
from flask import Flask   
from password import *  # for pw .ignore

# JST TimeZone
#jst = pytz.timezone('Asia/Tokyo')


### debug
#hostname = os.environ["hostname"]
#password = os.environ["password"]
# port = os.environ["port"]
pws_port = 6379
pws_KeyResult = "result"
pws_KeyRef = "Reference"
Local_DB = "127.0.0.1"


### switch ###
Redis_type = 1          # 0:local , 1:Remote

app = Flask(__name__)
COLOR = "#777789"
db_key = ["Red", "Gre", "Blu", "Unk"]
chk_count = []


############ Get judge data from Redis ######################################          
def read_db():
    global chk_count
    global r
    del chk_count[:]
    if Redis_type == 0:                                                         ####### Local Redis
        print "0: local Redis " + Local_DB
        r = redis.Redis(host=Local_DB, port=pws_port, db=1)
    else:                                                                       ####### Remote Redis
        print "1: Remote Redis " + REDIS_HOST
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PW)

    j = 0
    for i in db_key:
        print r.llen(i)
        chk_count.append((r.llen(i)- 3) // 3)     # ret.append(dat)
        j = j + 1
    print chk_count

### Save result to PWS redis #########################
def save_pcfdb():
    # r = redis.Redis(host = pws_host, port = pws_port, password = pws_pw)

    db_flush = 0                        ### if flush=1
    if db_flush is not 0:               ### 
        print "flush PWS Redis DB"
        r.flushall()                    ### debug
    
    for i in range(4):
        r.rpush(pws_KeyResult, chk_count[i])  # put Judge count

    lst_len = r.llen(pws_KeyResult)
    print "PWS list length " +  str(lst_len)
    print r.lrange(pws_KeyResult, 0, -1)                # print all list
    print r.lrange(pws_KeyResult, lst_len - 4, lst_len) # print new
    
def get_now():
    global now_t
    now_t = (datetime.datetime.now()) + datetime.timedelta(hours=9)
    print now_t    
    now_t = now_t.strftime("%m/%d %H:%M:%S")                                      
    print "JST..."
    print now_t

@app.route('/')
def mainmenu():

    get_now()
    print  now_t + " ******************************"
    print "load main"
    read_db()
    save_pcfdb()
    get_now()

    response = """
    <html>
    <body bgcolor="{}">

    <center><h1><u><font color="white">Color Judge Results</u></h1>
    <br>
    <b>
    Red: {}<br>
    Green: {}<br>
    Blue: {}<br>
    <br>
    Unknown: {}<br></b>
    <br><br><br>
    Updated {}
    </center>
    </body>
    </html>
    """.format(COLOR,chk_count[0],chk_count[1],chk_count[2],chk_count[3],now_t)
    
    return response

if __name__ == "__main__":
	app.run(debug=False,host='0.0.0.0', port = '8080')
