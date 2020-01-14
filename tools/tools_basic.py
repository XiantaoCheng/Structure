import sys, re
if __name__=='__main__':
    sys.path.append(sys.path[0]+'\\..')
from body.bone import NetP
from body.soul import Karma


def printNList(list_pt):
    string=''
    n=0
    print(list_pt)
    for point in list_pt:
        string=string+str(n)+'.'+point.info()+'\n'
        n=n+1
    print(string)

def readStdCode(code):
    parts=re.split('[ \t\n]*_{3,}[ \t\n]*',code)
    list_pt=NetP('').build(parts[0])
    parts.pop(0)
    list_km=[]
    for part in parts:
        list_km.append(readStdCode_karma(part,list_pt))
    return [list_km,list_pt]

def readStdCode_karma(code,points):
    wait_list=[]
    last=None
    head=None
    connection=None
    exp='(->>|=>>|->|=>|{[ \t\n]*|[|&]{[ \t\n]*|[ \t\n]*}|,[ \t\n]*|;[ \t\n]*|:[ \t\n]*|[|&]:[ \t\n]*)'
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
        elif unit[0]=='&':
            if unit[1]==':':
                last.m_yesAnd=True
                last.m_noAnd=True
                wait_list.append(['end_splitting',last])
            else:
                last.m_clauseAnd=True
                wait_list.append(['clause_splitting',last])
        elif unit[0]=='|':
            if unit[1]==':':
                last.m_yesAnd=False
                last.m_noAnd=False
                wait_list.append(['end_splitting',last])
            else:
                last.m_clauseAnd=False
                wait_list.append(['clause_splitting',last])
        else:
            current=Karma(points[int(unit)])
            if unit[0]=='+':
                current.m_buildMode=True
            current.m_cause=last
            if connection=='->':
                current.m_no=False
                if last!=None:
                    last.m_yese.append(current)
            elif connection=='->>':
                current.m_no=False
                if last!=None:
                    last.m_noe.append(current)
            elif connection=='=>':
                current.m_no=True
                if last!=None:
                    last.m_yese.append(current)
            elif connection=='=>>':
                current.m_no=True
                if last!=None:
                    last.m_noe.append(current)
            elif last!=None:
                last.m_clause.append(current)
            else:
                head=current
            connection=''
            last=current
    head.setRangers()
    return head


def buildPoint(point_str,recent,undefined):
    aNetPoint=re.compile(r'([\w.,\[\]#=+*\\\-^$_\'~:@/\(\)]*)\(([\w.,\[\]#=+*\\\-^$_\'~:@/\(\)]*), *([\w.,\[\]#=+*\\\-^$_\'~:@/\(\)]*)\)\[([-0-9]+),([-0-9]+)\]')
    aNetPoint2=re.compile(r'([\w.,\[\]#=+*\\\-^$_\'~:@/\(\)]*)\(([\w.,\[\]#=+*\\\-^$_\'~:@/\(\)]*), *([\w.,\[\]#=+*\\\-^$_\'~:@/\(\)]*)\)(?![\[])')
    # selfName=re.compile(r'([\w.,\[\]#=+*\\\-^$_\'~:@/\(\)]*)(?=[\(\[])')
    # con0Name=re.compile(r'\(([\w.,\[\]#=+*\\\-^$_\'~:@/\(\)]*),')
    # con1Name=re.compile(r', *([\w.,\[\]#=+*\\\-^$_\'~:@/\(\)]*)\)')
    # posX=re.compile(r'\[([-0-9]+),')
    # posY=re.compile(r',([-0-9]+)\]')
    
    parts=aNetPoint.findall(point_str)
    if parts==[]:
        parts=aNetPoint2.findall(point_str)
        if parts==[]:
            print('Error! Invalid point!')
            return [None,recent,undefined]
    # building:
    # find information:
    name=parts[0][0]
    con0_name=parts[0][1]
    con1_name=parts[0][2]
    if len(parts[0])>3:
        x=parts[0][3]
        y=parts[0][4]
    else:
        x=[]
        y=[]

    # build point:
    point=undefined.get(name,None)
    if point!=None:
        undefined.pop(name)
    else:
        point=NetP(name)
        recent.update({name:point})
    
    if con0_name!='':
        con0=recent.get(con0_name,None)
        if con0==None:
            con0=NetP(con0_name)
            recent.update({con0_name:con0})
            undefined.update({con0_name:con0})
        point.connect(con0,0)

    if con1_name!='':
        con1=recent.get(con1_name,None)
        if con1==None:
            con1=NetP(con1_name)
            recent.update({con1_name:con1})
            undefined.update({con1_name:con1})
        point.connect(con1,1)

    if x!=[]:
        point.m_pos[0]=int(x)
    if y!=[]:
        point.m_pos[1]=int(y)

    point.m_name=re.sub(r'#.*$',"",point.m_name)
    return [point,recent,undefined]

