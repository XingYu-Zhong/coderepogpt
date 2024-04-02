from tree_sitter import Language, Parser
import os
import platform


class BaseExtract:
    def __init__(self, directory, language):
        self.directory = str(directory)
        self.language = language

    def parse_file_with_treesitter(self, file_path):
        """
        使用 tree_sitter 解析文件，获取 AST（抽象语法树）。

        此函数读取指定路径的文件，并使用 tree_sitter 解析器来解析该文件，
        最终获取并返回文件的抽象语法树（AST）的根节点。

        Args:
            file_path (str): 要解析的文件路径。

        Returns:
            Node: AST 的根节点。
        """
        with open(file_path, "rb") as file:
            source_code = file.read()
        parser = Parser()

        # Determine the file extension based on the operating system
        system = platform.system()
        if system == "Windows":
            extension = "dll"
        elif system == "Darwin":
            extension = "dylib"
        else:  # Assume Linux if not Windows or macOS
            extension = "so"

        language_path = os.path.join(os.path.dirname(__file__), "build", f"tree-sitter-{self.language}.{extension}")
        parser.set_language(Language(language_path, self.language))
        tree = parser.parse(source_code)
        return tree.root_node


class python_extract(BaseExtract):
    def __init__(self, directory):
        super().__init__(directory, "python")

    def parse_file_with_treesitter(self, file_path):
        return super().parse_file_with_treesitter(file_path)

    def extract_functions(self, root_node, file_path):
        """
        从抽象语法树的根节点提取函数信息。

        此函数遍历抽象语法树的节点。当遇到类定义或函数定义时，提取相关信息并存储。
        对于每个类定义，记录当前类的名称。对于每个函数定义，记录函数的信息，
        包括其在文件中的起始和结束字节位置、所属的类（如果有）以及函数所在的文件路径。

        Args:
            root_node (Node): 语法树的根节点。
            file_path (str): 当前分析的文件路径。

        Returns:
            dict: 包含所有函数信息的字典。键为函数标识符，值为函数的详细信息。
        """
        functions = {}
        current_class = None
        current_function = None

        def traverse(node):
            """
            遍历语法树的内部节点，提取类和函数的定义信息。

            这是一个递归函数，用于检查当前节点的类型，并根据节点类型执行相应的操作。
            如果节点是类定义，它会更新当前类的名称；如果节点是函数定义，它会提取函数的信息并更新当前函数。

            Args:
                node (Node): 当前遍历到的节点。
            """
            nonlocal current_class, current_function
            if node.type == "class_definition":
                class_name = node.child_by_field_name("name")
                if class_name:
                    current_class = class_name.text.decode("utf-8")
                else:
                    current_class = None
            elif node.type == "function_definition":
                function_name = node.child_by_field_name("name")
                if function_name:
                    # 确保在构建functions字典时，所有的键都是字符串类型
                    function_id = f"{current_class}.{function_name.text.decode('utf-8')}" if current_class else function_name.text.decode("utf-8")
                    functions[function_id] = {
                        # 'start_byte': node.start_byte,
                        # 'end_byte': node.end_byte,
                        "class": current_class,
                        "file_path": file_path,
                    }
                    current_function = function_id
                else:
                    current_function = None
            # 遍历子节点
            for child in node.children:
                traverse(child)

        traverse(root_node)
        return functions

    def extract_calls(self, root_node, functions):
        """
        遍历语法树的节点，提取函数调用关系。

        此函数对每个函数调用进行分析，记录调用者和被调用者的信息，并将其存储在 calls 列表中。
        在这个过程中，如果当前存在类上下文，会用于确定被调用函数的完整名称。

        Args:
            root_node (Node): 语法树的根节点。
            functions (dict): 包含所有函数信息的字典。

        Returns:
            list: 包含所有函数调用关系的列表。
        """
        calls = []
        current_class = None
        current_function = None

        def traverse(node):
            """
            遍历语法树的内部节点，提取函数调用信息。

            这是一个递归函数，它会检查当前节点的类型，并根据节点类型执行相应的操作。
            如果节点是类定义，它会更新当前类的名称；如果节点是函数定义，它会更新当前函数；
            如果节点是函数调用，它会提取调用信息并存储在calls列表中。

            :param node: 当前遍历到的节点
            """
            nonlocal current_class, current_function
            if node.type == "class_definition":
                class_name = node.child_by_field_name("name")
                if class_name:
                    current_class = class_name.text.decode("utf-8")
            elif node.type == "function_definition":
                function_name = node.child_by_field_name("name")
                if function_name:
                    function_id = f"{current_class}.{function_name.text.decode('utf-8')}" if current_class else function_name.text.decode("utf-8")
                    current_function = function_id
            elif node.type == "call":
                function_called = node.child_by_field_name("function")
                if function_called:
                    function_called_text = function_called.text.decode("utf-8")
                    callee_function_name = function_called_text  # 默认为全局函数名
                    # 如果函数调用包含点号，说明它可能是一个类的方法或者模块中的函数
                    if "." in function_called_text and current_class:
                        callee_class, callee_function = function_called_text.rsplit(".", 1)
                        callee_function_name = f"{callee_class}.{callee_function}"
                        if callee_class == "self":
                            callee_function_name = f"{current_class}.{callee_function}"
                    elif current_class:
                        # 如果当前有类上下文，假设它是这个类的方法
                        callee_function_name = f"{current_class}.{function_called_text}"

                    # 确保当前函数（调用者）和被调用的函数（callee_function_name）不同
                    # print(f'current_function:{current_function},callee_function_name:{callee_function_name}')
                    if current_function and current_function != callee_function_name and callee_function_name in functions:
                        calls.append(
                            {
                                "caller": current_function,
                                "callee": callee_function_name,
                            }
                        )
            # 遍历子节点
            for child in node.children:
                traverse(child)

        traverse(root_node)
        return calls

    def python_extract_call_functions(self):
        directory = self.directory
        functions = {}
        calls = []
        original_directory = os.getcwd()  # 保存原始工作目录
        os.chdir(directory)  # 切换到目标仓库的根目录
        try:
            for root, dirs, files in os.walk("."):
                for filename in files:
                    if filename.endswith(".py"):
                        file_path = os.path.join(root, filename)
                        root_node = self.parse_file_with_treesitter(file_path)
                        file_path = file_path.replace("./", "")
                        f = self.extract_functions(root_node, file_path)
                        functions.update(f)
            for root, dirs, files in os.walk("."):
                for filename in files:
                    if filename.endswith(".py"):
                        file_path = os.path.join(root, filename)
                        root_node = self.parse_file_with_treesitter(file_path)
                        c = self.extract_calls(root_node, functions)
                        calls.extend(c)
        finally:
            os.chdir(original_directory)  # 恢复原始工作目录
        return functions, calls


