# This file contains all of the dialog classes for the teacher program
# it should not be run directly, it is for the teacher program to import

# Created by Dominic Mason

import random
from PyQt5 import QtNetwork, QtCore, QtGui, uic

class AddEditUserDialog(QtGui.QDialog):
   '''This is the dialog for both adding and editing users. The only difference is the title of the window
      and that if it is in edit mode, the username is set to the username that was selected rather than being
      left blank. Also the request sent to the database thread is different. Instances have to be passed the 
      database send queue in order to send requests to it.'''
   def __init__(self, dbSendQueue, user=None):
      super().__init__()
      self.dbSendQueue = dbSendQueue
      self.user = user
      if self.user:
         self.title = "Edit User"
         self.nameEdit = QtGui.QLineEdit(self.user)
         self.nameEdit.setEnabled = False
      else:
         self.title = "Add User"
         self.nameEdit = QtGui.QLineEdit("")
      # Determine whether it is adding or editing a user
      self.nameLabel = QtGui.QLabel("Username:")
      self.passLabel = QtGui.QLabel("Password:")
      self.passEdit = QtGui.QLineEdit("")
      self.passEdit.setEchoMode(QtGui.QLineEdit.Password)
      self.okButton = QtGui.QPushButton(self.title)
      self.okButton.clicked.connect(self.ok)
      self.okButton.setEnabled(True)
      self.cancelButton = QtGui.QPushButton("Cancel")
      self.cancelButton.setEnabled(True)
      self.cancelButton.clicked.connect(self.close)
      # Create and connect the GUI items
      layout = QtGui.QVBoxLayout()
      layout.addWidget(self.nameLabel)
      layout.addWidget(self.nameEdit)
      layout.addWidget(self.passLabel)
      layout.addWidget(self.passEdit)
      layout.addWidget(self.okButton)
      layout.addWidget(self.cancelButton)
      # Add the GUi items to a box layout
      self.setLayout(layout)
      self.nameEdit.setFocus()
      self.setWindowTitle(self.title)
      self.show()
      # Show the dialog window
   def ok(self):
      if self.user:
         request = {"action": "editUser", "completed": "User Edited Successfully", "errorText": "Error Editing User"}
      else:
         request = {"action": "addUser", "completed": "User Added Successfully", "errorText": "Error Adding User"}
      request["username"] = self.nameEdit.text()
      request["password"] = self.passEdit.text()
      self.dbSendQueue.put(request)
      self.close()
      # Send the request to the database and then close
      
class AddEditTopicDialog(QtGui.QDialog):
   '''This is the dialog for both adding and editing topics. The original plan was for users and topics
      to share a dialog to make the program more concise, but since all of the GUI items would have to be 
      different, I decided to use two dialogs, which look very similar. Instances have to be passed the 
      database send queue in order to send requests to it'''
   def __init__(self, dbSendQueue, selected=None):
      super().__init__()
      self.dbSendQueue = dbSendQueue
      self.selected = selected
      self.numSpin = QtGui.QSpinBox()
      if self.selected:
         self.title = "Edit Topic"
         self.nameEdit = QtGui.QLineEdit(self.selected[1])
         self.numSpin.setValue(int(selected[0]))
      else:
         self.title = "Add Topic"
         self.nameEdit = QtGui.QLineEdit("")
      # Determine whether it is adding or editing a topic
      self.topicLabel = QtGui.QLabel("Topic:")
      self.numLabel = QtGui.QLabel("ID:")
      self.numSpin.setMinimum(0)
      self.okButton = QtGui.QPushButton(self.title)
      self.okButton.clicked.connect(self.ok)
      self.okButton.setEnabled(True)
      self.cancelButton = QtGui.QPushButton("Cancel")
      self.cancelButton.setEnabled(True)
      self.cancelButton.clicked.connect(self.close)
      # Create and connect the GUI items
      layout = QtGui.QVBoxLayout()
      layout.addWidget(self.topicLabel)
      layout.addWidget(self.nameEdit)
      layout.addWidget(self.numLabel)
      layout.addWidget(self.numSpin)
      layout.addWidget(self.okButton)
      layout.addWidget(self.cancelButton)
      # Add the GUi items to a box layout
      self.setLayout(layout)
      self.nameEdit.setFocus()
      self.setWindowTitle(self.title)
      self.show()
      # Show the dialog window
   def ok(self):
      if self.selected:
         request = {"action": "editTopic", "completed": "Topic Edited Successfully", "errorText": "Error Editing Topic"}
         request["id"] = self.selected[0]
      else:
         request = {"action": "addTopic", "completed": "Topic Added Successfully", "errorText": "Error Adding Topic"}
      request["name"] = self.nameEdit.text()
      request["newID"] = self.numSpin.value()
      self.dbSendQueue.put(request)
      self.close()
      # Send the request to the database and then close
      
