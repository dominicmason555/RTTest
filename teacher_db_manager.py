# This file contains the database backend of the teacher program
# it should not be run directly, it is for the teacher program to import

# Created by Dominic Mason

import sqlite3, os, base64, hashlib, datetime, random
from string import Template
from PyQt5 import QtCore, QtGui
import teacher_db_handler as dbh

def handlerMethod(fn):
    '''This wraps a method so that it is given an instance of the handler class 
       from its file as its last positional argument. Also, if the database 
       connection can't be made, then it doesnt run the function. This applies to
       any method marked with the @handlerMethod decorator'''
    def createHandler(*args, **kwargs):
        with dbh.Handler() as handler:
            # The with statement ensures the handler is safely destroyed
            # after the function ends so that the database changes are 
            # saved and the connection is closed, as specified in the
            # __exit__ function of the database handler.
            if handler:
                # Only run the method if the connection has been made
                args = args + (handler,)
                # Add the handler as an argument
                return fn(*args, **kwargs)
            else:
                print("Failed to connect to database")
    return createHandler


class Mgr(QtCore.QObject):
    '''This class doesnt interact with the database directly,
       it interacts with the database handler'''
    def __init__(self, responseQueue, requestQueue):
        super().__init__()
        # Initialise the QObject class that it inherits, QObject is
        # written in C++
        self.debug = False
        self.lock = False
        self.requestQueue = requestQueue
        self.responseQueue = responseQueue
        
    def run(self):
        '''This starts the thread running, but it must not be called directly,
           it must be started with Mgr.start() instead for it to be started
           in its own thread. If it is called directly then it will run in 
           the thread in which it was called.'''
        print("Running DB Manager")
        self.constantTimer = QtCore.QTimer()
        self.constantTimer.timeout.connect(self.checkQueue)
        self.constantTimer.start(1)
        # Integrate the checkQueue function into the QT event loop, with
        # a delay between calls of 1 millisecond
        print("Database Manager Checking Queue")
        
    def createHash(self, password, salt=None):
        '''This creates a hash of a password using either a given salt value or
           a cryptographically secure randomly generated one from the os module.
           The reason that it hashes 1000 times instead of just once is because
           if a hash takes 1000 times as long to compute, then it takes 1000 
           times as long to crack a password.'''
        if salt == None:
            salt = base64.b64encode(os.urandom(30)).decode()
            # Secure random bytes in text format
        saltedPass = salt + password
        for i in range(1000):
            saltedPass = hashlib.sha512(saltedPass.encode()).hexdigest()
        # 1000 rounds of sha512 is a lot more than is necessary, but the
        # more secure the better. 30 bytes of salt is also a lot more
        # than most commercial hashes use.
        final = salt + "|==|" + saltedPass
        # This allows the salt to be separated from the hash when it is
        # retrieved from the database using hashed.split("|==|")
        # Neither of the two algorithms can generate the | character
        self.debugPrint(final)
        return str(final)
        
    def verifyHash(self, password, hashed):
        '''Create the hash of the password see if it matches the given hash using
           the given salt.'''
        return str(self.createHash(password, hashed.split("|==|")[0])) == hashed
        
    @handlerMethod
    def getSalt(self, request, handler):
        '''Extract the salt from the password hash for a specific user in the
           database so that it can be sent to the user for them to hash their
           password with'''
        print("Sending Password Salt to", request["username"])
        passHash  = handler.getPassHash(request["realUsername"])
        if passHash:
            salt = passHash[0][0].split("|==|")[0]
            request.update({"salt":salt, "denied":False})
        else:
            request.update({"denied":True})
            # If the user is not in the database, deny them before they 
            # hash their password
        return request
        
    @handlerMethod
    def processLogin(self, request, handler):
        '''Decide whether to allow a user to login or not by checking
           their password hash'''
        self.debugPrint(request)
        passHash  = handler.getPassHash(request["realUsername"])[0][0]
        self.debugPrint("Passhash: {}".format(passHash))
        self.debugPrint("Password: {}".format(request["password"]))
        if request["password"] == passHash:
            request["action"] = "acceptLogin"
        else:
            request["action"] = "denyLogin"
        return request
        
    @handlerMethod
    def addUser(self, request, handler):
        '''Adds a user, with error handling'''
        print("Adding user", request["username"])
        hashed = self.createHash(request["password"])
        request["error"] = not handler.addUser(request["username"], hashed)
        return request
        
    @handlerMethod
    def editUser(self, request, handler):
        '''Edits a user, with error handling'''
        print("Editing user", request["username"])
        hashed = self.createHash(request["password"])
        request["error"] = not handler.editUser(request["username"], hashed)
        return request
        
    @handlerMethod
    def removeUser(self, request, handler):
        '''Removes a user, with error handling'''
        print("Removing User", request["username"])
        request["completed"] = "User Removed Successfully"
        request["errorText"] = "Failed to Remove User"
        request["error"] = not handler.removeUser(request["username"])
        return request
        
    @handlerMethod
    def addTopic(self, request, handler):
        '''Adds a topic, with error handling'''
        print("Adding Topic", request["name"])
        request["error"] = not handler.addTopic(request["name"], request["newID"])
        return request
        
    @handlerMethod
    def editTopic(self, request, handler):
        '''Edits a topic, with error handling'''
        print("Editing topic", request["name"])
        request["error"] = not handler.editTopic(request["id"], request["newID"], request["name"])
        return request
        
    @handlerMethod
    def removeTopic(self, request, handler):
        '''Removes a topic, with error handling'''
        print("Removing Topic", request["name"])
        request["completed"] = "Topic Removed Successfully"
        request["errorText"] = "Failed to Remove Topic"
        request["error"] = not handler.removeTopic(request["id"])
        return request
        
    @handlerMethod
    def removeResults(self, request, handler):
        '''Removes results, by user or by topic'''
        if request["type"] == "user":
            request["error"] = not handler.removeResultsByUser(request["username"])
        if request["type"] == "topic":
            request["error"] = not handler.removeResultsByTopic(request["id"])
        return request
        
    def processAnswer(self, request):
        '''Routes an answer to the answer processor for its question type'''
        if request["qType"] == "mc":
            request = self.processMCAnswer(request)
        if request["qType"] == "sw":
            request = self.processSWAnswer(request)
        return request
            
    @handlerMethod
    def processMCAnswer(self, request, handler):
        '''Verifies the answer of a multiple choice question and then
           logs the result'''
        question = handler.getMCQuestion(request["QID"])
        # Read the question from the database
        if question:
            if  request["answer"] == question[7]:
                request.update({"passed":True})
            else:
                request.update({"passed":False})
            self.logResult(request)
        else:
            print("MC QID not found:", request["QID"])
        return request
        
    @handlerMethod
    def processSWAnswer(self, request, handler):
        '''Verifies the answer of a single word question and then
           logs the result'''
        question = handler.getSWQuestion(request["QID"])
        # Read the question from the database
        if question:
            if  request["answer"] == question[3]:
                request.update({"passed":True})
            else:
                request.update({"passed":False})
            self.logResult(request)
        else:
            print("SW QID not found:", request["QID"])
        return request
    
    @handlerMethod
    def logResult(self, request, handler):
        '''Instructs the handler to log a result'''
        handler.logResult(request)
        return request
        
    def debugPrint(self, msg):
        '''If the suer enabled debug mode, print the extra information'''
        if self.debug:
            print(msg)
            
    def setDebug(self, setting):
        '''Mirror the debug mode of the main thread'''
        if type(setting) == bool:
            self.debug = setting
        
    def createTreeItemList(self, request):
        '''Takes a list of topic tuples and question tuples and converts them into
           QStandardItems and then it adds the question itemsas sub-rows to the 
           correct topic items, then compiles a list of topic items
           for the main thread to append to a model when it receives them'''
        topics = request["response1"]
        questions = request["response2"]
        rowList = []
        for i in range(len(topics)):
            topicRow = QtGui.QStandardItem(str(topics[i][0]) + ": " + topics[i][1])
            topicRow.setSelectable(False)
            # Topics themselves should not be selectable in the topic/question tree
            for j in range(len(questions)):
                if questions[j][1] == topics[i][0]:
                    topicRow.appendRow(QtGui.QStandardItem(str(questions[j][0]) + ": " +questions[j][2]))
            rowList.append(topicRow)
        request["response3"] = rowList
        return request
        
    def createListItemList(self, request):
        '''Converts a list of tuples from the database into a list of QStandardItems'''
        rowList = []
        for i in request["response"]:
            strData = list(map(str, i))
            if request["data"] == "topics":
                row = strData[0] + ": " + strData[1]
                # This handles the fact that topics have IDs, unlike the other types
            else:
                row = strData[0]
            rowList.append(QtGui.QStandardItem(row))
        request["response3"] = rowList
        return request
        
    @handlerMethod
    def createTest(self, request, handler):
        '''This takes the request from setTest in the main thread that contains the parameters
           for the test, such as the users and the questions and the weighting method. This 
           function then creates a list of dictionaries that contain the username and all of 
           the questions that have been set so that they can then each be weighted'''
        unsortedQuestions = []
        for i in range(len(request["users"])):
            compiledList = []
            for qid in request["swIDs"]:
                compiledList.append(self.swQuestionToDict(handler.getSWQuestion(qid)))
            for qid in request["mcIDs"]:
                compiledList.append(self.mcQuestionToDict(handler.getMCQuestion(qid)))
            unsortedQuestions.append({"username":request["users"][i], "questionList":compiledList})
        # Make the list of dictionaries with lists of question lists
        if request["weighting"] == "question":
            sortedQuestions = self.weightQuestionsByQuestion(unsortedQuestions, request)
        elif request["weighting"] == "topic":
            sortedQuestions = self.weightQuestionsByTopic(unsortedQuestions, request)
        else:
            sortedQuestions = unsortedQuestions
        # Weight the questions using the right method, if needed
        request.update({"data":sortedQuestions})
        return request
        
    def swQuestionToDict(self, question):
        '''Maps the items in a single word question tuple to keys of a dictionary for easy access'''
        keys = ["QID", "topicID", "question", "answer"]
        questionDict = dict(zip(keys,question))
        questionDict.update({"qType":"sw"})
        return questionDict
        
    def mcQuestionToDict(self, question):
        '''Maps the items in a single word question tuple to keys of a dictionary for easy access'''
        keys = ["QID", "topicID", "question", "answer1", "answer2", "answer3", "answer4", "correct"]
        questionDict = dict(zip(keys,question))
        questionDict.update({"qType":"mc"})
        return questionDict
        
    @handlerMethod
    def weightQuestionsByQuestion(self, unsorted, request, handler):
        '''First assigns each question a random score between 0 and the weighting value (which can be 0), and then
           adds to the score based on the time taken to answer a question incorrectly in all of the past results
           for that user and question in a sort of running average.'''
        for quest in unsorted:
            print("Weighting results for", quest["username"],"by results per question with effect value of",request["effect"],"%")
            pastMC = handler.getMCResults(quest["username"])
            pastSW = handler.getSWResults(quest["username"])
            mcQs = handler.getMCQuestions()
            swQs = handler.getSWQuestions()
            # Get data from database
            mcweightDict = {}
            swweightDict = {}
            randMax = 100 - request["effect"]
            for item in mcQs:
                mcweightDict[item[0]] = random.randint(0,randMax)
            for item in swQs:
                swweightDict[item[0]] = random.randint(0,randMax)
            # Assign random initial score, 0 if weighting effect is set to the maximum
            for res in pastMC:
                if res[2] in request["mcIDs"]:
                    weight = res[5]
                    weight += weight * res[6]
                    mcweightDict[res[2]] = (mcweightDict[res[2]] + weight) // 1.5
            for res in pastSW:
                if res[2] in request["swIDs"]:
                    weight = res[5]
                    weight += weight * res[6]
                    swweightDict[res[2]] = (swweightDict[res[2]] + weight) // 1.5
            # Increase the weight with every mistake in the database, with a bigger effect the longer the answer took
            for weight in mcweightDict:
                self.debugPrint("Mistake weight for user {} on mc question {} is {}".format(quest["username"], weight, mcweightDict[weight]))
            for weight in swweightDict:
                self.debugPrint("Mistake weight for user {} on sw question {} is {}".format(quest["username"], weight, swweightDict[weight]))
            quest["mcWeights"] = mcweightDict
            quest["swWeights"] = swweightDict
            # The weights are actually applied to the question in formatQuestions, not here
        return self.formatQuestions(unsorted) if unsorted else unsorted
            
    @handlerMethod
    def weightQuestionsByTopic(self, unsorted, request, handler):
        '''First assigns each topic a random score between 0 and the weighting value (which can be 0), and then
           adds to the score based on the time taken to answer a question on the topic incorrectly in all of 
           the past results for that user and topic in a sort of running average.'''
        for quest in unsorted:
            print("Weighting results for", quest["username"],"by results per topic")
            pastMC = handler.getMCResults(quest["username"])
            pastSW = handler.getSWResults(quest["username"])
            topics = handler.getTopics()
            # Get data from database
            topicWeightDict = {}
            randMax = 100 - request["effect"]
            for topic in topics:
                topicWeightDict[topic[0]] = random.randint(0,randMax)
            # Assign random initial score, 0 if weighting effect is set to the maximum
            for res in pastMC:
                if res[2] in request["mcIDs"]:
                    weight = res[5]
                    weight += weight * res[6]
                    topicWeightDict[res[3]] = (topicWeightDict[res[3]] + weight) // 1.5
            for res in pastSW:
                if res[2] in request["swIDs"]:
                    weight = res[5]
                    weight += weight * res[6]
                    topicWeightDict[res[3]] = (topicWeightDict[res[3]] + weight) // 1.5
            # Increase the weight with every mistake in the database, with a bigger effect the longer the answer took
            for weight in topicWeightDict:
                print("Mistake weight for user {} on topic {} is {}".format(quest["username"], weight, topicWeightDict[weight]))
            quest["topicWeights"] = topicWeightDict
        # The weights are actually applied to the question in formatQuestions, not here
        return self.formatQuestions(unsorted) if unsorted else unsorted
            
    def formatQuestions(self, unsorted):
        '''Apply the weights in the dictionary to the question dictionaries.
           If no weight is found (which shouldnt happen) then assign a weight
           of 50.'''
        if "topicWeights" in unsorted[0]: 
            for userDict in unsorted:
                for questionDict in userDict["questionList"]:
                    if questionDict["topicID"] in userDict["topicWeights"]:
                        questionDict["weight"] = userDict["topicWeights"][questionDict["topicID"]]
        if "mcWeights" in unsorted[0]:
            for userDict in unsorted:
                for questionDict in userDict["questionList"]:
                    if questionDict["qType"] == "mc":
                        if questionDict["QID"] in userDict["mcWeights"]:
                            questionDict["weight"] = userDict["mcWeights"][questionDict["QID"]]
                        else:
                            questionDict["weight"] = 50
                    else:
                        if questionDict["QID"] in userDict["swWeights"]:
                            questionDict["weight"] = userDict["swWeights"][questionDict["QID"]]
                        else:
                            questionDict["weight"] = 50
        return unsorted
        
    @handlerMethod
    def getPastResults(self, request, handler):
        '''Get the past results from the database handler'''
        if "user" in request:
            if request["mcID"]:
                request["mcResults"] = handler.getMCResults(username=request["user"], mcID=request["mcID"])
            if request["swID"]:
                request["swResults"] = handler.getSWResults(username=request["user"], swID=request["swID"])
        else:
            if request["mcID"]:
                request["mcResults"] = handler.getMCResults(mcID=request["mcID"])
            if request["swID"]:
                request["swResults"] = handler.getSWResults(swID=request["swID"])
        return request
        
    @handlerMethod
    def getMCQuestions(self, request, handler):
        '''Get the multiple choice questions from the database handler and convert
           them from tuples to dictionaries'''
        questionList = []
        questions = handler.getMCQuestions()
        for line in questions:
            questionList.append({"QID":line[0], "topicNum":line[1], "question":line[2], 
                                    "answer1":line[3], "answer2":line[4], "answer3": line[5], 
                                    "answer4":line[6], "correct":line[7]})
        request.update({"data":questionList})
        return request
        
    @handlerMethod
    def getSWQuestions(self, request, handler):
        '''Get the single word questions from the database handler and convert
           them from tuples to dictionaries'''
        questionList = []
        questions = handler.getSWQuestions()
        for line in questions:
            questionList.append({"QID":line[0], "topicNum":line[1], "question":line[2], "answer":line[3]})
        request.update({"data":questionList})
        return request
        
    @handlerMethod
    def addEditQuestion(self, request, handler):
        '''Convert question from dictionary to tuple and use the handler to add
           it to the database or edit an existing question in the database, and
           report back to the main thread if it succeeded or failed'''
        if request["qType"] == "MC":
            q = request["question"]
            question = (q["qid"], q["topicID"], q["question"], q["answer1"],
                        q["answer2"], q["answer3"], q["answer4"], q["correct"])
            request["error"] = not handler.addEditMCQuestion(question)
            request.update({"completed":"Sucessfully added/edited MC question"})
            request.update({"errorText":"Error Adding/Editing MC Question"})
            # One of these messages will be shown to the user using ackCompleted
            # in the main thread once the request has gone back
        if request["qType"] == "SW":
            q = request["question"]
            question = (q["qid"], q["topicID"], q["question"], q["answer"])
            request["error"] = not handler.addEditSWQuestion(question)
            request.update({"completed":"Sucessfully Added/Edited SW Question"})
            request.update({"errorText":"Error Adding/Editing SW Question"})
            # One of these messages will be shown to the user using ackCompleted
            # in the main thread once the request has gone back
        return request
        
    @handlerMethod
    def removeQuestion(self, request, handler):
        '''Use the handler to remove a question and all results associated with it from the database'''
        if request["qType"] == "MC":
            request["error"] = not handler.removeMCQuestion(request["qid"])
            request.update({"completed":"Sucessfully Removed MC question"})
            request.update({"errorText":"Error Removing MC question"})
        if request["qType"] == "SW":
            request["error"] = not handler.removeSWQuestion(request["qid"])
            request.update({"completed":"Sucessfully Removed SW question"})
            request.update({"errorText":"Error Removing SW question"})
            # One of these messages will be shown to the user using ackCompleted
            # in the main thread once the request has gone back
        return request
    
    def checkQueue(self):
        '''Check the queue to see if there are any tasks to do, but only if the thread isnt locked'''
        if not self.lock:
            if not self.requestQueue.empty():
                self.processRequests()
            
    @handlerMethod
    def guiRequest(self, request, handler):
        '''Routes requests for GUI updating to thir relevent functions. This would have been
           another dictionary switch, but the arguments of the functions called are too
           diverse for that to be more efficient than just if statements'''
        if request["data"] == "topics":
            request["response"] = handler.getTopics()
            request = self.createListItemList(request)
        if request["data"] == "users":
            request["response"] = handler.getUsers()
            request = self.createListItemList(request)
        if request["data"] == "MCQT":
            request["response2"] = handler.getMCQuestions()
        if request["data"] == "SWQT":
            request["response2"] = handler.getSWQuestions()
        if request["data"] == "MCQT" or request["data"] == "SWQT":
            request["response1"] = handler.getTopics()
            request = self.createTreeItemList(request)
        if request["data"] == "MCEdit":
            request["response"] = handler.getMCQuestion(request["qid"])
        if request["data"] == "SWEdit":
            request["response"] = handler.getSWQuestion(request["qid"])
        if request["data"] == "graphScale":
            request["response"] = handler.getLargestQuestionID()
        if request["data"] == "graphResults":
            request = self.getPastResults(request)
        return request
        
    def processRequests(self):
        '''Decide what to do with requests from the main thread in its queue by using the python equivalent of a switch statement.
           The function uses a dictionary with strings from request["action"] as keys and functions in the class as values.
           It matches an action to the relevant function, and more than one action can map to the same function. If the 
           action is not found in the dictionary then it prints that the action wasnt found and does nothing. Once the function
           has been executed, the value it returns is put on to the queue to send to the main thread'''
        try:
            queueLength = self.requestQueue.qsize()
            request = self.requestQueue.get_nowait()
            self.debugPrint("Database Recieved: {} from Main Thread\n".format(request))
        except:
            print("Error decoding database response in dbm")
        # Error handling in case the queue is somehow checked while empty, which only happens if checkQueue is broken
        if not request:
            return
        # Cancel the function if the request is empty
        cases = {
                "updateGui": self.guiRequest,
                "addUser": self.addUser,
                "removeUser": self.removeUser,
                "editUser": self.editUser,
                "login": self.processLogin,
                "getSalt": self.getSalt,
                "getMCQuestions": self.getMCQuestions,
                "getSWQuestions": self.getSWQuestions,
                "answer": self.processAnswer,
                "addTopic": self.addTopic,
                "editTopic": self.editTopic,
                "removeTopic": self.removeTopic,
                "removeResults": self.removeResults,
                "addEditQuestion": self.addEditQuestion,
                "removeQuestion": self.removeQuestion,
                "setTest": self.createTest
                }
        try:
            case = cases[request["action"]]
        except KeyError:
            print("Error selecting action from database request")
            print("Action:", request["action"])
            return
        # Match the action to a function, or handle if there isnt a match
        try:
            self.lock = True
            timestamp = datetime.datetime.now()
            log = "{1}\nDatabase thread locking for {0} from main thread ({2} item(s) in queue)\n{1}"
            self.debugPrint(log.format(request["action"], ("--"*40), queueLength))
            self.responseQueue.put(case(request))
        finally:
            timed = round(((datetime.datetime.now() - timestamp).total_seconds() * 1000), 2)
            log = "{1}\nDatabase thread unlocking from {0} from main thread ({2}ms)\n{1}"
            self.debugPrint(log.format(request["action"], ("--"*40), timed))
            self.lock = False
            self.requestQueue.task_done()
        # Lock the thread, execute the function, unlock the thread and inform the queue that the task has finished
        # Also, in debug mode print the details of the request and the lock and unlock, and how long the function took to execute

if __name__ == "__main__": # If this file is run as a program, inform the user
    print("This is not the correct file to run") # which file they should run
    print("Run the file: RTTest_Teacher.pyw") # to run the actual program
    input("Press [enter] to close")