def readSubCode_new(code):
    aNetPoint=re.compile(r'[\w.,\[\]#=+*\\\-^$_\'~:@/\(\)]*\([\w.,\[\]#=+*\\\-^$_\'~:@/\(\)]*, *[\w.,\[\]#=+*\\\-^$_\'~:@/\(\)]*\)\[[-0-9]+,[-0-9]+\]')
    aNetPoint2=re.compile(r'([\w.,\[\]#=+*\\\-^$_\'~:@/\(\)]*\([\w.,\[\]#=+*\\\-^$_\'~:@/\(\)]*, *[\w.,\[\]#=+*\\\-^$_\'~:@/\(\)]*\))(?![\[])')
    exp='(->>|=>>|->|=>|{[ \t\n]*|[|&]{[ \t\n]*|[ \t\n]*}|\),[ \t\n]*|;[ \t\n]*|\):[ \t\n]*|\)[|&]:[ \t\n]*)'
    
    builtStack=[{}]
    undefinedStack=[{}]
    list_pt=[]
    wait_list=[]
    last=None
    head=None
    connection=None

    units=re.split(exp,code)
    units_new=[]
    for unit in units:
        if unit==None or unit=='':
            continue
        if unit=='),' or unit=='):' or unit==')|:' or unit==')&:':
            units_new[-1]+=')'
            units_new.append(unit[1:])
        else:
            units_new.append(unit)
    for unit in units_new:
        type1=aNetPoint.findall(unit)
        type2=aNetPoint2.findall(unit)

        if unit=='->' or unit=='=>' or unit=='->>' or unit=='=>>':
            connection=unit
        elif unit[0]=='{':
            wait_list.append(['clause_splitting',last])
            built=builtStack[-1]
            undefined=undefinedStack[-1]
            builtStack.append(built.copy())
            undefinedStack.append(undefined.copy())
        elif unit[0]==':':
            wait_list.append(['end_splitting',last])
        elif unit[0]==',':
            last=wait_list[-1][1]
        elif unit[0]==';':
            if wait_list!=[]:
                if wait_list[-1][0]=='end_splitting':
                    wait_list.pop()
                if wait_list!=[]:
                    last=wait_list[-1][1]
        elif unit[-1]=='}':
            last=wait_list[-1][1]
            wait_list.pop()
            builtStack.pop()
            undefinedStack.pop()
        elif unit[0]=='&':
            if unit[1]==':':
                last.m_yesAnd=True
                last.m_noAnd=True
                wait_list.append(['end_splitting',last])
            else:
                last.m_clauseAnd=True
                wait_list.append(['clause_splitting',last])
        elif unit[0]=='|':
            if unit[1]==':':
                last.m_yesAnd=False
                last.m_noAnd=False
                wait_list.append(['end_splitting',last])
            else:
                last.m_clauseAnd=False
                wait_list.append(['clause_splitting',last])
        elif type1!=[] or type2!=[]:
            if unit[0]=='+' or unit[0]=='\\':
                name=unit[1:]
            else:
                name=unit
            recent=builtStack.pop()
            undefined=undefinedStack.pop()
            [point,recent,undefined]=buildPoint(name,recent,undefined)
            builtStack.append(recent)
            undefinedStack.append(undefined)

            list_pt.append(point)

            current=Karma(point)
            if unit[0]=='+':
                current.m_buildMode=True
            current.m_cause=last
            if connection=='->':
                current.m_no=False
                if last!=None:
                    last.m_yese.append(current)
            elif connection=='->>':
                current.m_no=False
                if last!=None:
                    last.m_noe.append(current)
            elif connection=='=>':
                current.m_no=True
                if last!=None:
                    last.m_yese.append(current)
            elif connection=='=>>':
                current.m_no=True
                if last!=None:
                    last.m_noe.append(current)
            elif last!=None:
                last.m_clause.append(current)
            else:
                head=current
            connection=''
            last=current
    head.setRangers()
    return [[head],list_pt]

