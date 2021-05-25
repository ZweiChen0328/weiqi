#!/usr/bin/python3
# 使用Python内建GUI模組tkinter
from tkinter import *
# ttk覆寫tkinter部分物件，ttk對tkinter進行了優化
from tkinter.ttk import *
# deepcopy需要用到copy模組
import copy
import tkinter.messagebox

# 围棋應用物件定義
class model(Tk):
    def __init__(self, my_mode_num=19):
        Tk.__init__(self)
        # 模式，九路棋：9，十三路棋：13，十九路棋：19
        self.mode_num = my_mode_num
        # 棋盤尺寸設置基準值，預設：1.6
        self.size = 1.6
        # 棋盤每格的邊長
        self.dd = 360 * self.size / (self.mode_num - 1)
        # 相對於九路棋盤的校正比例
        self.p = 1 if self.mode_num == 9 else (2 / 3 if self.mode_num == 13 else 4 / 9)
        # 定義棋盤陣列,超過邊界：-1，無子：0，黑棋：1，白棋：2
        self.positions = [[0 for i in range(self.mode_num + 2)] for i in range(self.mode_num + 2)]
        # 初始化棋盤，所有超過邊界的值設為-1
        for m in range(self.mode_num + 2):
            for n in range(self.mode_num + 2):
                if m * n == 0 or m == self.mode_num + 1 or n == self.mode_num + 1:
                    self.positions[m][n] = -1
        # 拷貝三份棋盤“快照”，悔棋和判斷“打劫”時需要参考
        self.last_3_positions = copy.deepcopy(self.positions)
        self.last_2_positions = copy.deepcopy(self.positions)
        self.last_1_positions = copy.deepcopy(self.positions)
        # 紀錄每一手的落子點，作為棋譜紀錄
        self.record = []
        self.record_take = []
        # 記錄滑鼠經過的地方，用於顯示打算落子的棋子shadow
        self.cross_last = None
        # 當前輪到的玩家，黑：0，白：1，執黑先行
        self.present = 0
        # 初始時停止運行，點擊“開始對局”才開始運行
        self.stop = True
        # 悔棋次数，次数大於0才可悔棋，初始設為0（初始不能悔棋），悔棋後重置0，下棋或虛手pass時恢復為1，以禁止連續悔棋
        # 圖片來源，存放在當前目錄下的/Pictures/中
        self.photoW = PhotoImage(file="./Pictures/W.png")
        self.photoB = PhotoImage(file="./Pictures/B.png")
        self.photoBD = PhotoImage(file="./Pictures/" + "BD" + "-" + str(self.mode_num) + ".png")
        self.photoWD = PhotoImage(file="./Pictures/" + "WD" + "-" + str(self.mode_num) + ".png")
        self.photoBU = PhotoImage(file="./Pictures/" + "BU" + "-" + str(self.mode_num) + ".png")
        self.photoWU = PhotoImage(file="./Pictures/" + "WU" + "-" + str(self.mode_num) + ".png")
        # 用於黑白棋子圖片切换的列表
        self.photoWBU_list = [self.photoBU, self.photoWU]
        self.photoWBD_list = [self.photoBD, self.photoWD]
        # 視窗大小
        self.geometry(str(int(600 * self.size)) + 'x' + str(int(400 * self.size)))
        # 畫布控制物件，作爲容器
        self.canvas_bottom = Canvas(self, bg='#369', bd=0, width=600 * self.size, height=400 * self.size)
        self.canvas_bottom.place(x=0, y=0)
        # 畫棋盤，填充顏色
        self.canvas_bottom.create_rectangle(0 * self.size, 0 * self.size, 400 * self.size, 400 * self.size,
                                            fill='#FFD700')
        # 刻畫棋盤線及九個點
        # 先畫外框粗線
        self.canvas_bottom.create_rectangle(20 * self.size, 20 * self.size, 380 * self.size, 380 * self.size, width=3)
        # 棋盤上的九個定位點，以中點為模型，移動位置以作出其餘八個點
        for m in ([-1, 1] if self.mode_num == 9 else ([-1, 1] if self.mode_num == 13 else [-1, 0, 1])):
            for n in ([-1, 1] if self.mode_num == 9 else ([-1, 1] if self.mode_num == 13 else [-1, 0, 1])):
                self.oringinal = self.canvas_bottom.create_oval(200 * self.size - self.size * 2,
                                                                200 * self.size - self.size * 2,
                                                                200 * self.size + self.size * 2,
                                                                200 * self.size + self.size * 2, fill='#000')
                self.canvas_bottom.move(self.oringinal,
                                        m * self.dd * (2 if self.mode_num == 9 else (3 if self.mode_num == 13 else 6)),
                                        n * self.dd * (2 if self.mode_num == 9 else (3 if self.mode_num == 13 else 6)))

        if self.mode_num == 13:
            self.oringinal = self.canvas_bottom.create_oval(200 * self.size - self.size * 2,
                                                            200 * self.size - self.size * 2,
                                                            200 * self.size + self.size * 2,
                                                            200 * self.size + self.size * 2, fill='#000')
        # 畫中間的線條
        for i in range(1, self.mode_num - 1):
            self.canvas_bottom.create_line(20 * self.size, 20 * self.size + i * self.dd, 380 * self.size,
                                           20 * self.size + i * self.dd, width=2)
            self.canvas_bottom.create_line(20 * self.size + i * self.dd, 20 * self.size, 20 * self.size + i * self.dd,
                                           380 * self.size, width=2)
        # 放置右側初始圖片
        self.pW = self.canvas_bottom.create_image(500 * self.size + 11, 65 * self.size, image=self.photoW)
        self.pB = self.canvas_bottom.create_image(500 * self.size - 11, 65 * self.size, image=self.photoB)
        # 每張圖片都添加image標籤，方便reload函式删除圖片
        self.canvas_bottom.addtag_withtag('image', self.pW)
        self.canvas_bottom.addtag_withtag('image', self.pB)

    def recover(self, list_to_recover, b_or_w):
        if len(list_to_recover) > 0:
            for i in range(len(list_to_recover)):
                self.positions[list_to_recover[i][1]][list_to_recover[i][0]] = b_or_w + 1
                self.image_added = self.canvas_bottom.create_image(
                    20 * self.size + (list_to_recover[i][0] - 1) * self.dd + 4 * self.p,
                    20 * self.size + (list_to_recover[i][1] - 1) * self.dd - 5 * self.p,
                    image=self.photoWBD_list[b_or_w])
                self.canvas_bottom.addtag_withtag('image', self.image_added)
                self.canvas_bottom.addtag_withtag('position' + str(list_to_recover[i][0]) + str(list_to_recover[i][1]),
                                                  self.image_added)

    def get_deadlist(self, x, y):
        deadlist = []
        for i in [-1, 1]:
            if self.positions[y][x + i] == (2 if self.present == 0 else 1) and ([x + i, y] not in deadlist):
                killList = self.if_dead([[x + i, y]], (2 if self.present == 0 else 1), [x + i, y])
                if not killList == False:
                    deadlist += copy.deepcopy(killList)
            if self.positions[y + i][x] == (2 if self.present == 0 else 1) and ([x, y + i] not in deadlist):
                killList = self.if_dead([[x, y + i]], (2 if self.present == 0 else 1), [x, y + i])
                if not killList == False:
                    deadlist += copy.deepcopy(killList)
        return deadlist

    def if_dead(self, deadList, yourChessman, yourPosition):
        for i in [-1, 1]:
            if [yourPosition[0] + i, yourPosition[1]] not in deadList:
                if self.positions[yourPosition[1]][yourPosition[0] + i] == 0:
                    return False
            if [yourPosition[0], yourPosition[1] + i] not in deadList:
                if self.positions[yourPosition[1] + i][yourPosition[0]] == 0:
                    return False
        if ([yourPosition[0] + 1, yourPosition[1]] not in deadList) and (
                self.positions[yourPosition[1]][yourPosition[0] + 1] == yourChessman):
            midvar = self.if_dead(deadList + [[yourPosition[0] + 1, yourPosition[1]]], yourChessman,
                                  [yourPosition[0] + 1, yourPosition[1]])
            if not midvar:
                return False
            else:
                deadList += copy.deepcopy(midvar)
        if ([yourPosition[0] - 1, yourPosition[1]] not in deadList) and (
                self.positions[yourPosition[1]][yourPosition[0] - 1] == yourChessman):
            midvar = self.if_dead(deadList + [[yourPosition[0] - 1, yourPosition[1]]], yourChessman,
                                  [yourPosition[0] - 1, yourPosition[1]])
            if not midvar:
                return False
            else:
                deadList += copy.deepcopy(midvar)
        if ([yourPosition[0], yourPosition[1] + 1] not in deadList) and (
                self.positions[yourPosition[1] + 1][yourPosition[0]] == yourChessman):
            midvar = self.if_dead(deadList + [[yourPosition[0], yourPosition[1] + 1]], yourChessman,
                                  [yourPosition[0], yourPosition[1] + 1])
            if not midvar:
                return False
            else:
                deadList += copy.deepcopy(midvar)
        if ([yourPosition[0], yourPosition[1] - 1] not in deadList) and (
                self.positions[yourPosition[1] - 1][yourPosition[0]] == yourChessman):
            midvar = self.if_dead(deadList + [[yourPosition[0], yourPosition[1] - 1]], yourChessman,
                                  [yourPosition[0], yourPosition[1] - 1])
            if not midvar:
                return False
            else:
                deadList += copy.deepcopy(midvar)
        return deadList

    def kill(self, killList):
        if len(killList) > 0:
            for i in range(len(killList)):
                self.positions[killList[i][1]][killList[i][0]] = 0
                self.canvas_bottom.delete('position' + str(killList[i][0]) + str(killList[i][1]))

    def create_pW(self):
        self.pW = self.canvas_bottom.create_image(500 * self.size + 11, 65 * self.size, image=self.photoW)
        self.canvas_bottom.addtag_withtag('image', self.pW)

    def create_pB(self):
        self.pB = self.canvas_bottom.create_image(500 * self.size - 11, 65 * self.size, image=self.photoB)
        self.canvas_bottom.addtag_withtag('image', self.pB)

    def del_pW(self):
        self.canvas_bottom.delete(self.pW)

    def del_pB(self):
        self.canvas_bottom.delete(self.pB)

