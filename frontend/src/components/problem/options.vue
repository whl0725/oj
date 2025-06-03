<template>
<el-tabs v-model="activeTab" type="card" class="full-height-tabs">
    <el-tab-pane label="测试用例" name="testcase" class="testcase-tab full-height-pane">   
        <div class="item-container">
            <div class="item-row">
                <el-input 
                  type="textarea" 
                  v-model="customInput" 
                  rows="8" 
                  placeholder="请输入测试用例..." 
                  @input="updateParent"
                />
            </div>
        </div>
    </el-tab-pane>
    <el-tab-pane label="代码执行结果" name="result" class="full-height-pane">
        <div class="item-container">
            <div v-if="isRunning" class="loading-container">
                <el-empty :image-size="80" description="正在运行中，请稍候...">
                    <el-icon class="is-loading loading-icon"><Loading /></el-icon>
                </el-empty>
            </div>

            <div v-else-if="runResult">
                <div v-if="runResult.code == 200" class="result-header">
                  <span class="status-text">{{ runResult.msg[0].output || '运行完成' }}</span>
                </div>
                
                <!-- 编译错误信息 -->
                <div v-if="runResult.code == 400 "class="error-container">
                    <div class="section-title">编译错误</div>
                    <pre>{{ runResult.msg.details }}</pre>
                </div>
                
                <!-- 运行时错误信息
                <div v-if="runResult.result && runResult.result.runtime_error" class="error-container">
                    <div class="section-title">运行时错误</div>
                    <pre class="error-message">{{ runResult.result.runtime_error }}</pre>
                </div> -->
                
                <!-- 运行结果 -->
                <div v-if="runResult.code == 401" class="result-container">
                  <span class="status-text">运行超时</span>
                </div>
            </div>
            <div v-else class="empty-result">
                <el-empty :image-size="80" description="暂无运行结果，请先运行代码"></el-empty>
            </div>
        </div>
    </el-tab-pane>
</el-tabs>
</template>

<script>
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
    name: 'options',
    components: {
        Loading
    },
    props: {
        runResult: {
            type: Object,
            default: () => null
        },
        isRunning: {
            type: Boolean,
            default: false
        }
    },
    data() {
        return {
            customInput: '',
            activeTab: 'testcase'
        }
    },
    methods: {
        updateParent() {
            // 向父组件发送自定义事件，传递customInput的值
            this.$emit('update:customInput', this.customInput);
        },
        getStatusClass(status) {
            // 如果 status 不是字符串类型，返回默认样式
            // if (typeof status !== 'string') {
            //     console.log('Status is not a string:', status);
            //     return 'status-other';
            // }
            // // 如果 status 为空字符串，返回默认样式
            // if (!status.trim()) {
            //     return 'status-other';
            // }
            // try {
            //     const statusLower = status.toLowerCase();
            //     console.log('Status lower:', statusLower);
                
            //     if (statusLower.includes('成功') || statusLower.includes('正确')) {
            //         return 'status-accepted';
            //     } else if (statusLower.includes('错误') || statusLower.includes('wrong')) {
            //         return 'status-wrong';
            //     } else if (statusLower.includes('编译') || statusLower.includes('compile')) {
            //         return 'status-error';
            //     } else if (statusLower.includes('超时') || statusLower.includes('time limit')) {
            //         return 'status-tle';
            //     } else if (statusLower.includes('内存') || statusLower.includes('memory limit')) {
            //         return 'status-mle';
            //     } else {
            //         return 'status-other';
            //     }
            // } catch (error) {
            //     console.error('Error processing status:', error);
            //     return 'status-other';
            // }
        },
        // 切换到结果标签页
        showResult() {
            this.activeTab = 'result';
        },
    }
}
</script>

<style>
@import '@/assets/less/options.less';

/* 设置标签页头部的外边距 */
.el-tabs__header {
  margin: 0 !important;
}

/* 为了更好的兼容性，也可以设置特定类型的标签页 */
.el-tabs--card > .el-tabs__header,
.el-tabs--border-card > .el-tabs__header {
  margin: 0 !important;
}

/* 移除文本区域输入框的边框 */
.testcase-tab .el-textarea__inner {
  border: none !important;
  box-shadow: none !important;
}

/* 移除文本区域悬停和聚焦状态的边框 */
.testcase-tab .el-textarea__inner:hover,
.testcase-tab .el-textarea__inner:focus {
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
}

/* 确保整个标签组件占满可用空间 */
.full-height-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 调整标签页结构顺序 - 将标签导航栏放在上面 */
.full-height-tabs > .el-tabs__header {
  order: 0;
}

/* 标签内容区域占据剩余所有空间 */
.full-height-tabs > .el-tabs__content {
  flex: 1;
  overflow: hidden;
  order: 1;
}

/* 每个标签面板也是100%高度 */
.full-height-pane {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 整个容器的样式 */
.item-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 8px;
  box-sizing: border-box;
}

/* 移除多余的测试用例标签 */
.testcase-label {
  display: none;
}

/* 输入框行占据所有可用空间 */
.testcase-tab .item-row {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* Textarea组件也是100%高度 */
.testcase-tab .el-textarea {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Textarea内部元素占据所有可用空间 */
.testcase-tab .el-textarea__inner {
  flex: 1;
  height: 100% !important;
  resize: none !important;
  box-sizing: border-box !important;
}

/* 结果相关样式 */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.loading-icon {
  font-size: 24px;
  color: #409EFF;
  margin-top: 10px;
}

.is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  0% {
    transform: rotateZ(0deg);
  }
  100% {
    transform: rotateZ(360deg);
  }
}

.result-header {
  margin-bottom: 10px;
}

.result-status {
  font-size: 16px;
  font-weight: 600;
  padding: 8px 15px;
  border-radius: 4px;
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
  font-size: 14px;
  font-weight: 600;
  margin: 12px 0 8px 0;
  color: #303133;
  border-left: 4px solid #409eff;
  padding-left: 8px;
}

.error-container, .result-container {
  margin-bottom: 12px;
}

.error-message, .output-message {
  white-space: pre-wrap;
  word-wrap: break-word;
  background-color: #f8f8f8;
  color: #333;
  padding: 12px;
  border-radius: 4px;
  overflow: auto;
  font-family: 'Menlo', 'Monaco', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.5;
  max-height: 300px;
}

.error-message {
  background-color: #2d2d2d;
  color: #f8f8f2;
}

.empty-result {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
</style>