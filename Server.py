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
import DOS_Protect#My protection Script !(Takes care of logging as well)
import select#Check if socket is ready :3
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
Default = ["index.html","index.php"] #Default file to load.
Settings_file = "Settings.dat"#Load Settings.
Allowed_Directories_File = "Allowed_Dirs.dat"#Load Allowed Directories Dat.
Socket_Backlog = 5#MAX number of clients waiting to be accepted(in que).
#Should not be messed with!(you can change them,but I don't advise it)

#User Changeable
Ip=""#IP(if left blank will bind to all available interfaces)
Port = 80#Port
HTTPEnabled = 1#HTTP on/off
SSLPort = 443#Port for HTTPS
SSLEnabled = 0#HTTPS on/off
PHPEnabled = 0#PHP on/off
Logging = 0#Should The Server Log stuff?
ErrorLogging = 1#Should Server Log Exceptions(only ones that occur after Server is up).
Working_Directory = "%/root/"# % = execution directory(i.e:- where server root is set,Custom.py & PHP will be executed,and where allowed directories * will be set)
MAX_CONT_SIZE = 52428800 #50MB, Max size of post data
MAX_WAIT_TIME_Request = 3 #Max time(in seconds) for HTTP request to come through
MAX_WAIT_TIME_Data = 3#Max Wait time(in seconds) for additional data from request(per chunk)
MAX_SEND_TIME_DATA = 5#Max time(in seconds) for data to be sent out of the buffer
BuffSize = 1024#Size of buffer for short transfers
LargeBuffSize = 4096#Size of buffer for Files being served via service & HTTP request receival 
SSL_CERT = "server.crt"#Name of ssl certificate(should be in Server_Files/SSL_Cert/)
SSL_KEY = "server.key"#Name of ssl key(should be in Server_Files/SSL_Cert/)
#Play around with these to fine tune it to your machine & use case
NumberOfServicesPerThread = 12#number of connections on one thread [should be around 8 - 15]
ServiceThreadLimit = 18#Max number of threads to allow server to create(per instance i.e:- http & https) [should be near 15-50,as they run on one core]
Min_Active_ServiceThreads = 1#Minimum active threads(I.E:-dont kill this service thread even if it has no work)[should be near 0-3]
#Play around with these to fine tune it to your machine & use case
#User Changeable

#GLOBALS

#CHECKS
#Check if PHP enabled & init
if (PHPEnabled):
	import PHPI#PHP MODULE
	if (PHPI.Error):
		print(PHPI.EMSG)#check for errors
else:
	print "PHP initizialed..."
#Check if PHP enabled & init

