import sys
if __name__=='__main__':
    sys.path.append(sys.path[0]+'\\..')
from body.bone import NetP
from body.body_lib import Library
from tools import tools_acts, tools_parsers, tools_basic

class Pool:
    def __init__(self,point=None):
        super().__init__()

        self.m_self=None

        self.m_sysPool=[]
        self.m_pool=[]
        self.m_outDev=[]
        self.m_inDev=[]

        self.m_lib=None
        self.m_contain=None

        self.initialize(point)

    def initialize(self,point):
        if point==None:
            point=NetP('pool')
        self.m_self=point
        point.m_dev=self
        point.m_permission=0

        pt_lib=tools_basic.getPoint(point,'m_lib','actions')
        pt_contain=tools_basic.getPoint(point,'m_contain','points')
        pt_pool=tools_basic.getPoint(point,'m_pool','list')

        pt_lib.m_permission=0
        pt_contain.m_permission=0
        pt_pool.m_permission=0

        self.m_lib=Library(pt_lib)
        self.m_contain=pt_contain
        self.m_pool=tools_basic.getPointByFormat(pt_pool,'list')



    def register(self,dev_pt,mode=2):
        if dev_pt.m_dev==None:
            return
        else:
            device=dev_pt.m_dev
        if mode==0 or mode==2:
            if device not in self.m_outDev:
                self.m_outDev.append(device)
                device.m_inPool=self
                con=NetP('output')
                con.con(self.m_self,dev_pt)
                # self.m_sysPool.append(con)
        if mode==1 or mode==2:
            if device not in self.m_inDev:
                self.m_inDev.append(device)
                device.m_outPool=self
                con=NetP('input')
                con.con(self.m_self,dev_pt)
                # self.m_sysPool.append(con)

    def signout(self,dev_pt,mode=2):
        if dev_pt.m_dev==None:
            return
        else:
            device=dev_pt.m_dev
        if mode==0 or mode==2:
            if device in self.m_outDev:
                self.m_outDev.remove(device)
                device.m_inPool=None
                for con in self.m_self.m_con:
                    if con.m_name=='output' and con.m_db[1]==device:
                        con.delete()
                        # self.m_sysPool.remove(con)
                        del con
                        break
        if mode==1 or mode==2:
            if device in self.m_inDev:
                self.m_inDev.remove(device)
                device.m_outPool=None
                for con in self.m_self.m_con:
                    if con.m_name=='input' and con.m_db[1]==device:
                        con.delete()
                        # self.m_sysPool.remove(con)
                        del con
                        break

    def update(self):
        for device in self.m_outDev:
            device.update()

    def input(self,points,mode=1):
        if points==[]:
            return
        pt_pool=tools_basic.getPoint(self.m_self,'m_pool','list')
        points_new=[]
        origin=None
        for pt in self.m_pool:
            if pt.m_name=='诞生地':
                origin=pt
                break
        for point in points:
            if point not in self.m_pool:
                points_new.append(point)
                if origin!=None:
                    point.m_pos=origin.m_pos.copy()
        self.m_pool+=points_new
        tools_basic.setPointByFormat(pt_pool,'list.+=',points_new)
        if points_new!=[]:
            if mode==1:
                self.operate(points_new)
            self.update()

    def saveContain(self,action):
        list_pt=[]
        for pt in self.m_pool:
            if pt.m_permission!=0 and pt!=action:
                if pt.m_db[0]!=None and pt.m_db[0].m_permission==0:
                    continue
                if pt.m_db[1]!=None and pt.m_db[1].m_permission==0:
                    continue
                list_pt.append(pt)
        text=tools_basic.writeStdCode([],list_pt)
        self.m_contain.m_text=text

    def restoreContain(self,action):
        pt_pool=tools_basic.getPoint(self.m_self,'m_pool','list')
        list_pt=[]
        for pt in self.m_pool:
            if pt.m_permission!=0 and pt!=action:
                if pt.m_db[0]!=None and pt.m_db[0].m_permission==0:
                    continue
                if pt.m_db[1]!=None and pt.m_db[1].m_permission==0:
                    continue
                list_pt.append(pt)
        for pt in list_pt:
            tools_basic.setPointByFormat(pt_pool,'list.remove',pt)
            self.m_pool.remove(pt)
            pt.delete()
        del list_pt[:]
        list_pt=tools_basic.buildPoints_tokener(self.m_contain.m_text)
        tools_basic.setPointByFormat(pt_pool,'list.+=',list_pt)
        self.m_pool+=list_pt


    def renew(self,points):
        pt_pool=tools_basic.getPoint(self.m_self,'m_pool','list')
        tools_basic.setPointByFormat(pt_pool,'list.clear')
        self.m_pool.clear()
        self.input(points)

    def clear(self):
        pt_pool=tools_basic.getPoint(self.m_self,'m_pool','list')
        tools_basic.setPointByFormat(pt_pool,'list.clear')
        self.m_pool.clear()
        self.update()

    def close(self):
        self.clear()
        for device in self.m_outDev:
            self.signout(device)
        for device in self.m_inDev:
            self.signout(device)

    def divPts(self,points):
        actions=[]
        outputs=[]
        for point in points:
            if point.m_creator==None and point.m_needed!=None:
                # point.print()
                actions.append(point)
            else:
                outputs.append(point)
        return actions,outputs
    
    def printActionStack(self,actions,pop_ac):
        print('Pop:',pop_ac.info())
        print('Action Stack:')
        tools_basic.printPtList(actions)
        print()


    def operate(self,points):
        actions,outputs=self.divPts(points)
        self.input(outputs,0)
        pt_pool=tools_basic.getPoint(self.m_self,'m_pool','list')

        while len(actions)>0:
            action=actions.pop()
            # self.printActionStack(actions,action)
            if action.m_name=='[删除]' or action.m_name=='[del]':
                obj=None
                if action.m_db[1]!=None and action.m_db[1].m_permission!=0:
                    obj=action.m_db[1]
                    print('删除\"'+obj.info(1)+'\"')
                action.con(None,None)
                if obj in self.m_pool:
                    tools_basic.setPointByFormat(pt_pool,'list.remove',obj)
                    obj.delete()
                    self.m_pool.remove(obj)
                if obj in outputs:
                    obj.delete()
                    outputs.remove(obj)
            elif action.m_name=='[左连]' or action.m_name=='[lt_connect]':
                sbj=action.m_db[0]
                obj=action.m_db[1]
                action.con(None,None)
                if sbj!=None and sbj.m_permission!=0:
                    sbj.disconnect_i(0)
                    if obj!=None:
                        sbj.connect(obj,0)
            elif action.m_name=='[右连]' or action.m_name=='[rt_connect]':
                sbj=action.m_db[0]
                obj=action.m_db[1]
                action.con(None,None)
                if sbj!=None and sbj.m_permission!=0:
                    sbj.disconnect_i(1)
                    if obj!=None:
                        sbj.connect(obj,1)
            elif action.m_name=='[写入]' or action.m_name=='[write]':
                sbj=action.m_db[0]
                obj=action.m_db[1]
                action.con(None,None)
                if sbj!=None and obj!=None:
                    obj.m_name=sbj.m_name
                    obj.m_text=sbj.m_text
            elif action.m_name=='[检查连接节点]':
                obj=action.m_db[1]
                action.con(None,None)
                if obj!=None:
                    list_pt=[]
                    for con in obj.m_con:
                        if con.m_permission!=0:
                            list_pt.append(con)
                    if list_pt!=[]:
                        print(obj.info()+'的连接节点:')
                        tools_basic.printPtList(list_pt)
                        self.input(list_pt,0)
            elif action.m_name=='[推入]' or action.m_name=='[push]':
                obj=action.m_db[1]
                action.con(None,None)
                if obj!=None and obj not in self.m_pool:
                    tools_basic.setPointByFormat(pt_pool,'list.append',obj)
                    self.m_pool.append(obj)
            elif action.m_name=='[弹出]' or action.m_name=='[pop]':
                obj=action.m_db[1]
                action.con(None,None)
                if obj!=None and obj in self.m_pool:
                    tools_basic.setPointByFormat(pt_pool,'list.remove',obj)
                    self.m_pool.remove(obj)
            elif action.m_name=='[移动到]' or action.m_name=='[moveTo]':
                sbj=action.m_db[0]
                obj=action.m_db[1]
                action.con(None,None)
                if sbj!=None and obj!=None:
                    sbj.m_pos[0]=obj.m_pos[0]
                    sbj.m_pos[1]=obj.m_pos[1]
            elif action.m_name=='[载入]' or action.m_name=='[load]':
                obj=action.m_db[1]
                action.con(None,None)
                if obj!=None:
                    self.m_lib.loadLib(obj.m_name)
                    obj.delete()
                    if obj in self.m_pool:
                        tools_basic.setPointByFormat(pt_pool,'list.remove',obj)
                        self.m_pool.remove(obj)
                    if obj in outputs:
                        outputs.remove(obj)
                elif action.m_text!='':
                    self.m_lib.loadLib(action.m_text)
            elif action.m_name=='[打开]' or action.m_name=='[open]':
                obj=action.m_db[1]
                action.con(None,None)
                if obj!=None:
                    tools_acts.openFile(obj.m_name)
            elif action.m_name=='[显示函数库]':
                self.m_lib.print()
                action.con(None,None)
            elif action.m_name=='[显示节点]':
                obj=action.m_db[1]
                action.con(None,None)
                if obj!=None:
                    print(obj.info(1))
            elif action.m_name=='[上点]' or action.m_name=='[up]':
                sbj=action.m_db[0]
                action.con(None,None)
                if sbj!=None:
                    action.m_pos[0]=sbj.m_pos[0]
                    action.m_pos[1]=sbj.m_pos[1]-1
            elif action.m_name=='[下点]' or action.m_name=='[down]':
                sbj=action.m_db[0]
                action.con(None,None)
                if sbj!=None:
                    action.m_pos[0]=sbj.m_pos[0]
                    action.m_pos[1]=sbj.m_pos[1]+1
            elif action.m_name=='[左点]' or action.m_name=='[left]':
                sbj=action.m_db[0]
                action.con(None,None)
                if sbj!=None:
                    action.m_pos[0]=sbj.m_pos[0]-1
                    action.m_pos[1]=sbj.m_pos[1]
            elif action.m_name=='[右点]' or action.m_name=='[right]':
                sbj=action.m_db[0]
                action.con(None,None)
                if sbj!=None:
                    action.m_pos[0]=sbj.m_pos[0]+1
                    action.m_pos[1]=sbj.m_pos[1]
            elif action.m_name=='[显示器]' or action.m_name=='[命令行]' or action.m_name=='[调试器]' \
                or action.m_name=='[Brain]' or action.m_name=='[Mouth]' or action.m_name=='[Hand]':
                tools_acts.createDev(action)
                action.m_name=action.m_name[1:-1]
                action.m_creator='System'
            elif action.m_name=='[更新设备]' or action.m_name=='[updateDev]':
                obj=action.m_db[1]
                action.con(None,None)
                if obj!=None:
                    tools_acts.updateDev(obj)
            elif action.m_name=='[输入端接入]':
                if action.m_db[0]==self.m_self:
                    self.register(action.m_db[1],1)
                action.con(None,None)
            elif action.m_name=='[输出端接入]':
                if action.m_db[0]==self.m_self:
                    self.register(action.m_db[1],0)
                action.con(None,None)
            elif action.m_name=='[输入端拔出]':
                if action.m_db[0]==self.m_self:
                    self.signout(action.m_db[1],1)
                action.con(None,None)
            elif action.m_name=='[输出端拔出]':
                if action.m_db[0]==self.m_self:
                    self.signout(action.m_db[1],0)
                action.con(None,None)
            elif action.m_name=='[清空词条]' or action.m_name=='[clearTerm]':
                obj=action.m_db[1]
                action.con(None,None)
                if obj!=None and obj.m_dev!=None:
                    obj.m_dev.clearTerm()
                    print(obj.m_dev.info())
            elif action.m_name=='[导入词条]' or action.m_name=='[loadTerm]':
                obj=action.m_db[1]
                code=action.m_text
                action.con(None,None)
                if obj!=None and code!='':
                    obj.m_dev.loadTerm(code)
                    print(obj.m_dev.info())
            elif action.m_name=='[编辑文本]':
                sbj=action.m_db[0]
                obj=action.m_db[1]
                action.con(None,None)
                if obj!=None and sbj!=None and sbj.m_dev!=None:
                    sbj.m_dev.setReadPtr(obj)
            elif action.m_name=='[保存内景节点]' or action.m_name=='[savePool]':
                self.saveContain(action)
            elif action.m_name=='[恢复内景节点]' or action.m_name=='[loadPool]':
                self.restoreContain(action)
            elif action.m_name=='[生成算式]':
                obj=action.m_db[1]
                if obj!=None and obj.m_text!=None:
                    points_new=tools_parsers.eqn2struct(obj.m_text)
                    if points_new!=[]:
                        outputs+=points_new
                        self.input(points_new,0)
                        obj.connect(points_new[0],1)
                action.con(None,None)
            elif action.m_name=='[显示算式]':
                obj=action.m_db[1]
                action.con(None,None)
                if obj!=None:
                    str_eqn=tools_parsers.struct2Eqn(obj)
                    print(str_eqn)
            elif action.m_name=='[打开smilei]':
                points_new=tools_parsers.Smilei2struct(action.m_text)
                if points_new!=[]:
                    outputs+=points_new
                    self.input(points_new,0)
                action.con(None,None)
            else:
                points_new=self.m_lib.transfer(action)
                actions_new,outputs_new=self.divPts(points_new)
                actions+=actions_new
                outputs+=outputs_new
                self.input(outputs_new,0)
            if action in self.m_pool:
                action.con(None,None)
                tools_basic.setPointByFormat(pt_pool,'list.remove',action)
                self.m_pool.remove(action)

        return outputs

    def info(self):
        info_str=''
        for point in self.m_pool:
            info_str+=point.info()+'\n'
        return info_str

    def printSysPool(self):
        print('==============================')
        print('System pool:')
        for con in self.m_self.m_con:
            con.print()
        print('==============================')





if __name__=='__main__':
    interior=Pool()
    list_pt=NetP('').build('a(,)[1,2];b(,)[4,4];c(a,b)[2,3]')
    interior.m_pool=list_pt