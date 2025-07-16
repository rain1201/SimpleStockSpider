from py2neo import Graph,Node,Relationship,NodeMatcher
import py2neo,csv
graph=Graph("bolt://localhost:7687/",user="neo4j",password="password")
holderFile=open("holder.csv","r", encoding="utf-8", newline="")
holderCSV=csv.reader(holderFile)
conceptFile=open("concept.csv","r", encoding="utf-8", newline="")
conceptCSV=csv.reader(conceptFile)
noticeFile=open("notice.csv","r", encoding="utf-8", newline="")
noticeCSV=csv.reader(noticeFile)
basicFile=open("basic.csv","r", encoding="utf-8", newline="")
basicCSV=csv.reader(basicFile)
marketFile=open("market.csv","r", encoding="utf-8", newline="")
marketCSV=csv.reader(marketFile)
nmatcher=NodeMatcher(graph)
for i in basicCSV:
    a=Node("股票",代码=i[0],名称=i[1],行业=i[2])
    graph.create(a)
holders=[]
for i in holderCSV:
    a=None
    if not i[1] in holders:
        a=Node("股东",名称=i[1],类型=i[2])
        graph.create(a)
        holders.append(i[1])
    if not a:a=nmatcher.match("股东",名称=i[1]).first()
    b=nmatcher.match("股票",代码=i[0]).first()
    r=Relationship(a,"参股",b,类型=i[3],持股量=i[4],占比=i[5])
    graph.create(r)
concepts=[]
for i in conceptCSV:
    a=None
    if not i[1] in concepts:
        a=Node("概念",名称=i[1])
        graph.create(a)
        concepts.append(i[1])
    if not a:a=nmatcher.match("概念",名称=i[1]).first()
    b=nmatcher.match("股票",代码=i[0]).first()
    r=Relationship(b,"概念包括",a)
    graph.create(r)
for i in noticeCSV:
    a=Node("通知",时间=i[1],标题=i[2],URL=i[3])
    graph.create(a)
    b=nmatcher.match("股票",代码=i[0]).first()
    r=Relationship(b,"发布",a)
    graph.create(r)
market=[]
for i in marketCSV:
    a=None
    if not i[1] in market:
        a=Node("市场",名称=i[1])
        graph.create(a)
        market.append(i[1])
    if not a:a=nmatcher.match("市场",名称=i[1]).first()
    b=nmatcher.match("股票",代码=i[0]).first()
    r=Relationship(b,"成分股属于",a)
    graph.create(r)