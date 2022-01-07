#======================================================================================================================================================
#======================================================================================================================================================

# Imports

import os, configparser, json, OpenSSL


from datetime import datetime

from openpyxl import load_workbook, Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font

from tabulate import tabulate

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


#======================================================================================================================================================
#======================================================================================================================================================

# Variables

msg = MIMEMultipart()
formatter = '\n' + "____________________________________________________________________________________" + "\n"
Occurances_Summary=[]
Files_List=[]
Search_Dirs=[]
#Search_Dirs=["\\var\\log\\firemon\\nd", "\\var\\log\\fmos"]
#Search_Dirs=["\\var\\log\\firemon\\sm\\secmgr.log"]
Health_File_Name='health.log'
ssl_access_File_Name='ssl_access_log'
ndexec_File_Name='ndexec'


ssl_access_Search_Criteria=[]
ndexec_Search_Criteria=[]
Health_Search_Criteria=[]
Top_Largest_files=[] 
global_search=[]
Percentage_of_Licences_Allocated=[]
Days_Until_Certificates_Expire=[]
Device_Uptime=30

#Device Inventory Report
Device_Count=[]
device_type=[]
Device_Count2=[]
device_type2=[]
Check_Installed_DP=0
Total_Devices_Summary=""
Check_Installed_DPs=""
DP_list=[]

allFiles=[]
biggest2=[]
biggest3=[]
alldirs=[]


messagesDropped_list=[]
Drops_Found=0
Drops_Summary=""


final_unread=[]
unread=[]
all_files_full_path=[]
global_search_count=0

summary_cpu=[]
summary_cpu_count=0

exception_list=[]

lic_max_util=0
total_finds=[]

certs='\\etc\\pki\\tls\\certs\\localhost.crt', '\\etc\\pki\\ca-trust\\source\\anchors\\fmos-root.crt', '\\etc\\pki\\tls\\certs\\fmos-admin.cer'
display_name=''
warn_expire=0
Summary_Dir_Check='WARNING -- .xy files skipped'

cpu_count=0
temp_files_count=0

#======================================================================================================================================================
#======================================================================================================================================================

# Reading the Config File and storing contents

try:


	config = configparser.ConfigParser()
	config.read("mkdiag_script_config_v1.ini")


	for key in config['health']:
		value=config['health'][key]
		Health_Search_Criteria.append(value)


	for key in config['ndexec']:
		value=config['ndexec'][key]
		ndexec_Search_Criteria.append(value)


	for key in config['ssl_access']:
		value=config['ssl_access'][key]
		ssl_access_Search_Criteria.append(value)
		

	for key in config['No_Of_Files']:
		value=config['No_Of_Files'][key]
		Top_Largest_files.append(value)


	for key in config['global_search']:
		value=config['global_search'][key]
		global_search.append(value)


	for key in config['Percentage_of_Licences_Allocated']:
		value=config['Percentage_of_Licences_Allocated'][key]
		Percentage_of_Licences_Allocated.append(value)


	for key in config['Days_Until_Certificates_Expire']:
		value=config['Days_Until_Certificates_Expire'][key]
		Days_Until_Certificates_Expire.append(value)


	for key in config['Search_Dirs']:
		value=config['Search_Dirs'][key]
		Search_Dirs.append(value)


	for key in config['Device_Uptime_Config']:
		value=config['Device_Uptime_Config'][key]
		Device_Uptime=value


	for key in config['Days_Until_Certificates_Expire']:
		value=config['Days_Until_Certificates_Expire'][key]
		Days_Until_Certificates_Expire.append(value)

		


except Exception as e:
	print(e)
	print("Error reading config file")
	exception_list.append(e)



#======================================================================================================================================================
#======================================================================================================================================================

# Functions

def directory_search(MyLoc, Dir, Log, words):

	#Get a list of all files in a directory
	dir_search = os.listdir( MyLoc + Dir)
	Files_List=[]

	#Filter the list provided above to only files that contain string of interest
	for item in dir_search:
		if Log in item: #Pass in this string in future
			Files_List.append(item)
		else:
			pass

	#Loop through each log file of interest, reading each 
	for Log_Check in Files_List:
		#print(Log_Check)
		if '.xz' in Log_Check:
			Summary_Dir_Check='WARNING -- .xy files skipped'
			pass
		else:
			Summary_Dir_Check='WARNING -- .xy files skipped'
			f = open(str(windows_pwd) + Dir +"\\" + str(Log_Check))
			lines = f.read()
			occurances=0
			
			#Grab a word to search on, count total occurances in file and add to Occurances_Summary
			for word in words:
				occurances=lines.count(word)
				Occurances_Summary.append(str(Log_Check)+ " --- "+str(word)+' --- '+str(occurances))
				

				#Divide the file into lines and check if it contains the word of interest	
				for line in lines.split('\n'):
					if word in line:

						#Output successful matches to various places 
						print(Log_Check + " ---- "+ line + "\n")
						#LoggingFile.write(Log_Check + " ---- "+ line + "\n")
						#Health_LoggingFile.write(Log_Check + " ---- "+ line + "\n")
					else:
						pass



