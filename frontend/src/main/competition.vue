<!-- eslint-disable vue/no-multiple-template-root -->
<template>
    <div class="page-container">
      <div class="contest-header">
        <h2>All Contests</h2>
      </div>
  
      <div class="contest-list">
        <div 
          v-for="contest in contests" 
          :key="contest.id"
          class="contest-item"
          @click="handleContestClick(contest)"
        >
          <div class="contest-info">
            <div class="contest-title">
              {{ contest.title }}
            </div>
            
            <div class="contest-meta">
              <span>{{ contest.startTime }}</span>
              <span>{{ contest.duration }}</span>
              <span>{{ contest.rule }}</span>
            </div>
          </div>
          <div class="contest-status">
            <div class="status-box">
              <span class="status-dot" :class="getStatusDotClass(contest.status)"></span>
              <span class="status-text">{{ contest.status }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="pagination" style="margin-right: 30px;">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalContests"
          :page-sizes="[10, 20, 50, 100]"
          layout="prev, pager, next, sizes"
          background
        />
    </div>
</template>
  
<script>
import competitionApi from '@/api/competition/competition.js'
import { useCompetitionStore } from '@/store/competition'

export default {
  name: 'Competition',
  data() {
    return {
      keyword: '',
      rule: '',
      status: '',
      currentPage: 1,
      pageSize: 10,
      totalContests: 100,
      contests: []
    }
  },
  setup() {
    const competitionStore = useCompetitionStore()
    return { competitionStore }
  },
  created() {
    this.fetchContests()
  },
  methods: {
    fetchContests() {
      competitionApi.GetContests(this.currentPage, this.pageSize).then(response => {
        if (response.data.code === 0) {
          this.contests = response.data.data.map(contest => {
            // 时间计算
            const now = new Date()
            const beijingNow = new Date(now.getTime() + 8 * 60 * 60 * 1000 - now.getTimezoneOffset() * 60 * 1000)
            const start = new Date(contest.start_time)
            const end = new Date(contest.end_time)
            let status = ''
            if (beijingNow < start) {
              status = 'Upcoming'
            } else if (beijingNow >= start && beijingNow < end) {
              status = 'Underway'
            } else {
              status = 'Ended'
            }

            return {
              id: contest.id,
              title: contest.title,
              startTime: this.formatDate(contest.start_time),
              endTime: this.formatDate(contest.end_time),
              start_time: contest.start_time,
              end_time: contest.end_time,
              duration: this.calculateDuration(contest.start_time, contest.end_time),
              status: status,
              rule: contest.rule_type == 0 ? 'ACM' : 'OI',
              created_by: contest.created_by,
              description: contest.description || '',
              type: contest.contest_type || '密码保护'
            }
          })
          this.totalContests = response.data.total
        }
      }).catch(error => {
        console.error('获取比赛列表失败:', error)
      })
    },
    calculateDuration(startTime, endTime) {
      const start = new Date(startTime)
      const end = new Date(endTime)
      const durationInDays = (end - start) / (1000 * 60 * 60 * 24)
      return `${durationInDays.toFixed(1)} days`
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      const year = date.getFullYear()
      const month = date.getMonth() + 1
      const day = date.getDate()
      const hours = date.getHours().toString().padStart(2, '0')
      const minutes = date.getMinutes().toString().padStart(2, '0')
      return `${year}-${month}-${day} ${hours}:${minutes}`
    },
    getStatusDotClass(status) {
      if (status === 'Underway') return 'underway'
      if (status === 'Upcoming') return 'upcoming'
      if (status === 'Ended') return 'ended'
      return ''
    },
    handleContestClick(contest) {
      if (contest.status == 'Ended' || contest.status == 'Upcoming') return
      console.log(contest.id)
      const id = contest.id.toString()
      
      // 确保存储完整的比赛信息到Pinia
      this.competitionStore.setContest({
        id: id,
        title: contest.title,
        startTime: contest.startTime,
        endTime: contest.endTime,
        start_time: contest.start_time,
        end_time: contest.end_time,
        rule: contest.rule,
        creator: contest.created_by,
        status: contest.status,
        type: contest.type,
        description: contest.description || '',
        remainingTime: '',
        real_time_rank: false,
        visible: true,
      })
      
      // 确保在路由跳转前数据已经更新
      this.$nextTick(() => {
        this.$router.push({
          path: `/match/${id}/overview`
        })
      })
    },
    verifyPassword() {
      const currentId = this.$route.params.id
      if (!currentId || currentId === 'route') {
        console.error('无效的比赛ID')
        return
      }
      
      console.log('验证密码，当前ID:', currentId)
      match.ProblemSubmit(this.passwordDialog.form.password).then(response => {
        if (response.data === "ok") {
          console.log('密码验证成功，添加认证ID:', currentId)
          this.competitionStore.addAuthenticatedContest(currentId)
          ElMessage.success('密码验证成功')
        } else {
          ElMessage.error('密码错误')
        }
      }).catch(error => {
        console.error(error)
        ElMessage.error('验证失败，请稍后重试')
      })
    }
  },
  watch: {
    currentPage() {
      this.fetchContests()
    },
    pageSize() {
      this.currentPage = 1
      this.fetchContests()
    }
  }
}
</script>
  
<style lang="less" scoped>
@import '@/assets/less/competition.less';

.status-box {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 8px;
  padding: 2px 10px 2px 6px;
  width: fit-content;
}
.status-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 6px;
  background: #e0e0e0;
}
.status-dot.underway {
  background: #1ec972;
}
.status-dot.upcoming {
  background: #409eff;
}
.status-dot.ended {
  background: #bfbfbf;
}
.status-text {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}
</style>