import sys, re
if __name__=='__main__':
    sys.path.append(sys.path[0]+'\\..')
from body.bone import NetP
from body.body_motor import Motor
from tools import tools_basic
from PyQt5.QtWidgets import QTextEdit, QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QFont

class Debugger(QTextEdit):
    def __init__(self,point=None):
        super().__init__()
        self.m_self=None
        self.m_outPool=None
        self.m_motor=None

        self.m_words={}
        self.m_sents={}
        self.m_karmas=[]
        self.m_ptrKm=0

        self.setWindowTitle('debugger')
        self.setGeometry(300,300,400,200)
        self.setStyleSheet('font: 20px;')
        self.setFont(QFont('宋体'))
        self.setReadOnly(True)
        # self.closeEvent=self.reset

        self.initialize(point)

    def initialize(self,point):
        if point==None:
            point=NetP('debugger')
        self.m_self=point
        point.m_dev=self
        point.m_permission=0

        pt_motor=tools_basic.getPoint(point,'m_motor','compiler')
        if pt_motor.m_dev==None:
            self.m_motor=Motor(pt_motor)
        else:
            self.m_motor=pt_motor.m_dev


    def paintEvent(self,QPaintEvent):
        return super().paintEvent(QPaintEvent)

    def genPool(self,mode=0):
        if self.m_outPool==None:
            return []
        else:
            return self.m_outPool.m_pool
    
    def closeEvent(self,QCloseEvent):
        self.reset()
        return super().closeEvent(QCloseEvent)

    def keyPressEvent(self,event):
        modifiers=QApplication.keyboardModifiers()
        self.control(event.key())
        return super().keyPressEvent(event)

    def control(self,key):
        if key==Qt.Key_S:
            self.m_motor.run(1)
        elif key==Qt.Key_W:
            self.m_motor.runAll()
        elif key==Qt.Key_A:
            self.changeSent(False)
        elif key==Qt.Key_D:
            self.changeSent(True)
        self.markWords()
        if self.m_outPool!=None:
            self.m_outPool.update()

    def setSentsForRun(self,code):
        self.setPlainText(code)
        self.m_motor.reset()
        self.m_motor.loadCode(code)
        karmas=self.m_motor.m_karmas
        self.m_karmas=karmas
        if karmas==[]:
            return
        print(karmas[0].info_karma())
        start=0
        for sent in karmas:
            list_pt=tools_basic.pointsInChain(sent)
            words=[pt.m_name for pt in list_pt]
            word_map,start=self.mapWord(words,code,start)
            pos_sent=[start,start]
            for pt in list_pt:
                i=list_pt.index(pt)
                pos=word_map[i]
                if pos[0]==-1 or pos[1]==-1:
                    continue
                else:
                    if pos[0]<pos_sent[0]:
                        pos_sent[0]=pos[0]
                self.m_words.update({pt:pos})
            self.m_sents.update({sent:pos_sent})
        self.markWords()
        self.m_motor.run(0,karmas[0])
        

    def mapWord(self,words,text,start):
        word_map=[]
        for word in words:
            pos=text.find(word,start)
            if pos==-1:
                word_map.append((-1,-1))
            else:
                word_map.append((pos,pos+len(word)))
            start=pos+len(word)
        return word_map,start

    def selectText(self,start,end):
        cursor=self.textCursor()
        cursor0=self.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Right,QTextCursor.MoveAnchor,start)
        cursor.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor,end-start)
        self.setTextCursor(cursor)
        return cursor0

    def markWords(self):
        for word in self.m_words:
            index=self.m_words[word]
            cursor0=self.selectText(index[0],index[1])
            if word.m_master.m_reState=='':
                if word.m_master.stateSelf()=='green':
                    self.setTextBackgroundColor(Qt.green)
                    self.setTextColor(Qt.black)
                elif word.m_master.stateSelf()=='red':
                    self.setTextBackgroundColor(Qt.red)
                    self.setTextColor(Qt.black)
                elif word.m_master.stateSelf()=='blue':
                    self.setTextBackgroundColor(Qt.blue)
                    self.setTextColor(Qt.white)
                else:
                    self.setTextBackgroundColor(Qt.yellow)
                    self.setTextColor(Qt.black)
            elif word.m_master.m_reState=='dark green':
                self.setTextBackgroundColor(Qt.darkGreen)
                self.setTextColor(Qt.white)
            else:
                self.setTextBackgroundColor(Qt.darkYellow)
                self.setTextColor(Qt.white)
            self.setTextCursor(cursor0)

    def markSent(self,sent,mark):
        index=self.m_sents[sent]
        cursor0=self.selectText(index[0],index[1])
        self.setFontUnderline(mark)
        self.setTextCursor(cursor0)

    def movePtr(self,right):
        ptr=self.m_ptrKm
        curKm=self.m_karmas[ptr]
        if right==False:
            if ptr<=0:
                ptr=0
            elif self.m_motor.m_running==[] or self.m_motor.m_running[-1]!=curKm:
                pass
            elif curKm.m_stage!=1:
                pass
            else:
                ptr-=1
        else:
            if ptr>=len(self.m_karmas)-1:
                ptr=len(self.m_karmas)-1
            else:
                ptr+=1
        return ptr

    def changeSent(self,right):
        ptr=self.movePtr(right)
        curKm=self.m_karmas[self.m_ptrKm]
        if right==True and ptr==self.m_ptrKm:
            self.m_motor.run(-1)
        elif right==True and ptr>self.m_ptrKm:
            self.m_motor.run(-1)
            self.setRunningSent(ptr)
        elif right==False and ptr==self.m_ptrKm:
            self.setRunningSent(ptr)
        elif right==False and ptr<self.m_ptrKm:
            self.m_motor.retrive(curKm)
            self.setRunningSent(ptr)

    def setRunningSent(self,ptr):
        curKm=self.m_karmas[ptr]
        self.m_ptrKm=ptr
        self.m_motor.retrive(curKm)
        self.m_motor.run(0,curKm)
        

    def reset(self,code=''):
        self.m_words.clear()
        self.m_sents.clear()
        self.m_motor.reset()

        if code=='':
            return
        self.setSentsForRun(code)
        # self.changeSent()




if __name__=='__main__':
    app=QApplication(sys.argv)
    window=Debugger()
    window.reset('+test->+test(+1,+2)->+1->+2')
    window.show()
    print(window.m_words)
    sys.exit(app.exec_())