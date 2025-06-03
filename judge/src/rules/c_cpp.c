#include <stdio.h>
#include <seccomp.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdbool.h>

#include "../runner.h"


int _c_cpp_seccomp_rules(struct config *_config, bool allow_write_file) {
    // 定义一个白名单数组，包含允许的系统调用
    int syscalls_whitelist[] = {
        SCMP_SYS(access),        // 检查文件权限
        SCMP_SYS(arch_prctl),    // 设置架构特定的进程状态
        SCMP_SYS(brk),           // 改变数据段结束地址
        SCMP_SYS(clock_gettime), // 获取当前时间
        SCMP_SYS(close),         // 关闭文件描述符
        SCMP_SYS(exit_group),    // 终止进程组
        SCMP_SYS(faccessat),     // 检查文件权限（带路径）
        SCMP_SYS(fstat),         // 获取文件状态
        SCMP_SYS(futex),         // 线程同步
        SCMP_SYS(getrandom),     // 获取随机数
        SCMP_SYS(lseek),         // 文件定位
        SCMP_SYS(mmap),          // 内存映射
        SCMP_SYS(mprotect),      // 设置内存保护
        SCMP_SYS(munmap),        // 解除内存映射
        SCMP_SYS(newfstatat),    // 获取文件状态（带路径）
        SCMP_SYS(pread64),       // 从文件中预读
        SCMP_SYS(prlimit64),     // 获取或设置进程资源限制
        SCMP_SYS(read),          // 从文件中读取
        SCMP_SYS(readlink),      // 读取符号链接目标
        SCMP_SYS(readv),         // 从多个缓冲区中读取
        SCMP_SYS(rseq),          // 读取序列
        SCMP_SYS(set_robust_list), // 设置线程 robust futex 列表
        SCMP_SYS(set_tid_address), // 设置线程 ID 地址
        SCMP_SYS(write),         // 向文件中写入
        SCMP_SYS(writev)         // 向多个缓冲区中写入
    };

    // 计算白名单数组的大小
    int syscalls_whitelist_length = sizeof(syscalls_whitelist) / sizeof(int);
    scmp_filter_ctx ctx = NULL;

    // load seccomp rules
    ctx = seccomp_init(SCMP_ACT_KILL);
    if (!ctx) {
        return LOAD_SECCOMP_FAILED;
    }

    for (int i = 0; i < syscalls_whitelist_length; i++) {
        if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, syscalls_whitelist[i], 0) != 0) {
            return LOAD_SECCOMP_FAILED;
        }
    }

    // extra rule for execve
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(execve), 1, SCMP_A0(SCMP_CMP_EQ, (scmp_datum_t)(_config->exe_path))) != 0) {
        return LOAD_SECCOMP_FAILED;
    }

    if (allow_write_file) {
        if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(open), 0) != 0) {
            return LOAD_SECCOMP_FAILED;
        }
        if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(openat), 0) != 0) {
            return LOAD_SECCOMP_FAILED;
        }
        if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(dup), 0) != 0) {
            return LOAD_SECCOMP_FAILED;
        }
        if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(dup2), 0) != 0) {
            return LOAD_SECCOMP_FAILED;
        }
        if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(dup3), 0) != 0) {
            return LOAD_SECCOMP_FAILED;
        }
    } else {
        // do not allow "w" and "rw"
        if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(open), 1, SCMP_CMP(1, SCMP_CMP_MASKED_EQ, O_WRONLY | O_RDWR, 0)) != 0) {
            return LOAD_SECCOMP_FAILED;
        }
        if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(openat), 1, SCMP_CMP(2, SCMP_CMP_MASKED_EQ, O_WRONLY | O_RDWR, 0)) != 0) {
            return LOAD_SECCOMP_FAILED;
        }
    }

    if (seccomp_load(ctx) != 0) {
        return LOAD_SECCOMP_FAILED;
    }
    seccomp_release(ctx);
    return 0;
}

int c_cpp_seccomp_rules(struct config *_config, bool allow_write_file) {
    return _c_cpp_seccomp_rules(_config, false);
}