#======================================================================================================================================================
#======================================================================================================================================================

# Other

pwd=os.getcwd()
print("Present Working Directory " + pwd)
windows_pwd=pwd.replace('\\','\\\\')

try:
	os.mkdir(pwd + "\\script_output")
except:
	pass


wb=load_workbook('formatted.xlsx')
ws = wb.active
ws.title='nicko'

LoggingFile = open(pwd + "\\script_output\\Logging_" + os.path.basename(__file__) + ".txt" , "w")
Summary_LoggingFile = open(pwd + "\\script_output\\Summary_Logging_" + os.path.basename(__file__) + ".txt" , "w")


#======================================================================================================================================================
#======================================================================================================================================================

# mkdiagpkg.out

print(formatter)

print("Opening mkdiagpkg.out")
print()
f = open("mkdiagpkg.out")
mkdiagpkg_out = f.read().splitlines()


FMOSv=mkdiagpkg_out[1].split("FMOS release ")
mkdiag_created=mkdiagpkg_out[2]
hostname=mkdiagpkg_out[3].split(" ")[1]
Device_Uptime_host_test=(mkdiagpkg_out[4].split("up")[1].split(",")[0])

# if uptime contains mins set to one day


if 'days' not in Device_Uptime_host_test:
	Device_Uptime_host=1
Device_Uptime_host=Device_Uptime_host_test.strip()
Device_Uptime_host=Device_Uptime_host.split(" ")[0]



#elif 'days' in Device_Uptime_host_test:
#	Device_Uptime_host=int(Device_Uptime_host_test.split(" days")[0])

print('nick')
print(Device_Uptime_host)

# UpT=mkdiagpkg_out[4].split("up ")
FMOSv=FMOSv[1]
short_FMOSv = FMOSv[:-2]

# UpT=UpT[1].split(",")
# UpT=str(UpT[0]) +" "+str(UpT[1])

print("MKDIAG Generated: " + str(mkdiag_created))
print("FMOS Hostname: " + str(hostname))
print("FMOS Version: " + str(FMOSv))
print("Uptime: " + str(Device_Uptime_host_test))
print()
if int(Device_Uptime_host) > int(Device_Uptime):
	print("WARNING -- Device Uptime is greater than " + str(Device_Uptime)+ " days.")
	Check_Device_Uptime="WARNING -- Device Uptime is greater than " + str(Device_Uptime)+ " days."
else:
	print("PASS -- Device Uptime is less than " + str(Device_Uptime)+ " days.")
	Check_Device_Uptime="PASS -- Device Uptime is less than " + str(Device_Uptime)+ " days."

print()
print("Closing mkdiagpkg.out")
f.close()
print(formatter)

LoggingFile.write("Opening mkdiagpkg.out")
LoggingFile.write('\n' +"FMOS Version: " + mkdiagpkg_out[1])
LoggingFile.write('\n' +"Uptime: " + mkdiagpkg_out[4])
LoggingFile.write('\n' +"Closing mkdiagpkg.out")
LoggingFile.write(formatter)



#======================================================================================================================================================
#======================================================================================================================================================

# Device Inventory Report

