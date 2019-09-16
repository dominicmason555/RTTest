# This file contains the networking backend of the teacher program
# it should not be run directly, it is for the teacher program to import

# Created by Dominic Mason

import teacher_test_manager as tm
import queue, json, random, datetime
from PyQt5 import QtCore, QtNetwork, QtGui

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
                self.debugPrint("{1}\nNetwork thread locking for internal {0}\n{1}".format(fn.__name__, ("=="*35)))
                self.lock = True
            return fn(*args, **kwargs)
        finally:
            if toLock:
                timed = (datetime.datetime.now() - timestamp).total_seconds() * 1000
                self.debugPrint("{1}\nNetwork thread unlocking from internal {0} ({2}ms)\n{1}".format(fn.__name__, ("=="*35), timed))
                self.lock = False
    return doWithLock
# This is a function decorator. Whenever a function definition is preceded by "@lockMethod" it will be "wrapped" by this function.
# The function will first check if the thread is already locked, and if not then it will lock the thread. Then it will execute the
# function that has been passed to it using the "@lockMethod" decorator. Once that funciton has finished, it will then unlock
# the thread if it had to lock the thread before it ran the function. It will also show how long the function took to execute 
# if debug mode is enabled. This means that if a function marked as a lockMethod is executed, it will not be interrupted by any
# items from the queue while it is executing. This provides greater safety for the program as it ensures that only one function
# runs at a time even though clients and the gui are requesting function calls at any time.

class Client():
    '''This represents a client that is connected, it is used to store the socket connection,
       the username and whether they are actually logged in or just connected'''
    def __init__(self, username, connection):
        self.username = username
        self.connection = connection
        self.loggedIn = False
    def setUsername(self, username):
        self.username = username
    def getUsername(self):
        return self.username
    def getConnection(self):
        return self.connection
    def getDescriptor(self):
        return self.connection.socketDescriptor()
    def acceptLogin(self):
        self.loggedIn = True
    def getLoggedIn(self):
        return self.loggedIn
    def setBlockSize(self, size):
        self.connection.nextBlockSize = size

