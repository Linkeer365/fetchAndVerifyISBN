import requests
from lxml import etree
import os
# from concurrent.futures import ThreadPoolExecutor
import telnetlib
import time

target_dir=r"D:\fetch_IPs"

# 因为访问的是豆瓣所以只用中国的ip

url_template="https://www.kuaidaili.com/free/inha/{}/"

# check_url="http://book.ucdrs.superlib.net/search?sw=9787108020987"
# check_url="https://www.douban.com/"
check_url="https://douban.com/isbn/7101003044/"

headers = {
        "User-Agent": "Mozilla/5.0 (Linux; U; Android 10; zh-cn; GM1900 Build/QKQ1.190716.003) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/10.1 Mobile Safari/537.36"}

# proxy_url="http://114.103.20.118:4216"
# proxies={"http":f"{proxy_url}","https":f"{proxy_url}",}

def fetch_one_page(page_num):
	url=f"https://www.kuaidaili.com/free/inha/{page_num}/"
	# page_text=requests.get(url,headers=headers,proxies=proxies).text
	page_text=requests.get(url,headers=headers).text
	html=etree.HTML(page_text)
	ip_finds=html.xpath("//td[@data-title='IP']//text()")
	port_finds=html.xpath("//td[@data-title='PORT']//text()")
	# print(finds)
	# sys.exit(0)
	assert ip_finds!=[]
	assert port_finds!=[]
	finds=[f"http://{ip}:{port}" for ip,port in zip(ip_finds,port_finds)]
	finds_s="\n".join(finds)
	print(finds)
	finds_s="\n".join(finds)
	with open(f"{target_dir}{os.sep}uncheckIPs_{page_num}.txt","w",encoding="utf-8") as f:
		f.write(finds_s+"\n")
	print(f"{page_num} page done.")

def merge_pages(same_head="uncheckIPs_",max_num=3622):
	lines=[]
	for each in os.listdir(target_dir):
		if each.startswith(same_head) and each.endswith(".txt"):
			with open(f"{target_dir}{os.sep}{each}","r",encoding="utf-8") as f:
				lines.extend(f.readlines())
	print(f"Lines:{lines}")
	try:
		lines_s="\n".join(lines)
	except TypeError:
		lines=lines[0]
		lines_s="\n".join(lines)
	with open(f"{target_dir}{os.sep}uncheckIPs_merged.txt","w",encoding="utf-8") as f:
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
			res_code=requests.get(f"{check_url}",headers=headers,proxies=proxies,timeout=5).status_code
			if res_code==200:
				grade+=1
		except:
			# print(f"{some_url} is bad!")
			pass
		cnt+=1
		res_code=0
	return grade>=max_grades*0.6



def fetch_useful(uncheckIPs):
	useful_ips=[]
	for each_ip in uncheckIPs:
		each_ip=each_ip.strip("\n")
		if isUseful(each_ip):
			print(f"{each_ip} is checked good!")
			useful_ips.append(each_ip)
		else:
			print(f"{each_ip} is bad!")
	if useful_ips:
		useful_ips_s="\n".join(useful_ips)
		with open(f"{target_dir}{os.sep}checkedIPs_kuaidaili.txt","w",encoding="utf-8") as f:
			f.write(useful_ips_s)
		print("Useful Ips fetched.")
	else:
		print("All failed.")



def main():
	# thread_pool=ThreadPoolExecutor(max_workers=128)
	# 最大值是3622
	max_num=3622
	for each_num in range(1,max_num):
		fetch_one_page(each_num)
		time.sleep(1)
		# future=thread_pool.submit(fetch_one_page,each_num)
	# thread_pool.shutdown(wait=True)
	uncheck_ips=merge_pages()
	fetch_useful(uncheck_ips)
	print("All down.")

# merge_pages()
if __name__=="__main__":
	main()
