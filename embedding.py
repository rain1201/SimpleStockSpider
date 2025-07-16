import lmstudio as lms
from py2neo import Graph,Node,Relationship,NodeMatcher
import py2neo,csv
graph=Graph("bolt://localhost:7687/",user="neo4j",password="Neo4j123")
embeddingModel = lms.embedding_model("text-embedding-m3e-base")
result = graph.run("MATCH (s:股票) RETURN s.代码, s.名称, s.行业, ID(s) as id")
embedding_dim=768
updates = []
for record in result:
    stock_id = record["s.代码"]
    stock_info = f"{record['s.名称']} {record['s.行业']} {record['s.代码']}"
    embedding = embeddingModel.embed(stock_info)
    updates.append({"id":stock_id,"embedding":embedding})
batchSize = 30
graph.run(
    """
    DROP INDEX `stock-embeddings` IF EXISTS 
"""
)
graph.run(
    """
    CREATE VECTOR INDEX `stock-embeddings`
    FOR (a:股票) ON (a.embedding)
    OPTIONS {
    indexConfig: {
        `vector.dimensions`: 768,
        `vector.similarity_function`: 'cosine'
    }
    }
    """,
)
batchSize = 10
total_processed = 0
for i in range(0, len(updates), batchSize):
    batch = updates[i : i + batchSize]
    batch_update_query = """
    UNWIND $batch AS item
    MATCH (s:股票 {代码: item.id})
    CALL db.create.setNodeVectorProperty(s, 'embedding', item.embedding);
    """
    graph.run(batch_update_query,batch=batch)
    total_processed += len(batch)
    print(f"Processed {total_processed}/{len(updates)} chunks")