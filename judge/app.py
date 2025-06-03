import sys
# 在文件开头添加这行，增加整数字符串转换的限制
sys.set_int_max_str_digits(0)  # 设置为0表示不限制

# 或者设置一个足够大的值
# sys.set_int_max_str_digits(10000000)  # 设置一个足够大的值

from flask import Flask,request,Response, jsonify
import json
import uuid
import os
from _judge.config import JUDGER_WORKSPACE,loger, TOKEN,MAX_WORKERS,BATCH_SIZE
import hashlib
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
from compiler import Compiler
from until import chose
from Client import Client
from service import JudgeService


app = Flask(__name__)
app.debug = True

# 创建心跳服务实例
heartbeat_service = None
if os.getenv('ENABLE_HEARTBEAT'):
    print("Heartbeat service is enabled")
    heartbeat_service = JudgeService()
    # 在应用启动时直接启动心跳服务
    heartbeat_service.start()

# 定义错误码
ERROR_CODES = {
    "COMPILE_ERROR": {"code": 400, "message": "Compilation failed"},
    "Error writing test cases": {"code": 401, "message": "Runtime error occurred"},
    "Error creating judge client": {"code": 402, "message": "Time limit exceeded"},
    "Runtime Error":{"code":403,"message":"Runtime Error"},

    "SYSTEM_ERROR": {"code": 500, "message": "Internal system error"},
    "INVALID_TOKEN": {"code": 501, "message": "Invalid authentication token"},
    "BAD_REQUEST": {"code": 502, "message": "Bad request format"}
}



def create_error_response(error_type, details=None):
    """创建标准错误响应"""
    error = ERROR_CODES[error_type].copy()
    if details:
        error["details"] = details
    return jsonify(error), error["code"]

class SubmissionEnv():
    def __init__(self, judger_workspace, submission_id):
        self.work_dir = os.path.join(judger_workspace, submission_id)
        self.base_dir = judger_workspace
        
    def __enter__(self):
        try:
            # 首先确保基础工作目录存在
            os.makedirs(self.base_dir, exist_ok=True)
            os.chmod(self.base_dir, 0o755)
            
            # 然后创建提交专用目录
            os.makedirs(self.work_dir, exist_ok=True)     
            os.chmod(self.work_dir, 0o711)
            
            return self.work_dir
            
        except Exception as e:
            loger.exception(f"Failed to create directories: base_dir={self.base_dir}, work_dir={self.work_dir}")
            raise Exception(f"failed to create runtime dir: {str(e)}")
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            # 使用系统命令快速删除目录
            import shutil
            if os.path.exists(self.work_dir):
                shutil.rmtree(self.work_dir, ignore_errors=True)
        except Exception as e:
            loger.exception(f"Error cleaning up directory {self.work_dir}: {str(e)}")
    

def write_test_cases(test_dir, test_cases, start_idx, end_idx,mode = None):
    """批量写入测试用例"""
    try:
        # 确保测试用例目录存在
        os.makedirs(test_dir, exist_ok=True)
        os.chmod(test_dir, 0o755)
        
        batch_info = {}
        for i in range(start_idx, end_idx):
            if i >= len(test_cases):
                break
                
            test_case = test_cases[i]
            case_num = i + 1
            
            input_data = test_case['input'].encode("utf-8")
            if mode == None:
                output_data = test_case['output'].encode("utf-8")
                output_stripped = output_data.rstrip()
            batch_info[case_num] = {
                "input_name": f"{case_num}.in",
                "input_data": input_data,
                "input_size": len(input_data),
            }
            if mode == None:
                batch_info[case_num]["output_name"]= f"{case_num}.out"
                batch_info[case_num]["output_sha256"]=hashlib.sha256(output_data).hexdigest()
                batch_info[case_num]["output_size"] = len(output_data)
                batch_info[case_num]["stripped_output_sha256"]= hashlib.sha256(output_stripped).hexdigest()


            # 写入输入文件，使用更大的缓冲区
            input_path = os.path.join(test_dir, f"{case_num}.in")
            output_path = os.path.join(test_dir, f"{case_num}.out")
            
            with open(input_path, "wb", buffering=1024*1024) as f:
                f.write(input_data)
            if mode == None:
                with open(output_path, "wb", buffering=1024*1024) as f:
                    f.write(output_data)
                os.chmod(output_path, 0o644)
            # 设置适当的权限
            os.chmod(input_path, 0o644)
        return batch_info
    except Exception as e:
        loger.error(f"Error in batch {start_idx}-{end_idx}: {str(e)}")
        raise e

