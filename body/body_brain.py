import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QFont, QColor, QPen
from PyQt5.QtCore import Qt, QRectF
if __name__=='__main__':
    sys.path.append(sys.path[0]+'\\..')
from body.bone import NetP
from body.body_pool import Pool
from tools import tools_basic

class Brain(QWidget):
    def __init__(self,point=None):
        super().__init__()

        self.m_self=None
        
        self.m_pool=[]
        self.m_inPool=None
        self.m_outPool=None
        self.m_sysDict={}
        self.m_unit=40
        self.m_worldOrigin=[-5,-5]
        self.m_sizeW=[500,500]
        self.m_posW=[100,200]

        self.m_select=[]
        self.m_mode=0                           # 0-normal, 1-connect left, 2-connect right

        # discription:
        self.m_origin=NetP('起点')
        self.m_origin.m_pos=self.m_worldOrigin

        self.initialize(point)

        self.setWindow()
        self.show()
        self.initializeSys()


        #QMessageBox.about(self,"test","test")

    def initialize(self,point):
        if point==None:
            point=NetP('screen')
        self.m_self=point
        point.m_permission=0
        point.m_dev=self

        pt_select=tools_basic.getPoint(point,'m_select','list')
        self.m_select=tools_basic.getPointByFormat(pt_select,'list')


    def initializeSys(self):
        if self.m_sysDict!={}:
            return
        self.m_sysDict={'system':[NetP('选中'),self.m_origin],'selection':[]}

    def setWindow(self):
        self.setWindowTitle(self.m_self.m_name)
        self.setGeometry(self.m_posW[0],self.m_posW[1],self.m_sizeW[0],self.m_sizeW[1])

    def updateInfoW(self):
        self.m_sizeW[0]=self.geometry().width()
        self.m_sizeW[1]=self.geometry().height()
        self.m_posW[0]=self.geometry().x()
        self.m_posW[1]=self.geometry().y()

    def genPool(self):
        if self.m_inPool==None:
            pool=[]
        else:
            pool=self.m_inPool.m_pool
        return pool


    def paintEvent(self,event):
        self.updateInfoW()
        pool=self.genPool()
        qp=QPainter()
        qp.begin(self)
        self.gridOn(qp)
        for connect in pool:
            self.drawNetEdge(connect,qp)
        for point in pool:
            if self.inScreen(point.m_pos):
                self.drawNetPoint(point,qp)
        qp.end()

    def pointPosition(self,pos):
        x=(pos[0]-self.m_worldOrigin[0])*self.m_unit
        y=(pos[1]-self.m_worldOrigin[1])*self.m_unit
        return [x,y]

    def screenPos2WorldPos(self,posS):
        x=posS[0]/self.m_unit+self.m_worldOrigin[0]+0.5
        if x<0:
            x+=-1
        y=posS[1]/self.m_unit+self.m_worldOrigin[1]+0.5
        if y<0:
            y+=-1
        return [int(x),int(y)]

    def inScreen(self,pos):
        R=self.m_unit*0.4
        dx=(pos[0]-self.m_worldOrigin[0])*self.m_unit
        dy=(pos[1]-self.m_worldOrigin[1])*self.m_unit
        return dx>-R and dx<self.m_sizeW[0]+R and dy>-R and dy<self.m_sizeW[1]+R

    def screenAreaInWorld(self):
        x0=self.m_worldOrigin[0]
        y0=self.m_worldOrigin[1]
        dx=self.m_sizeW[0]/self.m_unit
        dy=self.m_sizeW[1]/self.m_unit
        return [x0,y0,dx,dy]

    def gridOn(self,qp):
        [x0,y0,dx,dy]=self.screenAreaInWorld()
        width=self.m_unit*0.5
        qp.setFont(QFont("Decorative",self.m_unit*0.2))

        for i in range(int(x0),int(x0+dx+1)):
            [xi,yi]=self.pointPosition([i,int(y0)])
            qp.drawLine(xi,0,xi,self.m_sizeW[1])
            if i!=x0:
                qp.drawText(QRectF(xi-width,yi,width,width),Qt.AlignCenter,str(i))
        for i in range(int(y0),int(y0+dy+1)):
            [xi,yi]=self.pointPosition([int(x0),i])
            qp.drawLine(0,yi,self.m_sizeW[0],yi)
            if i!=y0:
                qp.drawText(QRectF(xi,yi-width,width,width),Qt.AlignCenter,str(i))

    def drawNetPoint(self,point,qp):
        R=self.m_unit*0.4
        pos=self.pointPosition(point.m_pos)
        x0=pos[0]-R
        y0=pos[1]-R

        if point in self.m_select:
            if point==self.m_select[-1]:
                if self.m_mode==0:
                    qp.setPen(QPen(QColor(0,0,250,150),4,Qt.SolidLine))
                elif self.m_mode==1:
                    qp.setPen(QPen(QColor(0,250,0,150),4,Qt.SolidLine))
                else:
                    qp.setPen(QPen(QColor(250,0,0,150),4,Qt.SolidLine))
            else:
                if self.m_mode==0:
                    qp.setPen(QPen(QColor(31,73,125,100),4,Qt.SolidLine))
                elif self.m_mode==1:
                    qp.setPen(QPen(QColor(0,125,0,100),4,Qt.SolidLine))
                else:
                    qp.setPen(QPen(QColor(125,0,0,100),4,Qt.SolidLine))
        # elif point in self.m_preSec:
        #     qp.setPen(QPen(QColor(31,73,125,50),4,Qt.SolidLine))
        else:
            qp.setPen(QPen(QColor(31,73,125,0),4,Qt.SolidLine))

        if point.m_creator!=None or point.m_needed==None:
            qp.setBrush(QColor(155,187,89))
        else:
            qp.setBrush(QColor(50,50,200))

        qp.drawEllipse(x0,y0,R*2,R*2)
        qp.setPen(Qt.white)
        qp.setFont(QFont("Decorative",R*0.5))

        name=point.m_name[0:3]
        qp.drawText(QRectF(x0,y0,R*2,R*2),Qt.AlignCenter,name)

    def drawNetEdge(self,point,qp):
        pool=self.genPool()

        pos=self.pointPosition(point.m_pos)
        x0=pos[0]
        y0=pos[1]
        qp.setPen(QPen(QColor(31,73,125),5,Qt.SolidLine))

        if point.m_db[0]!=None and point.m_db[0] in pool:
            pos=self.pointPosition(point.m_db[0].m_pos)
            line0_x=pos[0]
            line0_y=pos[1]
            qp.drawLine(x0,y0,line0_x,line0_y)

        if point.m_db[1]!=None and point.m_db[1] in pool:
            pos=self.pointPosition(point.m_db[1].m_pos)
            line1_x=pos[0]
            line1_y=pos[1]
            qp.drawLine(x0,y0,line1_x,line1_y)

    def selectPoint(self,pos):
        R=self.m_unit*0.4
        for point in self.genPool():
            x,y=self.pointPosition(point.m_pos)
            if abs(x-pos[0])<R and abs(y-pos[1])<R:
                return point
        return None

    def mousePressEvent(self, event):
        modifier=QApplication.keyboardModifiers()
        pos=[event.windowPos().x(),event.windowPos().y()]
        point=self.selectPoint(pos)
        if point!=None:
            point.print()
        if event.buttons()==Qt.LeftButton:
            if point!=None:
                if point in self.m_select:
                    # self.m_select.remove(point)
                    self.removeSel(point)
                if modifier==Qt.ControlModifier:
                    # self.m_select.insert(0,point)
                    self.addSel(point)
                elif self.m_mode==0:
                    # self.m_select.clear()
                    # self.m_select.append(point)
                    self.clearSel()
                    self.addSel(point)
                else:
                    self.connectPoints(point,self.m_select,self.m_mode)
            else:
                if self.m_mode==0:
                    self.movePoints(self.m_select,pos)
                else:
                    self.connectPoints(point,self.m_select,self.m_mode)
        else:
            if point!=None and point in self.m_select:
                # self.m_select.remove(point)
                self.removeSel(point)
            elif self.m_select!=[]:
                # self.m_select.pop()
                self.popSel()
            if self.m_select==[]:
                self.m_mode=0
        if self.m_outPool!=None:
            self.m_outPool.update()

    def addSel(self,point):
        self.m_select.append(point)
        pt_select=tools_basic.getPoint(self.m_self,'m_select','list')
        tools_basic.setPointByFormat(pt_select,'list.append',point)
        # select=self.m_sysDict['system'][0]
        # connect=NetP('的')
        # connect.con(select,point)
        # list_pt=self.m_sysDict['selection']
        # list_pt.append(connect)

    def clearSel(self):
        self.m_select.clear()
        pt_select=tools_basic.getPoint(self.m_self,'m_select','list')
        tools_basic.setPointByFormat(pt_select,'list.clear')
        # list_pt=self.m_sysDict['selection']
        # for point in list_pt:
        #     point.delete()
        # del list_pt[:]
        # list_pt.clear()

    def removeSel(self,point):
        if point not in self.m_select:
            return
        self.m_select.remove(point)
        pt_select=tools_basic.getPoint(self.m_self,'m_select','list')
        tools_basic.setPointByFormat(pt_select,'list.remove',point)
        # if point not in self.m_select:
        #     return
        # i=self.m_select.index(point)
        # self.popSel(i)

    def popSel(self):
        self.m_select.pop()
        pt_select=tools_basic.getPoint(self.m_self,'m_select','list')
        tools_basic.setPointByFormat(pt_select,'list.pop')
        # self.m_select.pop(i)
        # list_pt=self.m_sysDict['selection']
        # sel=list_pt.pop(i)
        # sel.delete()
        # del sel

    def movePoints(self,list_pt,pos):
        if list_pt==[]:
            return
        pos0=list_pt[-1].m_pos
        pos1=self.screenPos2WorldPos(pos)
        dx=pos1[0]-pos0[0]
        dy=pos1[1]-pos0[1]
        for point in list_pt:
            point.m_pos[0]+=dx
            point.m_pos[1]+=dy

    def connectPoints(self,anchor,list_pt,mode):
        if list_pt==[]:
            return
        for connect in list_pt:
            if mode==1:
                connect.disconnect_i(0)
                if anchor!=None:
                    connect.connect(anchor,0)
            elif mode==2:
                connect.disconnect_i(1)
                if anchor!=None:
                    connect.connect(anchor,1)

    def keyPressEvent(self, event):
        if event.key()==Qt.Key_Up:
            self.m_worldOrigin[1]-=1
        elif event.key()==Qt.Key_Down:
            self.m_worldOrigin[1]+=1
        elif event.key()==Qt.Key_Right:
            self.m_worldOrigin[0]+=1
        elif event.key()==Qt.Key_Left:
            self.m_worldOrigin[0]-=1
        elif event.key()==Qt.Key_PageUp:
            self.m_unit+=1
        elif event.key()==Qt.Key_PageDown:
            self.m_unit-=1
        elif event.key()==Qt.Key_Q:
            self.m_mode=0
            # self.m_select.clear()
            self.clearSel()
        elif event.key()==Qt.Key_L:
            if self.m_mode!=1:
                self.m_mode=1
            else:
                self.m_mode=0
        elif event.key()==Qt.Key_R:
            if self.m_mode!=2:
                self.m_mode=2
            else:
                self.m_mode=0
        self.update()
        

    



if __name__=='__main__':
    app=QApplication(sys.argv)
    window=Brain('Draw')
    sys.exit(app.exec_())