#Check if SSL enabled & init
if SSLEnabled:
	try:
		import ssl
		SSL_Context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)#Create Context(default settings)
		SSL_Context.load_cert_chain(certfile=Server_file_path+"SSL_Cert/"+SSL_CERT, keyfile=Server_file_path+"SSL_Cert/"+SSL_KEY)#Load up cert and key
	except  Exception, e:
		print e#Print out Error
		print "SSL failed to be initizialed...."
		DOS_Protect.On = 0#Shutdown DOS protection
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
					DOS_Protect.On = 0#Shutdown DOS protection
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
		elif(((AllwdDir[:-1] in File_Path)or(AllwdDir[:-2] in File_Path)) & (AllwdDir[-1:] == "@")):
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
def Respond(Content_Name,Content_Path,Url_parameters,con,Request_Type,RAW_DATA,Keep_Alive,HTTPS):
	#Globals
	global PHPEnabled
	global PHP_CGI_PATH
	global MAX_WAIT_TIME_Data
	global MAX_SEND_TIME_DATA
	global Working_Directory
	global Port
	global Ip
	global BuffSize
	global ErrorLogging
	#Globals
	#Vars
	Cont="" #Define Response Content
	Custom_Headers = ""#Place Holder
	#Vars

	#Security Check
	if (Check_Directory(Content_Path) == 0):
		con.send(Forbidden(1,0,Content_Path+Content_Name))#Tell them to GTFO
		return 0#Stop Response
	#Security Check

	#MIME
	Mime = Check_Mime(Content_Name)
	if (Mime == None):
		Mime = "text/plain"
		if "html" in Content_Name:
			Mime = "text/html"
	#MIME

	#Handle Requests
	if (Request_Type == "GET" or Request_Type =="HEAD"):
		Cont_Size = "0"#Place Holder
		File_Obj = None#Place Holder

		#Check for Custom Handling
		Cont,Mime,Custom_Headers,Cont_File_Path = Custom.GET(Content_Name,Content_Path,Url_parameters,Mime,RAW_DATA,HTTPS)#Check for Custom input
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
				if ((Content_Name[-4:] == ".php")&PHPEnabled):
					tmp_headers,Cont = PHPI.GET_PHP(Content_Name,Content_Path,RAW_DATA,Url_parameters,Port,Ip,Working_Directory,HTTPS)
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
					DOS_Protect.ELog_Out.append(str(e)+" :exception at 1\n\n")
				#Log errors
				File_Obj.close()
				con.send(Forbidden(0,1,Content_Path+Content_Name))#404 Not Found
				return 0#Kill connection
		#Get Content(Make sure no custom or special documents).
		#Create Response
		if (File_Obj != None):
			Entire_File_size = os.path.getsize(Content_Path+Content_Name)
			Custom_Headers += "Content-Range:bytes "+str(File_Obj.tell())+"-"+str(Entire_File_size-1)+"/"+str(Entire_File_size)+"\n"#Add Content-Range:bytes to Headers
			Custom_Headers +="Keep-Alive: timeout=5, max=100\n"#Tell the client if they do not accept data with it 5 secs it will cut the connection!
			if (File_Obj.tell() != 0):
				con.send(GF.Construct_Header(Custom_Headers,Keep_Alive,Mime,str(Cont_Size),"206 Partial Content"))
			else:
				con.send(GF.Construct_Header(Custom_Headers,Keep_Alive,Mime,str(Cont_Size)))
		else:
			con.send(GF.Construct_Header(Custom_Headers,Keep_Alive,Mime,str(Cont_Size)))
		#Create Response*
		#Send
		if not(Request_Type == "HEAD"):
			try:
				con.settimeout(MAX_SEND_TIME_DATA)#time out on data send
				#If file is greater than 10Kb return FileObj
				if (Cont_Size > 10240)&(File_Obj != None):
					return File_Obj,Cont_Size # this is for thread pooling stuffs
				#If file is greater than 10Kb return FileObj
				Cont_Count = 0#Count
				while (Cont_Count < Cont_Size):
					if (File_Obj == None):
						con.send(Cont)
						Cont_Count += len(Cont)
					else:
						con.send(File_Obj.read(BuffSize))
						Cont_Count+=BuffSize
			except Exception,i:
				#Log errors
				if ErrorLogging:
					DOS_Protect.ELog_Out.append(str(i)+" :exception at 2\n\n")
				#Log errors
		#Send
		#Close any file
		if not(File_Obj == None):
			File_Obj.close()#Close File's Being Accessed!
		#Close any file
		#Terminate
		return 0#Return Success!
		#Terminate
	elif (Request_Type == "POST"):
		#Globals Post only
		global MAX_CONT_SIZE
		global Server_file_path
		#Globals Post ony

		#Make sure server does not get stuck waiting for data
		con.settimeout(MAX_WAIT_TIME_Data)
		#Make sure server does not get stuck waiting for data

		#Get post Data
		#Place holders
		POST_DATA = ""#Place holder
		POST_File_Name = ""#Place holder
		POST_File_Handling = 0#Var
		Incomplete_Post = 0#Var
		#Place holders
		#Check if post data is latched on to Header
		if not(len(RAW_DATA[-1]) < 3):
			POST_DATA = RAW_DATA[-1]#Get POST DATA
			#print RAW_DATA
			#print POST_DATA
		else:
			File_Boundry = None#Place holder
			File_Obj = None#Place holder

			#Get content Length
			Content_Len = 1024
			for POST_Header in RAW_DATA:
				if ("Content-Length".lower() in POST_Header.lower()):
					Content_Len = int(POST_Header.split(":")[1])
				#Get File Boundry
				if ("boundary=" in POST_Header):
					File_Boundry = (POST_Header.split("=")[1])
					if ("\r" in File_Boundry):
						File_Boundry = File_Boundry.split("\r")[0]
				#Get File Boundry
			#Get content Length

			#Check Perform Content Length Checks
			#Max Size Check
			if (Content_Len > MAX_CONT_SIZE):
				con.send(Forbidden())#File too large!
				return 0#Stop Response!
			#Max Size Check
			#File handling for large files(>100KB) Check
			if (Content_Len > 102400):
				POST_File_Handling = 1
				File_Obj = open(Server_file_path+"Temp/"+(str(uuid.uuid4()).replace("-",""))+".tmp","w+")
			#File handling for large files Check
			#Check Perform Content Length Checks
			#Get content
			#If Boundry Present Get data till boundry
			if (File_Boundry != None):
				Boundry = 1
				Recieved = 0
				while Boundry:
					#Prevent Crash upon file failure
					try:
						POST_DATA += con.recv(BuffSize)#Get post until boundry is there!
						Recieved +=BuffSize
						#Make sure not null
						if (POST_DATA[-1] == None):
							raise Exception
						#Make sure not null
					except Exception, e:
						#Log errors
						if ErrorLogging:
							DOS_Protect.ELog_Out.append(str(e)+" :exception at 3\n\n")
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
						POST_DATA = POST_DATA[:-(len(POST_DATA.split("\n")[-2])+1)]
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
						POST_DATA += con.recv(BuffSize)#Get post!
						#Make Sure not Null
						if (POST_DATA[-1] == None):
							raise Exception
						#Make Sure not Null
					except Exception, e:
						#Log errors
						if ErrorLogging:
							DOS_Protect.ELog_Out.append(str(e)+" :exception at 4\n\n")
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

		#Print out details
		#print POST_File_Name
		#if not(POST_File_Handling):
		#print POST_DATA
		#	print "Recieved Post:"+str(len(POST_DATA))#Remove Later
		#else:
		#	POST_DATA.seek(0, os.SEEK_END)
		#	print "Recieved Post:"+str(POST_DATA.tell())#Remove Later
		#	POST_DATA.seek(0)
		#Print out details

		#Check for Custom Handling
		Cont,Mime,Custom_Headers,Cont_File_Path = Custom.POST(Content_Name,Content_Path,Url_parameters,Mime,POST_DATA,RAW_DATA,POST_File_Name,HTTPS)#Check for Custom input
		#Check for Custom Handling*

		#Deal with Special documents(Only do so if not custom handled).
		if ((Cont == "")&(Cont_File_Path == "")):
			if (os.path.isfile(Content_Path+Content_Name)):
				if ((Content_Name[-4:] == ".php")&PHPEnabled):
					tmp_headers,Cont=PHPI.POST_PHP(RAW_DATA,Url_parameters,Content_Name,Port,Ip,Content_Path,Working_Directory,POST_File_Handling,POST_DATA,POST_File_Name,HTTPS)
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
			pass#File may have been deleted by Custom function or PHP
		#Close POST_DATA and delete file if it is one

		#Kill upon failure
		if (Cont == 0):
			return 0
		#Kill upon failure

		#Deal with response
		con.settimeout(MAX_SEND_TIME_DATA)#time out on data send
		if ((Cont == "")&(Cont_File_Path!="")):
			#Special case where output is a file
			Cont_Size = os.path.getsize(Cont_File_Path)#Get output size
			con.send(GF.Construct_Header(Custom_Headers,Keep_Alive,Mime,str(Cont_Size)))#Send Header
			Out_Obj = open(Cont_File_Path, "rb")
			try:
				#If file is greater than 10Kb return FileObj
				if (Cont_Size > 10240):
					return Out_Obj,Cont_Size # this is for thread pooling stuffs
				#If file is greater than 10Kb return FileObj
				Cont_Count = 0#Count
				while (Cont_Count < Cont_Size):
					con.send(Out_Obj.read(BuffSize))
					Cont_Count+=BuffSize
			except Exception, e:
				#Log errors
				if ErrorLogging:
					DOS_Protect.ELog_Out.append(str(e)+" :exception at 5\n\n")
				#Log errors
			Out_Obj.close()#Close output object
			#Special case where output is a file
		else:
			#Create & Send Response
			con.send(GF.Construct_Header(Custom_Headers,Keep_Alive,Mime,str(len(Cont)))+Cont)#Send Response
			#Create & Send Response*
		#Deal with response

		#Terminate
		return 0
		#Terminate
	return 0#just in case
	#Handle Requests	
