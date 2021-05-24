import numpy
import pandas as pd
import os
import requests
from lxml import etree
import time
from concurrent.futures import ThreadPoolExecutor
import sys

import random

# proxy_url="http://58.220.95.54:9400"

# proxies={"http":f"{proxy_url}",
#          "https":f"{proxy_url}",}


# 使用更快的f-strings
# https://blog.csdn.net/sunxb10/article/details/81036693

proxy_path=r"D:\fetch_IPs\checkedIPs.txt"

xls_path=r"D:\fetchAndVerifyISBN\publisher_identifiers.xlsx"

same_head="9787"

target_dir=r"D:\All_isbns"

douban_url_template="https://book.douban.com/isbn/{}/"

ucdrs_url_template="http://book.ucdrs.superlib.net/search?sw={}"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"}

# proxy_list=[]
# with open(proxy_path,"r",encoding="utf-8") as f:
#     proxy_list=[each.strip("\n") for each in f.readlines() if "http" in each]
# print(f"Proxy List:{proxy_list}")
# assert proxy_list!=[]


def get_check_digit(initpart):
    # https://wenku.baidu.com/view/b03803a59c3143323968011ca300a6c30c22f1cd.html
    if isinstance(initpart, int):
        initpart = str(initpart)
    assert len(initpart) == 12
    odd_place_digits = [int(val) for idx, val in enumerate(initpart, 1) if idx % 2 == 1]
    even_place_digits = [int(val) for idx, val in enumerate(initpart, 1) if idx % 2 == 0]
    weighted_sum = sum(odd_place_digits) * 1 + sum(even_place_digits) * 3
    # print("Weg Sum",weighted_sum)
    modOf10 = divmod(weighted_sum, 10)[1]
    check_digit = 10 - modOf10
    assert 0 <= check_digit <= 10
    # 强行归零
    if check_digit==10:
        check_digit=0
    return str(check_digit)


def get_titleIdentifier_len(publisherIdentifier):
    # https://baike.baidu.com/item/%E5%9B%BD%E9%99%85%E6%A0%87%E5%87%86%E4%B9%A6%E5%8F%B7/3271472?fromtitle=ISBN&fromid=391662&fr=aladdin
    maxlen = 8  # 13-4-1
    if isinstance(publisherIdentifier, int):
        publisherIdentifier = str(publisherIdentifier)
    titleIdentifier_len = maxlen - len(publisherIdentifier)
    assert 1 <= titleIdentifier_len <= maxlen
    return titleIdentifier_len

def get_full_ti_str(num,maxlen):
    if isinstance(num,int):
        num=str(num)
    full_str=num.zfill(maxlen)
    assert len(full_str)==maxlen
    return full_str

def is_collected_by_douban_fullstr(full_str):
    assert len(full_str)==13
    idx=0
    # rand_int=random.randint(0,len(proxy_list)-1)
    while idx<=len(proxy_list)-1:
        proxy_url=proxy_list[idx]
        proxies={   "http":f"{proxy_url}",
                    "https":f"{proxy_url}",}
        not_collected_str="豆瓣评论暂时没有收录此书，请原谅。"
        douban_url=douban_url_template.format(full_str)
        try:
            r=requests.get(douban_url,headers=headers,proxies=proxies)
            page_text=r.text
        except:
            idx+=1
            print(f"{proxy_url}有问题，更新为第{idx}个!")
            pass
    time.sleep(random.randint(1,3))
    html=etree.HTML(page_text)
    find=html.xpath("//li[starts-with(@style,'list-style-type:none;')]//text()")
    if find and find[0]==not_collected_str:
        print("Not Collected!")
        return False
    elif not find:
        print("Collected!")
        return True

