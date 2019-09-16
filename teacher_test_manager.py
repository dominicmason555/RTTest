# This file manages the currently set test of the teacher program
# it should not be run directly, it is for the teacher program to import

# Created by Dominic Mason

import random

class TestMgr():
    '''This class represents a test, it stores all of the information
       about the test that the teacher specifies and it can choose
       questions to give to students using the weighting method
       that the teacher selected'''
    def __init__(self, testRequest):
        '''Store all of the data of the request and initialise variables'''
        print("Starting Test")
        self.currentTest = testRequest
        self.currentUsers = testRequest["users"]
        self.questionsPerUser = testRequest["data"]
        self.storing = testRequest["storing"]
        self.setQuestions = {}
        self.autoEnabled = testRequest["auto"]
        if self.autoEnabled:
            self.testLength = testRequest["length"]
        self.questionCount = {}
        for user in self.currentUsers:
            self.setQuestions[user] = []
            self.questionCount[user] = 0
        
    def getUsers(self):
        '''Returns the users that the test applies to'''
        return self.currentUsers
        
    def getStoring(self):
        '''Returns whether or not the current test is 
           storing results'''
        return self.storing
        
    def checkFinished(self, user):
        '''Determines if there are any more questions
           for the specified user'''
        finished = True
        if user not in self.setQuestions:
            return True
        for questionSet in self.questionsPerUser:
            if questionSet["username"] == user:
                for question in questionSet["questionList"]:
                    if question not in self.setQuestions["user"]:
                        return False
        return True
        
    def getQuestion(self, user):
        '''Gets the next question for a user, if one is available'''
        if self.autoEnabled:
            return self.getQuestionAuto(user)
        else:
            return self.getQuestionNonAuto(user)
        
    def getQuestionAuto(self, user):
        '''Automatically choose the next question for a user, using
           the weights determined by the database thread'''
        if user not in self.questionCount:
            return False
        if self.questionCount[user] >= self.testLength:
            return False
        # Cancel if the test is over or the user isnt in the test
        total = 0
        toChooseFrom = []
        for question in self.questionsPerUser:
            if question["username"] == user:
                toChooseFrom = list(question["questionList"])
                break
        if not toChooseFrom:
            return False
        # Get all of the available questions to choose from
        for item in toChooseFrom:
            print("toChooseFrom", item)
            item["start"] = total
            item["end"] = total + item["weight"]
            total += item["weight"]
        # Set each question a section of a range of numbers where
        # the section is the size of the questions weight, so that
        # when a random value is chosen between 0 and the total of
        # all of the weights, it will have a higher chance of landing
        # in a section belonging to a question with a higher weight
        choice = random.randint(0,total)
        for original in toChooseFrom:
            item = dict(original)
            if item["start"] <= choice and item["end"] >= choice:
                # Then that item is the owner of the section that the
                # random generator chose
                print("Chosen question with weight:", item["weight"])
                unnecessary = ["start", "end", "weight", "answer", "correct"]
                for key in unnecessary:
                    if key in item:
                        item.pop(key)
                # Clean the temporary values for choosing from the question
                item.update({"action":"question"})
                print("Found question {} for {}".format(item, user))
                self.setQuestions[user].append(item)
                self.questionCount[user] += 1
                # Add the question to the list of questions that the
                # user has already had and increment the number of
                # questions that user has had
                return item
        return False
        
    def getQuestionNonAuto(self, user):
        '''Chooses each of the set questions once and then ends'''
        if user not in self.setQuestions:
            return False
        # Cancel if the test doesnt apply to that user
        for questionSet in self.questionsPerUser:
            if questionSet["username"] == user:
                for question in questionSet["questionList"]:
                    if question not in self.setQuestions[user]:
                        # If the user has been allocated a question but has not
                        # received it yet, then it is a valid choice
                        question.update({"action":"question"})
                        print("Found question {} for {}".format(question, user))
                        self.setQuestions[user].append(question)
                        self.questionCount[user] += 1
                        # Add the question to the list of questions that the
                        # user has already had and increment the number of
                        # questions that user has had
                        print(self.setQuestions, self.questionCount)
                        return question
        return False



if __name__ == "__main__": # If this file is run as a program, inform the user
    print("This is not the correct file to run") # which file they should run
    print("Run the file: RTTest_Teacher.pyw") # to run the actual program
    input("Press [enter] to close")