class java_extract(BaseExtract):
    def __init__(self, directory):
        super().__init__(directory, "java")

    def parse_file_with_treesitter(self, file_path):
        return super().parse_file_with_treesitter(file_path)

    def extract_functions(self, root_node, file_path):
        """
        从抽象语法树的根节点提取函数信息。

        此函数遍历抽象语法树的节点。当遇到类定义或函数定义时，提取相关信息并存储。
        对于每个类定义，记录当前类的名称。对于每个函数定义，记录函数的信息，
        包括其在文件中的起始和结束字节位置、所属的类（如果有）以及函数所在的文件路径。

        Args:
            root_node (Node): 语法树的根节点。
            file_path (str): 当前分析的文件路径。

        Returns:
            dict: 包含所有函数信息的字典。键为函数标识符，值为函数的详细信息。
        """
        functions = {}
        current_class = None
        current_function = None

        def traverse(node):
            """
            遍历语法树的内部节点，提取类和函数的定义信息。

            这是一个递归函数，用于检查当前节点的类型，并根据节点类型执行相应的操作。
            如果节点是类定义，它会更新当前类的名称；如果节点是函数定义，它会提取函数的信息并更新当前函数。

            Args:
                node (Node): 当前遍历到的节点。
            """
            nonlocal current_class, current_function
            if node.type == "class_declaration":
                class_name = node.child_by_field_name("name")
                if class_name:
                    current_class = class_name.text.decode("utf-8")
                else:
                    current_class = None
            elif node.type == "method_declaration":
                function_name = node.child_by_field_name("name")
                if function_name:
                    # 确保在构建functions字典时，所有的键都是字符串类型
                    function_id = f"{current_class}.{function_name.text.decode('utf-8')}" if current_class else function_name.text.decode("utf-8")
                    functions[function_id] = {
                        # 'start_byte': node.start_byte,
                        # 'end_byte': node.end_byte,
                        "class": current_class,
                        "file_path": file_path,
                    }
                    current_function = function_id
                else:
                    current_function = None
            # 遍历子节点
            for child in node.children:
                traverse(child)

        traverse(root_node)
        return functions

    def extract_calls(self, root_node):
        """
        遍历语法树的节点，提取函数调用关系。

        此函数对每个函数调用进行分析，记录调用者和被调用者的信息，并将其存储在 calls 列表中。
        在这个过程中，如果当前存在类上下文，会用于确定被调用函数的完整名称。

        Args:
            root_node (Node): 语法树的根节点。
            functions (dict): 包含所有函数信息的字典。

        Returns:
            list: 包含所有函数调用关系的列表。
        """
        calls = []
        current_class = None
        current_function = None
        variable_types = {}

        def traverse(node):
            """
            遍历语法树的内部节点，提取函数调用信息。

            这是一个递归函数，它会检查当前节点的类型，并根据节点类型执行相应的操作。
            如果节点是类定义，它会更新当前类的名称；如果节点是函数定义，它会更新当前函数；
            如果节点是函数调用，它会提取调用信息并存储在calls列表中。

            :param node: 当前遍历到的节点
            """
            nonlocal current_class, current_function
            stet = node.text.decode("utf-8")
            # print(f'node.type:{node.type},\nname:{stet}')
            if node.type == "class_declaration":
                class_name = node.child_by_field_name("name")
                if class_name:
                    current_class = class_name.text.decode("utf-8")
            elif node.type == "method_declaration":
                function_name = node.child_by_field_name("name")
                if function_name:
                    function_id = f"{current_class}.{function_name.text.decode('utf-8')}" if current_class else function_name.text.decode("utf-8")
                    current_function = function_id
            elif node.type == "assignment_expression":
                # 左侧是变量名，右侧是对象创建表达式
                variable_name_node = node.child_by_field_name("left")
                object_creation_node = node.child_by_field_name("right")
                if variable_name_node and object_creation_node and object_creation_node.type == "object_creation_expression":
                    variable_name = variable_name_node.text.decode("utf-8")
                    type_identifier_node = object_creation_node.child_by_field_name("type")
                    if type_identifier_node:
                        variable_type = type_identifier_node.text.decode("utf-8")
                        variable_types[variable_name] = variable_type
            elif node.type == "method_invocation":
                # 在Java中，方法调用可能是通过对象实例调用的，也可能是通过类名直接调用的静态方法
                # 因此，我们需要检查是否存在一个对象或类名前缀
                method_name = None
                caller_name = None
                for child in node.children:
                    if child.type == "identifier":
                        if method_name is None:
                            method_name = child.text.decode("utf-8")
                        else:
                            caller_name = method_name
                            method_name = child.text.decode("utf-8")
                    elif child.type == "field_access":
                        caller_name = "".join([n.text.decode("utf-8") for n in child.children if n.type == "identifier"])
                caller_node = node.child_by_field_name("object") or node.child_by_field_name("receiver")
                if caller_node:
                    caller_name = caller_node.text.decode("utf-8")
                    if caller_name in variable_types:
                        caller_name = variable_types[caller_name]
                    method_name = node.child_by_field_name("name").text.decode("utf-8")
                    callee_function_name = f"{caller_name}.{method_name}"
                    if current_function and current_function != callee_function_name:
                        calls.append(
                            {
                                "caller": current_function,
                                "callee": callee_function_name,
                            }
                        )
            # 遍历子节点
            for child in node.children:
                traverse(child)

        traverse(root_node)
        return calls

    def java_extract_call_functions(self):
        directory = self.directory
        functions = {}
        calls = []
        original_directory = os.getcwd()  # 保存原始工作目录
        os.chdir(directory)  # 切换到目标仓库的根目录
        try:
            for root, dirs, files in os.walk("."):
                for filename in files:
                    if filename.endswith(".java"):
                        file_path = os.path.join(root, filename)
                        root_node = self.parse_file_with_treesitter(file_path)
                        file_path = file_path.replace("./", "")
                        f = self.extract_functions(root_node, file_path)
                        functions.update(f)
            for root, dirs, files in os.walk("."):
                for filename in files:
                    if filename.endswith(".java"):
                        file_path = os.path.join(root, filename)
                        root_node = self.parse_file_with_treesitter(file_path)
                        c = self.extract_calls(root_node)
                        calls.extend(c)
        finally:
            os.chdir(original_directory)  # 恢复原始工作目录
        filtered_calls = [call for call in calls if call["caller"] in functions and call["callee"] in functions]
        calls = filtered_calls
        return functions, calls


