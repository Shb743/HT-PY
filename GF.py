#Author:Shoaib Omar (C) 2015
#Modify HDANA if needed.
#COLLECTION OF ALL FUNCTIONS NEEDED TO BE USED ACROSS SERVER(Global Functions)
HDANA = ["content-type","accept-ranges","content-length","etag"]#-MUST BE IN LOWER CASE-HeaderDuplicatesAreNotALlowed these headers will have their values replaced if duplicate custom headers are present

#Construct Output Header
def Construct_Header(Custom_Headers,Keep_Alive,Mime,Cont_Size,Code="200 OK",Ranges="bytes"):
	Response="HTTP/1.1 "+Code+"\nServer: SHB/1.0 (SHB)\nContent-Type: "+Mime+";\nContent-Length: "+Cont_Size+"\nAccept-Ranges: "+Ranges+"\nConnection: "+Keep_Alive+"\n\n"
	if (Custom_Headers != ""):
		Custom_Header_Array = Custom_Headers.split("\n")
		for Header in Custom_Header_Array:
			#Useless header detection
			if not(":" in Header):
				continue#Do not bother with use less headers
			#Useless header detection
			Split_Loc = Header.find(":")
			Tmp_Header_Holder = [Header[:Split_Loc].strip(),Header[Split_Loc+1:].strip()]
			Tmp_Header_HolderL = Tmp_Header_Holder[0].lower()
			#Special Case
			if "status" in Tmp_Header_HolderL:
				Response = Response.replace(Code,Tmp_Header_Holder[1])
				continue#Skip this header
			#Special Case
			#Avoid Duplicates?
			if ((Tmp_Header_HolderL in Response.lower()) & (Tmp_Header_HolderL in HDANA)): #Avoid duplicates in special cases
				Rsp_header_val = Response[Response.lower().index(Tmp_Header_HolderL)+len(Tmp_Header_Holder[0])+1:].split("\n")[0].strip()
				Response = Response.replace(Rsp_header_val,Tmp_Header_Holder[1])
			else:
				Response = Response[:-(len("\nConnection: "+Keep_Alive+"\n\n")-1)]+Header+"\n"+Response[-(len("\nConnection: "+Keep_Alive+"\n\n")-1):]
			#Avoid Duplicates?
	return Response
#Construct Output Header


#COLLECTION OF ALL FUNCTIONS NEEDED TO BE USED ACROSS SERVER(Global Functions)