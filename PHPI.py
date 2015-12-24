#Author:Shoaib Omar (C) 2015.
#PHP interface for Shoaib's HTTP Server.

#Modification of the server can result in additional security issues.

#IMPORTS
import os,sys,GF
#Escaping php
try:
	from pipes import quote
except ImportError:
	from shlex import quote
#Escaping php
#IMPORTS


#User Changeable
MAX_PHP_EXECUTION_TIME = 3#Max time php allowed to run...
#User Changeable

#GLOBALS
WD = os.getcwd()#Working Dir
Server_file_path = WD+"/Server_Files/"#Server Path.
PHP_CGI_PATH = ""#Place Holder.
WINDOWS_OS = (sys.platform == "win32")
Error=0
EMSG = ""
#GLOBALS

#Configure Subprocess
def Configure_Subprocess():
	#Globals
	global Server_file_path
	global WINDOWS_OS
	global Error
	global EMSG
	#Globals
	if not(os.path.isfile(Server_file_path+"Libraries/Subprocess32/subprocess32.py")):#Check if installed
		try:
			if (raw_input("Subprocess(an important library) is going to be installed,do you wish to continue(Y/N): ") == "Y"):
				if not(WINDOWS_OS):
					os.chdir(Server_file_path+"Libraries/")
					os.system("unzip "+Server_file_path+"Libraries/subprocess32-3.2.6.zip")
					os.chdir(Server_file_path+"Libraries/subprocess32-3.2.6/")
					os.system("python setup.py build")
					os.system("python setup.py clean")
					os.chdir("build/")
					os.system("mv "+os.listdir(os.getcwd())[0]+" "+Server_file_path+"Libraries/Subprocess32/")
					os.chdir(Server_file_path+"Libraries/")
					os.system("rm -r subprocess32-3.2.6")
					os.chdir(Server_file_path+"..")
				else:
					print "Has not been implemented on win32 yet!"
					Error=1
					EMSG = "No subprocess on windows."
			else:
				Error=1
				EMSG = "Closing Server,Server requires subprocess32 to be installed!"
		except Exception, e:
			Error=1
			EMSG = "Closing Server,Subprocess installation error:"+str(e)
#Configure Subprocess
Configure_Subprocess()#Configure it!
#Import Subprocess
sys.path.insert(0, Server_file_path+"Libraries/Subprocess32/")
import subprocess32 as subprocess#Mr PHP.
#Import Subprocess

#Configure PHP
def Configure_PHP():
	#Globals
	global WINDOWS_OS
	global Server_file_path
	global PHP_CGI_PATH
	global Error
	global EMSG
	#Globals
	try:
		if not(WINDOWS_OS):
			if not(os.path.isfile(Server_file_path+"PHP/php_compiled/bin/php-cgi")):
				if (raw_input("PHP is going to be installed,do you wish to continue(Y/N): ") == "Y"):
					#Get install options
					SQL = raw_input("Do you wish to enable SQL(Y/N): ") == "Y"
					SQL_Path = ""
					if SQL:
						SQL_Path = raw_input("Please enter the path for SQL: ")
						if SQL_Path == "":
							SQL_Path  = "/usr/local/mysql"

					CURL =  raw_input("Do you wish to enable CURL(Y/N): ") == "Y"
					CURL_Path = ""
					if CURL:
						CURL_Path = raw_input("Please enter the path for CURL: ")
						if CURL_Path == "":
							CURL_Path = "/usr"
					ODBC = raw_input("Do you wish to enable ODBC(Y/N): ") == "Y"
					ODBC_Path = ""
					if ODBC:
						ODBC_Path = raw_input("Please enter the path for ODBC: ")
						if ODBC_Path == "":
							ODBC_Path = "/usr"
					#Get install options
					#Configure options
					PHP_CONFIGURE_COMMAND = "./configure --prefix=\'"+Server_file_path+"PHP/php_compiled\' --disable-cli --enable-cgi --enable-trans-sid   --enable-mbstring --with-xml --enable-exif --enable-mbregex --enable-dbx --enable-sockets   --with-config-file-path=/etc --sysconfdir=/private/etc --without-pear"
					if SQL:
						PHP_CONFIGURE_COMMAND += " --with-mysql="+SQL_Path
					else:
						PHP_CONFIGURE_COMMAND += " --without-mysql"

					if CURL:
						PHP_CONFIGURE_COMMAND += " --with-curl="+CURL_Path
					else:
						PHP_CONFIGURE_COMMAND+=" --without-curl"

					if ODBC:
						PHP_CONFIGURE_COMMAND += " --with-iodbc="+ODBC_Path
					else:
						PHP_CONFIGURE_COMMAND+=" --without-iodbc"
					#Configure options
					os.chdir(Server_file_path+"PHP/php_source/")
					os.system("tar -xzvf php-5.6.9.tar.gz")#Unzip Source
					os.chdir("php-5.6.9/")#Go into source folder
					os.system(PHP_CONFIGURE_COMMAND)#Run The Configure Command
					os.system("make install")#Compile
					os.chdir("../")#Leave source folder
					os.system("rm -r php-5.6.9")#Delte source folder
					PHP_CGI_PATH = Server_file_path+"PHP/php_compiled/bin/./php-cgi"#Set PHP CGI PATH
				else:
					print "Server will not play nice with PHP Files!"
					EMSG = "You did not setup php,reboot server to reinitialize setup."
			else:
				PHP_CGI_PATH = Server_file_path+"PHP/php_compiled/bin/./php-cgi"#Set PHP CGI PATH
		else:
			PHP_CGI_PATH = Server_file_path+"PHP/no-path"#Set PHP CGI PATH
	except:
		Error = 1
		EMSG = "Error Configuring PHP"
