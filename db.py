import sqlite3      #匯入sqlite3
cx = sqlite3.connect('./train.db')  #建立資料庫，如果資料庫已經存在，則連結資料庫；如果資料庫不存在，則先建立資料庫，再連結該資料庫。
cu = cx.cursor()           #定義一個遊標，以便獲得查詢物件。
cu.execute('create table if not exists train4 (Chinese text,English text)')  #建立表
fr = open('food.txt',encoding="utf-8")    #開啟要讀取的txt檔案
i = 0
for line in fr.readlines():    #將資料按行插入資料庫的表train4中。
    line2 = line.split('\t')
    print(line2[0])
    print(line2[1])
    cu.execute('insert into train4 (Chinese,English) values(?,?)',(line2[0],line2[1]))
    i=i+1

cu.close()   #關閉遊標
cx.commit()   #事務提交
cx.close()   #關閉資料庫