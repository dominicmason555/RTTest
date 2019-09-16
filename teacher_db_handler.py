# This file contains the database backend of the teacher program
# it should not be run directly, it is for the teacher program to import

# Created by Dominic Mason

import sqlite3, os, base64, hashlib, datetime
from string import Template

class Handler():
    '''This is the handler for the database in the project.
       The database should not be interacted with in any
       other way than using an instance of this class.
       It is created every time the database is modified
       and destroyed afterwards, commiting the changes
       and closing the connection.'''
    def __init__(self):
        print("Accessing Database")
        
    def __enter__(self):
        '''Because the handler is only created using a "with" statement, this function
           is called whenever the class is instantiated, it can connect to the database
           here, and check that that works, and if not it can cancel it, which because
           of the @handlerMethod decorator in the db manager thread will cancel the 
           function that would have used the handler as well.'''
        try:
            assert os.path.exists("main.db")
            self.conn = sqlite3.connect("main.db", detect_types=sqlite3.PARSE_DECLTYPES)
            self.cur = self.conn.cursor()
        except:
            print("Database Connection Failed")
            return None
        # Connect, or return None and cancel the @handlerMethod function
        return self
        
    def addUser(self, username, passhash):
        '''Get the password hash of a user, but only if they exist'''
        for i in self.getUsers():
            if i[0] == username:
                return False
        self.cur.execute("insert into Students values (?,?)", (username, passhash))
        return True
        
    def removeUser(self, username):
        ''' Remove a user and all their results, but only if they exist'''
        users = self.getUsers()
        found = False
        for i  in range(len(users)):
            if users[i][0] == username:
                found = True
                username = users[i]
                break
        # Linear search
        if not found:
            return False
        # Cancel
        self.cur.execute("delete from Students where username = ?", (username))
        self.cur.execute("delete from PerformancePerMCQuestion where username = ?", (username))
        self.cur.execute("delete from PerformancePerSWQuestion where username = ?", (username))
        return True
        
    def editUser(self, username, passhash):
        '''Change a user's password, but only if they exist'''
        users = self.getUsers()
        found = False
        for i  in range(len(users)):
            if users[i][0] == username:
                found = True
                break
        # Linear search
        if not found:
            return False
        # Cancel
        self.cur.execute("update Students set pass_hash = ? where username = ?", (passhash, username))
        return True
        
    def addTopic(self, name, id):
        '''Add a topic to the database, but only if it doesnt already exist'''
        for i in self.getTopics():
            if i[0] == id or i[1] == name:
                return False
        # Linear search
        self.cur.execute("insert into Topics values (?,?)", (id, name))
        return True
        
    def removeTopic(self, id):
        '''Remove a topic and all questions and results associated with it, but only if it exists'''
        topics = self.getTopics()
        found = False
        print(id)
        for i  in range(len(topics)):
            print(topics[i])
            if str(topics[i][0]) == str(id):
                found = True
                topic = topics[i]
                break
        # Linear search
        if not found:
            return False
        # Cancel
        self.cur.execute("delete from Topics where TopicID = ?", (id,))
        self.cur.execute("delete from MultipleChoiceQuestions where TopicID = ?", (id,))
        self.cur.execute("delete from SingleWordQuestions where TopicID = ?", (id,))
        self.cur.execute("delete from PerformancePerMCQuestion where TopicID = ?", (id,))
        self.cur.execute("delete from PerformancePerSWQuestion where TopicID = ?", (id,))
        return True
        
    def editTopic(self, id, newID, name):
        '''Edit a topic and all questions and results associated with it, but only if it exists'''
        topics = self.getTopics()
        found = False
        for i  in range(len(topics)):
            if str(newID) != str(id) and str(topics[i][0]) == str(newID):
                return False
            if str(topics[i][0]) == str(id):
                found = True
                topicName = topics[i][1]
                break
        # Linear search
        if not found:
            return False
        # Cancel
        if str(id) != str(newID):
            self.cur.execute("update Topics set TopicID = ? where TopicID = ?", (newID, id))
            self.cur.execute("update MultipleChoiceQuestions set TopicID = ? where TopicID = ?", (newID, id))
            self.cur.execute("update SingleWordQuestions set TopicID = ? where TopicID = ?", (newID, id))
            self.cur.execute("update PerformancePerMCQuestion set TopicID = ? where TopicID = ?", (newID, id))
            self.cur.execute("update PerformancePerSWQuestion set TopicID = ? where TopicID = ?", (newID, id))
        if str(name) != str(topicName):
            for i in range(len(topics)):
                if str(topics[i][1]) == str(name):
                    return False
            # Linear search
            self.cur.execute("update Topics set Name = ? where TopicID = ?", (name, id))
        return True
        
    def removeResultsByTopic(self, id):
        '''Remove results for a topic, but only if it exists'''
        topics = self.getTopics()
        found = False
        print(id)
        for i  in range(len(topics)):
            print(topics[i])
            if str(topics[i][0]) == str(id):
                found = True
                topic = topics[i]
                break
        # Linear search
        if not found:
            return False
        # Cancel
        self.cur.execute("delete from PerformancePerMCQuestion where TopicID = ?", (id,))
        self.cur.execute("delete from PerformancePerSWQuestion where TopicID = ?", (id,))
        return True
        
    def removeResultsByUser(self, username):
        '''Remove results for a user, but only if the user exists'''
        users = self.getUsers()
        found = False
        for i  in range(len(users)):
            if users[i][0] == username:
                found = True
                username = users[i]
                break
        # Linear search
        if not found:
            return False
        # Cancel
        self.cur.execute("delete from PerformancePerMCQuestion where username = ?", (username))
        self.cur.execute("delete from PerformancePerSWQuestion where username = ?", (username))
        return True
        
    def logResult(self, request):
        '''Add a result to the database'''
        print("Logging result for", request["username"])
        # ppqID, username, qID, topicID, date, timeTaken, correct
        if request["qType"] == "mc":
            command = """insert into PerformancePerMCQuestion values (NULL,?,?,?,?,?,?)"""
        elif request["qType"] == "sw":
            command = """insert into PerformancePerSWQuestion values (NULL,?,?,?,?,?,?)"""
        else:
            return
        # Select MC or SW question, or cancel if there has been a mistake in the code
        self.cur.execute(command, (request["username"], request["QID"], request["topicID"], 
                         datetime.datetime.now(), request["time"], request["passed"]))
        
    def getPassHash(self, username):
        '''Get the password hash from a user in the database, but only if they exist'''
        users = self.getUsers()
        found = False
        for i  in range(len(users)):
            if users[i][0] == username:
                found = True
                username = users[i]
                break
        # Linear search
        if not found:
            return False
        # Cancel
        self.cur.execute("select pass_hash from Students where username = ?", (username))
        passHash = self.cur.fetchall()
        return passHash
    
    def getTopics(self):
        '''Get a tuple of topic tuples'''
        self.cur.execute("select * from Topics")
        data = self.cur.fetchall()
        return data
        
    def getUsers(self):
        '''Get a tuple of user tuples'''
        self.cur.execute("select username from Students")
        data = self.cur.fetchall()
        return data
        
    def getLargestQuestionID(self):
        '''Get the largest question ID in the database, for scaling the graphs with'''
        self.cur.execute("select * from MultipleChoiceQuestions order by MCQuestionID desc")
        mcQs = self.cur.fetchall()
        self.cur.execute("select * from SingleWordQuestions order by SWQuestionID desc")
        swQs = self.cur.fetchall()
        if mcQs[0][0] > swQs[0][0]:
            return mcQs[0][0]
        else:
            return swQs[0][0]
        
    def getMCQuestions(self):
        '''Get a tuple of multiple choice question tuples'''
        self.cur.execute("select * from MultipleChoiceQuestions")
        data = self.cur.fetchall()
        return data
        
    def getMCResults(self, username=None, mcID=None):
        '''Get results for one or all of the multiple choice questions for one or all of the users, but only if they exist'''
        if not username:
            if not mcID:
                self.cur.execute("select * from PerformancePerMCQuestion")
                data = self.cur.fetchall()
            else:
                self.cur.execute("select * from PerformancePerMCQuestion where MCQuestionID=?", (mcID,))
                data = self.cur.fetchall()
        else:
            if not mcID:
                self.cur.execute("select * from PerformancePerMCQuestion where username=?", (username,))
                data = self.cur.fetchall()
            else:
                self.cur.execute("select * from PerformancePerMCQuestion where MCQuestionID=? and username=?", (mcID, username))
                data = self.cur.fetchall()
        return data
        
    def getSWResults(self, username=None, swID=None):
        '''Get results for one or all of the single word questions for one or all of the users, but only if they exist'''
        if not username:
            if not swID:
                self.cur.execute("select * from PerformancePerSWQuestion")
                data = self.cur.fetchall()
            else:
                self.cur.execute("select * from PerformancePerSWQuestion where SWQuestionID=?", (swID,))
                data = self.cur.fetchall()
        else:
            if not swID:
                self.cur.execute("select * from PerformancePerSWQuestion where username=?", (username,))
                data = self.cur.fetchall()
            else:
                self.cur.execute("select * from PerformancePerSWQuestion where SWQuestionID=? and username=?", (swID, username))
                data = self.cur.fetchall()
        return data
        
    def addEditMCQuestion(self, question):
        '''Add or edit a multiple choice question with values from the dialog'''
        print("Question:", question)
        topics = self.getTopics()
        foundTopic = False
        for i  in range(len(topics)):
            print(topics[i])
            if str(topics[i][0]) == str(question[1]):
                foundTopic = True
                break
        # Linear search
        if not foundTopic:
            return False
        questions = self.getMCQuestions()
        foundQuestion = False
        for i  in range(len(questions)):
            print(questions[i])
            if str(questions[i][0]) == str(question[0]):
                foundQuestion = True
                break
        # Linear search
        if not question[0]:
            self.cur.execute("insert into MultipleChoiceQuestions values (?,?,?,?,?,?,?,?)", question)
        else:
            if not foundQuestion:
                print("Question not found")
                return False
            query = "update MultipleChoiceQuestions set TopicID=?, Question=?, Answer1=?, Answer2=?, Answer3=?, Answer4=?, CorrectAnswer=? where MCQuestionID = ?"
            self.cur.execute(query, (question[1], question[2], question[3], question[4],
                             question[5], question[6], question[7], question[0]))
            query = "update PerformancePerMCQuestion set TopicID=? where MCQuestionID=?"
            self.cur.execute(query, (question[1], question[0]))
        return True
        
    def removeMCQuestion(self, qid):
        '''Remove a multiple choice question from the database, but only if it exists'''
        questions = self.getMCQuestions()
        found = False
        for i  in range(len(questions)):
            if str(questions[i][0]) == str(qid):
                found = True
                qid = str(questions[i][0])
                break
        # Linear search
        if not found:
            print("Question Not Found")
            return False
        # Cancel
        self.cur.execute("delete from MultipleChoiceQuestions where MCQuestionID = ?", (qid))
        self.cur.execute("delete from PerformancePerMCQuestion where MCQuestionID = ?", (qid))
        return True
        
    def getMCQuestion(self, qid):
        '''Get a specific multiple choice question from the database by question ID, but only if it exists'''
        self.cur.execute("select * from MultipleChoiceQuestions where MCQuestionID = ?", (qid,))
        data = self.cur.fetchall()
        if len(data) > 1:
            print("Warning: Multiple MC Questions share a QID")
        return data[0]
        
    def getSWQuestions(self):
        '''Get all of the single word questions from the database'''
        self.cur.execute("select * from SingleWordQuestions")
        data = self.cur.fetchall()
        return data
        
    def addEditSWQuestion(self, question):
        '''Add or edit a single word question with values from the dialog'''
        print("Question:", question)
        topics = self.getTopics()
        found = False
        for i  in range(len(topics)):
            print(topics[i])
            if str(topics[i][0]) == str(question[1]):
                found = True
                break
        # Linear search
        if not found:
            return False
        questions = self.getSWQuestions()
        foundQuestion = False
        for i  in range(len(questions)):
            print(questions[i])
            if str(questions[i][0]) == str(question[0]):
                foundQuestion = True
                break
        # Linear search
        if not question[0]:
            self.cur.execute("insert into SingleWordQuestions values (?,?,?,?)", question)
        else:
            if not foundQuestion:
                print("Question not found")
                return False
            query = "update SingleWordQuestions set TopicID=?, Question=?, CorrectAnswer=? where SWQuestionID = ?"
            self.cur.execute(query, (question[1], question[2], question[3], question[0]))
            query = "update PerformancePerSWQuestion set TopicID=? where SWQuestionID=?"
            self.cur.execute(query, (question[1], question[0]))
        return True
        
    def removeSWQuestion(self, qid):
        '''Remove a single word question from the database, but only if it exists'''
        questions = self.getSWQuestions()
        found = False
        for i  in range(len(questions)):
            if str(questions[i][0]) == str(qid):
                found = True
                qid = str(questions[i][0])
                break
        if not found:
            print("Question Not Found")
            return False
        self.cur.execute("delete from SingleWordQuestions where SWQuestionID = ?", (qid))
        self.cur.execute("delete from PerformancePerSWQuestion where SWQuestionID = ?", (qid))
        return True
        
    def getSWQuestion(self, qid):
        '''Get a specific single word question from the database by question ID, but only if it exists'''
        self.cur.execute("select * from SingleWordQuestions where SWQuestionID = ?", (qid,))
        data = self.cur.fetchall()
        if len(data) > 1:
            print("Warning: Multiple SW Questions share a QID")
        return data[0]
        
    def __exit__(self, exception_type, exception_value, traceback):
        '''Because the handler is only created using a "with" statement, this function
           is called whenever the class is destroyed, which is when the function
           with the @handlerMethod decorator finishes, so that it does not have to
           be done manually. It commits any changes and closes the connection to the
           database'''
        if hasattr(self, 'conn'):
            self.conn.commit()
            self.conn.close()
        # Commit and close connection if connected
        else:
            print("Killing Disconnected DB Manager\n")
        # If the connection couldnt be established in the first place then
        # there is nothing to do here except warn the user that it failed


if __name__ == "__main__": # If this file is run as a program, inform the user
    print("This is not the correct file to run") # which file they should run
    print("Run the file: RTTest_Teacher.pyw") # to run the actual program
    input("Press [enter] to close")
