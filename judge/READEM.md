# 文档

### 对于使用判题机的说明

###### API说明
1.max_cpu_time=2000, //最大cpu时间
2.max_real_time=1000 //最大运行时间
3.max_memory=128*1024*1024, //最大内存
4.id //题目id


max_cpu_time=2000,
max_output_size=10000,
max_stack=32 * 1024 * 1024,
# five args above can be _judger.UNLIMITED
exe_path="main",
input_path="1.in",
output_path="4.out",
error_path="2.out",
args=[],
# can be empty list
env=[],
log_path="judger.log",
# can be None
seccomp_rule_name="c_cpp",
uid=0,
gid=0

要在环境变量里面加入：
1.JUDGE_MAX_WORKERS
2.JUDGE_BATCH_SIZE
3.BACKEND_URL
4.SERVICE_URL
5.TOKEN


好的，我来帮你写一个 Markdown 格式的 API 文档：

```markdown:judge_api.md
# 判题机 API 文档

## 基本信息

- 基础URL: `http://localhost:5000`
- 认证方式: Token (通过 judgertoken 请求头)
- 响应格式: JSON

## API 端点

### POST /

提交代码进行判题。

#### 请求头

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| judgertoken | string | 是 | 认证令牌 |

#### 请求体

```json
{
    "src": "string",          // 源代码
    "language": "string",     // 编程语言 (cpp/java/python/go)
    "max_cpu_time": integer,  // CPU时间限制(ms)
    "max_memory": integer,    // 内存限制(bytes)
    "test": [                 // 测试用例数组
        {
            "input": "string",   // 输入数据
            "output": "string"   // 期望输出
        }
    ]
}
```

#### 响应状态码

| 状态码 | 描述 |
|--------|------|
| 200 | 成功执行 |
| 400 | 编译错误或请求数据错误 |
| 401 | 认证失败或运行时错误 |
| 402 | 时间超限 |
| 403 | 内存超限 |
| 404 | 答案错误 |
| 500 | 系统内部错误 |

#### 成功响应示例

```json
{
    "status": "Accepted",
    "result": {
        "cpu_time": 1,
        "real_time": 2,
        "memory": 1024,
        "signal": 0,
        "exit_code": 0,
        "error": 0,
        "result": 0
    }
}
```

#### 错误响应示例

```json
{
    "code": 400,
    "message": "Compilation failed",
    "details": "具体错误信息"
}
```

## 错误码说明

| 错误类型 | 状态码 | 描述 |
|----------|--------|------|
| COMPILE_ERROR | 400 | 编译失败 |
| RUNTIME_ERROR | 401 | 运行时错误 |
| TIME_LIMIT | 402 | 时间超限 |
| MEMORY_LIMIT | 403 | 内存超限 |
| WRONG_ANSWER | 404 | 答案错误 |
| SYSTEM_ERROR | 500 | 系统内部错误 |
| INVALID_TOKEN | 401 | 无效的认证令牌 |
| BAD_REQUEST | 400 | 无效的请求数据 |

## 使用示例

### curl 示例

```bash
curl -X POST http://localhost:5000 \
     -H "Content-Type: application/json" \
     -H "judgertoken: your_token_here" \
     -d '{
         "src": "your_code_here",
         "language": "cpp",
         "max_cpu_time": 1000,
         "max_memory": 128000000,
         "test": [
             {
                 "input": "1 2 3",
                 "output": "6"
             }
         ]
     }'
```

### Python 示例

```python
import requests
import json

url = "http://localhost:5000"
headers = {
    "Content-Type": "application/json",
    "judgertoken": "your_token_here"
}

data = {
    "src": "your_code_here",
    "language": "cpp",
    "max_cpu_time": 1000,
    "max_memory": 128000000,
    "test": [
        {
            "input": "1 2 3",
            "output": "6"
        }
    ]
}

response = requests.post(url, headers=headers, json=data)
result = response.json()
print(result)
```

## 注意事项

1. 所有请求必须包含有效的 judgertoken
2. 代码长度和测试用例数量可能有限制
3. 内存限制单位为字节(bytes)
4. CPU时间限制单位为毫秒(ms)
5. 不同编程语言可能有不同的限制和配置
```

这个 Markdown 文档：
1. 包含了完整的 API 说明
2. 提供了请求和响应的详细格式
3. 包含了所有错误码的说明
4. 提供了使用示例
5. 列出了重要注意事项

你可以将这个文档保存为 `judge_api.md`，然后使用 Markdown 查看器或转换工具来查看或转换为其他格式。