class Application(model):
    # 初始化棋盤,預設十九路棋盤
    def __init__(self):
        model.__init__(self,mode_num)
        # 幾個功能按钮
        self.startButton = Button(self, text='開始對局', command=self.start)
        self.startButton.place(x=420 * self.size, y=200 * self.size)
        self.passmeButton = Button(self, text='停一手', command=self.passme)
        self.passmeButton.place(x=420 * self.size, y=225 * self.size)
        self.regretButton = Button(self, text='悔棋', command=self.regret)
        self.regretButton.place(x=420 * self.size, y=250 * self.size)
        self.replayButton = Button(self, text='重新開始', command=self.reload)
        self.replayButton.place(x=420 * self.size, y=275 * self.size)
        self.newGameButton1 = Button(self, text=('十三' if self.mode_num == 9 else '九') + '路棋', command=self.newGame1)
        self.newGameButton1.place(x=420 * self.size, y=300 * self.size)
        self.newGameButton2 = Button(self, text=('十三' if self.mode_num == 19 else '十九') + '路棋', command=self.newGame2)
        self.newGameButton2.place(x=420 * self.size, y=325 * self.size)
        self.quitButton = Button(self, text='退出棋局', command=self.quit)
        self.quitButton.place(x=420 * self.size, y=350 * self.size)
        self.territoryButton = Button(self, text='算地', command=self.territory)
        self.territoryButton.place(x=500 * self.size, y=200 * self.size)
        self.recordButton1 = Button(self, text='棋譜匯出', command=self.save_record)
        self.recordButton1.place(x=500 * self.size, y=225 * self.size)
        self.recordButton2 = Button(self, text='棋譜匯入', command=self.load_record)
        self.recordButton2.place(x=500 * self.size, y=250 * self.size)
        # 初始悔棋、停手按钮禁用
        self.passmeButton['state'] = DISABLED
        self.regretButton['state'] = DISABLED
        self.territoryButton['state'] = DISABLED
        # 滑鼠移动時，呼叫shadow函式，显示随滑鼠移动的棋子
        self.canvas_bottom.bind('<Motion>', self.shadow)
        # 滑鼠左键单击時，呼叫getdown函式，放下棋子
        self.canvas_bottom.bind('<Button-1>', self.getDown)
        # 设置退出快捷键<Ctrl>+<D>，快速退出遊戲
        self.bind('<Control-KeyPress-d>', self.keyboardQuit)

    # 開始對局函式，點擊“開始對局”時呼叫
    def start(self):
        # 停手按鈕解除
        self.passmeButton['state'] = NORMAL
        self.territoryButton['state'] = NORMAL
        # 删除右側太極圖
        self.canvas_bottom.delete(self.pW)
        self.canvas_bottom.delete(self.pB)
        # 利用右側圖案提示開始時誰先落子
        if self.present == 0:
            self.create_pB()
            self.del_pW()
        else:
            self.create_pW()
            self.del_pB()
        # 開始標誌，解除stop
        self.stop = None

    # 放棄一手函式，跳過落子環節
    def passme(self):
        # 悔棋恢復
        # 拷貝棋盤狀態，記錄前三次棋局
        self.last_3_positions = copy.deepcopy(self.last_2_positions)
        self.last_2_positions = copy.deepcopy(self.last_1_positions)
        self.last_1_positions = copy.deepcopy(self.positions)
        self.canvas_bottom.delete('image_added_sign')
        # 輪到下一玩家
        if self.present == 0:
            self.create_pW()
            self.del_pB()
            self.present = 1
        else:
            self.create_pB()
            self.del_pW()
            self.present = 0

    # 悔棋函式，可悔棋一回合，下两回合不可悔棋
    def regret(self):
        # 判定是否可以悔棋，以前第三盤棋局復原棋盤
        list_of_b = []
        list_of_w = []
        self.canvas_bottom.delete('image')
        if self.present == 0:
            self.create_pB()
        else:
            self.create_pW()
        for m in range(1, self.mode_num + 1):
            for n in range(1, self.mode_num + 1):
                self.positions[m][n] = 0

        for m in range(len(self.last_3_positions)):
            for n in range(len(self.last_3_positions[m])):
                if self.last_3_positions[m][n] == 1:
                    list_of_b += [[n, m]]
                elif self.last_3_positions[m][n] == 2:
                    list_of_w += [[n, m]]
        self.recover(list_of_b, 0)
        self.recover(list_of_w, 1)
        self.last_1_positions = copy.deepcopy(self.last_3_positions)
        self.record = copy.deepcopy(self.record[:-2])
        self.record_take = copy.deepcopy(self.record_take[:-2])
        # 判斷是否還能悔棋
        if len(self.record) < 2:
            self.regretButton['state'] = DISABLED
        # 重建last_2_positions、last_3_positions
        for m in range(1, self.mode_num + 1):
            for n in range(1, self.mode_num + 1):
                self.last_2_positions[m][n] = 0
                self.last_3_positions[m][n] = 0

        # 根據record恢復棋盤
        for r in self.record[:-2]:
            if r[2] == 1:
                self.last_3_positions[r[1]][r[0]] = 1
            elif r[2] == 2:
                self.last_3_positions[r[1]][r[0]] = 2

        for r in self.record[:-1]:
            if r[2] == 1:
                self.last_2_positions[r[1]][r[0]] = 1
            elif r[2] == 2:
                self.last_2_positions[r[1]][r[0]] = 2

        # 判斷是否為死棋
        if len(self.record_take) > 2:
            for t in self.record_take[-3]:
                self.last_3_positions[t[1]][t[0]] = 0
        if len(self.record_take) > 1:
            for t in self.record_take[-2]:
                self.last_2_positions[t[1]][t[0]] = 0

        # 判斷是否為被吃子
        if len(self.record_take) > 1:
            for t in self.record_take[-2]:
                if self.present == 1:
                    self.last_3_positions[t[1]][t[0]] = 1
                else:
                    self.last_3_positions[t[1]][t[0]] = 2

        if len(self.record_take) > 0:
            for t in self.record_take[-1]:
                if self.present == 1:
                    self.last_2_positions[t[1]][t[0]] = 2
                else:
                    self.last_2_positions[t[1]][t[0]] = 1

    # 點擊“重新開始”時呼叫重新加載函式,删除圖片，序列歸零，設置一些初始参數
    def reload(self):
        if self.stop is None:
            self.stop = True
            self.regretButton['state'] = DISABLED
            self.passmeButton['state'] = DISABLED
            self.territoryButton['state'] = DISABLED
        self.canvas_bottom.delete('image')
        self.present = 0
        self.create_pB()
        self.create_pW()
        self.record = []
        self.record_take = []
        for m in range(1, self.mode_num + 1):
            for n in range(1, self.mode_num + 1):
                self.positions[m][n] = 0
                self.last_3_positions[m][n] = 0
                self.last_2_positions[m][n] = 0
                self.last_1_positions[m][n] = 0

    # 顯示滑鼠移動下預定落子的位置
    def shadow(self, event):
        if not self.stop:
            # 找到最近格點，在當前位置靠近格點的可落子處顯示棋子圖片，並删除上一位置的棋子圖片
            if (20 * self.size < event.x < 380 * self.size) and (20 * self.size < event.y < 380 * self.size):
                dx = (event.x - 20 * self.size) % self.dd
                dy = (event.y - 20 * self.size) % self.dd
                x = int((event.x - 20 * self.size - dx) / self.dd + round(dx / self.dd) + 1)
                y = int((event.y - 20 * self.size - dy) / self.dd + round(dy / self.dd) + 1)
                # 判断該位置是否已有棋子
                if self.positions[y][x] == 0:
                    self.cross = self.canvas_bottom.create_image(
                        event.x - dx + round(dx / self.dd) * self.dd + 22 * self.p,
                        event.y - dy + round(dy / self.dd) * self.dd - 27 * self.p,
                        image=self.photoWBU_list[self.present])
                    self.canvas_bottom.addtag_withtag('image', self.cross)
                    if self.cross_last is not None:
                        self.canvas_bottom.delete(self.cross_last)
                    self.cross_last = self.cross
            else:
                if self.cross_last is not None:
                    self.canvas_bottom.delete(self.cross_last)

    def territory(self):
        if not self.stop:
            for y in range(self.mode_num):
                print()
                for x in range(self.mode_num):
                    count = 0
                    mag = 1
                    for i in [-1, 3]:
                        if not (y + i == -1 or y + i == 21):
                            if self.getTerritory(self.positions[y + i][x + 1]) is not None:
                                count += self.getTerritory(self.positions[y + i][x + 1])
                        if not (x + i == -1 or x + i == 21):
                            if self.getTerritory(self.positions[y + 1][x + i]) is not None:
                                count += self.getTerritory(self.positions[y + 1][x + i])
                    for m in [0, 2]:
                        for n in [0, 2]:
                            if self.getTerritory(self.positions[y + m][x + n]) is not None:
                                count += self.getTerritory(self.positions[y + m][x + n])

                        if self.getTerritory(self.positions[y + m][x + 1]) is not None:
                            count += self.getTerritory(self.positions[y + m][x + 1]) * 2
                        else:
                            mag += 0.25
                        if self.getTerritory(self.positions[y + 1][x + m]) is not None:
                            count += self.getTerritory(self.positions[y + 1][x + m]) * 2
                        else:
                            mag += 0.25
                    count += self.getTerritory(self.positions[y + 1][x + 1]) * 3
                    # if count!=0:
                    # print(x+1, y+1, count, mag, end=' ')
                    print(count, end=' ')

    def save_record(self):
        s = ''
        print('數字位置:', self.record)
        print('陣列位置:')
        for p in self.positions[1:-1]:
            print(p[1:-1])
        for r in self.record:
            if r[2] == 1:
                s += ';' + 'B[' + chr(r[0] + 96) + chr(r[1] + 96) + ']'
            else:
                s += ';' + 'W[' + chr(r[0] + 96) + chr(r[1] + 96) + ']'
        f = open('test.sgf', 'w')
        f.write('(')
        count = 0
        for i in s:
            f.write(i)
            if i == ']':
                count += 1
            if count == 10:
                f.write('\n')
                count = 0
        f.write(')')
        f.close()

    def load_record(self):
        f = open('test.sgf', 'r')
        print(f.read())
        self.recordShow()

        return

    def getTerritory(self, clr):
        if clr == -1:
            return None
        elif clr == 0:
            return 0
        elif clr == 1:
            return 1
        else:
            return -1

    # 落子，並驅動玩家的輪流下棋行為
    def getDown(self, event):
        if not self.stop:
            # 先找到最近格點
            if (20 * self.size - self.dd * 0.4 < event.x < self.dd * 0.4 + 380 * self.size) and (
                    20 * self.size - self.dd * 0.4 < event.y < self.dd * 0.4 + 380 * self.size):
                dx = (event.x - 20 * self.size) % self.dd
                dy = (event.y - 20 * self.size) % self.dd
                x = int((event.x - 20 * self.size - dx) / self.dd + round(dx / self.dd) + 1)
                y = int((event.y - 20 * self.size - dy) / self.dd + round(dy / self.dd) + 1)
                # 判斷位置是否已經被占據
                if self.positions[y][x] == 0:
                    # 未被占據，則嘗試占據，獲得占據後能殺死的棋子列表
                    self.positions[y][x] = self.present + 1
                    self.image_added = self.canvas_bottom.create_image(
                        event.x - dx + round(dx / self.dd) * self.dd + 4 * self.p,
                        event.y - dy + round(dy / self.dd) * self.dd - 5 * self.p,
                        image=self.photoWBD_list[self.present])
                    self.canvas_bottom.addtag_withtag('image', self.image_added)
                    # 棋子與位置標籤绑定，方便“殺死”
                    self.canvas_bottom.addtag_withtag('position' + str(x) + str(y), self.image_added)
                    deadlist = self.get_deadlist(x, y)
                    self.kill(deadlist)
                    # 判断是否重複棋局（打劫）
                    if not self.last_2_positions == self.positions:
                        # 判断是否有氣(避免不入子)或行棋後可殺棋提子
                        if len(deadlist) > 0 or self.if_dead([[x, y]], self.present + 1, [x, y]) == False:
                            # 當不重複棋局且並非不入子狀況下，即落子有效，並紀錄棋步
                            self.record.append([x, y, self.positions[y][x]])
                            if len(deadlist) > 0:
                                temp = []
                                for d in deadlist:
                                    temp.append([d[0], d[1]])
                                self.record_take.append(temp)
                            else:
                                self.record_take.append([])
                            self.last_3_positions = copy.deepcopy(self.last_2_positions)
                            self.last_2_positions = copy.deepcopy(self.last_1_positions)
                            self.last_1_positions = copy.deepcopy(self.positions)
                            # 删除上次的標記，重新創建標記
                            self.canvas_bottom.delete('image_added_sign')
                            self.image_added_sign = self.canvas_bottom.create_oval(
                                event.x - dx + round(dx / self.dd) * self.dd + 0.5 * self.dd,
                                event.y - dy + round(dy / self.dd) * self.dd + 0.5 * self.dd,
                                event.x - dx + round(dx / self.dd) * self.dd - 0.5 * self.dd,
                                event.y - dy + round(dy / self.dd) * self.dd - 0.5 * self.dd, width=3, outline='#3ae')
                            self.canvas_bottom.addtag_withtag('image', self.image_added_sign)
                            self.canvas_bottom.addtag_withtag('image_added_sign', self.image_added_sign)
                            if len(self.record) > 1:
                                self.regretButton['state'] = NORMAL
                            if self.present == 0:
                                self.create_pW()
                                self.del_pB()
                                self.present = 1
                            else:
                                self.create_pB()
                                self.del_pW()
                                self.present = 0
                        else:
                            # 不屬於殺死對方或有氣，則判断為無氣，警告並彈出警告訊息盒
                            self.positions[y][x] = 0
                            self.canvas_bottom.delete('position' + str(x) + str(y))
                            self.bell()
                            self.showwarningbox('沒氣了', "禁著點！")
                    else:
                        # 重複棋局，警告打劫
                        self.positions[y][x] = 0
                        self.canvas_bottom.delete('position' + str(x) + str(y))
                        self.recover(deadlist, (1 if self.present == 0 else 0))
                        self.bell()
                        self.showwarningbox("打劫", "不可提熱子！")
                else:
                    # 落子重疊，聲音警告
                    self.bell()
            else:
                # 超出邊界，聲音警告
                self.bell()

    # 判断棋子（yourChessman：棋子種類係黑棋或白棋，yourPosition：棋子位置）是否無氣（死亡），有氣则返回False，無氣则返回無氣棋子的列表
    # 本函式是對弈规则的關鍵，初始deadlist只包含了自己的位置，每次執行時，函式嘗試尋找yourPosition周圍有没有空的位置，有則结束並返回False代表有氣；
    # 若找不到，則找自己四周的同類（不在deadlist中的）是否有氣（即遞回呼叫本函式），無氣，则把該同類加入到deadlist，然候找下一個鄰居，只要有一個有氣，則返回False代表有氣；
    # 若四周没有一個有氣的同類，返回deadlist,至此结束遞回
    # def if_dead(self,deadlist,yourChessman,yourPosition):

    # 警告訊息顯示盒，接受標题和警告訊息
    def showwarningbox(self, title, message):
        self.canvas_bottom.delete(self.cross)
        tkinter.messagebox.showwarning(title, message)

    # 键盤快捷键退出遊戲
    def keyboardQuit(self, event):
        self.quit()

    # 以下两個函式修改全局變量值，newApp使主函式循環，以建立不同参数的對象
    def newGame1(self):
        global mode_num, newApp
        mode_num = (13 if self.mode_num == 9 else 9)
        newApp = True
        self.quit()

    def newGame2(self):
        global mode_num, newApp
        mode_num = (13 if self.mode_num == 19 else 19)
        newApp = True
        self.quit()

    def recordShow(self):
        global mode_num, newApp2
        mode_num = self.mode_num
        newApp2 = True
        self.quit()