print("Opening deviceInventoryReport")
print()
try:
	if os.path.exists(str(windows_pwd) +"\\var\\log\\firemon\\dc\\reports\\deviceInventoryReport.txt"):

		f = open(str(windows_pwd) +"\\var\\log\\firemon\\dc\\reports\\deviceInventoryReport.txt", encoding="utf8")
		deviceInventoryReport = f.readlines()

		for line in deviceInventoryReport:
			if "Device" in line:
				Device_Count.append(line)
			if 'DevicePack Artifact ID' in line:

				device_type.append(line)

		for item in Device_Count:
			if "/" in item:
				Device_Count2.append(item)
			if "Version" in item:
				Device_Count2.append(item)
				DP_Ver_Check=item.split(".")
				Storing_DP=DP_Ver_Check[0][-1]+'.'+ DP_Ver_Check[1][0]+'.'+ DP_Ver_Check[2][:2]
				DP_Ver_Check=DP_Ver_Check[0][-1]+'.'+ DP_Ver_Check[1]
				if DP_Ver_Check!= short_FMOSv:
					Check_Installed_DP+=1
				Storing_DP = Storing_DP.strip()
				if Storing_DP not in  DP_list:
					DP_list.append(Storing_DP)

		
		for item in device_type:

			item=item.split("│")[2].strip()

			device_type2.append(item)
		#print(device_type2)
		print()

		


		"""

		Make nice list showing device count

		"""
		device_totals=[]
		device_type3 = list(set(device_type2))
		# for line in device_type2:
		# 	print(line)


		for item in device_type3:		
			x=device_type2.count(item)
			emptylist=[] 		
			emptylist.append(item)
			emptylist.append(x)
			device_totals.append(emptylist)


		device_totals.sort(key = lambda x: x[1])
		print(tabulate(device_totals, headers=['Device', 'Count']))


		"""

		End of Make nice list showing device count

		"""


		print()
		Total_Devices=len(Device_Count2)/2
		print("There are "+str(int(Total_Devices))+" devices, using the following Device Packs")
		Total_Devices_Summary="There are "+str(int(Total_Devices))+" devices"
		

		print(', '.join(DP_list))
		print()

		if Check_Installed_DP != 0:
			print("WARNING -- Check Installed Device Packs")
			Check_Installed_DPs="WARNING -- Check Installed Device Packs"
		else:
			print("PASS -- Appropiate Device Packs Installed")
			Check_Installed_DPs="PASS -- Appropiate Device Packs Installed"
	else:
		Check_Installed_DPs="N/A -- Device Packs Check not performed. No DC element to MKDIAG"
		print(Check_Installed_DPs)






		
	print()
	print("Closing deviceInventoryReport")
	f.close()
	print(formatter)

except Exception as e:
	print(e)
	print("Error Checking Device Inventory")
	print()
	print(formatter)



#======================================================================================================================================================
#======================================================================================================================================================

# Directory Searches


print("Begining Directory Searches")
print()




for Search_Dir in Search_Dirs:
	if 'fmos' in Search_Dir:
		DirF=Search_Dir
		LogF=Health_File_Name
		WordsF=Health_Search_Criteria
	elif 'httpd' in Search_Dir:
		DirF=Search_Dir
		LogF=ssl_access_File_Name
		WordsF=ssl_access_Search_Criteria
	elif 'nd' in Search_Dir:
		DirF=Search_Dir
		LogF=ndexec_File_Name
		WordsF=ndexec_Search_Criteria

	directory_search(str(windows_pwd), DirF, LogF, WordsF)
print("Completed Directory Searches")
print(formatter)



#======================================================================================================================================================
#======================================================================================================================================================

# Top 3 biggest files

print("Calculating the 3 largest files present")
print()
try:

	for root, dirs, files in os.walk(".", topdown=True):
		for name in files:
			full_path=os.path.join(root, name)
			allFiles.append(full_path)


	max_file = max(allFiles, key =  lambda x: os.stat(x).st_size)
	print('Largest File (GB\'s): ', os.stat(max_file).st_size/1000000000)
	print(max_file)


	for item in allFiles:
		if str(max_file) in item:
			pass
		else:
			biggest2.append(item)



	max_file2 = max(biggest2, key =  lambda x: os.stat(x).st_size)
	print()
	print('Second Largest File (GB\'s): ', os.stat(max_file2).st_size/1000000000)
	print(max_file2)


	for item in biggest2:
		if str(max_file2) in item:
			pass
		else:
			biggest3.append(item)

	max_file3 = max(biggest3, key =  lambda x: os.stat(x).st_size)
	print()
	print('Third Largest File (GB\'s): ', os.stat(max_file3).st_size/1000000000)
	print(max_file3)


except Exception as e:
	print(e)
	print("Error Calculating largest 3 files")


print(formatter)



#======================================================================================================================================================
#======================================================================================================================================================

# Metrics Log

