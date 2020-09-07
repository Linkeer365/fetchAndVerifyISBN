# fetchAndVerifyISBN
校验生成的ISBN号码，目前只做了中国地区的...

## 大致思路

根据Public Identifiers然后遍历Title Identifers，最后用豆瓣API的ISBN接口去校验这本书到底是否存在