#RESPOND

#Log Ip addresses and Analyse args
def Analyse_Request(con,addr,HTTPS):
	#Globals
	global Logging
	global Server_file_path
	global MAX_WAIT_TIME_Request
	global Working_Directory
	global Default
	global On
	global ErrorLogging
	#Globals

	#Recieve Request
	Data = ""#Place Holder
	con.settimeout(MAX_WAIT_TIME_Request)#Make sure not to waste resources waiting for connection for too long.
	try:
		while On:
			tmp = con.recv(LargeBuffSize)
			if not tmp: break#Stop if invalid data detected
			Data += tmp
			if ("\r\n\r\n" in Data):break#Stop if End of HTTP detected
	except Exception, e:
		#Log errors
		if ErrorLogging:
			DOS_Protect.ELog_Out.append(str(e)+" :exception at 6\n\n")
		#Log errors
		return 0#Stop Response
	Data = Data.split("\n")#Get Data
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
			File_Name = Main_header[1][1:]
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
		#Normalize
		Content_Name = urllib.unquote(Content_Name).decode('utf8')#Normalize string
		Content_Path = urllib.unquote(Content_Path).decode('utf8')#Normalize string
		#Normalize
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
			Log_Entry = "IP:"+addr+"	|Request Type:"+Request_Type+"	|Requested Content:"+File_Name+"	|HTTPS:"+str(HTTPS)+"	|"
			Log_Entry+= "Passed Parameters:"+Url_parameters+"	|"
			Log_Entry+= "Date:"+str(datetime.datetime.utcnow().day)+"/"+str(datetime.datetime.utcnow().month)+"/"+str(datetime.datetime.utcnow().year)+"	|"
			Log_Entry+="Time:"+str(datetime.datetime.utcnow().hour)+":"+str(datetime.datetime.utcnow().minute)+"\n\n"
			#Create Log Entry
			DOS_Protect.Log_Out.append(Log_Entry)#Add to Logging que
		#Log Stuff
		return Respond(Content_Name,Content_Path,Url_parameters,con,Request_Type,Data,"close",HTTPS)#Send Response Connection-close/Keep-Alive
	except Exception, e:
		#Log errors
		if ErrorLogging:
			DOS_Protect.ELog_Out.append(str(e)+" :exception at 7\n\n")
		#Log errors
	#Process Data
	return 0#Failure ?
