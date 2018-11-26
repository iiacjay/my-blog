from django.shortcuts import render
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
import MySQLdb
import sys
import random

lotto_list = []

#main_url = "https://www.nlotto.co.kr/lotto645Confirm.do?method=byWin"
main_url = "http://www.nlotto.co.kr/gameResult.do?method=byWin"

# 각 회차별 당첨정보를 알 수 있는 주소
#basic_url = "https://www.nlotto.co.kr/lotto645Confirm.do?method=byWin&drwNo="
basic_url = "http://www.nlotto.co.kr/gameResult.do?method=byWin&drwNo="



def getLast():
    resp = requests.get(main_url)
    soup = BeautifulSoup(resp.text, "lxml")
    line = str(soup.find("meta", {"id": "desc", "name": "description"})['content'])

    begin = line.find(" ")
    end = line.find("회")

    if begin == -1 or end == -1:
        print("not found last lotto number")
        exit()

    return int(line[begin + 1: end])


def checkLast():
    db = MySQLdb.connect(host="localhost", user="admin", passwd="1234", db="lotto")
    cursor = db.cursor()

    sql = "SELECT MAX(count) FROM lotto"
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
    except:
        print(sys.exc_info()[0])

    cursor.close()
    db.close()

    return result[0]


def crawler(fromPos, toPos):
    for i in range(fromPos + 1, toPos + 1):
        crawler_url = basic_url + str(i)
        print("crawler: " + crawler_url)

        resp = requests.get(crawler_url)
        soup = BeautifulSoup(resp.text, "lxml")
        line = str(soup.find("meta", {"id": "desc", "name": "description"})['content'])

        begin = line.find("당첨번호")
        begin = line.find(" ", begin) + 1
        end = line.find(".", begin)
        numbers = line[begin:end]

        begin = line.find("총")
        begin = line.find(" ", begin) + 1
        end = line.find("명", begin)
        persons = line[begin:end]

        begin = line.find("당첨금액")
        begin = line.find(" ", begin) + 1
        end = line.find("원", begin)
        amount = line[begin:end]

        info = {}
        info["회차"] = i
        info["번호"] = numbers
        info["당첨자"] = persons
        info["금액"] = amount

        lotto_list.append(info)


def insert():
    db = MySQLdb.connect(host="localhost", user="admin", passwd="1234", db="lotto")
    cursor = db.cursor()

    for dic in lotto_list:
        count = dic["회차"]
        numbers = dic["번호"]
        persons = dic["당첨자"]
        amounts = dic["금액"]

        print("insert into database at " + str(count))

        numberlist = str(numbers).split(",")

        sql = "INSERT INTO `lotto`. `lotto`(`count`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `persion`, `amount`) " \
              "VALUES('%d', '%d', '%d', '%d', '%d', '%d', '%d', '%d', '%d', '%s')" \
              % (count,
                 int(numberlist[0]),
                 int(numberlist[1]),
                 int(numberlist[2]),
                 int(numberlist[3]),
                 int(numberlist[4]),
                 int(numberlist[5].split("+")[0]),
                 int(numberlist[5].split("+")[1]),
                 int(persons),
                 str(amounts))

        try:
            cursor.execute(sql)
            db.commit()
        except:
            print(sys.exc_info()[0])
            db.rollback()
            break

    cursor.close()
    db.close()


def analysis():
    db = MySQLdb.connect(host="localhost", user="admin", passwd="1234", db="lotto")
    cursor = db.cursor()

    for i in range(1, 8):

        sql = "select `"
        sql += str(i)
        sql += "` from lotto"

        try:
            cursor.execute(sql)
            results = cursor.fetchall()

            # 해당 숫자의 뽑힌 횟수를 하나씩 증가
            myarray = [0 for i in range(46)]

            for row in results:
                k = row[0]
                count = myarray[k]
                myarray[k] = count + 1

            maxvalue = myarray.index(max(myarray))
            #print(i, maxvalue)


        except:
            print(sys.exc_info()[0])

    cursor.close()
    db.close()