class AddEditMCQDialog(QtGui.QDialog):
   '''This is the dialog for both adding and editing multiple choice questions. If it is 
      editing a question, then the input widgets all initialise to the values of the selected 
      question. A lot of logic is required to facilitate different numbers of answers.
      Instances have to be passed the database send queue in order to send requests to it'''
   def __init__(self, dbSendQueue, question=None):
      super().__init__()
      uic.loadUi("teacher_edit_mc.ui", self)
      # This GUI was too complicated to design in the code, so I used QT designer,
      # as I did with the main window to design it. QT designer also allows you
      # to connect signals and slots without any code for simple tasks such as 
      # disabling sections that are not applicable when a box is unchecked.
      # The .ui file is an XML representation of the dialog, and this line
      # creates all of the objects and layouts at runtime.
      self.buttonBox.accepted.connect(self.ok)
      self.question = None
      self.dbSendQueue = dbSendQueue
      self.two_answers.setChecked(True)
      self.correct_1.setChecked(True)
      # Set the default values before any more are loaded
      if question:
         self.question = question
         print(self.question)
         self.topic_spin.setValue(self.question[1])
         self.question_edit.appendPlainText(self.question[2])
         self.answer1.setText(self.question[3])
         self.answer2.setText(self.question[4])
         if self.question[5] != None:
            self.three_answers.setChecked(True)
            self.answer3.setText(self.question[5])
         if self.question[6] != None:
            self.four_answers.setChecked(True)
            self.answer4.setText(self.question[6])
         if question[7] == 1:
            self.correct_1.setChecked(True)
         if question[7] == 2:
            self.correct_2.setChecked(True)
         if question[7] == 3:
            self.correct_3.setChecked(True)
         if question[7] == 4:
            self.correct_4.setChecked(True)
         # Set the widgets to the values from the chosen question if in edit mode
      self.setFixedSize(self.size())
      self.show()
   def ok(self):
      print("Adding/Editing MC Question")
      newQuestion = {"question":self.question_edit.toPlainText()}
      newQuestion.update({"answer1":self.answer1.text()})
      newQuestion.update({"answer2":self.answer2.text()})
      if self.three_answers.isChecked() or self.four_answers.isChecked():
         newQuestion.update({"answer3":self.answer3.text()})
      else:
         newQuestion.update({"answer3":None})
      if self.four_answers.isChecked():
         newQuestion.update({"answer4":self.answer4.text()})
      else:
         newQuestion.update({"answer4":None})
      if self.correct_1.isChecked():
         newQuestion.update({"correct":1})
      if self.correct_2.isChecked():
         newQuestion.update({"correct":2})
      if self.correct_3.isChecked():
         if self.three_answers.isChecked() or self.four_answers.isChecked():
            newQuestion.update({"correct":3})
         else:
            return
      if self.correct_4.isChecked():
         if self.three_answers.isChecked() or self.four_answers.isChecked():
            newQuestion.update({"correct":4})
         else:
            return
      newQuestion.update({"topicID":self.topic_spin.value()})
      # Create the request from the inputted values
      if self.question:
         newQuestion.update({"qid":self.question[0]})
      else:
         newQuestion.update({"qid":None})
      self.dbSendQueue.put({"action":"addEditQuestion", "qType":"MC", "question":newQuestion})
      self.close()
      # Send the request and close the dialog
      
class AddEditSWQDialog(QtGui.QDialog):
   '''This is the dialog for both adding and editing single word questions. 
      If it is editing a question, then the input widgets all initialise to 
      the values of the selected question. Instances have to be passed the 
      database send queue in order to send requests to it'''
   def __init__(self, dbSendQueue, question=None):
      super().__init__()
      uic.loadUi("teacher_edit_sw.ui", self)
      # This ui could probably have been hardcoded, but it would have taken longer
      self.question = None
      self.dbSendQueue = dbSendQueue
      self.buttonBox.accepted.connect(self.ok)
      if question:
         self.question = question
         print(self.question)
         self.topic_spin.setValue(self.question[1])
         self.question_edit.appendPlainText(self.question[2])
         self.answer1.setText(self.question[3])
      # Load the values from the selected question if there is one
      self.setFixedSize(self.size())
      self.show()
   def ok(self):
      print("Adding/Editing SW Question")
      newQuestion = {"question":self.question_edit.toPlainText()}
      newQuestion.update({"answer":self.answer1.text()})
      newQuestion.update({"topicID":self.topic_spin.value()})
      if self.question:
         newQuestion.update({"qid":self.question[0]})
      else:
         newQuestion.update({"qid":None})
      self.dbSendQueue.put({"action":"addEditQuestion", "qType":"SW", "question":newQuestion})
      self.close()
      # Send the request and close the dialog
      
class RTAnswersLogDialog(QtGui.QDialog):
   '''This is a small console-like window for displaying results in real time
      to the teacher, it can be either all of the results at once or the results
      of one specific student. It automatically scrolls to the bottom whenever a
      new line is added.'''
   def __init__(self, model):
      super().__init__()
      self.listView = QtGui.QListView()
      self.listView.setModel(model)
      self.listView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
      layout = QtGui.QVBoxLayout()
      layout.addWidget(self.listView)
      self.setLayout(layout)
      # Creates and sets the layout
      self.setWindowTitle("Realtime Log")
      self.setMinimumSize(450, 130)
      self.show()
   def scrollToBottom(self):
      '''Scrolls the view to the bottom.'''
      bar = self.listView.verticalScrollBar()
      bar.setValue(bar.maximum())


if __name__ == "__main__": # If this file is run as a program, inform the user
    print("This is not the correct file to run") # which file they should run
    print("Run the file: RTTest_Teacher.pyw") # to run the actual program
    input("Press [enter] to close")
