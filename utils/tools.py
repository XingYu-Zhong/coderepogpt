

import json

import os

def get_directory_structure(directory_path):
    """
    获取指定目录下的文件结构并返回为字符串格式。

    :param directory_path: str, 目录路径
    :return: str, 文件结构
    """
    structure = []

    for root, dirs, files in os.walk(directory_path):
        level = root.replace(directory_path, '').count(os.sep)
        indent = ' ' * 4 * level
        structure.append(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for file in files:
            structure.append(f"{sub_indent}{file}")

    return "\n".join(structure)

def filter_data(obj):
    LANGUAGE_TAG = {
    "c++"          : "// C++",
    "cpp"          : "// C++",
    "c"            : "// C",
    "c#"           : "// C#",
    "c-sharp"      : "// C#",
    "css"          : "/* CSS */",
    "cuda"         : "// Cuda",
    "fortran"      : "! Fortran",
    "go"           : "// Go",
    "html"         : "<!-- HTML -->",
    "java"         : "// Java",
    "js"           : "// JavaScript",
    "javascript"   : "// JavaScript",
    "kotlin"       : "// Kotlin",
    "lean"         : "-- Lean",
    "lua"          : "-- Lua",
    "objectivec"  : "// Objective-C",
    "objective-c"  : "// Objective-C",
    "objective-c++": "// Objective-C++",
    "pascal"       : "// Pascal",
    "php"          : "// PHP",
    "python"       : "# Python",
    "r"            : "# R",
    "rust"         : "// Rust",
    "ruby"         : "# Ruby",
    "scala"        : "// Scala",
    "shell"        : "# Shell",
    "sql"          : "-- SQL",
    "tex"          : f"% TeX",
    "typescript"   : "// TypeScript",
    "vue"          : "<!-- Vue -->",

    "assembly"     : "; Assembly",
    "dart"         : "// Dart",
    "perl"         : "# Perl",
    "prolog"       : f"% Prolog",
    "swift"        : "// swift",
    "lisp"         : "; Lisp",
    "vb"           : "' Visual Basic",
    "visual basic" : "' Visual Basic",
    "matlab"       : f"% Matlab",
    "delphi"       : "{ Delphi }",
    "scheme"       : "; Scheme",
    "basic"        : "' Basic",
    "assembly"     : "; Assembly",
    "groovy"       : "// Groovy",
    "abap"         : "* Abap",
    "gdscript"     : "# GDScript",
    "haskell"      : "-- Haskell",
    "julia"        : "# Julia",
    "elixir"       : "# Elixir",
    "excel"        : "' Excel",
    "clojure"      : "; Clojure",
    "actionscript" : "// ActionScript",
    "solidity"     : "// Solidity",
    "powershell"   : "# PowerShell",
    "erlang"       : f"% Erlang",
    "cobol"        : "// Cobol",
    "batchfile"  : ":: Batch file",
    "makefile"     : "# Makefile",
    "dockerfile"   : "# Dockerfile",
    "markdown"     : "<!-- Markdown -->",
    "cmake"        : "# CMake",
    "dockerfile"   : "# Dockerfile",
    }

    programming_languages_to_file_extensions = json.load(open('utils/programming-languages-to-file-extensions.json'))
    need2del = []
    for key in programming_languages_to_file_extensions.keys():
        if key.lower() not in LANGUAGE_TAG:
            need2del.append(key)

    for key in need2del:
        del programming_languages_to_file_extensions[key]

    ext_to_programming_languages = {}
    want_languages = []
    for key in programming_languages_to_file_extensions:
        for item in programming_languages_to_file_extensions[key]:
            ext_to_programming_languages[item] = key
            want_languages.append(item)

    ext = '.'+obj.split('.')[-1]
    with open('utils/keep.txt', 'r') as f:
        keep_files = f.readlines()
        keep_files = [l.strip() for l in keep_files]
    #print(ext)
    if ext not in want_languages:
        if obj in keep_files:
            return True
        return False
    else:
        return True