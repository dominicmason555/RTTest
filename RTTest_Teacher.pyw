#! /usr/bin/python3
# needed to specify python 3 instead of 2 on UNIX-like systems.

# Created by Dominic Mason

# This is the main file of the program, it creates threads for
# the other files to run in, or just imports from those files.
# The main window is created in this file, and it handles the GUI

# This file requires teacher_dialogs.py, teacher_db_manager.py,
# teacher_network_manager.py, teacher_db_handler.py, teacher_test_manager.py,
# main.db, mainwindowteacher.ui, teacher_edit_mc.ui, teacher_edit_sw.ui,
# config.ini and sip.pyd to be in the same directory

# If this program is run using the PyCharm IDE, then for unknown
# reasons the networking thread does not detect that any messages
# have been sent to it after it has received it's first message. 
# However the program works as intended on all the other IDEs 
# that it has been tested on, so it is probably a problem with 
# how PyCharm interfaces with the PyQt framework.

import sys, queue, json, pyqtgraph, configparser, datetime
import teacher_dialogs as di #The file containing the extra functions
import teacher_db_manager as db #The file containing the manager for the database
import teacher_network_manager as nw #The file containing the manager for the network
from PyQt5 import QtGui, QtCore, uic #Import the necessary modules from PyQt4.

def lockMethod(fn):
    '''Takes and releases the lock when executing a function if the thread is not already locked'''
    timestamp = None
    toLock = False
    def doWithLock(*args, **kwargs):
        self = args[0]
        toLock = True if not self.lock else False
        try:
            if toLock:
                timestamp = datetime.datetime.now()
                self.debugPrint("{1}\nMain thread locking for internal {0}\n{1}".format(fn.__name__, ("<>"*35)))
                self.lock = True
            return fn(*args, **kwargs)
        finally:
            if toLock:
                timed = (datetime.datetime.now() - timestamp).total_seconds() * 1000
                self.debugPrint("{1}\nMain thread unlocking from internal {0} ({2}ms)\n{1}".format(fn.__name__, ("<>"*35), timed))
                self.lock = False
    return doWithLock
# This is a function decorator. Whenever a function definition is preceded by "@lockMethod" it will be "wrapped" by this function.
# The function will first check if the thread is already locked, and if not then it will lock the thread. Then it will execute the
# function that has been passed to it using the "@lockMethod" decorator. Once that funciton has finished, it will then unlock
# the thread if it had to lock the thread before it ran the function. It will also show how long the function took to execute
# if debug mode is enabled. This means that if a function marked as a lockMethod is executed, it will not be interrupted by any
# items from the queues while it is executing. This provides greater safety for the program as it ensures that only one function
# runs at a time even though clients and the gui are requesting function calls at any time.


