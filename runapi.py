import os
import git
from dotenv import load_dotenv
from llm.functioncall.functionlist import *
from llm.functioncall.openai_function_call import OpenaiClient
import urllib.parse
def clone_repo_with_token(repo_url, clone_to):
    """
    克隆一个需要认证的GitHub仓库。

    参数:
    repo_url (str): 原始仓库的URL。
    clone_to (str): 克隆到的本地目录。

    返回:
    str: 成功时返回克隆到的本地目录（包含子目录），不成功时返回空字符串。
    """
    try:
        if not os.path.exists(clone_to):
            os.makedirs(clone_to)
        load_dotenv()
        # 从环境变量中获取令牌
        token = os.getenv('github_token')
        if not token:
            raise ValueError("GitHub token not found in environment variables")

        # 提取仓库的域名和路径
        if repo_url.startswith("https://"):
            repo_url = repo_url.replace("https://", f"https://{token}@")
        elif repo_url.startswith("http://"):
            repo_url = repo_url.replace("http://", f"http://{token}@")

        # 从URL中提取仓库名称
        repo_name = urllib.parse.urlparse(repo_url).path.split('/')[-1]

        # 在clone_to目录下创建新的目录
        cloned_path = os.path.join(clone_to, repo_name)
        if os.path.exists(cloned_path):
            return cloned_path
        # 克隆仓库
        repo = git.Repo.clone_from(repo_url, cloned_path)
        
        print(f"Repository cloned to {cloned_path}")
        return cloned_path
    except Exception as e:
        print(f"Failed to clone repository: {e}")
        return ''

def run(url,message):
    repo_path = clone_repo_with_token(url,'gitrepo')
    file_count = sum([len(files) for _, _, files in os.walk(repo_path)])
    if file_count > 100:
        return "项目太大了，请换小项目提问"

    client = OpenaiClient(repo_path) 
    messages = f"user:{message}"
    try:
        response = client.tools_chat_completion_request(messages)
    except Exception as e:
        print(f"An error occurred: {e}")
    # print(response)
    return response

# result = run('https://github.com/XingYu-Zhong/QuantitativeStrategies','这些策略有啥用？')
# print(result)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class RequestData(BaseModel):
    url: str
    message: str

@app.post("/run")
def run_endpoint(data: RequestData):
    try:
        result = run(data.url, data.message)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/privacy")
def privacy_policy():
    return {
        "message": "本API不搜集任何用户数据，仅在比赛期间开放。"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)