class go_extract(BaseExtract):
    def __init__(self, directory):
        super().__init__(directory, "go")

    def parse_file_with_treesitter(self, file_path):
        return super().parse_file_with_treesitter(file_path)

    def extract_functions(self, root_node, file_path):
        """
        从抽象语法树的根节点提取函数信息。

        此函数遍历抽象语法树的节点。当遇到类定义或函数定义时，提取相关信息并存储。
        对于每个类定义，记录当前类的名称。对于每个函数定义，记录函数的信息，
        包括其在文件中的起始和结束字节位置、所属的类（如果有）以及函数所在的文件路径。

        Args:
            root_node (Node): 语法树的根节点。
            file_path (str): 当前分析的文件路径。

        Returns:
            dict: 包含所有函数信息的字典。键为函数标识符，值为函数的详细信息。
        """
        functions = {}
        current_class = None
        current_function = None

        def traverse(node):
            """
            遍历语法树的内部节点，提取类和函数的定义信息。

            这是一个递归函数，用于检查当前节点的类型，并根据节点类型执行相应的操作。
            如果节点是类定义，它会更新当前类的名称；如果节点是函数定义，它会提取函数的信息并更新当前函数。

            Args:
                node (Node): 当前遍历到的节点。
            """
            nonlocal current_class, current_function

            if node.type == "function_declaration":
                function_name = node.child_by_field_name("name")
                if function_name:
                    # 确保在构建functions字典时，所有的键都是字符串类型
                    function_id = function_name.text.decode("utf-8")
                    functions[function_id] = {
                        # 'start_byte': node.start_byte,
                        # 'end_byte': node.end_byte,
                        "file_path": file_path
                    }
                    current_function = function_id
                else:
                    current_function = None
            # 遍历子节点
            for child in node.children:
                traverse(child)

        traverse(root_node)
        return functions

    def extract_calls(self, root_node):
        """
        遍历语法树的节点，提取函数调用关系。

        此函数对每个函数调用进行分析，记录调用者和被调用者的信息，并将其存储在 calls 列表中。
        在这个过程中，如果当前存在类上下文，会用于确定被调用函数的完整名称。

        Args:
            root_node (Node): 语法树的根节点。
            functions (dict): 包含所有函数信息的字典。

        Returns:
            list: 包含所有函数调用关系的列表。
        """
        calls = []
        current_function = None

        def traverse(node):
            """
            遍历语法树的内部节点，提取函数调用信息。

            这是一个递归函数，它会检查当前节点的类型，并根据节点类型执行相应的操作。
            如果节点是类定义，它会更新当前类的名称；如果节点是函数定义，它会更新当前函数；
            如果节点是函数调用，它会提取调用信息并存储在calls列表中。

            :param node: 当前遍历到的节点
            """
            # stet = node.text.decode('utf-8')
            # print(f'node.type:{node.type},\nname:{stet}')
            nonlocal current_function
            if node.type == "function_declaration":
                function_name_node = node.child_by_field_name("name")
                if function_name_node:
                    current_function = function_name_node.text.decode("utf-8")
                    # print(f'current_function:{current_function}')
            elif node.type == "call_expression":
                function_called_node = node.child_by_field_name("function")
                # print(f'function_called_node:{function_called_node}')
                if function_called_node:
                    function_called = function_called_node.text.decode("utf-8")

                    # print(f'function_called:{function_called},current_function:{current_function}')

                    if current_function and current_function != function_called:
                        calls.append(
                            {
                                "caller": current_function,
                                "callee": function_called,
                            }
                        )

            # 遍历子节点
            for child in node.children:
                traverse(child)

        traverse(root_node)
        return calls

    def go_extract_call_functions(self):
        directory = self.directory
        functions = {}
        calls = []
        original_directory = os.getcwd()  # 保存原始工作目录
        os.chdir(directory)  # 切换到目标仓库的根目录
        try:
            for root, dirs, files in os.walk("."):
                for filename in files:
                    if filename.endswith(".go"):
                        file_path = os.path.join(root, filename)
                        root_node = self.parse_file_with_treesitter(file_path)
                        file_path = file_path.replace("./", "")
                        f = self.extract_functions(root_node, file_path)
                        functions.update(f)
            for root, dirs, files in os.walk("."):
                for filename in files:
                    if filename.endswith(".go"):
                        file_path = os.path.join(root, filename)
                        root_node = self.parse_file_with_treesitter(file_path)
                        c = self.extract_calls(root_node)
                        calls.extend(c)
        finally:
            os.chdir(original_directory)  # 恢复原始工作目录
        filtered_calls = [call for call in calls if call["caller"] in functions and call["callee"] in functions]
        calls = filtered_calls
        return functions, calls