try:

	print("Opening metrics.log")
	print()
	if os.path.exists(str(windows_pwd) +"\\var\\log\\firemon\\dc\\metrics.log"):


		f = open(str(windows_pwd) +"\\var\\log\\firemon\\dc\\metrics.log")
		metrics = f.readlines()

		for line in metrics:
			if "messagesDropped" in line:
				messagesDropped_list.append(line)
			else:
				pass


		for item in messagesDropped_list:
			item=item.split(':')
			clean_item=item[1]
			clean_item=clean_item.strip()
			number_check=int(clean_item)
			if number_check > 0:
				print(item)
				Drops_Found+=1
			else:
				pass



		if Drops_Found > 0:
			Drops_Summary="WARNING -- Evidence Of Dropped Packets Found - Check \\var\\log\\firemon\\dc\\metrics.log"
		else:
			Drops_Summary="PASS -- No Evidence Of Dropped Packets Found"

		print(Drops_Summary)
	else:
		Drops_Summary="N/A -- Dropped Packets Check not performed. No DC element to MKDIAG"
		print(Drops_Summary)

	print()
	print("Closing metrics.log")

except Exception as e:
	print(e)
	print("Error Checking metrics.log")

print(formatter)



#======================================================================================================================================================
#======================================================================================================================================================

# Global Search

try:
	print("Start of performing Global Search")
	print()

	if len(global_search) > 0:
		print(', '.join(global_search))

	for gs in global_search:
		print('Looking for '+str(gs))
		print()
		for dirpath, subdirs, files in os.walk(".", topdown=True):
		    for x in files:
		    	all_files_full_path.append(os.path.join(dirpath, x))



		for name in all_files_full_path:
			if 'mkdiag_script_config_v1.ini'in name:
				pass
			else:
				try:

					f = open(name)
					lines = f.readlines()
					for line in lines:
						if gs in line:
							global_search_count=global_search_count+1
							print(name)
							total_finds.append(name)
							print(line)

				except:
					unread.append(name)



		i=1
		while i < 10:
			i=i+1
			for unreadable in unread:
				try:
					f = open(unreadable, encoding="utf8")
					fc = f.readlines()
					for line in lines:
						if gs in line:
							global_search_count=global_search_count+1
							print(line)
					unread.remove(unreadable)
				except:
					pass
	print()
	print()
	total_finds = list(dict.fromkeys(total_finds))
	print(', '.join(total_finds))
	print()
	print()
	print("End of performing Global Search")

except Exception as e:
	print(e)
	print("Error performing Global Search")


print(formatter)



#======================================================================================================================================================
#======================================================================================================================================================

# Top

try:

    print("Opening Top")
    print()
    f = open(str(windows_pwd) +"\\top.txt")
    top = f.read()

    line = top.split('\n')
    print(line[0])
    cpu_loadavg_1=line[0].split('average: ')[1].split(',')[0]
    cpu_loadavg_5=line[0].split('average: ')[1].split(',')[1].strip()
    cpu_loadavg_15=line[0].split('average: ')[1].split(',')[2].strip()
    MiB_Mem=line[3]

    print(cpu_loadavg_15)
    MiB_Swap=line[4]

    #MiB Mem


    MiB_Mem=MiB_Mem.split(" ")
    MiB_Mem_total=int(float(MiB_Mem[4]))
    MiB_Mem_used=int(float(MiB_Mem[12]))

    mem_pc = int(float(MiB_Mem_used /MiB_Mem_total *100))


    print('The total physical memory in use is '+str(mem_pc) +'%.')

    MiB_Mem_total_90pc = int(float(MiB_Mem_total / 100 * 90))
    if MiB_Mem_used > MiB_Mem_total_90pc:
        print("WARNING -- greater than 90% of total physical memory is in use")



    print()

    #Swap Mem

    MiB_Swap=MiB_Swap.split(" ")
    MiB_Swap_used=int(float(MiB_Swap[12]))

    if MiB_Swap_used > 0:
        print("WARNING -- Swap Memory in use")


    print()

    #CPU
    cpu_des=line[6]

    newlist=[]
    newlist.append(line[7:])

    for item in newlist[0]:
        all_ent=[]
        item2=item.split(" ")
        for items in item2:
            if items != "":
                all_ent.append(items)
        try:
            cpu_usage=int(float(all_ent[8]))
        except:
            pass



        if cpu_usage > 85:
            summary_cpu.append(item)
            summary_cpu_count+=1
            #print(item)
        else:
            pass

    if summary_cpu_count > 0:
        summary_cpu_text="WARNING -- The following processes are using 85% CPU or more"
        print(summary_cpu_text)
        print(cpu_des)
        for process in summary_cpu:
            print(process)
    else:
        summary_cpu_text="PASS -- Top does not show excessive CPU usage"
        print(summary_cpu_text)
    print()
    print("Closing Top")


