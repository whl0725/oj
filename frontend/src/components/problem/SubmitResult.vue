<template>
  <div v-if="visible" class="submit-result-container">
    <div class="result-header">
      <div class="result-status" :class="getStatusClass(resultData.msg)">
        <span class="status-text">{{ resultData.msg }}</span>
      </div>
    </div>
    
    <!-- 编译错误信息 -->
    <div v-if="resultData.result && resultData.result.compile_error" class="error-container">
      <div class="section-title">编译错误</div>
      <pre class="error-message">{{ resultData.result.compile_error }}</pre>
    </div>
    
    <!-- 运行时错误信息 -->
    <div v-if="resultData.result && resultData.result.runtime_error" class="error-container">
      <div class="section-title">运行时错误</div>
      <pre class="error-message">{{ resultData.result.runtime_error }}</pre>
    </div>  

    <!-- 提交的代码 -->
    <div class="code-container">
      <div class="section-title">提交的代码</div>
      <pre><code v-html="highlightedCode"></code></pre>
    </div>
  </div>
</template>

<script>
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css'; // 导入一个深色主题

export default {
  name: 'SubmitResult',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    resultData: {
      type: Object,
      default: () => ({})
    },
    code: {
      type: String,
      default: ''
    },
    language: {
      type: String,
      default: 'cpp'
    }
  },
  computed: {
    highlightedCode() {
      const sourceCode = this.resultData.src || this.code || '';
      try {
        // 根据language属性选择正确的语言
        const lang = this.getHighlightLanguage();
        if (hljs.getLanguage(lang)) {
          return hljs.highlight(sourceCode, { language: lang }).value;
        } else {
          // 如果没有找到匹配的语言，尝试自动检测
          return hljs.highlightAuto(sourceCode).value;
        }
      } catch (e) {
        console.error('代码高亮错误:', e);
        return sourceCode; // 如果出错，返回原始代码
      }
    }
  },
  methods: {
    getHighlightLanguage() {
      // 将language属性映射到highlight.js支持的语言名称
      const languageMap = {
        'cpp': 'cpp',
        'c': 'c',
        'java': 'java',
        'python': 'python',
        'python3': 'python',
        'javascript': 'javascript',
        'js': 'javascript',
        // 可以根据需要添加更多映射
      };
      return languageMap[this.language.toLowerCase()] || 'plaintext';
    },
    formatMemory(memoryBytes) {
      if (memoryBytes === undefined || memoryBytes === null) return 'N/A';
      
      if (memoryBytes < 1024) {
        return `${Math.round(memoryBytes * 100) / 100} KB`;
      }
      
      const mb = memoryBytes / 1024;
      return `${Math.round(mb * 100) / 100} MB`;
    },
    getStatusClass(status) {
      if (!status) return 'status-other';
      
      const statusLower = status.toLowerCase();
      
      if (statusLower.includes('正确') || statusLower.includes('accepted')) {
        return 'status-accepted';
      } else if (statusLower.includes('错误') || statusLower.includes('wrong')) {
        return 'status-wrong';
      } else if (statusLower.includes('编译') || statusLower.includes('compile')) {
        return 'status-error';
      } else if (statusLower.includes('超时') || statusLower.includes('time limit')) {
        return 'status-tle';
      } else if (statusLower.includes('内存') || statusLower.includes('memory limit')) {
        return 'status-mle';
      } else {
        return 'status-other';
      }
    }
  }
}
</script>

<style scoped>
.submit-result-container {
  padding: 24px;
  /* height: 1042px; */
  height: 100%;
  overflow-y: auto !important;
  overflow-x: hidden;
  background-color: #fff;
  border-radius: 8px;
}

.result-header {
  display: flex;
  align-items: center;
}

.result-status {
  font-size: 22px;
  font-weight: 600;
  padding: 10px 20px;
  border-radius: 6px;
}

.status-accepted {
  color: #67c23a;
  background-color: #f0f9eb;
  border-left: 4px solid #67c23a;
}

.status-wrong {
  color: #f56c6c;
  background-color: #fef0f0;
  border-left: 4px solid #f56c6c;
}

.status-error {
  color: #e6a23c;
  background-color: #fdf6ec;
  border-left: 4px solid #e6a23c;
}

.status-tle {
  color: #909399;
  background-color: #f4f4f5;
  border-left: 4px solid #909399;
}

.status-mle {
  color: #909399;
  background-color: #f4f4f5;
  border-left: 4px solid #909399;
}

.status-other {
  color: #409eff;
  background-color: #ecf5ff;
  border-left: 4px solid #409eff;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin: 20px 0 12px 0;
  color: #303133;
  border-left: 4px solid #409eff;
  padding-left: 10px;
}

.error-container {
  margin-bottom: 24px;
  padding: 16px;
  background-color: #fef0f0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.error-message {
  white-space: pre-wrap;
  word-wrap: break-word;
  background-color: #2d2d2d;
  color: #f8f8f2;
  padding: 16px;
  border-radius: 6px;
  overflow: auto;
  font-family: 'Menlo', 'Monaco', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.5;
}

.test-cases-container {
  margin-bottom: 24px;
}

.test-cases-table {
  width: 100%;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.code-container {
  margin-top: 0px;
  padding-top: 16px;
  border-radius: 8px;
  pre {
    height: 700px;
  }
}

.code-block {
  white-space: pre-wrap;
  word-wrap: break-word;
  background-color: #2d2d2d;
  color: #f8f8f2;
  padding: 16px;
  border-radius: 6px;
  overflow: auto;
  font-family: 'Menlo', 'Monaco', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.5;
}

/* 滚动条整体样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

/* 滚动条轨道 */
::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.03);
  border-radius: 4px;
}

/* 滚动条滑块 */
::-webkit-scrollbar-thumb {
  background: rgba(144, 147, 153, 0.3);
  border-radius: 4px;
}

/* 鼠标悬停在滑块上时 */
::-webkit-scrollbar-thumb:hover {
  background: rgba(144, 147, 153, 0.5);
}

/* 让滚动条在不滚动时半透明 */
.code-container pre:hover::-webkit-scrollbar-thumb {
  background: rgba(144, 147, 153, 0.5);
}

/* 响应式布局 */
@media (max-width: 768px) {
  .submit-result-container {
    padding: 16px;
  }
  
  .result-status {
    font-size: 18px;
    padding: 8px 16px;
  }
  
  .section-title {
    font-size: 16px;
  }
}
</style> 