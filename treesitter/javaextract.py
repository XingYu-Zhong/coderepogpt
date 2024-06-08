from tree_sitter import Node
from treesitter.baseextract import BaseExtract
from function.utils import *

CLASS_DEF_QUERY = """
(
    (class_declaration) @class
    (method_declaration) @method
)
"""

class JavaExtract:

    def __init__(self) -> None:
        self.extract = BaseExtract('java')

    def get_field_text(self, node: Node, field_name: str) -> str:
        name_field = node.child_by_field_name(field_name)
        if name_field is not None:
            return name_field.text.decode("utf-8")
        return ""

    def splitter_function(self, src_path):
        content = read_file(src_path)
        treenode = self.extract.parse_file_with_treesitter(context=content)
        captures = self.extract.query_treesitter(CLASS_DEF_QUERY, treenode)
        datas_list = []
        for node, tag in captures:
            match tag:
                case "class":
                    name = self.get_field_text(node, "name")
                    datas_list.append({
                        'source_path': src_path,
                        'begin_byte': node.start_byte,
                        'end_byte': node.end_byte,
                        'name': name,
                    })
                    body = node.child_by_field_name("body")
                    if body is not None:
                        for child in body.children:
                            match child.type:
                                case "method_declaration":
                                    method_name = f"{name}.{self.get_field_text(child, 'name')}"
                                    datas_list.append({
                                        'source_path': src_path,
                                        'begin_byte': child.start_byte,
                                        'end_byte': child.end_byte,
                                        'name': method_name,
                                    })
                                case _:
                                    continue
                case "method":
                    # Independent method, should not happen in Java, handled within class
                    continue
                case _:
                    raise ValueError("Unknown tag")
        return datas_list
