## 文件结构
buildindex.py处理图结构和最后fileindex
languagesextract.py处理不同语言的ast解析
prompt文件夹存放提示词
openai文件夹处理openai调用
build文件夹存放解析不同语言ast的so文件


## get start
这个文件夹可以单独创建一个虚拟环境
```shell
pip install -r requirements.txt
```
### 添加新的语言
- 先git clone 下来对应的tree-sitter目录
- 然后运行脚本

```python
from tree_sitter import Language
file_list = ["tree-sitter-go", "tree-sitter-javascript", "tree-sitter-python", "tree-sitter-java"] #这里填入你需要加上的新的语言目录
for i in file_list:
    Language.build_library(
        # Store the library in the `build` directory
        f"build/{i}.so",#这里是你希望存的so的路径
        # Include one or more languages
        [i],
    )
```
## TODO
- 获取当前函数和被调用函数的内容，让llm总结描述其具体关系

## 测试用例
图索引构造
```python
from codebase.buildindex import *
file_dir = 'nodes'#需要分析的文件夹
output_dir = 'output'#图结构放到的文件夹
gi= GraphIndex(file_dir,output_dir)
id = gi.analyze_directory('python')
print(f'id:{id}')
```
用不同语言构造图索引项目
```python
from codebase.buildindex import *
gi= GraphIndex('test','output')
id = gi.analyze_directory('java')
# id = gi.analyze_directory('go')
print(f'id:{id}')
```
会在output_dir里存放图索引的json，csv和png


```python
from codebase.buildindex import *
id = 'c5875bbe-ba4e-4350-8d28-19911714f918'
li = LLMIndex(openai_api_key='sk-bxxxxxxxxWvqxxxxxxcXxF1Y5X1vt8r',model ='gpt-4-1106-preview',graphid=id,target_dir='test',output_dir='output')
json_text = li.generate_file_descriptions_json()
'''
如果只做代码文件的提取，不加上其它文件
可以这样调用：
json_text = li.llm_extract_index()
'''
#json_text = li.llm_extract_index()
print(json_text)
```
索引生成
会在output_dir里存放索引的json文件（以indexfile结尾）
```shell
[
    {
        "file_path": "test/requirements.txt",
        "descriptions": "The document is a `requirements.txt` file which lists the Python packages required for a project. It is organized into sections with comments indicating the purpose of each group of packages.\n\n- Basic dependencies include:\n  - `requests`: for making HTTP requests.\n  - `typeguard`: for runtime type checking.\n  - `dill`: for serialization.\n  - `python-dotenv`: for managing environment variables.\n\n- Server-related packages include:\n  - `fastapi`: for building APIs with Python.\n  - `uvicorn`: an ASGI server for running FastAPI applications.\n  - `websockets`: for WebSocket communication.\n\n- Language model (llm) related libraries:\n  - `openai`: for accessing OpenAI's API.\n  - `tiktoken`: not a commonly known package, possibly related to token handling.\n  - `langchain`: not a commonly known package, possibly related to language processing.\n  - `tokentrim`: not a commonly known package, potentially for token manipulation or reduction.\n\n- Database packages:\n  - `redis`: for interacting with Redis data store.\n  - `sqlmodel`: for ORM with SQL databases.\n\n- Debugging tools:\n  - `debugpy`: for debugging Python code.\n  - `pytest`: for testing Python code.\n  - `httpx`: for making asynchronous HTTP requests.\n\n- Data processing libraries:\n  - `docx2txt`: for converting DOCX files to text.\n  - `numpy`: for numerical computing.\n  - `pandas`: for data manipulation and analysis.\n  - `python-multipart`: for handling multipart encoding.\n  - `lxml`: for XML and HTML processing.\n\n- Services:\n  - `markdown`: for converting Markdown to HTML.\n\n- Git and GitHub integration:\n  - `GitPython`: for interacting with git repositories.\n  - `PyGithub`: for using the GitHub API.\n\n- Jupyter notebook-related packages for code running:\n  - `ipykernel`: for running Jupyter kernel.\n  - `jupyter_client`: for client for the Jupyter protocol."
    },
    {
        "file_path": "test/test.txt",
        "descriptions": "The document 'test.txt' contains two lines of simple arithmetic expressions. The first line states the addition of 1 and 1, resulting in 2, and the second line states the addition of 2 and 2, resulting in 4."
    },
    {
        "file_path": "test/hellotest/new.py",
        "descriptions": "Contains a function 'testfunc' that calls 'hello'"
    },
    {
        "file_path": "test/hellotest/hel.py",
        "descriptions": "Contains a function 'hello'"
    },
    {
        "file_path": "test/repo_manager.py",
        "descriptions": "FileAction class: Provides string representation of a file action, RepoManager class: Initializes a RepoManager object with a README loader, Sets the root path for the repository, Retrieves the repository path, Adds a file to focus, Removes a file from focus, Sets a single focus file by adding it to the focus list, Gets the contents of all focus files, Retrieves the content of a specified file, Applies file actions and generates a file tree string, Adds a file to the repository, Removes a file from the repository, Modifies a file in the repository, Generates a string representation of the file tree, Iterates over the file tree, Provides file descriptions, Generates JSON representation of file descriptions, Iterates over file descriptions, Loads README file content"
    }
]
```


### 异步实验

```python
from codebase.buildindex import *
import time
import asyncio
gi= GraphIndex('test','output')
id = gi.analyze_directory('python')
# id = 'b966d3ba-6de4-4737-a125-66bb32faee9e'
li = LLMIndex(openai_api_key='sk-bxxxxxx1Y5Xxxxxxxxx8r',model ='gpt-4-1106-preview',graphid=id,target_dir='test',output_dir='output')

start_time = time.time()  # 记录开始时间
json_test = li.generate_file_descriptions_json()
end_time = time.time()  # 记录结束时间
print(f"正常运行时间: {end_time - start_time} 秒")

async def test():
    start_time = time.time()  # 记录开始时间
    descriptions_json = await li.fast_generate_file_descriptions_json()
    end_time = time.time()  # 记录结束时间
    print(f"异步运行时间: {end_time - start_time} 秒")

asyncio.run(test())
```

```shell
正常运行时间: 43.86116695404053 秒
异步运行时间: 39.68914771080017 秒
```
