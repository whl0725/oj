<template>
    <div class="judger-container">
        <div class="result-explanation">
            <h2>结果说明</h2>
            
            <ul class="explanation-list">
                <li>
                    <strong>等待和评审：</strong> 您的解决方案将很快被评审，请等待结果。
                </li>
                <li>
                    <strong>编译错误：</strong> 无法编译源代码，单击链接可直看编译器的输出。
                </li>
                <li>
                    <strong>接受：</strong> 恭喜。您的解决方案是正确的。
                </li>
                <li>
                    <strong>Wrong Answer（错误答案）：</strong> 程序的输出与judger的答案不匹配。
                </li>
                <li>
                    <strong>运行时错误：</strong> 您的程序异常终止，可能的原因包括：段错误、除以零或退出时出现非0代码。
                </li>
                <li>
                    <strong>Time Limit Exceeded：</strong> 程序使用的CPU时间已超出限制。
                </li>
                <li>
                    <strong>超出内存限制：</strong> 程序实际使用的内存已超出限制。
                </li>
                <li>
                    <strong>系统错误：</strong> 糟糕，我们出了点问题。请向管理员报告此情况。
                </li>
            </ul>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Judger'
}
</script>

<style lang="less" scoped>
.judger-container {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
}

.result-explanation {
    background-color: #fff;
    border-radius: 5px;
    padding: 20px 30px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    margin-bottom: 30px;
    
    h2 {
        font-size: 18px;
        font-weight: 500;
        color: #333;
        margin-bottom: 20px;
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
    }
}

.explanation-list {
    list-style-type: disc;
    padding-left: 20px;
    
    li {
        margin-bottom: 15px;
        line-height: 1.6;
        color: #606266;
        
        strong {
            color: #303133;
            font-weight: 500;
        }
    }
}
</style>


