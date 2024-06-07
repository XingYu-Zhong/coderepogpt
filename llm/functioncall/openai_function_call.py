import json
import os
from dotenv import load_dotenv
from openai import OpenAI

from tenacity import retry, wait_random_exponential, stop_after_attempt 
import llm.functioncall.functionlist as fl
from llm.functioncall.decorator import *
from logger.logging_config import logger
class OpenaiClient:
    def __init__(self,project_path,proxy=None):
        load_dotenv()
        if proxy:
            os.environ["HTTP_PROXY"] = proxy
            os.environ["HTTPS_PROXY"] = proxy
        openai_api_key = os.getenv("openai_api_key")
        self.tools_model = "gpt-4o"
        self.client = OpenAI(api_key = openai_api_key)
        self.tools = registered_functions
        self.messages = []#TODO save
        self.pa = fl.ProjectAnalyzer(project_path)

    @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
    def chat_completion_request(self,messages, tools=None, tool_choice=None,model = None):
        try:
            response = self.client.chat.completions.create(
                model=model if model else self.tools_model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
            )
            logger.info(f"messages:{messages}\nChatCompletion response: {response.choices[0].message}")
            return response
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e
        
    def tools_chat_completion_request(self,messages_history):
        self.messages.append({"role": "user", "content": messages_history})
        while True:
            prompt = """
            你的任务就是选择最佳操作。调用函数查找有助于回答用户问题的信息。在有足够信息回答问题时，调用 functions.finish。请始终遵守以下规则：
            - 始终调用函数，不要直接回答问题，即使问题不是用英语提出的
            - 不要调用以前使用过的具有相同参数的函数
            - 切勿假设索引库的结构（如上所述）或文件或文件夹的存在
            - 调用 functions.finish 时，请使用您确信有助于回答用户查询的路径，包括包含完整回答所需信息（包括定义和引用）的路径。
            - 如果用户引用或询问的信息在历史记录中，则调用 functions.finish
            - 如果在尝试收集信息后仍不确定如何回答询问，则调用 functions.finish
            - 如果查询是问候语，或者既不是问题也不是指令，则调用 functions.finish
            - 如果函数的输出是空的，请尝试使用不同的参数再次调用函数，或者尝试调用不同的函数
            - 始终调用函数。不要直接回答问题
            - user:后面的内容才是用户的输入，前面的background是一些背景介绍
            """ 
            self.messages.append({"role": "system", "content": prompt})
            chat_response = self.chat_completion_request(self.messages, self.tools, 'auto')
            
            assistant_message = chat_response.choices[0].message
            print(assistant_message)
            self.messages.pop()
            self.messages.append(assistant_message)
            tool_calls = assistant_message.tool_calls
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                function_args_str = ','.join([
                    f"{k}={repr(v) if isinstance(v, str) else v if not isinstance(v, list) else '[' + ', '.join(map(repr, v)) + ']'}"
                    for k, v in function_args.items()
                ])
                logger.info(f"Calling function self.pa.{function_name}({function_args_str})")
                function_call_response = eval(f"self.pa.{function_name}({function_args_str})")#TODO 展示
                if function_name == "finish":
                    # if len(function_call_response) == 0:
                    #     function_call_response = "The current question does not require a call to an external function, so please think about it and answer it directly."
                    # else:
                    #     response = []
                    #     for i in function_call_response:
                    #         print(self.messages[i])
                    #         response.append(self.messages[i])
                    #     function_call_response = response
                    self.messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_call_response),
                    }
                    )
                    chat_response = self.chat_completion_request(self.messages)
                    assistant_message = chat_response.choices[0].message
                    return assistant_message.content
                self.messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_call_response),
                    }
                )
