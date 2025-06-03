<template>
  <div class="main-content">
    <template v-if="!aiStore.currentDialogueId">
      <div class="main-center">
        <h1 class="main-title">您好，有什么我能帮你的吗？</h1>
        <div class="input-card simple-input-card">
          <textarea
            class="main-input"
            v-model="input"
            placeholder="请输入您的问题"
            @keyup.enter="send_Initialization"
            rows="1"
            @input="autoResize"
          />
        </div>
      </div>
    </template>
    <template v-else>
      <div class="chat-area">
        <div class="chat-msg-list" ref="chatListRef">
          <div v-for="msg in messages" :key="msg.id" :class="['msg-row', msg.role]">
            <template v-if="msg.role == 'assistant'">
              <el-avatar 
                :size="40" 
                src="/ai.png"
                class="avatar-left"
              />
              <div class="msg-bubble ai">
                <div class="msg-content">{{ msg.content }}</div>
                <div class="msg-meta">
                  <span class="msg-time">{{ msg.time }}</span>
                </div>
              </div>
            </template>
            <template v-else style="justify-content: flex-start;">
              <el-avatar
                :size="40"
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
        <div class="chat-input-card">
          <div class="input-inner">
            <textarea
              class="main-input-simple"
              v-model="input"
              placeholder="发消息、输入 @ 选择技能或 / 选择文件"
              @keyup.enter="send"
              rows="1"
              @input="autoResize"
            />
            <button class="send-btn" @click="send" :disabled="loading || !input.trim()">
              <el-icon><Top /></el-icon>
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { nextTick } from 'vue'
import { useStore } from '@/store/user.js'
import { Top } from '@element-plus/icons-vue'
import dialogueApi from '@/api/ai/dialogue.js'
import { useAiStore } from '@/store/ai'

export default {
  components: {
    Top
  },
  setup() {
    const store = useStore()
    const aiStore = useAiStore()
    return {
      store,
      aiStore
    }
  },
  data() {
    return {
      input: '',
      messages: [],
      isChatting: false,
      loading: false,
      kb_id: 1,
    }
  },
  computed: {
    currentDialogueId() {
      return this.aiStore.currentDialogueId
    }
  },
  created() {
    // 如果有chat_id，加载历史消息
    if (this.currentDialogueId) {
      this.loadChatHistory()
    }
  },
  methods: {
    setMessages(messages) {
      if (messages) {
        this.messages = messages.map(msg => ({
          id: Date.now() + Math.random(),
          role: msg.role,
          content: msg.content,
          time: new Date(msg.timestamp).toLocaleTimeString()
        }))
        this.isChatting = true
        this.scrollToBottom()
      }
    },
    async loadChatHistory() {
      dialogueApi.getDetails(this.aiStore.currentDialogueId).then(response => {
        this.setMessages(response.messages)
      }).catch(error => {
        
      })
    },
    async send_Initialization (){
      if (!this.input.trim() || this.loading) return
      this.loading = true
      const chat_id = ""
      this.aiStore.currentDialogueId = 1
      
      // 立即添加用户消息到对话区
      const userMessage = {
        id: Date.now(),
        role: 'user',
        content: this.input,
        time: new Date().toLocaleTimeString()
      }
      this.messages.push(userMessage)
      this.isChatting = true
      this.scrollToBottom()

      // 立即添加 AI 消息占位到对话区
      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: '',
        time: new Date().toLocaleTimeString()
      }
      this.messages.push(aiMessage)
      this.scrollToBottom()

      try {
        const whl = this.input
        this.input = ''
        const response = await dialogueApi.sendStreamMessage(
          whl, 
          this.store.user.id, 
          this.kb_id, 
          chat_id
        )
        const chatId = response.headers.get('X-Chat-ID')
        
        if (chatId) {
          this.aiStore.setCurrentDialogueId(chatId)
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
    async send() {
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
        
        console.log('Current chat_id:', this.currentDialogueId)
        const response = await dialogueApi.sendStreamMessage(
          whl, 
          this.store.user.id, 
          this.kb_id, 
          this.currentDialogueId
        )
        const chatId = response.headers.get('X-Chat-ID')
        
        if (chatId) {
          this.aiStore.setCurrentDialogueId(chatId)
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
    scrollToBottom() {
      nextTick(() => {
        if (this.$refs.chatListRef) {
          this.$refs.chatListRef.scrollTop = this.$refs.chatListRef.scrollHeight
        }
      })
    },
    autoResize(e) {
      const el = e.target
      el.style.height = 'auto'
      el.style.height = el.scrollHeight + 'px'
    },
    handleAvatarError() {
      // 处理头像加载错误
    }
  }
}
</script>

<style lang="less" scoped>
@import '@/assets/less/ai.less';
.simple-input-card {
  background: #fff !important;
  border: 1px solid #e5e6eb;
  border-radius: 16px;
  box-shadow: none;
  //padding: 18px 18px 12px 18px;
}
.main-input {
  background: #fff !important;
  border: none;
  outline: none;
  width: 100%;
  min-height: 50px;
  max-height: 200px;
  resize: none;
  border-radius: 8px;
  font-size: 17px;
  box-shadow: none;
  margin: 0;
  padding: 0;
  line-height: 1.7;
}
.main-input-simple {
    //background: #fff !important;
  border: none;
  outline: none;
  width: 100%;
  min-height: 50px;
  max-height: 100px;
  resize: none;
  border-radius: 8px;
  font-size: 17px;
  box-shadow: none;
  margin: 0;
  padding: 0;
  line-height: 1.7;
}
.chat-area {
  padding-left: 5px;
  padding-right: 5px;
    height: 700px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-msg-list {
    height: 700px;
  flex: 1;
  overflow-y: auto;
}

.chat-input-card {
  //background: #fff;
  //border: 1px solid #e5e6eb;
  border-radius: 16px;
  box-shadow: none;
  padding: 18px 18px 12px 18px;
  margin-top: 0;
  // 不要 position: absolute;
}

.input-inner {
  display: flex;
  align-items: flex-end;
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
}
.send-btn:disabled {
  background: #e5e6eb;
  color: #bbb;
  cursor: not-allowed;
}
.send-btn:not(:disabled):hover {
  background: #1876d1;
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
  border-radius: 16px;
  background: #f5f6fa;
  font-size: 16px;
  word-break: break-all;
  margin-top: 0;
}
.msg-bubble.assistant {
  background: #f5f6fa;
  color: #333;
  border-top-left-radius: 0;
}
.msg-bubble.user {
  background: #409eff;
  color: #fff;
  border-top-right-radius: 0;
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
</style>
