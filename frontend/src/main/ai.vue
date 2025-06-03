<template>
  <div class="ai-page-container">
    <!-- 左侧侧边栏 -->
    <div class="sidebar">
      <div class="sidebar-header">
        <div class="header-content">
          <div class="left-section">
            <h3>AI 助手</h3>
          </div>
          <el-button 
            type="primary" 
            size="default" 
            @click="createNewChat"
            :icon="Plus"
            class="new-chat-btn"
          >
            新建对话
          </el-button>
        </div>
      </div>
      <div class="chat-list">
        <div class="group-title">最近十条</div>
        <div
          v-for="chat in chatList.slice(0, 10)"
          :key="chat.id"
          class="chat-item"
          :title="chat.title"
          style="border-width: 4px !important;"
          @click="openChat(chat.chat_id)"
        >
          {{ chat.title}}
        </div>
      </div>
    </div>
    <!-- 右侧主对话区 -->
    <Dialogue ref="dialogue" />
  </div>
</template>

<script>
import Dialogue from '@/components/ai/dialogue.vue'
import { useAiStore } from '@/store/ai'
import { Plus } from '@element-plus/icons-vue'
import dialogueApi from '@/api/ai/dialogue.js'
export default {
  name: 'AIPage',
  components: {
    Dialogue,
    Plus
  },
  setup() {
    const aiStore = useAiStore()
    return {
      aiStore
    }
  },
  data() {
    return {
      chatList: []
    }
  },
  created() {
    // 页面创建时获取历史记录
    this.fetchChatHistory()
  },
  methods: {
    openChat(id){
      dialogueApi.getDetails(id).then(res => {
        this.aiStore.setCurrentDialogueId(res.chat_id)
        // 将消息数据传递给 Dialogue 组件
        this.$refs.dialogue.setMessages(res.messages)
      })
    },
    createNewChat() {
      this.aiStore.clearCurrentDialogue()
      // 清除对话组件中的消息
      this.$refs.dialogue.setMessages([])
    },
    async fetchChatHistory() {
      try {
        const res = await dialogueApi.getHistory()
        // 假设后端返回 [{id, title}] 或 [{chat_id, title}]
        if (res && res.data) {
          this.chatList = res.data.history
        }
      } catch (e) {
        console.error('获取历史会话失败', e)
      }
    }
  }
}
</script>

<style lang="less" scoped>
@import '@/assets/less/ai.less';

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  
  .left-section {
    h3 {
      margin: 0;
    }
  }

  .new-chat-btn {
    font-size: 14px;
    padding: 8px 16px;
  }
}

.sidebar {
  .sidebar-header {
    padding: 24px 8px 0;
  }
  
  .group-title {
    margin: 18px 0 8px 24px;
  }
}
</style>