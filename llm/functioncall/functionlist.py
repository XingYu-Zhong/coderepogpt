

from function.call_relation_search import CallRelationSearch
from function.utils import read_file
from llm.functioncall.decorator import functioncall






@functioncall(
    description="Can read any file.",
    param_descriptions={
        "file_path": {
            "description": "Path to the file to be read.",
            "type": "string"
        }
    }
)
def read_any_file(file_path):
    return read_file(file_path)

@functioncall(
    description="Call this to answer the user. Call this only when you have enough information to answer the user's query.",
    param_descriptions={
        "paths": {
            "type": "array",
            "items": {
                "type": "integer",
                "description": "The indices of the paths to answer with respect to. Can be empty if the answer is not related to a specific path."
            }
        }
    }
)
def finish(paths):
    return paths

@functioncall(
    description="Get the graph structure of function calls in the project.",
    param_descriptions={
        "project_path": {
            "description": "Path to the project.",
            "type": "string"
        }
    }
)
def call_relation(project_path):
    crs = CallRelationSearch(project_path)
    return crs.call_relation_search()