def buildPool(code):
    recent={}
    undefined={}
    list_pt=[]
    list_str=re.split('[\n;][\n\t ]*',code)
    for point_str in list_str:
        if point_str=='':
            continue
        [point,recent,undefined]=buildPoint(point_str,recent,undefined)
        list_pt.append(point)
    return list_pt





def readSubCode(code):
    pattern=re.compile(r'[\w.,\[\]#=*\\\-^$_\'~]*\([\w.,\[\]#=*\\\-^$_\'~]*,[\w.,\[\]#=*\\\-^$_\'~]*\)')
    part_ps=pattern.findall(code)
    n=0
    part_km=code
    while n<len(part_ps):
        part_km=re.sub(r'[\w.,\[\]#=*\\\-^$_\'~]*\([\w.,\[\]#=*\\\-^$_\'~]*,[\w.,\[\]#=*\\\-^$_\'~]*\)',str(n),part_km,1)
        n+=1
    code_cmp='[-1,-1]\n'.join(part_ps)
    code=code_cmp+'[-1,-1]\n__________________\n'+part_km
    return readStdCode(code)
        

def writeStdCode(karmas,list_pt):
    code=''
    i=0
    for point in list_pt:
        point.m_name+='#'+str(i)
        i=i+1
    for point in list_pt:
        code+=point.info()+'\n'
    for karma in karmas:
        code+='\n_____________________________\n'
        [text,list_pt]=writeStdCode_karma(karma,list_pt)
        code+=text
    for point in list_pt:
        point.m_name=re.sub(r'#.*$',"",point.m_name)
    return code

def writeStdCode_karma(karma,list_pt):
    karma_code=''

    if karma==None:
        return [karma_code,list_pt]
    
    if karma.m_symbol not in list_pt:
        list_pt.append(karma.m_symbol)
    if karma.m_buildMode==True:
        karma_code+='+'
    karma_code+=str(list_pt.index(karma.m_symbol))

    if karma.m_clause!=[]:
        if karma.m_clauseAnd==False:
            karma_code+='|'
        karma_code+='{'
        for clause in karma.m_clause:
            [text,list_pt]=writeStdCode_karma(clause,list_pt)
            karma_code+=text
            if clause!=karma.m_clause[-1]:
                karma_code+=','
        karma_code+='}'

    if len(karma.m_yese)+len(karma.m_noe)>1:
        if karma.m_yesAnd==True:
            karma_code+='&'
        karma_code+=':'
    for end in karma.m_yese:
        if end.m_no==False:
            karma_code+='->'
        else:
            karma_code+='=>'
        [text,list_pt]=writeStdCode_karma(end,list_pt)
        karma_code+=text
        if end!=karma.m_yese[-1]:
            karma_code+=','
    for end in karma.m_noe:
        if end.m_no==False:
            karma_code+='->>'
        else:
            karma_code+='=>>'
        [text,list_pt]=writeStdCode_karma(end,list_pt)
        karma_code+=text
        if end!=karma.m_noe[-1]:
            karma_code+=','
    if len(karma.m_yese)+len(karma.m_noe)>1:
        karma_code+=';'

    return [karma_code,list_pt]


