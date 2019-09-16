#! /usr/bin/python3
# needed to specify python 3 instead of 2 on UNIX-like systems.

# This is the client program, for the students to use
# to connect to the server. It only requires itself,
# mainwindowstudent.ui, studentconfig.ini and sip.pyd
# to be in its directory to run as long as all of the 
# modules are installed, the other files are for the
# server-side program

#Created by Dominic Mason

import sys, json, hashlib, time, configparser
from PyQt5 import QtWidgets, QtCore, QtNetwork, uic

class MainStudentWindow(QtWidgets.QMainWindow):
    '''This is the only window of the student program'''
    def login(self):
        '''When the login button is pressed, initiate the login sequence'''
        self.username = self.user_edit.text()
        self.password = self.pass_edit.text()
        self.address = self.address_edit.text()
        self.port = self.port_spin.value()
        # Get values from input widgets
        cfg = configparser.ConfigParser()
        try:
            cfg.read("studentconfig.ini")
            cfg.set("DEFAULT", "PORT", str(self.port))
            cfg.set("DEFAULT", "ADDRESS", self.address)
            with open('studentconfig.ini', 'w') as file:
                cfg.write(file)
        except:
            print("Failed to set port number to config.ini")
        # Save the address and port in the config file so
        # that they can be loaded automatically the next time.
        self.socket.connectToHost(self.address, self.port)
        # Attempt to connect to the server, if it fails
        # then the error will be handled by self.socketError
        request = {"realUsername":self.username, "action":"getSalt"}
        time.sleep(0.1)
        # Wait for 100ms to ensure that the socket has connected
        # properly on both ends
        self.sendMessage(request)
        # Request the password salt to use from the server
        
    def logout(self):
        '''Reset the program to its initial state and disconnect
           from the server'''
        self.username = ""
        self.password = ""
        self.socket.close()
        self.changePage("login")
        self.showMessage("Logged Out Successfully", "Info")
        
    def completeLogin(self, message):
        '''If the username is in the server's database, hash the
           password with the received salt and send the hash'''
        if not message["denied"]:
            hashed = self.createHash(self.password, message["salt"])
            request = {"action":"login", "realUsername":self.username, "password":hashed}
            self.sendMessage(request)
            # Request the login
        else:
            self.showMessage("Login Denied", "Info")
        # If the user was not in the database, there was no salt to send
        
    def verifyLogin(self, message):
        '''If the server accepts the login, change to the
           "waiting for question" page'''
        if message["login"] == "accepted":
            self.showMessage("Login Accepted", "Info")
            self.loggedIn = True
            self.changePage("wait")
        else:
            self.showMessage("Login Denied", "Info")
            
    def changePage(self, page):
        '''Changes to the page specified by the page parameter
           and handles resetting the contents of pages with 
           dynamic content'''
        self.lcdCount = 0
        self.lcdNumber.display(self.lcdCount)
        self.clockRunning = False
        # Reset the stop-clock at the top of the window
        if page == "login":
            self.stackedWidget.setCurrentIndex(0)
        if page == "wait":
            self.stackedWidget.setCurrentIndex(1)
        if page == "sw":
            self.stackedWidget.setCurrentIndex(2)
            self.sw_question_box.setText("")
            self.sw_answer_box.setText("")
            # Reset the content
        if page == "mc":
            self.stackedWidget.setCurrentIndex(3)
            self.mc_question_box.setText("")
            self.mc_answer_1.setText("Answer 1")
            self.mc_answer_2.setText("Answer 2")
            self.mc_answer_3.setText("Answer 3")
            self.mc_answer_3.setEnabled(False)
            self.mc_answer_4.setText("Answer 4")
            self.mc_answer_4.setEnabled(False)
            # Reset the conetent
        if page == "res":
            self.stackedWidget.setCurrentIndex(4)

    def showResults(self, message):
        '''Shoes the log of the results that the server sent'''
        self.changePage("res")
        # Switch to the results page
        text = ""
        for item in message["log"]:
            text = text + item + "\n"
        self.res_browse.setText(text)
        # Set the text browser's contents to the log in the request
        
    def showQuestion(self, message):
        '''Routes a question to the function for the question type'''
        self.topicID = message["topicID"]
        # The topic ID always has to be stored
        if message["qType"] == "sw":
            self.showSWQuestion(message)
        if message["qType"] == "mc":
            self.showMCQuestion(message)
        
    def showSWQuestion(self, message):
        '''Displays a single word question from a request'''
        self.changePage("sw")
        # Change to the single word question screen
        self.sw_question_box.setText(message["question"])
        # Set the question box's contents to the question
        self.swQID = message["QID"]
        # Store the question ID
        self.currentQuestion = True
        self.lcdCount = 0
        self.clockRunning = True
        # Start the stop-clock counting up
        
    def showMCQuestion(self, message):
        '''Displays a multiple choice question from a request'''
        self.changePage("mc")
        # Cahnges to the mupltiple choice question screen
        self.mc_question_box.setText(message["question"])
        self.mc_answer_1.setText(message["answer1"])
        self.mc_answer_2.setText(message["answer2"])
        # Show the question and first two answers which
        # must always be present
        if message["answer3"]:
            self.mc_answer_3.setText(message["answer3"])
            self.mc_answer_3.setEnabled(True)
            # If there is a third question, show it and
            # enable the user to choose it
            if message["answer4"]:
                self.mc_answer_4.setText(message["answer4"])
                self.mc_answer_4.setEnabled(True)
            # If there is a fourth question, show it and
            # enable the user to choose it
        self.mcQID = message["QID"]
        # Store the question ID
        self.mc_answer_1.setChecked(True)
        # Default to the first option being selected,
        # it is not possible to deselct all of the
        # options without completely re-implementing
        # the radio button behaviour from scratch
        self.currentQuestion = True
        self.clockRunning = True
        # Start the stop-clock counting up
        
    def submitMC(self):
        '''Submits the answer to a multiple choice question'''
        print("Submitting MC Question")
        mcSelection = self.checkMC()
        # Get the selected answer
        if not self.currentQuestion or not mcSelection:
            return
        # If there is not currently a question, 
        # this function shouldn't have been called
        self.clockRunning = False
        # Stop the stop-clock
        request = {"action":"answer", "qType":"mc", "QID":self.mcQID, "answer":mcSelection,
                    "time":self.lcdCount, "topicID":self.topicID}
        self.sendMessage(request)
        # Send all of the details of the answer
        self.changePage("wait")
        # Change back to the "Waiting for question" tab
        
    def checkMC(self):
        '''Gets the selected answer for a multiple choice question,
           with sanity checking'''
        selection = None
        if self.mc_answer_1.isChecked():
            selection = 1
        if self.mc_answer_2.isChecked():
            if selection:
                return False
            else:
                selection = 2
        if self.mc_answer_3.isChecked():
            if selection or not self.mc_answer_3.isEnabled():
                return False
            else:
                selection = 3
        if self.mc_answer_4.isChecked():
            if selection or not self.mc_answer_4.isEnabled():
                return False
            else:
                selection = 4
        # If a button that isnt enabled has been selected or
        # If more than one radio button is selected, something 
        # has gone wrong, so it won't return a choice.
        return selection
        
    def submitSW(self):
        '''Submits the answer to a single word question'''
        print("Submitting SW Question")
        if not self.currentQuestion:
            return
        # If there is not currently a question, 
        # this function shouldn't have been called
        self.clockRunning = False
        # Stop the stop-clock
        request = {"action":"answer", "qType":"sw", "QID":self.swQID, "answer":self.checkSW(),
                    "time":self.lcdCount, "topicID":self.topicID}
        self.sendMessage(request)
        # Send all of the details of the answer
        self.changePage("wait")
        # Change back to the "Waiting for question" tab
        
    def checkSW(self):
        '''Returns the lower-case version of the answer, 
           with whitespace removed'''
        raw  = self.sw_answer_box.text()
        return raw.lower().strip()
        
    def tickUp(self):
        '''Increment the value of the stop-clock by one
           second, unless it would cause an overflow'''
        if self.clockRunning:
            if self.lcdNumber.intValue() < 999998:
                self.lcdCount += 1
            else:
                self.ldCount = 999999
            self.lcdNumber.display(self.lcdCount)
            
    def createHash(self, password, salt):
        '''Hashes a password with the salt from the
           server's database'''
        saltedPass = salt + password
        for i in range(1000):
            saltedPass = hashlib.sha512(saltedPass.encode("utf-8")).hexdigest()
        # 1000 rounds of sha512 is a lot more than is necessary, but the
        # more secure the better.
        final = salt + "|==|" + saltedPass
        # This is the format that is stored in the server's database
        print("Hash: {}".format(final))
        return str(final)
        
    def receiveMessage(self):
        '''Extract the message from the server's socket in the form of
           a QDataStream, then read the stream as a QString, then use
           the JSON module to convert it from JSON into a dictionary
           and then process it as a request'''
        stream = QtCore.QDataStream(self.socket)
        stream.setVersion(QtCore.QDataStream.Qt_5_13)
        # The streams have to have the same version for compatability
        # between the two programs and all data that goes through
        # is converted to Qt's platform independant data types such as QString
        # which are made of C++ types. This means that the server and client could have
        # different architectures, different word lengths, different operating
        # systems or even be written in different languages and in theory they 
        # could still communicate
        while True:
            if self.nextBlockSize == 0:
                if self.socket.bytesAvailable() < self.INTSIZE:
                    break
                # If there is not enough data for an integer representing the
                # number of "blocks" left to transmit, then the transmission has
                # finished
                self.nextBlockSize = stream.readUInt32()
                # Read the remaining number of "blocks" from the stream
            if self.socket.bytesAvailable() < self.nextBlockSize:
                break
            # There has been an error if the number of bytes available is less
            # than the next block size
            message = stream.readQString()
            # Read the platform independent QString from the stream. Each 
            # message will only consist of one QString, so the message
            # stream must be over now
            print("Received: {}".format(message))
            self.processMessage(message)
            self.nextBlockSize = 0
            
    def sendMessage(self, message):
        '''Convert the message dictionary into a JSON object
           which is a string and then send it to the server'''
        print("Sending: {}".format(message))
        try:
            message = json.dumps(message)
        except:
            print("Error Encoding Message")
            print(message)
            return False
        # Encode the message dictionary as a JSON object string
        request = QtCore.QByteArray()
        # This is the array of bytes that will be sent
        stream = QtCore.QDataStream(request, QtCore.QIODevice.WriteOnly)
        # This is used to add data to the byte array
        stream.setVersion(QtCore.QDataStream.Qt_5_13)
        # Versions must match between server and client
        stream.writeUInt32(0)
        # Add a 0 to the stream before the message
        stream.writeQString(message)
        # Write the message to the stream
        stream.device().seek(0)
        # Move back to before the message, where the 0 is
        stream.writeUInt32(request.size() - self.INTSIZE)
        # Write the length of the message as an integer
        # which is the length of the stream minus the length of 
        # the 0 that was at the beginning of it, which is 4 bytes.
        # This is so that the server knows how many bytes to read.
        self.socket.write(request)
        # Write the byte stream to the TCP connection
        self.nextBlockSize = 0
        # Mark that the stream is empty after reading the QString from it
        return True
        
    def socketDisconnected(self):
        '''If the server closes the connection, reset the program'''
        self.socket.close()
        self.logout()
        
    def socketError(self):
        '''If the socket has an error, it is automatically handled
           by this function, which alerts the user as to what happened
           and disconnects from the sever'''
        errorString = self.socket.errorString()
        print("Error: {}".format(errorString))
        self.socket.close()
        # Close the connection
        self.showMessage(errorString, "Error")
        # Shows a dialog box to the user explaining what happened
        
    def showMessage(self, message, title):
        '''Shows a dialog box to the user'''
        self.msgBox.setText(message)
        self.msgBox.setWindowTitle(title)
        self.msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.msgBox.show()
        
    def processMessage(self, message):
        '''Decide what to do with requests from the server by using the python equivalent of a switch statement.
           The function uses a dictionary with strings from message["action"] as keys and functions in the class as values.
           It matches an action to the relevant function, and more than one action can map to the same function. If the 
           action is not found in the dictionary then it prints that the action wasnt found and does nothing.'''
        try:
            message = json.loads(message)
        except:
            print("Error decoding message")
         # Convert from a string into a dictionary using JSON
        cases = {
                "getSalt": self.completeLogin,
                "login": self.verifyLogin,
                "question": self.showQuestion,
                "results": self.showResults
                }
        try:
            case = cases[message["action"]]
        except KeyError:
            print("Error selecting action")
            print("Action", message["action"])
            case = False
        # Match the action to a function, or handle if there isnt a match
        if case:
            case(message)
        # Execute the function from the cases, if there is one
        
    def __init__(self):
        super().__init__()
        # Initialise QtWidgets.QMainWindow, which is written in C++
        uic.loadUi('mainwindowstudent.ui', self)
        # This loads the .ui file, which is an XML representation of the GUI
        # which was created using QT Designer.
        self.loggedIn = False
        self.username = ""
        self.password = ""
        self.address = ""
        self.port = 0
        self.lcdCount = 0
        self.nextBlockSize = 0
        self.INTSIZE = 4
        self.topicID = None
        self.clockRunning = False
        # Initialise variables
        self.constantTimer = QtCore.QTimer()
        self.constantTimer.start(1000)
        self.socket = QtNetwork.QTcpSocket()
        self.msgBox = QtWidgets.QMessageBox()
        # Create the timer, web socket and dialog box
        self.constantTimer.timeout.connect(self.tickUp)
        self.wait_logout_btn.clicked.connect(self.logout)
        self.res_logout_btn.clicked.connect(self.logout)
        self.mc_submit_btn.clicked.connect(self.submitMC)
        self.sw_submit_btn.clicked.connect(self.submitSW)
        self.socket.readyRead.connect(self.receiveMessage)
        self.socket.disconnected.connect(self.socketDisconnected)
        self.socket.error.connect(self.socketError)
        self.login_btn.clicked.connect(self.login)
        # Connect the Qt signals to the relevant functions
        self.setFixedSize(self.size())
        self.pass_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        # Prevent other people from being able to read the password box
        cfg = configparser.ConfigParser()
        try:
            cfg.read("studentconfig.ini")
            self.port = int(cfg["DEFAULT"]["PORT"])
            self.address = cfg["DEFAULT"]["ADDRESS"]
            print("Using Port",self.port)
            print("Using Address",self.address)
        except:
            print("Failed to load port and address from studentconfig.ini")
        # Attempt to load the last used values for the IP address and port
        # of ther server from studentconfig.ini
        if self.address:
            self.address_edit.setText(self.address)
        if self.port:
            self.port_spin.setValue(self.port)
        # Set the address box and port spin box to the values from
        # the config file if they were found
        self.show() #Show the main GUI
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv) #Refer to the application as app from now on.
    app.setStyle(QtWidgets.QStyleFactory.create("gtk+"))
    window = MainStudentWindow() #This opens the window
    sys.exit(app.exec_())
