import os
import shlex
from _judge.config import log_url
import _judge

class Compiler():
    def compile(self, compile, src_path, output_dir):
        # 从编译配置中获取编译命令
        command = compile["compile_command"]
        # 获取当前工作目录作为基准
        cwd = os.getcwd()
        # 转换为相对路径（相对于output_dir）
        src_path = os.path.relpath(src_path, output_dir)
        exe_path = compile["exe_name"]  # 直接使用文件名，因为我们会切换到output_dir       
        # 格式化编译命令，替换占位符为实际路径
        command = command.format(
            src_path=src_path,
            exe_dir=".",  # 使用当前目录，因为我们会切换到output_dir
            exe_path=exe_path
        )
        # 构建编译器的输出文件路径（使用相对路径）
        compiler_out = "compiler.out"  
        log_path = "judger.log"     
        # 切换到输出目录
        os.chdir(output_dir)
        # 确保编译器输出文件存在且可写
        try:
            with open(compiler_out, 'w') as f:
                pass
        except IOError as e:
            os.chdir(cwd)  # 恢复原始工作目录
            raise Exception(f"Cannot create compiler output file: {e}")           
        # 使用shlex.split将编译命令分割成可执行的命令和参数列表
        _command = shlex.split(command)
        # 获取编译环境变量配置
        env = compile.get("env", [])
        env.append("PATH=" + os.getenv("PATH"))
        try:
            result = _judge.run(max_cpu_time=compile["max_cpu_time"],
                              max_real_time=compile["max_real_time"],
                              max_memory=compile["max_memory"],
                              max_stack=256 * 1024 * 1024,
                              max_output_size=256 * 1024 * 1024,
                              max_process_number=-1,
                              exe_path=_command[0],
                              input_path="/dev/null",
                              output_path=compiler_out,
                              error_path=compiler_out,
                              args=_command[1::],
                              env=env,
                              log_path=log_path,
                              seccomp_rule_name=None,
                              uid=0,
                              gid=0)
            if result["result"] != _judge.RESULT_SUCCESS:
                # 编译失败，读取错误信息
                error_message = ""
                try:
                    with open(compiler_out, 'r', encoding='utf-8') as f:
                        error_message = f.read().strip()
                except:
                    error_message = "Unknown compilation error"
                
                # 确保返回的错误信息是字符串
                if not isinstance(error_message, str):
                    error_message = str(error_message)
                
                return {
                    "success": False,
                    "error": error_message
                }
            else:
                # 编译成功
                exe_full_path = os.path.join(output_dir, exe_path)
                if os.path.exists(exe_full_path):
                    os.chmod(exe_full_path, 0o755)
                    
                # 清理临时文件
                for temp_file in [compiler_out, log_path]:
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    except:
                        pass
                        
                return os.path.relpath(exe_full_path)

        except Exception as e:
            # 确保返回的错误信息是字符串
            error_message = str(e)
            return {
                "success": False,
                "error": error_message
            }
        finally:
            os.chdir(cwd)
    
    