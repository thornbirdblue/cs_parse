##########################################################################
#	CopyRight	(C)	VIVO,2021	All Rights Reserved!
#
#	Module:		Scan dumpsys media.camera txt file
#
#	File:		cs_parse.py
#
#	Author:		thornbird
#
#	Data:		2021-09-06
#
#	E-mail:		wwwthornbird@163.com
#
###########################################################################

###########################################################################
#
#	History:
#	Name		Data		Ver		Act
#--------------------------------------------------------------------------
#	thornbird	2015-07-23	v1.0		create
#
###########################################################################

#!/bin/python
import sys,os,re,string,time,datetime,xlwt

# save log record			!!! Save all log data !!!
logs = []

# log var
debugLog = 0
debugLogLevel=(0,1,2,3)	# 0:no log; 1:op logic; 2:op; 3:verbose

# save file name
fileName=''
ScanPath=''
SumTags=['FileName','Type']
SumTypes=['Least','Max','Avg']
file_col_width = 4500				# col width

class AppLogType:
	# app log pattern
	appLogType = r'.txt'

	# camera open start end end log
	# camera startPreview start and end log		!!! must a pair set
	CamKPITags = ('Open time(ms)','StartPreview(ms)','Sum time(ms)','Total time(ms)')
	CamLog = ('Dumping camera metadata array','Vendor Tags')
	CamLogPattern = (r'Dumping camera metadata array',r'com.\S.')

	logNames=[]
	
	logCnt = 0
	__path = ''
	__dir = ''
	__file = ''
	__record = []			### !!! 8 pair time record must to more than len(CamLog)!!!
	__CamLogList = []								### log time's array
	__CamTimeKPI = []								### every time kpi

	def __init__(self,path,dir,file):
		self.__path = path
		self.__dir = dir
		self.__file = file
		AppLogType.logCnt+=1
		self.__record = []
		self.__CamLogList  = []
		self.__CamTimeKPI = []
	

	def __ScanCamLog(self,fd):
		if debugLog >= debugLogLevel[2]:
			print 'INFO: begin scan camera log!'

		while 1:
			line = fd.readline()
			
			if not line:
				if debugLog >= debugLogLevel[2]:
					print 'INFO: Finish Parse file!\n'
				break;

			if debugLog >= debugLogLevel[-1]:
				print 'INFO: Read line is :'+line
	
			for i in range(0,len(AppLogType.CamLog)):							# Adapter every key tag
				if debugLog >= debugLogLevel[-1]:
					print 'INFO: Camera log-> '+AppLogType.CamLog[i]

				log = re.compile(AppLogType.CamLogPattern[i])
		
				if debugLog >= debugLogLevel[-1]:
					print 'INFO: Scan log-> '+log.pattern

				search = re.match(log,line)
				if search:
					if debugLog >= debugLogLevel[1]:
						print 'INFO: Search Camera log->'+search.group()
						print 'line is: '+line
					if 1 == i:	
						Format = re.compile(r'\d/\d entries, \d/\d bytes')
					else:
						Format = re.compile(r'com.\S.\S (\S):')

					
					if debugLog >= debugLogLevel[2]:
						print 'INFO: Format-> '+Format.pattern
					
					f = re.search(Format,line)
					if f:
						if debugLog >= debugLogLevel[2]:
							print 'INFO: Find key time-> '+f.group()

						# patch-> cal tag position and write to the right pos
						if debugLog >= debugLogLevel[1]:
							tags = search.group()
							print tags

						self.__record.append(f.group())

						
						if debugLog >= debugLogLevel[2]:
							print 'INFO: Time -> '+self.__record[i]

	def ScanCameraLog(self):
		if debugLog >= debugLogLevel[1]:
			print 'Parse file: '+os.path.join(self.__path,self.__file)
		try:
			fd = open(os.path.join(self.__path,self.__file),'rb')								# 2015-09-08 liuchangjian fix error code in file bug!!! change r to rb mode!
			
			if debugLog >= debugLogLevel[2]:
				print 'INFO: open file :'+os.path.join(self.__path,self.__file)

			self.__ScanCamLog(fd)

			fd.close()

		except IOError:
			print "open file ERROR: Can't open"+os.path.join(self.__path,self.__file)
			sys.exit()

	def GetName(self):
		return self.__file

	def GetCamLogList(self):
		if debugLog >= debugLogLevel[2]:
			print 'Cam Log list len: '+str(len(self.__CamLogList))

		return self.__CamLogList
		
	def GetCamTimeKPIIndex(self,index):
		if debugLog >= debugLogLevel[2]:
			print 'AppLogType Cam Time KPI index '+str(index)+' is : '+str(self.__CamTimeKPI[index])
		return self.__CamTimeKPI[index]
	
	def GetCamTimeKPI(self):
		if debugLog >= debugLogLevel[2]:
			print 'AppLogType Cam Time KPI : '
			print self.__CamTimeKPI
		return self.__CamTimeKPI
		