def listToDict(list_pt):
    dict_pt={}
    for point in list_pt:
        term=dict_pt.get(point.m_name,[])
        term.append(point)
        dict_pt.update({point.m_name:term})
    return dict_pt

def dictToList(dict_pt):
    list_pt=[]
    for term in dict_pt:
        list_pt+=dict_pt[term]
    return list_pt

def ptToDict(point):
    dict_con={}
    for con in point.m_con:
        if con.m_db[0]==point:
            dict_con.update({con.m_name:con})
    return dict_con

            
def runKarmaByOneStep(karma,pool,n=1):
    head=karma
    list_km=karma.allEffects()
    if karma.m_stage==0:
        karma.m_stage=1
    for i in range(n):
        for km in list_km:
            change,list_new=km.Reason_oneStep(pool)
            if change:
                break
        showKarmaState(karma)
        print('__________')

def showKarmaState(karma):
    list_km=karma.allEffects()
    for km in list_km:
        print(km.m_symbol.m_name,km.m_stage)

def pointsInChain(karma):
    list_km=karma.allEffects()
    list_pt=[]
    for km in list_km:
        list_pt.append(km.m_symbol)
    return list_pt

def getAllSystemPt(point,list_pt=None):
    if list_pt==None:
        list_pt=[]
    list_pt+=[point]
    for con in point.m_con:
        if con.m_permission==0 and con.m_db[0]==point:
            list_pt.append(con)
            if con.m_db[1]!=None and con.m_db[1] not in list_pt:
                if con.m_db[1].m_permission==0:
                    getAllSystemPt(con.m_db[1],list_pt)
                else:
                    list_pt+=[con.m_db[1]]
            # if con.m_db[1].m_permission==0:
            #     list_pt+=getAllSystemPt(con.m_db[1])
    return list_pt

def getPoint(point,key,default=''):
    dict_pt=ptToDict(point)
    con=dict_pt.get(key,None)
    if con==None:
        con=NetP(key).con(point,NetP(default))
    con.m_permission=0
    pt=con.m_db[1]
    pt.m_permission=0
    return pt

def setPoint(point,key,value):
    for con in point.m_con:
        if con.m_db[0]==point and con.m_name==key:
            con.con(point,value)
            return
    NetP(key).con(point,value)

def getPointByFormat(point,type_pt):
    list_pt=[]
    if type_pt=='list':
        for con in point.m_con:
            if con.m_name=='.[i]' and con.m_db[0]==point and con.m_db[1]!=None:
                list_pt.append(con.m_db[1])
                con.m_permission=0
    return list_pt

def setPointByFormat(point,type_pt,value=None):
    if type_pt=='list.append':
        con=NetP('.[i]').con(point,value)
        con.m_permission=0
    elif type_pt=='list.+=':
        for pt in value:
            con=NetP('.[i]').con(point,pt)
            con.m_permission=0
    elif type_pt=='list.clear':
        list_del=[]
        for con in point.m_con:
            if con.m_name=='.[i]' and con.m_db[0]==point and con.m_db[1]!=None:
                list_del.append(con)
        for pt in list_del:
            pt.delete()
        del list_del[:]
    elif type_pt=='list.pop':
        list_pt=getPointByFormat(point,'list')
        pt=list_pt[-1]
        for con in pt.m_con:
            if con.m_name=='.[i]' and con.m_db[0]==point and con .m_db[1]==pt:
                con.delete()
                del con
        del pt
    elif type_pt=='list.remove':
        list_pt=getPointByFormat(point,'list')
        if value in list_pt:
            for con in value.m_con:
                if con.m_name=='.[i]' and con.m_db[0]==point and con .m_db[1]==value:
                    con.delete()
                    del con
        
    

