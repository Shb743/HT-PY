#Author:Shoaib Omar (C) 2015

#Imports
import socket#We need you Mr. Sock!
import threading#Mutex Locks :$
from threading import Thread#Multi Threading Yay :)
from multiprocessing import Process#Multi processing Yay :)
import datetime#Needed for logging purposes
import os,sys#System Stuffs :#
import urllib#Needed to unquote URLS
import json#Decoding Settings File :O
import uuid#Generating Temporary file names & Service Thread ID's ~
import GF#Global Functions
import Custom#Custom Handling of requests
import HouseKeeping#My HouseKeeping Script !(Takes care of logging & DOS protection)
import time#Time out,sleeping etc...
#Imports*

#GLOBALS

#Should not be messed with!(you can change them,but I don't advise it)
TLock = threading.Lock()#Thread Lock for safe cross threading
HTTPSProc = None#Define process for SSL.
On = 1#Is the Server Running.
Server_file_path = os.getcwd()+"/Server_Files/"#Server Path.
Allowed_Directories = []#Place Holder.
White_List = None#Place Holder.
Black_List = None#Place Holder.
SSL_Context = None#Place Holder.
SHB_Mime = []# SHB MIME !
Default = ["index.html","main.html"] #Default file to load.
Settings_file = "Settings.dat"#Load Settings.
Allowed_Directories_File = "Allowed_Dirs.dat"#Load Allowed Directories Dat.
Socket_Backlog = 5#MAX number of clients waiting to be accepted(in socket que).
SNTBLN = 5 # (Spawn New Thread BackLog Number - if the waiting_que size is greater than this a new service thread will be spawned)
BuffSize = 1024#Size of buffer for recv
#Should not be messed with!(you can change them,but I don't advise it)

#User Changeable
Ip=""#IP(if left blank will bind to all available interfaces)
Port = 80#Port
HTTPEnabled = 1#HTTP on/off
SSLPort = 443#Port for HTTPS
SSLEnabled = 0#HTTPS on/off
Logging = 1#Should The Server Log stuff?
ErrorLogging = 1#Should Server Log Exceptions(only ones that occur after Server is up).
Working_Directory = "%/root/"# % = execution directory(i.e:- where server root is set,Custom.py will be executed,and where allowed directories * will be set)
MAX_CONT_SIZE = 52428800 #50MB, Max size of post data
MAX_QUE_BACKLOG = 20 #Max number of people in the waiting que at any given point
MAX_SERVE_TIME = 3#Max time for a single request to occur[If needing to serve large files/streaming increase this number]
MAX_BUFFER_WAIT = 1#Time for buffer to clear(Send & Recv)[Increase if streaming video/audio]
SSL_CERT = "server.crt"#Name of ssl certificate(should be in Server_Files/SSL_Cert/)[pem file]
SSL_KEY = "server.key"#Name of ssl key(should be in Server_Files/SSL_Cert/)[pem file]
#Play around with these to fine tune it to your machine & use case
ServiceThreadLimit = 25#Max number of threads to allow server to create(per instance i.e:- http & https) [should be near 15-50,as they run on one core]
Min_Active_ServiceThreads = 1#Minimum active threads(I.E:-dont kill this service thread even if it has no work)[should be near 1-3][Never make it 0]
#Play around with these to fine tune it to your machine & use case
#User Changeable

#GLOBALS

#CHECKS

#Check if SSL enabled & init
if SSLEnabled:
	try:
		import ssl
		SSL_Context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)#Create Context(default settings)
		SSL_Context.load_cert_chain(certfile=Server_file_path+"SSL_Cert/"+SSL_CERT, keyfile=Server_file_path+"SSL_Cert/"+SSL_KEY)#Load up cert and key
	except  Exception, e:
		print e#Print out Error
		print "SSL failed to be initizialed...."
		HouseKeeping.On = 0#Shutdown HouseKeeping
		On = 0;#Shutdown server
		sys.exit("Dead")#State Death
#Check if SSL enabled & init
#CHECKS

#Load Mime List
def Load_Mime():
	#Globals
	global SHB_Mime
	global Server_file_path
	#GLobals
	Mime_File = open(Server_file_path+"mime.typ.shb","r")#Create file pointer to Mime List
	Mime_Holder = (Mime_File.read()).split("\n")#Load List to RAM
	Mime_File.close()#Close mime list
	for SHB_Mime_typ in Mime_Holder:
		tmp = SHB_Mime_typ.split("	")
		SHB_Mime.append([tmp[0],tmp[-1]])
