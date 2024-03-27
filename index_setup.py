from tree_sitter import Language
import platform
import subprocess
import shutil
import os


support_language = ["python"]

gitrepo = [f"git clone https://github.com/tree-sitter/tree-sitter-{i}.git" for i in support_language]
# 尝试执行 git 命令，如果失败则尝试使用另一种方式
for cmd in gitrepo:
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        # 如果失败，尝试使用 SSH 方式克隆
        cmd = cmd.replace("https://", "git@").replace("/", ":")
        cmd = cmd.replace("git clone ", "git clone git@")
        subprocess.run(cmd, shell=True)

file_list = [
    f"tree-sitter-{language}" for language in support_language
]  # 这里填入你需要加上的新的语言目录
# Determine the file extension based on the operating system
system = platform.system()
if system == "Windows":
    extension = "dll"

elif system == "Darwin":
    extension = "dylib"
else:  # Assume Linux if not Windows or macOS
    extension = "so"
for i in file_list:
    Language.build_library(
        # Store the library in the `build` directory
        f"build/{i}.{extension}",  # 这里是你希望存的路径
        # Include one or more languages
        [i],
    )

# 删除下载的目录
import os
import stat
import shutil

def onerror(func, path, exc_info):
    """
    Error handler for `shutil.rmtree`.
    
    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.
    
    If the error is for another reason it re-raises the error.
    
    Usage : `shutil.rmtree(path, onerror=onerror)`
    """
    # Check if access error
    if not os.access(path, os.W_OK):
        # Try adding write permission and then retry
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

# 在调用shutil.rmtree时使用onerror处理程序
for lang in support_language:
    dir_name = f"tree-sitter-{lang}"
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name, onerror=onerror)