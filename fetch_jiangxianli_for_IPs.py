import requests
from lxml import etree
import os
# from concurrent.futures import ThreadPoolExecutor
import telnetlib
import time

target_dir=r"D:\fetch_IPs"

# 因为访问的是豆瓣所以只用中国的ip

url_template="https://ip.jiangxianli.com/?page={}&country=中国"

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"}



def fetch_one_page(page_num):
	url=f"https://ip.jiangxianli.com/?page={page_num}&country=中国"
	page_text=requests.get(url,headers=headers).text
	html=etree.HTML(page_text)
	finds=html.xpath("//button[@class='layui-btn layui-btn-sm btn-copy']//@data-url")
	assert finds!=[]
	finds_s="\n".join(finds)
	with open(f"{target_dir}{os.sep}uncheckIPs_{page_num}.txt","a",encoding="utf-8") as f:
		f.write(finds_s+"\n")
	print(f"{page_num} page done.")

def merge_pages(same_head="uncheckIPs_",max_num=7):
	lines=[]
	for each in os.listdir(target_dir):
		if each.startswith(same_head) and each.endswith(".txt"):
			with open(f"{target_dir}{os.sep}{each}","r",encoding="utf-8") as f:
				lines.append(f.readlines())
	print(f"Lines:{lines}")
	try:
		lines_s="\n".join(lines)
	except TypeError:
		lines=lines[0]
		lines_s="\n".join(lines)
	with open(f"{target_dir}{os.sep}uncheckIPs_merged.txt","a",encoding="utf-8") as f:
		f.write(lines_s)
	print("All Page Merged.")
	return lines

def isUseful(some_url):
	proxies={"https":f"{some_url}",
			 "http":f"{some_url}"}
	max_grades=10
	cnt=0
	res_code=0
	grade=0
	# 至少达到7分
	while cnt<=9:
		try:
			res_code=requests.get("https://www.douban.com/",headers=headers,proxies=proxies,timeout=5).status_code
			if res_code==200:
				grade+=1
		except:
			pass
		cnt+=1
		res_code=0
	return grade>=max_grades*0.7



def fetch_useful(uncheckIPs):
	useful_ips=[]
	for each_ip in uncheckIPs:
		each_ip=each_ip.strip("\n")
		if isUseful(each_ip):
			print(f"{each_ip} is checked good!")
			useful_ips.append(each_ip)
	useful_ips_s="\n".join(useful_ips)
	with open(f"{target_dir}{os.sep}checkedIPs.txt","a",encoding="utf-8") as f:
		f.write(useful_ips_s)
	print("Useful Ips fetched.")



def main():
	# thread_pool=ThreadPoolExecutor(max_workers=128)
	for each_num in range(1,8):
		fetch_one_page(each_num)
		time.sleep(1)
		# future=thread_pool.submit(fetch_one_page,each_num)
	# thread_pool.shutdown(wait=True)
	uncheck_ips=merge_pages()
	fetch_useful(uncheck_ips)
	print("All down.")

if __name__=="__main__":
	main()
