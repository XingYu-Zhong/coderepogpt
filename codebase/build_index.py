import asyncio
import csv
import uuid
import json
import networkx as nx
import os
import re
import matplotlib.pyplot as plt

from enum import Enum
from pathlib import Path
from typing import Optional, Literal, TypeAlias

from .language_extract import *
from .openai.lc_openai import *
from .prompt.few_shot_generate_file_descriptions import *


LanguageType: TypeAlias = Literal["python", "java", "golang", "go", "js", "javascript", "cpp", "c++", "c", "php"]


class GraphIndex:
    def __init__(self, file_dir: Optional[str] = None, output_dir: str = "output") -> None:
        """
        Initializes a GraphIndex instance.

        Args:
            file_dir (str): The directory of files, required.
            output_dir (str, optional): The output directory. Defaults to 'output'.
        """
        if file_dir is None:
            raise ValueError("file_dir is none")
        elif not os.path.exists(file_dir):
            raise ValueError(f"The directory {file_dir} does not exist")
        self.file_dir = file_dir
        self.output_dir = output_dir

    def build_call_graph(self, functions: dict, calls: list):
        """
        根据函数信息和调用关系构建调用图。

        根据提供的函数信息和它们之间的调用关系，此函数创建并返回一个表示调用图的有向图。
        这有助于理解函数间的依赖关系和调用结构。

        Args:
            functions (dict): 包含函数信息的字典，键是函数名称，值是相关信息。
            calls (list): 包含函数调用关系的列表，每个元素是一个函数调用的元组。

        Returns:
            Graph: 表示函数调用关系的有向图。
        """
        G = nx.DiGraph()
        for function, info in functions.items():
            G.add_node(function, **info)
        for call in calls:
            if call["caller"] in G and call["callee"] in G:
                G.add_edge(call["caller"], call["callee"], **{k: v for k, v in call.items() if k not in ["caller", "callee"]})
            else:
                if call["caller"] not in G:
                    G.add_node(call["caller"], **functions.get(call["caller"], {}))
                if call["callee"] not in G:
                    G.add_node(call["callee"], **functions.get(call["callee"], {}))
                G.add_edge(call["caller"], call["callee"], **{k: v for k, v in call.items() if k not in ["caller", "callee"]})
        return G

    def visualize_call_graph(self, G: nx.DiGraph, file_path: str):
        """
        可视化调用图。

        接受一个调用图的有向图表示，并将其可视化输出为一张图片，保存到指定路径。
        此函数不返回任何值。

        Args:
            G (Graph): 调用图的有向图表示。这个图应该包含所有需要展示的节点和边。
            file_path (str): 图片保存路径。指定生成的可视化图片应该保存在哪个位置。

        Returns:
            None
        """
        # 设置布局，增加节点间隔以确保节点之间有一定间隙，避免节点重合
        pos = nx.spring_layout(G, k=1.5, iterations=100)
        # 计算图的大小，确保所有节点都能在图内清楚地显示
        plt.figure(figsize=(40, 40))
        # 绘制节点
        nx.draw_networkx_nodes(G, pos, node_size=500, node_color="lightblue", linewidths=0.25)
        # 绘制边，使用箭头以区分方向，并设置合适的箭头大小
        nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=5, node_size=500)
        # 绘制节点标签，并调整字体大小以防止重叠
        nx.draw_networkx_labels(G, pos, font_size=7, font_family="sans-serif")
        # 保存图片，确保图片大小固定
        plt.savefig(file_path, format="PNG", bbox_inches="tight")

    def analyze_directory(self, language: LanguageType = "python"):
        """
        分析指定目录下的文件，构建调用图。

        此函数遍历指定目录下的所有文件，分析其中的函数定义和调用关系，
        并构建一个调用图。这有助于理解代码结构和函数间的依赖关系。
        函数执行完毕后不返回任何值。

        Args:
            language (str): 指定的语言类型。默认为 'python'。

        Returns:
            None
        """

        directory = self.file_dir
        out_path = self.output_dir

        match language.lower():
            case "python":
                extract = python_extract(directory)
                functions, calls = extract.python_extract_call_functions()
            case "java":
                extract = java_extract(directory)
                functions, calls = extract.java_extract_call_functions()
            case "golang" | "go":
                extract = go_extract(directory)
                functions, calls = extract.go_extract_call_functions()
            case "js" | "javascript":
                extract = js_extract(directory)
                functions, calls = extract.js_extract_call_functions()
            case "cpp" | "c++":
                extract = cpp_extract(directory)
                functions, calls = extract.cpp_extract_call_functions()
            case "c":
                extract = c_extract(directory)
                functions, calls = extract.c_extract_call_functions()
            case "php":
                extract = php_extract(directory)
                functions, calls = extract.php_extract_call_functions()
            case _:
                raise ValueError("Unsupported language types: {}".format(language))

        id = str(uuid.uuid1())
        if not os.path.exists(out_path):
            os.makedirs(out_path)

        visualize_file_path = os.path.join(out_path, id + ".png")
        graph_json_file_path = os.path.join(out_path, id + ".json")

        call_graph = self.build_call_graph(functions, calls)
        self.visualize_call_graph(call_graph, visualize_file_path)
        call_graph_data = nx.readwrite.json_graph.node_link_data(call_graph)

        # 将图结构转换为CSV格式并保存
        csv_file_path = os.path.join(out_path, id + ".csv")
        with open(csv_file_path, "w", encoding="utf-8", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["id", "class", "file_path", "source", "target"])
            node_links = {edge["source"]: edge["target"] for edge in call_graph_data["links"]}
            for node in call_graph_data["nodes"]:
                class_name = node.get("class", "")
                node_id = node.get("id", "")
                file_path = node.get("file_path", "")
                source = node_id if node_id in node_links else ""
                target = node_links.get(node_id, "")
                csv_writer.writerow([node_id, class_name, file_path, source, target])

        with open(graph_json_file_path, "w", encoding="utf-8") as f:
            json.dump(call_graph_data, f, ensure_ascii=False, indent=4)

        return id