class js_extract(BaseExtract):
    def __init__(self, directory):
        super().__init__(directory, "javascript")

    def parse_file_with_treesitter(self, file_path):
        return super().parse_file_with_treesitter(file_path)

    def extract_functions(self, root_node, file_path):
        """
        从抽象语法树的根节点提取函数信息。

        此函数遍历抽象语法树的节点。当遇到类定义或函数定义时，提取相关信息并存储。
        对于每个类定义，记录当前类的名称。对于每个函数定义，记录函数的信息，
        包括其在文件中的起始和结束字节位置、所属的类（如果有）以及函数所在的文件路径。

        Args:
            root_node (Node): 语法树的根节点。
            file_path (str): 当前分析的文件路径。

        Returns:
            dict: 包含所有函数信息的字典。键为函数标识符，值为函数的详细信息。
        """
        functions = {}
        current_class = None
        current_function = None

        def traverse(node):
            """
            遍历语法树的内部节点，提取类和函数的定义信息。

            这是一个递归函数，用于检查当前节点的类型，并根据节点类型执行相应的操作。
            如果节点是类定义，它会更新当前类的名称；如果节点是函数定义，它会提取函数的信息并更新当前函数。

            Args:
                node (Node): 当前遍历到的节点。
            """
            nonlocal current_class, current_function
            # testss = node.text.decode('utf-8')
            # print(f'text:{testss}\ntype:{node.type}')
            if node.type == "class_declaration":
                class_name_node = node.child_by_field_name("name")
                if class_name_node:
                    current_class = class_name_node.text.decode("utf-8")
            elif node.type == "method_definition":
                function_name_node = node.child_by_field_name("name")
                if function_name_node:
                    function_name = function_name_node.text.decode("utf-8")
                    # 如果当前节点是方法定义，并且存在当前类的上下文，则将类名附加到函数名前
                    function_id = f"{current_class}.{function_name}" if current_class else function_name
                    functions[function_id] = {
                        # 'start_byte': node.start_byte,
                        # 'end_byte': node.end_byte,
                        "class": current_class if node.type == "method_definition" else None,
                        "file_path": file_path,
                    }
                    current_function = function_id
                else:
                    current_function = None
            # 遍历子节点
            for child in node.children:
                traverse(child)

        traverse(root_node)
        return functions

    def extract_calls(self, root_node):
        """
        遍历语法树的节点，提取函数调用关系。

        此函数对每个函数调用进行分析，记录调用者和被调用者的信息，并将其存储在 calls 列表中。
        在这个过程中，如果当前存在类上下文，会用于确定被调用函数的完整名称。

        Args:
            root_node (Node): 语法树的根节点。
            functions (dict): 包含所有函数信息的字典。

        Returns:
            list: 包含所有函数调用关系的列表。
        """
        calls = []
        current_function = None
        current_class = None
        variable_types = {}

        def traverse(node):
            """
            遍历语法树的内部节点，提取函数调用信息。

            这是一个递归函数，它会检查当前节点的类型，并根据节点类型执行相应的操作。
            如果节点是类定义，它会更新当前类的名称；如果节点是函数定义，它会更新当前函数；
            如果节点是函数调用，它会提取调用信息并存储在calls列表中。

            :param node: 当前遍历到的节点
            """
            nonlocal current_function, current_class, variable_types
            if node.type == "class_declaration":
                class_name_node = node.child_by_field_name("name")
                if class_name_node:
                    current_class = class_name_node.text.decode("utf-8")
            elif node.type == "method_definition":
                function_name_node = node.child_by_field_name("name")
                if function_name_node:
                    function_name = function_name_node.text.decode("utf-8")
                    current_function = f"{current_class}.{function_name}" if current_class else function_name
            elif node.type == "variable_declarator":
                variable_name_node = node.child_by_field_name("name")
                # 查找 new_expression 节点
                for child in node.children:
                    if child.type == "new_expression":
                        type_node = child.named_child(0)  # 假设类型节点是 new_expression 的第一个命名子节点
                        if type_node and variable_name_node:
                            variable_name = variable_name_node.text.decode("utf-8")
                            variable_type = type_node.text.decode("utf-8")
                            variable_types[variable_name] = variable_type
                        break  # 找到 new_expression 后不需要继续遍历其他子节点

            elif node.type == "call_expression":
                # 提取调用表达式中的方法名和对象名
                method_name_node = node.child_by_field_name("function")
                if method_name_node and method_name_node.type == "member_expression":
                    object_node = method_name_node.child_by_field_name("object")
                    property_node = method_name_node.child_by_field_name("property")
                    if object_node and property_node:
                        object_name = object_node.text.decode("utf-8")
                        method_name = property_node.text.decode("utf-8")
                        # print(f'object_name:{object_name}\nmethod_name:{method_name}')
                        # 如果对象名是 'this' 或者与当前类名相同，我们可以假设它是当前类的方法调用
                        if object_name == "this":
                            object_name = current_class
                        # 如果对象名是一个变量，我们需要查找这个变量对应的类名
                        elif object_name in variable_types:
                            object_name = variable_types[object_name]
                        callee = f"{object_name}.{method_name}"
                    else:
                        callee = method_name_node.text.decode("utf-8")

                    if current_function and callee and current_function != callee:
                        calls.append(
                            {
                                "caller": current_function,
                                "callee": callee,
                            }
                        )

            # 遍历子节点
            for child in node.children:
                traverse(child)

        traverse(root_node)
        return calls

    def js_extract_call_functions(self):
        directory = self.directory
        functions = {}
        calls = []
        original_directory = os.getcwd()  # 保存原始工作目录
        os.chdir(directory)  # 切换到目标仓库的根目录
        try:
            for root, dirs, files in os.walk("."):
                for filename in files:
                    if filename.endswith(".js"):
                        file_path = os.path.join(root, filename)
                        root_node = self.parse_file_with_treesitter(file_path)
                        file_path = file_path.replace("./", "")
                        f = self.extract_functions(root_node, file_path)
                        functions.update(f)
            for root, dirs, files in os.walk("."):
                for filename in files:
                    if filename.endswith(".js"):
                        file_path = os.path.join(root, filename)
                        root_node = self.parse_file_with_treesitter(file_path)
                        c = self.extract_calls(root_node)
                        calls.extend(c)
        finally:
            os.chdir(original_directory)  # 恢复原始工作目录
        filtered_calls = [call for call in calls if call["caller"] in functions and call["callee"] in functions]
        calls = filtered_calls
        return functions, calls