#Configure PHP
Configure_PHP()#Configure it!
os.chdir(WD)#Reset working Dir

#Communicate
def subprocess_cmd(command,InData,cwdd,MAX_PHP_EXECUTION_TIME):
	#print command+'\n'+str(InData)+"\n\n\n"
	process = subprocess.Popen(command,stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True,cwd=cwdd)
	proc_stdout = ""
	try:
		if (InData!=None):
			proc_stdout = process.communicate(input=InData,timeout=MAX_PHP_EXECUTION_TIME)[0].strip()
		else:
			proc_stdout = process.communicate(timeout=MAX_PHP_EXECUTION_TIME)[0].strip()
		return proc_stdout
	except:
		process.kill()#Kill process
	return "Status:400 Error\n\rSome thing went wrong with php?"#Upon Failure
#Communicate

#Header to enviornment variables
def HeaderToEnvVars(RAW_DATA):
	Export_Str = ""
	for Data in RAW_DATA:
		if (":" in Data):
			Data = Data.replace("'",'"')#Prevent escape strings :3
			Split_Loc = Data.find(":")#Split only by first :
			Meh_data = [Data[:Split_Loc].strip(),Data[Split_Loc+1:].strip()]#split only by first :
			MEH = quote((Meh_data[0].upper()).replace("-","_").strip())#Replace - with _ & make shell safe
			if (MEH == "CONTENT_TYPE"):
				Export_Str += "export "+MEH+"="+quote(Meh_data[1])+";"
			elif( (len(MEH) >= 3) and not("HTTP" in MEH)):#Make sure first header is not inserted
				Export_Str += "export HTTP_"+MEH+"="+quote(Meh_data[1])+";"
	return Export_Str
#Header to enviornment variables




#GET/HEAD
def GET_PHP(Content_Name,Content_Path,RAW_DATA,Url_parameters,Port,Ip,Working_Directory,HTTPS):
	#Error Check
	if (EMSG!=""):
		html = "<html><h2>PHP FAILED TO LOAD</h2><br><p1>An error has occured:"+EMSG+"<p1></html>"
		return GF.Construct_Header("","close","text/html",str(len(html)),"400 ERROR"),html
	#Error Check
	global PHP_CGI_PATH
	global MAX_PHP_EXECUTION_TIME
	global WINDOWS_OS
	if not(WINDOWS_OS):
		#print Content_Path
		Export_String = HeaderToEnvVars(RAW_DATA)+ "export QUERY_STRING="+quote(Url_parameters)+";export SCRIPT_FILENAME="+quote(Content_Name)+";export REQUEST_METHOD=GET;export GATEWAY_INTERFACE=CGI/1.1;export REDIRECT_STATUS=true;export SERVER_SOFTWARE='SHB/1.0 (SHB)';export SERVER_PROTOCOL='HTTP/1.1';export SERVER_PORT="+str(Port)+";export SERVER_NAME='"+Ip+"';export PATH_INFO="+quote(Content_Path.replace(Working_Directory[:-1],"")+Content_Name)+";"
		#Set HTTPS to true
		if HTTPS:
			Export_String+="export HTTPS=1;"
		#Set HTTPS to true
		PHP_OUT=subprocess_cmd(Export_String+PHP_CGI_PATH+" '"+Content_Name+"'",None,Content_Path,MAX_PHP_EXECUTION_TIME).split("\n\r")
		Custom_Headers = PHP_OUT[0].replace("\r\n","\n")#Extract Header info
		del PHP_OUT[0]#Delete Header info
		#Make sure there is content
		if (len(PHP_OUT) > 0):
			Cont = str.join("\n",PHP_OUT).strip()#Extract content
		#Make sure there is content
		del PHP_OUT
		return Custom_Headers,Cont
	else:
		html = """<html><h1>Sorry I have not bothered to get this working on windows,yet. :P,If you want to get it done with out waiting for me, go ahead</h1>
		<br>
		<p1>The php files should already exist in Server_Files/PHP/php_windows/ and the PHP_CGI_PATH should automatically set to it.
		<br>
		the only thing you need to do is configure the communication between the server and the executable...
		<br>
		The code above (where this message is produced) should show you how to do it,as this is the code used by the unix php binary.
		</p1>
		</html>
		"""
		return GF.Construct_Header("","close","text/html",str(len(html)),"400 ERROR"),html#Tell windows users that Im Sorry O.o,Am I,am I really ?#Tell windows users that Im Sorry O.o,Am I,am I really ?#Tell windows users that Im Sorry O.o,Am I,am I really ?