# Only exec in one adb_log directory!!! Can't have two adb_log dir
def ScanFiles(arg,dirname,files):
	if debugLog >= debugLogLevel[-1]:
		print dirname

	for file in files:
		logType = re.compile(AppLogType.appLogType)

		if debugLog >= debugLogLevel[-1]:
			print AppLogType.appLogType
			print file
		
		m = re.match(logType,file)
		if m:
			path,name = os.path.split(dirname)

			if debugLog >= debugLogLevel[2]:
				print '\nFound Dir: '+name
			
			log = AppLogType(dirname,name,file)
			logs.append(log)
			log.ScanCameraLog()

def OutPutData(xl,Ssheet,mlog,index):
	LogName = mlog.GetName()
	if debugLog >= debugLogLevel[2]:
		print "\nSave sheets: "
		print AppLogType.logNames

	if LogName in AppLogType.logNames:
		for i in range(1,99):
			if (LogName+'_'+str(i)) in AppLogType.logNames:
				continue
			else:
				LogName = LogName+'_'+str(i)
				if debugLog >= debugLogLevel[2]:
					print 'Rename sheet name to '+LogName
				AppLogType.logNames.append(LogName)
				sheet = xl.add_sheet(LogName)
				if debugLog >= debugLogLevel[1]:
					print "\nSave sheet: "+LogName
				break
	else:
		AppLogType.logNames.append(mlog.GetName())
		sheet = xl.add_sheet(mlog.GetName())
		if debugLog >= debugLogLevel[1]:
			print "\nSave sheet: "+mlog.GetName()

	# Ssheet save
	Ssheet.col(0).width = 9000
	Ssheet.write(index*3+1,0,mlog.GetName())

	Ssheet.col(2).width=file_col_width
	for i in range(0,len(SumTypes)):
		Ssheet.write(index*3+1+i,1,SumTypes[i])
	
	# sheet save	
	for i in range(0,len(AppLogType.CamLog)):
		sheet.col(i+1).width=file_col_width
		sheet.write(0,i+1,AppLogType.CamLog[i])

	for i in range(0,len(AppLogType.CamKPITags)):
		col_p=i+1+len(AppLogType.CamLog)+1
		sheet.col(col_p).width=3000
		sheet.write(0,col_p,AppLogType.CamKPITags[i])
	
	log = mlog.GetCamLogList()

	for i in range(0,len(log)):
		sheet.write(i+1,0,i+1)
		
	excel_date_fmt = 'MM-DD h:mm:ss.0'
	style = xlwt.XFStyle()
	style.num_format_str = excel_date_fmt
		
	for i in range(0,len(log)):
		data = log[i]
		
		if debugLog >= debugLogLevel[2]:
			print 'Group '+str(i+1)+' data len: '+str(len(data))
		
		for j in range(0,len(data)):
			if debugLog >= debugLogLevel[2]:
				print data[j]
			sheet.write(i+1,j+1,data[j],style)
	
		KPIIndexData = mlog.GetCamTimeKPIIndex(i)
	
		if debugLog >= debugLogLevel[2]:
			print 'KPI index data is '+str(KPIIndexData)
		
		if len(KPIIndexData) < len(AppLogType.CamKPITags):
			print 'ERROR: kpi data len '+str(len(KPIIndexData))+' is less than need('+str(len(AppLogType.CamKPITags))+')!!!'
			return
		else:
			for j in range(0,len(AppLogType.CamKPITags)):
				sheet.write(i+1,j+1+len(AppLogType.CamLog)+1,KPIIndexData[j])


	# Save min max avg data to SumSheet
	KPIData = mlog.GetCamTimeKPI()

	if debugLog >= debugLogLevel[1]:
		print 'KPI data is '+str(KPIData)

	s_col_pos = len(SumTags)
	
	if KPIData:
		for i in range(0,len(AppLogType.CamKPITags)):
			GroupList = [x[i] for x in KPIData]
		
			if debugLog >= debugLogLevel[1]:
				print 'Group data is '+str(GroupList)

			# remove 0 item
			GList = []
			for j in range(0,len(GroupList)):
				if GroupList[j] == 0:
					print 'WARNING: Remove List '+str(j)+'! Val is '+str(GroupList[j])
				# liuchangjian 2015-09-08 del else code! fix zero bug!
				GList.append(GroupList[j])				
		
			GList.sort()
		
			if debugLog >= debugLogLevel[2]:
				print 'Sort Group data is '+str(GList)

			Ssheet.write(index*3+1,s_col_pos+i,GList[0])
			Ssheet.write(index*3+1+1,s_col_pos+i,GList[-1])
			Ssheet.write(index*3+1+2,s_col_pos+i,sum(GList)/len(GList))
	else:
		print 'WARNing: There is no Camera log in '+LogName+' file!!!'


