import sys, re
if __name__=='__main__':
    sys.path.append(sys.path[0]+'\\..')
sys.path.append(sys.path[0]+'\\..')
from body.bone import NetP
from body.soul import Karma
from tools import tools_basic
from body.body_motor import Motor
import logging

class Library:
    def __init__(self,point=None):
        self.m_self=None
        self.m_lib=[]
        self.m_terms=[]
        self.m_motor=None

        self.initialize(point)

    def initialize(self,point):
        if point==None:
            point=NetP('library')
        self.m_self=point
        point.m_dev=self
        point.m_permission=0

        pt_motor=tools_basic.getPoint(point,'m_motor','compiler')
        pt_terms=tools_basic.getPoint(point,'m_terms','list')

        self.m_motor=pt_motor.m_dev
        self.m_terms=tools_basic.getPointByFormat(pt_terms,'list')
        for term in self.m_terms:
            term.m_permission=0

        print(self.info())

    def updateMotor(self):
        pt_motor=tools_basic.getPoint(self.m_self,'m_motor','compiler')
        self.m_motor=pt_motor.m_dev

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
        print('Load success!')

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
        list_km=[]
        try:
            list_km=tools_basic.readSubCode_tokener(code)
        except Exception as e:
            logging.exception(e)
        return list_km

    def transfer(self,question):
        if question==None:
            return
        print('请问怎么做'+question.m_name+'的动作?('+question.info()+')')
        if self.m_motor==None:
            self.updateMotor()
            if self.m_motor==None:
                print('No appropriate motor in the library to run this code.')
                return []
        if question.m_text!='':
            outputs=self.m_motor.runCode(question.m_text,question)
            return outputs
        for term in self.m_terms:
            if question.m_name[1:-1]!=term.m_name:
                continue
            outputs=self.m_motor.runCode(term.m_text,question)
            if question.m_creator==None:
                continue
            return outputs
        return []

            

    def info(self):
        information='+++++++ LIBRARY ++++++\nName: '+self.m_self.m_name+'\nLibrary: \n'
        for dirc in self.m_lib:
            information+=dirc+';\n'
        information+='Terms:\n'
        for term in self.m_terms:
            information+=term.m_name+' '
        return information
    
    def print(self):
        print(self.info())