#GET/HEAD





#POST
def POST_PHP(RAW_DATA,Url_parameters,Content_Name,Port,Ip,Content_Path,Working_Directory,POST_File_Handling,POST_DATA,POST_File_Name,HTTPS):
	#Error Check
	if (EMSG!=""):
		html = "<html><h2>PHP FAILED TO LOAD</h2><br><p1>An error has occured:"+EMSG+"<p1></html>"
		return GF.Construct_Header("","close","text/html",str(len(html)),"400 ERROR"),html
	#Error Check
	global MAX_PHP_EXECUTION_TIME
	global WINDOWS_OS
	global PHP_CGI_PATH
	if not(WINDOWS_OS):
		PHP_OUT = ""#Place Holder
		Export_String = HeaderToEnvVars(RAW_DATA)+ "export QUERY_STRING="+quote(Url_parameters)+";export SCRIPT_FILENAME="+quote(Content_Name)+";export REQUEST_METHOD=POST;export GATEWAY_INTERFACE=CGI/1.1;export REDIRECT_STATUS=true;export SERVER_SOFTWARE='SHB/1.0 (SHB)';export SERVER_PROTOCOL='HTTP/1.1';export SERVER_PORT="+str(Port)+";export SERVER_NAME='"+Ip+"';export PATH_INFO="+quote(Content_Path.replace(Working_Directory[:-1],"")+Content_Name)+";"
		#Set HTTPS to true
		if HTTPS:
			Export_String+="export HTTPS=1;"
		#Set HTTPS to true
		#Normal
		if not(POST_File_Handling):
			#Check for valid post headers
			if not("CONTENT_TYPE" in Export_String):
				html = "<html><h1>POST ERROR,header \"CONTENT_TYPE\" not present!</h1></html>"
				con.send(GF.Construct_Header("","close","text/html",str(len(html)),"400 ERROR")+html)
				return None#Stop execution
			#Check for valid post headers
			Export_String = "export CONTENT_LENGTH='"+str(len(POST_DATA))+"';"+Export_String
			#print Export_String+PHP_CGI_PATH+" '"+Content_Name+"'"
			#print ""
			#print POST_DATA
			#print ""
			#print Content_Path
			#print "\n\n\n"
			PHP_OUT=subprocess_cmd(Export_String+PHP_CGI_PATH+" '"+Content_Name+"'",POST_DATA,Content_Path,MAX_PHP_EXECUTION_TIME).split("\n\r")
		#Normal
		#File Handling
		else:
			if (POST_File_Name != ""):
				Export_String +="export POST_FILE_PATH="+quote(POST_DATA.name)+";export POST_FILE_NAME="+quote(POST_File_Name)+";"
			else:
				Export_String +="export POST_FILE_PATH="+quote(POST_DATA.name)+";"
			PHP_OUT=subprocess_cmd(Export_String+PHP_CGI_PATH+" '"+Content_Name+"'",None,Content_Path,MAX_PHP_EXECUTION_TIME).split("\n\r")
		#File Handling
		Custom_Headers = PHP_OUT[0].replace("\r\n","\n")#Extract Header info
		del PHP_OUT[0]#Delete Header info
		#Make sure there is content
		if (len(PHP_OUT) > 0):
			Cont = str.join("\n",PHP_OUT).strip()#Extract content
		#Make sure there is content
		del PHP_OUT
		return Custom_Headers,Cont
	else:
		html = """<html><h1>Sorry I have not bothered to get this working on windows,yet. :P,If you want to get it done with out waiting for me, go ahead</h1>
		<br>
		<p1>The php files should already exist in Server_Files/PHP/php_windows/ and the PHP_CGI_PATH should automatically set to it.
		<br>
		the only thing you need to do is configure the communication between the server and the executable...
		<br>
		The code above (where this message is produced) should show you how to do it,as this is the code used by the unix php binary.
		</p1>
		</html>
		"""
		return "status: 400 Error\nContent-Type: text/html;\n",html#Tell windows users that Im Sorry O.o,Am I,am I really ?
#POST