#Load Mime List
Load_Mime()#Load Up mime List to RAM
print "Loaded Mime List..."
#Check Mime List
def Check_Mime(file_name):
	#Globals
	global SHB_Mime
	#Globals
	#Get ext
	file_ext = file_name.split(".")[-1]
	#Get ext
	#check mime
	for Mime_type,exts in SHB_Mime:
		for ext in exts.split(" "):
			if file_ext == ext.strip():
				return Mime_type
	#check mime
	return None #Return None type
#Check Mime List

#Settings
def Settings():
	#globals
	global Server_file_path
	global Settings_file
	global White_List
	global Black_List
	global SSL_Context
	#globals
	f = open(Server_file_path+Settings_file, "a+")
	f.seek(0)
	Settings = f.read().split("\n")
	#Auto Generate file
	if (len(Settings[0]) < 5):
		f.write('*White List\n-enabled:N\n-Adresslist = [\"192.168.0.1\",\"127.0.0.1\"]\n\n')
		f.write('*Black List\n-enabled:N\n-Adresslist = [\"111.111.111.111\",\"0.0.0.0\"]\n\n')
		f.write("*Ciphers\n-enabled:N\nCipherString = ALL:!ADH:!RC4+RSA:+HIGH:+MEDIUM:!LOW:!SSLv2:!EXPORT\n\n#Note CipherString above not recomended it's just an example")
		f.seek(0)
		Settings = f.read().split("\n")
	#Auto Generate file
	f.close()
	for i in range(len(Settings)):
		if ("*White" in Settings[i]):
			i+=1
			if (Settings[i].split(":")[1] == "Y"):
				i+=1
				White_List = json.loads(Settings[i].split("=")[1].strip())
		if ("*Black" in Settings[i]):
			i+=1
			if (Settings[i].split(":")[1] == "Y"):
				i+=1
				Black_List = json.loads(Settings[i].split("=")[1].strip())
		if ("*Ciphers" in Settings[i]):
			i+=1
			if ((Settings[i].split(":")[1] == "Y")and(SSL_Context != None)):
				i+=1
				try:
					SSL_Context.set_ciphers(Settings[i].split("=")[1].strip())#Cipher string
				except Exception, e:
					print e#Print out Error
					print "SSL failed to load cipher string..."
					HouseKeeping.On = 0#Shutdown HouseKeeping
					On = 0;#Shutdown server
					sys.exit("Dead")#State Death
#Settings
Settings()#Load up Settings
print "Loaded Settings(White/Black List)..."
#Set working directory
def Set_working_dir():
	#globals
	global Working_Directory
	global Server_file_path
	#globals
	os.chdir(Server_file_path+"../")
	Working_Directory = Working_Directory.replace("%",os.getcwd())
	os.chdir(Working_Directory)
	Custom.Server_Working_Directory = Working_Directory#Tell custom module where the working dir is
#Set working directory
Set_working_dir()#Set it !
print "Set Working Directory..."
#Get Directories
def Get_Allowed_Directories():
	#Globals
	global Allowed_Directories_File
	global Allowed_Directories
	global Server_file_path
	global Working_Directory
	#Globals
	#get allowed list
	f = open(Server_file_path+Allowed_Directories_File, "a+")
	f.seek(0)
	AllwdDirs = f.read().split("\n")
	#Auto Generate file
	if (len(AllwdDirs[0]) < 5):
		f.write("#To comment use a #\n#Working_Directory = *, eg : - */something\n#All child dirs = @ eg */@ means everything in the working dir is allowed\n*")
		f.seek(0)
		AllwdDirs = f.read().split("\n")
	#Auto Generate file
	f.close()
	#get allowed list
	for Dir in AllwdDirs:
		Dir = Dir.replace(" ","\ ")#Get spaced out of the way
		Dir = Dir.replace("*",Working_Directory[:-1])#Make cwd
		#Ignore comments
		if Dir[:1] != "#":
			Allowed_Directories.append(Dir)
		#Ignore comments
#Get Directories
Get_Allowed_Directories()#Populate !
print "Loaded Allowed Directories..."

#Check Directory
def Check_Directory(File_Path):
	#Globals
	global Allowed_Directories
	#Globals
	#Check directory
	for AllwdDir in Allowed_Directories:
		if ((File_Path == AllwdDir)or(File_Path == AllwdDir[:-1])or(File_Path[:-1] == AllwdDir)):
			return 1#Success
		elif(((AllwdDir[:-1] in File_Path)or(AllwdDir[:-2] in File_Path)) & (AllwdDir[-1] == "@")):
			return 1#Success
	#Check directory
	return 0#Failed
#Check Directory

