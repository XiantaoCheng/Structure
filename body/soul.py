import sys
import re
if __name__=='__main__':
    sys.path.append(sys.path[0]+'\\..')
from body.bone import NetP

def dictToList(dict_pt):
    list_pt=[]
    for term in dict_pt:
        list_pt+=dict_pt[term]
    return list_pt

class Karma:
    def __init__(self,symbol):
        self.m_symbol=symbol
        symbol.m_master=self

        self.m_map=None

        self.m_cause=None
        self.m_yese=[]
        self.m_noe=[]
        self.m_yesAnd=False
        self.m_noAnd=False

        self.m_clause=[]
        self.m_clauseAnd=True

        self.m_not=False
        self.m_no=False
        
        self.m_buildMode=False

        self.m_listMP=[]
        self.m_restricted=False

        self.m_ranger=None
        self.m_rangType=False                               # connecting---True, connected---False

        # one step
        self.m_stage=0
        self.m_reState=''
        self.m_choose=True
        self.m_interp=False

    def stateSelf(self):
        if self.m_interp==True:
            return 'blue'
        if self.m_symbol==None or self.m_map==None:
            return 'yellow'

        # [eq](,) and [is](,) function points
        if self.m_symbol.m_name=='[eq]' or self.m_symbol.m_name=='[同名]':
            return self.stateSelf_eq()
        elif self.m_symbol.m_name=='[is]' or self.m_symbol.m_name=='[是]':
            return self.stateSelf_is()

        # _re"^.*"(,) regular expression
        if self.m_symbol.m_name=='_正则表达式' or self.m_symbol.m_name=='_re':
            try:
                pattern=re.compile(self.m_symbol.m_text)
            except:
                print('Invalid regular expression: '+self.m_symbol.m_text+'!')
                return 'red'
            match=self.m_map.m_name
            if pattern.findall(match)!=[]:
                return 'green'
            else:
                return 'red'

        # _word(,)
        if self.m_symbol.m_name!='' and self.m_symbol.m_name[0]=='_':
            return 'green'

        # [word](,)
        if self.m_symbol.m_name!='' and self.m_symbol.m_name[0]=='[' and self.m_symbol.m_name[-1]==']':
            name1=self.m_symbol.m_name[1:-1]
            name2=self.m_symbol.m_name
            if self.m_interp==False and self.m_map.m_creator==None and self.m_buildMode==False:
                return 'red'
            if name1==self.m_map.m_name or name2==self.m_map.m_name:
                return 'green'
            else:
                return 'red'

        # ~word(,)
        if self.m_symbol.m_name!='' and self.m_symbol.m_name[0]=='~':
            name=self.m_symbol.m_name[1:]
            if name==self.m_map.m_name:
                return 'red'
            else: 
                return 'green'
        # word(,)
        else:
            name=self.m_map.m_name
            if name!='' and name[0]=='[' and name[-1]==']':
                name=name[1:-1]
            if name!=self.m_symbol.m_name:
                return 'red'
            else:
                return 'green'

    def stateSelf_eq(self):
        if self.m_map==None:
            return 'yellow'
        if self.m_symbol.m_db[0]==None or self.m_symbol.m_db[1]==None:
            return 'red'
        
        karmaL=self.m_symbol.m_db[0].m_master
        karmaR=self.m_symbol.m_db[1].m_master
        if karmaL.m_map==None or karmaR.m_map==None:
            return 'green'
        else:
            if karmaL.m_map.m_name==karmaR.m_map.m_name:
                return 'green'
            else:
                return 'red'

    def stateSelf_is(self):
        if self.m_map==None:
            return 'yellow'
        if self.m_symbol.m_db[0]==None or self.m_symbol.m_db[1]==None:
            return 'red'
        
        karmaL=self.m_symbol.m_db[0].m_master
        karmaR=self.m_symbol.m_db[1].m_master
        if karmaL.m_map==None or karmaR.m_map==None:
            return 'green'
        else:
            if karmaL.m_map==karmaR.m_map:
                return 'green'
            else:
                return 'red'
    
    def stateRelation(self):
        if self.m_map==None or self.m_symbol==None:
            return True
            
        cause=self.m_cause
        while cause!=None:
            if cause.m_symbol==self.m_symbol.m_db[0]:
                if cause.m_map!=self.m_map.m_db[0]:
                    return False
            if cause.m_symbol==self.m_symbol.m_db[1]:
                if cause.m_map!=self.m_map.m_db[1]:
                    return False

            # For a function point, you should check the relation between the point through the function point selfstate()
            if cause.m_symbol.m_db[0]==self.m_symbol:
                if cause.m_map.m_db[0]!=self.m_map or cause.stateSelf()=='red':
                    return False
            if cause.m_symbol.m_db[1]==self.m_symbol:
                if cause.m_map.m_db[1]!=self.m_map or cause.stateSelf()=='red':
                    return False

            cause=cause.m_cause
        
        return True

    def newMap(self,pool,areaType,list_new):
        if self.m_restricted==True:                                                                                     # restrict the map pool by m_listMP
            list_map=self.m_listMP
        elif self.m_ranger!=None and self.m_ranger.buildingNewMap()==False:                                                  # restrict the map pool by m_cause
            if self.m_rangType==True:
                if self.m_ranger.m_map==None or self.m_ranger.m_map.m_con==[]:
                    list_map=dictToList(pool)
                else:
                    list_map=self.m_ranger.m_map.m_con.copy()
            elif self.m_ranger.m_symbol.m_db[0]!=None and self.m_ranger.m_symbol.m_db[0]==self.m_symbol:
                if self.m_ranger.m_map.m_db[0]==None:
                    list_map=dictToList(pool)
                else:
                    list_map=[self.m_ranger.m_map.m_db[0]]
            else:
                if self.m_ranger.m_map.m_db[1]==None:
                    list_map=dictToList(pool)
                else:
                    list_map=[self.m_ranger.m_map.m_db[1]]
        elif self.selfType()=='实万用链节' or self.selfType()=='实否定链节':                                                 # '_point' and '' aren't restricted
            list_map=dictToList(pool)
            if len(self.m_symbol.m_name)>2 and self.m_symbol.m_name[1]=='_':
                for mp in list_map:
                    if mp in list_new:
                        list_map.remove(mp)
        else:
            list_map=dictToList(pool)
            # list_map=pool.get(self.m_symbol.m_name,[])
        # print('pool:',pool)
        if self.m_buildMode==False or areaType==False:
            name=self.m_symbol.m_name
            # function points
            if self.isFunctionPoint()==1:
                if self.m_map==None:
                    point=NetP(name,self.m_symbol.m_text)
                    point.m_needed=self
                    point.m_creator=self
                    self.map(point)
                else:
                    self.m_map.delete()
                    del self.m_map
                    self.map(None)
                return
            elif self.isFunctionPoint()==2:
                # function points [P] don't find map from pool
                if self.m_map==None:
                    point=NetP(name,self.m_symbol.m_text)
                    point.m_needed=self
                    self.map(point)
                    self.m_interp=True
                else:
                    self.m_map.delete()
                    self.m_map=m_needed=None
                    self.map(None)
                return

            # only take real points when karma is start with _ and ~
            list_have=[]
            for point in list_map:
                if self.selfType()=='实万用链节' or self.selfType()=='实否定链节':
                    if point.m_creator!=None or point.m_needed==None:
                        list_have.append(point)
                    # else:
                    #     pass
                        # print('Erased from map_list:',point.info(),', it should be an imagine point.')
                else:
                    list_have.append(point)
            mp=self.m_map
            self.map(self.nextInlist(mp,list_have))
            return
        else:
            name=self.m_symbol.m_name
            # answer questions
            # +word(,)
            if name!='' and (name[0]!='[' or name[-1]!=']'):
                if self.m_map!=None:
                    self.m_map.m_creator=None
                    if self.m_map.m_needed==None:
                        self.m_map.delete()
                        self.map(None)
                        return
                    else:
                        self.m_map.m_name='['+self.m_map.m_name+']'
                list_need=[]
                for point in list_map:
                    if point.m_creator==None and point.m_needed!=None:
                        list_need.append(point)
                point=self.m_map
                self.map(self.nextInlist(point,list_need))
                if self.m_map==None:
                    if self.m_restricted==True:
                        self.map(None)
                        return
                    point=NetP(self.m_symbol.m_name,self.m_symbol.m_text)
                    self.map(point)
                else:
                    self.m_map.m_name=self.m_map.m_name[1:-1]
                self.m_map.m_creator=self
                return
            # +[word](,)
            else:
                if self.m_map==None:
                    point=NetP(name,self.m_symbol.m_text)
                    point.m_needed=self
                    self.map(point)
                    return
                else:
                    self.m_map.m_needed=None
                    self.m_map.delete()
                    self.map(None)
                    return

        self.map(None)


    def nextInlist(self,point,list_pt):
        if list_pt==[]:
            return None
        if point==None:
            return list_pt[0]
        
        try:
            i=list_pt.index(point)
        except:
            return None
        
        if i+1>=len(list_pt):
            return None
        else:
            return list_pt[i+1]

    def map(self,point):
        self.m_map=point
        self.m_stage=0
        self.m_interp=False
        self.m_reState=''
        self.m_choose=True
        for clause in self.m_clause:
            clause.map(None)
        for end in self.m_noe:
            end.map(None)
        for end in self.m_yese:
            end.map(None)
        
        if self.m_map!=None:
            cause=self.m_cause
            while cause!=None:
                # function relation points
                if cause.needBuildRelation():
                    if cause.m_map.m_needed==None or cause.m_map.m_needed==cause:
                        if cause.m_symbol.m_db[0]==self.m_symbol:
                            cause.m_map.connect(self.m_map,0)
                        if cause.m_symbol.m_db[1]==self.m_symbol:
                            cause.m_map.connect(self.m_map,1)
                if self.needBuildRelation():
                    if self.m_map.m_needed==None or self.m_map.m_needed==self:
                        if self.m_symbol.m_db[0]==cause.m_symbol:
                            self.m_map.connect(cause.m_map,0)
                        if self.m_symbol.m_db[1]==cause.m_symbol:
                            self.m_map.connect(cause.m_map,1)
                cause=cause.m_cause

    def buildingNewMap(self):
        if self.m_map==None:
            return False
        elif self.m_buildMode==False:
            return False
        elif self.m_map.m_needed==None:
            return True
        return False

    def needBuildRelation(self):
        if self.buildingNewMap():
            return True
        elif self.isFunctionPoint()!=0:
            return True
        return False
    
    def selfType(self):
        name=self.m_symbol.m_name
        if name=='':
            return "实链节"
        elif name[0]=='_':
            return "实万用链节"
        elif name[0]=='~':
            return "实否定链节"
        elif name[0]=='[' and name[-1]==']':
            return "虚链节"
        return "实链节"

    def isFunctionPoint(self):
        if self.m_symbol.m_name=='':
            return 0
        elif self.m_symbol.m_name=='[eq]' or self.m_symbol.m_name=='[同名]':
            return 1
        elif self.m_symbol.m_name=='[is]' or self.m_symbol.m_name=='[是]':
            return 1
        elif self.m_symbol.m_name=='[]':
            return 1
        elif self.m_symbol.m_name[0]=='[' and self.m_symbol.m_name[-1]==']':
            return 2
        return 0

    def Reason_iterative(self,pool,show=False,order=None,list_new=None,areaType=True):
        # order records the order of mapping.
        if list_new==None:
            list_new=[]
        if self.m_no==True:
            areaType=not areaType
        if order!=None:
            order.append([order[-1][0]+1,self.m_symbol.m_name])
            #print(order)
        while True:
            #Stage 1
            self.m_stage=1
            self.m_reState=''
            if show:
                print('Begin:')
                print(self.m_symbol.m_name)
            self.newMap(pool,areaType,list_new)
            if show and self.m_map!=None:
                print('\''+self.m_symbol.m_name+'\''+'Stage 0: Have a new map(',self.stateSelf(),')')
                print(self.m_map,':',self.m_map.m_name)
            if self.stateRelation()==False:
                continue
            if self.stateSelf()=='red':
                continue
            if self.stateSelf()=='yellow':
                if show:
                    print('\''+self.m_symbol.m_name+'\''+'Stage 3: Output final state:')
                    if self.m_no==False:
                        print('dark yellow')
                    else:
                        print('dark green')
                if self.m_no==False:
                    self.m_stage=5
                    self.m_reState='dark yellow'
                    return ['dark yellow',pool,list_new]
                else:
                    self.m_stage=5
                    self.m_reState='dark green'
                    return ['dark green',pool,list_new]
            if show:
                print('\''+self.m_symbol.m_name+'\''+'Stage 1: Check map state:')
                print(self.stateSelf())

            # Stage 2
            self.m_stage=2
            self.m_reState=''
            if self.m_clause==[]:
                choose=True
            else:
                choose=self.m_clauseAnd
            for clause in self.m_clause:
                [state_re,pool,list_new]=clause.Reason_iterative(pool,show,order,list_new,areaType)
                if order!=None:
                    order.append([order[-1][0]-1,self.m_symbol.m_name])
                if self.m_clauseAnd==True:
                    if state_re=='dark yellow':
                        choose=False
                        break
                else:
                    if state_re=='dark green':
                        choose=True
                        break
            
            if show:
                print('\''+self.m_symbol.m_name+'\''+'Stage 2: Choose No-end or Yes-end:')
                if choose:
                    print('Yes')
                else:
                    print('No')

            # Stage 3
            self.m_stage=3
            self.m_reState=''
            if choose==False:
                if self.m_noe!=[]:
                    result=self.m_noAnd
                    for end in self.m_noe:
                        [state_re,pool,list_new]=end.Reason_iterative(pool,show,order,list_new,areaType)
                        if order!=None:
                            order.append([order[-1][0]-1,self.m_symbol.m_name])

                        if self.m_noAnd==True:
                            if state_re=='dark yellow':
                                result=False
                                break
                        else:
                            if state_re=='dark green':
                                result=True
                                break
                else:
                    result=False

                if result==False:
                    continue

            if choose==True:
                if self.m_yese!=[]:
                    result=self.m_yesAnd
                    for end in self.m_yese:
                        [state_re,pool,list_new]=end.Reason_iterative(pool,show,order,list_new,areaType)
                        if order!=None:
                            order.append([order[-1][0]-1,self.m_symbol.m_name])
                        if self.m_yesAnd==True:
                            if state_re=='dark yellow':
                                result=False
                                break
                        else:
                            if state_re=='dark green':
                                result=True
                                break
                elif self.m_noe!=[]:
                    result=False
                else:
                    result=True

                if result==False:
                    continue

            if show:
                print('\''+self.m_symbol.m_name+'\''+'Stage 3: Output final state:')
                if self.m_no:
                    print('dark yellow')
                else:
                    print('dark green')
            

            #Stage 4
            self.m_stage=4
            self.m_reState=''
            if self.m_buildMode==True and self.m_map!=None:
                list_pt=pool.get(self.m_map.m_name,[])
                list_pt.append(self.m_map)
                pool.update({self.m_map.m_name:list_pt})
                list_new.append(self.m_map)

            if self.m_no==True:
                self.m_stage=5
                self.m_reState='dark yellow'
                return ['dark yellow',pool,list_new]
            else:
                self.m_stage=5
                self.m_reState='dark green'
                return ['dark green',pool,list_new]

    def isChosen(self):
        if self.m_cause==None:
            return False
        if self.m_cause.m_choose==False:
            return self in self.m_cause.m_noe
        else:
            return self in self.m_cause.m_yese

    def Reason_oneStep(self,pool):
        list_new=[]
        areaType=self.areaType()
        change=False
        
        if self.m_stage==0:
            if self.m_cause!=None:
                if self in self.m_cause.m_clause:
                    if self.m_cause.m_stage==2:
                        self.m_stage=1
                        change=True
                else:
                    if self.m_cause.m_stage==3 and self.isChosen():
                        self.m_stage=1
                        change=True
                        # print(self.m_symbol.info(),'start!','The choose of the cause is:',self.m_cause.m_choose)

        if self.m_stage==1:
            while True:
                if self.stateSelf()!='blue':
                    self.newMap(pool,areaType,list_new)
                else:
                    self.m_interp=False
                # if self.m_map!=None:
                #     print('Map:',self.m_map.info(),self.stateSelf())
                change=True
                if self.stateRelation()==False:
                    continue
                elif self.stateSelf()=='red':
                    continue
                elif self.stateSelf()=='yellow':
                    self.m_stage=5
                    if self.m_no==False:
                        self.m_reState='dark yellow'
                        return [change,list_new]
                    else:
                        self.m_reState='dark green'
                        return [change,list_new]
                elif self.stateSelf()=='blue':
                    self.m_stage=1
                    return [change,list_new]
                else:
                    self.m_stage=2
                    break

        if self.m_stage==2:
            if self.m_clause==[]:
                self.m_choose=True
                self.m_stage=3
                change=True
            else:
                self.m_choose=self.m_clauseAnd
                keep=False
            for clause in self.m_clause:
                if self.m_clauseAnd==True:
                    if clause.m_reState=='dark yellow':
                        self.m_choose=False
                        self.m_stage=3
                        change=True
                        break
                    elif clause.m_reState=='':
                        keep=True
                else:
                    if clause.m_reState=='dark green':
                        self.m_choose=True
                        self.m_stage=3
                        change=True
                        break
                    elif clause.m_reState=='':
                        keep=True
            if self.m_clause!=[] and keep==False:
                self.m_stage=3
                change=True

        if self.m_stage==3:
            # print(self.m_symbol.info(),'End type:',self.m_yesAnd)
            if self.m_choose==False:
                if self.m_noe==[]:
                    self.m_stage=1
                    change=True
                    return [change,list_new]
                keep=False
                for end in self.m_noe:
                    if end.m_reState=='':
                        keep=True
                    elif self.m_noAnd==True:
                        if end.m_reState=='dark yellow':
                            self.m_stage=1
                            change=True
                            return [change,list_new]
                    else:
                        if end.m_reState=='dark green':
                            self.m_stage=4
                            change=True
                            break
                if self.m_stage==3 and keep==False:
                    if self.m_noAnd==True:
                        self.m_stage==4
                        change=True
                    else:
                        self.m_stage=1
                        change=True
                        return [change,list_new]
            else:
                if self.m_yese==[] and self.m_noe==[]:
                    self.m_stage=4
                    change=True
                elif self.m_yese==[]:
                    self.m_stage=1
                    change=True
                    return [change,list_new]
                else:
                    keep=False
                    for end in self.m_yese:
                        if end.m_reState=='':
                            keep=True
                        elif self.m_yesAnd==True:
                            if end.m_reState=='dark yellow':
                                self.m_stage=1
                                change=True
                                return [change,list_new]
                        else:
                            if end.m_reState=='dark green':
                                self.m_stage=4
                                change=True
                                break
                    if keep==False and self.m_stage==3:
                        if self.m_yesAnd:
                            self.m_stage=4
                            change=True
                        else:
                            self.m_stage=1
                            change=True
                            return [change,list_new]

        if self.m_stage==4:
            if (self.m_buildMode==True or self.isFunctionPoint()==1) and self.m_map!=None:
                list_new.append(self.m_map)
            self.m_stage=5
            if self.m_no==True:
                self.m_reState='dark yellow'
                change=True
                return [change,list_new]
            else:
                self.m_reState='dark green'
                change=True
                return [change,list_new]

        return [change,list_new]

    def areaType(self):
        aType=True
        cause=self
        while True:
            if cause.m_no==True:
                aType=not aType
            if cause.m_cause==None:
                return aType
            else:
                cause=cause.m_cause
        

    def build(self,code,points):
        wait_list=[]
        last=self
        connection=None
        exp='(->>|=>>|->|=>|{[ \t\n]*|[ \t\n]*}|,[ \t\n]*|;[ \t\n]*|:[ \t\n]*)'
        units=re.split(exp,code)
        for unit in units:
            if unit=='':
                continue
            elif unit=='->' or unit=='=>' or unit=='->>' or unit=='=>>':
                connection=unit
            elif unit[0]=='{':
                wait_list.append(['clause_splitting',last])
            elif unit[0]==':':
                wait_list.append(['end_splitting',last])
            elif unit[0]==',':
                last=wait_list[-1][1]
            elif unit[0]==';':
                if wait_list[-1][0]=='end_splitting':
                    wait_list.pop()
                if wait_list!=[]:
                    last=wait_list[-1][1]
            elif unit[-1]=='}':
                last=wait_list[-1][1]
                wait_list.pop()
            else:
                current=Karma(points[int(unit)])
                current.m_cause=last
                if connection=='->':
                    current.m_no=False
                    last.m_yese.append(current)
                elif connection=='->>':
                    current.m_no=False
                    last.m_noe.append(current)
                elif connection=='=>':
                    current.m_no=True
                    last.m_yese.append(current)
                elif connection=='=>>':
                    current.m_no=True
                    last.m_noe.append(current)
                else:
                    last.m_clause.append(current)
                connection=''
                last=current
            print(wait_list)

    def info_cause(self):
        info=''
        karma=self
        while True:
            if karma.m_symbol!=None:
                info=karma.m_symbol.m_name+info
            if karma.m_cause==None:
                break
            if karma in karma.m_cause.m_yese:
                if karma.m_no==True:
                    info='=>'+info
                else:
                    info='->'+info
            elif karma in karma.m_cause.m_noe:
                if karma.m_no==True:
                    info='=>>'+info
                else:
                    info='->>'+info
            elif karma in karma.m_cause.m_clause:
                info='=='+info
            karma=karma.m_cause
        print(info)
        return info

    def allEffects(self):
        list_effects=[self]
        for karma in self.m_clause:
            list_effects+=karma.allEffects()
        for karma in self.m_noe:
            list_effects+=karma.allEffects()
        for karma in self.m_yese:
            list_effects+=karma.allEffects()
        # list_effects.append(self)
        return list_effects

    def setAllBuildMode(self,mode,list_km):
        self.m_buildMode=mode
        for point in self.m_symbol.m_con:
            for karma in list_km:
                if karma.m_symbol==point:
                    karma.setAllBuildMode(mode,list_km)

    # one of causes provides map pool for this karma
    def setRangers(self,causes=None):
        connecting=None
        connected=None
        order=0
        if causes==None:
            causes=[]
        # elif self.m_buildMode!=True and self.m_symbol.m_name!='[]' and self.m_symbol.m_name!='[eq]' and self.m_symbol.m_name!='[同名]'\
        #     and self.m_symbol.m_name!='[is]' and self.m_symbol.m_name!='[是]':
        # word(,)
        elif self.m_buildMode!=True and self.isFunctionPoint()==0:
            for cause in causes:
                # [pt]->word
                if cause.isFunctionPoint()!=0:
                    # [pt]->word([pt],)
                    if self.m_symbol.m_db[0]==cause.m_symbol or self.m_symbol.m_db[1]==cause.m_symbol:
                        connecting=cause
                        connected=None
                        break
                elif cause.m_buildMode==True and order<1:
                    # +cause(,self)->self(,)
                    if cause.m_symbol.m_db[0]==self.m_symbol or cause.m_symbol.m_db[1]==self.m_symbol:
                        connected=cause
                        order=1
                    # +cause(,)->self(,cause)
                    elif self.m_symbol.m_db[0]==cause.m_symbol or self.m_symbol.m_db[1]==cause.m_symbol:
                        connecting=cause
                # cause->self
                elif order<2:
                    if cause.m_symbol.m_db[0]==self.m_symbol or cause.m_symbol.m_db[1]==self.m_symbol:
                        connected=cause
                        order=2
                    elif self.m_symbol.m_db[0]==cause.m_symbol or self.m_symbol.m_db[1]==cause.m_symbol:
                        connecting=cause
            if connected!=None:
                self.m_ranger=connected
            elif connecting!=None:
                self.m_ranger=connecting
                self.m_rangType=True
        
        # set next one except for [eq], and buildMode==True
        # if self.m_buildMode!=True and self.m_symbol.m_name!='' and self.m_symbol.m_name!='[eq]' and self.m_symbol.m_name!='[同名]':
        # if self.isFunctionPoint()==0 and self.m_buildMode!=True:
        # if self.isFunctionPoint()==0:                                       # a building point can be a ranger of an another point(Why?)(May because of new point can be a answer point)
        causes=causes[:]+[self]

        for con in self.m_clause:
            # for cause in causes:
            #     cause.m_symbol.print()
            con.setRangers(causes)
        for end in self.m_yese:
            end.setRangers(causes)
        for end in self.m_noe:
            end.setRangers(causes)

    def info_karma(self,info='',head=0):
        if self.m_ranger!=None:
            ranger=self.m_ranger.m_symbol.info(1)
            info+='['+ranger+']'
            head+=len(ranger)+2
        if self.m_buildMode==True:
            info+='+'
            head+=1
            
        info+=self.m_symbol.info(1)
        head+=len(self.m_symbol.info(1))

        if self.m_clause!=[]:
            info+='{'
            head+=1
            for clause in self.m_clause:
                info+='\n'+''.rjust(head)
                info=clause.info_karma(info,head)
            info+='\n'+'}'.rjust(head-1)
        n=0
        for end in self.m_yese:
            if n==0:
                if end.m_no==False:
                    info+='->'
                else:
                    info+='=>'
                info=end.info_karma(info,head+2)
                n+=1
            else:
                if end.m_no==False:
                    info+='\n'+'->'.rjust(head+2)
                else:
                    info+='\n'+'=>'.rjust(head+2)
                info=end.info_karma(info,head)
        for end in self.m_noe:
            if n==0:
                if end.m_no==False:
                    info+='->>'
                else:
                    info+='=>>'
                info=end.info_karma(info,head+3)
                n+=1
            else:
                if end.m_no==False:
                    info+='\n'+'->>'.rjust(head+3)
                else:
                    info+='\n'+'=>>'.rjust(head+3)
                info=end.info_karma(info,head)

        return info
                

        
        




        




if __name__=='__main__':
    points=[NetP('0'),NetP('1'),NetP('2'),NetP('3'),NetP('4'),NetP('5'),NetP('6'),NetP('7'),NetP('8'),NetP('9')]
    test=Karma(NetP('[self]'))
    
    f=open('test\\test.txt')
    code=f.read()
    test.build(code,points)
    points[9].m_master.info_cause()
    list_effect=test.allEffects()
    print(test.info_karma())