except Exception as e:
	print(e)
	print("Error reading Top")

print(formatter)



#======================================================================================================================================================
#======================================================================================================================================================

# Crashdump

print("Checking for Crash Dumps")
print()
try:


	os.chdir(str(windows_pwd) +"\\var\\lib")
	if os.path.isdir('crashdump'):
		os.chdir(str(windows_pwd) +"\\var\\lib\\crashdump")

		here=os.listdir()

		if len(here) > 0:

			Core_Summary='WARNING -- Core Files Found'
			print(Core_Summary)
			for core in here:
				print(core)
		else:
			Core_Summary='PASS -- No Core Files Found'
			print(Core_Summary)

	else:
		Core_Summary='PASS -- No Core Files Found'
		print(Core_Summary)

	os.chdir(str(windows_pwd))


		
	print()
	print("Closing Check for Crash Dumps")
	f.close()
	print(formatter)

except Exception as e:
	print(e)
	print("Error Checking for Crash Dumps")



#======================================================================================================================================================
#======================================================================================================================================================

# Off Site Backup

print("Checking for Off Box Backup")
print()
try:


	os.chdir(str(windows_pwd) +"\\etc\\firemon\\postbackup.d")
	here=os.listdir()


	if len(here) < 3:

		Backup_Summary='WARNING -- Check if \'Off Box\' Backup Configured'
		print(Backup_Summary)
		print()
		for her in here:
			print(her)

	else:
		Backup_Summary='PASS -- \'Off Box\' Backup Configured'
		print(Backup_Summary)


	os.chdir(str(windows_pwd))

		
	print()
	print("Closing Check for Off Box Backup")
	print(formatter)

except Exception as e:
	print(e)
	print("Error Checking for Off Box Backup")



#======================================================================================================================================================
#======================================================================================================================================================

# sm_diagpkg.json 

print("Beginning to parse sm-diagpkg.json")
print()
License_Allocation=int(Percentage_of_Licences_Allocated[0])



try:

	r=open('sm-diagpkg.json')
	f = json.load(r)
	counter=0
	text=""
	Norm_Ret_counter=0

	comp_name=str(f["companyName"])
	device_count=str(f["deviceCount"])

	print("Summary for: "+str(comp_name))
	print("Total Devices: "+str(device_count))
	print()
	print()
	print('Using ' +str(License_Allocation)+ '% allocation and greater to fire warning')
	for n in f['domains'][0]['licenseAllocations']:
		categoryName=n['categoryName']
		licenseTotal=n['licenseTotal']
		licenseUsed=n['licenseUsed']


		if licenseTotal!=0:


			print('License Type: '+str(categoryName))
			print('Total Available '+str(licenseTotal))
			utilization=licenseUsed/licenseTotal*100
			if utilization > License_Allocation:
				lic_max_util+=1
			print('Currently Used '+str(int(utilization))+ "%")
			print()

	if lic_max_util > 0:
		License_Summary= 'WARNING -- A License Allocation Over '+str(License_Allocation)+'% Threshold'
		print(License_Summary)
	else:
		License_Summary= 'PASS -- All License Allocations Under '+str(License_Allocation)+'% Threshold'
		print(License_Summary)
	print()


	for n in f['domains'][0]['devices']:
		revisionlist=[]
		counter+=1
		name=n['name']
		retrievalError=n['retrievalError']
		normalizationError=n['normalizationError']
		devicePack=n['devicePack']['version']
		for revision in n['revisionList']:
			id=revision['id']
			revisionlist.append(id)

		if normalizationError == 0 and retrievalError == 0:
			#text="There are no known retrieval or normalization errors for this device"
			pass
		else:

			if retrievalError != 0:
				Norm_Ret_counter+=1
				text="WARNING - There are RETRIEVAL errors for this device"
			if normalizationError != 0:
				Norm_Ret_counter+=1
				text="WARNING - There are NORMALIZATION errors for this device"
			if normalizationError > 0 and retrievalError > 0:
				Norm_Ret_counter+=1
				text="There are BOTH RETRIEVAL AND NORMALIZATION errors for this device"




			print('Device Name: '+str(name))
			print('Device Pack: '+str(devicePack))
			revisionlist.sort()
			print('Known revisions are: '+str(revisionlist))
			print(text)
			print()
	

	if Norm_Ret_counter > 0:
		Norm_Ret_Summary='WARNING -- NORMALIZATION / RETRIEVAL Errors Found (sm-diagpkg.json)'
		print(Norm_Ret_Summary)
	else:
		Norm_Ret_Summary='PASS -- No NORMALIZATION / RETRIEVAL Errors Found (sm-diagpkg.json)'
		print(Norm_Ret_Summary)



	print()
	print("Finishing parsing sm-diagpkg.json")
	
	print(formatter)

