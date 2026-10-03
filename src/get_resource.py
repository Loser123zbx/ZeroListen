import requests
from contextlib import closing
import zipfile

#文件下载器
def Down_load(file_url,file_path):
        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}
        with closing(requests.get(file_url,headers=headers,stream=True)) as response:
                chunk_size = 1024  # 单次请求最大值
                content_size = int(response.headers['content-length'])  # 内容体总大小
                data_count = 0
                with open(file_path, "wb") as file:
                        for data in response.iter_content(chunk_size=chunk_size):
                                file.write(data)
                                data_count = data_count + len(data)
                                now_jd = (data_count / content_size) * 100
                                print("\r 文件下载进度：%d%%(%d/%d) - %s" % (now_jd, data_count, content_size, file_path), end=" ")

def unzip_file(zip_path, extract_to):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)

def run_command(command):
        import subprocess
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stdout.decode(), stderr.decode(
        )


 
if __name__ == '__main__':
        headers = {
                "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        }
        file_url = "https://mirrors.aliyun.com/python-release/windows/python-3.11.4-embed-amd64.zip" #文件链接
        file_path = "D:\\python-3.11.4-embed-amd64.zip"   #文件路径
        Down_load(file_url,file_path)
        unzip_file(file_path, "D:\\python-3.11.4-embed-amd64")