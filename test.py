import os
from llamaindex.createindex import IndexStore
from llm.functioncall.functionlist import *
from llm.functioncall.openai_function_call import OpenaiClient
from treesitter.pythonextract import PyExtract




# directory = "tmp/testpy"
# datas_list = []
# for root, dirs, files in os.walk(directory):
#     for filename in files:
#         full_path = os.path.join(root, filename)  # 构建完整路径
#         normalized_path = os.path.normpath(full_path)  # 标准化路径
#         extract = PyExtract()
#         result_list = extract.splitter_function(normalized_path)  # 使用标准化的完整路径
#         for i in result_list:
#             datas_list.append(i)
# print(datas_list)
# original_directory = os.getcwd()  # 保存原始工作目录
# os.chdir(directory)  # 切换到目标仓库的根目录
# try:
    
# finally:
#     os.chdir(original_directory)  # 恢复原始工作目录

client = OpenaiClient('tmp/testpy')
messages = "user:我想知道testfunc的具体实现然后详细解释运行这个函数后的效果"
response = client.tools_chat_completion_request(messages)
print(response)


# index = IndexStore('tmp/testpy')
# response  =index.search("Which function is used to hello",10)
# print(response)

