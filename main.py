from flask import Flask, render_template, request, redirect, url_for, session, abort
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import timedelta

import randomstring, os, sqlite3, hashlib, requests, datetime, random, ast, threading, traceback

app = Flask(__name__)

app.secret_key = randomstring.pick(20)

app.config["TEMPLATES_AUTO_RELOAD"] = True

name = "트론"

@app.template_filter('lenjago')
def lenjago(jago, txt):
    return len(jago.split(txt))

def db(name):
    return "./database/" + name + ".db"

def hash(string):
    return str(hashlib.sha512(("sexkingfingwwkj" + string + "14i!").encode()).hexdigest())

def js_location_href(link):
    return f'<script> location.href = "{link}" </script>'

def getip():
    return request.headers.get("CF-Connecting-IP", request.remote_addr)

def nowstr():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

def make_expiretime(days):
    ServerTime = datetime.datetime.now()
    ExpireTime = ServerTime + timedelta(days=days)
    ExpireTime_STR = (ServerTime + timedelta(days=days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

def get_expiretime(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        how_long = (ExpireTime - ServerTime)
        days = how_long.days
        hours = how_long.seconds // 3600
        minutes = how_long.seconds // 60 - hours * 60
        return str(round(days)) + "일 " + str(round(hours)) + "시간"
    else:
        return False

def is_expired(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        return False
    else:
        return True

def is_real_id(name, id, token):
    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE id == ?;", (id,))
    is_real_id = cur.fetchone()
    if is_real_id != None:
        if is_real_id[2] == token:
            return True
        else:
            return False
    else:
        return False

def login_check(name, id, pw):
    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE id == ?;", (id,))
    is_real_id = cur.fetchone()
    if is_real_id != None:
        if is_real_id[1] == hash(pw):
            return True
        else:
            return False
    else:
        return False

def get_token(name, id, pw):
    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE id == ?;", (id,))
    is_real_id = cur.fetchone()
    if is_real_id != None:
        if is_real_id[1] == hash(pw):
            return is_real_id[2]
        else:
            return False
    else:
        return False
        
def db_user_find(name, sex, sex2):
    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute(f"SELECT * FROM users WHERE {sex} == ?;", (sex2,))
    db_user_find = cur.fetchone()
    if db_user_find != None:
        return True
    else:
        return False

def is_admin(name, id):
    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE id == ?;", (id,))
    is_real_id = cur.fetchone()
    if is_real_id != None:
        if is_real_id[8] == 1:
            return True
        else:
            return False
    else:
        return False
        
def user_info_get(name, session):
    if ("id" in session):
        con = sqlite3.connect(db(name))
        cur = con.cursor()
        cur.execute(f"SELECT * FROM users WHERE id == ?;", (session['id'],))
        user_info = cur.fetchone()
        if user_info != None:
            return user_info
    return False

def server_info_get(name):
    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM info;")
    server_info = cur.fetchone()
    if server_info != None:
        return server_info
    else:
        return False

def add_time(now_days, add_days):
    ExpireTime = datetime.datetime.strptime(now_days, '%Y-%m-%d %H:%M')
    ExpireTime_STR = (ExpireTime + timedelta(days=add_days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

if not (os.path.isfile("./license.db")):
    con = sqlite3.connect("./license.db")
    cur = con.cursor()
    cur.execute("""CREATE TABLE "license" ("key" TEXT, "day" INTEGER, "is_used" INTEGER);""")
    con.commit()
    cur.execute("""CREATE TABLE "adm" ("ip" TEXT, "name" TEXT, "id" TEXT, "pw" TEXT);""")
    con.commit()
    con.close()

@app.route("/admin/create", methods=["GET", "POST"])
def shop_create():
    if (request.method == "GET"):
        return render_template("create.html")
    else:
        shop_name = request.form["shop_name"]
        adm_id = request.form["admin_id"]
        adm_pw = request.form["admin_pw"]
        key = request.form["key"]
        
        if shop_name == "" or shop_name == None or adm_id == "" or adm_id == None or adm_pw == "" or adm_pw == None or key == "" or key == None:
            return "모든 입력값을 입력해주세요!"

        if not (shop_name.isalpha()):
            return "샵 이름은 영어만 가능합니다!"

        con = sqlite3.connect("./license.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM license WHERE key == ?;", (key,))
        key_info = cur.fetchone()

        if key_info == None:
            return "존재하지 않는 라이센스입니다!"

        if key_info[2] == 1:
            return "이미 사용된 라이센스입니다!"

        license_day = key_info[1]

        if (shop_name.isalpha()):
            if not (os.path.isfile(f"./database/{shop_name}.db")):
                con = sqlite3.connect(f"./database/{shop_name}.db")
                cur = con.cursor()
                cur.execute("""CREATE TABLE "info" ("shop_name" INTEGER, "buy_log_webhook" TEXT, "cultureid" TEXT, "culturepw" TEXT, "culturecookie" TEXT, "charge_log" TEXT, "notice_img_link" TEXT, "culture_fees" INTEGER, "bankname" TEXT, "bank_acc_name" TEXT, "bankaddress" TEXT, "push_pins" TEXT, "music_url" TEXT, "channel_talk" TEXT);""")
                con.commit()
                cur.execute("CREATE TABLE users (id INTEGER, pw TEXT, name TEXT, token TEXT, role TEXT, money INTEGER, ip TEXT, buylog TEXT, isadmin INTEGER, warnings INTEGER, ban INTEGER, telegram TEXT);")
                con.commit()
                cur.execute("""CREATE TABLE "products" ("name" TEXT, "description" TEXT, "name_1" TEXT, "name_2" TEXT, "name_3" TEXT, "price_1" INTEGER, "price_2" INTEGER, "price_3" INTEGER, "product_img_url" TEXT, "stock_1" TEXT, "stock_2" TEXT, "stock_3" TEXT, "product_detail" TEXT, "item_id" TEXT, "category" TEXT, reseller_price_1 INTEGER, reseller_price_2 INTEGER, reseller_price_3 INTEGER, video TEXT);""")
                con.commit()
                cur.execute("""CREATE TABLE "account_charge" ("id" TEXT, "name" TEXT, "amount" INTEGER, "charge_date" TEXT);""")
                con.commit()
                cur.execute("""CREATE TABLE "coupon" ("code" TEXT, "amount" INTEGER);""")
                con.commit()
                cur.execute("""CREATE TABLE "user_buy_log" ("id" TEXT, "product_name" TEXT, "buy_code" TEXT, "amount" INTEGER);""")
                con.commit()
                cur.execute("""CREATE TABLE "user_charge_log" ("id" TEXT, "amount" INTEGER, "payment_method" TEXT, "approve" TEXT);""")
                con.commit()
                cur.execute("""CREATE TABLE "admin_log" ("charge_amount" INTEGER, "id" TEXT);""")
                con.commit()
                cur.execute("""CREATE TABLE "license" ("expire_day" TEXT, "license_day" INTEGER);""")
                con.commit()
                cur.execute("""CREATE TABLE "category" ("name" TEXT, "id" TEXT);""")
                con.commit()
                cur.execute("""CREATE TABLE "link" ("name" TEXT, "link" TEXT);""")
                con.commit()
                cur.execute("INSERT INTO info VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", ("", "", "", "", "", "[]", "", 0, "", "", "", "", "", ""))
                con.commit()
                cur.execute("INSERT INTO admin_log VALUES(?, ?);", (0, "sex"))
                con.commit()
                cur.execute("INSERT INTO license VALUES(?, ?);", (make_expiretime(license_day), 30))
                con.commit()
                cur.execute("INSERT INTO users Values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (adm_id, hash(adm_pw), "관리자", hash(randomstring.pick(15)), "관리자", 0, "관리자 아이피 비공개", "[]", 1, 0, 0, "JOR5555"))
                con.commit()
                con.close()

                con = sqlite3.connect("./license.db")
                cur = con.cursor()
                cur.execute("UPDATE license SET is_used = ? WHERE key == ?", (1, key))
                con.commit()
                con.close()

                return "success"
            else:
                return "이미 존재하는 스토어 이름입니다!"
        else:
            return "스토어 이름은 영어만 가능합니다!"

@app.route("/admin/code_gen", methods=["GET", "POST"])
def code_gen():
    if (request.method == "GET"):
        my_ip = getip()
        
        con = sqlite3.connect("./license.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM adm WHERE ip == ?;", (my_ip,))
        ip_info = cur.fetchone()

        if ip_info != None:
            if ("adm_id" in session):
                if session['adm_id'] == ip_info[2]:
                    return render_template("code_gen.html")
                else:
                    return f"<script> alert('Please Sign In!'); location.href='/admin/login'; </script>"
            else:
                    return f"<script> alert('Please Sign In!'); location.href='/admin/login'; </script>"
        else:
            return f"<script> alert('Unlock HWID Reset! Your IP : {my_ip}'); location.href='/'; </script>"
    else:
        if request.form["amount"] == None or request.form["amount"] == "" or request.form["days"] == None or request.form["days"] == "":
            return "모든 값을 채워주세요!"

        my_ip = getip()

        con = sqlite3.connect("./license.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM adm WHERE ip == ?;", (my_ip,))
        ip_info = cur.fetchone()

        if ("adm_id" in session):
            if session['adm_id'] != ip_info[2]:
                return "FUCK YOU!"
        
        con = sqlite3.connect("./license.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM adm WHERE ip == ?;", (my_ip,))
        ip_info = cur.fetchone()

        if ip_info != None:
            codes = []
            days = request.form["days"]

            nick_name = ip_info[1]

            for n in range(int(request.form["amount"])):
                generated = f"MoS-{days}-{randomstring.pick(30)}-{randomstring.pick(5)}-GenBy-{nick_name}"
                cur.execute("INSERT INTO license VALUES (?, ?, ?);", (generated, int(request.form["days"]), 0))
                con.commit()
                codes.append(generated)

            return "OK\n" + "\n".join(codes)
        else:
            return "FUCK YOU!"

@app.route("/admin/login", methods=["GET", "POST"])
def adm_login():
    if (request.method == "GET"):
        my_ip = getip()
        
        con = sqlite3.connect("./license.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM adm WHERE ip == ?;", (my_ip,))
        ip_info = cur.fetchone()
        print(ip_info)

        if ip_info != None:
            if not ("adm_id" in session):
                return render_template("admin_login.html")
            else:
                return f"<script> location.href='/code_gen'; </script>"
        else:
            return f"<script> alert('Unlock HWID Reset! Your IP : {my_ip}'); location.href='/'; </script>"
    else:
        my_ip = getip()
        
        con = sqlite3.connect("./license.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM adm WHERE ip == ?;", (my_ip,))
        ip_info = cur.fetchone()

        if ip_info != None:
            if not ("adm_id" in session):
                if ip_info[2] == request.form['id']:
                    if ip_info[3] == request.form['pw']:
                        session['adm_id'] = request.form['id']

                        return "success"
                    else:
                        return "아이디 또는 비밀번호가 일치하지 않습니다!"
                else:
                    return "아이디 또는 비밀번호가 일치하지 않습니다!"
            else:
                return "FUCK YOU!"
        else:
            return "FUCK YOU!"

@app.route("/", methods=["GET"])
def main():
    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM category;")
    categorys = cur.fetchall()

    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM link;")
    link_info = cur.fetchall()

    return render_template("index.html",link_info=link_info, shop_name=name, categorys=categorys, server_info=server_info_get(name), user_info=user_info_get(name, session))

@app.route("/buylog", methods=["GET"])
def buylog():
    if (name.isalpha()):
        if (os.path.isfile(db(name))):
            if ("id" in session):
                if is_real_id(name, session['id'], session['token']) == True:
                    user_id = session["id"]
                    logo = user_id[0:1]

                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute(f"SELECT * FROM user_buy_log ORDER BY log_date DESC")
                    buylogs_info = cur.fetchall()

                    return render_template("buy_log.html", shop_name=name, server_info=server_info_get(name), user_info=user_info_get(name, session), buylogs=buylogs_info)
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            abort(404)
    else:
        abort(404)

@app.route("/pw_change", methods=["GET"])
def pw_change():
    if (name.isalpha()):
        if (os.path.isfile(db(name))):
            if ("id" in session):
                if is_real_id(name, session['id'], session['token']) == True:
                    user_id = session["id"]
                    logo = user_id[0:1]

                    user_infos = user_info_get(name, session)

                    buylogs = ast.literal_eval(user_infos[7])

                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute("SELECT * FROM category;")
                    categorys = cur.fetchall()

                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute("SELECT * FROM link;")
                    link_info = cur.fetchall()

                    return render_template("password_change.html",link_info=link_info, categorys=categorys, shop_name=name, server_info=server_info_get(name), user_info=user_info_get(name, session), buylogs=reversed(sorted(buylogs)))
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            abort(404)
    else:
        abort(404)

@app.route("/my_buylog", methods=["GET"])
def my_buylog():
    if (name.isalpha()):
        if (os.path.isfile(db(name))):
            if ("id" in session):
                if is_real_id(name, session['id'], session['token']) == True:
                    user_id = session["id"]
                    logo = user_id[0:1]

                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute("SELECT * FROM category;")
                    categorys = cur.fetchall()

                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute(f"SELECT * FROM user_buy_log where id = '{user_id}' ORDER BY log_date DESC")
                    buylogs_info = cur.fetchall()

                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute("SELECT * FROM link;")
                    link_info = cur.fetchall()

                    return render_template("buylog.html", shop_name=name, categorys=categorys, server_info=server_info_get(name), user_info=user_info_get(name, session), buylogs=buylogs_info, link_info=link_info)
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            abort(404)
    else:
        abort(404)

@app.route("/change_pw", methods=["POST"])
def change_pw():
    if (name.isalpha()):
        if (os.path.isfile(db(name))):
            if ("id" in session):
                if is_real_id(name, session['id'], session['token']) == True:
                    before_pw = request.form["before_pw"]
                    after_pw = request.form["after_pw"]
                    after_pw_re = request.form["after_pw_re"]

                    if before_pw == "" or after_pw == "" or after_pw_re == "":
                        return "입력값을 모두 입력해주세요!"

                    if after_pw == after_pw_re:
                        if login_check(name, session["id"], before_pw) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("UPDATE users SET pw = ? WHERE id == ?", (hash(after_pw), session['id']))
                            con.commit()
                            
                            return "success"
                        else:
                            return "기존 비밀번호가 맞지 않습니다."
                    else:
                        return "변경할 비밀번호가 일치하지 않습니다."
                else:
                    return "FUCK YOU!"
            else:
                return "FUCK YOU!"
        else:
            return "FUCK YOU!"
    else:
        return "FUCK YOU!"

@app.route("/charge", methods=["GET"])
def charge():
    if (name.isalpha()):
        if (os.path.isfile(db(name))):
            if ("id" in session):
                if is_real_id(name, session['id'], session['token']) == True:
                    user_id = session["id"]
                    logo = user_id[0:1]

                    return render_template("charge.html", shop_name=name, server_info=server_info_get(name), user_info=user_info_get(name, session))
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            abort(404)
    else:
        abort(404)

@app.route("/buy", methods=["POST"])
def buy():
    if (name.isalpha()):
        if (os.path.isfile(db(name))):
            if ("id" in session):
                if is_real_id(name, session['id'], session['token']) == True:
                    amount = int(request.form["amount"])
                    option = request.form["option"]
                    product_id = request.form["product_id"]

                    if amount <= 0:
                        return "자판기 터는 새끼 나와!"
                    
                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute("SELECT * FROM products WHERE item_id == ?;", (product_id,))
                    item_info = list(cur.fetchone())

                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute("SELECT * FROM custom_price WHERE product_id == ? AND user_id == ?;", (product_id, session['id']))
                    custom_price = cur.fetchone()

                    if custom_price != None:
                        item_info[5] = custom_price[2]
                        item_info[6] = custom_price[3]
                        item_info[7] = custom_price[4]
                        item_info[15] = custom_price[2]
                        item_info[16] = custom_price[3]
                        item_info[17] = custom_price[4]

                    user_info = user_info_get(name, session)

                    if user_info[4] == "리셀러":
                        price = int(item_info[14 + int(option)]) * amount
                    else:
                        price = int(item_info[4 + int(option)]) * amount

                    if user_info[5] >= price:
                        if len(item_info[8 + int(option)].split("\n")) >= amount:
                            now_stock = item_info[8 + int(option)].split("\n")
                            bought_stock = []
                            for n in range(amount):
                                choiced_stock = random.choice(now_stock)
                                bought_stock.append(choiced_stock)
                                now_stock.remove(choiced_stock)

                            bought_stock = "\n".join(bought_stock)

                            now_buylog = ast.literal_eval(user_info[7])

                            option_b = item_info[int(option) + 1]

                            now_buylog.append([nowstr(), f"{item_info[0]} ( {option_b} )", bought_stock])
                            
                            current_datetime = datetime.datetime.now()
                            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")

                            cur.execute(f"UPDATE products SET stock_{option} = ? WHERE item_id == ?", ("\n".join(now_stock), product_id))
                            con.commit()
                            cur.execute("UPDATE users SET money = ?, buylog = ? WHERE id == ?", (int(user_info[5]) - price, str(now_buylog), session['id']))
                            con.commit()
                            cur.execute("INSERT INTO user_buy_log VALUES(?, ?, ?, ?, ?);", (session['id'], f"{item_info[0]} ( {option_b} )", bought_stock, amount, formatted_datetime))
                            con.commit()

                            server_info = server_info_get(name)

                            try:
                                webhook = DiscordWebhook(username="MOS TEAM.", url=server_info[1], avatar_url="https://media.discordapp.net/attachments/1000637877153169531/1001458136340762685/unknown.png")
                                embed = DiscordEmbed(title='MOS TEAM.', description=f'**`💸ㅣ구매로그`**\n\n`{session["id"][:2]}** 님이 {item_info[0]} ( {option_b} ) {amount}개 구매 감사합니다! 🎉`', color='03b2f8')
                                
                                if item_info[8] != "":
                                    embed.set_thumbnail(url=item_info[8])
                                    
                                embed.set_footer(text='MOS TEAM.')
                                webhook.add_embed(embed)
                                webhook.execute()
                            except:
                                pass

                            if user_info[4] == "비구매자":
                                cur.execute("UPDATE users SET role = ? WHERE id == ?", ("구매자", session['id']))
                                con.commit()

                            return "ok"
                        else:
                            return "재고가 부족합니다!"
                    else:
                        return "포인트가 부족합니다!"
                else:
                    return "FUCK YOU!"
            else:
                return "FUCK YOU!"
        else:
            return "FUCK YOU!"
    else:
        return "FUCK YOU!"

@app.route("/bank_charge", methods=["GET", "POST"])
def bank_charge():
    if (request.method == "GET"):
        con = sqlite3.connect(db(name))
        cur = con.cursor()
        cur.execute("SELECT * FROM category;")
        categorys = cur.fetchall()

        con = sqlite3.connect(db(name))
        cur = con.cursor()
        cur.execute("SELECT * FROM link;")
        link_info = cur.fetchall()

        return render_template("account_charge.html", link_info=link_info, categorys=categorys, shop_name=name, server_info=server_info_get(name), user_info=user_info_get(name, session))
    else:
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        bank_name = request.form["bank_name"]
                        amount = request.form["amount"]

                        if bank_name == "" or bank_name == None or amount == "" or amount == None:
                            return "입력값을 채워주세요!"

                        if int(amount) < 1000:
                            return "1,000원 이상부터 충전이 가능합니다!"

                        con = sqlite3.connect(db(name))
                        cur = con.cursor()
                        cur.execute("SELECT * FROM account_charge WHERE id == ?;", (session['id'],))
                        account_charge_info = cur.fetchone()

                        con = sqlite3.connect(db(name))
                        cur = con.cursor()
                        cur.execute("SELECT * FROM account_charge WHERE name == ?;", (bank_name,))
                        account_charge_info2 = cur.fetchone()

                        if account_charge_info2 != None:
                            return "이름이 중복된 충전이 있습니다!"

                        if account_charge_info == None:
                            cur.execute("INSERT INTO account_charge Values(?, ?, ?, ?);", (session['id'], bank_name, amount, make_expiretime(1)))
                            con.commit()
                            con.close()

                            name_id = session["id"]

                            server_info = server_info_get(name)
                            bankpin = server_info[11]

                            def waiting():
                                server_info = server_info_get(name)
                                bankpin = server_info[11]
                                print(bankpin)
                                jsondata = {
                                    "shop" : name, "userinfo": bank_name, "userid": name_id, "amount": int(amount)
                                }
                                result = requests.post("http://127.0.0.1:4040/api", json=jsondata)
                                print(jsondata)
                                if result.status_code != 200:
                                    raise Exception("계좌자충 에러")
                                result = result.json()

                                if result["result"] == False:
                                    con = sqlite3.connect(db(name))
                                    cur = con.cursor()
                                    cur.execute("DELETE FROM account_charge WHERE id == ?;", (name_id,))
                                    con.commit()
                                    con.close()

                                if result["result"] == True:
                                    con = sqlite3.connect(db(name))
                                    cur = con.cursor()
                                    cur.execute("DELETE FROM account_charge WHERE id == ?;", (name_id,))
                                    con.commit()
                                    cur.execute("UPDATE users SET money = money + ? WHERE id == ?;", (int(amount), name_id,))
                                    con.commit()
                                    con.close()

                            t1 = threading.Thread(target=waiting, args=())
                            t1.start()

                            return "ok"
                        else:
                            return "이미 충전중입니다!"
                    else:
                        return "FUCK YOU!"
                else:
                    return "FUCK YOU!"
            else:
                abort(404)
        else:
            abort(404)
            
@app.route("/item", methods=["GET"])
def item():
    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM products;")
    products = cur.fetchall()

    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM category;")
    categorys = cur.fetchall()

    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM link;")
    link_info = cur.fetchall()

    return render_template("item.html", link_info=link_info, shop_name=name, server_info=server_info_get(name), user_info=user_info_get(name, session), products=products, categorys=categorys)

@app.route("/item/<category_id>", methods=["GET"])
def item_category_id(category_id):
    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM category;")
    categorys = cur.fetchall()

    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM category WHERE id == ?;", (category_id,))
    category_i = cur.fetchone()

    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM products WHERE category == ?;", (category_i[1],))
    products = cur.fetchall()

    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM link;")
    link_info = cur.fetchall()

    return render_template("item.html", shop_name=name,link_info=link_info, server_info=server_info_get(name), user_info=user_info_get(name, session), products=products, categorys=categorys)

@app.route("/admin/admin_license", methods=["GET"])
def admin_license():
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM license;")
                            result = cur.fetchone()

                            license_expired_date = get_expiretime(result[0])

                            return render_template("admin_license.html", shop_name=name, license_expired_date=license_expired_date, expired_date=result[0])
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/admin_link_setting", methods=["GET"])
def admin_link_setting():
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM link;")
                            link = cur.fetchall()

                            return render_template("admin_link_setting.html", shop_name=name, link=link)
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/user_moonsang_zero/<user_id>", methods=["GET"])
def user_moonsang_zero(user_id):
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("UPDATE users SET warnings = ? WHERE id == ?;", (0, user_id))
                            con.commit()

                            return js_location_href(f"/admin/admin_user_setting_detail/{user_id}")

@app.route("/admin/product_stock_edit/<item_id>", methods=["GET"])
def product_stock_edit(item_id):
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM products WHERE item_id == ?;", (item_id,))
                            product_info = cur.fetchone()

                            return render_template("admin_stock_setting.html", shop_name=name, product_info=product_info)
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")
            
@app.route("/admin/admin_user_buy_log", methods=["GET"])
def admin_user_buy_log():
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM user_buy_log;")
                            user_buy_log = cur.fetchall()

                            return render_template("admin_user_buy_log.html", shop_name=name, buy_log=user_buy_log)
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/buy_log_search/<user_id>", methods=["GET"])
def buy_log_search(user_id):
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM user_buy_log WHERE id == ?;", (user_id,))
                            user_buy_log = cur.fetchall()

                            if user_buy_log == None:
                                is_exist == False
                            else:
                                is_exist = True

                            return render_template("admin_user_buy_log_search.html", shop_name=name, buy_log=user_buy_log, is_exist=is_exist)
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/product_stock_edit_save/<item_id>", methods=["POST"])
def product_stock_edit_save(item_id):
    if (request.method == "POST"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM products WHERE item_id == ?;", (item_id,))
                            product_info = cur.fetchone()

                            cur.execute("UPDATE products SET stock_1 = ?, stock_2 = ?, stock_3 = ? WHERE item_id == ?;", (request.form["stock_1"], request.form["stock_2"], request.form["stock_3"], item_id))
                            con.commit()

                            return "ok"
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/create_link", methods=["POST"])
def create_link():
    if (request.method == "POST"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            link_name = request.form["link_name"]

                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("INSERT INTO link VALUES(?, ?);", (link_name, ""))
                            con.commit()
                            con.close()

                            return "ok"
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/link_edit/<link>", methods=["GET"])
def link_edit(link):
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute(f"SELECT * FROM link WHERE name == ?;", (link,))
                            link_info = cur.fetchone()
                            con.close()

                            return render_template("admin_link_edit.html", shop_name=name, link_info=link_info)
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/link_remove/<link>", methods=["GET"])
def link_remove(link):
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("DELETE FROM link WHERE name == ?;", (link,))
                            con.commit()
                            con.close()

                            return js_location_href(f"/admin/admin_link_setting")
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/nobuyer_clear", methods=["GET"])
def nobuyer_clear():
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM users WHERE role == ?;", ("비구매자",))
                            users = cur.fetchall()

                            for user in users:
                                cur.execute("DELETE FROM users WHERE id == ?;", (user[0],))
                                con.commit()

                            con.close()

                            return js_location_href(f"/admin/admin_user_setting")
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/link_edit_save", methods=["POST"])
def link_edit_save():
    if (request.method == "POST"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("UPDATE link SET link = ? WHERE name == ?;", (request.form["link"], request.form["link_name"],))
                            con.commit()
                            con.close()

                            return "ok"
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/product_option_abled/<item_id>/<option>", methods=["POST"])
def product_option_abled(item_id, option):
    if (request.method == "POST"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute(f"UPDATE products SET name_{option} = ? WHERE item_id == ?;", ("", item_id))
                            con.commit()

                            return "ok"
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/product_option_disabled/<item_id>/<option>", methods=["POST"])
def product_option_disabled(item_id, option):
    if (request.method == "POST"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute(f"UPDATE products SET name_{option} = ? WHERE item_id == ?;", (None, item_id))
                            con.commit()

                            return "ok"
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/admin_charge_setting", methods=["GET", "POST"])
def admin_charge_setting():
    if (request.method == "POST"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM account_charge WHERE id == ?;", (request.form["user_id"],))
                            account_charge_info = cur.fetchone()

                            if request.form["approve"] == "True":
                                cur.execute("DELETE FROM account_charge WHERE id == ?;", (request.form["user_id"],))
                                con.commit()
                                cur.execute("UPDATE users SET money = money + ? WHERE id == ?;",(account_charge_info[2], request.form["user_id"]))
                                con.commit()
                            else:
                                cur.execute("DELETE FROM account_charge WHERE id == ?;", (request.form["user_id"],))
                                con.commit()

                            return "ok"
                        else:
                            return "FUCK YOU!"
                    else:
                        return "FUCK YOU!"
                else:
                    return "FUCK YOU!"
            else:
                return "FUCK YOU!"
        else:
            return "FUCK YOU!"
    else:
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM account_charge;")
                            charge_infos = cur.fetchall()

                            return render_template("admin_user_charge_setting.html", shop_name=name, charge_infos=charge_infos, is_search=False)
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")


@app.route("/admin/product_delete/<item_id>", methods=["POST"])
def product_delete(item_id):
    if (request.method == "POST"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM products WHERE item_id == ?;", (item_id,))
                            product_info = cur.fetchone()

                            cur.execute("DELETE FROM products WHERE item_id == ?;", (item_id,))
                            con.commit()

                            return "ok"
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/product_edit_save", methods=["POST"])
def product_edit_save():
    if (request.method == "POST"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM products WHERE name == ?;", (request.form["product_name"],))
                            product_info = cur.fetchone()

                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM category WHERE name == ?;", (request.form["product_setting_category"],))
                            product_setting_category_info = cur.fetchone()
                            
                            if product_setting_category_info == None:
                                return "존재하지 않는 카테고리!"

                            cur.execute("UPDATE products SET description = ?, product_detail = ? WHERE name == ?;", (request.form["product_description"], request.form["product_description_2"], request.form["product_name"]))
                            con.commit()
                            cur.execute("UPDATE products SET name_1 = ?, name_2 = ?, name_3 = ? WHERE name == ?;", (request.form["product_option_1_name"], request.form["product_option_2_name"], request.form["product_option_3_name"], request.form["product_name"]))
                            con.commit()
                            cur.execute("UPDATE products SET price_1 = ?, price_2 = ?, price_3 = ? WHERE name == ?;", (request.form["product_option_1_price"], request.form["product_option_2_price"], request.form["product_option_3_price"], request.form["product_name"]))
                            con.commit()
                            cur.execute("UPDATE products SET product_img_url = ? WHERE name == ?;", (request.form["product_image_url"], request.form["product_name"]))
                            con.commit()
                            cur.execute("UPDATE products SET category = ? WHERE name == ?;", (product_setting_category_info[1], request.form["product_name"]))
                            con.commit()

                            if request.form['product_option_1_name'] == "비활성화":
                                cur.execute("UPDATE products SET name_1 = ? WHERE name == ?;", (None, request.form["product_name"]))
                                con.commit()

                            if request.form['product_option_2_name'] == "비활성화":
                                cur.execute("UPDATE products SET name_2 = ? WHERE name == ?;", (None, request.form["product_name"]))
                                con.commit()

                            if request.form['product_option_3_name'] == "비활성화":
                                cur.execute("UPDATE products SET name_3 = ? WHERE name == ?;", (None, request.form["product_name"]))
                                con.commit()

                            product_setting_option_1_reseller_price = request.form["product_setting_option_1_reseller_price"]
                            product_setting_option_2_reseller_price = request.form["product_setting_option_2_reseller_price"]
                            product_setting_option_3_reseller_price = request.form["product_setting_option_3_reseller_price"]

                            cur.execute("UPDATE products SET reseller_price_1 = ? WHERE name == ?;", (product_setting_option_1_reseller_price, request.form["product_name"]))
                            con.commit()
                            cur.execute("UPDATE products SET reseller_price_2 = ? WHERE name == ?;", (product_setting_option_2_reseller_price, request.form["product_name"]))
                            con.commit()
                            cur.execute("UPDATE products SET reseller_price_3 = ? WHERE name == ?;", (product_setting_option_3_reseller_price, request.form["product_name"]))
                            con.commit()
                            cur.execute("UPDATE products SET video = ? WHERE name == ?;", (request.form["product_video_url"], request.form["product_name"]))
                            con.commit()
                            con.close()

                            return "ok"
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/category_setting", methods=["GET"])
def admin_category_setting():
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM category;")
                            category = cur.fetchall()

                            return render_template("admin_category_setting.html", shop_name=name, category=category)
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/create_category", methods=["POST"])
def create_category():
    if (request.method == "POST"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM category WHERE name == ?;", (request.form["category_name"],))
                            category = cur.fetchone()

                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT COUNT(*) FROM category;")
                            category_count = cur.fetchall()
                            if int(category_count[0][0]) >= 16:
                                return "카테고리는 15개까지만 생성이 가능합니다!"

                            if category == None:
                                cur.execute("INSERT INTO category VALUES(?, ?);", (request.form["category_name"], randomstring.pick(8)))
                                con.commit()
                                
                                return "ok"
                            else:
                                return "이미 존재하는 카테고리입니다."
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/category_remove/<category_name>", methods=["GET"])
def category_remove(category_name):
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM category WHERE id == ?;", (category_name,))
                            category = cur.fetchone()

                            if category != None:
                                cur.execute("DELETE FROM category WHERE name == ?;", (category[0],))
                                con.commit()
                                
                                return js_location_href(f"/admin/category_setting")
                            else:
                                return "존재하지 않는 카테고리입니다."
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")
            
@app.route("/admin/admin_product_setting", methods=["GET"])
def admin_product_setting():
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM products;")
                            product_info = cur.fetchall()

                            return render_template("admin_product_setting.html", shop_name=name, product_info=product_info, is_search=False)
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/product_search/<prod_name>", methods=["GET"])
def product_search(prod_name):
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM products WHERE name == ?;", (prod_name,))
                            product_info = cur.fetchone()

                            if product_info == None:
                                is_exist == False
                            else:
                                is_exist = True

                            return render_template("admin_product_setting.html", shop_name=name, product_info=product_info, is_search=True, is_exist=is_exist)
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/create_product", methods=["POST"])
def create_product():
    if (request.method == "POST"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()

                            product_name = request.form["product_name"]

                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM products WHERE name == ?;", (product_name,))
                            is_already_product = cur.fetchone()

                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT COUNT(*) FROM products;")
                            product_counts = cur.fetchall()
                            if int(product_counts[0][0]) >= 101:
                                return "제품은 100개까지만 생성이 가능합니다!"

                            if is_already_product == None:
                                cur.execute("INSERT INTO products VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (product_name, "설명", "옵션 1", "옵션 2", "옵션 3", 0, 0, 0, "", "", "", "", "", randomstring.pick(8), "", "", "", "", ""))
                                con.commit()

                                return "ok"
                            else:
                                return "이미 존재하는 제품명!"
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/create_price/<prd_id>", methods=["POST"])
def create_price(prd_id):
    if (request.method == "POST"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()

                            user_id = request.form["user_id"]

                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM custom_price WHERE product_id == ? AND user_id == ?;", (prd_id, user_id))
                            is_already_product = cur.fetchone()

                            if is_already_product == None:
                                cur.execute("INSERT INTO custom_price VALUES(?, ?, ?, ?, ?);", (prd_id, user_id, 0, 0, 0))
                                con.commit()

                                return "ok"
                            else:
                                return "이미 존재합니다!"
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/remove_price/<prd_id>/<user_id>", methods=["POST"])
def remove_price(prd_id, user_id):
    if (request.method == "POST"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        con = sqlite3.connect(db(name))
                        cur = con.cursor()
                        cur.execute("SELECT * FROM custom_price WHERE product_id == ? AND user_id == ?;", (prd_id, user_id))
                        is_already_product = cur.fetchone()

                        if is_already_product != None:
                            cur.execute("DELETE FROM custom_price WHERE product_id == ? AND user_id == ?;", (prd_id, user_id))
                            con.commit()

                            return "ok"
                        else:
                            return "존재하지 않습니다!"
    return js_location_href(f"/login")

@app.route("/admin/edit_price/<prd_id>/<user_id>", methods=["POST"])
def edit_price(prd_id, user_id):
    if (request.method == "POST"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()

                            price_1 = request.form["price_1"]
                            price_2 = request.form["price_2"]
                            price_3 = request.form["price_3"]

                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM custom_price WHERE product_id == ? AND user_id == ?;", (prd_id, user_id))
                            
                            if cur.fetchone() == None:
                                return "존재하지 않습니다!"
                            
                            cur.execute("UPDATE custom_price SET price_1 = ?, price_2 = ?, price_3 = ? WHERE product_id == ? AND user_id == ?;", (price_1, price_2, price_3, prd_id, user_id))
                            con.commit()
                            
                            return "ok";
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/product_edit/<prd_id>", methods=["GET"])
def product_edit(prd_id):
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM products WHERE item_id == ?;", (prd_id,))
                            product_info = cur.fetchone()

                            if product_info == None:
                                is_exist = False
                            else:
                                is_exist = True

                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM custom_price WHERE product_id == ?;", (prd_id,))
                            custom_price = cur.fetchall()

                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM category WHERE id == ?;", (product_info[14],))
                            product_setting_category_info = cur.fetchone()

                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM category;")
                            product_setting_category_infos = cur.fetchall()

                            if product_setting_category_info == None:
                                product_setting_category = ""
                            else:
                                product_setting_category = product_setting_category_info[0]

                            return render_template("admin_product_setting_detail.html", product_setting_category_infos=product_setting_category_infos, shop_name=name, product_info=product_info, custom_price=custom_price, is_search=True, is_exist=is_exist, category_name=product_setting_category)
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                return js_location_href(f"/login")
        else:
            return js_location_href(f"/login")

@app.route("/admin/admin_home", methods=["GET"])
def admin_home():
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM admin_log WHERE id == ?;", ("sex",))
                            user_charge_amount = cur.fetchone()

                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute('SELECT * FROM users WHERE role="구매자";')
                            buyer = cur.fetchall()

                            buyer_count = 0

                            for i in buyer:
                                buyer_count += 1

                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT COUNT(*) FROM users;")
                            user = cur.fetchall()

                            user_count = user[0][0]

                            buy_percent = round((buyer_count / user_count) * 100)

                            return render_template("admin_home.html", shop_name=name, user_charge_amount=user_charge_amount[0], buyer_count=buyer_count, user_count=user_count, buy_percent=buy_percent)
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                abort(404)
        else:
            abort(404)

@app.route("/admin/admin_user_setting", methods=["GET"])
def admin_user_setting():
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM users;")
                            users = cur.fetchall()

                            return render_template("admin_user_setting.html", shop_name=name, shop_info=server_info_get(name), users=users, is_search=False)
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                abort(404)
        else:
            abort(404)

@app.route("/admin/admin_user_setting_serach/<user_id>", methods=["GET"])
def admin_user_setting_search(user_id):
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM users WHERE id == ?;", (user_id,))
                            users = cur.fetchone()

                            if users == None:
                                is_exist = False
                            else:
                                is_exist = True

                            return render_template("admin_user_setting.html", shop_name=name, shop_info=server_info_get(name), users=users, is_search=True, is_exist=is_exist)
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                abort(404)
        else:
            abort(404)

@app.route("/admin/admin_user_setting_detail/<user_id>", methods=["GET"])
def admin_user_setting_detail(user_id):
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM users WHERE id == ?;", (user_id,))
                            users = cur.fetchone()

                            if users == None:
                                is_exist = False
                            else:
                                is_exist = True

                            return render_template("admin_user_setting_detail.html", shop_name=name, shop_info=server_info_get(name), users=users, is_exist=is_exist)
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                abort(404)
        else:
            abort(404)

@app.route("/admin/license_key_confirm", methods=["POST"])
def license_key_confirm():
    if (name.isalpha()):
        if (os.path.isfile(db(name))):
            if ("id" in session):
                if is_real_id(name, session['id'], session['token']) == True:
                    if is_admin(name, session['id']) == True:
                        license_key = request.form["license_key"]

                        if license_key == None or license_key == "":
                            return "라이센스 코드를 입력해주세요!"

                        con = sqlite3.connect("./license.db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM license WHERE key == ?;", (license_key,))
                        key_info = cur.fetchone()
                        con.close()

                        if key_info == None:
                            return "존재하지 않는 라이센스입니다!"

                        if key_info[2] == 1:
                            return "이미 사용된 라이센스입니다!"

                        license_day = key_info[1]

                        con = sqlite3.connect(db(name))
                        cur = con.cursor()
                        cur.execute("SELECT * FROM license;")
                        license_info = cur.fetchone()

                        expired_date = add_time(license_info[0], int(license_day))

                        cur.execute("UPDATE license SET expire_day = ? WHERE license_day == ?", (expired_date, 30))
                        con.commit()

                        con = sqlite3.connect("./license.db")
                        cur = con.cursor()
                        cur.execute("UPDATE license SET is_used = ? WHERE key == ?", (1, license_key))
                        con.commit()
                        con.close()

                        return f"OK {str(license_day)}일 연장 완료!"

@app.route("/admin/admin_user_setting_detail_save", methods=["POST"])
def admin_user_setting_detail_save():
    if (name.isalpha()):
        if (os.path.isfile(db(name))):
            if ("id" in session):
                if is_real_id(name, session['id'], session['token']) == True:
                    if is_admin(name, session['id']) == True:
                        userid = request.form["user_id"]
                        user_money = request.form["user_money"]
                        is_ban = request.form["is_ban"]
                        is_reseller = request.form["is_reseller"]

                        if userid == None or userid == "" or user_money == None or user_money == "" or is_ban == None or is_ban == "":
                            return "모든 값을 채워주세요!"

                        if is_ban == "True" or is_ban == True:
                            is_ban = 1
                        elif is_ban == "False" or is_ban == False:
                            is_ban = 0

                        if is_reseller == "true":
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("UPDATE users SET role = ? WHERE id == ?;", ("리셀러", userid))
                            con.commit()
                        else:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM users WHERE id == ?;", (userid,))
                            user_info = cur.fetchone()

                            if user_info[8] == 1:
                                con = sqlite3.connect(db(name))
                                cur = con.cursor()
                                cur.execute("UPDATE users SET role = ? WHERE id == ?;", ("관리자", userid))
                                con.commit()
                            else:
                                con = sqlite3.connect(db(name))
                                cur = con.cursor()
                                cur.execute("UPDATE users SET role = ? WHERE id == ?;", ("비구매자", userid))
                                con.commit()

                        con = sqlite3.connect(db(name))
                        cur = con.cursor()
                        cur.execute("SELECT * FROM users WHERE id == ?;", (userid,))
                        user_info = cur.fetchone()

                        cur.execute("UPDATE users SET money = ?, ban = ? WHERE id == ?;", (user_money, is_ban, userid))
                        con.commit()

                        return "ok"
                    else:
                        return "FUCK YOU!"
                else:
                    return "FUCK YOU!"
            else:
                return "FUCK YOU!"
        else:
            return "FUCK YOU!"
    else:
        return "FUCK YOU!"

@app.route("/admin/admin_general", methods=["GET", "POST"])
def admin_general():
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if is_admin(name, session['id']) == True:
                            return render_template("admin_general.html", shop_name=name, server_info=server_info_get(name))
                        else:
                            return js_location_href(f"/login")
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                abort(404)
        else:
            abort(404)
    else:
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        buy_log_webhook_url = request.form["buy_log_webhook_url"]
                        store_music = request.form["store_music"]
                        ct_cookie = request.form["ct_cookie"]
                        ct_id = request.form["ct_id"]
                        ct_pw = request.form["ct_pw"]
                        ct_fees = request.form["ct_fees"]
                        bank_number = request.form["bank_number"]
                        bank_charge_key = request.form["bank_charge_key"]
                        notice_img_url =request.form["notice_img_url"]
                        channeltalk_plugin = request.form["channeltalk_plugin"]

                        con = sqlite3.connect(db(name))
                        cur = con.cursor()
                        cur.execute("SELECT * FROM info;")
                        shop_info = cur.fetchone()

                        cur.execute("UPDATE info SET cultureid = ?, culturepw = ?, culturecookie = ?, music_url = ?, culture_fees = ?", (ct_id, ct_pw, ct_cookie, store_music, int(ct_fees)))
                        con.commit()
                        cur.execute("UPDATE info SET bankaddress = ?, push_pins = ?, notice_img_link = ?, buy_log_webhook = ?", (bank_number, bank_charge_key, notice_img_url, buy_log_webhook_url))
                        con.commit()
                        cur.execute("UPDATE info SET channel_talk = ?", (channeltalk_plugin,))
                        con.commit()

                        return "ok"
                    else:
                        return "FUCK YOU!"
                else:
                    return "FUCK YOU!"
            else:
                return "FUCK YOU!"
        else:
            return "FUCK YOU!"


@app.route("/buy/<item_id>", methods=["GET"])
def item_buy(item_id):
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        user_id = session["id"]
                        logo = user_id[0:1]

                        con = sqlite3.connect(db(name))
                        cur = con.cursor()
                        cur.execute("SELECT * FROM products WHERE item_id == ?;", (item_id,))
                        product = list(cur.fetchone())

                        con = sqlite3.connect(db(name))
                        cur = con.cursor()
                        cur.execute("SELECT * FROM custom_price WHERE product_id == ? AND user_id == ?;", (item_id, user_id))
                        custom_price = cur.fetchone()

                        if custom_price != None:
                            product[5] = custom_price[2]
                            product[6] = custom_price[3]
                            product[7] = custom_price[4]
                            product[15] = custom_price[2]
                            product[16] = custom_price[3]
                            product[17] = custom_price[4]

                        con = sqlite3.connect(db(name))
                        cur = con.cursor()
                        cur.execute("SELECT * FROM category;")
                        categorys = cur.fetchall()

                        con = sqlite3.connect(db(name))
                        cur = con.cursor()
                        cur.execute("SELECT * FROM link;")
                        link_info = cur.fetchall()

                        return render_template("item_detail.html", link_info=link_info, categorys=categorys, shop_name=name, server_info=server_info_get(name), user_info=user_info_get(name, session), product=product)
                    else:
                        return js_location_href(f"/login")
                else:
                    return js_location_href(f"/login")
            else:
                abort(404)
        else:
            abort(404)

@app.route("/culture_charge", methods=["GET", "POST"])
def culture_charge():
    if (request.method == "GET"):
        con = sqlite3.connect(db(name))
        cur = con.cursor()
        cur.execute("SELECT * FROM category;")
        categorys = cur.fetchall()

        con = sqlite3.connect(db(name))
        cur = con.cursor()
        cur.execute("SELECT * FROM link;")
        link_info = cur.fetchall()

        return render_template("cultureland_charge.html", link_info=link_info, categorys=categorys, shop_name=name, server_info=server_info_get(name), user_info=user_info_get(name, session))
    else:
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if ("id" in session):
                    if is_real_id(name, session['id'], session['token']) == True:
                        if request.form['pin'] == "" or request.form['pin'] == None:
                            return "핀번호를 입력해주세요!"

                        user_info = user_info_get(name, session)
                        if user_info[9] >= 3:
                            return "3회 이상 충전실패로 인한 충전실패"
                    
                        pin = request.form['pin']

                        con = sqlite3.connect(db(name))
                        cur = con.cursor()
                        cur.execute("SELECT * FROM info;")
                        server_info = cur.fetchone()
                        choi_res = requests.post("https://choiticket.com/skin/SKIN_ORDER/01/ajax.pin.chk.php", data={
                            "sort": "cul",
                            "pin": pin
                        }, headers={
                            "x-requested-with": "XMLHttpRequest"
                        }).json()
                        if( not choi_res["ERROR"] == "0000" ):
                            cur.execute("UPDATE users SET warnings = ? WHERE id == ?;", (user_info[9] + 1, session['id']))
                            con.commit()
                            return "충전실패 ( 상품권 번호 불일치 ) 경고 1회 추가"

                        try:
                            jsondata = {"token": "9INAtVVtp2WcTSvI0wGG", "id": server_info[2], 'pw': server_info[3], "cookie": server_info[4], "pin": pin}
                            res = requests.post("http://127.0.0.1:123/api", json=jsondata)
                            if (res.status_code != 200):
                                raise TypeError
                            else:
                                res = res.json()
                        except:
                            return "서버 에러가 발생했습니다."

                        con = sqlite3.connect(db(name))
                        cur = con.cursor()

                        if (res["success"] == True):
                            amount = int((int(res["amount"] )/ 100) * (100 - int(server_info[7])))

                            cur.execute("UPDATE users SET money = ? WHERE id == ?;", (user_info[5] + int(amount), session['id']))
                            con.commit()

                            cur.execute("UPDATE admin_log SET charge_amount = charge_amount + ? WHERE id == ?;", (int(amount), "sex"))
                            con.commit()

                            now_chargelog = ast.literal_eval(server_info[5])
                            now_chargelog.append([nowstr(), session['id'], "문화상품권", str(amount)])

                            cur.execute("UPDATE info SET charge_log = ? WHERE shop_name == ?;", (str(now_chargelog), ""))
                            con.commit()

                            return "charge_success|" + str(amount)

                        elif (res["success"] == False):
                            cur.execute("UPDATE users SET warnings = ? WHERE id == ?;", (user_info[9] + 1, session['id']))
                            con.commit()

                            return res["result"] + " 경고 1회 추가"
                    else:
                        return "FUCK YOU!"
                else:
                    return "FUCK YOU!"
            else:
                abort(404)
        else:
            abort(404)

@app.route("/login", methods=["GET", "POST"])
def login():
    if (request.method == "GET"):
        abort(404)
    else:
        if not ("id" in session):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute("SELECT * FROM license;")
                    result = cur.fetchone()

                    if is_expired(result[0]):
                        return "expired_license"

                    id = request.form['id']
                    pw = request.form['pw']

                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute("SELECT * FROM users WHERE id == ?;", (id,))
                    users = cur.fetchone()

                    if users == None:
                        return "login_fail"

                    if users[9] == 1:
                        return "ban_user"

                    if login_check(name, id, pw) == True:

                        session['id'] = id
                        session['token'] = get_token(name, id, pw)


                        return "login_success"

                    else:
                        return "login_fail"
        else:
            return "login_already"

@app.route("/register", methods=["GET", "POST"])
def register():
    if (request.method == "GET"):
        abort(404)
    else:
        try:
            if not ("id" in session):
                if (name.isalpha()):
                    if (os.path.isfile(db(name))):
                        con = sqlite3.connect(db(name))
                        cur = con.cursor()
                        cur.execute("SELECT * FROM license;")
                        result = cur.fetchone()

                        if is_expired(result[0]):
                            return "자판기 라이센스가 만료되었습니다. 관리자한테 문의해주세요!"
                        print(request.data)
                        id = request.form.get('id')
                        uname = request.form.get('name')
                        pw = hash(request.form.get('pw'))
                        re_pw = hash(request.form['re_pw'])
                        telegram = request.form['telegram']

                        if id == "" or uname == "" or pw == "" or re_pw == "" or telegram == "":
                            return "모든 값을 채워주세요!"

                        if telegram[0] != "@":
                            return "텔레그램 아이디는 @로 시작해야합니다!"

                        if db_user_find(name, "ip", getip()) != True:
                            if db_user_find(name, "id", id) != True:
                                if pw == re_pw:
                                    if telegram == None or telegram == "":
                                        telegram = ""

                                    token = hash(randomstring.pick(15))

                                    con = sqlite3.connect(f"./database/{name}.db")
                                    cur = con.cursor()
                                    cur.execute("INSERT INTO users Values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (id, pw, uname, token, "비구매자", 0, getip(), "[]", 0, 0, 0, telegram))
                                    con.commit()
                                    con.close()
                                    
                                    session['id'] = id
                                    session['token'] = token

                                    return "register_success"
                                else:
                                    return "비밀번호가 일치하지 않습니다!"
                            else:
                                return "이미 존재하는 아이디입니다!"
                        else:
                            return "한 아이피당 한번만 가입이 가능합니다!"
            else:
                return "다른 자판기에 접속중이거나 이미 로그인된 상태입니다!"
        except:
            traceback.print_exc()

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/")

@app.route("/admin/logout", methods=["GET"])
def logout_2():
    session.clear()
    return js_location_href("/admin/login")

@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