class cpp_extract(BaseExtract):
    def __init__(self, directory):
        super().__init__(directory, "cpp")

    def parse_file_with_treesitter(self, file_path):
        return super().parse_file_with_treesitter(file_path)

    def extract_functions(self, root_node, file_path):
        """
        从抽象语法树的根节点提取函数信息。

        此函数遍历抽象语法树的节点。当遇到类定义或函数定义时，提取相关信息并存储。
        对于每个类定义，记录当前类的名称。对于每个函数定义，记录函数的信息，
        包括其在文件中的起始和结束字节位置、所属的类（如果有）以及函数所在的文件路径。

        Args:
            root_node (Node): 语法树的根节点。
            file_path (str): 当前分析的文件路径。

        Returns:
            dict: 包含所有函数信息的字典。键为函数标识符，值为函数的详细信息。
        """
        functions = {}
        current_class = None

        def traverse(node):
            """
            遍历语法树的内部节点，提取类和函数的定义信息。

            这是一个递归函数，用于检查当前节点的类型，并根据节点类型执行相应的操作。
            如果节点是类定义，它会更新当前类的名称；如果节点是函数定义，它会提取函数的信息并更新当前函数。

            Args:
                node (Node): 当前遍历到的节点。
            """
            nonlocal current_class
            # test = node.text.decode("utf-8")
            # print(f'node.type:{node.type},test:{test}')
            if node.type == "class_specifier":
                class_name_node = node.child_by_field_name("name")

                if class_name_node:
                    current_class = class_name_node.text.decode("utf-8")
                    # print(f'current_class:{current_class}')
            elif node.type == "function_declarator":
                function_name_node = None
                for i in range(0, node.child_count):
                    child = node.child(i)
                    if child.type == "field_identifier":
                        function_name_node = child
                        break
                if function_name_node:

                    function_name = function_name_node.text.decode("utf-8")
                    # print(f'node.type:{function_name_node.type},function_name:{function_name}')
                    function_id = f"{current_class}.{function_name}" if current_class else function_name
                    functions[function_id] = {
                        # 'start_byte': node.start_byte,
                        # 'end_byte': node.end_byte,
                        "class": current_class,
                        "file_path": file_path,
                    }
            # 遍历子节点
            for child in node.children:
                traverse(child)

        traverse(root_node)
        return functions

    def extract_calls(self, root_node):
        """
        遍历语法树的节点，提取函数调用关系。

        此函数对每个函数调用进行分析，记录调用者和被调用者的信息，并将其存储在 calls 列表中。
        在这个过程中，如果当前存在类上下文，会用于确定被调用函数的完整名称。

        Args:
            root_node (Node): 语法树的根节点。
            functions (dict): 包含所有函数信息的字典。

        Returns:
            list: 包含所有函数调用关系的列表。
        """
        calls = []
        current_function = None
        current_class = None
        variable_types = {}
        callee = None

        def traverse(node):
            """
            遍历语法树的内部节点，提取函数调用信息。

            这是一个递归函数，它会检查当前节点的类型，并根据节点类型执行相应的操作。
            如果节点是类定义，它会更新当前类的名称；如果节点是函数定义，它会更新当前函数；
            如果节点是函数调用，它会提取调用信息并存储在calls列表中。

            :param node: 当前遍历到的节点
            """
            nonlocal current_function, current_class, variable_types, callee
            # test = node.text.decode("utf-8")
            # print(f'node.type:{node.type},text:{test}')
            if node.type == "class_specifier":
                class_name_node = node.child_by_field_name("name")

                if class_name_node:
                    current_class = class_name_node.text.decode("utf-8")
            elif node.type == "function_declarator":
                function_name_node = None
                for i in range(0, node.child_count):
                    child = node.child(i)
                    if child.type == "field_identifier":
                        function_name_node = child
                        break
                if function_name_node:
                    function_name = function_name_node.text.decode("utf-8")
                    current_function = f"{current_class}.{function_name}" if current_class else function_name

            elif node.type == "declaration":
                # 在C++中，变量声明可能包含类型和变量名
                type_node = node.child_by_field_name("type")
                variable_name_node = node.child_by_field_name("declarator")
                if type_node and variable_name_node:
                    variable_type = type_node.text.decode("utf-8")
                    variable_name = variable_name_node.text.decode("utf-8")
                    variable_types[variable_name] = variable_type

            elif node.type == "call_expression":
                # 提取调用表达式中的方法名和对象名
                method_name_node = None
                object_name = None
                for child in node.children:
                    if child.type == "field_expression":
                        # field_expression 通常包含一个对象和一个通过该对象调用的方法
                        object_node = child.child_by_field_name("argument")
                        method_name_node = child.child_by_field_name("field")
                        if object_node and method_name_node:
                            object_name = object_node.text.decode("utf-8")
                            method_name = method_name_node.text.decode("utf-8")
                            # 如果对象名是一个变量，我们需要查找这个变量对应的类名
                            if object_name in variable_types:
                                object_name = variable_types[object_name]
                            callee = f"{object_name}.{method_name}"
                    elif child.type == "identifier" and method_name_node is None:
                        # 如果是直接的函数调用，没有对象名
                        method_name_node = child
                        callee = method_name_node.text.decode("utf-8")

                if method_name_node and not object_name:
                    # 直接的函数调用，没有对象名
                    callee = method_name_node.text.decode("utf-8")

                if current_function and callee and current_function != callee:
                    calls.append(
                        {
                            "caller": current_function,
                            "callee": callee,
                        }
                    )

            # 遍历子节点
            for child in node.children:
                traverse(child)

        traverse(root_node)
        return calls

    def cpp_extract_call_functions(self):
        directory = self.directory
        functions = {}
        calls = []
        original_directory = os.getcwd()  # 保存原始工作目录
        os.chdir(directory)  # 切换到目标仓库的根目录
        try:
            for root, dirs, files in os.walk("."):
                for filename in files:
                    if filename.endswith(".cpp"):
                        file_path = os.path.join(root, filename)
                        root_node = self.parse_file_with_treesitter(file_path)
                        file_path = file_path.replace("./", "")
                        f = self.extract_functions(root_node, file_path)
                        functions.update(f)
            for root, dirs, files in os.walk("."):
                for filename in files:
                    if filename.endswith(".cpp"):
                        file_path = os.path.join(root, filename)
                        root_node = self.parse_file_with_treesitter(file_path)
                        c = self.extract_calls(root_node)
                        calls.extend(c)
        finally:
            os.chdir(original_directory)  # 恢复原始工作目录
        filtered_calls = [call for call in calls if call["caller"] in functions and call["callee"] in functions]
        calls = filtered_calls
        return functions, calls


