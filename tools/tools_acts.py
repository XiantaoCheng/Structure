import os, sys


def openFile(director):
    os.system('start '+director)

def createDev(dev_pt):
    if dev_pt.m_name=='[Brain]' or dev_pt.m_name=='[显示器]':
        from body.body_brain import Brain
        device=Brain(dev_pt.m_name)
    elif dev_pt.m_name=='[Hand]' or dev_pt.m_name=='[调试器]':
        from body.body_hand import Hand
        device=Hand(dev_pt.m_name)
    elif dev_pt.m_name=='[Mouth]' or dev_pt.m_name=='[命令行]':
        from body.body_mouth import Mouth
        device=Mouth(dev_pt.m_name)
    else:
        return None
    del device.m_self
    device.m_self=dev_pt
    dev_pt.m_dev=device
    return device

def updateDev(dev_pt):
    device=dev_pt.m_dev
    if device!=None and not device.isVisible():
        device.setVisible(True)
        device.update()