#Forbidden
def Forbidden(Swear=0,Not_found=0,File_Name=''):
	html  = ""
	Number = ""
	if Not_found:
		html = Custom.Not_Found(File_Name)
		Number = "404 NOT FOUND"
		if (html == ""):
			html = "<html><h1>404 NOT FOUND</h1></html>"
	else:
		Number = "403 Forbidden"
		html = Custom.Forbidden(File_Name)
		if (html == ""):
			html = "<html><h1>403 Forbidden</h1></html>"
			if Swear:
				html = "<html><h1>403 GTFO</h1></html>"
	Message = GF.Construct_Header("","close","text/html",str(len(html)),Number)
	Message += html
	return Message
#Forbidden

#RESPOND
def Respond(Content_Name,Content_Path,Url_parameters,con,Request_Type,RAW_DATA,Payload,Keep_Alive,HTTPS,timeS,timeO):
	#Globals
	global Working_Directory
	global Port
	global Ip
	global BuffSize
	global ErrorLogging
	#Globals
	#Vars
	Cont="" #Define Response Content
	Custom_Headers = ""#Place Holder
	ResponseCode = "200 OK"#Response Default
	#Vars

	#Security Check
	if (Check_Directory(Content_Path) == 0):
		con.send(Forbidden(1,0,Content_Path+Content_Name))#Tell them to GTFO
		return 0#Stop Response
	#Security Check

	#MIME
	Mime = Check_Mime(Content_Name)
	if (Mime == None):
		Mime = "text/plain"#When in doubt its plain text
	#MIME

	#Handle Requests
	if (Request_Type == "GET" or Request_Type =="HEAD"):
		Cont_Size = "0"#Place Holder
		File_Obj = None#Place Holder

		#Check for Custom Handling
		Cont,Mime,Custom_Headers,Cont_File_Path,ResponseCode = Custom.GET(Content_Name,Content_Path,Url_parameters,Mime,RAW_DATA,HTTPS)#Check for Custom input
		#Kill upon failure
		if (Cont == 0):
			return 0
		#Kill upon failure
		#If file path is output
		if ((Cont == "")&(Cont_File_Path!="")):
			Content_Name = ""#Zero out old file
			Content_Path = Cont_File_Path#New file input
		#If file path is output
		#Check for Custom Handling*

		#Deal with Special documents(Only do so if not custom handled).
		if ((Cont == "")&(Cont_File_Path == "")):
			if (os.path.isfile(Content_Path+Content_Name)):
				if (Content_Name[-5:] == ".html"):
					Cont,Mime,tmp_headers,ResponseCode = Custom.Parse(Content_Name,Content_Path,Url_parameters,Mime,RAW_DATA,HTTPS)
					Custom_Headers+=tmp_headers
			else:
				con.send(Forbidden(0,1,Content_Path+Content_Name))#404 Not Found
				return 0#Kill connection
		#Deal with Special documents(Only do so if not custom handled).
		Cont_Size = str(len(Cont))#Set it to data size if not loading a file
		#Get Content(Make sure no custom or special documents).
		if (Cont == ""):
			try:
				#GET Requested bytes
				Requested_Bytes = [0,0]
				for Raw_Header in RAW_DATA:
					if ("Range:" in Raw_Header):
						Requested_Bytes = (Raw_Header.split("bytes=")[1]).split("-")
						#Make sure ending range is not null
						if Requested_Bytes[1].strip() == "":
							Requested_Bytes[1] = 0
						#Make sure ending range is not null
						#Convert to integers
						Requested_Bytes[1] = int(Requested_Bytes[1])
						Requested_Bytes[0]= int(Requested_Bytes[0])
						#Convert to integers
				#GET Requested bytes
				if (os.path.isfile(Content_Path+Content_Name)):
					#Get size of content to be sent
					if (Requested_Bytes[1] == 0):
						Cont_Size = (os.path.getsize(Content_Path+Content_Name) - (Requested_Bytes[0]))
					else:
						Cont_Size =(Requested_Bytes[1] - Requested_Bytes[0])
					#Get size of content to be sent
					File_Obj = open(Content_Path+Content_Name, "rb")
					File_Obj.seek(Requested_Bytes[0])
				else:
					con.send(Forbidden(0,1,Content_Path+Content_Name))#404 Not Found
					return 0#Kill connection
			except Exception, e:
				#Log errors
				if ErrorLogging:
					HouseKeeping.ELog_Out.append(str(e)+" :exception at 1\n\n")
				#Log errors
				File_Obj.close()
				con.send(Forbidden(0,1,Content_Path+Content_Name))#404 Not Found
				return 0#Kill connection
		#Get Content(Make sure no custom or special documents).
		#Create Response
		if (File_Obj != None):
			Entire_File_size = os.path.getsize(Content_Path+Content_Name)
			Custom_Headers += "Content-Range:bytes "+str(File_Obj.tell())+"-"+str(Entire_File_size-1)+"/"+str(Entire_File_size)+"\n"#Add Content-Range:bytes to Headers
			Custom_Headers +="Keep-Alive: timeout=0.5, max=100\n"#Tell the client if they do not accept data with it 5 secs it will cut the connection!
			if (File_Obj.tell() != 0):
				con.send(GF.Construct_Header(Custom_Headers,Keep_Alive,Mime,str(Cont_Size),"206 Partial Content"))
			else:
				con.send(GF.Construct_Header(Custom_Headers,Keep_Alive,Mime,str(Cont_Size),ResponseCode))
		else:
			con.send(GF.Construct_Header(Custom_Headers,Keep_Alive,Mime,str(Cont_Size),ResponseCode))
		#Create Response*
		#Send
		if not(Request_Type == "HEAD"):
			try:
				Cont_Count = 0#Count
				while (Cont_Count < Cont_Size):
					if ((time.time()-timeS)>timeO): raise Exception("Serve Timed Out")#@TimeOut
					if (File_Obj == None):
						con.send(Cont)
						Cont_Count += len(Cont)
					else:
						con.send(File_Obj.read(BuffSize))
						Cont_Count+=BuffSize
			except Exception,i:
				#Log errors
				if ErrorLogging:
					HouseKeeping.ELog_Out.append(str(i)+" :exception at 2\n\n")
				#Log errors
		#Send
		#Close any file
		if not(File_Obj == None):
			File_Obj.close()#Close File's Being Accessed!
		#Close any file
		#Terminate
		return 0#Return
		#Terminate
	elif (Request_Type == "POST"):
		#Globals Post only
		global MAX_CONT_SIZE
		global Server_file_path
		#Globals Post ony

		#Place holders
		POST_DATA = ""#Place holder
		POST_File_Name = ""#Place holder
		POST_File_Handling = 0#Place holder
		Incomplete_Post = 0#Place holder
		Content_Len = 1024#Place holder
		File_Boundry = None#Place holder
		File_Obj = None#Place holder
		NeedToRecv = 0#PlaceHolder
		#Place holders
		#Get content Length & File Boundry
		#Check for data in headers
		for POST_Header in RAW_DATA:
			if ("Content-Length".lower() in POST_Header.lower()):
				Content_Len = int(POST_Header.split(":")[1])
			#Get File Boundry
			if ("boundary=" in POST_Header):
				File_Boundry = (POST_Header.split("=")[1])
				if ("\r" in File_Boundry):
					File_Boundry = File_Boundry.split("\r")[0]
			#Get File Boundry
		#Check for data in headers
		#Get content Length & File Boundry
		#Check if post data is latched on to Header
		if (Payload != None):
			#Check for data in post specific headers
			for POST_Header in Payload.split('\n'):
				#Get File Name
				if ("Content-Disposition:" in POST_Header):
					POST_File_Name = (POST_Header.split('="')[-1])[:-2]
				#Get File Name
			#Check for data in post specific headers
			#Sort out payload (File post etc)
			if (POST_File_Name !=  ""):
				#Remove Post Headers
				POST_DATA = Payload.split("\r\n\r\n")[2]
				#Remove Post Headers
			else:
				#No Post Headers
				POST_DATA = Payload
				#No Post Headers
			#Sort out payload (File post etc)
			if (len(Payload)<Content_Len):
				NeedToRecv = 1
			elif (File_Boundry != None):
				#Remove Footer
				POST_DATA = POST_DATA.replace(("--"+File_Boundry+"--"),"")#Remove footer if whole file
				#Remove Footer
		else:
			NeedToRecv = 1
		#Get post Data
		if NeedToRecv:
			#Check Perform Content Length Checks
			#Max Size Check
			if (Content_Len > MAX_CONT_SIZE):
				con.send(Forbidden())#File too large!
				return 0#Stop Response!
			#Max Size Check
			#File handling for large files(>100KB) Check
			if (Content_Len > 102400):
				POST_File_Handling = 1
				File_Obj = open(Server_file_path+"Temp/"+(str(uuid.uuid4()).replace("-",""))+".tmp","wb+")
			#File handling for large files Check
			#Check Perform Content Length Checks
			#Get content
			#If Boundry Present Get data till boundry
			if (File_Boundry != None):
				Boundry = 1
				Recieved = len(POST_DATA)
				while Boundry:
					#Prevent Crash upon file failure
					try:
						if ((time.time()-timeS)>timeO): raise Exception("Serve Timed Out")#@TimeOut
						POST_DATA += con.recv(BuffSize)#Get post until boundry is there!
						Recieved +=BuffSize
						#Make sure not null
						if (POST_DATA[-1] == None):
							raise Exception("Recieved Null on post")
						#Make sure not null
					except Exception, e:
						#Log errors
						if ErrorLogging:
							HouseKeeping.ELog_Out.append(str(e)+" :exception at 3\n\n")
						#Log errors
						Incomplete_Post = 1#Stop processing request
						break#Leave loop file not Recieved
					#Prevent Crash upon file failure
					#Check For Post data Headers
					if (Recieved == BuffSize):
						#Extract File name
						Post_Headers = POST_DATA.split("\n")
						for PHeader in Post_Headers:
							if ("Content-Disposition:" in PHeader):
								POST_File_Name = (PHeader.split('="')[-1])[:-2]
						#Extract File name
						#Remove Post Headers
						POST_DATA = POST_DATA.split("\r\n\r\n")[2]
						#Remove Post Headers
					#Check For Post data Headers
					#Make sure file sent is not larger than stated
					if ((Recieved-Content_Len)>BuffSize):
						Incomplete_Post = 1#Stop processing request
						break#Leave loop file not Recieved
					#Make sure file sent is not larger than stated
					#Check for Boundry
					if (File_Boundry in POST_DATA[-(len(File_Boundry)+10):]):
						Boundry = 0
						#Remove Footer
						POST_DATA = POST_DATA.replace(("--"+File_Boundry+"--"),"")#Remove footer if whole file
						#Remove Footer
					#Check for Boundry

					#File Handle if required
					if POST_File_Handling:
						File_Obj.write(POST_DATA)#Write to file
						POST_DATA = ""#Dump data from memory
					#File Handle if required
			#If Boundry Present Get data till boundry
			#If not Just get the Data
			else:
				Data_Recieved = 0
				while (Data_Recieved<Content_Len):
					#Prevent Crash upon file failure
					try:
						if ((time.time()-timeS)>timeO): raise Exception("Serve Timed Out")#@TimeOut
						POST_DATA += con.recv(BuffSize)#Get post!
						#Make Sure not Null
						if (POST_DATA[-1] == None):
							raise Exception
						#Make Sure not Null
					except Exception, e:
						#Log errors
						if ErrorLogging:
							HouseKeeping.ELog_Out.append(str(e)+" :exception at 4\n\n")
						#Log errors
						Incomplete_Post = 1#Stop processing request
						break#Leave loop file not Recieved
					#Prevent Crash upon file failure
					Data_Recieved+=BuffSize
					#File Handle if required
					if POST_File_Handling:
						File_Obj.write(POST_DATA)#Write to file
						POST_DATA = ""#Dump data from memory
					#File Handle if required
			#If not Just get the Data
			#Set POST_DATA to File Object!
			if POST_File_Handling:
				File_Obj.seek(0)
				POST_DATA = File_Obj
			#Set POST_DATA to File Object!
			#Get content
		#Get post Data

		#Check for Incomplete_Post
		if Incomplete_Post:
			#Delete file if it is a file
			if (POST_File_Handling):
				Name = POST_DATA.name#Get name
				POST_DATA.close()#Close the File
				os.remove(Name)#Delete file from disk
			#Delete file if it is a file
			return 0#Stop Response
		#Check for Incomplete_Post

		#Check for Custom Handling
		Cont,Mime,Custom_Headers,Cont_File_Path,ResponseCode = Custom.POST(Content_Name,Content_Path,Url_parameters,Mime,POST_DATA,RAW_DATA,POST_File_Name,HTTPS)#Check for Custom input
		#Check for Custom Handling*

		#Deal with Special documents(Only do so if not custom handled).
		if ((Cont == "")&(Cont_File_Path == "")):
			if (os.path.isfile(Content_Path+Content_Name)):
				if (Content_Name[-5:] == ".html"):
					Cont,Mime,tmp_headers,ResponseCode = Custom.Parse(Content_Name,Content_Path,Url_parameters,Mime,RAW_DATA,HTTPS,POST_DATA,POST_File_Handling,POST_File_Name)
					Custom_Headers+=tmp_headers
			else:
				con.send(Forbidden(0,1,Content_Path+Content_Name))#404 Not Found
				Cont = 0#Report Failure
		#Deal with Special documents(Only do so if not custom handled).
	

		#Close POST_DATA and delete file if it is one
		try:
			if (POST_File_Handling):
				Name = POST_DATA.name#Get name
				POST_DATA.close()#Close the File
				os.remove(Name)#Delete file from disk
		except:
			pass#File may have been deleted by Custom function
		#Close POST_DATA and delete file if it is one

		#Kill upon failure
		if (Cont == 0):
			return 0
		#Kill upon failure

		#Deal with response $
		if ((Cont == "")&(Cont_File_Path!="")):
			#Special case where output is a file
			Cont_Size = os.path.getsize(Cont_File_Path)#Get output size
			con.send(GF.Construct_Header(Custom_Headers,Keep_Alive,Mime,str(Cont_Size),ResponseCode))#Send Header
			Out_Obj = open(Cont_File_Path, "rb")
			try:
				Cont_Count = 0#Count
				while (Cont_Count < Cont_Size):
					if ((time.time()-timeS)>timeO): raise Exception("Serve Timed Out")#@TimeOut
					con.send(Out_Obj.read(BuffSize))
					Cont_Count+=BuffSize
			except Exception, e:
				#Log errors
				if ErrorLogging:
					HouseKeeping.ELog_Out.append(str(e)+" :exception at 5\n\n")
				#Log errors
			Out_Obj.close()#Close output object
			#Special case where output is a file
		else:
			#Create & Send Response
			con.send(GF.Construct_Header(Custom_Headers,Keep_Alive,Mime,str(len(Cont)),ResponseCode)+Cont)#Send Response
			#Create & Send Response*
		#Deal with response

		#Terminate
		return 0
		#Terminate
	return 0#just in case
	#Handle Requests	
