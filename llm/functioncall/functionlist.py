

from logger.logging_config import logger
from function.call_relation_search import CallRelationSearch
from function.embedding_search import EmbeddingSearch
from function.utils import read_file
from llm.functioncall.decorator import functioncall



class ProjectAnalyzer:
    def __init__(self, project_path):
        self.project_path = project_path
        self.crs = CallRelationSearch(project_path)
        self.es = EmbeddingSearch(project_path)
    @functioncall(
        description="Can read any file.",
        param_descriptions={
            "file_path": {
                "description": "Path to the file to be read.",
                "type": "string"
            }
        }
    )
    def read_any_file(self,file_path):
        return read_file(file_path)

    @functioncall(
        description="Call this to answer the user. Call this only when you have enough information to answer the user's query.",
        param_descriptions={
            "paths": {
                "type": "array",
                "items": {
                    "type": "integer",
                    "description": "The index of the path to be answered. Can be null if the answer is not related to a specific path. For example:[1,3] or []."
                }
            }
        }
    )
    def finish(self,paths):
        logger.info(f"Finish called with paths: {paths}")
        return paths

    @functioncall(
        description="Get the graph structure of function calls in the project.",
        param_descriptions={
        }
    )
    def call_relation(self):
        return self.crs.call_relation_search()

    @functioncall(
        description="Get the block of code in the codebase that is most similar to the query, including file path, function name, and function body.",
        param_descriptions={
            "project_path": {
                "description": "Path to the project.",
                "type": "string"
            },
            "query": {
                "description": "Problems requiring queries to the code base.",
                "type": "string"
            }
        }
    )
    def coderepo_search(self,query):
        return self.es.search_embedding(query=query)