def is_collected_by_douban_fullstr2(full_str):
    assert len(full_str)==13
    idx=0
    # rand_int=random.randint(0,len(proxy_list)-1)
    not_collected_str="豆瓣评论暂时没有收录此书，请原谅。"
    douban_url=douban_url_template.format(full_str)
    r=requests.get(douban_url,headers=headers)
    time.sleep(5)
    page_text=r.text
    html=etree.HTML(page_text)
    find=html.xpath("//li[starts-with(@style,'list-style-type:none;')]//text()")
    if find and find[0]==not_collected_str:
        print("Not Collected!")
        return False
    elif not find:
        print("Collected!")
        return True

def is_collected_by_ucdrs_fullstr2(full_str):
    assert len(full_str)==13
    idx=0
    # rand_int=random.randint(0,len(proxy_list)-1)
    not_collected_str="抱歉"
    ucdrs_url=ucdrs_url_template.format(full_str)

    print("ucdrs_url:",ucdrs_url)

    r=requests.get(ucdrs_url,headers=headers)
    time.sleep(1)
    page_text=r.text
    html=etree.HTML(page_text)
    find=html.xpath("//div[starts-with(@style,'font-size:13px; line-height:24px;')]")
    print("find:",find)
    if find:
        print("Not Collected!")
        return False
    elif not find:
        print("Collected!")
        return True

def is_collected_by_ucdrs_fullstr(full_str):
    assert len(full_str)==13
    idx=0
    # rand_int=random.randint(0,len(proxy_list)-1)
    while idx<=len(proxy_list)-1:
        proxy_url=proxy_list[idx]
        proxies={   "http":f"{proxy_url}",
                    "https":f"{proxy_url}",}
        # not_collected_str="豆瓣评论暂时没有收录此书，请原谅。"
        ucdrs_url=ucdrs_url_template.format(full_str)
        try:
            r=requests.get(ucdrs_url,headers=headers,proxies=proxies)
            page_text=r.text
        except:
            idx+=1
            print(f"{proxy_url}有问题，更新为第{idx}个!")
            pass
    time.sleep(random.randint(1,3))
    html=etree.HTML(page_text)
    find=html.xpath("//div[starts-with(@style,'font-size:13px; line-height:24px;')]")

    if find:
        print("Not Collected!")
        return False
    elif not find:
        print("Collected!")
        return True

def single(some_pi,some_publisher,some_num,ti_len,target_dir2):
    start_time=time.time()
    full_ti_str = get_full_ti_str(some_num, ti_len)
    init_part = f"{same_head}{some_pi}{full_ti_str}"
    check_digit = get_check_digit(init_part)
    full_str = f"{init_part}{check_digit}"
    # print("Full Str:", full_str)
    # if is_collected_by_douban_fullstr2(full_str):
    if is_collected_by_ucdrs_fullstr2(full_str):
        isbn = full_str
        print("Collected ISBN:", full_str)
        with open(f"{target_dir2}{os.sep}{isbn}.txt", "a", encoding="utf-8") as f:
            f.write(isbn+"\n")
        # with open(f"{target_dir2}{os.sep}already_num.txt","a",encoding="utf-8") as g:
        #     g.write(some_num+"\n")
    end_time=time.time()
    time_cost=end_time-start_time
    print(f"one file done. Time Cost:{time_cost}")

# def single2(some_pi,some_publisher,startAtVal=0):
#     # pi_isbns = []
#     ti_len = get_titleIdentifier_len(some_pi)
#     target_dir2 = f"{target_dir}{os.sep}{some_publisher}"
#     for each_num in range(startAtVal, 10 ** ti_len):
#         full_ti_str = get_full_ti_str(each_num, ti_len)
#         init_part = f"{same_head}{some_pi}{full_ti_str}"
#         check_digit = get_check_digit(init_part)
#         full_str = f"{init_part}{check_digit}"
#         print("Full Str:", full_str)
#         if is_collected_by_douban_fullstr(full_str):
#             isbn = full_str
#             with open(f"{target_dir2}{os.sep}{some_publisher}-{some_pi}.txt", "a", encoding="utf-8") as f:
#                 f.write(isbn+"\n")
#         # pi_isbns.append(isbn)
#     if not os.path.exists(target_dir2):
#         # 指明是文件夹
#         os.makedirs(target_dir2)