#Log Ip addresses and Analyse args*


#Manage Requests
Active_Requests={}#List of active threads assigned to a threaded service.
Active_ServiceThreads = []#Number of active threads
def Threaded_Service(My_ID,time_out):
	#Globals
	global Min_Active_ServiceThreads
	global TLock
	global Active_ServiceThreads
	global Active_Requests
	global On
	global LargeBuffSize
	#Globals
	time.sleep(0.025)#Wait for work(25ms)
	Running = 1#Set loop to on
	Remaining_Transfers = []#All the data left for transfer.
	while Running:
		#Make sure service dies with server
		if (On == 0):
			break
		#Make sure service dies with server
		#Send out data to buffer on requests
		Addback = []
		for i in range(len(Remaining_Transfers)):
			transfer = Remaining_Transfers.pop()
			try:
				#DOS Check
				if transfer[1] in DOS_Protect.Blocked_Candidates:
					transfer[0].close()#Connection killed
					continue#Quick next loop!
				#DOS Check
				transfer[0].send(transfer[2].read(LargeBuffSize))
				transfer[3]+=LargeBuffSize
				if (transfer[3] < transfer[4]):
					Addback.append(transfer)
				else:
					transfer[2].close()#make sure to close file.
					transfer[0].close()#make sure to close socket.
					DOS_Protect.Remove_Address(transfer[1])
			except Exception,excp:
				#Log errors
				if ErrorLogging:
					DOS_Protect.ELog_Out.append(str(excp)+" :exception at 8\n\n")
				#Log errors
				transfer[2].close()#make sure to close file.
				transfer[0].close()#make sure to close socket.
		Remaining_Transfers = Addback
		#Send out data to buffer on requests
		try:
			my_jobs = Active_Requests[My_ID]
			if (my_jobs != []):
				ready_to_read, ready_to_write, in_error = select.select([item[0] for item in my_jobs], [], [], 0.05)#check which sockets are readable (wait 50ms before moving on)
				for my_job in my_jobs:
					#DOS check
					if my_job[1] in DOS_Protect.Blocked_Candidates:
						Active_Requests[My_ID].remove(my_job)#Remove from active list
						my_job[0].close()#Connection killed
						continue#Quick next loop!
					#DOS check
					if (my_job[0] in ready_to_read):
						File_Obj = Analyse_Request(my_job[0],my_job[1],my_job[2])#Run job
						Active_Requests[My_ID].remove(my_job)#Remove from active list
						#Move Job to Remaining transfers if there is data left to be sent
						if File_Obj:
							Remaining_Transfers.append([my_job[0],my_job[1],File_Obj[0],0,File_Obj[1]])#add to que
						else:
							DOS_Protect.Remove_Address(my_job[1])#Remove from concurrency list
							my_job[0].close()#Connection completed
						#Move Job to Remaining transfers if there is data left to be sent
					else:
						if ((time.time()-my_job[3])>time_out):
							DOS_Protect.Remove_Address(my_job[1])#Remove from concurrency list
							Active_Requests[My_ID].remove(my_job)#Remove from active list
							my_job[0].close()#Connection time out
			#check if i may kill my self
			if ((Active_Requests[My_ID] == []) & (len(Active_ServiceThreads) > Min_Active_ServiceThreads) & (Remaining_Transfers==[])):
				time.sleep(0.05)#wait make sure no new requests(50ms) are coming in
				TLock.acquire()#Lock threading :#
				if ((Active_Requests[My_ID] == []) & (len(Active_ServiceThreads) > Min_Active_ServiceThreads)):
					del Active_Requests[My_ID]#Remove me
					Active_ServiceThreads.remove(My_ID)#DeActivate Me
					TLock.release()#Release threading :O
					Running = 0#Stop Service
					break#Leave loop
				TLock.release()#Release threading :O
			elif ((Active_Requests[My_ID] == []) & (Remaining_Transfers==[])):
				time.sleep(0.05)#IDLE for 50ms so as to not use up cpu
			#check if i may kill my self
		except Exception, e:
			#Release locked up thread
			if TLock.locked():
				TLock.release()#Release threading :O
			#Release locked up thread
			#Log errors
			if ErrorLogging:
				DOS_Protect.ELog_Out.append(str(e)+" :exception at 9\n\n")
			#Log errors
			#Running = 0#Kill service
	#print "trying to kill my self here: "+My_ID
	#print str(len(Active_ServiceThreads)) + ' threads are active'
	#print str(len([grandchild for parent in Active_Requests.values() for child in parent for grandchild in child])/4)+ " Requests being processed" 
	return 0#Finished Service
