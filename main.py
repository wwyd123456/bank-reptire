import subprocess
import sys
from keyToName import key2Name
if len(sys.argv) <= 1: print("未传递参数")
date = sys.argv[1]
if "-" not in date:
    date = date[0:4] + "-" + date[4:6] + "-" + date[6:]
code = sys.argv[2]
name = key2Name[code]
# 定义要执行的Shell命令
command = "scrapy crawl chinabank -a date=%s -a name=%s --nolog"%(date,name)
try:
    # 调用subprocess.run()函数执行Shell命令并获取输出结果
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        
        # 打印输出结果
        print(result.stdout)
    else:
        print("脚本执行失败！错误信息如下：")
        print(result.stderr)
except Exception as e:
    print("发生了未知错误：", str(e))