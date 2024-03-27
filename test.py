from llm.functioncall.functionlist import *
from llm.functioncall.openai_function_call import OpenaiClient



client = OpenaiClient()
messages = "这是用户的项目路径:tmp/testpy"+"\nuser:我想知道项目里的testfunc这个函数怎么实现的"
response = client.tools_chat_completion_request(messages)
print(response)
# import json
# print(json.dumps(registered_functions, indent=4))
# with open('registered_functions.json', 'w') as f:
#     json.dump(registered_functions, f)