def getdb(last, i):
    db = MySQLdb.connect(host="localhost", user="admin", passwd="1234", db="lotto")
    cursor = db.cursor()
    retval = 0
    number = random.randint(1, last)
    number2 = random.randint(1, 6)
    # print("number is =", number)

    sql = "SELECT `"
    # sql += str(i)
    sql += str(number2)
    sql += "` FROM lotto "
    sql += "WHERE count = "
    sql += str(number)

    try:
        cursor.execute(sql)
        results = cursor.fetchone()
        retval = results[0]
        # print("retval is =", retval)
    except:
        print(sys.exc_info()[0])
    cursor.close()
    db.close()

    return retval


def pick(last):
    results2 = [0 for j in range(6)]
    i = 0
    flag = 0
    count = 0
    while (1):
        if i == 0:
            results2[i] = getdb(last, i + 1)
            i = i + 1
            count = count + 1
        else:
            results2[i] = getdb(last, i + 1)
            for j in range(0, count):
                if results2[i] == results2[j]:
                    # print("same value")
                    results2[i] = getdb(last, i + 1)
                    continue
            i = i + 1
            count = count + 1
        if i == 6:
            break
    results2.sort()
    print("예상 번호는 ", results2, " 입니다.")


def getdb_100(start, last, i):
    db = MySQLdb.connect(host="localhost", user="admin", passwd="1234", db="lotto")
    cursor = db.cursor()
    retval = 0
    number = random.randint(start, last)
    number2 = random.randint(1, 6)
    # print("number is =", number)

    sql = "SELECT `"
    # sql += str(i)
    sql += str(number2)
    sql += "` FROM lotto "
    sql += "WHERE count = "
    sql += str(number)

    try:
        cursor.execute(sql)
        results = cursor.fetchone()
        retval = results[0]
        # print("retval is =", retval)
    except:
        print(sys.exc_info()[0])
    cursor.close()
    db.close()

    return retval


def pick_top100(start, last):
    results2 = [0 for j in range(6)]
    lotto_num = []
    i = 0
    flag = 0
    count = 0
    while (1):
        if i == 0:
            results2[i] = getdb_100(start, last, i + 1)
            i = i + 1
            count = count + 1
        else:
            results2[i] = getdb_100(start, last, i + 1)
            for j in range(0, count):
                if results2[i] == results2[j]:
                    # print("same value")
                    results2[i] = getdb_100(start, last, i + 1)
                    continue

            i = i + 1
            count = count + 1
        if i == 6:
            break
    results2.sort()
    lotto_num.append(results2)
    print(lotto_num)
    return lotto_num
    #print("예상 번호는 ", results2, " 입니다.")

# Create your views here.
def index(request):

    last = getLast()
    dblast = checkLast()
    lotto_temp=[]

    if dblast is None:
        dblast = 0

    if dblast < last:
        print("최신 회차는 " + str(last) + " 회 이며, 데이터베이스에는 " + str(dblast) + "회 까지 저장되어 있습니다.")
        print("업데이트를 시작합니다.")
        crawler(dblast, last)
    if dblast >= last:
        print("DB가 최신입니다.")

    insert()
    print("당첨 번호를 분석중입니다...")
    analysis()
    print("예상 번호를 추출 중입니다...")

    #    for i in range(0, 5):
    #        pick(last)



    start = last - 100

    for i in range(0, 5):
        lotto_temp.append(pick_top100(start, last))

    return render(request, 'mylotto/mypage.html', {'welcome_text': lotto_temp})

    #return HttpResponse(lotto_num)


"""
    def main():
        print("DB 정보를 확인 중입니다.")
        last = getLast()
        dblast = checkLast()

        if dblast is None:
            dblast = 0

        if dblast < last:
            print("최신 회차는 " + str(last) + " 회 이며, 데이터베이스에는 " + str(dblast) + "회 까지 저장되어 있습니다.")
            print("업데이트를 시작합니다.")
            crawler(dblast, last)
        if dblast >= last:
            print("DB가 최신입니다.")

        insert()
        print("당첨 번호를 분석중입니다...")
        analysis()
        print("예상 번호를 추출 중입니다...")

        #    for i in range(0, 5):
        #        pick(last)



        start = last - 100

        for i in range(0, 5):
            pick_top100(start, last)

    if __name__ == "__main__":
        main()
"""

