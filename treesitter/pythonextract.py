

from tree_sitter import Node
from treesitter.baseextract import BaseExtract
from function.utils import *
FUNCTION_DEF_QUERY = """
(module
    (function_definition) @function
)
(module
    (decorated_definition) @decorated_function
)
(module
    (class_definition) @class
)
"""
class PyExtract:

    def __init__(self) -> None:
        self.extract = BaseExtract('python')
    def get_field_text(self,node: Node, field_name: str) -> str:
        name_field = node.child_by_field_name(field_name)
        if name_field is not None:
            return name_field.text.decode("utf-8")
        return ""
    def splitter_function(self,src_path):
        content = read_file(src_path)
        treenode = self.extract.parse_file_with_treesitter(context=content)
        captures = self.extract.query_treesitter(FUNCTION_DEF_QUERY,treenode)
        datas_list = []
        for node, tag in captures:
            match tag:
                case "function":
                    name = self.get_field_text(node, "name")
                    datas_list.append({
                        'source_path':src_path,
                        'begin_byte':node.start_byte,
                        'end_byte':node.end_byte,
                        'name':name,
                    })
                case "decorated_function":
                    definition = node.child_by_field_name("definition")
                    if definition is None:
                        continue
                    name = self.get_field_text(definition, "name")
                    datas_list.append({
                        'source_path':src_path,
                        'begin_byte':node.start_byte,
                        'end_byte':node.end_byte,
                        'name':name,
                    })
                case "class":
                    name = self.get_field_text(node, "name")
                    datas_list.append({
                        'source_path':src_path,
                        'begin_byte':node.start_byte,
                        'end_byte':node.end_byte,
                        'name':name,
                    })
                    body = node.child_by_field_name("body")
                    if body is not None:
                        for child in body.children:
                            match child.type:
                                case "function_definition":
                                    method_name = f"{name}.{self.get_field_text(child, 'name')}"
                                    datas_list.append({
                                        'source_path':src_path,
                                        'begin_byte':node.start_byte,
                                        'end_byte':node.end_byte,
                                        'name':method_name,
                                    })
                                case "decorated_definition":
                                    definition = child.child_by_field_name("definition")
                                    if definition is None:
                                        continue
                                    method_name = f"{name}.{self.get_field_text(definition, 'name')}"
                                    datas_list.append({
                                        'source_path':src_path,
                                        'begin_byte':node.start_byte,
                                        'end_byte':node.end_byte,
                                        'name':method_name,
                                    })
                                case _:
                                    continue
                
                case _:
                    raise ValueError("Unknown tag")
        return datas_list

    