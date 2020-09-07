import requests
from concurrent.futures import ThreadPoolExecutor

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"}

ori_url="http://book.ucdrs.superlib.net/search?sw=9787108020987"
def ssj(proxy_url,url):
	proxies={"http":f"{proxy_url}",}
			# "https":f"{proxy_url}",}
	page=requests.get(url,headers=headers,proxies=proxies).status_code
	print(page)

def main():
	urls=[ori_url]*100
	thread_pool=ThreadPoolExecutor(max_workers=256)
	for url in urls:
		future=thread_pool.submit(ssj,"http://49.4.67.31:3128",url)
	thread_pool.shutdown(wait=False)
	print("done.")

main()