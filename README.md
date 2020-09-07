# fetchAndVerifyISBN
校验生成的ISBN号码，目前只做了中国地区的...

## 大致思路

根据Public Identifiers然后遍历Title Identifers，最后用豆瓣API的ISBN接口去校验这本书到底是否存在

### 步骤

1. 目前还没有做协程并发那些的（因为IP池还没有搞定，获取ip池的那段代码弄丢了还得重新写就非常麻烦...）
2. 记忆力是已经有了，各个publisher主要是用already_dir实现的，然后每个出版社内部就是sortByLambda+Num_slice，不重要（因为状态不好还整了挺久的...）

