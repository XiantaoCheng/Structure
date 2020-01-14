import sys, re
if __name__=='__main__':
    sys.path.append(sys.path[0]+'\\..')
from tools import tools_basic
from body.bone import NetP
from body.soul import Karma

def run(code,pool_ls,inputs=None,show=False):
    dict_out={}
    [list_km,list_pt]=tools_basic.readSubCode_new(code)
    karma=list_km[0]
    name_ip=re.compile(r'^_\[input_?([\w]*)\]$')
    if inputs!=None:
        list_km=karma.allEffects()
        for km in list_km:
            name=name_ip.findall(km.m_symbol.m_name)
            if name!=[]:
                km.m_restricted=True
                map_res=inputs.get(name[0],[])
                if map_res==[]:
                    km.m_listMP=map_res
                else:
                    km.m_listMP=[map_res]

    pool=tools_basic.listToDict(pool_ls)
    state_re,pool,list_new=karma.Reason_iterative(pool,show)
    if state_re=='dark yellow':
        return state_re,dict_out
    name_op=re.compile(r'^\[output_?([\w]*)\]$')
    for point in list_new:
        name=name_op.findall(point.m_name)
        if name!=[]:
            list_out=dict_out.get(name[0],[])
            if point.m_db[1]!=None and point.m_db[1] not in list_out:
                list_out.append(point.m_db[1])
                dict_out.update({name[0]:list_out})
    return state_re,dict_out



if __name__=='__main__':
    list_pt=NetP('').build('a(,);b(,);b#2(a,);c(,)')
    list_pt[0].print()
    state_re,dict_out=run('r\'\w\'(,)->a(,)->[eq](a,~b)->~b(,)->_[input_a](,)->+[output](,_[input_a])',list_pt,{'a':list_pt[0]},0)
    print(dict_out)
    for term in dict_out:
        for point in dict_out[term]:
            point.print()