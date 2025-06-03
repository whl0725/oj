<template>
  <div class="details-container">
    <div class="contest-header">
      <div class="header-left">
        <el-icon><Back /></el-icon>
        <el-icon><CaretLeft /></el-icon>
        <el-icon><CaretRight /></el-icon>
        <el-icon><Refresh /></el-icon>
      </div>
      <div class="header-right">
        <el-icon class="setting-icon"><Setting /></el-icon>
        <el-avatar :size="32" :src="user_avatar" />
      </div>
    </div>
    <Splitpanes class="custom-theme" style="height: calc(100vh - 60px);">
      <Pane size="30" min-size="20" class="left-pane">
        <el-tabs v-model="activeTab" class="problem-tabs" type="card">
          <el-tab-pane name="题目描述">
            <template #label>
              <div style="display: flex; align-items: center;">
                <el-icon><Document /></el-icon>
                <span style="margin-left: 5px;">题目描述</span>
              </div>
            </template>
            <div class="problem-content">
              <div class="problem-header">
                <a class="problem-title">{{ problemData.id }}. {{ problemData.title }}</a>
                <div class="problem-meta">
                  <div class="difficulty-tags">
                    <el-tag size="small" :type="difficultyType" effect="dark" class="difficulty-tag">简单</el-tag>
                    <el-tag size="small" type="info" effect="plain">通过率: 45.9%</el-tag>
                  </div>
                  <div class="action-tags">
                    <el-tag size="small" type="info" effect="plain" class="action-tag">
                      <el-icon><Collection /></el-icon>收藏
                    </el-tag>
                    <el-tag size="small" type="info" effect="plain" class="action-tag">
                      <el-icon><Share /></el-icon>分享
                    </el-tag>
                  </div>
                </div>
              </div>
              <div class="problem-description">
                <div class="description-item">
                  <div class="item-content markdown-body" v-html="problemData.description"></div>
                </div>
                
                <div class="description-item">
                  <div v-for="(example, index) in problemData.examples" :key="index" class="example-box">
                    <div class="example-header">示例 {{ index + 1 }}:</div>
                    <div class="example-content">
                      <div class="example-input">
                        <div class="example-row">
                          <div class="label">输入:</div>
                          <div class="content code-block" v-html="example.input"></div>
                        </div>
                      </div>
                      
                      <div class="example-output">
                        <div class="example-row">
                          <div class="label">输出:</div>
                          <div class="content code-block" v-html="example.output"></div>
                        </div>
                      </div>
                      
                      <div class="example-explanation">
                        <div class="example-row">
                          <div class="label">解释:</div>
                          <div class="content code-block">{{ example.explanation }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="description-item">
                  <div class="constraints">
                    <div class="constraint-title">提示:</div>
                    <div><pre v-html="problemData.hint"></pre></div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane name="提交结果" v-if="showResult || isSubmitting">
            <template #label>
              <div style="display: flex; align-items: center;">
                <el-icon><Document /></el-icon>
                <span style="margin-left: 5px;">提交结果</span>
                <el-icon v-if="isSubmitting" class="is-loading"><Loading /></el-icon>
              </div>
            </template>
            <div v-if="isSubmitting" class="loading-container">
              <el-empty :image-size="100" description="正在判题中，请稍候...">
                <el-icon class="is-loading loading-icon"><Loading /></el-icon>
              </el-empty>
            </div>
            <SubmitResult 
              v-else
              :visible="showResult" 
              :resultData="submitResult" 
              :language="language"
              @close="showResult = false" 
            />
          </el-tab-pane>
          <!-- <solution name="题解" /> -->
          <!-- <Submit name="提交" /> -->
          
        </el-tabs>
      </Pane>

      <Pane size="70" min-size="25" class="right-pane">
        <splitpanes horizontal>
          <pane min-size="20" style="margin-bottom: 7px !important;">
            <div class="code-editor">
              <div class="editor-header">
                <div class="header-left">
                  <el-select v-model="language" class="language-select">
                    <el-option 
                      v-for="lang in languages" 
                      :key="lang.value" 
                      :label="lang.label" 
                      :value="lang.value" 
                    />
                  </el-select>
                </div>
                <div class="header-right">
                  <el-button 
                    type="primary" 
                    @click="handleSubmit"
                    :disabled="isSubmitting || isRunning"
                  >提交</el-button>
                  <el-button 
                    type="success" 
                    @click="handleRun"
                    :disabled="isSubmitting || isRunning"
                  >运行</el-button>
                </div>
              </div>
              <div class="monaco-container">
                <MonacoEditor
                  :value="code"
                  :language="language"
                  :theme="'vs'"
                  :options="editorOptions"
                  @change="onChange"
                />
              </div>
            </div>
          </pane>
          <pane min-size="5" class="cs-pane">
            <!-- <options @update:customInput="updateCustomInput" ref="optionsComponent"/> -->
            <options 
              @update:customInput="updateCustomInput" 
              ref="optionsComponent"
              :runResult="runResult"
              :isRunning="isRunning"
            />
          </pane>
        </splitpanes>
      </Pane>
      <Pane size="25"  class="ai-assistant-pane" ref="assistantEl">
<!--        isSidebar:{{isSidebar}}-->
        <div v-show="isSidebar" 
          style="background: #ffffff; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center;" 
          @click="showAI"
        >
          <el-avatar :size="28" src="/ai.png" />
        </div>
        <!-- 对话框 -->
        <AIAssistant v-show="!isSidebar"/>
      </Pane>
    </Splitpanes>
    
  </div>
</template>

<script>
import { ElMessage, ElLoading } from 'element-plus'
import problem_api from '@/api/problem/details'
import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'
import MonacoEditor from '@/components/problem/MonacoEditor.vue'
import options from '@/components/problem/options.vue'
// import Solution from './Solution.vue'
// import Submit from './Submit.vue'
import SubmitResult from '@/components/problem/SubmitResult.vue'
import { Back, CaretLeft, CaretRight, Refresh, Setting, Collection, Share, Plus, Loading } from '@element-plus/icons-vue'
import { Document, Monitor, Warning, Notebook, List } from '@element-plus/icons-vue'
import { useStore } from '../../store/user.js'
import AIAssistant from '@/components/problem/AIAssistant.vue'
// import ResizeObserver from 'resize-observer-polyfill';
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useDetailsStore } from '../../store/details.js'
export default {
  name: 'ProblemDetails',
  components: {
    Splitpanes,
    Pane,
    MonacoEditor,
    options,
    // Solution,
    // Submit,
    Back,
    CaretLeft,
    CaretRight,
    Refresh,
    Setting,
    Collection,
    Share,
    Document,
    Monitor,
    Warning,
    Plus,
    Notebook,
    List,
    SubmitResult,
    Loading,
    AIAssistant
  },
  setup() {
    const store = useStore()
    const detailsStore = useDetailsStore()
    const isSidebar = ref(false)
    let observer = null
    onMounted(() => {
      const el = document.querySelector('.ai-assistant-pane')
      observer = new ResizeObserver(entries => {
        const [entry] = entries
        isSidebar.value = entry.contentRect.width <= 40
      })
      if (el) observer.observe(el)
    })
    onBeforeUnmount(() => {
      if (observer) observer.disconnect()
      detailsStore.clearAll()  // 清除details_id
    })
    return { isSidebar, store, detailsStore }
  },
  created() {
    // 使用异步处理获取题目数据
    problem_api.getProblemDetails(this.problemId)
      .then(response => {
        console.log('获取题目详情:', response);
        if (response && response.data) {
          // 更新整个problemData对象或仅更新部分属性
          this.problemData.description = response.data.description;
          this.problemData.title = response.data.title;
          this.problemData.hint = response.data.hint;
          this.problemData.examples = response.data.samples;
          
          // 转换语言数据格式
          if (response.data.languages) {
            this.languages = Object.entries(response.data.languages).map(([value, label]) => ({
              label: label,
              value: value
            }));
          }
        }
      })
      .catch(error => {
        console.error('获取题目详情失败:', error);
        ElMessage.error('获取题目详情失败，请稍后重试');
        
      });
    //problem_api.getProblemLanguages(this.problemId)
  },
  data() {
    return {
      user_avatar: this.store.user.avatar,
      problemId: this.$route.params.id,
      pollTaskId: null,
      problemData: {
        id: this.$route.params.id,
        title: '',
        description: '',
        hint: '',
        examples: []
      },
      language: 'cpp',
      languages: [],
      code: '#include <iostream>\nusing namespace std;\nint main() {\n    return 0;\n}',
      editorOptions: {
        fontSize: 21,
        tabSize: 4,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        automaticLayout: true,
        scrollbar: {
          vertical: 'visible',
          horizontal: 'visible'
        }
      },
      difficultyType: 'success',
      customInput: '',
      showResult: false,
      submitResult: {},
      activeTab: '题目描述',
      isSubmitting: false,
      startSubmitTime: null,
      endSubmitTime: null,
      submitDuration: null,
      isRunning: false,
      runResult: null,
      runPollTaskId: null,
    }
  }, 
  methods: {
    onChange(value) {
      this.code = value
    },
    handleSubmit() {
      if (this.isSubmitting || this.isRunning) {
        return;
      }
      this.isSubmitting = true;
      this.activeTab = '提交结果';
      
      problem_api.ProblemSubmit(this.problemId, this.code, this.language, this.store.user.username)
        .then(res => {
          console.log('提交结果:', res);
          if(res.data.code == 200 && res.data.msg == '提交成功') {
            this.startPolling(res.data.submit_id);
          } else {
            this.submitResult = res.data;
            this.isSubmitting = false;
            this.showResult = true;
          }
        })
        .catch(err => {
          console.error('提交错误:', err);
          ElMessage.error('提交失败，请稍后重试');
          this.isSubmitting = false;
        });
    },
    startPolling(submissionId) {
      this.clearPollingTask();
      
      const pollResult = () => {
        problem_api.getSubmissionResult(submissionId)
          .then(res => {
            console.log('轮询判题结果:', res);
            
            if (!res || !res.data) {
              console.error('轮询响应无效');
              this.clearPollingTask();
              this.isSubmitting = false;
              ElMessage.error('获取判题结果失败');
              return;
            }
            
            console.log('响应状态码:', res.data.code);
            console.log('响应数据:', res.data);
            
            if (res.data.code === 200) {
              this.submitResult = res.data;
              this.isSubmitting = false;
              this.showResult = true;
              ElMessage.success(`答案正确`);
              this.clearPollingTask();
            } else if (res.data.code === 201) {
              console.log('判题中，请稍候...');
            } else {
              this.submitResult = res.data;
              console.log('submitResult:', this.submitResult);
              this.isSubmitting = false;
              this.showResult = true;
              
              if (res.data.code === 202) {
                ElMessage.error(`答案错误`);
              } else if (res.data.code === 203) {
                ElMessage.error(`编译错误`);
              } else if (res.data.code === 204) {
                ElMessage.error(`运行时错误`);
              } else {
                ElMessage.error(`判题结果: ${res.data.msg || '未知状态'}`);
              }
              this.clearPollingTask();
            }
          })
          .catch(err => {
            console.error('轮询错误:', err);
            this.clearPollingTask();
            this.isSubmitting = false;
            ElMessage.error('获取判题结果失败');
          });
      };
      
      pollResult();
      this.pollTaskId = setInterval(pollResult, 200); 
    },
    calculateDuration() {
      if (this.startSubmitTime && this.endSubmitTime) {
        const durationMs = this.endSubmitTime - this.startSubmitTime;
        this.submitDuration = (durationMs / 1000).toFixed(2);
        console.log(`从提交到轮询结束耗时: ${this.submitDuration}秒`);
      }
    },
    clearPollingTask() {
      if (this.pollTaskId) {
        clearInterval(this.pollTaskId);
        this.pollTaskId = null;
      }
    },
    handleRun() {
      if (this.isSubmitting || this.isRunning) {
        return;
      }
      this.isRunning = true;
      
      if(this.customInput == '') {
        ElMessage.error('请输入自定义测试用例');
        this.isRunning = false;
        return;
      }
      
      problem_api.runCode(this.problemId, this.code, this.language, this.store.user.username, this.customInput)
        .then(res => {
          console.log('运行代码结果:', res);
          if(res.data.code == 200 && res.data.msg == '提交成功') {
            // 开始轮询获取结果
            this.startRunPolling(res.data.run_id);
          } else {
            this.runResult = res.data;
            this.isRunning = false;
            // 通知子组件切换到结果标签页
            this.$refs.optionsComponent.showResult();
          }
        })
        .catch(err => {
          console.error('运行代码错误:', err);
          ElMessage.error('运行失败，请稍后重试');
          this.isRunning = false;
        });
    },

    startRunPolling(runId) {
      this.clearRunPollingTask();
      
      const pollResult = () => {
        problem_api.getRunResult(runId)
          .then(res => {
            console.log('轮询运行结果:', res);
            
            if (!res || !res.data) {
              console.error('轮询响应无效');
              this.clearRunPollingTask();
              this.isRunning = false;
              ElMessage.error('获取运行结果失败');
              return;
            }
            
            if (res.data.code == 200) {
              this.isRunning = false;
              ElMessage.success('代码运行成功');
              this.runResult = {
                msg: res.data.msg,
                result: res.data.result || {},
                code: res.data.code
              };
              this.$refs.optionsComponent.showResult();
              this.clearRunPollingTask();
            } else if (res.data.code === 201) {
              console.log('运行中，请稍候...');
            } else {
              this.isRunning = false;
              if (res.data.code == 400) {
                  this.runResult = {
                    msg: res.data.msg,
                    result: res.data.details || {},
                    code: res.data.code
                };
              console.log('runResult:', this.runResult);
                ElMessage.error('编译错误');
              }
              if(res.data.code == 401){
                this.runResult = {
                  msg: res.data.msg,
                  result: res.data.msg || {},
                  code: 401
                };
                console.log('runResult:', this.runResult);
                ElMessage.error('运行超时');
              }
              this.$refs.optionsComponent.showResult();
              this.clearRunPollingTask();
            }
          })
          .catch(err => {
            console.error('轮询错误:', err);
            this.clearRunPollingTask();
            this.isRunning = false;
            ElMessage.error('获取运行结果失败');
          });
      };
      
      pollResult();
      this.runPollTaskId = setInterval(pollResult, 200); 
    },

    clearRunPollingTask() {
      if (this.runPollTaskId) {
        clearInterval(this.runPollTaskId);
        this.runPollTaskId = null;
      }
    },
    updateCustomInput(value) {
      // 更新从子组件接收到的自定义输入
      this.customInput = value;
    },
    showAI() {
      const assistantEl = this.$refs.assistantEl
      if (assistantEl) {
        assistantEl.style.width = '25%'
      }
      console.log(assistantEl);
    },
  },
  mounted() {},
  beforeRouteEnter(to, from, next) {
    next(vm => {
      vm.activeTab = '题目描述';
      vm.showResult = false;
      vm.submitResult = {};
      vm.isSubmitting = false;
    });
  },
  beforeRouteUpdate(to, from, next) {
    if (to.params.id !== from.params.id || to.path === from.path) {
      this.activeTab = '题目描述';
      this.showResult = false;
      this.submitResult = {};
      this.isSubmitting = false;
    }
    next();
  },
  beforeUnmount() {
    this.clearPollingTask();
  },
  beforeRouteLeave(to, from, next) {
    this.clearPollingTask();
    next();
  },
  beforeDestroy() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  }
}
</script>

