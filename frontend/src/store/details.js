import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useDetailsStore = defineStore('details', {
  state: () => ({
    details_id: ref(localStorage.getItem('details_id') || ''),
    //messages: ref(JSON.parse(localStorage.getItem('ai_messages') || '[]'))
  }),
  actions: {
    setDetailsId(detailsId) {
      this.details_id = detailsId
      localStorage.setItem('details_id', detailsId)
    },
    setMessages(messages) {
      this.messages = messages
      localStorage.setItem('ai_messages', JSON.stringify(messages))
    },
    clearAll(){
      this.details_id = ''
      localStorage.removeItem('details_id')
      this.messages = []
      localStorage.removeItem('ai_messages')
    }
  },
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'details',
        storage: localStorage,
        paths: ['details_id', 'messages']
      }
    ]
  }
})