#RESPOND

#Log Ip addresses and Analyse args
def Analyse_Request(con,addr,HTTPS,timeS,timeO):
	#Globals
	global Logging
	global Server_file_path
	global Working_Directory
	global Default
	global On
	global ErrorLogging
	global BuffSize
	#Globals
	#Recieve Request
	Data = ""#Place Holder
	Payload = ""#Place Holder
	try:
		while On:
			tmp = con.recv(BuffSize)
			if ((time.time()-timeS)>timeO): return 3#@TimeOut
			if not tmp: break#Stop if invalid data detected
			Data += tmp
			if ("\r\n\r\n" in Data):break#Stop if End of HTTP detected
	except Exception, e:
		#Log errors
		if ErrorLogging:
			HouseKeeping.ELog_Out.append(str(e)+" :exception at 6\n\n")
		#Log errors
		return 0#Stop Response
	#Get Data and remove payload that came with data
	Data = Data.split("\r\n\r\n")
	for i in range(len(Data)):
		if (i != 0):
			Payload += Data[i]+"\r\n\r\n"
	Data = Data[0].split('\n')#Get Data
	#Get Data and remove payload that came with data
	#Chrome sends blank request fro some reason
	if (Data == ['']):
		return 0
	#Chrome sends blank request fro some reason
	#Recieve Request
	#Process Data
	try:
		Main_header = Data[0].split(" ")#Obtain the main header
		Request_Type = ""#Place Holder
		File_Name = ""#Place Holder
		Url_parameters = ""#Place Holder

		#Check for valid header and extract information
		#Take main Header info
		if (len(Main_header)> 1):
			Request_Type = Main_header[0]
			File_Name = urllib.unquote(Main_header[1][1:]).decode('utf8')#Normalize string
		#Take main Header info

		#Url Handling
		if ("?" in File_Name):
			tmp_Contttt = File_Name.split("?")
			Url_parameters = tmp_Contttt[1]#Get Url Parameters
			File_Name = tmp_Contttt[0]#Remove ? marks
		#Url Handling
		#Content Path & Name
		Content_Path = (File_Name[:-len(File_Name.split("/")[-1])-1])
		if (Content_Path[:1] != "/"):
			#Make sure not to go //
			if ((len(Content_Path) > 2)):
				Content_Path = Working_Directory+Content_Path+"/"
			else:
				Content_Path = Working_Directory+"/"
			#Make sure not to go //
		Content_Name = File_Name.split("/")[-1]
		#Content Path & Name
		#Make Sure / at end of content path
		if (Content_Path[-1]!="/"):
			Content_Path+="/"
		#Make Sure / at end of content path
		#If no file is requested set Default
		if (Content_Name == "" or Content_Name[-1] == "/"):
			if os.path.isfile(Content_Path+Default[0]):
				Content_Name = Content_Name + Default[0]
			elif os.path.isfile(Content_Path+Default[1]):
				Content_Name = Content_Name + Default[1]
			else:
				#Security Check as to not help identify files on the system
				if (Check_Directory(Content_Path) == 0):
					con.send(Forbidden(1,0,Content_Path+Content_Name))#Tell them to GTFO
					return 0#Stop Response
				#Security Check as to not help identify files on the system
				#Normal Respone if Security clears
				else:
					con.send(Forbidden(0,1,Content_Path+Content_Name))#Tell them the file is not found
					return 0#Stop Response
				#Normal Respone if Security clears
		#If no file is requested set Default
		#Check for valid header and extract information

		#Log Stuff
		if Logging:
			#Create Log Entry
			Log_Entry = "IP:"+addr+"	|Request Type:"+Request_Type+"	|Requested Content:"+File_Name+"	|"
			Log_Entry+= "Passed Parameters:"+Url_parameters+"	|"
			Log_Entry+= "Date:"+datetime.datetime.now().strftime('%D')+"	|"
			Log_Entry+="Time:"+datetime.datetime.now().strftime('%H:%M')+"\n\n"
			#Create Log Entry
			HouseKeeping.Log_Out.append(Log_Entry)#Add to Logging que
		#Log Stuff
		return Respond(Content_Name,Content_Path,Url_parameters,con,Request_Type,Data,Payload,"close",HTTPS,timeS,timeO)#Send Response Connection-close/Keep-Alive
	except Exception, e:
		#Log errors
		if ErrorLogging:
			HouseKeeping.ELog_Out.append(str(e)+" :exception at 7\n\n")
		#Log errors
	#Process Data
	return 0#Failure ?
