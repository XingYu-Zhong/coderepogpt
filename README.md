# coderepogpt

## 简介

CodeRepoGPT是一个基于LLM的代码项目咨询平台。它能够根据用户输入的内容，自动索引到相关代码片段，文件等收集足够多信息后回答用户问题。

## 技术规划
主要通过function call来进行交互，通过gpt-4-turbo-preview来进行回答。

具体function有
- embedding的搜索:有llamaindex版本和针对code优化版本（分为两步，第一步对代码func进行切割，第二步对每个func进行解释，然后对解释的内容进行embedding）。根据用户输入消息来匹配向量数据库中最相关的topk
- 调用关系搜索:通过treesitter来解析ast，之后通过递归把函数之间关系找到。初始本版可以直接把所有调用关系都返回，之后可以优化成只返回用户输入函数的调用关系。
- 文件内容的读取：直接通过路径来返回文件内容

## 项目结构
```
.
├── README.md
├── function
│   ├── __init__.py
│   ├── embedding_search.py
│   ├── call_relation_search.py
│   └── file_context_read.py
├── llm
│   ├── __init__.py
│   ├── openai_function_call.py

```

## 项目运行

```
pip install -r requirements.txt
python main.py
```

## 注册函数工具
在这个functionlist.py中，你可以注册你想要调用的函数。
```
├── llm
│   ├── functionlist.py
```
我们通过装饰器@functioncall()来注册函数。
```python
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
```
需要添加函数的描述，以及参数的描述，特别要注意的是type，必须按照openai的functioncall里的type来写