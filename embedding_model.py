import os
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from conf import CACHE_DIR, EMBED_MODEL_DIR

def bge_embedding_model(**kwargs) -> HuggingFaceEmbedding:
    embed_model = HuggingFaceEmbedding(
        model_name=os.path.join(EMBED_MODEL_DIR),
        cache_folder=CACHE_DIR,
        **kwargs,
    )
    return embed_model

def test_bge_embedding_model():
    from llama_index.core import VectorStoreIndex, Document
    from llms import dash_scope_qwen
    documents = [Document(text="量子计算利用量子比特实现并行计算")]
    embed_model = bge_embedding_model()
    index = VectorStoreIndex.from_documents(
    documents,
    embed_model=embed_model
    )
    query_engine = index.as_query_engine(llm=dash_scope_qwen())
    response = query_engine.query("量子比特的作用是什么？")
    print(response)

test_bge_embedding_model()