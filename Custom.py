#Author:Shoaib Omar (C) 2015.
#Custom interface for Shoaib's HTTP Server.

#Modification of the server(even from here) can result in additional security issues.
#YOU have been WARNED!

#If you want output to be a file(good if output is large to save ram)use Final_Output_File_Path,only used if Final_Output_Content is empty.
#BE CAREFUL Final_Output_File_Path bypasses the allowed folders security checks so it can compromise the entire filesystem if handled incorrectly.
#If returning empty content & path Server will follow usual routine[I.e:- returning files/php].
#If returning 0 as content Server will kill the connection.
#Custom Headers must follow HTTP protocol,EG:- "Accept-Ranges: bytes\n" [don't forget new line after each header]
#Examples are there to help you understand how the code works,they can and should be deleted after you do.

#ALL HEADER DATA IS in the RAW_DATA variable,it is a LIST.
#Any info such as user-agent,can be looked at from here!
#Be careful make sure you sanitize anything before using the data directly,
#as this can result in security flaws.

#POST_DATA can either be a file object (if content size is large > 100KB) or just a var containing the data!
#File name would be the name of the file being posted,may be empty if the data posted is not a file...
#Mime is not the mime of the data but the mime of your output,it should be set.

#IMPORTS
#imports should go here :D
#so that they are loaded when the server is loaded and not when functions are called!
#IMPORTS

#GLOABAL VARS
Server_Working_Directory = ""#Is automatically defult working directory i.e root
#GLOABAL VARS

#Custom GET request Handling
def GET(Requested_Content_Name,Requested_Content_Path,Url_parameters,Mime,RAW_DATA,HTTPS):
	#Init
	global Server_Working_Directory
	Final_Output_Content = ""#Place Holder
	Custom_Headers = ""#Place Holder
	Final_Output_File_Path=""#Place Holder
	#Init

	try:
		#Do Work Here
		#EXAMPLE
		if ("Hello.html" in Requested_Content_Name):
			Final_Output_Content = "<html><h1>Hello World!</h1></html>"
		#EXAMPLE
		#Do Work Here
	except Exception, e:
		pass
	return Final_Output_Content,Mime,Custom_Headers,Final_Output_File_Path#Return Content,Mime type & Any custom headers.
#Custom GET request Handling

#Custom POST request Handling
def POST(Requested_Content_Name,Requested_Content_Path,Url_parameters,Mime,POST_DATA,RAW_DATA,File_Name,HTTPS):
	#Init
	global Server_Working_Directory
	Final_Output_Content = ""#Place Holder
	Custom_Headers = ""#Place Holder
	Final_Output_File_Path=""#Place Holder
	#Init

	try:
		#Do Work Here

		#EXAMPLE
		#Basic Example
		if ("Donald" in POST_DATA):
			Final_Output_Content = "Duck"
		#Basic Example
		#
		#Advanced Example
		#Method = 0
		#if ((File_Name == "E1.mkv") & ("CopyThatFile=True" in Url_parameters)):#This will check for a url like http://website.com/post.html?CopyThatFile=True in the post Action=field
		#	import os
		#	#Method 1
		#	if (Method):
		#		F = open("E1.mkv","wb")
		#		POST_DATA.seek(0, os.SEEK_END)
		#		lenght = POST_DATA.tell()
		#		POST_DATA.seek(0)
		#		count = 0
		#		while (count < lenght):
		#			F.write(POST_DATA.read(64511))
		#			count+=64511
		#		F.close()
		#	else:
		#		#Method 2
		#		os.system("cp "+POST_DATA.name.replace(" ","\ ")+" E1.mkv")
		#		#Method 2
		#	Final_Output_Content ="<html><h1>Worked</h1></html>"
		#	Mime = "text/html"#Set Mime type of output
		#Advanced Example
		#EXAMPLE

		#Do Work Here
	except Exception, e:
		pass
	return Final_Output_Content,Mime,Custom_Headers,Final_Output_File_Path#Return Content,Mime type & Any custom headers.
#Custom POST request Handling

#Custom 404
def Not_Found(File_Name):
	HTML = ""
	try:
		#Get HTML from file or etc
		pass
		#Get HTML from file or etc
	except Exception, e:
		pass
	return HTML
#Custom 404

#Custom 403
def Forbidden(File_Name):
	HTML = ""
	try:
		#Get HTML from file or etc
		pass
		#Get HTML from file or etc
	except Exception, e:
		pass
	return HTML
#Custom 403

#User Agent
#def Get_User_Agent(RAW_DATA):
#	#Get User-Agent
#	for SubData in RAW_DATA:
#		if "User-Agent:" in SubData:
#			return SubData.split(":")[1].strip()
#	#Get User-Agent
#	return None#No User Agent.
#User Agent

#Cookies
#def Get_Cookies(RAW_DATA):
#	#Get Cookies
#	for SubData in RAW_DATA:
#		if "ookie:" in SubData:
#			return SubData.split(":")[1].strip()
#	#Get Cookies 
#	return None#No Cookies.
#Cookies