def printPointByFormat(point,type_pt):
    if type_pt=='list':
        list_pt=getPointByFormat(point,type_pt)
        print([pt.info() for pt in list_pt])

def printPoint(point):
    print(point.info(),'{')
    for con in point.m_con:
        if con.m_db[0]==point:
            print(con.m_name+':',con.m_db[1].info())
    print('}')

def printPtList(list_pt):
    info_pt='['
    for pt in list_pt:
        info_pt+=pt.info()
        if pt!=list_pt[-1]:
            info_pt+=', '
    info_pt+=']'
    print(info_pt)
    



############################### grammar of karma ###################################
class NetPStack:
    def __init__(self):
        self.m_builtStack=[{}]
        self.m_undefinedStack=[{}]

    def popBuilt(self):
        return self.m_builtStack.pop()

    def popUndefined(self):
        return self.m_undefinedStack.pop()

    def pushBuilt(self,built):
        self.m_builtStack.append(built)

    def pushUndefined(self,undefined):
        self.m_undefinedStack.append(undefined)

    def enterClause(self):
        self.m_builtStack.append(self.m_builtStack[-1].copy())
        self.m_undefinedStack.append(self.m_undefinedStack[-1].copy())

    def leaveClause(self):
        if len(self.m_undefinedStack)>1:
            if len(self.m_undefinedStack[-1])>len(self.m_undefinedStack[-2]):
                print('\n\n\nError! Undefined net point in some clause.\nUndefined stack:',self.m_undefinedStack[-1])
                raise Exception('Error! Undefined net point in some clause.')
        self.m_builtStack.pop()
        self.m_undefinedStack.pop()

    def buildNetP(self,name,con0_name='',con1_name=''):
        recent=self.m_builtStack[-1]
        undefined=self.m_undefinedStack[-1]

        point=undefined.get(name,None)
        if point==None:
            point=NetP(re.sub(r'#.*$','',name))
            recent.update({name:point})
        else:
            undefined.pop(name)

        if con0_name!='':
            con0=recent.get(con0_name,None)
            if con0==None:
                con0=NetP(re.sub(r'#.*$','',con0_name))
                recent.update({con0_name:con0})
                undefined.update({con0_name:con0})
            point.connect(con0,0)
        if con1_name!='':
            con1=recent.get(con1_name,None)
            if con1==None:
                con1=NetP(re.sub(r'#.*$','',con1_name))
                recent.update({con1_name:con1})
                undefined.update({con1_name:con1})
            point.connect(con1,1)
        return point

# User api:
def readSubCode_tokener(code):
    list_karma=[]
    code=re.sub(r'%.*\n','\n',code)
    code=re.sub(r'^[ \t\n]*','',code)
    while code!='':
        [code,karma,pointStack]=chainToken(code)
        karma.setRangers()
        list_karma.append(karma)
        if code!='' and code[0]==';':
            code=code[1:]
        code=re.sub(r'^[ \t\n]*','',code)
    return list_karma

def buildPoints_tokener(code):
    list_pt=[]
    code=re.sub(r'\n%.*\n','\n\n',code)
    code=re.sub(r'^[ \t\n]*','',code)
    pointStack=NetPStack()
    while code!='':
        code,netP,pointStack=netPToken(code,pointStack)
        list_pt.append(netP)
        code=re.sub(r'^[ \t\n;]*','',code)
    return list_pt

def divideSents_tokener(code):
    list_sent=[]
    code=re.sub(r'%.*\n','\n',code)
    code=re.sub(r'^[ \t\n]*','',code)
    code_keep=code
    while code!='':
        [code,karma,pointStack]=chainToken(code)
        si=code_keep.rfind(code)
        text=code_keep[0:si]
        if code!='' and code[0]==';':
            code=code[1:]
        code=re.sub(r'^[ \t\n]*','',code)
        code_keep=code
        sent=NetP(karma.m_symbol.m_name,text)
        list_sent.append(sent)
    return list_sent

