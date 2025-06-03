<template>
<!--  { 'sidebar-mode': isSidebar }-->
  <div :class="['ai-assistant']">
    <div class="ai-assistant-header">
      <el-avatar
        :size="30"
        src="/ai.png"
        class="avatar-left"
      />
      <p>AI Assistant</p>
    </div>
    <div class="ai-assistant-content" ref="chatListRef">
      <div v-for="msg in messages" :key="msg.id" :class="['msg-row', msg.role]">
        <template v-if="msg.role == 'assistant'">
          <el-avatar
            :size="36"
            src="/ai.png"
            class="avatar-left"
          />
          <div class="msg-bubble assistant">
            <div class="msg-content" >{{ msg.content }}</div>
            <div class="msg-meta">
              <span class="msg-time">{{ msg.time }}</span>
            </div>
          </div>
        </template>
        <template v-else>
          <el-avatar
            :size="36"
            :src="store.user.avatar"
            class="avatar-right"
          />
          <div class="msg-bubble user">
            <div class="msg-content">{{ msg.content }}</div>
            <div class="msg-meta">
              <span class="msg-time">{{ msg.time }}</span>
            </div>
          </div>
        </template>
      </div>
    </div>
    <div class="ai-assistant-footer">
      <div class="input-inner">
        <textarea
          class="main-input-simple"
          v-model="input"
          placeholder="请输入问题"
          @keyup.enter="sendMessage"
          rows="1"
          @input="autoResize"
        />
        <button class="send-btn" @click="sendMessage" :disabled="loading || !input.trim()">
          <el-icon><Top /></el-icon>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { useStore } from '@/store/user'
import { Top } from '@element-plus/icons-vue'
import { nextTick, onBeforeUnmount } from 'vue'
import dialogueApi from '@/api/ai/dialogue.js'
import { useDetailsStore } from '@/store/details'
export default {
  name: 'AIAssistant',
  components: {
    Top
  },
  setup() {
    const detailsStore = useDetailsStore()
    return {
      detailsStore
    }
  },
  data() {
    const detailsStore = useDetailsStore()
    return {
      store: useStore(),
      input: '',
      messages: [
        {
          id: Date.now(),
          role: 'assistant',
          content: '你好！我是AI助手，我可以帮助你解决编程问题，请随时向我提问。',
          time: new Date().toLocaleTimeString()
        }
      ],
      kb_id: 2,
      loading: false,
      isChatting: false
    }
  },
  watch: {
    messages: {
      handler(newMessages) {
        this.detailsStore.setMessages(newMessages)
      },
      deep: true
    }
  },
  computed: {
    currentDialogueId() {
      return this.detailsStore.details_id
    }
  },
  created() {
    // 如果有chat_id，加载历史消息
    // if (this.currentDialogueId) {
    //   this.loadChatHistory()
    // }
  },
  methods: {
    scrollToBottom() {
      nextTick(() => {
        if (this.$refs.chatListRef) {
          this.$refs.chatListRef.scrollTop = this.$refs.chatListRef.scrollHeight
        }
      })
    },
    async loadChatHistory() {

      dialogueApi.getDetails(this.detailsStore.details_id).then(response => {
        this.setMessages(response.messages)
      }).catch(error => {
        
      })
    },
    autoResize(e) {
      const el = e.target
      el.style.height = 'auto'
      el.style.height = el.scrollHeight + 'px'
    },
    async sendMessage() {
      if (!this.input.trim() || this.loading) return
      this.loading = true
      const userMessage = {
        id: Date.now(),
        role: 'user',
        content: this.input,
        time: new Date().toLocaleTimeString()
      }
      this.messages.push(userMessage)
      this.isChatting = true
      this.scrollToBottom()

      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: '',
        time: new Date().toLocaleTimeString()
      }
      this.messages.push(aiMessage)
      
      try {
        const whl = this.input
        this.input = ''
        console.log('Current chat_id:', this.detailsStore.details_id)
        const response = await dialogueApi.sendStreamMessage(
          whl, 
          this.store.user.id, 
          this.kb_id, 
          this.detailsStore.details_id
        )
        const chatId = response.headers.get('X-Chat-ID')
        
        if (chatId) {
          this.detailsStore.setDetailsId(chatId)
        }
        
        const reader = response.body.getReader()
        const decoder = new TextDecoder('utf-8')
        let buffer = ''
        
        // 模拟流式打字效果
        const streamText = async (text) => {
          for (let i = 0; i < text.length; i++) {
            await new Promise(resolve => setTimeout(resolve, 50))
            this.messages[this.messages.length - 1].content += text[i]
            this.scrollToBottom()
          }
        }
        
        while (true) {
          const { value, done } = await reader.read()
          if (done) break
          const chunk = decoder.decode(value, { stream: true })
          const lines = chunk.split('\n')
          let data = ''
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              data += line.slice(6)
              if (data === '[DONE]') continue
              try {
                const parsed = JSON.parse(data)
                if (parsed.choices?.[0]?.delta?.content) {
                  buffer += parsed.choices[0].delta.content
                  await streamText(parsed.choices[0].delta.content)
                }
              } catch (e) {
                // 可能不是json，忽略
              }
            }
          }
        }
      } catch (error) {
        console.error('发送消息失败:', error)
        if (error.response) {
          console.error('错误详情:', error.response.data)
        }
      } finally {
        this.loading = false
        this.input = ''
      }
    },
  },
  beforeUnmount() {
    this.detailsStore.clearAll()
  },
}
</script>