#     print("one done.")

# 多线程之后，估计就不会按照顺序了所以这里要改一下...
def get_start_val(some_target_dir,some_ti_len):
    some_target_dir+=os.sep
    if len(os.listdir(some_target_dir))==0:
        return 0
    else:
        dir_list=[each for each in os.listdir(some_target_dir) if (each[:-4]).isdigit()]
        sorted_dir=sorted(dir_list,key=lambda x:int(x[:-4]))
        print(sorted_dir)
        last_name=(sorted_dir[-1])[:-4]
        # 因为你最终肯定还是等于ti_len的嘛
        last_num=int(last_name[-1-some_ti_len:-1])
        start_val=last_num
        return start_val

def get_nums(some_target_dir,some_ti_len):
    some_target_dir+=os.sep
    full_nums=list(range(0,10**some_ti_len))
    if len(os.listdir(some_target_dir))==0:
        return full_nums
    else:
        old_nums=[int((each[:-4])[-1-some_ti_len:-1]) for each in os.listdir(some_target_dir) if (each[:-4]).isdigit()]
        nums=[each for each in full_nums if not each in old_nums]
        return nums


def main():
    df=pd.read_excel(xls_path,names=None,usecols=[0,3],dtype=str) # 1 base
    vals=df.values.tolist()
    for each in vals:
        if isinstance(each[0],str):
            print(each)
    # sys.exit(0)
    # nan, nan 是浮点数，不能用!=nan去筛选！！
    publishers=list(reversed([val[0] for val in vals if isinstance(val[0],str)]))
    publisher_identifiers=list(reversed([val[1] for val in vals if isinstance(val[1],str)]))

    # log_path=f"{target_dir}{os.sep}checker.txt"
    # if os.path.exists(log_path):
    #     with open(log_path,"r",encoding="utf-8") as f:
    #         startAtVal=int(f.readlines()[-1].replace("\n",""))
    # startAtVal=0
    #
    pip_dict=dict(zip(publisher_identifiers,publishers))
    completed_set=set()
    if os.path.exists(f"{target_dir}{os.sep}already_dir.txt"):
        with open(f"{target_dir}{os.sep}already_dir.txt","r",encoding="utf-8") as f:
            completed_set=set(f.readlines())
    # print("Complete Set:",completed_set)
    for each_pi,each_publisher in pip_dict.items():
        target_dir2 = f"{target_dir}{os.sep}{each_publisher}"
        if not os.path.exists(target_dir2):
            # 指明是文件夹
            os.makedirs(target_dir2)
        if each_publisher+"\n" in completed_set:
            print(f"{each_publisher} is Already!")
            continue
        ti_len=get_titleIdentifier_len(each_pi)
        # 这样就能有记忆力了
        # startAtVal=get_start_val(target_dir2,ti_len)

        nums=get_nums(target_dir2,ti_len)

        # if os.path.exists(f"{target_dir2}{os.sep}already_num.txt"):
        #     with open(f"{target_dir2}{os.sep}already_num.txt","r",encoding="utf-8") as h:
        #         startAtVal=int(h.readlines()[-1].replace("\n",""))
        # thread_pool=ThreadPoolExecutor(max_workers=1)
        # for each_num in range(startAtVal,10 ** ti_len):
        for each_num in nums:
            single(each_pi,each_publisher,each_num,ti_len,target_dir2)
            # future=thread_pool.submit(single,each_pi,each_publisher,each_num,ti_len,target_dir2)
        # thread_pool.shutdown(wait=True)
        print("one dir done.")
        with open(f"{target_dir}{os.sep}already_dir.txt","a",encoding="utf-8") as f:
            f.write(each_publisher+"\n")
        time.sleep(5)
    print("ThreadPool: All done.")
    # print(publisher_identifiers)
    # print(publishers)
    # pass

if __name__ == '__main__':
    main()