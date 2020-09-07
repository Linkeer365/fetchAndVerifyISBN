import requests

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"}

url="http://douban.com/isbn/7101003044/"
def ssj(proxy_url):
	proxies={"http":f"{proxy_url}",}
			# "https":f"{proxy_url}",}
	page=requests.get(url,headers=headers,proxies=proxies).status_code
	print(page)
ssj("http://49.4.67.31:3128")