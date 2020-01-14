import sys, re
if __name__=='__main__':
    sys.path.append(sys.path[0]+'\\..')
sys.path.append(sys.path[0]+'\\..')
from body.bone import NetP
from body.soul import Karma
from tools import tools_basic
import logging

class Motor:
    def __init__(self,point=None):
        self.m_self=None
        self.m_source=None
        self.m_lib=[]
        
        self.m_mapDict={}
        self.m_questions=[]
        self.m_karmas=[]
        self.m_running=[]
        self.m_terms=[]

        self.m_inputs=[]
        self.m_outputs=[]
        # Both of lists are listing tmp points generated in the process.
        self.m_tmpNew=[]
        self.m_answers=[]
        # self.loadLib('C:\\Users\\cheng\\Dropbox\\结构语言\\Nini6.2_Eden\\Nini\\testLib.txt')

        self.initialize(point)

    def initialize(self,point):
        if point==None:
            point=NetP('compiler')
        self.m_self=point
        point.m_dev=self
        point.m_permission=0

        pt_source=tools_basic.getPoint(point,'m_source','incomingPool')
        pt_terms=tools_basic.getPoint(point,'m_terms','list')
        self.m_inputs=pt_source.m_dev.m_pool
        self.m_terms=tools_basic.getPointByFormat(pt_terms,'list')
        for term in self.m_terms:
            term.m_permission=0

        print(self.info())

    def genPool(self,sent=None):
        if sent==None:
            return self.m_inputs
        else:
            return self.m_inputs+self.m_mapDict[sent]

    def reset(self):
        for sent in self.m_karmas:
            self.retrive(sent)
        self.clearTmpPts()

        self.m_mapDict.clear()
        self.m_karmas.clear()
        self.m_outputs.clear()
        self.m_running.clear()
        self.m_questions.clear()

    def loadCode(self,code):
        for karma in self.m_karmas:
            self.m_mapDict.pop(karma)
        self.m_karmas=self.compile(code)
        for karma in self.m_karmas:
            self.m_mapDict.update({karma:[]})

    def loadLib(self,direct):
        if direct in self.m_lib:
            return
        try:
            f=open(direct,encoding='gbk')
        except:
            print(direct+" doesn't exist!")
            return
        try:
            code=f.read()
        except:
            f.close()
            f=open(direct,encoding='utf-8')
            code=f.read()
        self.loadTerm(code)
        self.m_lib.append(direct)

    def loadTerm(self,code):
        sents=[]
        try:
            sents=tools_basic.divideSents_tokener(code)
            pt_terms=tools_basic.getPoint(self.m_self,'m_terms','list')
            for sent in sents:
                tools_basic.setPointByFormat(pt_terms,'list.append',sent)
                sent.m_permission=0
        except Exception as e:
            logging.exception(e)
        self.m_terms+=sents
    
    def clearTerm(self):
        self.m_terms.clear()
        pt_terms=tools_basic.getPoint(self.m_self,'m_terms','list')
        tools_basic.setPointByFormat(pt_terms,'list.clear')

    def compile(self,code):
        karmas=[]
        try:
            karmas=tools_basic.readSubCode_tokener(code)
        except Exception as e:
            logging.exception(e)
        return karmas


    def retrive(self,sent):
        list_map=self.m_mapDict.get(sent,[])
        for amap in list_map:
            if amap in self.m_tmpNew:
                self.m_tmpNew.remove(amap)
            if amap in self.m_outputs:
                self.m_outputs.remove(amap)
            amap.delete()
            del amap
        sent.map(None)
        if list_map!=[]:
            del list_map[:]
            list_map.clear()

    def runAll(self):
        for karma in self.m_mapDict:
            self.retrive(karma)
        for karma in self.m_karmas:
            karma.m_stage=1
            self.run(-1,karma)
            if karma.m_reState=='dark yellow':
                self.retrive(karma)
            elif karma.m_reState=='dark green':
                self.m_mapDict[karma].clear()

    def updateTmpNew(self,list_new):
        for pt in list_new:
            # if pt not in self.m_tmpNew and pt not in self.m_outputs:
            self.m_tmpNew.append(pt)
        return self.m_tmpNew

    def updateOutputs(self,list_new):
        for point in list_new:
            # if point not in self.m_outputs:
            self.m_outputs.append(point)
            # if point in self.m_tmpNew:
            #     self.m_tmpNew.remove(point)
        return self.m_outputs

    def updateAnswers(self,list_new):
        for point in list_new:
            if point in self.m_questions and point.m_creator!=None:
                point.m_creator.map(None)
                self.m_questions.remove(point)
                self.m_answers.append(point)
        return self.m_answers

    def updateOutPool(self,list_new,sent,karma_type):
        if karma_type!=1 and sent in self.m_karmas:
            self.updateOutputs(list_new)
        else:
            self.updateTmpNew(list_new)
        return self.genPool()

    def clearTmpPts(self):
        for pt in self.m_answers:
            pt.delete()
            del pt
        for pt in self.m_tmpNew:
            pt.delete()
            del pt
        self.m_answers.clear()
        self.m_tmpNew.clear()

    def printKarmaState(self,karma):
        if karma.m_map!=None:
            print(karma.m_symbol.info(),karma.stateSelf(),str(karma.m_stage)+'(Stage)')
            print(karma.m_map.info(),karma.m_map.m_needed!=None,karma.m_map.m_creator!=None)
        else:
            print(karma.m_symbol.info(),karma.stateSelf(),str(karma.m_stage)+'(Stage)')
            print(karma.m_map)

    def run(self,n=1,sent=None):
        if sent==None:
            if self.m_running==[]:
                print("Error! Nothing can run.")
                return False
            else:
                sent=self.m_running[-1]
        else:
            self.m_running.append(sent)
        if sent.m_stage==0:
            sent.m_stage=1
        i=0
        outPool=self.genPool(sent)
        list_map=self.m_mapDict[sent]
        running=sent.allEffects()
        while i!=n:
            i+=1
            change=False
            for karma in running:
                result,list_new=karma.Reason_oneStep(tools_basic.listToDict(outPool))
                if karma.m_interp==True:
                    # outPool=self.updateOutPool(list_new,sent)
                    self.m_questions.append(karma.m_map)
                    self.callLib(karma.m_map)
                if result:
                    if n!=-1:
                        self.printKarmaState(karma)
                    change=True
                    list_map+=list_new
                    self.updateAnswers(list_new)
                    self.updateOutPool(list_new,sent,karma.isFunctionPoint())
                    outPool=self.m_inputs+list_map
                    break
            # print('Running Stack:',[karma.m_symbol.info() for karma in self.m_running])
            # print('Change State:',change)
            if change==False:
                self.m_running.pop()
                break
        return True

    def callLib(self,question,n=-1):
        if question==None:
            return
        else:
            print('请问什么是'+question.m_name+'?('+question.info()+')')
        if question.m_text!='':
            karmas=self.compile(question.m_text)
            karma=karmas[0]
            karma.m_stage=1
            karma.m_restricted=True
            karma.m_listMP=[question]
            self.m_mapDict.update({karma:[]})
            self.run(n,karma)
            if question.m_creator==None:
                self.retrive(karma)
                del self.m_mapDict[karma]
            return
        for term in self.m_terms:
            if question.m_name[1:-1]!=term.m_name:
                continue
            karmas=self.compile(term.m_text)
            karma=karmas[0]
            karma.m_stage=1
            karma.m_restricted=True
            karma.m_listMP=[question]
            self.m_mapDict.update({karma:[]})
            self.run(n,karma)
            if question.m_creator==None:
                self.retrive(karma)
                del self.m_mapDict[karma]
            else:
                return
            


    def output(self):
        list_out=self.m_outputs
        return list_out

    def runCode(self,code,question=None):
        self.reset()
        self.loadCode(code)
        if question!=None and self.m_karmas!=[]:
            self.m_karmas[0].m_listMP=[question]
            self.m_karmas[0].m_restricted=True
        self.runAll()
        if question!=None and question.m_creator==None:
            return []
        return self.output()

    def info(self):
        information='+++++++ MOTOR ++++++\nName: '+self.m_self.m_name+'\nLibrary: '
        for dirc in self.m_lib:
            information+=dirc+';\n'
        information+='\nterms: '
        for term in self.m_terms:
            information+=term.m_name
            if term!=self.m_terms[-1]:
                information+=', '
        information+='\nMaps: '
        for sent in self.m_mapDict:
            information+=sent.m_symbol.m_name+'('
            for map in self.m_mapDict[sent]:
                information+=map.m_name
                if map!=self.m_mapDict[sent][-1]:
                    information+=', '
            information+=') '
        information+='\n'
        return information
    
    def print(self):
        print(self.info())



if __name__=='__main__':
    test=Motor(None)
    pool=NetP('').build('a(,);b(a,);c(d,b);d(,)')
    test.m_inputs=pool
    list_new=test.runCode('a(,)->+c(,a)')
    for point in list_new:
        point.print()