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
On = 1#Is service Active
Max_Concurrent_Requests = 30#Should be increased if large number of connections are expected
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
	#Globals
	#Perform Checks
	while On:
		TBD = []
		for Candidate in DOS_Candidates:
			if (DOS_Candidates[Candidate] > Max_Concurrent_Requests):
				Blocked_Candidates.append(Candidate)
				TBD.append(Candidate)
				Possible_DOS_LOG(Candidate)
		#Clear doser
		for BD in TBD:
			del DOS_Candidates[BD]
		#Clear doser
		time.sleep(3.5)#Check every few seconds,i.e:- allow other threads to execute
	#Perform Checks
#Security Checks

#Alert Server owner to Possible DOS
def Possible_DOS_LOG(address):
	DOS_LOG = open(File_Path+"Server_Files/Logs/DOS.dat","a+")
	DOS_LOG.write("Added to DOS list:"+address+"\n")
	DOS_LOG.write("Date:"+str(datetime.datetime.utcnow().day)+"/"+str(datetime.datetime.utcnow().month)+"/"+str(datetime.datetime.utcnow().year)+"\n")
	DOS_LOG.write("Time:"+str(datetime.datetime.utcnow().hour)+":"+str(datetime.datetime.utcnow().minute)+"\n\n")
	DOS_LOG.close()
#Alert Server owner to Possible DOS

#Main
def Init():
	Thread(target=Check, args=()).start()#Start DOS protection
#Main
