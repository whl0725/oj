import { defineStore } from 'pinia'

export const useCompetitionStore = defineStore('competition', {
  state: () => ({
    contests: {}, // 比赛信息对象
    authenticatedContests: [], // 已通过密码校验的比赛ID数组
  }),

  getters: {
    // 判断某个比赛是否已认证
    isAuthenticated: (state) => (contestId) => {
      // 确保是数组并且包含contestId
      return Array.isArray(state.authenticatedContests) && 
             state.authenticatedContests.includes(contestId)
    },
    // 获取比赛信息
    getContest: (state) => (contestId) => {
      return state.contests[contestId] || null
    }
  },

  actions: {
    // 初始化 store
    initStore() {
      if (!Array.isArray(this.authenticatedContests)) {
        this.authenticatedContests = []
      }
    },

    // 设置比赛信息
    setContest(contest) {
      if (!contest?.id) {
        throw new Error('比赛ID不能为空')
      }
      const defaultContest = {
        id: null,
        title: '',
        startTime: '',
        endTime: '',
        start_time: '',
        end_time: '',
        rule: '',
        creator: '',
        status: '',
        remainingTime: '',
        real_time_rank: false,
        visible: true,
      }
      this.contests[contest.id] = {
        ...defaultContest,
        ...contest
      }
    },

    // 认证通过，记录比赛ID
    authenticateContest(contestId) {
      this.initStore() // 确保初始化
      if (!this.authenticatedContests.includes(contestId)) {
        this.authenticatedContests.push(contestId)
      }
    },

    // 取消认证（如退出比赛时调用）
    deauthenticateContest(contestId) {
      this.initStore() // 确保初始化
      this.authenticatedContests = this.authenticatedContests.filter(id => id !== contestId)
    },

    // 清空所有认证（如登出时调用）
    clearAllAuthenticated() {
      this.authenticatedContests = []
    },

    // 为了兼容性，保留原来的方法名
    matchMedia(id) {
      return this.contests[id] || null
    }
  },

  persist: {
    enabled: true,
    strategies: [
      {
        key: 'competition',
        storage: localStorage,
        paths: ['authenticatedContests', 'contests']  // 同时持久化 contests
      }
    ]
  }
}) 