# Save data to excel
def SaveLogKPI():
	xlwb = xlwt.Workbook(encoding='utf-8')
	SumSheet = xlwb.add_sheet('Sum')

	for i in range(0,len(SumTags)):
		SumSheet.col(i).width=file_col_width
		SumSheet.write(0,i,SumTags[i])
	
	for i in range(0,len(AppLogType.CamKPITags)):
		col_p=len(SumTags)+i
		SumSheet.col(col_p).width=file_col_width
		SumSheet.write(0,col_p,AppLogType.CamKPITags[i])

	for mlog in logs:
		OutPutData(xlwb,SumSheet,mlog,logs.index(mlog))
	
	if fileName:
		xlwb.save(fileName+'.xls')	
	else:
		xlwb.save('cam_kpi_data.xls')	


def ParseArgv():
	if len(sys.argv) > appParaNum+1:
		CameraOpenKPIHelp()
		sys.exit()
	else:
		for i in range(1,len(sys.argv)):
			if sys.argv[i] == '-h':
				Usage()
				sys.exit()
			elif sys.argv[i] == '-d':
				if sys.argv[i+1]:
					debug = string.atoi(sys.argv[i+1],10)
					if type(debug) == int:
						global debugLog
						debugLog = debug						
						print 'Log level is: '+str(debugLog)
					else:
						print 'cmd para ERROR: '+sys.argv[i+1]+' is not int num!!!'
				else:
					CameraOpenKPIHelp()
					sys.exit()
			elif sys.argv[i] == '-o':
				if sys.argv[i+1]:
					global fileName
					fileName = sys.argv[i+1]
					print 'OutFileName is '+fileName
				else:
					Usage()
					sys.exit()
			elif sys.argv[i] == '-p':
				if sys.argv[i+1]:
					global ScanPath
					ScanPath = sys.argv[i+1]
					print 'Scan dir path is '+ScanPath
				else:
					Usage()
					sys.exit()
					

def Usage():
	print 'Command Format :'
	print '		cs_parse [-d 1/2/3] [-o outputfile] [-p path] | [-h]'

appParaNum = 6

if __name__ == '__main__':
	ParseArgv()

	print ScanPath.strip()
	if not ScanPath.strip():
		spath = os.getcwd()
	else:
		spath = ScanPath
	
	print 'Scan DIR: '+spath+'\n'

	os.path.walk(spath,ScanFiles,())
	print 'Total Parse file num: '+str(AppLogType.logCnt)

	if AppLogType.logCnt:
		SaveLogKPI()
