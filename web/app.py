import chainlit as cl


@cl.on_chat_start
async def start():
    # 发送含有操作按钮的消息
    actions = [
        cl.Action(name="upload_file", value="file", description="Upload File"),
        cl.Action(name="provide_url", value="url", description="Provide URL")
    ]

    await cl.Message(content="Please choose an option:", actions=actions).send()

@cl.action_callback("upload_file")
async def on_upload_file(action: cl.Action):
    # 处理文件上传操作
    # 请根据您的需求添加相应逻辑
    return "You have chosen to upload a file."

@cl.action_callback("provide_url")
async def on_provide_url(action: cl.Action):
    # 处理提供URL操作
    # 请根据您的需求添加相应逻辑
    return "You have chosen to provide a URL."

@cl.step
def tool():
    return "Response from the tool!"


@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def main(message: cl.Message):
    """
    This function is called every time a user inputs a message in the UI.
    It sends back an intermediate response from the tool, followed by the final answer.

    Args:
        message: The user's message.

    Returns:
        None.
    """

    # Call the tool
    tool()

    # Send the final answer.
    await cl.Message(content="This is the final answer").send()