########

def chainToken(code,pointStack=None):
    if pointStack==None:
        pointStack=NetPStack()
    [code,karma,pointStack]=karmaToken(code,pointStack)
    if code=='' or code[0]==';' or code[0]=='\n' or code[0]=='}' or code[0]==',':
        return [code,karma,pointStack]
    elif code[0]==':':
        code=code[1:]
        [code,karma,pointStack]=splitToken(code,karma,pointStack)
    elif code[0]=='|' or code[0]=='&':
        typeSub=code[0]
        code=code[1:]
        if code!='' and code[0]==':':
            if typeSub=='|':
                karma.m_noAnd=False
                karma.m_yesAnd=False
            else:
                karma.m_noAnd=True
                karma.m_yesAnd=True
            code=code[1:]
            [code,karma,pointStack]=splitToken(code,karma,pointStack)
    else:
        [code,typeCon]=conToken(code)
        [code,effect,pointStack]=chainToken(code,pointStack)
        buildRelation(karma,typeCon,effect)
    return [code,karma,pointStack]


def conToken(code):
    while len(code)>3 and code[0:3]=='...':
        code=re.sub(r'^\.\.\..*[\n\t ]*','',code)
    code=re.sub(r'^[ \t]*','',code)
    if len(code)>2 and code[0:3]=='->>':
        typeCon=code[0:3]
        code=code[3:]
    elif len(code)>2 and code[0:3]=='=>>':
        typeCon=code[0:3]
        code=code[3:]
    elif len(code)>1 and code[0:2]=='->':
        typeCon=code[0:2]
        code=code[2:]
    elif len(code)>1 and code[0:2]=='=>':
        typeCon=code[0:2]
        code=code[2:]
    else:
        print('\n\n\nIllegal connection symbol!\nCode:',code)
        raise Exception('Illegal connection symbol!')
    code=re.sub(r'^[ \t]*','',code)
    return [code,typeCon]

def clauseToken(code,karma,pointStack):
    pointStack.enterClause()
    while True:
        code=re.sub(r'^[ \t\n]*','',code)
        if code=='':
            raise Exception('Error! Unbalanced bracket!')
        elif code[0]=='}':
            break
        else:
            [code,clause,pointStack]=chainToken(code,pointStack)
            karma.m_clause.append(clause)
            clause.m_cause=karma
            if code!='' and code[0]!=',':
                break
            elif code!='':
                code=code[1:]
    pointStack.leaveClause()
    return [code,karma,pointStack]

def splitToken(code,karma,pointStack):
    while True:
        code=re.sub(r'^[ \t\n]*','',code)
        [code,typeCon]=conToken(code)
        [code,effect,pointStack]=chainToken(code,pointStack)
        buildRelation(karma,typeCon,effect)
        code=re.sub(r'^[ \t\n]*','',code)
        if code=='' or code[0]==';' or code[0]=='}':
            break
        elif code[0]!=',':
            print('\n\n\n\nError! Ilegal splitting type!\nCode:',code)
            raise Exception('Error! Ilegal splitting type!')
        else:
            code=code[1:]
    return [code,karma,pointStack]

