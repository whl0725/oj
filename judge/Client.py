import _judge
import os
from multiprocessing import Pool
import psutil
import json
import hashlib
import shlex
def _run(instance, test_case_file_id):
    try:
        return instance.one(test_case_file_id)
    finally:
        # 立即删除临时文件
        test_case_dir = instance.test_case_dir
        user_output = os.path.join(test_case_dir, f"user_output_{test_case_file_id}")
        error_path = os.path.join(test_case_dir, f"error_{test_case_file_id}")
        for path in [user_output, error_path]:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except:
                pass


class Client(object):
    def __init__(self, run_config, exe_path, max_cpu_time, max_memory, test_case_dir,
                 submission_dir,test_display, memory_limit_check_only=0, max_stack=None, mode= None):
        self.exe_path = exe_path
        self.max_cpu_time = int(max_cpu_time)
        self.max_memory = int(max_memory)
        self.test_case_dir = test_case_dir
        self.submission_dir = submission_dir

        self.run_config = run_config
        self._test_case_info = self._load_test_case_info()
        self.max_stack = max_stack
        self.test_display=  test_display
        if self.run_config["memory_limit_check_only"]:
            self.memory_limit_check_only = self.run_config["memory_limit_check_only"]
        else:
            self.memory_limit_check_only = 0
        self.mode = mode
    
    def _load_test_case_info(self):
        try:
            with open(os.path.join(self.test_case_dir, "info")) as f:
                return json.load(f)
        except IOError:
            raise Exception("Test case not found")
        except ValueError:
            raise Exception("Bad test case config")

    def one(self, test_case_file_id):
        test_case_info = self._test_case_info["test_cases"][str(test_case_file_id)]
        
        input_path = os.path.join(self.test_case_dir, test_case_info["input_name"])
        # 将输出和错误文件放在 test 目录下
        user_output_path = os.path.join(self.test_case_dir, f"user_output_{test_case_file_id}")
        error_path = os.path.join(self.test_case_dir, f"error_{test_case_file_id}")
        
        command = self.run_config["command"].format(
            exe_path=self.exe_path, 
            exe_dir=os.path.dirname(self.exe_path),
            max_memory=int(self.max_memory / 1024)
        )
        command = shlex.split(command)
        env = ["PATH=" + os.environ.get("PATH", "")] + self.run_config.get("env", [])

        seccomp_rule = self.run_config["seccomp_rule"]

        run_result = _judge.run(
            max_cpu_time=self.max_cpu_time,
            max_real_time=self.max_cpu_time * 2,
            max_memory=self.max_memory,
            max_stack=self.max_stack or 256 * 1024 * 1024,
            max_output_size=max(test_case_info.get("output_size", 0) * 2, 1024 * 1024 * 128),
            max_process_number=-1,
            exe_path=command[0],
            input_path=input_path,
            output_path=user_output_path,
            error_path=error_path,
            args=command[1:],
            env=env,
            memory_limit_check_only=1,
            log_path=os.path.join(self.test_case_dir, "judge.log"),  # 日志也放在 test 目录下
            seccomp_rule_name=seccomp_rule,
            uid=0,
            gid=0
        )
        status_map = {
            0: "Accepted",
            1: "Time Limit Exceeded",
            2: "Time Limit Exceeded",
            3: "Memory Limit Exceeded",
            4: "Runtime Error",
            5: "System Error"
        }
        result_code = run_result.get("result", 5)
        status = status_map.get(result_code, "System Error")
        
        if status == "Accepted" and self.mode == None:
            try:
                # 使用更大的缓冲区读取文件
                with open(user_output_path, "rb", buffering=512*1024) as f:
                    user_output = f.read()
                # 计算哈希值时一次性完成
                user_output_stripped = user_output.rstrip()
                user_output_sha256 = hashlib.sha256(user_output).hexdigest()
                user_output_stripped_sha256 = hashlib.sha256(user_output_stripped).hexdigest()
                
                if not (user_output_sha256 == test_case_info["output_sha256"] or 
                       user_output_stripped_sha256 == test_case_info["stripped_output_sha256"]):
                    status = "Wrong Answer"
            except Exception as e:
                status = "Judge Error"
                run_result["error"] = str(e)
        
        result = {
            "test_case": str(test_case_file_id),
            "status": status,
            "time_cost": run_result.get("cpu_time", 0),
            "memory_cost": run_result.get("memory", 0)/(1024**2),
            "error": run_result.get("error", None)
        }
        
        # 如果mode为1，添加output到结果中
        if self.mode == 1 and os.path.exists(user_output_path):
            try:
                with open(user_output_path, "rb") as f:
                    output = f.read()
                    result["output"] = output.decode('utf-8', errors='replace')
                del result["memory_cost"]
                del result["time_cost"]
                del result["status"]

                print(result)
            except Exception as e:
                result["output_error"] = str(e)
                
        return result

    def run(self):
        result = []
        # 使用更少的进程以减少资源竞争
        process_count = min(psutil.cpu_count() // 2 or 1, 4)
        pool = Pool(processes=process_count)
        
        try:
            # 检查测试用例信息
            if not self._test_case_info or "test_cases" not in self._test_case_info:
                return {
                    "total_count": 0,
                    "accepted_count": 0,
                    "total_time": 0,
                    "max_memory": 0,
                    "test_cases": [],
                    "error": "测试用例信息为空或格式不正确"
                }
            
            # 检查测试用例是否为空
            test_cases = sorted(self._test_case_info["test_cases"].keys())
            if not test_cases:
                return {
                    "total_count": 0,
                    "accepted_count": 0,
                    "total_time": 0,
                    "max_memory": 0,
                    "test_cases": [],
                    "error": "没有找到有效的测试用例"
                }
            
            # 批量提交任务
            chunk_size = max(len(test_cases) // process_count, 1)  # 优化任务分配
            
            try:
                results = pool.starmap(_run, [(self, test_id) for test_id in test_cases], 
                                     chunksize=chunk_size)
                result.extend(results)
            except Exception as e:
                return {
                    "total_count": 0,
                    "accepted_count": 0,
                    "total_time": 0,
                    "max_memory": 0,
                    "test_cases": [],
                    "error": f"执行测试失败: {str(e)}"
                }
            
            # 使用列表推导式优化汇总计算
            try:
                # 如果mode为1，保留所有测试用例的输出结果
                if self.mode == 1:
                    summary = {
                        
                    }
                    summary["test_cases"] = sorted(result, key=lambda x: int(x["test_case"]))

                    return summary
                accepted_results = [r for r in result if r["status"] == "Accepted"]
                if not self.test_display:
                    summary = {
                        "total_count": len(result),
                        "accepted_count": len(accepted_results),
                        "total_time": sum(r["time_cost"] for r in result),
                        "max_memory": sum((r["memory_cost"] for r in result)),
                    }
                else:
                    summary = {
                        "total_count": len(result),
                        "accepted_count": len(accepted_results),
                        "total_time": sum(r["time_cost"] for r in result),
                        "max_memory": sum((r["memory_cost"] for r in result)),
                        "test_cases": sorted(result, key=lambda x: int(x["test_case"]))
                    }
                    
               
                    
                return summary
            except Exception as e:
                return {
                    "total_count": len(result) if result else 0,
                    "accepted_count": 0,
                    "total_time": 0,
                    "max_memory": 0,
                    "test_cases": [],
                    "error": f"汇总测试结果失败: {str(e)}"
                }
            
        except Exception as e:
            return {
                "total_count": 0,
                "accepted_count": 0,
                "total_time": 0,
                "max_memory": 0,
                "test_cases": [],
                "error": str(e)
            }
        finally:
            pool.close()
            pool.join()