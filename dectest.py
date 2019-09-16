def countF(file):
    with open(file) as f:
        contents = f.read()
    c = contents.count("def ")
    print("%-26s : %-4i functions" % (file, c))
    return c

def countL(file):
    with open(file) as f:
        total = sum(1 for line in f)
    print("{:<26} : {:<4} lines".format(file, total))
    return total

files = ["RTTest_Teacher.pyw","RTTest_Student.pyw","teacher_db_handler.py","teacher_db_manager.py",
         "teacher_network_manager.py","teacher_dialogs.py", "teacher_test_manager.py"]

totalF = 0
totalL = 0
for file in files:
    totalF += countF(file)
print()
for file in files:
    totalL += countL(file)
print()
print("Total files                :", len(files))
print("Total functions            :", totalF)
print("Total lines                :", totalL)
print("Mean lines per file        :", (totalL // len(files)))
print("Mean functions per file    :", (totalF // len(files)))
print("Mean lines per function    :", ((totalL // totalF)-1))
##
if 1:
    print(0)
elif(1):
    print(1)
##

import random
from PyQt4 import QtGui
sim = QtGui.QStandardItemModel()
for i in range(10):
    sim.appendRow(QtGui.QStandardItem(str(random.randint(0,100))))
for i in range(sim.rowCount()):
    print(sim.data(sim.index(i,0)))

##

import random
choiceList = []
for i in range(10):
    choiceList.append({"name":chr(i+97), "weight":random.randint(0,100)})
print(sorted(choiceList, key = lambda k: k["weight"]), "\n\n")
total = 0
for item in choiceList:
    item["start"] = total
    item["end"] = total + item["weight"]
    total += item["weight"]
print(choiceList)
choice = random.randint(0,total)
print(choice)
for item in choiceList:
    if item["start"] <= choice and item["end"] >= choice:
        print("Chosen:", item)

##

import sqlite3, datetime, time

conn = sqlite3.connect("test.db", detect_types=sqlite3.PARSE_DECLTYPES)
cursor = conn.cursor()

try:
    #cursor.execute("create table test (col1 INTEGER PRIMARY KEY AUTOINCREMENT, col2 timestamp)")
    cursor.execute("insert into test values (NULL, ?)", (datetime.datetime.now(),))
    cursor.execute("select * from test")
    all = cursor.fetchall()
    print(all)
    time.sleep(1)
    print(datetime.datetime.now() - all[-1][1])
finally:
    cursor.close()
    conn.commit()
    conn.close()

def lockMethod(fn):
    def doWithLock(*args, **kwargs):
        self = args[0]
        try:
            print("\n=========\nLocking for {} from GUI".format(fn.__name__))
            self.lock = True
            return fn(*args, **kwargs)
        finally:
            print("Unlocking from {}\n=========\n".format(fn.__name__))
            self.lock = False
    return doWithLock
    
class TestClass():
    def __init__(self):
        self.lock = False
    @lockMethod
    def test(self):
        print("Doing a thing with lock being", self.lock)
        
t = TestClass()
print("Lock is", t.lock)
t.test()
lockMethod(t.test)
print("Lock is", t.lock)

t1 = datetime.datetime.now()
time.sleep(1)
t2 = datetime.datetime.now()
print(t1, t2)
print(str((t2-t1).total_seconds()*1000)+"ms")

##

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
  
app = QtGui.QApplication([])
view = pg.GraphicsView()
l = pg.GraphicsLayout(border=(100,100,100))
view.setCentralItem(l)
view.show()
view.setWindowTitle('pyqtgraph example: GraphicsLayout')
view.resize(800,600)
  
# Title at top
text = """
This example demonstrates the use of GraphicsLayout to arrange items in a grid.<br>
The items added to the layout must be subclasses of QGraphicsWidget (this includes <br>
PlotItem, ViewBox, LabelItem, and GrphicsLayout itself).
"""
l.addLabel(text, col=1, colspan=4)
l.nextRow()
  
# Put vertical label on left side
l.addLabel('Long Vertical Label', angle=-90, rowspan=3)
  
# Add 3 plots into the first row (automatic position)
p1 = l.addPlot(title="Plot 1")
p2 = l.addPlot(title="Plot 2")
vb = l.addViewBox(lockAspect=True)
img = pg.ImageItem(np.random.normal(size=(200,100)))
vb.addItem(img)
vb.autoRange()
  
  
# Add a sub-layout into the second row (automatic position)
# The added item should avoid the first column, which is already filled
l.nextRow()
l2 = l.addLayout(colspan=3, border=(50,0,0))
l2.setContentsMargins(10, 10, 10, 10)
l2.addLabel("Sub-layout: this layout demonstrates the use of shared axes and axis labels", colspan=3)
l2.nextRow()
l2.addLabel('Vertical Axis Label', angle=-90, rowspan=2)
p21 = l2.addPlot()
p22 = l2.addPlot()
l2.nextRow()
p23 = l2.addPlot()
p24 = l2.addPlot()
l2.nextRow()
l2.addLabel("HorizontalAxisLabel", col=1, colspan=2)
  
# hide axes on some plots
p21.hideAxis('bottom')
p22.hideAxis('bottom')
p22.hideAxis('left')
p24.hideAxis('left')
p21.hideButtons()
p22.hideButtons()
p23.hideButtons()
p24.hideButtons()
  
  
# Add 2 more plots into the third row (manual position)
p4 = l.addPlot(row=3, col=1)
p5 = l.addPlot(row=3, col=2, colspan=2)
  
# show some content in the plots
p1.plot([1,3,2,4,3,5])
p2.plot([1,3,2,4,3,5])
p4.plot([1,3,2,4,3,5])
p5.plot([1,3,2,4,3,5])
  
  
  
# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
        
##
import datetime, numpy
import pyqtgraph as pg
from PyQt4 import QtCore, QtGui

r2 = {'swResults': [(249, 'testUser2', 1, 3, datetime.datetime(2017, 3, 18, 17, 58, 33, 366947), 2, 1), (251, 'testUser2', 1, 3, datetime.datetime(2017, 3, 18, 17, 59, 33, 150596), 9, 0), (253, 'testUser2', 1, 3, datetime.datetime(2017, 3, 18, 17, 59, 50, 69794), 6, 1), (254, 'testUser2', 1, 3,datetime.datetime(2017, 3, 18, 19, 3, 3, 816326), 7, 1), (260, 'testUser2', 1, 3, datetime.datetime(2017, 3, 18, 21, 47, 23, 445805), 5, 0), (262,'testUser2', 6, 9, datetime.datetime(2017, 3, 18, 21, 47, 44, 598003), 21, 1), (316, 'testUser2', 1, 3, datetime.datetime(2017, 3, 20, 20, 29, 52,566050), 6, 1), (318, 'testUser2', 6, 9, datetime.datetime(2017, 3, 20, 20, 30, 26, 265532), 18, 1), (324, 'testUser2', 1, 3, datetime.datetime(2017, 3, 20, 21, 23, 10, 965521), 3, 1), (325, 'testUser2', 1, 3, datetime.datetime(2017, 3, 20, 21, 24, 29, 908353), 2, 1), (326, 'testUser2', 1, 3, datetime.datetime(2017, 3, 20, 21, 24, 31, 258236), 1, 1), (327, 'testUser2', 1, 3, datetime.datetime(2017, 3, 20, 21, 24, 32, 389064), 1, 1), (328, 'testUser2', 1, 3, datetime.datetime(2017, 3, 20, 21, 24, 34, 198702), 1, 0), (329, 'testUser2', 6, 9, datetime.datetime(2017, 3, 20, 21, 25, 6, 292412), 5, 1), (331, 'testUser2', 6, 9, datetime.datetime(2017, 3, 20, 21, 39, 7, 502457), 4, 1), (334, 'testUser2', 6, 9, datetime.datetime(2017, 3, 20, 21, 39, 14, 284585), 6, 0), (335, 'testUser2', 1, 3, datetime.datetime(2017, 3, 20, 21, 57, 59, 781783), 9, 1), (336, 'testUser2', 1, 3, datetime.datetime(2017, 3, 20, 21, 59, 46, 84877), 11, 1), (337, 'testUser2', 1, 3, datetime.datetime(2017, 3, 20, 22, 0, 0, 493230), 15, 1), (338, 'testUser2', 1, 3, datetime.datetime(2017, 3, 20, 22, 0, 3, 619117), 3, 0), (339, 'testUser2', 1, 3, datetime.datetime(2017, 3, 20, 22, 0, 6, 444920), 2, 0), (340, 'testUser2', 1, 3, datetime.datetime(2017, 3, 20, 22, 0, 8, 782584), 2, 1), (341, 'testUser2', 1, 3, datetime.datetime(2017, 3, 20, 22, 0, 11, 910182), 3, 1)], 'eType': 'graphResults', 'mcResults': [(55, 'testUser2', 3, 9, datetime.datetime(2017, 3, 7, 20, 15, 16, 817809), 10, 1), (58, 'testUser2', 1, 9, datetime.datetime(2017, 3, 7, 20, 15, 32, 17967), 2, 0), (62, 'testUser2', 1, 9, datetime.datetime(2017, 3, 7, 20, 16, 14, 818001), 9, 0), (64, 'testUser2', 1, 9, datetime.datetime(2017, 3, 7, 20, 17, 36, 742065), 2, 1), (65, 'testUser2', 3, 9, datetime.datetime(2017, 3, 7, 20, 18, 12, 570785), 36, 1), (66, 'testUser2', 1, 9, datetime.datetime(2017, 3, 7, 20, 18, 21, 657068), 9, 1), (112, 'testUser2', 3, 9, datetime.datetime(2017, 3, 7, 20, 29, 25, 993210), 4, 1), (113, 'testUser2', 1, 9, datetime.datetime(2017, 3, 7, 20, 30, 33, 312490), 68, 0), (114, 'testUser2', 1, 9, datetime.datetime(2017, 3, 7, 20, 30, 35, 912834), 2, 0), (118, 'testUser2', 3, 9, datetime.datetime(2017, 3, 7, 20, 30, 57, 224533), 20, 1), (121, 'testUser2', 1, 9, datetime.datetime(2017, 3, 7, 21, 43, 40, 956845), 3, 1), (323, 'testUser2', 2, 1, datetime.datetime(2017, 3, 18, 21, 48, 29, 382552), 44, 1), (324, 'testUser2', 1, 9, datetime.datetime(2017, 3, 18, 21, 48, 33, 814518), 5, 1), (326, 'testUser2', 3, 9, datetime.datetime(2017, 3, 18, 21, 48, 38, 382809), 4, 0), (378, 'testUser2', 3, 9, datetime.datetime(2017, 3, 20, 20, 30, 7, 771779), 15, 1), (380, 'testUser2', 2, 1, datetime.datetime(2017, 3, 20, 20, 30, 33, 520773), 8, 0), (381, 'testUser2', 2, 1, datetime.datetime(2017, 3, 20, 20, 30, 38, 182874), 4, 1), (382, 'testUser2', 1, 9, datetime.datetime(2017, 3, 20, 20, 30, 42, 255328), 4, 0), (384, 'testUser2', 1, 9, datetime.datetime(2017, 3, 20, 20, 30, 45, 116247), 3, 1), (385, 'testUser2', 3, 9, datetime.datetime(2017, 3, 20, 20, 30, 59, 238264), 14, 0), (386, 'testUser2', 3, 9, datetime.datetime(2017, 3, 20, 21, 23, 6, 782506), 2, 1), (387, 'testUser2', 3, 9, datetime.datetime(2017, 3, 20, 21, 23, 8, 309940), 1, 1), (388, 'testUser2', 2, 1, datetime.datetime(2017, 3, 20, 21, 24, 59, 988651), 2, 1), (389, 'testUser2', 2, 1, datetime.datetime(2017, 3, 20, 21, 25, 0, 925417), 1, 1), (392, 'testUser2', 2, 1, datetime.datetime(2017, 3, 20, 21, 25, 11, 261824), 5, 0), (394, 'testUser2', 1, 9, datetime.datetime(2017, 3, 20, 21, 41, 28, 69028), 1, 1), (396, 'testUser2', 1, 9, datetime.datetime(2017, 3, 20, 21, 41, 33, 13310), 5, 0)],'data': 'graphResults', 'action': 'updateGui', 'user': 'testUser2'}

lengths = []
correct = []
brushes = []
for item in r2["swResults"]:
    lengths.append(item[5])
    if item[6]:
        correct.append("o")
        brushes.append(pg.mkColor("r"))
    else:
        correct.append("x")
        brushes.append(pg.mkColor("g"))

pw = pg.PlotWidget()
pi = pw.getPlotItem()

print(lengths)
pi.scatterPlot(lengths, brush=brushes, antialias=True, symbol=correct)
pi.setLabels(bottom="Attempt Number", left="Time to Answer")
pi.setTitle("Graph of past results where O is correct and X is incorrect")
pw.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
pw.show()
pw.resize(600, 300)






