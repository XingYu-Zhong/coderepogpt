from tree_sitter import Language, Node, Parser
import os
import platform
class BaseExtract:
    def __init__(self,language:str):
        # Determine the file extension based on the operating system
        system = platform.system()
        if system == "Windows":
            extension = "dll"
        elif system == "Darwin":
            extension = "dylib"
        else:  # Assume Linux if not Windows or macOS
            extension = "so"
        language_path = os.path.join(os.path.dirname(__file__), "../codebase/build", f"tree-sitter-{language}.{extension}")
        self.treesitter = Language(language_path, language)

    def parse_file_with_treesitter(self, context:str):
        """
        使用 tree_sitter 解析文件，获取 AST（抽象语法树）。

        此函数读取指定路径的文件，并使用 tree_sitter 解析器来解析该文件，
        最终获取并返回文件的抽象语法树（AST）的根节点。

        Args:
            context (str): 要解析的文件内容。
            language (str): 要解析的文件的语言。

        Returns:
            Node: AST 的根节点。
        """
        source_code = context.encode()
        parser = Parser()
        parser.set_language(self.treesitter)
        tree = parser.parse(source_code)
        return tree.root_node
    
    def query_treesitter(self, query_context:str, node:Node):
        query = self.treesitter.query(query_context)
        captures = query.captures(node)
        return captures