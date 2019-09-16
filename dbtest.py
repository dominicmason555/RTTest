import sqlite3

con = sqlite3.connect("main.db", detect_types=sqlite3.PARSE_DECLTYPES)
cur = con.cursor()
cur.execute("select * from PerformancePerMCQuestion join MultipleChoiceQuestions using (MCQuestionID) where MultipleChoiceQuestions.TopicID = 1")
print(cur.fetchall())
con.close()