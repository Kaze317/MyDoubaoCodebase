import subprocess
A_path = "./download.exe"
B_path = "./backfill.exe"

print("正在运行文件download.exe")
subprocess.run(A_path,check=True)
print("文件download.exe运行完成")

print("正在运行文件backfill.exe")
subprocess.run(B_path,check=True)
print("文件backfill.exe运行完成")