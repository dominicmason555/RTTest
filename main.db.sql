BEGIN TRANSACTION;
CREATE TABLE `Topics` (
	`TopicID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`Name`	TEXT NOT NULL
);
INSERT INTO `Topics` VALUES (1,'Hardware');
INSERT INTO `Topics` VALUES (2,'Programming');
INSERT INTO `Topics` VALUES (3,'Binary');
INSERT INTO `Topics` VALUES (4,'Representation of Images');
INSERT INTO `Topics` VALUES (5,'Hexadecimal');
INSERT INTO `Topics` VALUES (6,'Software Concepts');
INSERT INTO `Topics` VALUES (7,'Operating Systems');
INSERT INTO `Topics` VALUES (8,'Networking');
INSERT INTO `Topics` VALUES (9,'Databases');
CREATE TABLE "Students" (
	`username`	TEXT NOT NULL UNIQUE,
	`pass_hash`	TEXT NOT NULL,
	PRIMARY KEY(`username`)
);
INSERT INTO `Students` VALUES ('testUser1','OkOGrYOqMP/FbGCpnL1hgbYsQK80UcF86gEd5HNh|==|1882ceccaeb17b34ee143689391de1efd805b93f791ee111273ee00fc5cca8814b209b792ae8aacf22b0de9c96c0d1ed34ec09dca0cdb9f4e75117ed168aac8e');
INSERT INTO `Students` VALUES ('testUser2','ovuKGPtqOzOmMZXOM/OqNytWds2Sh+MzMjz1HSTB|==|1459cb92eab957018e316b71252ab08d3c215e17aaa9b942db2ce7e12f21cb9f68bb658f36bf4c3b0f6c3ffb38cddd98329bb8333ed317fea742575299b6096a');
INSERT INTO `Students` VALUES ('testUser3','tLsyKvh5cTaNdzgyGUJvYtJf94EhhsGP0e0Y7j+r|==|afe2060d8cc26af63e2a1e69cefabe98eb575b6313ebfa0d5154db2d6ee5e42a963202c11974934bbf1198d5faf8b78e5ae2b39a3546d90954d5853670378d58');
INSERT INTO `Students` VALUES ('testUser4','t1Zs1KzkhYkjbE7FAHHwhlX7u2f2dzOGshXeclCH|==|807990d558a0381cbdbc38eb2149b9429eb8616c1891a5a5b06f888a7f4d1261352031497f79c36b26472beeebebd49e67524e819433cdcba8c36eaadbecd4fc');
CREATE TABLE "SingleWordQuestions" (
	`SWQuestionID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`TopicID`	INTEGER NOT NULL,
	`Question`	TEXT NOT NULL UNIQUE,
	`CorrectAnswer`	TEXT NOT NULL,
	FOREIGN KEY(`TopicID`) REFERENCES `Topics`
);
INSERT INTO `SingleWordQuestions` VALUES (1,3,'What is the decimal representation of the binary number 00101011','43');
INSERT INTO `SingleWordQuestions` VALUES (6,9,'What does the Q in SQL stand for?','query');
CREATE TABLE "PerformancePerSWQuestion" (
	`PPQSWID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`username`	TEXT NOT NULL,
	`SWQuestionID`	INTEGER NOT NULL,
	`TopicID`	INTEGER NOT NULL,
	`Date`	timestamp NOT NULL,
	`TimeTaken`	INTEGER NOT NULL,
	`Correct`	INTEGER NOT NULL,
	FOREIGN KEY(`username`) REFERENCES `Students`,
	FOREIGN KEY(`SWQuestionID`) REFERENCES `SingleWordQuestions`,
	FOREIGN KEY(`TopicID`) REFERENCES `Topics`
);
INSERT INTO `PerformancePerSWQuestion` VALUES (249,'testUser2',1,3,'2017-03-18 17:58:33.366947',2,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (251,'testUser2',1,3,'2017-03-18 17:59:33.150596',9,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (253,'testUser2',1,3,'2017-03-18 17:59:50.069794',6,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (254,'testUser2',1,3,'2017-03-18 19:03:03.816326',7,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (256,'testUser1',1,3,'2017-03-18 21:40:42.366211',4,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (257,'testUser1',1,3,'2017-03-18 21:45:11.258413',4,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (258,'testUser1',6,9,'2017-03-18 21:45:21.039948',10,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (259,'testUser1',1,3,'2017-03-18 21:47:21.896835',4,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (260,'testUser2',1,3,'2017-03-18 21:47:23.445805',5,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (261,'testUser1',6,9,'2017-03-18 21:47:40.461805',18,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (262,'testUser2',6,9,'2017-03-18 21:47:44.598003',21,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (263,'testUser1',1,3,'2017-03-18 22:33:41.964331',4,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (264,'testUser1',1,3,'2017-03-19 11:47:41.194441',11,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (265,'testUser1',6,9,'2017-03-19 18:08:53.085487',10,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (266,'testUser1',6,9,'2017-03-19 18:13:39.847187',4,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (267,'testUser1',1,3,'2017-03-19 18:13:46.796319',5,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (268,'testUser1',6,9,'2017-03-19 18:13:51.622635',4,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (269,'testUser1',6,9,'2017-03-19 18:13:55.109623',4,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (270,'testUser1',6,9,'2017-03-19 18:13:59.701163',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (271,'testUser1',1,3,'2017-03-19 18:14:02.917802',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (272,'testUser1',6,9,'2017-03-19 18:14:06.677182',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (273,'testUser1',1,3,'2017-03-19 18:19:51.477393',2,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (274,'testUser1',1,3,'2017-03-19 18:19:59.485529',1,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (275,'testUser1',1,3,'2017-03-19 18:21:11.445335',2,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (276,'testUser1',6,9,'2017-03-19 18:21:23.953260',4,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (277,'testUser1',6,9,'2017-03-19 18:23:06.874989',4,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (278,'testUser1',1,3,'2017-03-19 18:23:20.701455',2,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (279,'testUser1',1,3,'2017-03-19 18:23:26.532609',1,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (280,'testUser1',6,9,'2017-03-19 18:23:49.093101',2,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (281,'testUser1',6,9,'2017-03-19 18:23:54.245195',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (282,'testUser1',1,3,'2017-03-19 18:23:56.916462',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (283,'testUser1',6,9,'2017-03-19 19:07:59.387485',5,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (284,'testUser1',6,9,'2017-03-19 19:08:02.739409',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (285,'testUser1',1,3,'2017-03-19 19:08:47.596193',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (286,'testUser1',1,3,'2017-03-19 19:08:53.748438',6,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (287,'testUser1',1,3,'2017-03-19 19:09:53.571978',3,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (288,'testUser1',1,3,'2017-03-19 21:32:10.198865',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (289,'testUser1',1,3,'2017-03-19 21:33:40.535391',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (290,'testUser1',1,3,'2017-03-20 10:51:44.846864',4,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (291,'testUser1',1,3,'2017-03-20 11:08:08.509321',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (292,'testUser1',1,3,'2017-03-20 11:08:10.581149',2,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (293,'testUser1',6,9,'2017-03-20 11:08:41.077042',1,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (294,'testUser1',6,9,'2017-03-20 11:09:18.876918',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (295,'testUser1',6,9,'2017-03-20 11:10:39.213344',6,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (296,'testUser1',6,9,'2017-03-20 11:11:27.974871',2,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (297,'testUser1',1,3,'2017-03-20 11:15:18.109959',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (298,'testUser1',1,3,'2017-03-20 11:15:19.975031',2,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (299,'testUser1',1,3,'2017-03-20 11:16:49.253658',2,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (300,'testUser1',1,3,'2017-03-20 11:16:50.607170',1,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (301,'testUser1',1,3,'2017-03-20 11:16:51.767982',1,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (302,'testUser1',1,3,'2017-03-20 11:16:52.985824',2,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (303,'testUser1',1,3,'2017-03-20 11:19:23.926563',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (304,'testUser1',1,3,'2017-03-20 11:19:24.852320',0,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (305,'testUser1',1,3,'2017-03-20 11:19:25.873110',0,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (306,'testUser1',1,3,'2017-03-20 11:19:27.524628',1,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (307,'testUser1',1,3,'2017-03-20 11:25:53.048869',4,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (308,'testUser1',1,3,'2017-03-20 11:49:50.073484',5,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (309,'testUser1',6,9,'2017-03-20 11:49:53.420901',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (310,'testUser1',6,9,'2017-03-20 20:27:16.171002',4,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (311,'testUser1',1,3,'2017-03-20 20:27:49.436388',1,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (312,'testUser1',6,9,'2017-03-20 20:28:35.753589',4,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (313,'testUser1',6,9,'2017-03-20 20:28:38.510371',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (314,'testUser1',6,9,'2017-03-20 20:28:44.356664',5,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (315,'testUser1',6,9,'2017-03-20 20:28:47.591583',4,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (316,'testUser2',1,3,'2017-03-20 20:29:52.566050',6,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (317,'testUser1',6,9,'2017-03-20 20:29:58.403248',12,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (318,'testUser2',6,9,'2017-03-20 20:30:26.265532',18,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (319,'testUser1',1,3,'2017-03-20 20:30:36.428877',7,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (320,'testUser1',6,9,'2017-03-20 20:30:40.620863',4,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (321,'testUser1',1,3,'2017-03-20 20:30:48.243747',4,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (322,'testUser1',6,9,'2017-03-20 20:31:02.380303',15,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (323,'testUser1',6,9,'2017-03-20 20:31:05.364701',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (324,'testUser2',1,3,'2017-03-20 21:23:10.965521',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (325,'testUser2',1,3,'2017-03-20 21:24:29.908353',2,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (326,'testUser2',1,3,'2017-03-20 21:24:31.258236',1,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (327,'testUser2',1,3,'2017-03-20 21:24:32.389064',1,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (328,'testUser2',1,3,'2017-03-20 21:24:34.198702',1,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (329,'testUser2',6,9,'2017-03-20 21:25:06.292412',5,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (330,'testUser1',6,9,'2017-03-20 21:25:10.002966',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (331,'testUser2',6,9,'2017-03-20 21:39:07.502457',4,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (332,'testUser1',6,9,'2017-03-20 21:39:09.179042',5,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (333,'testUser1',6,9,'2017-03-20 21:39:11.946432',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (334,'testUser2',6,9,'2017-03-20 21:39:14.284585',6,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (335,'testUser2',1,3,'2017-03-20 21:57:59.781783',9,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (336,'testUser2',1,3,'2017-03-20 21:59:46.084877',11,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (337,'testUser2',1,3,'2017-03-20 22:00:00.493230',15,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (338,'testUser2',1,3,'2017-03-20 22:00:03.619117',3,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (339,'testUser2',1,3,'2017-03-20 22:00:06.444920',2,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (340,'testUser2',1,3,'2017-03-20 22:00:08.782584',2,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (341,'testUser2',1,3,'2017-03-20 22:00:11.910182',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (342,'testUser1',1,3,'2017-03-23 09:04:28.122338',13,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (343,'testUser1',1,3,'2017-03-23 09:04:39.433904',12,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (344,'testUser1',1,3,'2017-03-23 09:05:47.016938',5,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (345,'testUser2',6,9,'2017-03-23 09:05:54.673798',13,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (346,'testUser2',6,9,'2017-03-23 09:06:01.064730',6,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (347,'testUser2',6,9,'2017-03-23 09:06:21.522449',15,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (348,'testUser2',6,9,'2017-03-23 09:06:28.505323',6,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (349,'testUser1',1,3,'2017-03-23 09:55:44.507723',4,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (350,'testUser1',1,3,'2017-03-23 09:55:50.028570',5,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (351,'testUser1',6,9,'2017-03-23 09:58:29.139964',10,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (352,'testUser1',1,3,'2017-03-23 09:58:32.788532',4,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (353,'testUser1',1,3,'2017-03-23 09:58:37.003997',4,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (354,'testUser1',1,3,'2017-03-24 13:32:25.269939',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (355,'testUser1',6,9,'2017-03-24 13:32:34.413308',6,0);
INSERT INTO `PerformancePerSWQuestion` VALUES (356,'testUser1',6,9,'2017-03-24 13:44:26.750787',5,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (357,'testUser2',6,9,'2017-03-24 13:44:30.884742',9,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (358,'testUser2',6,9,'2017-03-24 13:45:40.026822',10,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (359,'testUser1',6,9,'2017-03-24 13:45:40.689454',10,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (360,'testUser2',6,9,'2017-03-24 13:45:51.467747',6,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (362,'testUser2',6,9,'2017-03-24 13:46:17.539644',6,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (364,'testUser2',6,9,'2017-03-24 13:46:23.465302',4,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (365,'testUser2',1,3,'2017-03-24 13:46:26.169885',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (366,'testUser1',1,3,'2017-03-24 13:46:28.329947',18,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (367,'testUser2',6,9,'2017-03-24 13:46:32.091540',6,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (368,'testUser1',1,3,'2017-03-24 13:46:46.952731',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (369,'testUser1',6,9,'2017-03-24 13:46:51.700264',3,1);
INSERT INTO `PerformancePerSWQuestion` VALUES (370,'testUser1',6,9,'2017-03-25 16:36:30.163361',78,0);
CREATE TABLE "PerformancePerMCQuestion" (
	`PPQMCID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`username`	TEXT NOT NULL,
	`MCQuestionID`	INTEGER NOT NULL,
	`TopicID`	INTEGER NOT NULL,
	`Date`	timestamp NOT NULL,
	`TimeTaken`	INTEGER NOT NULL,
	`Correct`	INTEGER NOT NULL,
	FOREIGN KEY(`username`) REFERENCES `Students`,
	FOREIGN KEY(`MCQuestionID`) REFERENCES `MultipleChoiceQuestions`,
	FOREIGN KEY(`TopicID`) REFERENCES `Topics`
);
INSERT INTO `PerformancePerMCQuestion` VALUES (55,'testUser2',3,9,'2017-03-07 20:15:16.817809',10,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (58,'testUser2',1,9,'2017-03-07 20:15:32.017967',2,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (62,'testUser2',1,9,'2017-03-07 20:16:14.818001',9,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (64,'testUser2',1,9,'2017-03-07 20:17:36.742065',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (65,'testUser2',3,9,'2017-03-07 20:18:12.570785',36,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (66,'testUser2',1,9,'2017-03-07 20:18:21.657068',9,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (112,'testUser2',3,9,'2017-03-07 20:29:25.993210',4,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (113,'testUser2',1,9,'2017-03-07 20:30:33.312490',68,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (114,'testUser2',1,9,'2017-03-07 20:30:35.912834',2,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (118,'testUser2',3,9,'2017-03-07 20:30:57.224533',20,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (121,'testUser2',1,9,'2017-03-07 21:43:40.956845',3,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (318,'testUser1',2,1,'2017-03-18 21:45:24.580588',4,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (319,'testUser1',1,9,'2017-03-18 21:45:27.614011',3,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (320,'testUser1',3,9,'2017-03-18 21:45:33.973280',6,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (321,'testUser1',2,1,'2017-03-18 21:47:42.338336',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (322,'testUser1',1,9,'2017-03-18 21:48:27.883129',46,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (323,'testUser2',2,1,'2017-03-18 21:48:29.382552',44,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (324,'testUser2',1,9,'2017-03-18 21:48:33.814518',5,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (325,'testUser1',3,9,'2017-03-18 21:48:36.383744',8,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (326,'testUser2',3,9,'2017-03-18 21:48:38.382809',4,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (327,'testUser1',3,9,'2017-03-19 18:10:10.453209',6,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (328,'testUser1',1,9,'2017-03-19 18:13:35.956666',4,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (329,'testUser1',1,9,'2017-03-19 18:13:41.973291',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (330,'testUser1',1,9,'2017-03-19 18:13:56.493125',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (331,'testUser1',1,9,'2017-03-19 18:19:47.980929',4,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (332,'testUser1',1,9,'2017-03-19 18:19:48.932170',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (333,'testUser1',1,9,'2017-03-19 18:19:52.460199',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (334,'testUser1',3,9,'2017-03-19 18:19:54.284296',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (335,'testUser1',1,9,'2017-03-19 18:19:55.852773',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (336,'testUser1',1,9,'2017-03-19 18:19:56.972528',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (337,'testUser1',1,9,'2017-03-19 18:19:57.804375',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (338,'testUser1',1,9,'2017-03-19 18:20:00.620851',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (339,'testUser1',3,9,'2017-03-19 18:20:58.070104',14,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (340,'testUser1',3,9,'2017-03-19 18:21:08.717043',10,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (341,'testUser1',2,1,'2017-03-19 18:21:12.997761',2,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (342,'testUser1',3,9,'2017-03-19 18:21:14.181077',1,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (343,'testUser1',2,1,'2017-03-19 18:21:15.676502',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (344,'testUser1',2,1,'2017-03-19 18:21:17.245593',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (345,'testUser1',3,9,'2017-03-19 18:21:18.588974',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (346,'testUser1',3,9,'2017-03-19 18:21:19.662778',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (347,'testUser1',3,9,'2017-03-19 18:21:38.470656',4,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (348,'testUser1',3,9,'2017-03-19 18:21:38.964797',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (349,'testUser1',3,9,'2017-03-19 18:21:39.363930',0,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (350,'testUser1',3,9,'2017-03-19 18:21:40.037101',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (351,'testUser1',3,9,'2017-03-19 18:23:23.469242',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (352,'testUser1',3,9,'2017-03-19 18:23:24.708092',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (353,'testUser1',3,9,'2017-03-19 18:23:28.093621',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (354,'testUser1',3,9,'2017-03-19 18:23:29.014345',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (355,'testUser1',3,9,'2017-03-19 18:23:46.820468',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (356,'testUser1',1,9,'2017-03-19 18:23:51.029150',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (357,'testUser1',3,9,'2017-03-19 18:52:21.820018',3,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (358,'testUser1',1,9,'2017-03-19 19:10:36.772385',3,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (359,'testUser1',1,9,'2017-03-19 19:10:43.797632',6,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (360,'testUser1',3,9,'2017-03-19 21:34:30.087292',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (361,'testUser1',1,9,'2017-03-20 11:11:24.945985',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (362,'testUser1',3,9,'2017-03-20 11:11:29.990682',1,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (363,'testUser1',3,9,'2017-03-20 11:14:30.893852',1,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (364,'testUser1',3,9,'2017-03-20 11:14:32.367816',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (365,'testUser1',1,9,'2017-03-20 11:14:34.030772',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (366,'testUser1',1,9,'2017-03-20 11:14:35.350730',1,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (367,'testUser1',2,1,'2017-03-20 11:15:22.703031',3,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (368,'testUser1',1,9,'2017-03-20 11:15:24.234112',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (369,'testUser1',1,9,'2017-03-20 11:25:54.709310',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (370,'testUser1',2,1,'2017-03-20 11:49:56.454924',3,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (371,'testUser1',1,9,'2017-03-20 11:49:57.777321',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (372,'testUser1',3,9,'2017-03-20 11:49:59.398758',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (373,'testUser1',2,1,'2017-03-20 20:27:47.397170',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (374,'testUser1',2,1,'2017-03-20 20:28:25.709257',7,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (375,'testUser1',2,1,'2017-03-20 20:28:28.168098',2,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (376,'testUser1',1,9,'2017-03-20 20:28:29.791112',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (377,'testUser1',2,1,'2017-03-20 20:28:32.222431',2,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (378,'testUser2',3,9,'2017-03-20 20:30:07.771779',15,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (379,'testUser1',2,1,'2017-03-20 20:30:29.748171',31,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (380,'testUser2',2,1,'2017-03-20 20:30:33.520773',8,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (381,'testUser2',2,1,'2017-03-20 20:30:38.182874',4,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (382,'testUser2',1,9,'2017-03-20 20:30:42.255328',4,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (383,'testUser1',2,1,'2017-03-20 20:30:43.467173',3,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (384,'testUser2',1,9,'2017-03-20 20:30:45.116247',3,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (385,'testUser2',3,9,'2017-03-20 20:30:59.238264',14,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (386,'testUser2',3,9,'2017-03-20 21:23:06.782506',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (387,'testUser2',3,9,'2017-03-20 21:23:08.309940',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (388,'testUser2',2,1,'2017-03-20 21:24:59.988651',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (389,'testUser2',2,1,'2017-03-20 21:25:00.925417',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (390,'testUser1',2,1,'2017-03-20 21:25:01.906696',4,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (391,'testUser1',2,1,'2017-03-20 21:25:07.034623',5,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (392,'testUser2',2,1,'2017-03-20 21:25:11.261824',5,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (393,'testUser1',2,1,'2017-03-20 21:25:12.539637',3,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (394,'testUser2',1,9,'2017-03-20 21:41:28.069028',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (395,'testUser1',1,9,'2017-03-20 21:41:31.772959',5,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (396,'testUser2',1,9,'2017-03-20 21:41:33.013310',5,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (397,'testUser1',1,9,'2017-03-20 21:41:35.773094',4,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (398,'testUser1',2,1,'2017-03-23 09:04:14.660429',11,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (399,'testUser1',2,1,'2017-03-23 09:04:52.225907',12,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (400,'testUser2',3,9,'2017-03-23 09:06:06.321217',5,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (401,'testUser1',2,1,'2017-03-23 09:06:37.929407',51,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (402,'testUser1',2,1,'2017-03-23 09:06:39.653955',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (403,'testUser1',2,1,'2017-03-23 09:06:41.014448',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (404,'testUser1',2,1,'2017-03-23 09:06:42.366307',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (405,'testUser2',2,1,'2017-03-23 09:07:02.801568',4,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (406,'testUser2',2,1,'2017-03-23 09:07:04.829918',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (407,'testUser2',1,9,'2017-03-23 09:07:23.338084',18,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (408,'testUser2',2,1,'2017-03-23 09:07:25.445120',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (409,'testUser2',2,1,'2017-03-23 09:07:28.237029',3,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (410,'testUser1',2,1,'2017-03-23 09:08:10.857231',6,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (411,'testUser1',2,1,'2017-03-23 09:08:12.341363',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (412,'testUser1',2,1,'2017-03-23 09:08:13.956898',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (413,'testUser1',2,1,'2017-03-23 09:08:16.150000',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (414,'testUser1',2,1,'2017-03-23 09:08:18.413856',3,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (415,'testUser2',3,9,'2017-03-23 09:08:37.585795',6,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (416,'testUser2',1,9,'2017-03-23 09:08:43.729560',6,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (417,'testUser2',1,9,'2017-03-23 09:08:45.149540',1,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (418,'testUser2',1,9,'2017-03-23 09:08:45.894056',1,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (419,'testUser2',1,9,'2017-03-23 09:08:46.662323',1,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (420,'testUser1',3,9,'2017-03-23 09:55:28.507303',6,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (421,'testUser1',3,9,'2017-03-23 09:55:30.627262',2,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (422,'testUser1',2,1,'2017-03-23 09:55:36.580838',6,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (423,'testUser1',1,9,'2017-03-23 09:55:38.346741',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (424,'testUser1',2,1,'2017-03-23 09:55:40.346316',2,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (425,'testUser1',2,1,'2017-03-23 09:55:53.116895',3,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (426,'testUser1',1,9,'2017-03-23 09:55:55.475063',3,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (427,'testUser1',2,1,'2017-03-23 09:55:57.699654',2,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (428,'testUser1',2,1,'2017-03-23 09:57:29.163816',4,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (429,'testUser1',2,1,'2017-03-23 09:57:38.107949',9,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (430,'testUser1',2,1,'2017-03-23 09:57:39.539395',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (431,'testUser1',2,1,'2017-03-23 09:58:18.779874',3,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (432,'testUser1',2,1,'2017-03-24 13:32:09.938221',18,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (433,'testUser1',2,1,'2017-03-24 13:32:20.148522',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (434,'testUser1',2,1,'2017-03-24 13:32:21.995532',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (435,'testUser1',1,9,'2017-03-24 13:32:28.430422',3,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (436,'testUser1',1,9,'2017-03-24 13:32:52.341546',18,0);
INSERT INTO `PerformancePerMCQuestion` VALUES (438,'testUser2',1,9,'2017-03-24 13:45:45.853385',5,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (439,'testUser1',1,9,'2017-03-24 13:45:46.457971',6,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (440,'testUser1',2,1,'2017-03-24 13:46:06.299920',20,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (441,'testUser1',1,9,'2017-03-24 13:46:08.449964',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (442,'testUser1',2,1,'2017-03-24 13:46:10.553973',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (443,'testUser2',2,1,'2017-03-24 13:46:11.698066',20,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (445,'testUser2',1,9,'2017-03-24 13:46:19.569582',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (449,'testUser2',3,9,'2017-03-24 13:46:34.457800',2,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (453,'testUser1',1,9,'2017-03-24 13:46:44.618502',16,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (454,'testUser1',1,9,'2017-03-24 13:46:48.265985',1,1);
INSERT INTO `PerformancePerMCQuestion` VALUES (455,'testUser1',3,9,'2017-03-25 16:37:18.848732',49,1);
CREATE TABLE `MultipleChoiceQuestions` (
	`MCQuestionID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`TopicID`	INTEGER NOT NULL,
	`Question`	TEXT NOT NULL UNIQUE,
	`Answer1`	TEXT NOT NULL,
	`Answer2`	TEXT NOT NULL,
	`Answer3`	TEXT,
	`Answer4`	TEXT,
	`CorrectAnswer`	INTEGER NOT NULL,
	FOREIGN KEY(`TopicID`) REFERENCES Topics
);
INSERT INTO `MultipleChoiceQuestions` VALUES (1,9,'What is the SQL command to retrieve data from a table?','RETRIEVE','EXTRACT','SELECT',NULL,3);
INSERT INTO `MultipleChoiceQuestions` VALUES (2,1,'What is meant by the volatile memory?','The memory could break at any time','The memory will keep its contents when it is not receiving power','The memory will not keep its contents when it is not receiving power','The memory will not keep its contents when it is receiving power',3);
INSERT INTO `MultipleChoiceQuestions` VALUES (3,9,'What is the SQL command to remove a table from a database?','DROP TABLE','DELETE TABLE','DESTROY TABLE',NULL,1);
COMMIT;
