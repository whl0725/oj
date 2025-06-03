from flask import Flask,request,Response
import json
import uuid
import os
from _judge.config import JUDGER_WORKSPACE,loger
import hashlib

from compiler import Compiler
#from _judge.config import TOKEN
from until import chose

from Client import Client

from service import JudgeService

TOKEN = '123456'
app = Flask(__name__)
app.debug = True

# 创建心跳服务实例
heartbeat_service = None
if os.getenv('ENABLE_HEARTBEAT'):
    heartbeat_service = JudgeService()
    # 在应用启动时直接启动心跳服务
    heartbeat_service.start()

class SubmissionEnv():
    def __init__(self, judger_workspace, submission_id):
        self.work_dir = os.path.join(judger_workspace, submission_id)
        
    def __enter__(self):
        try:
            # 确保父目录存在
            os.makedirs(self.work_dir, exist_ok=True)     
            os.chmod(self.work_dir, 0o711)
        except Exception as e:
            loger.exception(e)
            raise Exception(f"failed to create runtime dir: {str(e)}")
        return self.work_dir
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # try:
        #     # 使用系统命令快速删除目录
        #     import shutil
        #     shutil.rmtree(self.work_dir, ignore_errors=True)
        # except Exception as e:
        #     loger.exception(f"Error cleaning up directory {self.work_dir}: {str(e)}")
        pass


def judge_Test(src,max_cpu_time,max_memory,mode,language,test):
    submission_id = uuid.uuid4().hex
    with SubmissionEnv(JUDGER_WORKSPACE, submission_id=str(submission_id)) as env:
        work_crl = env
        compile,run = chose(language=language)
        
        if compile:
            # 使用 with 语句自动关闭文件
            src_path = os.path.join(work_crl, compile["src_name"])
            try:
                # 写入源代码
                src = """
# include <stdio.h>
int main(){
    int n;
    scanf("%d", &n);
    printf("%d", n);
    return 0;
}
"""
                with open(src_path, "w", encoding="utf-8") as f:
                    f.write(src)
                os.chmod(src_path, 0o777)
                
                exe_path = Compiler().compile(compile=compile,
                                            src_path=src_path,
                                            output_dir=work_crl)
                
                # 编译完成后立即删除源文件
                # try:
                #     os.remove(src_path)
                # except:
                #     pass
                    
                if isinstance(exe_path, dict):
                    return {
                        "status": "Compile Error",
                        "error": exe_path.get("error", "Unknown compilation error")
                    }
                
            except Exception as e:
                loger.exception(e)
                return {
                    "status": "Compile Error",
                    "error": str(e)
                }

        # 写入测试用例
        test_dir = os.path.join(work_crl, "test")
        os.makedirs(test_dir, exist_ok=True)
        os.chmod(test_dir, 0o755)
     
        # 创建测试用例文件
        try:
            # 预处理所有测试用例数据
            test_cases_info = {}
            for i, test_case in enumerate(test, 1):
                input_data = test_case['input'].encode("utf-8")
                output_data = test_case['output'].encode("utf-8")
                output_stripped = output_data.rstrip()
                
                test_cases_info[i] = {
                    "input_name": f"{i}.in",
                    "input_data": input_data,
                    "input_size": len(input_data),
                    "output_name": f"{i}.out",
                    "output_sha256": hashlib.sha256(output_data).hexdigest(),
                    "output_size": len(output_data),
                    "stripped_output_sha256": hashlib.sha256(output_stripped).hexdigest()
                }
            
            # 批量写入文件
            for i, case_info in test_cases_info.items():
                with open(os.path.join(test_dir, case_info["input_name"]), "wb", 
                         buffering=64*1024) as f:
                    f.write(case_info["input_data"])
                
            # 写入 info 文件
            info = {
                "test_case_number": len(test),
                "spj": False,
                "test_cases": {i: {k: v for k, v in case_info.items() 
                                 if k != "input_data"}
                              for i, case_info in test_cases_info.items()}
            }
            
            with open(os.path.join(test_dir, "info"), "w", encoding="utf-8") as f:
                json.dump(info, f)

        except Exception as e:
            loger.exception(f"Error writing test cases: {str(e)}")
            return f"Error writing test cases: {str(e)}"

        # 下面执行代码
        test_case_dir = os.path.join(work_crl, "test")
        judge_client = Client(
            run_config=run,
            exe_path=exe_path,
            max_cpu_time=max_cpu_time,
            max_memory=max_memory,
            test_case_dir=test_case_dir,
            submission_dir=work_crl,
            memory_limit_check_only=False,
            max_stack=128 * 1024 * 1024
        )
        run_result = judge_client.run()
        return run_result        



def judge_SPJ(data):
    submission_id = uuid.uuid4().hex
    return submission_id

@app.route('/',methods=['POST'])
def judger():  # put application's code here
    token = request.headers.get('judgertoken')
    if(token != TOKEN):
        return 'Wrong Token!', 403
    try:
        data = request.get_json()
        if(data['type'] == 'spj'):
            storage=judge_SPJ(data)
        elif(data['type'] == 'test'):
            storage=judge_Test(**data['data'])
        return Response(json.dumps(storage), mimetype='application/json', status=200)
    except Exception as e:
        return 'Wrong Data!', 403
    

@app.teardown_appcontext
def cleanup(exception=None):
    if heartbeat_service is not None:
        heartbeat_service.stop()

if __name__ == '__main__':
    try:
        app.run()
    finally:
        if heartbeat_service is not None:
            heartbeat_service.stop()