#Manage Requests

#Create Service Threads
def Create_Service_Thread():
	global MAX_WAIT_TIME_Request
	global Active_ServiceThreads
	ID = str(uuid.uuid4())[:6]
	if not(ID in Active_ServiceThreads):
		Active_ServiceThreads.append(ID)
		Active_Requests[ID] = []
		Thread(target=Threaded_Service, args=(ID,MAX_WAIT_TIME_Request)).start()
		return ID
	else:
		return Create_Service_Thread()
#Create Service Threads

#MAIN
try:
	#Serve
	def Serv_HTTP(HTTPS,SSL_Context=None):
		#Globals
		#Service Threads
		global ServiceThreadLimit
		global Min_Active_ServiceThreads
		global NumberOfServicesPerThread
		global Active_Requests
		global Active_ServiceThreads
		global TLock
		#Service Threads
		#Logging
		global ErrorLogging
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
			if HTTPS:
				Sock.bind((Ip,SSLPort))#Bind to SSL port
				Sock.listen(Socket_Backlog)#Start listening
				print("HTTPS Server Active!")
			else:
				Sock.bind((Ip,Port))#Bind socket to port
				Sock.listen(Socket_Backlog)#Start listening
				print("HTTP Server Active!")#PRINT
		except Exception, err:
			print err
			On = 0#Shutdown any Loops on HTTPS server
			DOS_Protect.On = 0#Shutdown DOS protection
			sys.exit("Dead")#State Death
		#Base
		DOS_Protect.Init()#Begin DOS protection service
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
				if (address[0] in DOS_Protect.Blocked_Candidates):
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

				#If Https
				if HTTPS:
					connection = SSL_Context.wrap_socket(connection, server_side=True)#HTTPSify the connection
				#If Https

				#Accept Connection
				Accepted = 0
				TLock.acquire()#Lock threading :#
				for Active_Service in Active_ServiceThreads:
					if (len(Active_Requests[Active_Service]) < NumberOfServicesPerThread):
						Active_Requests[Active_Service].append([connection,address[0],HTTPS,time.time()])
						Accepted = 1
						#Add to Candidate list for dos
						DOS_Protect.Add_Address(address[0])
						#Add to Candidate list for dos
						break#Stop for loop
				TLock.release()#Release threading :O
				if ((len(Active_ServiceThreads) < ServiceThreadLimit)&(Accepted == 0)):
					ID = Create_Service_Thread()
					Active_Requests[ID].append([connection,address[0],HTTPS,time.time()])
					#Add to Candidate list for dos
					DOS_Protect.Add_Address(address[0])
					#Add to Candidate list for dos
				elif(Accepted==0):
					connection.close()#No space
				#Accept Connection
			except Exception, err:
				#Log errors
				if ErrorLogging:
					DOS_Protect.ELog_Out.append(str(err)+" :exception at 10\n\n")
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
			HTTPSProc = Process(target=Serv_HTTP, args=(1,SSL_Context))
			HTTPSProc.start()
			#start HTTPS on seprate Process (Creates new instance of all variables)
		#HTTPS
		#HTTP
		Serv_HTTP(0)
		#HTTP
	elif SSLEnabled:
		#HTTPS
		Serv_HTTP(1,SSL_Context)
		#HTTPS
	#Start Serving
except:
	DOS_Protect.On = 0#Shutdown DOS protection
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
DOS_Protect.On = 0#Shutdown DOS protection
On = 0#Shutdown any Loops on core server
#SSL
if HTTPSProc:
	HTTPSProc.terminate()#Terminate https process
#SSL
sys.exit("Dead")#State Death
#Shut Down(Ensurance)