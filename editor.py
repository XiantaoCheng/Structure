import sys
from body.body_textEditor import Editor
from PyQt5.QtWidgets import QApplication, QMessageBox
# import matlab.engine

if __name__=="__main__":
    app=QApplication(sys.argv)
    testFile="benchmarks\\TuringMachine.snb"
    ed=Editor('editor')
    sys.argv.append(testFile)
    
    if len(sys.argv)<2:
        QMessageBox.warning(ed,"Open fail!","Invalid file name!")
    else:
        ed.openFile(sys.argv[1])
    sys.exit(app.exec_())