class c_extract(BaseExtract):
    def __init__(self, directory):
        self.directory = str(directory)

    def parse_file_with_treesitter(self, file_path):
        """
        使用 tree_sitter 解析文件，获取 AST（抽象语法树）。

        此函数读取指定路径的文件，并使用 tree_sitter 解析器来解析该文件，
        最终获取并返回文件的抽象语法树（AST）的根节点。

        Args:
            file_path (str): 要解析的文件路径。

        Returns:
            Node: AST 的根节点。
        """
        with open(file_path, "rb") as file:
            source_code = file.read()
        parser = Parser()
        system = platform.system()
        if system == "Windows":
            extension = "dll"
        elif system == "Darwin":
            extension = "dylib"
        else:  # Assume Linux if not Windows or macOS
            extension = "so"
        language_path = os.path.join(os.path.dirname(__file__), "build", f"tree-sitter-c.{extension}")
        parser.set_language(Language(language_path, "c"))
        tree = parser.parse(source_code)
        return tree.root_node

    def extract_functions(self, root_node, file_path):
        """
        从抽象语法树的根节点提取函数信息。

        此函数遍历抽象语法树的节点。当遇到结构体定义或函数定义时，提取相关信息并存储。
        对于每个结构体定义，记录当前结构体的名称。对于每个函数定义，记录函数的信息，
        包括其在文件中的起始和结束字节位置、所属的结构体（如果有）以及函数所在的文件路径。

        Args:
            root_node (Node): 语法树的根节点。
            file_path (str): 当前分析的文件路径。

        Returns:
            dict: 包含所有函数信息的字典。键为函数标识符，值为函数的详细信息。
        """
        functions = {}
        current_struct = None

        def traverse(node):
            """
            遍历语法树的内部节点，提取结构体和函数的定义信息。

            这是一个递归函数，用于检查当前节点的类型，并根据节点类型执行相应的操作。
            如果节点是结构体定义，它会更新当前结构体的名称；如果节点是函数定义，它会提取函数的信息并更新当前函数。

            Args:
                node (Node): 当前遍历到的节点。
            """
            nonlocal current_struct
            if node.type == "struct_specifier":
                # 获取结构体名称
                name_node = node.child_by_field_name("name")
                if name_node:
                    current_struct = name_node.text.decode("utf-8")
            elif node.type == "function_definition":
                # 获取函数名称
                function_name_node = node.child_by_field_name("declarator")
                while function_name_node and function_name_node.type != "identifier":
                    function_name_node = function_name_node.child_by_field_name("declarator") or function_name_node.named_child(0)
                if function_name_node:
                    function_name = function_name_node.text.decode("utf-8")
                    function_id = f"{current_struct}.{function_name}" if current_struct else function_name
                    functions[function_id] = {
                        # 'start_byte': node.start_byte,
                        # 'end_byte': node.end_byte,
                        "class": current_struct,
                        "file_path": file_path,
                    }
            # 遍历子节点
            for child in node.children:
                traverse(child)

        traverse(root_node)
        return functions

    def extract_calls(self, root_node, functions):
        """
        遍历语法树的节点，提取函数调用关系。

        此函数对每个函数调用进行分析，记录调用者和被调用者的信息，并将其存储在 calls 列表中。
        在这个过程中，如果当前存在结构体上下文，会用于确定被调用函数的完整名称。

        Args:
            root_node (Node): 语法树的根节点。
            functions (dict): 包含所有函数信息的字典。

        Returns:
            list: 包含所有函数调用关系的列表。
        """
        calls = []
        current_function = None
        current_struct = None
        variable_types = {}

        def traverse(node):
            """
            遍历语法树的内部节点，提取函数调用信息。

            这是一个递归函数，它会检查当前节点的类型，并根据节点类型执行相应的操作。
            如果节点是函数定义，它会更新当前函数；
            如果节点是函数调用，它会提取调用信息并存储在calls列表中。

            :param node: 当前遍历到的节点
            """
            nonlocal current_function, variable_types, current_struct
            if node.type == "struct_specifier":
                # 获取结构体名称
                name_node = node.child_by_field_name("name")
                if name_node:
                    current_struct = name_node.text.decode("utf-8")
            elif node.type == "function_definition":
                function_name_node = node.child_by_field_name("declarator")
                while function_name_node and function_name_node.type != "identifier":
                    function_name_node = function_name_node.child_by_field_name("declarator") or function_name_node.named_child(0)
                if function_name_node:
                    current_function = function_name_node.text.decode("utf-8")
                    # print(f'current_function:{current_function}')

            elif node.type == "declaration":
                # 在C中，变量声明可能包含类型和变量名
                # 我们需要找到类型标识符，这可能是一个结构体名称
                type_node = node.child_by_field_name("type")
                variable_name_node = node.child_by_field_name("declarator")
                if type_node and variable_name_node:
                    # 遍历类型节点的子节点以找到类型标识符
                    type_identifier_node = None
                    for child in type_node.children:
                        if child.type == "type_identifier":
                            type_identifier_node = child
                            break
                    if type_identifier_node:
                        variable_type = type_identifier_node.text.decode("utf-8")
                        variable_name = variable_name_node.text.decode("utf-8")
                        variable_types[variable_name] = variable_type

            elif node.type == "call_expression":
                # 提取调用表达式中的方法名
                function_called_node = node.child_by_field_name("function")
                test = function_called_node.text.decode("utf-8")
                # print(f'function_called_node:{test},type:{function_called_node.type}')
                if function_called_node and function_called_node.type == "field_expression":
                    # field_expression 通常包含一个对象和一个通过该对象调用的方法
                    object_node = function_called_node.child_by_field_name("argument")
                    method_name_node = function_called_node.child_by_field_name("field")
                    if object_node and method_name_node:
                        object_name = object_node.text.decode("utf-8")
                        method_name = method_name_node.text.decode("utf-8")
                        # 如果对象名是一个变量，我们需要查找这个变量对应的结构体类型
                        if object_name in variable_types:
                            struct_type = variable_types[object_name]

                            callee = f"{struct_type}.{method_name}"

                            caller = f"{current_struct}.{current_function}"
                            # print(f'callee:{callee},caller:{caller},isbool :{callee in functions}')

                            calls.append(
                                {
                                    "caller": caller,
                                    "callee": callee,
                                }
                            )
                elif function_called_node and function_called_node.type == "identifier":
                    # 直接的函数调用，没有对象名
                    function_called = function_called_node.text.decode("utf-8")
                    if current_function and function_called in functions:
                        calls.append(
                            {
                                "caller": current_function,
                                "callee": function_called,
                            }
                        )

            # 遍历子节点
            for child in node.children:
                traverse(child)

        traverse(root_node)
        return calls

    def c_extract_call_functions(self):
        directory = self.directory
        functions = {}
        calls = []
        original_directory = os.getcwd()  # 保存原始工作目录
        os.chdir(directory)  # 切换到目标仓库的根目录
        try:
            for root, dirs, files in os.walk("."):
                for filename in files:
                    if filename.endswith(".c"):
                        file_path = os.path.join(root, filename)
                        root_node = self.parse_file_with_treesitter(file_path)
                        file_path = file_path.replace("./", "")
                        function = self.extract_functions(root_node, file_path)
                        functions.update(function)
            for root, dirs, files in os.walk("."):
                for filename in files:
                    if filename.endswith(".c"):
                        file_path = os.path.join(root, filename)
                        root_node = self.parse_file_with_treesitter(file_path)
                        call = self.extract_calls(root_node, functions)
                        calls.extend(call)
        finally:
            os.chdir(original_directory)  # 恢复原始工作目录
        filtered_calls = [call for call in calls if call["caller"] in functions and call["callee"] in functions]
        calls = filtered_calls
        return functions, calls


