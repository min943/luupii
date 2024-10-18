import datetime, sqlite3, os

from datetime import timedelta

def add_time(now_days, add_days):
    ExpireTime = datetime.datetime.strptime(now_days, '%Y-%m-%d %H:%M')
    ExpireTime_STR = (ExpireTime + timedelta(days=add_days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

shop_name = input("연장할 샵 이름을 입력해주세요!")
add_time_amount = input("연장할 기간을 입력해주세요!")

if (os.path.isfile(f"./database/{shop_name}.db")):
    con = sqlite3.connect(f"./database/{shop_name}.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM license;")
    license_info = cur.fetchone()

    expired_date = add_time(license_info[0], int(add_time_amount))

    print(f"연장된 만료 일자 : {expired_date}")

    cur.execute("UPDATE license SET expire_day = ? WHERE license_day == ?", (expired_date, 30))
    con.commit()
else:
    print("존재하지 않는 샵입니다.")