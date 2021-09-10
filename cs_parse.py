#!/usr/bin/env python
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

import sys,os,re,string,time,datetime,xlwt

# save log record			!!! Save all log data !!!
logs = []

# log var
debugLog = 0
debugLogLevel=(0,1,2,3)	# 0:no log; 1:op logic; 2:op; 3:verbose

ScanFile=''

# save file name
fileName=''
ScanPath=''
file_col_width = 4500				# col width

class AppLogType:
	# app log pattern
	appLogType = r'.txt'

	# camera open start end end log
	# camera startPreview start and end log		!!! must a pair set
	CamLog = ('ids','device','hal_device','meta_array','meta','vendor_tags','error_traces')
	
	logNames=[]
	
	logCnt = 0
	__path = ''
	__dir = ''
	__file = ''

	__numCam = 0
	__ids=[]
	__infos={}

	__tagLogs={'ids':'Number of camera devices: (\d+)','device':'== Camera device (\d+)','hal_device':'== Camera HAL device device@\d\.\d/legacy/(\d)','meta_array':'Dumping camera metadata array: \d+ / (\d+) entries, \d+ / (\d+) bytes of extra data.','meta':'(\w+\.\S+) \(\d+\):','vendor_tags':'0x\d+ \((\S+)\) with','error_traces':'== Camera error traces'}

	__stat= 0
	__curId= -1
	
	__metaEntries = 0
	__metaExtra = 0
	__dynMeta=[]
	__staMeta=[]
	__idsDyn={}
	__idsSta={}
	__vendorTags=[]

	def __init__(self,path,d,f):
		self.__path = path
		self.__dir = d
		self.__file = f
		AppLogType.logCnt+=1

	def __resetMeta(self):
		if self.__stat == 1:
			self.__dynMeta.clear()
		elif self.__stat == 2:
			self.__staMeta.clear()

	def __saveData(self):
		data = []
		
		if self.__stat == 1:
			data = self.__dynMeta
			if data:
				self.__idsDyn[self.__curId] = self.__dynMeta.copy()
		elif self.__stat == 2:
			data = self.__staMeta
			if data:
				self.__idsSta[self.__curId] = self.__staMeta.copy()
		
		if debugLog >= debugLogLevel[1] and data:
			print( 'INFO Save id %s Data: '%str(self.__curId))
			print( data)

		self.__resetMeta()
	
	def __saveMetaNum(self,entries,extra):
		if self.__stat == 1:
			self.__dynMeta.append(entries)
			self.__dynMeta.append(extra)
		elif self.__stat == 2:
			self.__staMeta.append(entries)
			self.__staMeta.append(extra)
	
	def __saveMeta(self,stat,tag):
		if self.__stat == 1:
			self.__dynMeta.append(tag)
		elif self.__stat == 2:
			self.__staMeta.append(tag)
		
		if debugLog >= debugLogLevel[2]:
			print( 'INFO Save Meta: '+str(tag))
	
	def __saveVendorTags(self,tag):
		self.__vendorTags.append(tag)

		if debugLog >= debugLogLevel[2]:
			print( 'INFO Save Vendor Tag: '+str(tag))

	def __saveInfo(self,tag,search):
		if tag == AppLogType.CamLog[0]:
			self.__numCam = search.group(1)

			if debugLog >= debugLogLevel[1]:
				print( 'INFO Cam nums: '+str(self.__numCam))
		elif tag == AppLogType.CamLog[1]:
			self.__stat = 1

			if self.__curId != -1:
				self.__saveData()

			self.__curId = search.group(1)

			self.__ids.append(self.__curId)					# Save cam ids!!!	

			if debugLog >= debugLogLevel[2]:
				print( 'INFO Cur Id: '+str(self.__curId))

		elif tag == AppLogType.CamLog[2]:
			if self.__curId != -1:
				self.__saveData()
			
			self.__stat = 2
			self.__curId = search.group(1)
			
			if debugLog >= debugLogLevel[2]:
				print( 'INFO Cur Id: '+str(self.__curId))

		elif tag == AppLogType.CamLog[3]:
			if debugLog >= debugLogLevel[2]:
				print( 'INFO metadata array: '+search.group())
			
			self.__saveMetaNum(search.group(1),search.group(2))
		elif tag == AppLogType.CamLog[4]:
			self.__saveMeta(self.__stat,search.group(1))
		elif tag == AppLogType.CamLog[5]:
			self.__saveVendorTags(search.group(1))



	def __ScanCamLog(self,fd):
		if debugLog >= debugLogLevel[2]:
			print( 'INFO: begin scan camera log!')

		while 1:
			line = fd.readline()
			
			if not line:
				self.__saveData()
				if debugLog >= debugLogLevel[1]:
					print( 'INFO: Finish Parse file!\n')
				break;

			line = str(line)

			if debugLog >= debugLogLevel[-1]:
				print( 'INFO: Read line is :',line)
	
			for i in range(0,len(AppLogType.CamLog)):							# Adapter every key tag
				if debugLog >= debugLogLevel[-1]:
					print( 'INFO: Camera log-> '+AppLogType.CamLog[i])

				log = re.compile(self.__tagLogs[AppLogType.CamLog[i]])
		
				if debugLog >= debugLogLevel[-1]:
					print( 'INFO: Scan log-> '+log.pattern)

				search = re.search(log,line)
				if search:
					if AppLogType.CamLog[i] == AppLogType.CamLog[-1]:
						self.__saveData()
						print( 'INFO Finish Scan: '+line)
						break;

					if debugLog >= debugLogLevel[2]:
						print( 'INFO: Search: '+search.group())
					
					if debugLog >= debugLogLevel[-1]:
						print( 'Find line is: '+line)
				
					self.__saveInfo(AppLogType.CamLog[i],search)	
	
	def ScanCameraLog(self):
		if debugLog >= debugLogLevel[1]:
			print( 'Parse file: '+os.path.join(self.__path,self.__file))
		try:
			fd = open(os.path.join(self.__path,self.__file),'rb')								# 2015-09-08 liuchangjian fix error code in file bug!!! change r to rb mode!
			
			if debugLog >= debugLogLevel[2]:
				print( 'INFO: open file :'+os.path.join(self.__path,self.__file))

			self.__ScanCamLog(fd)

			fd.close()

		except IOError:
			print( "open file ERROR: Can't open"+os.path.join(self.__path,self.__file))
			sys.exit()

	def GetName(self):
		return self.__file

	def GetIds(self):
		if debugLog >= debugLogLevel[1]:
			print('Ids: ',self.__ids)
		return self.__ids

	def GetVendorTags(self):
		if debugLog >= debugLogLevel[1]:
			print('Ids: ',self.__vendorTags)
		return self.__vendorTags

	def GetCamLogList(self,id = '0'):
		data = []
		if id in self.__idsDyn:
			data.append(self.__idsDyn[id])
		if id in self.__idsSta:
			data.append(self.__idsSta[id])
	
		if debugLog >= debugLogLevel[1] and data:
			print(data)

		return data	
		

