from llm.functioncall.functionlist import *
from llm.functioncall.openai_function_call import OpenaiClient



client = OpenaiClient()
messages = "background:这是用户的项目路径的根路径:tmp/testpy"+"\nuser:我想知道中国的首都是哪里？"
response = client.tools_chat_completion_request(messages)
print(response)
# import json
# print(json.dumps(registered_functions, indent=4))
# with open('registered_functions.json', 'w') as f:
#     json.dump(registered_functions, f)
