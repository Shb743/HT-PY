#Author:Shoaib Omar (C) 2015
#Imports
import time
from threading import Thread
import threading
import datetime
import os
#Imports

#Globals
File_Path = os.getcwd()+"/"
DOS_Candidates = {}
Blocked_Candidates = []
On = 1#Is DOS_Protect Active
Log_Out = []#Logging
ELog_Out = []#Error Logging
TLock = threading.Lock()#Thread Lock for safe cross threading
#FileName & path for Logs(For HTTPS logs an S will be added to end of the name)
ErrorLogFile=File_Path+"Server_Files/Logs/ErrorLog"
LogFile=File_Path+"Server_Files/Logs/Log"
DOSFile=File_Path+"Server_Files/Logs/DOS"
#FileName & path for Logs(For HTTPS logs an S will be added to end of the name)
Max_Concurrent_Requests = 30#Should be increased if a large number of connections(from each user) is expected[i.e:for bench marking]
#Globals

print "DOS protection service ready to start..."#on import

#Add to DOS_Candidates
def Add_Address(address):
	if (address in DOS_Candidates):
		DOS_Candidates[address] += 1
	else:
		DOS_Candidates[address] = 1
#Add to DOS_Candidates

#Add to DOS_Candidates
def Remove_Address(address):
	if (address in DOS_Candidates):
		if (DOS_Candidates[address] > 1):
			DOS_Candidates[address] -= 1
		else:
			del DOS_Candidates[address]
#Add to DOS_Candidates

#Security Checks
def Check():
	#Globals
	global On
	global Max_Concurrent_Requests
	global Blocked_Candidates
	global DOS_Candidates
	global Log_Out
	global LogFile
	global ErrorLogFile
	global TLock
	#Globals
	#Perform Checks
	while On:
		TBD = []
		TLock.acquire()#Lock threading :#
		#DOS Check
		for Candidate in DOS_Candidates:
			if (DOS_Candidates[Candidate] > Max_Concurrent_Requests):
				Blocked_Candidates.append(Candidate)
				TBD.append(Candidate)
				Possible_DOS_LOG(Candidate)
		#DOS Check
		TLock.release()#Release threading :O
		#Clear doser
		for BD in TBD:
			del DOS_Candidates[BD]
		#Clear doser
		#Logging
		if (Log_Out != []):
			Log_object = open(LogFile+".dat", "a")#Open Log File
			for i in range(len(Log_Out)):
				Log_object.write(Log_Out.pop())
			Log_object.close()
		#Logging
		#Error-Logging
		if (ELog_Out != []):
			ELog_object = open(ErrorLogFile+".dat", "a")#Open Log File
			for i in range(len(ELog_Out)):
				ELog_object.write(ELog_Out.pop())
			ELog_object.write("Date:"+datetime.datetime.now().strftime('%D')+"\n"+"Time:"+datetime.datetime.now().strftime('%H:%M')+"\n\n\n")
			ELog_object.close()
		#Error-Logging
		time.sleep(5)#Check every few seconds,i.e:- allow other threads to execute & dont hold up threads too oftn
	#Perform Checks
#Security Checks

#Alert Server owner to Possible DOS
def Possible_DOS_LOG(address):
	global DOSFile
	DOS_LOG = open(DOSFile+".dat","a")
	DLOGOUT = "Added to DOS list:"+address+"\n"
	DLOGOUT += "Date:"+datetime.datetime.now().strftime('%D')+"\n"
	DLOGOUT += "Time:"+datetime.datetime.now().strftime('%H:%M')+"\n\n"
	DOS_LOG.write(DLOGOUT)
	DOS_LOG.close()
#Alert Server owner to Possible DOS

#Main
def Init():
	Thread(target=Check, args=()).start()#Start DOS protection
#Main