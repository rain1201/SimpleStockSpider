import lmstudio as lms
from py2neo import Graph,Node,Relationship,NodeMatcher
import py2neo,csv
graph=Graph("bolt://localhost:7687/",user="neo4j",password="Neo4j123")
llmModel = lms.llm("qwen3-4b")
embeddingModel = lms.embedding_model("text-embedding-m3e-base")
while(1):
    question=input(">")
    embedding = embeddingModel.embed(question)
    result = graph.run("""
            WITH $embedding AS question_embedding
            CALL db.index.vector.queryNodes(
                'stock-embeddings',  // 股票信息向量索引名称
                $top_k,              // 返回结果数量
                question_embedding   // 问题嵌入向量
            ) YIELD node AS stock, score
            OPTIONAL MATCH (stock)<-[holder_rel:参股]-(holder:股东)
            OPTIONAL MATCH (stock)-[:概念包括]->(concept:概念)
            RETURN stock.代码 AS 股票代码,
                stock.名称 AS 股票名称,
                stock.行业 AS 所属行业,
                COLLECT(DISTINCT holder{.*, 持股类型: holder_rel.类型, 持股量: holder_rel.持股量, 持股占比: holder_rel.占比}) AS 股东信息,
                COLLECT(DISTINCT concept.名称) AS 关联概念,
                score AS 相似度得分
        """, {
            'embedding': embedding,
            'top_k': 3
        }).data()

    prompt = f"# Question:\n{question}\n\n# Graph DB search results:\n{result}"
    messages = [
        {"role": "system", "content": "假定你是一名财务分析人员，现在你需要回答客户关于一些股票的咨询。\
                                    你的助手将会为你提供相关股票在数据库中的信息，你需要严格根据这些信息回答问题。\
                                    注意你只能根据提供的信息回答，如果提供的信息与问题不相关，请直接说明你无法回答这个问题。\
                                    进行计算或比较数字大小时，你需要注意小数位数与单位。"},
        {"role": "user", "content": question},
        {"role": "assistant", "content":str(result)}
    ]
    for fragment in llmModel.respond_stream({"messages": messages}):
        print(fragment.content, end="", flush=True)
    print()
    