except Exception as e:
	print(e)
	print("Error parsing sm-diagpkg.json")
	print()
	print(formatter)


#======================================================================================================================================================
#======================================================================================================================================================

# SSL Certificates 

print("Checking Certificate Expiry Dates")
print()
days_till_expiry=int(Days_Until_Certificates_Expire[0])



try:

	for cert in certs:
		cert_name=cert.split('\\')[-1]
		if cert_name =='localhost.crt':
			display_name = 'Server (Apache / HTTPS)'
		elif cert_name =='fmos-root.crt':
			display_name = 'FMOS Ecosystem Root CA'
		elif cert_name =='fmos-admin.cer':
			display_name = 'FMOS Control Panel'

		with open(windows_pwd +cert, "r") as my_cert_file:
				my_cert_text = my_cert_file.read()
				cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, my_cert_text)



				exp_date=datetime.strptime(cert.get_notAfter().decode('ascii'), '%Y%m%d%H%M%SZ')
				#exp_date2=datetime.strptime(exp_date, '%Y-%m-%d')
				today=datetime.today().strftime('%Y-%m-%d')


				print(cert_name)
				print(display_name)
				print('Expires: '+str(exp_date))
				delta = exp_date - datetime.today()
				print('Days till expiry: '+str(delta.days))
				if days_till_expiry >= delta.days:
					warn_expire+=1
				print()



	if warn_expire > 0:
		Sumarry_Cert=('WARNING -- A Certificate Expires Soon')
		print(Sumarry_Cert)
		print()
	else:
		Sumarry_Cert=('PASS -- Certificate Expiry Date Not Soon')
		print(Sumarry_Cert)
		print()
		print()





except Exception as e:
	print(e)
	print("Error Checking Certificate Expiry Dates")
	print()
	print(formatter)

print("Closing Check for Certificate Expiry Dates")

print(formatter)

#======================================================================================================================================================
#======================================================================================================================================================

# Device Role

print("Checking for device Role")
print()
try:

	f = open(str(windows_pwd) +"\\etc\\firemon\\fm_roles")
	fm_role = f.readlines()


	if '0' in fm_role[0]  and '1' in fm_role[1] and '1' in fm_role[2] and '1' in fm_role[3] and '1' in fm_role[4]:
		device="AS and DB"
	elif '1' in fm_role[0]  and '0' in fm_role[1] and '0' in fm_role[2] and '0' in fm_role[3] and '0' in fm_role[4]:
		device="DC only"
	elif '0' in fm_role[0]  and '1' in fm_role[1] and '0' in fm_role[2] and '0' in fm_role[3] and '0' in fm_role[4]:
		device="AS only"
	elif '0' in fm_role[0]  and '0' in fm_role[1] and '1' in fm_role[2] and '0' in fm_role[3] and '0' in fm_role[4]:
		device="DB only"
	elif '1' in fm_role[0]  and '1' in fm_role[1] and '1' in fm_role[2] and '1' in fm_role[3] and '1' in fm_role[4]:
		device="All in One"


	print(device)
	

	print()
	print("Closing Check for device Role")
	print(formatter)

except Exception as e:
	print(e)
	print("Error Checking for for device Role")
	print()
	print(formatter)



#======================================================================================================================================================
#======================================================================================================================================================

# CPU INFO

print("Checking CPU's")
print()
try:

	f = open(str(windows_pwd) +"\\cpuinfo.txt")
	cpu_info = f.readlines()



	for line in cpu_info:
		if 'processor	: ' in line:
			cpu_count += 1

	cpuload=[['1',cpu_loadavg_1],['5',cpu_loadavg_5],['15',cpu_loadavg_15]]
	print(tabulate(cpuload, headers=['Time Mins', 'CPU Load Avg']))
	# print('Number of Processors: '+str(cpu_count))
	# print('CPU Load Average 1min: '+str(cpu_loadavg_1))
	# print('CPU Load Average 5min: '+str(cpu_loadavg_5))
	# print('CPU Load Average 15mins: '+str(cpu_loadavg_15))
	
	# cpu_info_xls=[cpu_count,cpu_loadavg_1,cpu_loadavg_5,cpu_loadavg_15]
	# print(cpu_info_xls)

	print()
	print("Closing Check of CPU's")
	print(formatter)

