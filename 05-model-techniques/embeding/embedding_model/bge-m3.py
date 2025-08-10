#!/usr/bin/env python
# coding: utf-8

# In[1]:


#模型下载 modelscope相当于国内的huggingface
from modelscope import snapshot_download
# 这个bge-m3不超过3GB,大部分电脑都可以跑
model_dir = snapshot_download('BAAI/bge-m3', cache_dir='models')


# In[1]:

# 也是一个模型库，就和Sentence Transformers差不多，但是这个是BAAI专门给BGE设计的，用BGE的话就用这个加载
from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel('models/BAAI/bge-m3',
                       use_fp16=True) # Setting use_fp16 to True speeds up computation with a slight performance degradation

sentences_1 = ["What is BGE M3?", "Defination of BM25"]
sentences_2 = ["BGE M3 is an embedding model supporting dense retrieval, lexical matching and multi-vector interaction.",
               "BM25 is a bag-of-words retrieval function that ranks a set of documents based on the query terms appearing in each document"]

embeddings_1 = model.encode(sentences_1,
                            batch_size=12,
                            max_length=8192, # If you don't need such a long length, you can set a smaller value to speed up the encoding process.
                            )['dense_vecs']
embeddings_2 = model.encode(sentences_2)['dense_vecs']
similarity = embeddings_1 @ embeddings_2.T
print(similarity)
# [[0.6265, 0.3477], [0.3499, 0.678 ]]