def judge_Test(src,max_cpu_time,max_memory,language,test,test_display=False,max_stack=128 * 1024 * 1024,mode=None):
    submission_id = uuid.uuid4().hex
    with SubmissionEnv(JUDGER_WORKSPACE, submission_id=str(submission_id)) as env:
        work_crl = env
        compile,run = chose(language=language)
        
        if compile:
            # 使用 with 语句自动关闭文件
            src_path = os.path.join(work_crl, compile["src_name"])
            try:
                # 写入源代码
                with open(src_path, "w", encoding="utf-8") as f:
                    f.write(src)
                os.chmod(src_path, 0o777)
                
                exe_path = Compiler().compile(compile=compile,
                                            src_path=src_path,
                                            output_dir=work_crl)
                
                   
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

        # 检查测试用例是否为空
        if not test:
            loger.error("测试用例为空")
            return {
                "status": "Error writing test cases",
                "error": "测试用例为空"
            }
            
        # 验证测试用例格式
        if mode == None :
            for i, test_case in enumerate(test):
                if not isinstance(test_case, dict) or "input" not in test_case or "output" not in test_case:
                    loger.error(f"测试用例 {i+1} 格式不正确")
                    return {
                        "status": "Error writing test cases",
                        "error": f"测试用例 {i+1} 格式不正确"
                    }
        else :
            for i, test_case in enumerate(test):
                if not isinstance(test_case, dict) or "input" not in test_case :
                    loger.error(f"测试用例 {i+1} 格式不正确")
                    return {
                        "status": "Error writing test cases",
                        "error": f"测试用例 {i+1} 格式不正确"
                    }

        # 写入测试用例
        test_dir = os.path.join(work_crl, "test")
        os.makedirs(test_dir, exist_ok=True)
        os.chmod(test_dir, 0o755)
     
        # 创建测试用例文件
        try:
            test_cases_info = {}
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = []
                
                # 按批次提交任务
                for i in range(0, len(test), BATCH_SIZE):
                    end_idx = min(i + BATCH_SIZE, len(test))
                    future = executor.submit(write_test_cases, test_dir, test, i, end_idx,mode)
                    futures.append(future)
                # 收集结果
                for future in as_completed(futures):
                    try:
                        batch_info = future.result()
                        test_cases_info.update(batch_info)
                    except Exception as e:
                        loger.error(f"Batch processing failed: {str(e)}")
                        return {
                            "status": "Error writing test cases",
                            "error":f"Error writing test cases: {str(e)}"
                        }
            # 验证测试用例信息是否为空
            if not test_cases_info:
                loger.error("No test cases were processed successfully")
                return {
                    "status": "Error writing test cases",
                    "error": "No test cases were processed successfully"
                }
            # 写入 info 文件
            info = {
                "test_case_number": len(test),
                "test_cases": {i: {k: v for k, v in case_info.items() if k != "input_data"}
                              for i, case_info in test_cases_info.items()}
            }
            # 减少验证步骤的I/O操作
            json_str = json.dumps(info)
            if not json_str or json_str == "{}":
                raise ValueError("Generated empty JSON for info file")
            
            info_path = os.path.join(test_dir, "info")
            with open(info_path, "w", encoding="utf-8", buffering=65536) as f:  # 增加写缓冲区
                f.write(json_str)  # 直接写入字符串而不是再次序列化
            
            # 验证写入后的文件
            if not os.path.exists(info_path) or os.path.getsize(info_path) == 0:
                loger.error("Info file was not written or is empty")
                return {
                    "status": "Error writing test cases",
                    "error": "Info file was not written or is empty"
                }
        except Exception as e:
            loger.error(f"Error writing test cases: {str(e)}")
            return {
                "status": "Error writing test cases",
                "error": f"Error writing test cases: {str(e)}"
            }

        # 创建评测客户端
        try:
            test_case_dir = os.path.join(work_crl, "test")
            judge_client = Client(
                run_config=run,
                exe_path=exe_path,
                max_cpu_time=max_cpu_time,
                max_memory=max_memory,
                test_case_dir=test_case_dir,
                submission_dir=work_crl,
                max_stack=max_stack,
                test_display=test_display,
                mode=mode
            )
        except Exception as e:
            loger.error(f"Error creating judge client: {str(e)}")
            return {
                "status": "Error creating judge client",
                "error": f"Error creating judge client: {str(e)}"
            }
            
        # 执行测试
        try:
            run_result = judge_client.run()
            return run_result
        except Exception as e:
            loger.error(f"执行测试失败: {str(e)}")
            return {
                "status": "Runtime Error",
                "error": f"执行测试失败: {str(e)}"
            }


@app.route('/', methods=['POST'])
def judger():  
    # 验证令牌
    token = request.headers.get('judgertoken')
    if token != TOKEN:
        return create_error_response("INVALID_TOKEN")
    try:
        data = request.get_json()
        if not data:
            return create_error_response("BAD_REQUEST", "Missing request data")

        result = judge_Test(**data)
        
        # 根据结果返回不同的状态码
        if isinstance(result, dict):
            if result.get("status") == "Compile Error":
                return create_error_response("COMPILE_ERROR", result.get("error"))
            elif result.get("status") == "Runtime Error":
                return create_error_response("Runtime Error", result.get("error"))
            elif result.get("status") == "Error creating judge client":
                return create_error_response("Error creating judge client", result.get("error"))
            elif result.get("status") == "Error writing test cases":
                return create_error_response("Error writing test cases", result.get("error"))
        
        return jsonify(result), 200

    except Exception as e:
        loger.error(f"System error: {str(e)}")
        return create_error_response("SYSTEM_ERROR", str(e))
    

@app.teardown_appcontext
def cleanup(exception=None):
    if heartbeat_service is not None:
        heartbeat_service.stop()

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=4399)
    finally:
        if heartbeat_service is not None:
            heartbeat_service.stop()