<style lang="less" scoped>
@import '@/assets/less/details.less';
.problem-tabs {
  
  :deep(.el-tabs__nav) {
    .el-tabs__item:not(:last-child)::after {
      content: '';
      position: absolute;
      right: 0;
      top: 15%;
      height: 70%;
      width: 1px;
      background-color: #dcdee4;
    }
  }
  
  :deep(.el-tabs__item) {
    padding: 0 10px;
  }
}

/* 添加水平排列标签和内容的样式 */
.example-row {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  margin-bottom: 5px;
}

.example-row .label {
  min-width: 30px;
  margin-right: 0;
  white-space: nowrap;
  padding-top: 3px;
}

.example-row .content {
  flex: 1;
  overflow-y: auto;
  max-height: none;
  word-break: break-word;
}

.example-explanation {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
}

/* 约束条件样式 */
.constraints {
  margin-top: 20px;
  
  .constraint-title {
    font-size: 14px;
    color: #262626;
    font-weight: bold;
    margin-bottom: 10px;
  }
  
  ul {
    list-style-type: disc;
    padding-left: 20px;
    
    li {
      padding: 5px 0;
      background: none;
      
      &:before {
        content: none;
      }
      
      code {
        font-family: 'Menlo', monospace;
        background-color: transparent;
        font-size: 14px;
        color: #333;
      }
    }
  }
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: 40px 0;
}