def runScan(dirname,name,f):
	log = AppLogType(dirname,name,f)
	logs.append(log)
	log.ScanCameraLog()
	
# Only exec in one adb_log directory!!! Can't have two adb_log dir
def ScanFiles(arg,dirname,files):
	if debugLog >= debugLogLevel[-1]:
		print( dirname)

	for file in files:
		logType = re.compile(AppLogType.appLogType)

		if debugLog >= debugLogLevel[-1]:
			print( AppLogType.appLogType)
			print( file)
		
		m = re.match(logType,file)
		if m:
			path,name = os.path.split(dirname)

			if debugLog >= debugLogLevel[2]:
				print( '\nFound Dir: '+name)
			
			runScan(dirname,name,file)

def SheetSaveVendorTags(mlog,xl):
	log = mlog.GetVendorTags()

	if log:
		sheet = xl.add_sheet('VendorTags')


	for i in range(0,len(log)):
		data = log[i]

		if debugLog >= debugLogLevel[2]:
			print( ' Data: '+str(data))

		sheet.write(i,0,data)

def SheetSave(mlog,xl,id):
	log = mlog.GetCamLogList(id)

	if log:
		sheet = xl.add_sheet(id)


	for i in range(0,len(log)):
		data = log[i]

		if debugLog >= debugLogLevel[2]:
			print( 'Group '+str(i+1)+' data len: '+str(len(data)))

		for j in range(0,len(data)):
			if debugLog >= debugLogLevel[2]:
				print( data[j])
			
			sheet.write(j,i+1,data[j])