class Application2(model):
    # 初始化棋盤,預設十九路棋盤
    def __init__(self):
        model.__init__(self, mode_num)
        self.record = self.load_record()
        self.record_take = []
        self.record_next = []
        self.previousButton = Button(self, text='上一手', command=self.previousMove)
        self.previousButton.place(x=420 * self.size, y=200 * self.size)
        self.nextButton = Button(self, text='下一手', command=self.nextMove)
        self.nextButton.place(x=420 * self.size, y=225 * self.size)
        self.previousButton['state'] = DISABLED
        self.nextButton['state'] = DISABLED
        self.backButton = Button(self, text='返回', command=self.back)
        self.backButton.place(x=420 * self.size, y=250 * self.size)
        for r in self.record:
            self.getDown(r[0], r[1])
        if not self.record==[]:
            self.previousButton['state'] = NORMAL

    def getDown(self, x, y):
        self.positions[y][x] = self.present + 1
        ex = 30 + self.dd*(x-1)
        ey = 30 + self.dd*(y-1)
        dx = (ex - 20 * self.size) % self.dd
        dy = (ey - 20 * self.size) % self.dd
        self.image_added = self.canvas_bottom.create_image(
            ex - dx + round(dx / self.dd) * self.dd + 4 * self.p,
            ey - dy + round(dy / self.dd) * self.dd - 5 * self.p,
            image=self.photoWBD_list[self.present])

        self.canvas_bottom.addtag_withtag('image', self.image_added)
        # 棋子與位置標籤绑定，方便“殺死”
        self.canvas_bottom.addtag_withtag('position' + str(x) + str(y), self.image_added)
        deadlist = self.get_deadlist(x, y)
        self.kill(deadlist)
        if len(deadlist) > 0:
            temp = []
            for d in deadlist:
                temp.append([d[0], d[1]])
            self.record_take.append(temp)
        else:
            self.record_take.append([])

        self.last_3_positions = copy.deepcopy(self.last_2_positions)
        self.last_2_positions = copy.deepcopy(self.last_1_positions)
        self.last_1_positions = copy.deepcopy(self.positions)
        # 删除上次的標記，重新創建標記
        self.canvas_bottom.delete('image_added_sign')
        self.image_added_sign = self.canvas_bottom.create_oval(
            ex - dx + round(dx / self.dd) * self.dd + 0.5 * self.dd,
            ey - dy + round(dy / self.dd) * self.dd + 0.5 * self.dd,
            ex - dx + round(dx / self.dd) * self.dd - 0.5 * self.dd,
            ey - dy + round(dy / self.dd) * self.dd - 0.5 * self.dd, width=3, outline='#3ae')
        self.canvas_bottom.addtag_withtag('image', self.image_added_sign)
        self.canvas_bottom.addtag_withtag('image_added_sign', self.image_added_sign)

        if self.present == 0:
            self.create_pW()
            self.del_pB()
            self.present = 1
        else:
            self.create_pB()
            self.del_pW()
            self.present = 0

    def previousMove(self):
        # for i in range(time):
        list_of_b = []
        list_of_w = []
        self.canvas_bottom.delete('image')
        if self.present == 1:
            self.create_pB()
            self.del_pW()
            self.present = 0
        else:
            self.create_pW()
            self.del_pB()
            self.present = 1

        for m in range(len(self.last_2_positions)):
            for n in range(len(self.last_2_positions[m])):
                if self.last_2_positions[m][n] == 1:
                    list_of_b += [[n, m]]
                elif self.last_2_positions[m][n] == 2:
                    list_of_w += [[n, m]]

        self.recover(list_of_b, 0)
        self.recover(list_of_w, 1)
        self.last_1_positions = copy.deepcopy(self.last_2_positions)
        self.last_2_positions = copy.deepcopy(self.last_3_positions)
        self.positions = copy.deepcopy(self.last_1_positions)
        self.record_next.append(self.record[-1])
        self.record = copy.deepcopy(self.record[:-1])
        self.record_take = copy.deepcopy(self.record_take[:-1])
        print(self.record)
        # 判斷是否還有上一手
        if len(self.record) < 1:
            self.previousButton['state'] = DISABLED
        if len(self.record_next) > 0:
            self.nextButton['state'] = NORMAL
        # 重建last_2_positions、last_3_positions
        for m in range(1, self.mode_num + 1):
            for n in range(1, self.mode_num + 1):
                self.last_3_positions[m][n] = 0

        # 根據record恢復棋盤
        for r in self.record[:-2]:
            if r[2] == 1:
                self.last_3_positions[r[1]][r[0]] = 1
            elif r[2] == 2:
                self.last_3_positions[r[1]][r[0]] = 2

        # 判斷是否為死棋
        if len(self.record_take) > 3:
            for t in self.record_take[-4]:
                self.last_3_positions[t[1]][t[0]] = 0
            for t in self.record_take[-3]:
                self.last_3_positions[t[1]][t[0]] = 0


        # 判斷是否為被吃子
        if len(self.record_take) > 1:
            for t in self.record_take[-2]:
                if self.present == 1:
                    self.last_3_positions[t[1]][t[0]] = 1
                else:
                    self.last_3_positions[t[1]][t[0]] = 2

    def nextMove(self):
        if len(self.record_next) > 0:
            self.record.append(self.record_next[-1])
            self.getDown(self.record_next[-1][0], self.record_next[-1][1])
            print(self.record)
            self.record_next = copy.deepcopy(self.record_next[:-1])
        if len(self.record_next) <= 0:
            self.nextButton['state'] = DISABLED
        if len(self.record) > 0:
            self.previousButton['state'] = NORMAL

    def load_record(self):
        f = open('test.sgf', 'r')
        a = re.sub(r'[\':\s ,(;\[\])]*', '', f.read())
        r = []
        for i in range(int(len(a)/3)):
            if a[i*3] == 'B':
                r.append([ord(a[i*3 + 1])-96, ord(a[i*3 + 2])-96, 1])
            else:
                r.append([ord(a[i*3 + 1])-96, ord(a[i*3 + 2])-96, 2])
        f.close()
        return r

    def back(self):
        global mode_num, newApp
        mode_num = self.mode_num
        newApp = True
        self.quit()

# 聲明全局變量，用於新建Application對象時切换成不同模式的遊戲
global mode_num, newApp, newApp2
mode_num = 19
newApp = False
newApp2 = False
if __name__ == '__main__':
    # 循環，直到不切换遊戲模式
    while True:
        newApp = False
        newApp2 = False
        app = Application()
        app.title('圍棋')
        app.mainloop()
        if newApp2:
            app.destroy()
            app = Application2()
            app.title('圍棋')
            app.mainloop()
        if newApp:
            app.destroy()
        else:
            break