def karmaToken(code,pointStack):
    if code=='':
        raise Exception('Error! Invalid karma detected!')
    buildType=False
    karma=None
    if code[0]=='+':
        buildType=True
    [code,netP,pointStack]=netPToken(code,pointStack)
    karma=Karma(netP)
    if buildType==True and netP.m_name!='+':
        netP.m_name=netP.m_name[1:]
        karma.m_buildMode=True
    if code!='' and code[0]=='{':
        code=code[1:]
        [code,karma,pointStack]=clauseToken(code,karma,pointStack)
        code=re.sub(r'^[\n\t ]*','',code)
        if code=='' or code[0]!='}':
            print('\n\n\nError! Unbalanced bracket.\nCode:',code)
            raise Exception('Error! Unbalanced bracket.')
        else:
            code=code[1:]
    elif code!='' and (code[0]=='|' or code[0]=='&'):
        typeSub=code[0]
        code=code[1:]
        if code!='' and code[0]=='{':
            if typeSub=='|':
                karma.m_clauseAnd=False
            else:
                karma.m_clauseAnd=True
            code=code[1:]
            [code,karma,pointStack]=clauseToken(code,karma,pointStack)
            code=re.sub(r'^[\n\t ]*','',code)
            if code=='' or code[0]!='}':
                raise Exception('Error! Unbalanced bracket.')
            else:
                code=code[1:]
        else:
            code=typeSub+code
    return [code,karma,pointStack]

def netPToken(code,pointStack):
    title=r'^[\w\[\]~#.+=\-^/*\\]*'
    name=re.match(title,code).group()
    code=re.sub(title,'',code)
    if name=='':
        print('\n\n\nError! Invalid name.\nCode:',code)
        raise Exception('Error! Invalid name.')
    if name[-1]=='=' or name[-1]=='-':
        if len(code)>0 and code[0]=='>':
            code=name[-1]+code
            name=name[0:-1]
    con0_name=''
    con1_name=''
    text=''
    if code!='' and code[0]=='\"':
        code=code[1:]
        [code,text]=textToken(code)
        if code=='' or code[0]!='\"':
            raise Exception('Error! Unbalanced quote!')
        code=code[1:]
    if code!='' and code[0]=='(':
        code=code[1:]
        con0_name=re.match(title,code).group()
        code=re.sub(title,'',code)
        if code=='' or code[0]!=',':
            print(code)
            raise Exception('Error! Ilegal net point format. A net point must be title"text"(title,title)')
        code=code[1:]
        con1_name=re.match(title,code).group()
        code=re.sub(title,'',code)
        if code=='' or code[0]!=')':
            raise Exception('Error! Unbalanced bracket in a net point format!')
        code=code[1:]
    if name=='':
        print('Warning! There is a point without a name!')
    netP=pointStack.buildNetP(name,con0_name,con1_name)
    posFormat=r'^\[(-?\d+), *(-?\d+)\]'
    pos=re.findall(posFormat,code)
    if pos!=[]:
        x=int(pos[0][0])
        y=int(pos[0][1])
        netP.m_pos=[x,y]
        code=re.sub(r'^\[-?\d+, *-?\d+\]','',code)
    netP.m_text=text
    return [code,netP,pointStack]

def textToken(code):
    text=''
    preEnd=True
    while True:
        if code=='':
            break
        elif len(code)>1 and code[0:2]=='\\"':
            preEnd=False
        elif code[0]=='\"' and preEnd==True:
            break
        else:
            text+=code[0]
            preEnd=True
        code=code[1:]
    return [code,text]

def buildRelation(karma,typeCon,effect):
    if typeCon=='->':
        karma.m_yese.append(effect)
    elif typeCon=='->>':
        karma.m_noe.append(effect)
    elif typeCon=='=>':
        karma.m_yese.append(effect)
        effect.m_no=True
    elif typeCon=='=>>':
        karma.m_noe.append(effect)
        effect.m_no=True
    else:
        raise Exception('Error! Ilegal connection type!')
    effect.m_cause=karma
##############################################################################





if __name__=='__main__':

    [karmas,list_pt]=readSubCode_new('_东西(,){[](,)->[是](_东西,猫)->猫(,),[](,)->上面(_东西,桌子)->桌子(,)}->+棒(,)')
    print(karmas[0].info_karma())

    
    
    [code,karma,pointStack]=chainToken('[a]->和平([a],~c#12)->~c#12|{d"f\\\\\"(a,b)->d(,c)"->c->d,c}&:->c,->d')
    print(karma.info_karma())
    print(pointStack.m_undefinedStack)