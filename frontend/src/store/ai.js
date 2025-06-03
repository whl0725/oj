import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAiStore = defineStore('ai', {
  state: () => ({
    currentDialogueId: ref(localStorage.getItem('currentDialogueId') || '')
  }),
  
  actions: {
    setCurrentDialogueId(chatId) {
      this.currentDialogueId = chatId
      localStorage.setItem('currentDialogueId', chatId)
    },
    
    clearCurrentDialogue() {
      this.currentDialogueId = ''
      localStorage.removeItem('currentDialogueId')
    }
  }
})
