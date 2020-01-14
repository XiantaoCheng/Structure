import sys, re
if __name__=='__main__':
    sys.path.append(sys.path[0]+'\\..')
from body.bone import NetP
from body.soul import Karma
from body.body_motor import Motor
from body.body_pool import Pool
from body.body_brain import Brain
from body.body_debugger import Debugger
from tools import tools_sl, tools_basic
from PyQt5.QtWidgets import QTextEdit, QApplication, QMessageBox, QFontDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QFont
# import matlab.engine

class Editor(QTextEdit):
    def __init__(self,name):
        super().__init__()
        self.m_self=None
        
        self.m_pool=None
        self.m_motor=None
        self.m_debugger=None
        self.m_screen=None

        self.m_plainText=None
        self.m_readPtr=None
        

        self.m_currentFile=''
        self.m_changed=False
        self.textChanged.connect(self.changed)
        self.m_systemMark='\n-----------系统-----------\n'

    def initialize(self,point):
        if point==None:
            point=NetP('editor')
        self.m_self=point
        point.m_dev=self
        point.m_permission=0

        pt_text=tools_basic.getPoint(point,'m_plainText','text')
        pt_pool=tools_basic.getPoint(point,'m_pool','pool')
        pt_motor=tools_basic.getPoint(point,'m_motor','compiler')
        pt_debugger=tools_basic.getPoint(point,'m_debugger','debugger')
        pt_screen=tools_basic.getPoint(point,'m_screen','screen')

        self.modifyPtStruct(pt_debugger,pt_motor,pt_pool)

        self.m_plainText=pt_text
        self.setReadPtr(pt_text)
        self.m_pool=Pool(pt_pool)
        self.m_motor=Motor(pt_motor)
        self.m_debugger=Debugger(pt_debugger)
        self.m_screen=Brain(pt_screen)
        self.m_pool.register(self.m_screen.m_self)
        self.m_pool.register(self.m_debugger.m_self)

        self.updateByPts()
        self.setFont(QFont('宋体'))
        self.setStyleSheet('font: 20px;')
        self.show()

    def modifyPtStruct(self,pt_debugger,pt_motor,pt_pool):
        tools_basic.setPoint(pt_debugger,'m_motor',pt_motor)
        tools_basic.setPoint(pt_motor,'m_source',pt_pool)
        pt_lib=tools_basic.getPoint(pt_pool,'m_lib')
        tools_basic.setPoint(pt_lib,'m_motor',pt_motor)

    def resizeEvent(self, QResizeEvent):
        self.updateSysPts()
        return super().resizeEvent(QResizeEvent)

    def keyPressEvent(self, QKeyEvent):
        modifier=QApplication.keyboardModifiers()
        if modifier==Qt.ControlModifier:
            if QKeyEvent.key()==Qt.Key_S:
                self.saveAsFile()
            elif QKeyEvent.key()==Qt.Key_R:
                self.runCode()
            elif QKeyEvent.key()==Qt.Key_T:
                self.debugCode()
            elif QKeyEvent.key()==Qt.Key_Q:
                self.setReadPtr(self.m_plainText)
        return super().keyPressEvent(QKeyEvent)

    def openFile(self,fileName):
        [text1,text2]=self.readFile(fileName)
        if text1==None and text2==None:
            return False
        self.m_currentFile=fileName
        self.loadText(text1,text2)
        self.m_changed=False
        self.updateState()
        return True

    def readFile(self,fileName):
        try:
            f=open(fileName,encoding='gbk')
        except:
            print("The file, "+fileName+", doesn't exist.")
            return [None,None]
        try:
            textGbk=f.read()
        except:
            textGbk=None
        f.close()

        f=open(fileName,encoding='utf-8')
        try:
            textUtf=f.read()
        except:
            textUtf=None
        f.close()
        return [textGbk,textUtf]


    def loadText(self,text1,text2):
        head=None
        if text1==None:
            code,ni=self.fixFormat(text2)
        elif text2==None:
            code,ni=self.fixFormat(text1)
        else:
            code1,n1=self.fixFormat(text1)
            code2,n2=self.fixFormat(text2)
            if n1==-1:
                code=code2
            else:
                code=code1
        list_pt=tools_basic.buildPoints_tokener(code)
        # for point in list_pt:
        #     point.m_permission=0
        #     if point.m_db[0]!=None or point.m_db[1]!=None:
        #         continue
        #     for con in point.m_con:
        #         if con.m_db[1]==point:
        #             break
        #         head=point
        head=list_pt[0]
        self.initialize(head)
        # for point in list_pt:
        #     if point.m_name=='in':
        #         print(point.info(),point.m_permission)

    def fixFormat(self,text):
        ni=text.find(self.m_systemMark)
        # old fashion
        if ni!=0:
            # code='editor(,);m_plainText(editor,text);text\"'+code+'\"(,);'
            code=self.transferCode(text)
        # new fashion
        else:
            code=text[len(self.m_systemMark):]
        return code,ni

    def transferCode(self,text):
        plainText,sysPt,nrmPt=self.takeParts_oldFasion(text)
        code='editor(,);m_plainText(editor,text);text\"'+plainText\
            +'\"(,);m_pool(editor,pool);pool(,);m_contain(pool,points);'+\
            'points\"'+nrmPt+'\"(,);'
        return code
    
    def takeParts_oldFasion(self,wholeText):
        normalMark='\n----------普通----------\n'
        systemMark='\n----------系统----------\n'
        n=wholeText.rfind(normalMark)
        if n==-1:
            return [wholeText,'','']
        s=wholeText.rfind(systemMark,0,n)
        if s==-1:
            return [wholeText,'','']
        return [wholeText[0:s],wholeText[s+len(systemMark):n],wholeText[n+len(normalMark):]]


    def saveAsFile(self,fileName=None):
        if fileName==None:
            fileName=self.m_currentFile
        if fileName=='':
            QMessageBox.Warning(self,"Save failed!","Warning: the file name can't be empty")
        text=self.m_systemMark+self.saveText()
        f=open(fileName,'+w')
        f.write(text)
        f.close()
        self.m_currentFile=fileName
        self.m_changed=False
        self.updateState()

    def saveText(self):
        list_pt=tools_basic.getAllSystemPt(self.m_self)
        return tools_basic.writeStdCode([],list_pt)

    

    def updateState(self):
        title=''
        if self.m_changed==True:
            title='*'
        i=self.m_currentFile.rfind('\\')
        if i+1==len(self.m_currentFile):
            i=-1
        title+=self.m_currentFile[i+1:]
        if self.m_readPtr!=self.m_plainText:
            title+=': '+self.m_readPtr.info(1)
        self.setWindowTitle(title)

    def changed(self):
        self.m_changed=True
        self.updateState()
        if self.m_self!=None:
            # pt_text=tools_basic.getPoint(self.m_self,'m_plainText')
            # pt_text.m_text=self.toPlainText()
            self.m_readPtr.m_text=self.toPlainText()

    def runCode(self):
        # complete the selection area
        text=self.toPlainText()
        cursor=self.textCursor()
        s=cursor.selectionStart()
        e=cursor.selectionEnd()
        ns=text.rfind('\n',0,s)+1
        ne=text.find('\n',e,-1)
        cursor=self.selectText(ns,ne)
        code=cursor.selectedText().replace("\u2029",'\n')
        # operate code
        operation_pool=self.m_motor.m_inputs
        if self.m_self not in operation_pool:
            operation_pool.append(self.m_self)
        outputs=self.m_motor.runCode(code)
        operation_pool.remove(self.m_self)
        self.m_pool.input(outputs)

    def debugCode(self):
        # complete the selection area
        text=self.toPlainText()
        cursor=self.textCursor()
        s=cursor.selectionStart()
        e=cursor.selectionEnd()
        ns=text.rfind('\n',0,s)+1
        ne=text.find('\n',e,-1)
        cursor=self.selectText(ns,ne)
        code=cursor.selectedText().replace("\u2029",'\n')
        #debug
        if self.m_debugger.isVisible()==False:
            self.m_debugger.setVisible(True)
        self.m_debugger.reset(code)

    def setReadPtr(self,pt_text):
        self.m_readPtr=pt_text
        self.setPlainText(pt_text.m_text)

    def selectText(self,start,end):
        cursor=self.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Right,QTextCursor.MoveAnchor,start)
        if end==-1:
            cursor.movePosition(QTextCursor.End,QTextCursor.KeepAnchor)
        else:
            cursor.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor,end-start)
        self.setTextCursor(cursor)
        return cursor


    ######## functions interact with points
    def updateSysPts(self):
        pt_x=tools_basic.getPoint(self.m_self,'m_x')
        pt_y=tools_basic.getPoint(self.m_self,'m_y')
        pt_height=tools_basic.getPoint(self.m_self,'m_height')
        pt_width=tools_basic.getPoint(self.m_self,'m_width')

        pt_x.m_name=str(self.geometry().x())
        pt_y.m_name=str(self.geometry().y())
        pt_width.m_name=str(self.geometry().width())
        pt_height.m_name=str(self.geometry().height())


    def updateByPts(self):
        pt_x=tools_basic.getPoint(self.m_self,'m_x','300')
        pt_y=tools_basic.getPoint(self.m_self,'m_y','300')
        pt_height=tools_basic.getPoint(self.m_self,'m_height','600')
        pt_width=tools_basic.getPoint(self.m_self,'m_width','300')

        x=int(pt_x.m_name)
        y=int(pt_y.m_name)
        width=int(pt_width.m_name)
        height=int(pt_height.m_name)

        self.setGeometry(x,y,width,height)
        


if __name__=="__main__":
    app=QApplication(sys.argv)
    editor=Editor("editor")
    if len(sys.argv)<2:
        print("Invalid file name!")
    else:
        print(sys.argv[1])
        editor.openFile(sys.argv[1])
    sys.exit(app.exec_())