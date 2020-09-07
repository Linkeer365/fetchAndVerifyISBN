import numpy
import pandas as pd
import os
import requests
from lxml import etree
import time
from concurrent.futures import ThreadPoolExecutor
import sys

import random


# 使用更快的f-strings
# https://blog.csdn.net/sunxb10/article/details/81036693


xls_path="D:\AllDowns\fetchAndVerifyISBN\publisher_identifiers.xlsx"

same_head="9787"

target_dir=r"D:\All_isbns"

douban_url_template="https://book.douban.com/isbn/{}/"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"}



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
    not_collected_str="豆瓣评论暂时没有收录此书，请原谅。"
    douban_url=douban_url_template.format(full_str)
    page_text=requests.get(douban_url,headers=headers).text
    time.sleep(random.randint(2,5))
    html=etree.HTML(page_text)
    find=html.xpath("//li[starts-with(@style,'list-style-type:none;')]//text()")
    if find and find[0]==not_collected_str:
        print("Not Collected!")
        return False
    elif not find:
        print("Collected!")
        return True

def single(some_pi,some_publisher,some_num,ti_len,target_dir2):
    full_ti_str = get_full_ti_str(some_num, ti_len)
    init_part = f"{same_head}{some_pi}{full_ti_str}"
    check_digit = get_check_digit(init_part)
    full_str = f"{init_part}{check_digit}"
    print("Full Str:", full_str)
    if is_collected_by_douban_fullstr(full_str):
        isbn = full_str
        with open(f"{target_dir2}{os.sep}{isbn}.txt", "a", encoding="utf-8") as f:
            f.write(isbn+"\n")
        # with open(f"{target_dir2}{os.sep}already_num.txt","a",encoding="utf-8") as g:
        #     g.write(some_num+"\n")
    print("one file done.")

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
#
#     print("one done.")

def get_start_val(some_target_dir,some_ti_len):
    some_target_dir+=os.sep
    if len(os.listdir(target_dir))==0:
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
    # thread_pool=ThreadPoolExecutor(max_workers=2)
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
        startAtVal=get_start_val(target_dir2,ti_len)
        # if os.path.exists(f"{target_dir2}{os.sep}already_num.txt"):
        #     with open(f"{target_dir2}{os.sep}already_num.txt","r",encoding="utf-8") as h:
        #         startAtVal=int(h.readlines()[-1].replace("\n",""))
        for each_num in range(startAtVal,10 ** ti_len):
            single(each_pi,each_publisher,each_num,ti_len,target_dir2)
            # future=thread_pool.submit(single,each_pi,each_publisher,each_num,ti_len,target_dir2)
        print("one dir done.")
        with open(f"{target_dir}{os.sep}already_dir.txt","a",encoding="utf-8") as f:
            f.write(each_publisher+"\n")
    # thread_pool.shutdown(wait=False)
    print("ThreadPool: All done.")
    # print(publisher_identifiers)
    # print(publishers)
    # pass

if __name__ == '__main__':
    main()