class LLMIndex:
    def __init__(
        self, openai_api_key: str, graphid: str, target_dir: str, output_dir: str = "output", model: str = "gpt-4-1106-preview", retry_count: int = 3
    ) -> None:
        """
        初始化 LLMIndex 类的实例。

        此初始化函数配置了用于 LLMIndex 的基本参数，包括 OpenAI 的 API 密钥、图的唯一标识符、目标和输出目录的路径等。
        还可以指定所使用的模型和在调用 LLM 进行解析时的最大重试次数。

        Args:
            openai_api_key (str): OpenAI 的 API 密钥。
            graphid (str): 图的唯一标识符。
            target_dir (str): 目标目录的路径。
            output_dir (str, optional): 输出目录的路径。默认为 'output'。
            model (str, optional): 使用的模型。默认为 'gpt-4-1106-preview'。
            retry_count (int, optional): index 调用 LLM 解析的最大重试次数。默认为 3。
        Returns:
            None
        """
        self.graphid = graphid
        self.output_dir = output_dir
        self.target_dir = Path(target_dir)
        self.csv_index = self._get_csv_content()
        self.lc_llm = ChatLLM(openai_api_key=openai_api_key, model=model)
        self.retry_count = retry_count

    def _get_csv_content(self):
        """
        获取 CSV 文件的内容。

        读取并返回 CSV 文件的内容。此函数假设 CSV 文件已经指定且可访问，
        并将其内容作为字符串返回。
        Args:
            None
        Returns:
            str: CSV 文件的内容字符串。
        """
        csv_file_path = os.path.join(self.output_dir, self.graphid + ".csv")
        with open(csv_file_path, "r", encoding="utf-8") as csv_file:
            return csv_file.read()

    def llm_extract_index(self):
        """
        使用 LLM 从 CSV 索引中提取并生成描述信息。

        此函数利用 LLM（大型语言模型）处理 CSV 文件中的数据，从中提取重要信息，
        并生成相应的描述。这个过程依赖于 LLM 的解析能力来理解和描述 CSV 中的数据。
        Args:
            None
        Returns:
            str: 从 CSV 索引中提取的描述信息。
        """
        # instructions = INDEX_FILE_DESCRIPTION_INSTRUCTION_PROMPT + INDEX_FILE_DESCRIPTION_LONG_EXAMPLE_PROMPT + INDEX_FILE_DESCRIPTION_HINT
        instructions = INDEX_FILE_DESCRIPTION_INSTRUCTION_PROMPT + INDEX_FILE_DESCRIPTION_HINT + INDEX_FILE_DESCRIPTION_SHORT_EXAMPLE_PROMPT
        prompt = "Input:\n" + self.csv_index + "\n\nOutput:\n"
        retry_count = self.retry_count
        response = ""
        for attempt in range(retry_count):
            chat_result = self.lc_llm.chat(prompt=prompt, instructions=instructions)
            try:
                # 使用正则表达式匹配字典部分
                match = re.search(r"\[.*\]", chat_result, re.DOTALL)
                if match:
                    dict_str = match.group()
                    # 使用json.loads()函数将字符串转换为字典
                    response = json.loads(dict_str)
                else:
                    response = json.loads(chat_result)
                break  # 如果解析成功，跳出循环
            except Exception as e:
                if attempt < retry_count - 1:
                    continue  # 如果不是最后一次尝试，继续下一次循环
                else:
                    raise ValueError(f"llm_extract_index: {e}")  # 如果是最后一次尝试，抛出异常

        index_file_path = os.path.join(self.output_dir, self.graphid + "-onlyindexfile.json")

        with open(index_file_path, "w", encoding="utf-8") as f:
            json.dump(response, f, ensure_ascii=False, indent=4)
        return response

    def _llm_file_descriptions(self, file_path: Path) -> str:
        """
        为给定文件生成描述。

        该函数使用 OpenAINode 对象来生成文件内容的概要。根据文件类型，概要规则有所不同：
        - 对于代码文件，它会概括每个类和函数，并描述它们各自的功能。
        - 对于文本文件，它会直接转述文本内容。
        - 返回的是一个清晰、不含额外分析的段落式总结。

        Args:
            file_path (Path): 要概括的文件的路径。

        Returns:
            str: 文件内容的总结。
        """

        FILE_DESCRIPTIOMS_PROMPT = """
    Your job is to summarize the contents of the document.
    Follow these rules strictly:
        - For code files, it summarizes each class and function, describing what each does.
        - For text files, it directly intermediates the text content.
        - The response is a clear, unambiguous paragraph summary without additional analysis.
    """
        # 检查路径是否为文件
        if file_path.is_file():
            with open(file_path, "r", errors="ignore") as file:
                content = file.read()
            content = content.replace("{", "{{").replace("}", "}}")
            if self.lc_llm.count_tokenizer(content) > 4000:
                content = self.lc_llm.split_text(content, 4000)
            prompt = "This is the file path:\n" + str(file_path) + "\nThis is the contents of the file:\n" + content
            chat_result = self.lc_llm.chat(prompt=prompt, instructions=FILE_DESCRIPTIOMS_PROMPT)
            return chat_result
        else:
            # 如果路径是一个目录，返回一个错误信息或者忽略
            return f"Error: {file_path} is a directory, not a file."

    def generate_file_descriptions_json(self):
        """
        生成包含目录中文件描述的 JSON 字符串。

        此函数遍历给定路径中的文件和目录。对于每个文件，它生成一个包含文件名和其描述的字典。
        如果遇到目录，则递归调用该函数处理该目录。然后将字典列表序列化为 JSON 格式的字符串。

        Args:
            directory_path (str): 要遍历的目录路径。

        Returns:
            str: 表示文件列表及其描述的 JSON 格式字符串。
        """
        json_file = self.llm_extract_index()
        dict_file = {}
        for i in json_file:
            dict_file[i["file_path"]] = i["descriptions"]  # type: ignore

        def _descriptions_iter(dir_path: Path):
            """
            一个生成器函数，生成文件描述。

            这个函数遍历指定目录路径中的文件，并逐个产生关于每个文件的描述。

            Args:
                dir_path (Path): 需要遍历的目录路径。

            Returns:
                dict: 一个包含 'file_name' 和 'descriptions' 键的字典。
            """
            contents = list(dir_path.iterdir())
            for path in contents:
                if path.is_file():  # 确保路径是一个文件
                    if str(path) in dict_file:
                        description = dict_file[str(path)]
                    else:
                        description = self._llm_file_descriptions(path)
                    yield {"file_path": str(path), "descriptions": description}
                elif path.is_dir():  # 如果是目录，递归调用
                    yield from _descriptions_iter(path)

        descriptions_list = list(_descriptions_iter(self.target_dir))
        result_json = json.dumps(descriptions_list, indent=4)
        index_file_path = os.path.join(self.output_dir, self.graphid + "-indexfile.json")
        with open(index_file_path, "w", encoding="utf-8") as f:
            json.dump(descriptions_list, f, ensure_ascii=False, indent=4)
        return result_json

    async def _fast_llm_file_descriptions(self, file_path: Path) -> str:
        """
        异步地为给定文件生成描述。

        此函数异步地处理指定文件路径的文件，并生成该文件的描述。它利用了异步编程的优势，
        在处理大型文件或多个文件时可以提高性能。

        Args:
            file_path (Path): 需要生成描述的文件路径。

        Returns:
            str: 给定文件的描述。
        """
        FILE_DESCRIPTIOMS_PROMPT = """
        Your job is to summarize the contents of the document.
        Follow these rules strictly:
            - For code files, it summarizes each class and function, describing what each does.
            - For text files, it directly intermediates the text content.
            - The response is a clear, unambiguous paragraph summary without additional analysis.
        """
        if file_path.is_file():
            with open(file_path, "r", errors="ignore") as file:
                content = file.read()
            content = content.replace("{", "{{").replace("}", "}}")
            if self.lc_llm.count_tokenizer(content) > 4000:
                content = self.lc_llm.split_text(content, 4000)
            prompt = "This is the file path:\n" + str(file_path) + "\nThis is the contents of the file:\n" + content
            # 使用异步调用 achat
            chat_result = await self.lc_llm.achat(prompt=prompt, instructions=FILE_DESCRIPTIOMS_PROMPT)
            return chat_result
        else:
            return f"Error: {file_path} is a directory, not a file."

    async def fast_generate_file_descriptions_json(self):
        json_file = self.llm_extract_index()
        dict_file = {}
        for i in json_file:
            dict_file[i["file_path"]] = i["descriptions"]  # type: ignore

        async def _descriptions_iter(dir_path: Path):
            contents = list(dir_path.iterdir())
            tasks = []
            paths = []
            for path in contents:
                if path.is_file():
                    if str(path) in dict_file:
                        description = dict_file[str(path)]
                        yield {"file_path": str(path), "descriptions": description}
                    else:
                        # 改为异步调用
                        task = asyncio.create_task(self._fast_llm_file_descriptions(path))
                        tasks.append(task)
                        paths.append(path)
                elif path.is_dir():
                    # 递归调用需要同步到异步的转换
                    async for desc in _descriptions_iter(path):
                        yield desc
            # 等待所有异步任务完成
            descriptions = await asyncio.gather(*tasks)
            for description, path in zip(descriptions, paths):
                yield {"file_path": str(path), "descriptions": description}

        # 异步生成器必须在异步环境中使用
        async def collect_descriptions():
            return [desc async for desc in _descriptions_iter(self.target_dir)]

        descriptions_list = await collect_descriptions()
        result_json = json.dumps(descriptions_list, indent=4)
        index_file_path = os.path.join(self.output_dir, self.graphid + "-indexfile.json")
        with open(index_file_path, "w", encoding="utf-8") as f:
            json.dump(descriptions_list, f, ensure_ascii=False, indent=4)
        return result_json
