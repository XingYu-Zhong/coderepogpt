

import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex,Document,StorageContext,load_index_from_storage
from llama_index.embeddings.openai import OpenAIEmbedding
import openai
from function.utils import read_file
from llamaindex.instructorembedding import InstructorEmbeddings
from treesitter.pythonextract import PyExtract
from llama_index.core.schema import BaseNode
from llama_index.core import Settings
FILE_DIR_BASE = ".llamaindex"
class IndexStore:
    def __init__(self,file_dir):
        self.file_dir = file_dir
        load_dotenv()
        
        Settings.embed_model = InstructorEmbeddings()
        
        self.file_dir_index = os.path.join(FILE_DIR_BASE, file_dir)
        # 检查路径是否存在
        if os.path.exists(self.file_dir_index):
            # 路径存在，从这个路径读取索引
            storage_context = StorageContext.from_defaults(persist_dir=self.file_dir_index)
            self.index = load_index_from_storage(storage_context)
        else:
            # 路径不存在，创建新的索引
            os.makedirs(self.file_dir, exist_ok=True)  # 确保目录被创建
            self.index = VectorStoreIndex(self.to_documents())
            self.index.storage_context.persist(persist_dir=self.file_dir_index)


    def to_documents(self):
        document_list = []
        for root, dirs, files in os.walk(self.file_dir):
            for filename in files:
                if filename.endswith('.py'):  # 只处理 .py 文件
                    full_path = os.path.join(root, filename)  # 构建完整路径
                    normalized_path = os.path.normpath(full_path)  # 标准化路径
                    extract = PyExtract()
                    result_list = extract.splitter_function(normalized_path)  # 使用标准化的完整路径
                    for result in result_list:
                        document = Document(
                            text=read_file(file_path=result['source_path'], begin_byte=result['begin_byte'], end_byte=result['end_byte']),
                            metadata={"filepath": result['source_path'], "name": result['name']},
                        )
                        document_list.append(document)

        return document_list
    
    def search(self, query: str,topk:int):
        retriever = self.index.as_retriever(verbose=True)
        result = retriever.retrieve(query)
        # print(f'result:{result}')
        nodes: list["BaseNode"] = []
        for r in result[:topk]:
            nodes.append(r.node)
        return nodes