import sys,re
if __name__=='__main__':
    sys.path.append(sys.path[0]+'\\..')
from body.bone import NetP

def str2struct(string):
    list_pt=[]
    this=None
    for letter in string:
        this=NetP(letter)
        if list_pt!=[]:
            list_pt[-1].connect(this,1)
        list_pt.append(this)
    return list_pt

def struct2str(list_pt):
    string=''
    head=None
    for point in list_pt:
        if point.m_con==[]:
            head=point
            break
    if head==None:
        return string
    while True:
        string+=head.m_name
        if head.m_db[1]!=None:
            head=head.m_db[1]
        else:
            break
    return string


###################################  Formula Parser  ######################################
def equationToken(string,list_pt=None):
    sign=None
    equation=None
    equal=None
    if list_pt==None:
        list_pt=[]
    if string[0]=='-':
        sign=NetP('-')
        list_pt.append(sign)
        string=string[1:]
    [formula,string,list_pt]=formulaToken(string,list_pt)
    equation=formula
    if sign!=None:
        sign.con(None,formula)
    if string=='':
        return [equation,string,list_pt]
    elif string[0]=='=':
        equal=NetP('=')
        list_pt.append(equal)
        string=string[1:]
        [point,string,list_pt]=equationToken(string,list_pt)
        equal.con(equation,point)
        if string=='':
            return [equation,string,list_pt]
    raise Exception('Error: wrong equation format!')

def formulaToken(string,list_pt):
    [formula,string,list_pt]=variableToken(string,list_pt)
    if string=='':
        return [formula,string,list_pt]
    elif string[0]=='+' or string[0]=='-' or string[0]=='*' or string[0]=='/' or string[0]=='^':
        relation=NetP(string[0])
        list_pt.append(relation)
        string=string[1:]
        [point,string,list_pt]=formulaToken(string,list_pt)
        relation.con(formula,point)
    return [formula,string,list_pt]

def variableToken(string,list_pt):
    variable_name=''
    variable=None
    if string=='':
        raise Exception('Error: empty variable.')
    elif string[0]=='(':
        sign=None
        variable=NetP('括号')
        list_pt.append(variable)
        relation=NetP('in')
        list_pt.append(relation)
        string=string[1:]
        if string[0]=='-':
            sign=NetP('-')
            list_pt.append(sign)
        [point,string,list_pt]=formulaToken(string,list_pt)
        relation.con(variable,point)
        if sign!=None:
            sign.con(None,point)
        if string=='' or string[0]!=')':
            raise Exception('Error: unbalanced bracket!')
        else:
            string=string[1:]
    elif string[0].isdigit():
        while True:
            if string!='' and string[0].isdigit():
                variable_name+=string[0]
                string=string[1:]
            else:
                break
        variable=NetP(variable_name)
        list_pt.append(variable)
    elif string[0].isalpha():
        while True:
            if string=='':
                break
            elif string[0].isdigit() or string[0].isalpha():
                variable_name+=string[0]
                string=string[1:]
            else:
                break
        variable=NetP(variable_name)
        list_pt.append(variable)
        if string!='' and string[0]=='(':
            relation=NetP('in')
            list_pt.append(relation)
            string=string[1:]
            [inputs,string,list_pt]=inputToken(string,list_pt)
            relation.con(variable,inputs)
            if string=='' or string[0]!=')':
                raise Exception('Error: unbalanced brackets.')
            else:
                string=string[1:]
    
    return [variable,string,list_pt]

def inputToken(string,list_pt):
    [inputs,string,list_pt]=formulaToken(string,list_pt)
    last=inputs
    while string!='' and string[0]==',':
        relation=NetP('and')
        list_pt.append(relation)
        string=string[1:]
        [point,string,list_pt]=formulaToken(string,list_pt)
        relation.con(last,point)
        last=point
    return [inputs,string,list_pt]

def eqn2struct(string):
    string=string.replace(" ","")
    point,string,list_pt=equationToken(string)
    return list_pt

########################################################################################

def nextPoints(point,key):
    list_pt=[]
    for pt in point.m_con:
        if pt.m_name==key and pt.m_db[0]==point and pt.m_db[1]!=None:
            list_pt.append(pt.m_db[1])
    return list_pt

def struct2Eqn(point):
    eqn=''
    name=point.m_name
    
    if name=='和式':
        addPts=nextPoints(point,'+')
        minPts=nextPoints(point,'-')
        for pt in addPts:
            if eqn!='':
                eqn+='+'
            eqn+=struct2Eqn(pt)
        for pt in minPts:
            eqn+='-'+struct2Eqn(pt)
    elif name=='乘式':
        mulPts=nextPoints(point,'*')
        devPts=nextPoints(point,'/')
        for pt in mulPts:
            if eqn!='':
                eqn+='*'
            eqn+=struct2Eqn(pt)
        for pt in devPts:
            if eqn=='':
                eqn+='1'
            eqn+='/'+struct2Eqn(pt)
    else:
        if name=='括号':
            eqn+='('
            contain=nextPoints(point,'in')
            for pt in contain:
                eqn+=struct2Eqn(pt)
            eqn+=')'
        else:
            eqn+=name
        pwrPts=nextPoints(point,'^')
        for pt in pwrPts:
            eqn+='^'+struct2Eqn(pt)
    eqlPts=nextPoints(point,'=')
    for pt in eqlPts:
        eqn+='='+struct2Eqn(pt)
    return eqn



