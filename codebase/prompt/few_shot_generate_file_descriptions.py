INDEX_FILE_DESCRIPTION_INSTRUCTION_PROMPT = """
You are a project architect and you can summarize the description of each file through the graph structure of the project, containing the call relationships between their functions。
Follow these rules strictly:
- Read and understand the graph index,The diagram structure may be input to you in csv format or json format, you need to understand the graph structure.
- Based on the file paths in the graph structure, each file gives a summary of the relationships between functions within the file, forming a description of the file. Also cross-file direct function relationships need to be described clearly, putting cross-file specific paths into the description.
- Ensure the output can be parsed by Python json.loads.
- The output is strictly in json format, file_path is the path to the file, and descriptions is a summary description of the file.
"""
INDEX_FILE_DESCRIPTION_SHORT_EXAMPLE_PROMPT = """
Here is some examples:

Input:
class,id,file_path,source,target
FileAction.__str__,FileAction,test/repo_manager.py,,
RepoManager.__init__,RepoManager,test/repo_manager.py,RepoManager.__init__,RepoManager._load_readme
RepoManager.set_root_path,RepoManager,test/repo_manager.py,,
RepoManager.get_repo_path,RepoManager,test/repo_manager.py,,
RepoManager.add_focus_file,RepoManager,test/repo_manager.py,,
RepoManager.remove_focus_file,RepoManager,test/repo_manager.py,,
RepoManager.set_focus_file,RepoManager,test/repo_manager.py,RepoManager.set_focus_file,RepoManager.add_focus_file
RepoManager.get_focus_files_content,RepoManager,test/repo_manager.py,,
RepoManager.get_file_content,RepoManager,test/repo_manager.py,,
RepoManager.apply_file_actions,RepoManager,test/repo_manager.py,RepoManager.apply_file_actions,RepoManager._generate_file_tree_str
RepoManager._add_file,RepoManager,test/repo_manager.py,,
RepoManager._remove_file,RepoManager,test/repo_manager.py,,
RepoManager._modify_file,RepoManager,test/repo_manager.py,,
RepoManager._generate_file_tree_str,RepoManager,test/repo_manager.py,,
RepoManager._tree_iter,RepoManager,test/repo_manager.py,,
RepoManager._file_descriptions,RepoManager,test/repo_manager.py,,
RepoManager._generate_file_descriptions_json,RepoManager,test/repo_manager.py,,
RepoManager._descriptions_iter,RepoManager,test/repo_manager.py,RepoManager._descriptions_iter,RepoManager._file_descriptions
RepoManager._load_readme,RepoManager,test/repo_manager.py,,
testfunc,,test/hellotest/new.py,testfunc,hello
hello,,test/hellotest/hel.py,,

Output:
[
    {
        "file_path": "test/repo_manager.py",
        "descriptions": "The file contains classes and functions related to repository management. The 'RepoManager' class has functions like 'init', 'set_root_path', 'get_repo_path', 'add_focus_file', 'remove_focus_file', 'set_focus_file', 'get_focus_files_content', 'get_file_content', 'apply_file_actions', '_add_file', '_remove_file', '_modify_file', '_generate_file_tree_str', '_tree_iter', '_file_descriptions', '_generate_file_descriptions_json', '_descriptions_iter', '_load_readme'. Function relationships include 'RepoManager.init' calling 'RepoManager._load_readme', 'RepoManager.set_focus_file' calling 'RepoManager.add_focus_file', 'RepoManager.apply_file_actions' calling 'RepoManager._generate_file_tree_str', and 'RepoManager._descriptions_iter' calling 'RepoManager._file_descriptions'."
    },
    {
        "file_path": "test/hellotest/new.py",
        "descriptions": "The file 'new.py' contains the function 'testfunc' which has a direct relationship with the 'hello' function in the file 'hel.py'."
    },
    {
        "file_path": "test/hellotest/hel.py",
        "descriptions": "The file 'hel.py' contains the function 'hello'. It is called by the function 'testfunc' in the file 'new.py'."
    }
]
"""
INDEX_FILE_DESCRIPTION_LONG_EXAMPLE_PROMPT = """
Here is some examples:

Input:
class,id,file_path,source,target
BaseNode.__init__,BaseNode,nodes/base_node.py,,
BaseNode.run,BaseNode,nodes/base_node.py,,
OpenAINode.__init__,OpenAINode,nodes/openai/openai.py,,
OpenAINode.complete,OpenAINode,nodes/openai/openai.py,OpenAINode.complete,OpenAINode._make_completion
OpenAINode.chat,OpenAINode,nodes/openai/openai.py,OpenAINode.chat,OpenAINode._make_completion
OpenAINode.chat_with_prompt_template,OpenAINode,nodes/openai/openai.py,OpenAINode.chat_with_prompt_template,OpenAINode._make_completion
OpenAINode.chat_with_message,OpenAINode,nodes/openai/openai.py,OpenAINode.chat_with_message,OpenAINode._make_completion
OpenAINode.chat_with_messages,OpenAINode,nodes/openai/openai.py,OpenAINode.chat_with_messages,OpenAINode._make_completion
OpenAINode._make_completion,OpenAINode,nodes/openai/openai.py,OpenAINode._make_completion,OpenAINode.add_single_message
OpenAINode.add_function,OpenAINode,nodes/openai/openai.py,,
OpenAINode.add_single_message,OpenAINode,nodes/openai/openai.py,,
OpenAINode.add_system_message,OpenAINode,nodes/openai/openai.py,OpenAINode.add_system_message,OpenAINode.add_single_message
OpenAINode.add_role,OpenAINode,nodes/openai/openai.py,OpenAINode.add_role,OpenAINode.add_single_message
OpenAINode.add_content,OpenAINode,nodes/openai/openai.py,,
AsyncOpenAINode.__init__,AsyncOpenAINode,nodes/openai/openai.py,,
AsyncOpenAINode.complete,AsyncOpenAINode,nodes/openai/openai.py,AsyncOpenAINode.complete,AsyncOpenAINode._make_completion
AsyncOpenAINode.chat,AsyncOpenAINode,nodes/openai/openai.py,AsyncOpenAINode.chat,AsyncOpenAINode._make_completion
AsyncOpenAINode.chat_with_prompt_template,AsyncOpenAINode,nodes/openai/openai.py,AsyncOpenAINode.chat_with_prompt_template,AsyncOpenAINode._make_completion
AsyncOpenAINode.chat_with_message,AsyncOpenAINode,nodes/openai/openai.py,AsyncOpenAINode.chat_with_message,AsyncOpenAINode._make_completion
AsyncOpenAINode.chat_with_messages,AsyncOpenAINode,nodes/openai/openai.py,AsyncOpenAINode.chat_with_messages,AsyncOpenAINode._make_completion
AsyncOpenAINode._make_completion,AsyncOpenAINode,nodes/openai/openai.py,AsyncOpenAINode._make_completion,AsyncOpenAINode.add_single_message
AsyncOpenAINode.add_function,AsyncOpenAINode,nodes/openai/openai.py,,
AsyncOpenAINode.add_single_message,AsyncOpenAINode,nodes/openai/openai.py,,
AsyncOpenAINode.add_system_message,AsyncOpenAINode,nodes/openai/openai.py,AsyncOpenAINode.add_system_message,AsyncOpenAINode.add_single_message
AsyncOpenAINode.add_role,AsyncOpenAINode,nodes/openai/openai.py,AsyncOpenAINode.add_role,AsyncOpenAINode.add_single_message
AsyncOpenAINode.add_content,AsyncOpenAINode,nodes/openai/openai.py,,
FunctionParameter.dict,FunctionParameter,nodes/openai/openai_model.py,,
AsyncOpenAIStreamResp.__init__,AsyncOpenAIStreamResp,nodes/openai/openai_model.py,,
AsyncOpenAIStreamResp.__aiter__,AsyncOpenAIStreamResp,nodes/openai/openai_model.py,,
AsyncOpenAIStreamResp.__anext__,AsyncOpenAIStreamResp,nodes/openai/openai_model.py,,

Output:
[
    {
        "file_path": "nodes/base_node.py",
        "descriptions": "This file contains the BaseNode class, which is foundational but has no direct function relationships with other files."
    },
    {
        "file_path": "nodes/openai/openai.py",
        "descriptions": "Contains OpenAINode and AsyncOpenAINode classes. OpenAINode includes various methods like complete, chat, chat_with_prompt_template, chat_with_message, chat_with_messages, all calling _make_completion. _make_completion calls add_single_message. Other methods are add_function, add_single_message, add_system_message, and add_content. AsyncOpenAINode mirrors these methods and relationships. add_system_message and add_role in both classes also call add_single_message."
    },
    {
        "file_path": "nodes/openai/openai_model.py",
        "descriptions": "Includes the AsyncOpenAIStreamResp and FunctionParameter classes. AsyncOpenAIStreamResp has methods init, aiter, and anext with no external function calls. FunctionParameter has a method dict with no external function calls."
    }
]

Input:
class,id,file_path,source,target
set_password,,tree-sitter-python/examples/tabs.py,,
main,,tree-sitter-python/examples/mixed-spaces-tabs.py,,
TokenTests.test_backslash,TokenTests,tree-sitter-python/examples/python3.8_grammar.py,,
TokenTests.test_plain_integers,TokenTests,tree-sitter-python/examples/python3.8_grammar.py,,
TokenTests.test_long_integers,TokenTests,tree-sitter-python/examples/python3.8_grammar.py,,
TokenTests.test_floats,TokenTests,tree-sitter-python/examples/python3.8_grammar.py,,
TokenTests.test_float_exponent_tokenization,TokenTests,tree-sitter-python/examples/python3.8_grammar.py,,
TokenTests.test_underscore_literals,TokenTests,tree-sitter-python/examples/python3.8_grammar.py,,
TokenTests.test_string_literals,TokenTests,tree-sitter-python/examples/python3.8_grammar.py,,
TokenTests.test_ellipsis,TokenTests,tree-sitter-python/examples/python3.8_grammar.py,,
TokenTests.test_eof_error,TokenTests,tree-sitter-python/examples/python3.8_grammar.py,,
CNS.__init__,CNS,tree-sitter-python/examples/python3.8_grammar.py,,
CNS.__setitem__,CNS,tree-sitter-python/examples/python3.8_grammar.py,,
CNS.__getitem__,CNS,tree-sitter-python/examples/python3.8_grammar.py,,
GrammarTests.test_eval_input,GrammarTests,tree-sitter-python/examples/python3.8_grammar.py,,
GrammarTests.test_var_annot_basics,GrammarTests,tree-sitter-python/examples/python3.8_grammar.py,,
GrammarTests.one,GrammarTests,tree-sitter-python/examples/python3.8_grammar.py,,
GrammarTests.test_var_annot_syntax_errors,GrammarTests,tree-sitter-python/examples/python3.8_grammar.py,,
GrammarTests.test_var_annot_basic_semantics,GrammarTests,tree-sitter-python/examples/python3.8_grammar.py,,
GrammarTests.f,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.f_OK,GrammarTests,tree-sitter-python/examples/python3.8_grammar.py,,
GrammarTests.fbad,GrammarTests,tree-sitter-python/examples/python3.8_grammar.py,,
GrammarTests.f2bad,GrammarTests,tree-sitter-python/examples/python3.8_grammar.py,,
C.__init__,C,tree-sitter-python/examples/python3.8_grammar.py,,
Cbad2.test_var_annot_metaclass_semantics,Cbad2,tree-sitter-python/examples/python3.8_grammar.py,,
CMeta.__prepare__,CMeta,tree-sitter-python/examples/python3.8_grammar.py,,
CC.test_var_annot_module_semantics,CC,tree-sitter-python/examples/python3.8_grammar.py,,
CC.test_var_annot_in_module,CC,tree-sitter-python/examples/python3.8_grammar.py,,
CC.test_var_annot_simple_exec,CC,tree-sitter-python/examples/python3.8_grammar.py,,
CC.test_var_annot_custom_maps,CC,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.__init__,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.__setitem__,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.__getitem__,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.test_var_annot_refleak,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.test_funcdef,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.f1,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.f2,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.f3,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.a1,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.a2,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.v0,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.v1,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.v2,CNS2,tree-sitter-python/examples/python3.8_grammar.py,CNS2.v2,CNS2.v1
CNS2.d01,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.d11,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.d21,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.d02,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.d12,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.d22,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.d01v,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.d11v,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.d21v,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.d02v,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.d12v,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.d22v,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.pos0key1,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.pos2key2,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.pos2key2dict,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
CNS2.f,CNS2,tree-sitter-python/examples/python3.8_grammar.py,,
Spam.f,Spam,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.null,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.f,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_lambdef,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_simple_stmt,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.foo,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_expr_stmt,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_former_statements_refer_to_builtins,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_del_stmt,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_pass_stmt,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_break_stmt,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_continue_stmt,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_break_continue_loop,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_inner,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_return,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.g1,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.g2,Ham,tree-sitter-python/examples/python3.8_grammar.py,Ham.g2,Ham.g1
Ham.test_break_in_finally,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_continue_in_finally,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_return_in_finally,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.g3,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_yield,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.g,Ham,tree-sitter-python/examples/python3.8_grammar.py,Ham.g,Ham.f
Ham.test_yield_in_comprehensions,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_raise,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_import,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_global,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_nonlocal,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_assert,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.testAssert2,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_if,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_while,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Ham.test_for,Ham,tree-sitter-python/examples/python3.8_grammar.py,,
Squares.__init__,Squares,tree-sitter-python/examples/python2-grammar.py,,
Squares.__len__,Squares,tree-sitter-python/examples/python2-grammar.py,,
Squares.__getitem__,Squares,tree-sitter-python/examples/python2-grammar.py,,
Squares.test_try,Squares,tree-sitter-python/examples/python3.8_grammar.py,,
Squares.test_suite,Squares,tree-sitter-python/examples/python3.8_grammar.py,,
Squares.test_test,Squares,tree-sitter-python/examples/python3.8_grammar.py,,
Squares.test_comparison,Squares,tree-sitter-python/examples/python3.8_grammar.py,,
Squares.test_binary_mask_ops,Squares,tree-sitter-python/examples/python3.8_grammar.py,,
Squares.test_shift_ops,Squares,tree-sitter-python/examples/python3.8_grammar.py,,
Squares.test_additive_ops,Squares,tree-sitter-python/examples/python3.8_grammar.py,,
Squares.test_multiplicative_ops,Squares,tree-sitter-python/examples/python3.8_grammar.py,,
Squares.test_unary_ops,Squares,tree-sitter-python/examples/python3.8_grammar.py,,
Squares.test_selectors,Squares,tree-sitter-python/examples/python3.8_grammar.py,,
Squares.test_atoms,Squares,tree-sitter-python/examples/python3.8_grammar.py,,
Squares.test_classdef,Squares,tree-sitter-python/examples/python3.8_grammar.py,,
C.meth1,C,tree-sitter-python/examples/python2-grammar.py,,
C.meth2,C,tree-sitter-python/examples/python2-grammar.py,,
C.meth3,C,tree-sitter-python/examples/python2-grammar.py,,
C.class_decorator,C,tree-sitter-python/examples/python2-grammar.py,,
G.test_dictcomps,G,tree-sitter-python/examples/python3.8_grammar.py,,
G.test_listcomps,G,tree-sitter-python/examples/python3.8_grammar.py,,
G.test_in_func,G,tree-sitter-python/examples/python2-grammar.py,,
G.test_nested_front,G,tree-sitter-python/examples/python2-grammar.py,,
G.test_genexps,G,tree-sitter-python/examples/python3.8_grammar.py,,
G.test_comprehension_specials,G,tree-sitter-python/examples/python3.8_grammar.py,,
G.test_with_statement,G,tree-sitter-python/examples/python2-grammar.py,,
manager.__enter__,manager,tree-sitter-python/examples/python2-grammar.py,,
manager.__exit__,manager,tree-sitter-python/examples/python2-grammar.py,,
manager.test_if_else_expr,manager,tree-sitter-python/examples/python3.8_grammar.py,,
manager._checkeval,manager,tree-sitter-python/examples/python2-grammar.py,,
manager.test_paren_evaluation,manager,tree-sitter-python/examples/python3.8_grammar.py,,
manager.test_matrix_mul,manager,tree-sitter-python/examples/python3.8_grammar.py,,
M.__matmul__,M,tree-sitter-python/examples/python3.8_grammar.py,,
M.__imatmul__,M,tree-sitter-python/examples/python3.8_grammar.py,,
M.test_async_await,M,tree-sitter-python/examples/python3.8_grammar.py,,
M.test,M,tree-sitter-python/examples/python3.8_grammar.py,,
M.sum,M,tree-sitter-python/examples/python3.8_grammar.py,,
M.decorator,M,tree-sitter-python/examples/python3.8_grammar.py,,
M.test2,M,tree-sitter-python/examples/python3.8_grammar.py,,
M.test_async_for,M,tree-sitter-python/examples/python3.8_grammar.py,,
AIter.__aiter__,AIter,tree-sitter-python/examples/python3.8_grammar.py,,
AIter.__anext__,AIter,tree-sitter-python/examples/python3.8_grammar.py,,
AIter.foo,AIter,tree-sitter-python/examples/python3.8_grammar.py,,
AIter.test_async_with,AIter,tree-sitter-python/examples/python3.8_grammar.py,,
manager.__aenter__,manager,tree-sitter-python/examples/python3.8_grammar.py,,
manager.__aexit__,manager,tree-sitter-python/examples/python3.8_grammar.py,,
manager.foo,manager,tree-sitter-python/examples/python3.8_grammar.py,,
Foo.bar,Foo,tree-sitter-python/examples/compound-statement-without-trailing-newline.py,,
TokenTests.testBackslash,TokenTests,tree-sitter-python/examples/python2-grammar.py,,
TokenTests.testPlainIntegers,TokenTests,tree-sitter-python/examples/python2-grammar.py,,
TokenTests.testLongIntegers,TokenTests,tree-sitter-python/examples/python2-grammar.py,,
TokenTests.testUnderscoresInNumbers,TokenTests,tree-sitter-python/examples/python3-grammar.py,,
TokenTests.testFloats,TokenTests,tree-sitter-python/examples/python2-grammar.py,,
TokenTests.testEllipsis,TokenTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.testEvalInput,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.testFuncdef,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.f1,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.f2,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.f3,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.a1,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.a2,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.v0,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.v1,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.v2,GrammarTests,tree-sitter-python/examples/python2-grammar.py,GrammarTests.v2,GrammarTests.v1
GrammarTests.d01,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.d11,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.d21,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.d02,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.d12,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.d22,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.d01v,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.d11v,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.d21v,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.d02v,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.d12v,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.d22v,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.pos0key1,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.pos2key2,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.pos2key2dict,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.null,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.testLambdef,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.testSimpleStmt,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.foo,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.testExprStmt,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.testDelStmt,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.testPassStmt,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.testBreakStmt,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.testContinueStmt,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.test_break_continue_loop,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.test_inner,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.testReturn,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.g1,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.g2,GrammarTests,tree-sitter-python/examples/python3-grammar.py,GrammarTests.g2,GrammarTests.g1
GrammarTests.testYield,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.testRaise,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.testImport,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.testGlobal,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.testNonlocal,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.testAssert,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.testIf,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.testWhile,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
GrammarTests.testFor,GrammarTests,tree-sitter-python/examples/python3-grammar.py,,
Squares.testTry,Squares,tree-sitter-python/examples/python2-grammar.py,,
Squares.testSuite,Squares,tree-sitter-python/examples/python2-grammar.py,,
Squares.testTest,Squares,tree-sitter-python/examples/python2-grammar.py,,
Squares.testComparison,Squares,tree-sitter-python/examples/python2-grammar.py,,
Squares.testBinaryMaskOps,Squares,tree-sitter-python/examples/python2-grammar.py,,
Squares.testShiftOps,Squares,tree-sitter-python/examples/python2-grammar.py,,
Squares.testAdditiveOps,Squares,tree-sitter-python/examples/python2-grammar.py,,
Squares.testMultiplicativeOps,Squares,tree-sitter-python/examples/python2-grammar.py,,
Squares.testUnaryOps,Squares,tree-sitter-python/examples/python2-grammar.py,,
Squares.testSelectors,Squares,tree-sitter-python/examples/python2-grammar.py,,
Squares.testAtoms,Squares,tree-sitter-python/examples/python2-grammar.py,,
Squares.testClassdef,Squares,tree-sitter-python/examples/python2-grammar.py,,
G.testDictcomps,G,tree-sitter-python/examples/python3-grammar.py,,
G.testListcomps,G,tree-sitter-python/examples/python2-grammar.py,,
G.testGenexps,G,tree-sitter-python/examples/python2-grammar.py,,
G.testComprehensionSpecials,G,tree-sitter-python/examples/python2-grammar.py,,
manager.testIfElseExpr,manager,tree-sitter-python/examples/python2-grammar.py,,
manager.testStringLiterals,manager,tree-sitter-python/examples/python2-grammar.py,,
manager.test_main,manager,tree-sitter-python/examples/python2-grammar.py,,
hi,,tree-sitter-python/examples/multiple-newlines.py,,
bye,,tree-sitter-python/examples/multiple-newlines.py,,
GrammarTests.f4,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.f5,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.v3,GrammarTests,tree-sitter-python/examples/python2-grammar.py,GrammarTests.v3,GrammarTests.v2
GrammarTests.d31v,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.d32v,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
GrammarTests.testPrintStmt,GrammarTests,tree-sitter-python/examples/python2-grammar.py,,
Gulp.write,Gulp,tree-sitter-python/examples/python2-grammar.py,,
Gulp.driver,Gulp,tree-sitter-python/examples/python2-grammar.py,Gulp.driver,Gulp.tellme
Gulp.tellme,Gulp,tree-sitter-python/examples/python2-grammar.py,Gulp.tellme,Gulp.driver
Gulp.testDelStmt,Gulp,tree-sitter-python/examples/python2-grammar.py,,
Gulp.testPassStmt,Gulp,tree-sitter-python/examples/python2-grammar.py,,
Gulp.testBreakStmt,Gulp,tree-sitter-python/examples/python2-grammar.py,,
Gulp.testContinueStmt,Gulp,tree-sitter-python/examples/python2-grammar.py,,
Gulp.test_break_continue_loop,Gulp,tree-sitter-python/examples/python2-grammar.py,,
Gulp.test_inner,Gulp,tree-sitter-python/examples/python2-grammar.py,,
Gulp.testReturn,Gulp,tree-sitter-python/examples/python2-grammar.py,,
Gulp.g1,Gulp,tree-sitter-python/examples/python2-grammar.py,,
Gulp.g2,Gulp,tree-sitter-python/examples/python2-grammar.py,Gulp.g2,Gulp.g1
Gulp.testYield,Gulp,tree-sitter-python/examples/python2-grammar.py,,
Gulp.testRaise,Gulp,tree-sitter-python/examples/python2-grammar.py,,
Gulp.testImport,Gulp,tree-sitter-python/examples/python2-grammar.py,,
Gulp.testGlobal,Gulp,tree-sitter-python/examples/python2-grammar.py,,
Gulp.testExec,Gulp,tree-sitter-python/examples/python2-grammar.py,,
Gulp.testAssert,Gulp,tree-sitter-python/examples/python2-grammar.py,,
Gulp.testIf,Gulp,tree-sitter-python/examples/python2-grammar.py,,
Gulp.testWhile,Gulp,tree-sitter-python/examples/python2-grammar.py,,
Gulp.testFor,Gulp,tree-sitter-python/examples/python2-grammar.py,,
MyClass.hello,MyClass,tree-sitter-python/test/tags/main.py,,
MyClass.main,MyClass,tree-sitter-python/test/tags/main.py,,
g,,tree-sitter-python/test/highlight/parameters.py,,

Output:
[
    {
        "file_path": "tree-sitter-python/examples/tabs.py",
        "descriptions": "This file contains a single function 'set_password' with no internal or cross-file function relationships."
    },
    {
        "file_path": "tree-sitter-python/examples/mixed-spaces-tabs.py",
        "descriptions": "This file contains a single function 'main' with no internal or cross-file function relationships."
    },
    {
        "file_path": "tree-sitter-python/examples/python3.8_grammar.py",
        "descriptions": "This file includes multiple classes (TokenTests, CNS, GrammarTests, C, Cbad2, CMeta, CC, CNS2, Ham) with various functions. 'CNS2.v2' calls 'CNS2.v1'. Key classes and their functions include: TokenTests with tests for various token types, CNS with item access methods, GrammarTests with multiple test methods, C with initialization, Cbad2 for metaclass semantics, CMeta for class preparation, CC for module semantics tests, CNS2 with test functions and cross-function calls, and Ham with tests for lambda definitions, statements, and loops. 'Ham.g2' calls 'Ham.g1', and 'Ham.g' calls 'Ham.f'."
    },
    {
        "file_path": "tree-sitter-python/examples/python2-grammar.py",
        "descriptions": "This file includes multiple classes (Squares, C, G, manager, GrammarTests, Gulp) with various functions. 'GrammarTests.v2' calls 'GrammarTests.v1', and 'GrammarTests.v3' calls 'GrammarTests.v2'. 'Gulp.driver' and 'Gulp.tellme' have mutual calls. 'Gulp.g2' calls 'Gulp.g1'. Key classes and their functions include: Squares with item access and tests methods, C with methods and decorators, G with comprehension and statement tests, manager with context management and test methods, GrammarTests with various test functions, and Gulp with statement tests and mutual function calls."
    },
    {
        "file_path": "tree-sitter-python/examples/python3-grammar.py",
        "descriptions": "This file contains the GrammarTests class with various test functions. 'GrammarTests.g2' calls 'GrammarTests.g1'. It includes tests for lambda definitions, statements, import, global and nonlocal usage, assert statements, control flow structures like if, while, for loops, and yield statements."
    },
    {
        "file_path": "tree-sitter-python/examples/compound-statement-without-trailing-newline.py",
        "descriptions": "This file contains a single class 'Foo' with one function 'bar' that has no internal or cross-file function relationships."
    },
    {
        "file_path": "tree-sitter-python/test/tags/main.py",
        "descriptions": "This file contains the MyClass class with functions 'hello' and 'main', both having no internal or cross-file function relationships."
    },
    {
        "file_path": "tree-sitter-python/test/highlight/parameters.py",
        "descriptions": "This file contains a single global function 'g' with no internal or cross-file function relationships."
    }
]

"""

INDEX_FILE_DESCRIPTION_HINT = """
You should only respond in JSON format as described below
Response Format:
[
    {
        "file_path": "",
        "descriptions": ""
    }
]
You must abide by the following rules:
- Do not output any other information and do not contain quotation marks, such as `, \", \' and so on.
- Ensure the output can be parsed by Python json.loads.
- Don't output in markdown format, something like ```json or ```,just output in the corresponding string format
"""
