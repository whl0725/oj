default_env = ["LANG=en_US.UTF-8", "LANGUAGE=en_US:en", "LC_ALL=en_US.UTF-8"]

_c_lang_config = {
    "compile": {
        "src_name": "main.c",
        "exe_name": "main",
        "max_cpu_time": 3000,
        "max_real_time": 10000,
        "max_memory": 256 * 1024 * 1024,
        "compile_command": "/usr/bin/gcc -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c17 {src_path} -lm -o {exe_path}",
    },
    "run": {
        "memory_limit_check_only": None,
        "command": "{exe_path}",
        "seccomp_rule": "c_cpp",
        "env": default_env
    }
}

_cpp_lang_config = {
    "compile": {
        "src_name": "main.cpp",
        "exe_name": "main",
        "max_cpu_time": 10000,
        "max_real_time": 20000,
        "max_memory": 1024 * 1024 * 1024,
        "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c++20 {src_path} -lm -o {exe_path}",
    },
    "run": {
        "memory_limit_check_only": None,
        "command": "{exe_path}",
        "seccomp_rule": "c_cpp",
        "env": default_env
    }
}

_java_lang_config = {
    "compile": {
        "src_name": "Main.java",
        "exe_name": "Main",
        "max_cpu_time": 5000,
        "max_real_time": 10000,
        "max_memory": -1,
        "compile_command": "/usr/bin/javac {src_path} -d {exe_dir}"
    },
    "run": {
        "command": "/usr/bin/java -cp {exe_dir} -XX:MaxRAM={max_memory}k Main",
        "seccomp_rule": None,
        "env": default_env,
        "memory_limit_check_only": 1
    }
}

_py3_lang_config = {
    "compile": {
        "src_name": "solution.py",
        "exe_name": "solution.py",
        "max_cpu_time": 4000,
        "max_real_time": 10000,
        "max_memory": 512 * 1024 * 1024,
        "compile_command": "/usr/bin/python3 -m py_compile {src_path}",
    },
    "run": {
        "memory_limit_check_only": None,
        "command": "/usr/bin/python3 -BS {exe_path}",
        "seccomp_rule": "general",
        "env": default_env
    }
}

_go_lang_config = {
    # "compile": {
    #     "src_name": "main.go",
    #     "exe_name": "main",
    #     "max['/usr/bin/go', 'build', '-o', 'main', 'main.go']
    #     "max_real_time": 5000,
    #     "max_memory": 1024 * 1024 * 1024,
    #     "compile_command": "/usr/bin/go build -ldflags='-s -w' -o {exe_path} {src_path}",
    #     "env": [
    #         "GOCACHE=/tmp",
    #         "GOPATH=/tmp",
    #         "GOMAXPROCS=1",
    #         "GOGC=off"
    #     ] + default_env
    # },
    # "run": {
    #     "command": "{exe_path}",
    #     "seccomp_rule": None,
    #     "env": [
    #         "GOMAXPROCS=1",
    #         "GOGC=off"
    #     ] + default_env,
    #     "memory_limit_check_only": 1
    # }
    "compile": {
        "src_name": "main.go",
        "exe_name": "main",
        "max_cpu_time": 3000,
        "max_real_time": 6000,
        "max_memory": 1024 * 1024 * 1024,
        "compile_command": "/usr/bin/go build -ldflags='-s -w' -o {exe_path} {src_path}",
        "env": ["GOCACHE=/tmp", "GOPATH=/tmp", "GOMAXPROCS=1"] + default_env
    },
    "run": {
        "command": "{exe_path}",
        "seccomp_rule": "golang",
        "env": ["GOMAXPROCS=1"] + default_env,
        "memory_limit_check_only": 1
    }
}