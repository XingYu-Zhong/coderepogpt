from tree_sitter import Node
from treesitter.baseextract import BaseExtract
from function.utils import *

CLASS_DEF_QUERY = """
(
  (class_declaration) @class
  (function_declaration) @function
)
"""

class JSExtract:

    def __init__(self) -> None:
        self.extract = BaseExtract('javascript')

    def get_node_text(self, node: Node, content: bytes) -> str:
        return content[node.start_byte:node.end_byte].decode("utf-8")

    def get_class_name(self, node: Node, content: bytes) -> str:
        name_node = node.child_by_field_name('name')
        if name_node:
            return self.get_node_text(name_node, content)
        return ""

    def get_function_name(self, node: Node, content: bytes) -> str:
        name_node = node.child_by_field_name('name')
        if name_node:
            return self.get_node_text(name_node, content)
        return ""

    def splitter_function(self, src_path):
        content = read_file(src_path).encode("utf-8")
        treenode = self.extract.parse_file_with_treesitter(context=content.decode("utf-8"))
        captures = self.extract.query_treesitter(CLASS_DEF_QUERY, treenode)
        datas_list = []
        for capture in captures:
            node, tag = capture
            if tag == "class":
                class_name = self.get_class_name(node, content)
                datas_list.append({
                    'source_path': src_path,
                    'begin_byte': node.start_byte,
                    'end_byte': node.end_byte,
                    'name': class_name,
                })
                body = node.child_by_field_name("body")
                if body is not None:
                    for child in body.children:
                        if child.type == "method_definition":
                            method_name = f"{class_name}.{self.get_function_name(child, content)}"
                            datas_list.append({
                                'source_path': src_path,
                                'begin_byte': child.start_byte,
                                'end_byte': child.end_byte,
                                'name': method_name,
                            })
            elif tag == "function":
                function_name = self.get_function_name(node, content)
                datas_list.append({
                    'source_path': src_path,
                    'begin_byte': node.start_byte,
                    'end_byte': node.end_byte,
                    'name': function_name,
                })
            else:
                raise ValueError("Unknown tag")
        return datas_list

# 示例用法
# js_extract = JSExtract()
# result = js_extract.splitter_function('path/to/your/js/file.js')
# print(result)