#Log Ip addresses and Analyse args*


#Manage Requests
QuedRequests = []#Requests waiting to be handled
Active_ServiceThreads = []#Number of active threads
def Threaded_Service(My_ID,Serve_Time,Sock_TimeOut,SSL_Context):
	#Globals
	global Min_Active_ServiceThreads
	global TLock
	global Active_ServiceThreads
	global QuedRequests
	global On
	#Globals
	Running = 1#Set loop to on
	while Running:
		#Make sure service dies with server
		if (On == 0):
			break
		#Make sure service dies with server
		try:
			TLock.acquire()#Lock threading :#
			if (QuedRequests):
				my_job = QuedRequests.pop(0)#Grab item from que
				TLock.release()#Release threading :O
				#DOS check
				if my_job[1] in HouseKeeping.Blocked_Candidates:
					my_job[0].close()#Connection killed
					continue#Quick next loop!
				#DOS check
				#If Https
				if my_job[2]:
					my_job[0] = SSL_Context.wrap_socket(my_job[0], server_side=True)#HTTPSify the connection
				#If Https
				my_job[0].settimeout(Sock_TimeOut)#Make sure not to waste resources waiting for data(Send&Recv).
				Analyse_Request(my_job[0],my_job[1],my_job[2],time.time(),Serve_Time)
				HouseKeeping.Remove_Address(my_job[1])#Remove from concurrency list
			#check if i may kill my self
			elif (len(Active_ServiceThreads) > Min_Active_ServiceThreads):
				TLock.release()#Release threading :O
				time.sleep(0.020)#wait make sure no new requests(20ms) are coming in
				TLock.acquire()#Lock threading :#
				if ((len(Active_ServiceThreads) > Min_Active_ServiceThreads) & (not QuedRequests)):
					Active_ServiceThreads.remove(My_ID)#DeActivate Me
					TLock.release()#Release threading :O
					Running = 0#Stop Service
					break#Leave loop
				TLock.release()#Release threading :O
			#check if i may kill my self
			#Idle
			else:
				TLock.release()
				time.sleep(0.05)#IDLE for 50ms so as to not use up cpu
			#Idle
		except Exception, e:
			print str(e)
			#Release locked up thread
			if TLock.locked():
				TLock.release()#Release threading :O
			#Release locked up thread
			#Log errors
			if ErrorLogging:
				HouseKeeping.ELog_Out.append(str(e)+" :exception at 9\n\n")
			#Log errors
	return 0#Finished Service