def OutPutData(xl,mlog,index):
	LogName = mlog.GetName()
	if debugLog >= debugLogLevel[2]:
		print( "\nSave sheets: ")
		print( AppLogType.logNames)

	if LogName in AppLogType.logNames:
		for i in range(1,99):
			if (LogName+'_'+str(i)) in AppLogType.logNames:
				continue
			else:
				LogName = LogName+'_'+str(i)
				if debugLog >= debugLogLevel[2]:
					print( 'Rename sheet name to '+LogName)
				AppLogType.logNames.append(LogName)
				sheet = xl.add_sheet(LogName)
				if debugLog >= debugLogLevel[1]:
					print( "\nSave sheet: "+LogName)
				break
	else:
		AppLogType.logNames.append(mlog.GetName())
		sheet = xl.add_sheet(mlog.GetName())
		if debugLog >= debugLogLevel[1]:
			print( "\nSave sheet: "+mlog.GetName())

	# sheet save	
	#sheet.col(i+1).width=file_col_width

	
	ids = mlog.GetIds()

	for i in ids:
		SheetSave(mlog,xl,i)
	
	SheetSaveVendorTags(mlog,xl)
		
def SaveLog():
	xlwb = xlwt.Workbook(encoding='utf-8')
	
	for mlog in logs:
		OutPutData(xlwb,mlog,logs.index(mlog))
	
	if fileName:
		xlwb.save(fileName+'.xls')	
	else:
		xlwb.save('cam_data.xls')	


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
					debug = int(sys.argv[i+1])
					if type(debug) == int:
						global debugLog
						debugLog = debug						
						print( 'Log level is: '+str(debugLog))
					else:
						print( 'cmd para ERROR: '+sys.argv[i+1]+' is not int num!!!')
				else:
					CameraOpenKPIHelp()
					sys.exit()
			elif sys.argv[i] == '-o':
				if sys.argv[i+1]:
					global fileName
					fileName = sys.argv[i+1]
					print( 'OutFileName is '+fileName)
				else:
					Usage()
					sys.exit()
			elif sys.argv[i] == '-p':
				if sys.argv[i+1]:
					global ScanPath
					ScanPath = sys.argv[i+1]
					print( 'Scan dir path is '+ScanPath)
				else:
					Usage()
					sys.exit()
			else:
				global ScanFile
				ScanFile = sys.argv[i]
				print( 'Scan file is '+ScanFile)

					

def Usage():
	print( 'Command Format :')
	print( '		cs_parse [-d 1/2/3] [-o outputfile] [-p path] | [-h]')

appParaNum = 6

if __name__ == '__main__':
	ParseArgv()

	print( ScanPath.strip())
	if not ScanPath.strip():
		spath = os.getcwd()
	else:
		spath = ScanPath
	
	print( 'Scan DIR: '+spath+'\n')
	
	if ScanFile:
		runScan(spath,spath,ScanFile)
	else:
		os.path.walk(spath,ScanFiles,())
		print( 'Total Parse file num: '+str(AppLogType.logCnt))

	if AppLogType.logCnt:
		SaveLog()