.loading-icon {
  font-size: 30px;
  color: #409EFF;
  margin-top: 20px;
}

/* 标签页中的加载图标样式 */
.is-loading {
  animation: rotating 2s linear infinite;
  margin-left: 5px;
  font-size: 14px;
  color: #409EFF;
}

@keyframes rotating {
  0% {
    transform: rotateZ(0deg);
  }
  100% {
    transform: rotateZ(360deg);
  }
}
</style>

<!-- 添加全局样式覆盖 -->
<style>
/* 覆盖题解标签的左内边距 */
.el-tabs--card > .el-tabs__header .el-tabs__item:nth-child(2),
.el-tabs--border-card > .el-tabs__header .el-tabs__item:nth-child(2) {
  padding-left: 10 !important;
}

/* 针对元素定位更精确，提高选择器优先级 */
.problem-tabs .el-tabs__nav .el-tabs__item:nth-child(2) {
  padding-left: 10 !important;
}

/* 增加选择器特异性 */
html body .problem-tabs .el-tabs__header .el-tabs__nav .el-tabs__item:nth-child(2) {
  padding-left: 10px !important;
}

/* 设置标签页头部的外边距 */
.el-tabs__header {
  margin: 0 !important;
}

/* 为了更好的兼容性，也可以设置特定类型的标签页 */
.el-tabs--card > .el-tabs__header,
.el-tabs--border-card > .el-tabs__header {
  margin: 0 !important;
}
</style>