<style scoped lang="less">
.ai-assistant {
  width: 100%;
  height: 100%;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .ai-assistant-header {
    padding: 10px 16px;
    border-bottom: 1px solid #eee;
    flex-shrink: 0;
    font-size: 20px;
    font-weight: 500;
    color: #333;
    display: flex;
    align-items: center;
    gap: 8px;

    p {
      margin: 0;
      line-height: 1;
    }
  }

  .ai-assistant-content {
    flex: 1;
    overflow-y: auto;
    padding-top: 16px;
    padding-bottom: 16px;
    padding-left: 0px;
    padding-right: 0px;
    background: #fff;
    height: 0;
  }

  .ai-assistant-footer {

    border-top: 1px solid #eee;
    padding: 12px;
    background: #fff;
    flex-shrink: 0;
  }
}

.input-inner {
  display: flex;
  align-items: flex-end;
}

.main-input-simple {
  border: none;
  outline: none;
  width: 100%;
  min-height: 26px;
  max-height: 26px;
  resize: none;
  border-radius: 8px;
  font-size: 14px;
  box-shadow: none;
  margin: 0;
  padding: 8px 12px;
  line-height: 1.5;
  border: 1px solid #dcdfe6;
}

.send-btn {
  margin-left: 10px;
  width: 38px;
  height: 38px;
  background: #409eff;
  color: #fff;
  border: none;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;

  &:disabled {
    background: #e5e6eb;
    color: #bbb;
    cursor: not-allowed;
  }

  &:not(:disabled):hover {
    background: #1876d1;
  }
}

.msg-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  padding: 10px;
}

.msg-row.assistant {
  align-items: flex-start;
}

.msg-row.user {
  flex-direction: row-reverse;
  align-items: flex-start;
}

.avatar-left, .avatar-right {
  margin: 0 8px;
  flex-shrink: 0;
}

.msg-bubble {
  max-width: 60%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  word-break: break-all;
  margin-top: 0;
}

.msg-bubble.assistant {
  background: #f5f6fa;
  color: #333;
  border-top-left-radius: 4px;
}

.msg-bubble.user {
  background: #409eff;
  color: #fff;
  border-top-right-radius: 4px;
}

.msg-content {
  line-height: 1.5;
}

.msg-meta {
  margin-top: 4px;
  font-size: 12px;
  color: #999;
}

.msg-bubble.user .msg-meta {
  color: rgba(255, 255, 255, 0.8);
}

// 保持原有的响应式样式
.ai-assistant.sidebar-mode {
  width: 60px;
  padding-top: 0;
  .ai-assistant-header,
  .ai-assistant-content {
    display: none;
  }
  .ai-assistant-footer {
    height: 100vh;
    background: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    .input-wrapper {
      display: none;
    }
    &::after {
      content: '\f0e6';
      font-family: 'FontAwesome';
      font-size: 28px;
      color: #409eff;
      display: block;
    }
  }
}

@media (max-width: 400px) {
  .ai-assistant {
    min-width: 60px;
    max-width: 60px;
    width: 60px !important;
    padding-top: 0;
    .ai-assistant-header,
    .ai-assistant-content {
      display: none;
    }
    .ai-assistant-footer {
      height: 100vh;
      background: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      .input-wrapper {
        display: none;
      }
      &::after {
        content: '\f0e6';
        font-family: 'FontAwesome';
        font-size: 28px;
        color: #409eff;
        display: block;
      }
    }
  }
}
</style>