class MainTeacherWindow(QtGui.QMainWindow):
    '''This is the main window of the application, it controls the GUI and allows the teacher to control the server.
       This is created in the main thread, and it controls all of the actions of the database thread, and the majority
       of the actions of the network thread by sending and receiving requests and responses between the threads using
       the queues. All communication between the network thread and the database thread must first go through the
       main thread in order to ensure that the actions of the teacher have priority over the actions of the students.'''

    def closeEvent(self,event):
        '''Close the app when the close menu item clicked by first ensuring that it is safe to
           close the server and then killing the background threads that pyqtgraph creates.'''
        while not server.finish():
            pass
        print("Stopping Server")
        pyqtgraph.exit()

    @lockMethod
    def setTest(self, request=None):
        '''This function reads all of the GUI inputs of the set test tab and converts it into a request dictionary
           to send to the database thread for getting and weighting questions. It is called using the Set The Test
           button in the Set Test tab. It also cleans up all of the logs and graphs of results from the previous
           test if there was one, and it changes the tab to the View Results tab and shows the main answer log.'''
        storing = self.set_store_performance_check.isChecked()
        auto = self.set_auto_check.isChecked()
        selUsers = []
        for i in range(len(self.set_who_user_list.selectedIndexes())): # Get the selected users
            selUsers.append(self.logged_list_model.itemFromIndex(self.set_who_user_list.selectedIndexes()[i]).text())
        mcIDs = []
        swIDs = []
        for i in range(len(self.set_question_mc_tree.selectedIndexes())):
            mcIDs.append(int(self.mc_question_tree_model.itemFromIndex(
                                  self.set_question_mc_tree.selectedIndexes()[i]).text().split(":")[0]))
        for i in range(len(self.set_question_sw_tree.selectedIndexes())):
            swIDs.append(int(self.sw_question_tree_model.itemFromIndex(
                                  self.set_question_sw_tree.selectedIndexes()[i]).text().split(":")[0]))
        # Gets the question IDs of the selected questions
        requestOfTest = {"action":"setTest","users":selUsers, "mcIDs":mcIDs, "swIDs":swIDs, "storing":storing, "auto":auto}
        # This is what the database thread receives
        if not self.set_auto_check.isChecked():
            requestOfTest.update({"weighting":None})
        else:
            if self.set_topic_auto_question_radial.isChecked():
                requestOfTest.update({"weighting":"question"})
            else:
                requestOfTest.update({"weighting":"topic"})
            requestOfTest.update({"effect":self.set_topic_auto_percentage_slider.value()})
            requestOfTest.update({"length":self.set_question_number_spin.value()})
        # Specifies the weighting of the questions
        self.answer_log_all_model.clear()
        self.view_rt_graph.clear()
        for model in self.answer_logs:
            self.answer_logs[model].clear()
        for graph in self.graphDict:
            self.graphDict[graph].clear()
        # Cleans up the answer logs and graphs
        self.sendToDB(requestOfTest)
        self.showRTLog()
        self.main_tab.setCurrentIndex(1)
        # Shows the log and changes to the View Results tab

    @lockMethod
    def logPerformance(self, request):
        '''This function takes a message from the database thread that describes an answer that a student has given,
           once the database thread has checked to see if it is correct. It converts it in to two human-readable
           formats, a string called logString and a point to plot on the relevant scatter graphs. It also checks
           if the results of the user are stored in the user specific graph or log dictionaries, and if not it
           creates a user specific log and a user specific graph in the relevant dictionaries of the class, with
           the username as the key e.g. {"testUser1":<pyqtgraph.widgets.PlotWidget.PlotWidget object at 0x0000000004730C18>}'''
        request.update({"wordPassed":("correct" if request["passed"] else "incorrect")})
        request.update({"wordType":("multiple choice" if request["qType"] == "mc" else "single word")})
        logString = "User {username} got {wordType} question {QID} {wordPassed} in {time} seconds".format(**request)
        # Makes the result human-readable
        print(logString)
        self.answer_log_all_model.appendRow(QtGui.QStandardItem(logString))
        if request["username"] not in self.answer_logs:
            self.answer_logs[request["username"]] = QtGui.QStandardItemModel()
        self.answer_logs[request["username"]].appendRow(QtGui.QStandardItem(logString))
        # Adds the result to the relevant logs
        if self.RTLog and not self.RTLog.isHidden():
            QtCore.QTimer.singleShot(20, lambda: self.RTLog.scrollToBottom())
        # Ensures that the log automatically scrolls down if it is currently shown
        plotBrush = pyqtgraph.mkColor("b") if request["passed"] else pyqtgraph.mkColor("r")
        plotSymbol = 'o' if request["qType"] == "mc" else'd'
        self.view_rt_graph.scatterPlot([request["QID"]], [request["time"]], pen=None, brush=plotBrush ,symbol=plotSymbol)
        if request["username"] not in self.graphDict:
            self.graphDict[request["username"]] = pyqtgraph.PlotWidget()
            self.graphDict[request["username"]].setWindowTitle("Graph of {}'s results in real time".format(request["username"]))
            title = "Graph of results of {} where blue is correct, red is incorrect, <br>diamonds are single word questions and circles are multiple choice questions".format(request["username"])
            self.graphDict[request["username"]].setTitle(title)
            self.graphDict[request["username"]].setMinimumHeight(250)
            self.graphDict[request["username"]].setMinimumWidth(500)
            self.graphDict[request["username"]].setLabels(bottom="Question ID", left="Time to Answer")
            self.graphDict[request["username"]].resize(500,250)
        self.graphDict[request["username"]].scatterPlot([request["QID"]], [request["time"]], pen=None, brush=plotBrush, symbol=plotSymbol)
        # Plots the result on the relevant graphs
        self.nwSendQueue.put({"action":"nextQuestion","username":request["username"]})
        # Sends the network thread a request to give the user their next question if there is one available

    def showRTLogSpecific(self):
        '''Shows the answer log for a specific user'''
        selected = self.view_rt_specific_user_dropdown.currentText()
        self.showRTLog(selected)

    def showRTLog(self, user=None):
        '''Shows the answer log for either all users or a secific user'''
        if not user:
            if not self.RTLog:
                self.RTLog = di.RTAnswersLogDialog(self.answer_log_all_model)
            if self.RTLog.isHidden():
                self.RTLog.show()
        else:
            if user in self.answer_logs:
                self.answer_dialogs[user] = di.RTAnswersLogDialog(self.answer_logs[user])

    def showRTGraphSpecific(self):
        '''Shows the graph for a specific user'''
        selected = self.view_rt_specific_user_dropdown.currentText()
        if selected in self.graphDict:
            self.graphDict[selected].show()

    def showRTGraphs(self):
        '''Shows the graphs for all users'''
        for user in self.graphDict:
            self.graphDict[user].show()

    def adminUserAddBtn(self):
        '''Shows the dialog for adding a user'''
        self.addUserDialog = di.AddEditUserDialog(self.dbSendQueue)

    def adminUserEditBtn(self):
        '''Shows the same dialog for editing a user'''
        try:
            selected = self.user_list_model.data(self.admin_user_list.selectedIndexes()[0])
            self.addUserDialog = di.AddEditUserDialog(self.dbSendQueue, selected)
        except:
            self.ackCompleted({"error":True,"errorText":"Error Editing User"})

    def adminUserRemoveBtn(self):
        '''Removes the currently selected user'''
        try:
            selected = self.user_list_model.data(self.admin_user_list.selectedIndexes()[0])
            self.sendToDB({"action":"removeUser", "username":selected})
        except:
            self.ackCompleted({"error":True,"errorText":"Error Removing User"})

    def adminTopicAddBtn(self):
        '''Shows the dialog for adding a topic'''
        self.addQuestionDialog = di.AddEditTopicDialog(self.dbSendQueue)

    def adminTopicEditBtn(self):
        '''Shows the dialog for editing a topic'''
        try:
            selected = self.topic_list_model.data(self.admin_topic_list.selectedIndexes()[0]).split(": ")
            self.addTopicDialog = di.AddEditTopicDialog(self.dbSendQueue, selected)
        except:
            self.ackCompleted({"error":True,"errorText":"Error Editing Topic"})

    def adminTopicRemoveBtn(self):
        '''Removes the currently selected topic'''
        try:
           selected = self.topic_list_model.data(self.admin_topic_list.selectedIndexes()[0]).split(": ")
           self.sendToDB({"action":"removeTopic", "name":selected[1], "id":selected[0]})
        except:
           self.ackCompleted({"error":True,"errorText":"Error Removing Topic"})

    def adminMCQAddBtn(self):
        '''Shows the dialog for adding a multiple choice question'''
        self.addQuestionDialog = di.AddEditMCQDialog(self.dbSendQueue)

    def adminMCQEditBtn(self):
        '''Sends a request to the database thread to get the data of the question before editing it'''
        try:
            question = self.mc_question_tree_model.itemFromIndex(
                            self.admin_questions_mc_tree.selectedIndexes()[0]).text().split(": ")
            self.sendToDB({"action":"updateGui", "data":"MCEdit", "eType":"MCQ", "qid":question[0]})
        except:
            self.ackCompleted({"error":True,"errorText":"Error Editing MC Question"})

    def editMCQuestion(self, request):
        '''Shows the dialog for editing a multiple choice question'''
        print("Editing MC Question")
        if not request["response"]:
            self.ackCompleted({"error":True,"errorText":"Error Editing MC Question"})
            return
        self.addQuestionDialog = di.AddEditMCQDialog(self.dbSendQueue, question=request["response"])

    def adminMCQRemoveBtn(self):
        '''Requests that the database thread delete the question and all results associated with it'''
        try:
            question = self.mc_question_tree_model.itemFromIndex(
                            self.admin_questions_mc_tree.selectedIndexes()[0]).text().split(": ")
            self.sendToDB({"action":"removeQuestion", "qType":"MC", "qid":question[0]})
        except:
            self.ackCompleted({"error":True,"errorText":"Error Removing MC Question"})

    def adminSWQAddBtn(self):
        '''Shows the dialog for adding a single word question'''
        self.addQuestionDialog = di.AddEditSWQDialog(self.dbSendQueue)

    def adminSWQEditBtn(self):
        '''Sends a request to the database thread to get the data of the question before editing it'''
        try:
            question = self.sw_question_tree_model.itemFromIndex(
                            self.admin_questions_sw_tree.selectedIndexes()[0]).text().split(": ")
            self.sendToDB({"action":"updateGui", "data":"SWEdit", "eType":"SWQ", "qid":question[0]})
        except:
            self.ackCompleted({"error":True,"errorText":"Error Editing SW Question"})

    def editSWQuestion(self, request):
        '''Shows the dialog for editing a single word question'''
        if not request["response"]:
            self.ackCompleted({"error":True,"errorText":"Error Editing SW Question"})
            return
        self.addQuestionDialog = di.AddEditSWQDialog(self.dbSendQueue, question=request["response"])

    def adminSWQRemoveBtn(self):
        '''Requests that the database thread delete the question and all results associated with it'''
        try:
            question = self.sw_question_tree_model.itemFromIndex(
                            self.admin_questions_sw_tree.selectedIndexes()[0]).text().split(": ")
            self.sendToDB({"action":"removeQuestion", "qType":"SW", "qid":question[0]})
        except:
            self.ackCompleted({"error":True,"errorText":"Error Removing SW Question"})

    def adminResultsTopicBtn(self):
        '''Requests that the database thread delete all results associated with the topic'''
        topicID = window.admin_results_topic_combo.currentText().split(": ")[0]
        self.sendToDB({"action":"removeResults", "id":topicID, "type":"topic",
                              "completed":"Results Sucessfully Deleted", "errorText":"Failed to Delete Results"})

    def adminResultsUserBtn(self):
        '''Requests that the database thread delete all results associated with the user'''
        username = window.admin_results_user_combo.currentText()
        self.sendToDB({"action":"removeResults", "username":username, "type":"user",
                              "completed":"Results Sucessfully Deleted", "errorText":"Failed to Delete Results"})

    def ackCompleted(self, request):
        '''This will display a dialog to either confirm the success of an action or display an error from any thread'''
        self.msgBox = QtGui.QMessageBox()
        if request["error"]:
            text = request["errorText"]
        else:
            text = request["completed"]
        self.msgBox.setText(text)
        self.msgBox.setWindowTitle("Info")
        self.msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
        self.msgBox.show()
        if not request["error"]:
            self.refreshAllViews()

    @lockMethod
    def refreshAllViews(self, checked=False):
        '''Request the data for all of the views in the GUI from the relevant threads'''
        self.sendToDB({"action":"updateGui","data":"SWQT", "model":self.sw_question_tree_model, "eType":"tree"})
        self.sendToDB({"action":"updateGui","data":"MCQT", "model":self.mc_question_tree_model, "eType":"tree"})
        self.sendToDB({"action":"updateGui","data":"topics", "model":self.topic_list_model, "eType":"list"})
        self.sendToDB({"action":"updateGui","data":"users", "model":self.user_list_model, "eType":"list"})
        self.nwSendQueue.put({"action":"updateGui", "data":"loggedIn", "model":self.logged_list_model, "eType":"list"})
        self.sendToDB({"action":"updateGui", "data":"graphScale", "eType":"graph"})

    def showAddress(self, message):
        '''Display the correct IP address at the bottom of the GUI'''
        self.set_ip_label.setText(message["address"].toString())
        self.set_port_box.setValue(message["port"])

    def sendMessage(self, message):
        '''Format a message for the network thread to send, send it to the network thread and print the message'''
        username = message["client"].getUsername()
        client = message["client"]
        message = self.hideClient(message)
        self.nwSendQueue.put({"action":"send", "username":username, "client":client, "message":message})
        print("Sent:     \'{}\' to   {}".format(str(message), username))

    def hideClient(self, message):
        '''Remove the client object from a message so it can be cleanly printed'''
        clean = dict(message)
        clean.pop("client")
        return clean

    @lockMethod
    def changePort(self):
        '''Set the port number in the config file so that the next time the program starts, it will use the new value'''
        request = {"completed":"Port Changed Successfully\nThe program must be restarted for this to take effect",
                    "error":"Failed to change port","error":False}
        newPort = str(self.set_port_box.value())
        cfg = configparser.ConfigParser()
        try:
            cfg.read("config.ini")
            cfg.set("DEFAULT", "PORT", newPort)
            print("Set port to", newPort)
            with open('config.ini', 'w') as file:
                cfg.write(file)
        except:
            print("Failed to set port number to config.ini")
            request.update({"error":True})
        self.ackCompleted(request)

    def getAnswerLog(self, request):
        '''Get a client's results to send them to them at the end of the test'''
        print("Getting results for",request["username"])
        if request["username"] not in self.answer_logs:
            return
        log = self.answer_logs[request["username"]]
        textFromLog = []
        for i in range(log.rowCount()):
            textFromLog.append(log.data(log.index(i,0)))
        request["log"] = textFromLog
        self.nwSendQueue.put(request)

    def redirectToNW(self, request):
        '''Redirect a request to the network thread'''
        self.nwSendQueue.put(request)

    def redirectToDB(self, request):
        '''Redirect a reqeust to the database thread'''
        self.sendToDB(request)

    def processListRequest(self, request):
        '''Used for debugging the database thread, not used in standard execution, prints out the data of the request'''
        try:
            print(request["response"])
        except:
            print("Error Listing Request")

    def processGuiViewRequest(self, request):
        '''Appends the QtGui StandardItemRows in request["response3"] to the model in request["model"]'''
        model = request["model"]
        model.clear()
        root = model.invisibleRootItem()
        for i in request["response3"]:
            root.appendRow(i)
        self.set_question_mc_tree.expandAll()
        self.set_question_sw_tree.expandAll()
        self.admin_questions_mc_tree.expandAll()
        self.admin_questions_sw_tree.expandAll()

    def debugPrint(self, msg):
        '''If debug has been enabled from the menu item, print extra information'''
        if self.debug:
            print(msg)

    def sendToDB(self, request):
        '''Prints the requests sent to the database if debug mode is enabled'''
        self.debugPrint("Sending {} to database".format(request))
        self.dbSendQueue.put(request)

    def toggleDebug(self):
        '''Toggles the debug prints for extra information'''
        self.debug = not self.debug
        dbMgr.setDebug(self.debug)
        server.setDebug(self.debug)
        print("Debug:",self.debug, "\n")

    def graphPastSpecific(self):
        '''Opens the graph dialog for the user selected in the drop down menu, using self.graphDict with the username as the key'''
        selected = self.view_specific_user_dropdown.currentText()
        mcID = None
        swID = None
        if self.view_past_mc_tree.selectedIndexes():
            mcID = int(self.mc_question_tree_model.itemFromIndex(
                                  self.view_past_mc_tree.selectedIndexes()[0]).text().split(":")[0])
        if self.view_past_sw_tree.selectedIndexes():
            swID = int(self.sw_question_tree_model.itemFromIndex(
                                  self.view_past_sw_tree.selectedIndexes()[0]).text().split(":")[0])
        if not mcID and not swID:
            self.ackCompleted({"error":True, "errorText":"Please select a question"})
            return
        self.sendToDB({"action":"updateGui", "data":"graphResults", "eType":"graphResults", "user":selected, "mcID":mcID, "swID":swID})

    def graphPastAll(self):
        '''Opens a graph dialog for every user in self.graphDict'''
        mcID = None
        swID = None
        if self.view_past_mc_tree.selectedIndexes():
            mcID = int(self.mc_question_tree_model.itemFromIndex(
                                  self.view_past_mc_tree.selectedIndexes()[0]).text().split(":")[0])
        if self.view_past_sw_tree.selectedIndexes():
            swID = int(self.sw_question_tree_model.itemFromIndex(
                                  self.view_past_sw_tree.selectedIndexes()[0]).text().split(":")[0])
        if not mcID and not swID:
            self.ackCompleted({"error":True, "errorText":"Please select a user"})
            return
        self.sendToDB({"action":"updateGui", "data":"graphResults", "eType":"graphResults", "mcID":mcID, "swID":swID})

    def showPastGraph(self, request):
        '''This compiles the data from the database into a scatter plot, creates a dialog, adds the plot to the dialog
           and stores the dialog in the list: self.openGraphs so that the dialog is not destroyed by the garbage
           collector when the function ends'''
        if "swResults" in request:
            results = request["swResults"]
        else:
            results = request["mcResults"]
        if "user" not in request:
            request["user"] = "all users"
        results = sorted(results, key=lambda i: i[4])
        lengths = []
        colours = []
        for item in results:
            lengths.append(item[5])
            if item[6]:
                colours.append(pyqtgraph.mkColor("b"))
            else:
                colours.append(pyqtgraph.mkColor("r"))
        pw = pyqtgraph.PlotWidget()
        pi = pw.getPlotItem()
        pi.scatterPlot(lengths, brush=colours, antialias=True, symbol="d")
        pi.setLabels(bottom="Attempt Number", left="Time to Answer")
        pi.setTitle("Graph of past results of {} where blue is correct and red is incorrect".format(request["user"]))
        pw.setWindowTitle("Past results of {}".format(request["user"]))
        pw.show()
        pw.resize(600, 300)
        self.openGraphs.append(pw)

    def processGuiGraphRequest(self, request):
        '''This sets the scale of the main graph from 1 to the largest question ID in the database when the program loads'''
        self.debugPrint("Graph scale: {}".format(request["response"]))
        if request["data"] == "graphScale":
            self.view_rt_graph.setXRange(1,request["response"])

    def processQuestionRequest(self, request):
        '''Routes question requests by question type'''
        if request["data"] == "MCEdit":
            self.editMCQuestion(request)
        if request["data"] == "SWEdit":
            self.editSWQuestion(request)

    def processGuiRequest(self, request):
        '''Routes gui requests to the relevant functions'''
        if request["data"] == "refresh":
            self.refreshAllViews()
            return
        cases = {
                "tree" : self.processGuiViewRequest,
                "list" : self.processGuiViewRequest,
                "MCQ" : self.processQuestionRequest,
                "SWQ" : self.processQuestionRequest,
                "graph": self.processGuiGraphRequest,
                "graphResults": self.showPastGraph
                }
        try:
            case = cases[request["eType"]]
        except KeyError:
            print("Error selecting eType from Gui request")
            print("Action:", request["eType"])
            return
        case(request)

    def ignoreRequest(self, request):
        '''This does nothing with the request, it is not used in the finished program'''
        pass

    def processDatabaseMessage(self):
        '''Decide what to do with requests from the database thread in its queue by using the python equivalent of a switch statement.
           The function uses a dictionary with strings from request["action"] as keys and functions in the class as values.
           It matches an action to the relevant function, and more than one action can map to the same function. If the
           action is not found in the dictionary then it prints that the action wasnt found and does nothing.'''
        try:
            queueLength = self.dbReceiveQueue.qsize()
            request = self.dbReceiveQueue.get_nowait()
            self.debugPrint("Main Thread Recieved: {} from DBM\n".format(request))
        except:
            print("Error decoding database response in main thread")
        # Error handling in case the queue is somehow checked while empty, which only happens if checkForMessages is broken
        try:
            assert request
        except AssertionError:
            print("No data from databse, db file may be missing")
            self.ackCompleted({"errorText":"No data from databse, db file may be missing", "error":True})
            self.dbReceiveQueue.task_done()
            return
        # Cancel the function if the request is empty
        cases = {
                "list": self.processListRequest,
                "updateGui": self.processGuiRequest,
                "addUser": self.ackCompleted,
                "removeUser": self.ackCompleted,
                "editUser": self.ackCompleted,
                "addTopic": self.ackCompleted,
                "removeTopic": self.ackCompleted,
                "editTopic": self.ackCompleted,
                "acceptLogin": self.redirectToNW,
                "denyLogin": self.redirectToNW,
                "getSalt": self.sendMessage,
                "answer": self.logPerformance,
                "removeResults": self.ackCompleted,
                "addEditQuestion": self.ackCompleted,
                "removeQuestion": self.ackCompleted,
                "setTest": self.redirectToNW
                }
        try:
            case = cases[request["action"]]
        except KeyError:
            print("Error selecting action from database request")
            print("Action:", request["action"])
            return
        # Match the action to a function, or handle if there isnt a match
        try:
            timestamp = datetime.datetime.now()
            self.lock = True
            log = "{1}\nMain thread locking for {0} from database thread ({2} item(s) in queue)\n{1}"
            self.debugPrint(log.format(request["action"], ("<>"*40), queueLength))
            case(request)
        finally:
            timed = round(((datetime.datetime.now() - timestamp).total_seconds() * 1000), 2)
            self.lock = False
            log = "{1}\nMain thread unlocking from {0} from database thread ({2}ms)\n{1}"
            self.debugPrint(log.format(request["action"], ("<>"*40), timed))
            self.dbReceiveQueue.task_done()
        # Lock the thread, execute the function, unlock the thread and inform the database queue that the task has finished
        # Also, in debug mode print the details of the request and the lock and unlock, and how long the function took to execute

    def processNetworkMessage(self):
        '''Decide what to do with requests from the network thread in its queue by using the python equivalent of a switch statement.
           The function uses a dictionary with strings from request["action"] as keys and functions in the class as values.
           It matches an action to the relevant function, and more than one action can map to the same function. If the
           action is not found in the dictionary then it prints that the action wasnt found and does nothing.'''
        try:
            queueLength = self.nwReceiveQueue.qsize()
            request = self.nwReceiveQueue.get_nowait()
        except:
            print("Error processing network request in main thread")
        # Error handling in case the queue is somehow checked while empty, which only happens if checkForMessages is broken
        if not request:
            self.nwReceiveQueue.task_done()
            return
        # Cancel the funciton if the request is empty
        if type(request["client"]) == nw.Client:
            clean = str(self.hideClient(request))
            self.debugPrint("Received: \'{}\' from {}\n".format(clean, request["client"].getUsername()))
        # If the request is from a client rather than the thread itself and debug mode is enabled, print it.
        cases = {
                "echo": self.sendMessage,
                "login": self.redirectToDB,
                "getSalt": self.redirectToDB,
                "updateGui": self.processGuiRequest,
                "showAddress": self.showAddress,
                "answer": self.redirectToDB,
                "getAnswerLog": self.getAnswerLog
                }
        try:
            case = cases[request["action"]]
        except KeyError:
            print("Error selecting action from network request")
            print("Action:", request["action"])
            return
        # Match the action to a function, or handle if there isnt a match
        try:
            timestamp = datetime.datetime.now()
            self.lock = True
            log = "{1}\nMain thread locking for {0} from network thread ({2} item(s) in queue)\n{1}"
            self.debugPrint(log.format(request["action"], ("<>"*40), queueLength))
            case(request)
        finally:
            timed = round(((datetime.datetime.now() - timestamp).total_seconds() * 1000), 2)
            log = "{1}\nMain thread unlocking from {0} from network thread ({2}ms)\n{1}"
            self.debugPrint(log.format(request["action"], ("<>"*40), timed))
            self.lock = False
            self.nwReceiveQueue.task_done()
        # Lock the thread, execute the function, unlock the thread and inform the network queue that the task has finished
        # Also, in debug mode print the details of the request and the lock and unlock, and how long the function took to execute

    def checkForMessages(self):
        '''This function is integrated into the QT event loop so that  if it has been 1ms since the last time, when QT is checking
           if it needs to update the gui, then it will run this function, which will check the queues for something to do if the
           thread is not currently locked'''
        if not self.lock:
            if not self.nwReceiveQueue.empty():
                self.processNetworkMessage()
            if not self.dbReceiveQueue.empty():
                self.processDatabaseMessage()

    def __init__(self):
        super().__init__()
        # Initialise QtGui.QMainWindow, which is written in C++
        uic.loadUi('mainwindowteacher.ui', self)
        # This loads the .ui file, which is an XML representation of the GUI
        # which was created using QT Designer.
        self.debug = False
        self.lock = False
        self.answer_log_all_model = QtGui.QStandardItemModel()
        self.answer_logs = {}
        self.answer_dialogs = {}
        self.graphDict = {}
        self.openGraphs = []
        self.RTLog = None
        # These are items which have to be remembered for the duration of the program
        # If these were not attributes of the class, then python's garbage collector
        # would delete them when they leave the scope of the function that interacts
        # with them.
        self.actionRefresh_All_Views.triggered.connect(self.refreshAllViews)
        self.admin_user_add_btn.clicked.connect(self.adminUserAddBtn)
        self.admin_user_edit_btn.clicked.connect(self.adminUserEditBtn)
        self.admin_user_remove_btn.clicked.connect(self.adminUserRemoveBtn)
        self.admin_questions_mc_add_btn.clicked.connect(self.adminMCQAddBtn)
        self.admin_questions_mc_edit_btn.clicked.connect(self.adminMCQEditBtn)
        self.admin_questions_mc_remove_btn.clicked.connect(self.adminMCQRemoveBtn)
        self.admin_questions_sw_add_btn.clicked.connect(self.adminSWQAddBtn)
        self.admin_questions_sw_edit_btn.clicked.connect(self.adminSWQEditBtn)
        self.admin_questions_sw_remove_btn.clicked.connect(self.adminSWQRemoveBtn)
        self.admin_topic_add_btn.clicked.connect(self.adminTopicAddBtn)
        self.admin_topic_remove_btn.clicked.connect(self.adminTopicRemoveBtn)
        self.admin_topic_edit_btn.clicked.connect(self.adminTopicEditBtn)
        self.view_rt_all_console_btn.clicked.connect(self.showRTLog)
        self.view_rt_specific_console_btn.clicked.connect(self.showRTLogSpecific)
        self.admin_results_topic_btn.clicked.connect(self.adminResultsTopicBtn)
        self.admin_results_user_btn.clicked.connect(self.adminResultsUserBtn)
        self.actionClose.triggered.connect(lambda: self.closeEvent(self.actionClose))
        #Lambda functions are required to connect Qt signals to function calls
        #with arguments by creating an anonymous function with no arguments
        #that calls the real function with the correct arguments.
        self.actionToggle_Debug.triggered.connect(self.toggleDebug)
        self.set_test_link.clicked.connect(self.setTest)
        self.set_port_btn.clicked.connect(self.changePort)
        self.view_rt_specific_line_btn.clicked.connect(self.showRTGraphSpecific)
        self.view_rt_all_line_btn.clicked.connect(self.showRTGraphs)
        self.view_past_specific_line_btn.clicked.connect(self.graphPastSpecific)
        self.view_past_all_line_btn.clicked.connect(self.graphPastAll)
        # Connect all of the QT signals such as items in the gui being clicked
        # to their relevant functions
        self.nwReceiveQueue = queue.Queue()
        self.nwSendQueue = queue.Queue()
        self.dbReceiveQueue = queue.Queue()
        self.dbSendQueue = queue.Queue()
        # These are the queues used to transfer requests and responses between the threads
        self.sw_question_tree_model = QtGui.QStandardItemModel()
        self.set_question_sw_tree.setModel(self.sw_question_tree_model)
        self.view_past_sw_tree.setModel(self.sw_question_tree_model)
        self.admin_questions_sw_tree.setModel(self.sw_question_tree_model)
        self.mc_question_tree_model = QtGui.QStandardItemModel()
        self.set_question_mc_tree.setModel(self.mc_question_tree_model)
        self.view_past_mc_tree.setModel(self.mc_question_tree_model)
        self.admin_questions_mc_tree.setModel(self.mc_question_tree_model)
        self.user_list_model = QtGui.QStandardItemModel()
        self.admin_user_list.setModel(self.user_list_model)
        self.admin_results_user_combo.setModel(self.user_list_model)
        self.view_specific_user_dropdown.setModel(self.user_list_model)
        self.topic_list_model = QtGui.QStandardItemModel()
        self.admin_topic_list.setModel(self.topic_list_model)
        self.admin_results_topic_combo.setModel(self.topic_list_model)
        self.logged_list_model = QtGui.QStandardItemModel()
        self.set_who_user_list.setModel(self.logged_list_model)
        self.view_rt_specific_user_dropdown.setModel(self.logged_list_model)
        # These are the data models for the program. in QT, the models of the data are
        # separate from the views where you can see them, and updatting the model
        # updates all views that view it automatically. This is very useful for the
        # topic/question trees and the answer logs.
        self.setFixedSize(self.size())
        self.refreshAllViews()
        self.view_rt_graph.setLabels(left="Time to Answer", bottom="Question ID")
        self.show()
        # Show the main GUI after initialising
        print("Main window loaded\n")
        self.constantTimer = QtCore.QTimer()
        self.constantTimer.timeout.connect(self.checkForMessages)
        self.constantTimer.start(1)
        print("Began Queue Checking")
        # Integrate the checkForMessages function into the QT event loop, with
        # a delay between calls of 1 millisecond



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setStyle(QtGui.QStyleFactory.create("gtk+"))
    # Set the GUI to the native style for the platform
    cfg = configparser.ConfigParser()
    try:
        cfg.read("config.ini")
        port = int(cfg["DEFAULT"]["PORT"])
        print("Using port",port)
    except:
        port = None
        print("Failed to load port number from config.ini")
    # Try to load the port for the server from config.ini
    window = MainTeacherWindow()
    # Creates the main window
    dbThread = QtCore.QThread()
    dbMgr = db.Mgr(window.dbReceiveQueue, window.dbSendQueue)
    dbMgr.moveToThread(dbThread)
    dbThread.started.connect(dbMgr.run)
    dbThread.start()
    # Creates the database manager, then moves it to its own thread and starts it
    serverThread = QtCore.QThread()
    server = nw.Server(window.nwReceiveQueue, window.nwSendQueue, port)
    server.moveToThread(serverThread)
    serverThread.started.connect(server.run)
    serverThread.start()
    # Creates the network manager, then moves it to its own thread and starts it
    app.exec_()
    # Runs the application
