from _judge.languages import _cpp_lang_config ,_c_lang_config,_py3_lang_config,_go_lang_config,_java_lang_config
# 定义python,java,go,c++的编译和运行命令
def chose(language):
    if language == 'c':
        return _c_lang_config['compile'], _c_lang_config['run']
    if language == 'cpp':
        return _cpp_lang_config ['compile'], _cpp_lang_config['run']
    elif language == 'java':
        return _java_lang_config['compile'], _java_lang_config['run']

    elif language == 'python':
        return _py3_lang_config['compile'], _py3_lang_config['run']
    else:
        return _go_lang_config['compile'], _go_lang_config['run']
    