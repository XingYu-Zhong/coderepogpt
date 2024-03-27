from function.codebase.build_index import GraphIndex
from function.utils import *

class CallRelationSearch:
    def __init__(self,file_dir:str,output_dir:str = 'output',language :str ='python'):
        self.output_dir =output_dir
        gi= GraphIndex(file_dir,output_dir)
        self.id = gi.analyze_directory(language)
    def call_relation_search(self):
        return read_file(file_path=f'{self.output_dir}/{self.id}.csv',encoding='utf-8')