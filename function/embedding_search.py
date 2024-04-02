

from llamaindex.createindex import IndexStore


class EmbeddingSearch:
    def  __init__(self,project_path):
        self.index = IndexStore(project_path)
    def search_embedding(self, query:str, k:int=10):
        return self.index.search(query=query,topk=k)