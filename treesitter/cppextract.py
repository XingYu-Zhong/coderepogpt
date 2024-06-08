from tree_sitter import Node
from treesitter.baseextract import BaseExtract
from function.utils import *

CLASS_DEF_QUERY = """
(translation_unit
    (class_specifier) @class
)
(translation_unit
    (function_definition) @function
)
"""

class CppExtract:

    def __init__(self) -> None:
        self.extract = BaseExtract('cpp')

    def get_node_text(self, node: Node, content: bytes) -> str:
        return content[node.start_byte:node.end_byte].decode("utf-8")

    def get_class_name(self, node: Node) -> str:
        for child in node.children:
            if child.type == 'type_identifier':
                return child.text.decode("utf-8")
        return ""

    def get_function_name(self, node: Node) -> str:
        for child in node.children:
            if child.type == 'function_declarator':
                for subchild in child.children:
                    if subchild.type == 'identifier':
                        return subchild.text.decode("utf-8")
        return ""

    def extract_class_methods(self, class_node: Node, content: bytes, src_path: str) -> list:
        methods_list = []
        for child in class_node.children:
            if child.type == "field_declaration_list":
                for subchild in child.children:
                    if subchild.type == "function_definition":
                        method_name = self.get_function_name(subchild)
                        class_name = self.get_class_name(class_node)
                        full_method_name = f"{class_name}::{method_name}"
                        methods_list.append({
                            'source_path': src_path,
                            'begin_byte': subchild.start_byte,
                            'end_byte': subchild.end_byte,
                            'name': full_method_name,
                        })
        return methods_list

    def splitter_function(self, src_path):
        content = read_file(src_path).encode("utf-8")
        treenode = self.extract.parse_file_with_treesitter(context=content.decode("utf-8"))
        captures = self.extract.query_treesitter(CLASS_DEF_QUERY, treenode)
        datas_list = []
        for node, tag in captures:
            match tag:
                case "class":
                    name = self.get_class_name(node)
                    datas_list.append({
                        'source_path': src_path,
                        'begin_byte': node.start_byte,
                        'end_byte': node.end_byte,
                        'name': name,
                    })
                    # Extract methods within the class
                    methods = self.extract_class_methods(node, content, src_path)
                    datas_list.extend(methods)
                case "function":
                    # Standalone function
                    name = self.get_function_name(node)
                    datas_list.append({
                        'source_path': src_path,
                        'begin_byte': node.start_byte,
                        'end_byte': node.end_byte,
                        'name': name,
                    })
                case _:
                    raise ValueError("Unknown tag")
        return datas_list