<template>
    <div class="faq-container" style="margin-bottom: 10px;">
        <div class="faq-header">
            <h2>常见问题</h2>
        </div>
        <ul class="faq-list">
            <li class="faq-item">
                <strong>输入和输出在哪里?</strong>
                <div class="faq-a">
                    您的程序应从 <code>stdin</code>（标准输入）读取输入，并将输出写入 <code>stdout</code>（标准输出）。例如，您可以在 C 中使用 <code>scanf</code> 或在 C++ 中使用 <code>cin</code> 读取，并在 C 中使用 <code>printf</code> 或在 C++ 中使用 <code>cout</code> 写入 <code>stdout</code>。用户程序不允许读取或写入文件，否则您将收到 <span class="faq-link">运行时错误</span>。
                </div>
            </li>
            <li class="faq-item">
                <strong>提交执行时间是什么意思?</strong>
                <div class="faq-a">
                    OnlineJudge 可能会使用不同的输入文件多次测试您的代码。如果您的代码在每个输入文件的时间限制内给出正确的答案，则显示的执行时间是每个测试用例所花费的最大时间。否则，执行时间将毫无意义。
                </div>
            </li>
            <li class="faq-item">
                <strong>如何使用 C++ Int64?</strong>
                <div class="faq-a">
                    您应该声明 <code>long long</code> 并与 <code>cin</code>/<code>cout</code> 或 <code>%lld</code> 一起使用，使用 <code>__int64</code> 将导致 <span class="faq-link">编译失败</span>。
                </div>
            </li>
            <li class="faq-item">
                <strong>Java 规范?</strong>
                <div class="faq-a">
                    所有程序都必须以 <code>Main</code> 类的静态 <code>main</code> 方法开始。不要求使用公共类；即使 <code>Main</code> 也必须是非公共类以避免编译错误。请勿在 <code>main</code> 中进行 I/O 以避免由于过度刷新而导致超出时间限制。
                </div>
            </li>
            <li class="faq-item">
                <strong>关于输出格式错误?</strong>
                <div class="faq-a">
                    该 OJ 中没有输出格式错误。Judge将对自动输出结果整然地包裹在输出的 <b>最后</b> 一行中。如果仍然与正确的输出不同，则结果将是 <span class="faq-link">答案错误</span>。
                </div>
            </li>
            <li class="faq-item">
                <strong>如何报告有关此 OJ 的错误?</strong>
                <div class="faq-a">
                    onlinejudge 是开源的，您可以到 <a href="https://github.com/" target="_blank" class="faq-link">Github</a> 提交问题，尽量写清楚相关错误的详细信息（例如env、版本..）。这样有助于我们极大地解决该错误。当然，我们很高兴合并您的请求。
                </div>
            </li>
        </ul>
    </div>
</template>
<script>
export default {
    name: 'FAQ'
}
</script>
<style scoped>
.faq-container {
    padding: 20px;
    max-width: 1400px;
    height: 100%;
    margin-left: auto;
    margin-right: auto;
    margin-bottom: 20px;
}
.faq-header {
    background-color: #fff;
    border-radius: 5px 5px 0 0;
    padding: 20px 30px;
    /* box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1); */
    margin-bottom: 0;
}
.faq-header h2 {
    font-size: 18px;
    font-weight: 500;
    color: #333;
    /* margin-bottom: 20px; */
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
}
.faq-list {
    background-color: #fff;
    border-radius: 0 0 5px 5px;
    padding: 0px 30px;
    /* box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1); */
    list-style-type: disc;  
    padding-left: 40px;
    padding-bottom: 10px;
}
.faq-item {
    margin-bottom: 15px;
    line-height: 1.6;
    color: #606266;
}
.faq-item strong {
    color: #303133;
    font-weight: 500;
}
.faq-a {
    margin-top: 4px;
    font-size: 15px;
    color: #444;
    line-height: 1.8;
}
.faq-link {
    color: #409eff;
    font-weight: 500;
}
code {
    background: #f5f5f5;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 14px;
    font-family: 'JetBrains Mono', 'Consolas', 'Menlo', monospace;
}
a.faq-link {
    text-decoration: underline;
}
</style>