#Manage Requests

#Create Service Threads
def Create_Service_Thread():
	global MAX_SERVE_TIME
	global MAX_BUFFER_WAIT
	global SSL_Context
	global Active_ServiceThreads
	ID = str(uuid.uuid4())[:6]
	if not(ID in Active_ServiceThreads):
		Active_ServiceThreads.append(ID)
		Thread(target=Threaded_Service, args=(ID,MAX_SERVE_TIME,MAX_BUFFER_WAIT,SSL_Context)).start()
		return ID
	else:
		return Create_Service_Thread()
#Create Service Threads

#MAIN
try:
	#Serve
	def Serv_HTTP(HTTPS):
		#Globals
		#Service Threads
		global ServiceThreadLimit
		global Min_Active_ServiceThreads
		global QuedRequests
		global Active_ServiceThreads
		global MAX_QUE_BACKLOG
		global SNTBLN
		#Service Threads
		#Logging
		global ErrorLogging
		global TLock
		#Logging
		#Base
		global On
		global SSLPort
		global Socket_Backlog
		global Ip
		global Port
		#Base
		#Globals
		#INIT
		#Base
		Sock = socket.socket()#Define Sock.
		try:
			Sock.settimeout(None)#Just a precaution
			if HTTPS:
				#Change LOG file names
				HouseKeeping.ErrorLogFile+="S"
				HouseKeeping.LogFile+="S"
				HouseKeeping.DOSFile+="S"
				#Change LOG file names
				#Configure socket
				Sock.bind((Ip,SSLPort))#Bind to SSL port
				Sock.listen(Socket_Backlog)#Start listening
				#Configure socket
				print("HTTPS Server Active!")
			else:
				#Configure socket
				Sock.bind((Ip,Port))#Bind socket to port
				Sock.listen(Socket_Backlog)#Start listening
				#Configure socket
				print("HTTP Server Active!")
		except Exception, err:
			print err
			On = 0#Shutdown any Loops on HTTPS server
			HouseKeeping.On = 0#Shutdown HouseKeeping
			sys.exit("Dead")#State Death
		#Base
		HouseKeeping.TLock = TLock#Share Thread Lock
		HouseKeeping.Init()#Begin HouseKeeping service
		#Create Min Services
		for i in range(Min_Active_ServiceThreads):
			Create_Service_Thread()
		#Create Min Services
		#INIT
		#Main Loop
		while On:
			try:
				# wait for next client to connect
				connection, address = Sock.accept() # connection is a new socket

				#Check DOS List
				if (address[0] in HouseKeeping.Blocked_Candidates):
					connection.close()#Do not waste any more resources on the DOSer
					continue#skip to the next connection.
				#Check DOS List

				#Check White_List
				if White_List != None:
					if not(address[0] in White_List):
						connection.send(Forbidden())#Tell them their not allowed
						connection.close()
						continue#skip to the next connection.
				#Check White_List

				#Check Black_List
				if Black_List != None:
					if (address[0] in Black_List):
						connection.send(Forbidden())#Tell them their not allowed
						connection.close()
						continue#skip to the next connection.
				#Check Black_List

				#Accept Connection
				if (len(QuedRequests) < MAX_QUE_BACKLOG):
					QuedRequests.append([connection,address[0],HTTPS])
					#Add to Candidate list for dos
					HouseKeeping.Add_Address(address[0])
					#Add to Candidate list for dos
				else:
					connection.close()#No space
				#Accept Connection

				#Check if Server Needs New Service Thread
				if ((len(QuedRequests) > SNTBLN)&(len(Active_ServiceThreads)<ServiceThreadLimit)):
					Create_Service_Thread()
				#Check if Server Needs New Service Thread
			except Exception, err:
				#Log errors
				if ErrorLogging:
					HouseKeeping.ELog_Out.append(str(err)+" :exception at 10\n\n")
				#Log errors
				continue#skip to the next connection.
		Sock.close()#Kill the socket
		#Main Loop
	#Serve
	#Start Serving
	print ""#Move to next line
	if HTTPEnabled:
		#HTTPS
		if SSLEnabled:
			#start HTTPS on seprate Process (Creates new instance of all variables)
			HTTPSProc = Process(target=Serv_HTTP, args=(1,))
			HTTPSProc.start()
			#start HTTPS on seprate Process (Creates new instance of all variables)
		#HTTPS
		#HTTP
		Serv_HTTP(0)
		#HTTP
	elif SSLEnabled:
		#HTTPS
		Serv_HTTP(1)
		#HTTPS
	#Start Serving
except :
	HouseKeeping.On = 0#Shutdown HouseKeeping
	On = 0#Shutdown any Loops on core server
	#SSL
	if HTTPSProc:
		HTTPSProc.terminate()#Terminate https process
	#SSL
	#Release locked up thread
	if TLock.locked():
		TLock.release()#Release threading :O
	#Release locked up thread
	sys.exit("Dead")#State Death
#MAIN
#Shut Down(Ensurance)
HouseKeeping.On = 0#Shutdown HouseKeeping
On = 0#Shutdown any Loops on core server
#SSL
if HTTPSProc:
	HTTPSProc.terminate()#Terminate https process
#SSL
sys.exit("Dead")#State Death
#Shut Down(Ensurance)