class php_extract(BaseExtract):
    def __init__(self, directory):
        super().__init__(directory, "php")

    def parse_file_with_treesitter(self, file_path):
        return super().parse_file_with_treesitter(file_path)

    def extract_functions(self, root_node, file_path):
        """
        从抽象语法树的根节点提取 PHP 函数和类方法信息。

        此函数遍历抽象语法树的节点。当遇到类定义或方法定义时，提取相关信息并存储。
        对于每个类定义，记录当前类的名称。对于每个函数或方法定义，记录函数的信息，
        包括其在文件中的起始和结束字节位置、所属的类（如果有）以及函数所在的文件路径。

        Args:
            root_node (Node): 语法树的根节点。
            file_path (str): 当前分析的文件路径。

        Returns:
            dict: 包含所有函数信息的字典。键为函数标识符，值为函数的详细信息。
        """
        functions = {}
        current_class = None

        def traverse(node):
            """
            遍历语法树的内部节点，提取类和函数的定义信息。

            这是一个递归函数，用于检查当前节点的类型，并根据节点类型执行相应的操作。
            如果节点是类定义，它会更新当前类的名称；如果节点是函数或方法定义，它会提取函数的信息并更新当前函数。

            Args:
                node (Node): 当前遍历到的节点。
            """
            nonlocal current_class
            if node.type == "class_declaration":
                class_name_node = node.child_by_field_name("name")
                if class_name_node:
                    current_class = class_name_node.text.decode("utf-8")
            elif node.type == "function_definition" or node.type == "method_declaration":
                function_name_node = node.child_by_field_name("name")
                if function_name_node:
                    function_name = function_name_node.text.decode("utf-8")
                    function_id = f"{current_class}.{function_name}" if current_class else function_name
                    functions[function_id] = {
                        # 'start_byte': node.start_byte,
                        # 'end_byte': node.end_byte,
                        "class": current_class,
                        "file_path": file_path,
                    }
            # 遍历子节点
            for child in node.children:
                traverse(child)

        traverse(root_node)
        return functions

    def extract_calls(self, root_node, functions):
        """
        遍历语法树的节点，提取 PHP 函数和方法调用关系。

        此函数对每个函数调用进行分析，记录调用者和被调用者的信息，并将其存储在 calls 列表中。
        在这个过程中，如果当前存在类上下文，会用于确定被调用函数的完整名称。

        Args:
            root_node (Node): 语法树的根节点。
            functions (dict): 包含所有函数信息的字典。

        Returns:
            list: 包含所有函数调用关系的列表。
        """
        calls = []
        current_function = None
        current_class = None
        variable_assignments = {}
        variable_types = {}

        def traverse(node):
            """
            遍历语法树的内部节点，提取函数调用信息。

            这是一个递归函数，它会检查当前节点的类型，并根据节点类型执行相应的操作。
            如果节点是类定义，它会更新当前类的名称；如果节点是函数定义，它会更新当前函数；
            如果节点是函数调用，它会提取调用信息并存储在calls列表中。

            :param node: 当前遍历到的节点
            """
            nonlocal current_function, current_class, variable_assignments
            if node.type == "class_declaration":
                class_name_node = node.child_by_field_name("name")
                if class_name_node:
                    current_class = class_name_node.text.decode("utf-8")
            elif node.type in ["function_definition", "method_declaration"]:
                function_name_node = node.child_by_field_name("name")
                if function_name_node:
                    function_name = function_name_node.text.decode("utf-8")
                    current_function = f"{current_class}.{function_name}" if current_class else function_name
            elif node.type == "assignment_expression":
                # 处理变量赋值
                variable_name_node = node.child_by_field_name("left")
                value_node = node.child_by_field_name("right")
                if variable_name_node and value_node:
                    variable_name = variable_name_node.text.decode("utf-8")
                    if value_node.type == "object_creation_expression":
                        # test = value_node.text.decode("utf-8")
                        class_name_node = None
                        # 这是一个对象创建表达式，提取类名
                        for child in value_node.children:
                            if child.type == "name":
                                class_name_node = child
                        # print(f'class_name_node:{class_name_node}')
                        if class_name_node:
                            class_name = class_name_node.text.decode("utf-8")
                            # print(f'class_name:{class_name}')
                            variable_types[variable_name] = class_name
                    elif value_node.type == "member_access_expression":
                        # 这是一个成员访问表达式，提取方法名
                        method_name_node = value_node.child_by_field_name("name")
                        if method_name_node:
                            method_name = method_name_node.text.decode("utf-8")
                            object_node = value_node.child_by_field_name("object")
                            if object_node:
                                object_name = object_node.text.decode("utf-8")
                                if object_name in variable_types:
                                    # 如果对象名是之前创建的变量，则获取实际的类名
                                    class_name = variable_types[object_name]
                                    variable_assignments[variable_name] = f"{class_name}.{method_name}"
            elif node.type == "function_call_expression":
                # 处理函数调用
                # print(f'variable_assignments:{variable_assignments}')
                function_name_node = node.child_by_field_name("function")
                if function_name_node and function_name_node.type == "variable_name":
                    function_name = function_name_node.text.decode("utf-8")

                    function_name = function_name_node.text.decode("utf-8")
                    # print(f'function_name:{function_name}')
                    if function_name in variable_assignments:
                        # 如果函数名是之前赋值的变量，则获取实际的函数名
                        callee = variable_assignments[function_name]
                        # print(f'callee:{callee},current_function:{current_function}')
                        if current_function and callee in functions:
                            calls.append(
                                {
                                    "caller": current_function,
                                    "callee": callee,
                                }
                            )

            # 遍历子节点
            for child in node.children:
                traverse(child)

        traverse(root_node)
        return calls

    def php_extract_call_functions(self):
        directory = self.directory
        functions = {}
        calls = []
        original_directory = os.getcwd()  # 保存原始工作目录
        os.chdir(directory)  # 切换到目标仓库的根目录
        try:
            for root, dirs, files in os.walk("."):
                for filename in files:
                    if filename.endswith(".php"):
                        file_path = os.path.join(root, filename)
                        root_node = self.parse_file_with_treesitter(file_path)
                        file_path = file_path.replace("./", "")
                        function = self.extract_functions(root_node, file_path)
                        functions.update(function)
            for root, dirs, files in os.walk("."):
                for filename in files:
                    if filename.endswith(".php"):
                        file_path = os.path.join(root, filename)
                        root_node = self.parse_file_with_treesitter(file_path)
                        call = self.extract_calls(root_node, functions)
                        calls.extend(call)
        finally:
            os.chdir(original_directory)  # 恢复原始工作目录
        filtered_calls = [call for call in calls if call["caller"] in functions and call["callee"] in functions]
        calls = filtered_calls
        return functions, calls