class Server(QtCore.QObject):
    '''This is the object that runs in the networking thread and controls all of the networking
       part of the program. Only the main thread can control this thread by using the queues,
       but it will act independantly whenever a client connects, disconnects or sends a message.
       The messages are in the same format as the requests of the program except they are converted
       into JSON for transmission, and then converted back again in the student program.'''
    def __init__(self,receiveQueue, sendQueue, port=None):
        print("Server Initialising")
        super().__init__()
        # Initialises the QObject class
        self.receiveQueue = receiveQueue
        self.sendQueue = sendQueue
        self.connections = []
        self.lock = False
        self.testManager = None
        # This will be set to a new instance of the TestMgr class whenever a test is set
        if port:
            self.port = port
        else:
            self.port = 9999
            print("Missing port number from config.ini, defaulting to 9999")
        # If config.ini was sucessfully read then it can load the port from there, otherwise default to 9999
        self.INTSIZE = 4
        # This is how many bytes there are in an integer, the QtNetwork module needs this, because it is 
        # written in C++ and directly modifies the message stream byte by byte
        
    def debugPrint(self, msg):
        '''If the user has enabled the debug mode, then display extra information 
           about what the program is doing'''
        if self.debug:
            print(msg)
            
    def setDebug(self, setting):
        '''Toggles debug mode'''
        if type(setting) == bool:
            self.debug = setting
        
    def run(self):
        '''This starts the thread running, but it must not be called directly,
           it must be started with Server.start() instead for it to be started
           in its own thread. If it is called directly then it will run in 
           the thread in which it was called.'''
        self.debug = False
        self.lock = False
        for i in QtNetwork.QNetworkInterface.allAddresses():
            print("Found Address:", i.toString())
            if i != QtNetwork.QHostAddress.LocalHost and i.protocol() == QtNetwork.QAbstractSocket.IPv4Protocol:
                self.address = i
                break
        # This determines the IP adress of the server
        self.tcpServer = QtNetwork.QTcpServer(self)
        self.tcpServer.listen(QtNetwork.QHostAddress("0.0.0.0"), self.port)
        # Listen on all addreses on the specified port only
        self.tcpServer.newConnection.connect(self.addConnection)
        # Call self.addConnection whenever the server signals that there is a new inbound connection
        print("Server Initialised")
        self.constantTimer = QtCore.QTimer()
        self.constantTimer.timeout.connect(self.checkQueue)
        self.constantTimer.start(1)
        print("Server Checking Queue")
        # Integrate the checkQueue function into the QT event loop, with
        # a delay between calls of 1 millisecond
        self.receiveQueue.put({"action":"showAddress", "port":self.port, "address":self.address, "client":"thread"})
        # Inform the main thread of the address and port so that it can display them
        
    @lockMethod
    def addConnection(self):
        '''Connect a client with a temporary username made out of their socket descriptor so that
           their login can pe processed. Once they have logged in, the username will change 
           to the user's actual username.'''
        connection = self.tcpServer.nextPendingConnection()
        username = "connection{}".format(connection.socketDescriptor())
        # Create the temporary username
        client = Client(username, connection)
        # Create an instance of the Client class
        client.setBlockSize(0)
        # This is necessary for sending and receiving data, 0 means no current data
        print("{} connected to socket {}".format(client.getUsername(), client.getDescriptor()))
        self.connections.append(client)
        # Add the client to the list of curernt connections
        print("Now {} connection(s)".format(len(self.connections)))
        client.getConnection().readyRead.connect(self.receiveMessage)
        client.getConnection().disconnected.connect(lambda: self.removeConnection(client))
        client.getConnection().error.connect(self.socketError)
        # Connect the client's tcp socket's signals to the relevant functions
        
    @lockMethod
    def receiveMessage(self):
        '''Extract the message from the client's conenction in the form of
           a QDataStream, then read the stream as a QString, then use
           the JSON module to convert it from JSON into a dictionary
           and then send it as a request to the main thread'''
        for client in self.connections:
            s = client.getConnection()
            if s.bytesAvailable() > 0:
                # Determine which client has data being sent
                stream = QtCore.QDataStream(s)
                stream.setVersion(QtCore.QDataStream.Qt_5_13)
                # The streams have to have the same version for compatability
                # between the two programs and all data that goes through
                # is converted to Qt's platform independant data types such as QString
                # which are made of C++ types. This means that the server and client could have
                # different architectures, different word lengths, different operating
                # systems or even be written in different languages and in theory they 
                # could still communicate
                if s.nextBlockSize == 0:
                    if s.bytesAvailable() < self.INTSIZE:
                        return
                    # If there is not enough data for an integer representing the
                    # number of "blocks" left to transmit, then the transmission has
                    # finished
                    s.nextBlockSize = stream.readUInt32()
                    # Read the remaining number of "blocks" from the stream
                if s.bytesAvailable() < s.nextBlockSize:
                    return
                # There has been an error if the number of bytes available is less
                # than the next block size
                textFromClient = stream.readQString()
                # Read the platform independent QString from the stream. Each 
                # message will only consist of one QString, so the message
                # stream must be over now
                client.setBlockSize(0)
                # Mark that the stream is empty after reading the QString from it
                toSend = json.loads(textFromClient)
                # Convert from a string into a dictionary using JSON
                toSend.update({"client":client, "username":client.getUsername()})
                # Add the client and the username to the dictionary
                try:
                    self.receiveQueue.put(toSend)
                except:
                    print("Couldn't Add item to nwReceiveQueue")
                # Add the message to the main thread's queue
        
    @lockMethod
    def sendMessage(self, text, socketId):
        '''Write the text to the data stream to the client'''
        for client in self.connections:
            s = client.getConnection()
            sent = False
            if True: #str(client.getDescriptor()) == str(socketId):
                # Select the right client
                print("Sending Message")
                reply = QtCore.QByteArray()
                # This is the array of bytes that will be sent
                stream = QtCore.QDataStream(reply, QtCore.QIODevice.WriteOnly)
                # This is used to add data to the byte array
                stream.setVersion(QtCore.QDataStream.Qt_5_13)
                # Versions must match between server and client
                stream.writeUInt32(0)
                # Add a 0 to the stream before the message
                stream.writeQString(text)
                # Write the message to the stream
                stream.device().seek(0)
                # Move back to before the message, where the 0 is
                stream.writeUInt32(reply.size() - self.INTSIZE)
                # Write the length of the message as an integer
                # which is the length of the stream minus the length of 
                # the 0 that was at the beginning of it, which is 4 bytes.
                # This is so that the client knows how many bytes to read.
                s.write(reply)
                # Write the byte stream to the TCP connection
                sent = True
                # Indicate that the client was found and the message was sent
            else:
                print("Client not found")
            if not sent:
                print("Failed to send message to",socketId)
            # Inform the user in case the program tried to send a message
            # to a user that didnt exist or was not connected
        
    @lockMethod
    def removeConnection(self, user):
        '''This is called when a user disconnects, and it removes them
           from the list of connections and signals to the main thread
           to update its model of the logged in users'''
        username = user.getUsername()
        print("{} Disconnected".format(username))
        for i in range(len(self.connections)):
            if self.connections[i].getUsername() == username:
                del self.connections[i]
                break
        # Find the user in the list of connections and delete them
        print("Now {} connections(s)".format(len(self.connections)))
        self.refreshGui()
        
    def socketError(self):
        '''If an error has occurred, inform the user and signal the
           main thread to refresh the gui in case it caused anything
           about the clients to change'''
        print("A socket error has occurred")
        self.refreshGui()
        
    @lockMethod
    def acceptLogin(self, request):
        '''Send a message to a client that informs them that they have
           successfully logged in, and change the Client object's username
           to the user's real username and change its status to logged in'''
        print("Accepted Login from {} on socket {}".format(request["realUsername"], request["client"].getDescriptor()))
        print(request)
        request["client"].setUsername(request["realUsername"])
        request["client"].acceptLogin()
        # Change the username to the real username and set the logged in status to True
        message = {"message":request}
        message["message"].update({"action":"login", "login":"accepted"})
        self.sendRequest(message)
        # Message the client that they have logged in successfully
        self.refreshGui()
        
    def refreshGui(self):
        '''Send a reqeust to the main thread to update the GUI'''
        self.receiveQueue.put({"action":"updateGui", "data":"refresh", "client":"thread"})
        
    @lockMethod
    def denyLogin(self, request):
        '''Message the client informing them that they have been denied'''
        print("Denied Login from {}".format(request["username"]))
        message = {"message":request}
        message["message"].update({"action":"login", "login":"denied"})
        self.sendRequest(message)
        
    @lockMethod
    def getLoggedInUsers(self):
        '''Create a list of the usernames of the currently logged in users'''
        clientList = []
        for c in self.connections:
            if c.getLoggedIn():
                clientList.append(QtGui.QStandardItem(c.getUsername()))
        return clientList
        
    @lockMethod
    def setTest(self, request):
        '''Set a test my creating a new instance of the TestMgr class
           from teacher_test_manager.py with the test request, storing
           it and then using it to give each of the users their first 
           question'''
        self.testManager = tm.TestMgr(request)
        # Replace the previous test manager (if there was one) with
        # a new one that contains all of the details of the current 
        # test and can set questions to a user using the weighting
        # method set by the teacher
        for user in self.testManager.getUsers():
            question = self.testManager.getQuestion(user)
            if question:
                self.sendRequest({"username":user, "message":question})
            else:
                print("No question for user:",user)
        # Set each user their first question, if there is one available
                
    @lockMethod
    def nextQuestion(self, request):
        '''Set a user their next question from the test manager if there
           is one available, and if not then request the log of their 
           answers from the main thread so that it can be sent to them'''
        user = request["username"]
        question = self.testManager.getQuestion(user)
        # Try to get question
        if question:
            self.sendRequest({"username":user, "message":question})
            # Send it to them
        else:
            return {"action":"getAnswerLog", "username":user, "client":"thread"}
            # Request the log of their answers to send it to them
            
    def showResults(self, request):
        '''Send results to a user when their test has finished'''
        request["action"] = "results"
        self.sendRequest(request)
        
    def checkQueue(self):
        '''If the thread isnt locked then check the queue for a
           request to execute'''
        if not self.lock:
            if not self.sendQueue.empty():
                self.processRequests()
        
    @lockMethod
    def sendRequest(self, request):
        '''Extracts the message and the socket descriptor from a
           request and uses them to send the message with self.sendMessage'''
        self.debugPrint("SendRequest: {}".format(request))
        username = ""
        realUsername = ""
        if "username" in request:
            username = request["username"]
        if "message" in request:
            if "username" in request["message"]:
                username = request["message"]["username"]
        if "realUsername" in request:
            realUsername = request["realUsername"]
        if "message" in request:
            if "realUsername" in request["message"]:
                realUsername = request["message"]["realUsername"]
        # These are all of the possible locations for a username.
        # The reason that there are so many is because the requests
        # can come from many different places that all work slightly
        # differently, so it is faster to just send the message around
        # between threads and deal with the different permutations
        # here once than to restructure every request every time it is
        # created by this thread or by the main or database threads,
        # which all have to do it differently to be compatible with their
        # queue systems
        sent = False
        for con in self.connections:
            if con.getUsername() == username or con.getUsername() == realUsername:
                if "client" in request:
                    request.pop("client")
                if "message" in request:
                    if "client" in request["message"]:
                        request["message"].pop("client")
                # Clean the request
                if "message" in request:
                    toSend = json.dumps(request["message"])
                else:
                    toSend = json.dumps(request)
                # Convert request from dictionary to JSON
                self.debugPrint("Sending: {}".format(toSend))
                self.sendMessage(toSend, con.getDescriptor())
                # Send the request
                sent = True
        if not sent:
            print("Could not send message to", username)
        
    @lockMethod
    def guiRequest(self, request):
        '''Decide what to do with a GUI request, it is easily
           extendable for future types of GUI request'''
        if request["data"] == "loggedIn":
            request["response3"] = self.getLoggedInUsers()
        request["client"] = "thread"
        return request
            
    def processRequests(self):
        '''Decide what to do with requests from the main thread in its queue by using the python equivalent of a switch statement.
           The function uses a dictionary with strings from request["action"] as keys and functions in the class as values.
           It matches an action to the relevant function, and more than one action can map to the same function. If the 
           action is not found in the dictionary then it prints that the action wasnt found and does nothing. Once the function
           has been executed, the value it returns is put on to the queue to send to the main thread'''
        self.debugPrint("processRequests")
        try:
            queueLength = self.sendQueue.qsize()
            request = self.sendQueue.get_nowait()
            self.sendQueue.task_done()
            self.debugPrint("NW Received: {} from Main Thread\n".format(request))
        except:
            print("Error dequeueing network request")
        # Error handling in case the queue is somehow checked while empty, which only happens if checkQueue is broken
        if not request:
            return
        # Cancel the function if the request is empty
        cases = {
                "send": self.sendRequest,
                "acceptLogin": self.acceptLogin,
                "denyLogin": self.denyLogin,
                "updateGui": self.guiRequest,
                "setTest": self.setTest,
                "nextQuestion": self.nextQuestion,
                "getAnswerLog": self.showResults
                }
        try:
            if request:
                case = cases[request["action"]]
            else:
                case = False
        except KeyError:
            print("Error selecting action from NW request")
            print("Action:", request["action"])
            return
        # Match the action to a function, or handle if there isnt a match
        if case:
            try:
                timestamp = datetime.datetime.now()
                self.lock = True
                log = "{1}\nNetwork thread locking for {0} from main thread ({2} item(s) in queue)\n{1}"
                self.debugPrint(log.format(request["action"], ("=="*40), queueLength))
                self.receiveQueue.put(case(request))
            finally:
                timed = round(((datetime.datetime.now() - timestamp).total_seconds() * 1000), 2)
                log = "{1}\nNetwork thread unlocking from {0} from main thread ({2}ms)\n{1}"
                self.debugPrint(log.format(request["action"], ("=="*40), timed))
                self.lock = False
        # Lock the thread, execute the function, unlock the thread and inform the queue that the task has finished
        # Also, in debug mode print the details of the request and the lock and unlock, and how long the function took to execute
        
    def finish(self):
        '''Shut the server down safely to close the program'''
        print("Server can exit: ",end="")
        print(not self.lock)
        if self.lock:
            return False
        # The server cant exit if it is locked for a sensitive operation
        else:
            for client in self.connections:
                client.getConnection().close()
            # Close all of the connections
            self.tcpServer.close()
            # Stop accepting new connections
            print("Server closed to new connections")
            return True

if __name__ == "__main__": #if this file is run as a program, inform the user
    print("This is not the correct file to run") #which file they should run
    print("Run the file: RTTest_Teacher.pyw") #to run the actual program
    input("Press [enter] to close")