except Exception as e:
	print(e)
	print("Error Checking CPU's")
	print()
	print(formatter)

#======================================================================================================================================================
#======================================================================================================================================================

# temp-files.txt

print("Checking temp-files")
print()
try:

	f = open(str(windows_pwd) +"\\temp-files.txt")
	temp_files = f.readlines()



	for line in temp_files:
		if 'devpack_pylib' in line:
			temp_files_count += 1

	print('Number temp files: '+str(temp_files_count))

	file_size = os.path.getsize(str(windows_pwd) +"\\temp-files.txt")
	file_size_mb=file_size/1000000
	print("Folder Size is:", file_size_mb, "Mb")

	print()
	print("Closing Check for temp-files")
	print(formatter)

except Exception as e:
	print(e)
	print("Error Checking for temp-files")
	print()
	print(formatter)

#======================================================================================================================================================
#======================================================================================================================================================

# dc.conf

print("Checking dc.conf file")
print()
try:


	f = open(str(windows_pwd) +"\\etc\\firemon\\dc.conf")
	dc_conf = f.readlines()
	for line in dc_conf:
		if "--DataCollector.SyslogServer.ThreadNumberForProcessingMessages" in line:
			print(line)
			line=line.split(" ")[1]
			print(line)
			print("CPU's:")
			print(cpu_count)
			cpu_minus_one = cpu_count-1
			print("minus1: " +str(cpu_minus_one))
			if line != cpu_minus_one:
				print('warn')
		else:
			pass

	

	print()
	print("Closing Check of dc.conf file")
	print(formatter)

except Exception as e:
	print(e)
	print("Error Checking dc.conf file")
	print()
	print(formatter)

#======================================================================================================================================================
#======================================================================================================================================================

# Java heap size

print("Checking Java heap size")
print()
try:

	r=open(str(windows_pwd) +"\\etc\\firemon\\sm.jvm.options")
	s=open(str(windows_pwd) +"\\etc\\firemon\\wf.jvm.options")
	t=open(str(windows_pwd) +"\\etc\\firemon\\nd.jvm.options")

	
	sm = r.readlines()
	nd = s.readlines()
	wf = t.readlines()

	print('SM '+str(sm[3].split('mx')[1]))
	print('WF '+str(wf[3].split('mx')[1]))
	print('ND '+str(nd[3].split('mx')[1]))
	print()
	print("Closing Check for Java heap size")
	print(formatter)

except Exception as e:
	print(e)
	print("Error Checking Java heap size")
	print()
	print(formatter)

#======================================================================================================================================================
#======================================================================================================================================================

# Syslog information

# print("Checking for Off Box Backup")
# print()
# try:

# 	r=open('sm-diagpkg.json')

	

# 	print()
# 	print("Closing Check for Off Box Backup")
# 	print(formatter)

# except Exception as e:
# 	print(e)
# 	print("Error Checking for Off Box Backup")
# 	print()
# 	print(formatter)

#======================================================================================================================================================
#======================================================================================================================================================

# Syslog information

# print("Checking for Off Box Backup")
# print()
# try:

# 	r=open('sm-diagpkg.json')

	

# 	print()
# 	print("Closing Check for Off Box Backup")
# 	print(formatter)

# except Exception as e:
# 	print(e)
# 	print("Error Checking for Off Box Backup")
# 	print()
# 	print(formatter)

#======================================================================================================================================================
#======================================================================================================================================================

# Spacer

print()
print()
print()
print()
print()
print()
print()

#======================================================================================================================================================
#======================================================================================================================================================

# Summary Section


print(formatter)
Summary_LoggingFile.write(formatter +'\n')
print()


print("Summary Section")
Summary_LoggingFile.write("Summary Section")
print(formatter)
Summary_LoggingFile.write(formatter +'\n'+'\n' +'\n')
 
print()
print('General Info:')
Summary_LoggingFile.write('General Info:' +'\n' +'\n' )
print()

summary_list=[]
summary_list2=[]

# print("Customer: " + str(comp_name))
# summary_list.append("Customer: " + str(comp_name))
# Summary_LoggingFile.write("Customer: " + str(comp_name) +'\n')