###################################  Smilei parser  ####################################
def Smilei2struct(title):
    try:
        f=open(title)
    except:
        print('No such file exits!')
        return []
    code=f.read()
    [code,list_pt]=SmileiToken(code,title)
    return list_pt

def SmileiToken(code,title,list_pt=None):
    if list_pt==None:
        list_pt=[]
    point=NetP('smilei')
    point.m_text=title
    list_pt.append(point)
    code=re.sub(r'[ \t]','',code)
    code=re.sub(r'#.*\n','',code)
    while code!='':
        code=re.sub(r'^\n*','',code)
        if code=='':
            break
        else:
            [code,line_pt]=lineSmToken(code,list_pt)
            con=NetP('in')
            list_pt.append(con)
            con.con(point,line_pt)
    return [code,list_pt]

def lineSmToken(code,list_pt):
    nameFormat=r'^[\w\.]+'
    name=re.match(nameFormat,code).group()
    if name=='':
        raise Exception('Error! Invalid name of function or variable!')
    code=re.sub(nameFormat,'',code)
    line_pt=NetP(name)
    list_pt.append(line_pt)
    if code!='' and code[0]=='=':
        code=code[1:]
        [code,content]=conSmToken(code)
        if content=='':
            raise Exception('Error! Invalid assignment value!')
        line_pt.m_text=content
    elif code!='' and code[0]=='(':
        code=code[1:]
        code=re.sub(r'^\n*','',code)
        [code,var]=varSmToken(code,list_pt)
        con=NetP('in')
        list_pt.append(con)
        con.con(line_pt,var)
        while True:
            if code!='' and code[0]==',':
                code=code[1:]
            else:
                break
            code=re.sub(r'^\n*','',code)
            if code!='' and code[0]==')':
                break
            [code,var]=varSmToken(code,list_pt)
            con=NetP('in')
            list_pt.append(con)
            con.con(line_pt,var)
        code=re.sub(r'^\n*','',code)
        if code=='' or code[0]!=')':
            raise Exception('Error! Unbalanced bracket!')
        code=code[1:]
    return [code,line_pt]

def varSmToken(code,list_pt):
    nameFormat=r'^[\w\.]+'
    name=re.match(nameFormat,code).group()
    if name=='':
        raise Exception('Error! Invalid name!')
    code=re.sub(nameFormat,'',code)
    if code=='' or code[0]!='=':
        raise Exception('Error! Every variable must be assigned by some values.')
    code=code[1:]
    [code,content]=conSmToken(code)
    var=NetP(name)
    list_pt.append(var)
    var.m_text=content
    return [code,var]

def conSmToken(code):
    content=''
    if code=='':
        raise Exception('Error! Value can\'t be empty!')
    if code[0]=='[':
        content+=code[0]
        code=code[1:]
        code=re.sub(r'^\n*','',code)
        [code,con]=listSmToken(code)
        content+=con
        code=re.sub(r'^\n*','',code)
        if code=='' or code[0]!=']':
            raise Exception('Error! Unbalanced list bracket!')
        code=code[1:]
        content+=']'
    else:
        stack1=0
        stack2=0
        while code!='':
            if code[0]=='\n':
                break
            elif code[0]==',' and stack1==0 and stack2==0:
                break
            elif code[0]=='(':
                stack1+=1
            elif code[0]=='[':
                stack2+=1
            elif code[0]==')':
                stack1-=1
            elif code[0]==']':
                stack2-=1
            if stack1<0 or stack2<0:
                break
            content+=code[0]
            code=code[1:]
        if content=='':
            raise Exception('Error! Value can\'t be empty!')
    return [code,content]

def listSmToken(code):
    content=''
    if code=='' or code[0]==']':
        return [code,content]
    [code,con]=conSmToken(code)
    content+=con
    while True:
        if code=='' or code[0]!=',':
            break
        content+=','
        code=code[1:]
        code=re.sub(r'^\n*','',code)
        if code=='' or code[0]==']':
            break
        [code,con]=conSmToken(code)
        content+=con
    return [code,content]
    




########################################################################################

if __name__=='__main__':
    list_pt=eqn2struct('x^2-(x-y)/(x+y ) + 1*f(x+1, y)=2')
    print(list_pt)
    for point in list_pt:
        point.print()

    # f=open('files\smilei_sample.py')
    # [code,point,list_pt]=SmileiToken(f.read(),'test')
    list_pt=Smilei2struct('files\smilei_sample.py')
    for point in list_pt:
        point.print()