print("Server Hostname: " + str(hostname))
summary_list.append("Server Hostname: " + str(hostname))
Summary_LoggingFile.write("Server hostname: " + str(hostname) +'\n')

print("FMOS Version: " + str(FMOSv))
summary_list.append("FMOS Version: " + str(FMOSv))
Summary_LoggingFile.write("FMOS Version: " + str(FMOSv) +'\n')

print("Server Role: "+str(device))
summary_list.append("Server Role: "+str(device))
Summary_LoggingFile.write('Server Role: '+str(device)+'\n')

print("Uptime: " + str(UpT))
summary_list.append("Uptime: " + str(UpT))
Summary_LoggingFile.write("Uptime: " + str(UpT)+'\n')

if Check_Installed_DPs =="N/A -- Device Packs Check not performed. No DC element to MKDIAG":
	pass
else:
	print("Devices found (deviceInventoryReport): " + str(int(Total_Devices)))
	Summary_LoggingFile.write("Devices found (deviceInventoryReport): " + str(int(Total_Devices))+'\n')

print("Devices found (sm_diagpkg): " + str(device_count))
Summary_LoggingFile.write("Devices found (sm_diagpkg): " + str(device_count) +'\n')

print("MKDIAG Created: " + str(mkdiag_created))
summary_list.append("MKDIAG Created: " + str(mkdiag_created))
Summary_LoggingFile.write("MKDIAG Created: " + str(mkdiag_created) +'\n')



print()
print(formatter)
Summary_LoggingFile.write(formatter +'\n')


#======================================================================================================================================================
#======================================================================================================================================================

# Writing Checks Carried Out
# 
print()
print('Checks carried out:')

Summary_LoggingFile.write('Checks carried out:' +'\n'+'\n')
print()

print(Check_Installed_DPs)
summary_list2.append(Check_Installed_DPs)
Summary_LoggingFile.write(Check_Installed_DPs+'\n')

print(Drops_Summary)
summary_list2.append(Drops_Summary)
Summary_LoggingFile.write(Drops_Summary+'\n')

print(Core_Summary)
summary_list2.append(Core_Summary)
Summary_LoggingFile.write(Core_Summary+'\n')

print(Backup_Summary)
summary_list2.append(Backup_Summary)
Summary_LoggingFile.write(Backup_Summary+'\n')

print(License_Summary)
summary_list2.append(License_Summary)
Summary_LoggingFile.write(License_Summary+'\n')

print(Norm_Ret_Summary)
summary_list2.append(Norm_Ret_Summary)
Summary_LoggingFile.write(Norm_Ret_Summary+'\n')

print(Sumarry_Cert)
summary_list2.append(Sumarry_Cert)
Summary_LoggingFile.write(Sumarry_Cert+'\n')

print(Summary_Dir_Check)
summary_list2.append(Summary_Dir_Check)
Summary_LoggingFile.write(Summary_Dir_Check+'\n')

print(Check_Device_Uptime)
summary_list2.append(Check_Device_Uptime)
Summary_LoggingFile.write(Check_Device_Uptime+'\n')



print(formatter)
Summary_LoggingFile.write(formatter +'\n'+'\n')
# 
# 
# 

print()

print()
print('Certificate Info:')

Summary_LoggingFile.write('Checks carried out:' +'\n'+'\n')
print()





print(formatter)
Summary_LoggingFile.write(formatter +'\n'+'\n')
# 
# 
# 

print()











#======================================================================================================================================================
#======================================================================================================================================================

# Writing to Excel

print("Writing to Excel: "+ str(hostname.split('.')[0])+'.xlsx')
print()
try:

	#for item in summary_list:
	for i, item in enumerate(summary_list):
		ws.cell(row=i+2, column=1).value = item
	print('General Info written successfully')

	for i, item in enumerate(summary_list2):
		ws.cell(row=i+3, column=3).value = item
	print('Checks carried out written successfully')

	for i, item in enumerate(cpu_info_xls):
		ws.cell(row=i+4, column=6).value = item
	print('CPU written successfully')



	print()
	print("Closing Writing to Excel")
	print(formatter)

except Exception as e:
	print(e)
	print("Error Writing to Excel")
	print()
	print(formatter)

#======================================================================================================================================================
#======================================================================================================================================================





print()

print()

wb.save(pwd + '\\script_output\\'+str(hostname.split('.')[0])+'.xlsx')
LoggingFile.close()
Summary_LoggingFile.close()

exit()

