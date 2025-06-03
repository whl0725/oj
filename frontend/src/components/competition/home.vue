<template>
  <div class="view-container">
    <div class="contest-container">
      <div class="contest-main">
        <router-view @password-verified="updatePasswordStatus"></router-view>
      </div>
      <el-menu 
        class="side-menu"
        :default-active="route.path"
        mode="vertical"
        router>
        <el-menu-item 
          :index="`/match/${route.params.id}/overview`"
        >
          <el-icon><HomeFilled /></el-icon>
          <span>Overview</span>
        </el-menu-item>
        <el-menu-item 
          :index="`/match/${route.params.id}/announcement`"
          :disabled="isPasswordProtected && !isPasswordCorrect"
          @click="handleMenuClick($event, 'announcement')">
          <el-icon><Message /></el-icon>
          <span>Announcements</span>
        </el-menu-item>
        <el-menu-item 
          :index="`/match/${route.params.id}/problem`"
          :disabled="isPasswordProtected && !isPasswordCorrect"
          :class="{'sidebar-highlight': isPasswordProtected && isPasswordCorrect}"
          @click="handleMenuClick($event, 'problem')">
          <el-icon><Document /></el-icon>
          <span>Problems</span>
        </el-menu-item>
        <el-menu-item 
          :index="`/match/${route.params.id}/submission`"
          :disabled="isPasswordProtected && !isPasswordCorrect"
          @click="handleMenuClick($event, 'submission')">
          <el-icon><List /></el-icon>
          <span>Submissions</span>
        </el-menu-item>
        <!-- <el-menu-item 
          :index="`/match/${route.params.id}/rank`"
          :disabled="isPasswordProtected && !isPasswordCorrect"
          @click="handleMenuClick($event, 'rank')">
          <el-icon><TrendCharts /></el-icon>
          <span>Rankings</span>
        </el-menu-item> -->
      </el-menu>
    </div>  
  </div>
</template>

<script>
import { HomeFilled, Message, Document, List, TrendCharts } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import match from '@/api/competition/match'
import { useCompetitionStore } from '@/store/competition'
import { storeToRefs } from 'pinia'
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export default {
  name: 'ContestMatch',
  components: {
    HomeFilled,
    Message,
    Document,
    List,
    TrendCharts
  },
  data() {
    return {
      contestInfo: {
        id: null,
        title: '',
        description: '',
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
        password: null,
        ContestType: '0' // 默认为公开
      },
      passwordDialog: {
        form: {
          password: ''
        }
      },
      timer: null,
      isPasswordCorrect: false,
      isPasswordProtected: false
    }
  },
  created() {
    // 获取比赛信息
    match.Description(this.$route.params.id).then(response => {
      if (response.data && response.data[0]) {
        this.contestInfo = response.data[0];
        // 检查比赛类型
        this.isPasswordProtected = this.contestInfo.ContestType === '1';
      }
    }).catch(error => {
      console.error('获取比赛信息失败:', error);
    });
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const store = useCompetitionStore()
    const contestInfo = ref(null)  // 先初始化为 null
    const isPasswordCorrect = ref(false)
    const isPasswordProtected = ref(false)
    
    // 获取比赛数据并赋值
    const getContestInfo = () => {
      const contest = store.getContest(route.params.id)
      if (contest) {
        contestInfo.value = contest
        // 检查比赛类型
        isPasswordProtected.value = contest.ContestType === '1'
        // 检查认证状态
        if (store.isAuthenticated(route.params.id)) {
          isPasswordCorrect.value = true
        }
      }
    }
    
    // 处理菜单点击
    const handleMenuClick = (event, path) => {
      // 如果已禁用，则显示提示信息
      if (isPasswordProtected.value && !isPasswordCorrect.value) {
        event.preventDefault()
        ElMessage.warning('请先输入正确的比赛密码')
        router.push(`/match/${route.params.id}/overview`)
        return false
      }
      return true
    }
    
    // 更新密码验证状态
    const updatePasswordStatus = (status) => {
      isPasswordCorrect.value = status
      if (status) {
        // 密码验证成功，更新 store
        store.authenticateContest(route.params.id)
      }
    }
    
    // 立即执行一次获取数据
    onMounted(() => {
      store.initStore() // 确保 store 初始化
      getContestInfo()
    })
    
    return {
      route,
      contestInfo,
      getContestInfo,
      isPasswordCorrect,
      isPasswordProtected,
      handleMenuClick,
      updatePasswordStatus
    }
  },
  methods: {
    // 如果需要在methods中添加方法
    checkAccess(path) {
      if (this.isPasswordProtected && !this.isPasswordCorrect && path !== '/overview') {
        ElMessage.warning('请先输入正确的比赛密码');
        return false;
      }
      return true;
    }
  }
}
</script>

<style lang="less" scoped>
.view-container {
  min-height: auto;
  display: flex;
  flex-direction: column;
  margin-top: 20px;
  height: 100%;
}

.contest-container {
  flex: 1;
  width: auto;
  margin: 0 auto;
  display: flex;
  height: 100%;
}

.contest-main {
  width: 1400px;
  background: #fff;
  padding: 0px;
  margin-right: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  
  .contest-title {
    font-size: 24px;
    color: #333;
    margin: 0 0 15px 0;
    display: inline-block;
    font-weight: 500;
  }

  .contest-time {
    float: right;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: #1e1e1e;
    font-size: 14px;
    width: auto;
    height: 32px;
    padding: 0 10px;
    border-radius: 4px;
    background-color: #fff;
    border: 1px solid #e4e7ed;

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background-color: #1aaa55;
    }

    .running {
      background-color: #1aaa55;
    }
  }

  .contest-description {
    color: #666;
    margin: 20px 0;
    font-size: 14px;
    line-height: 1.5;
    clear: both;
  }

  .password-input-container {
    display: flex;
    gap: 8px;
    margin: 15px 0;

    .contest-password {
      flex: 0 1 200px;
      height: 36px;
      padding: 8px 12px;
      border: 1px solid #dcdfe6;
      border-radius: 4px;
      font-size: 14px;
      color: #606266;
      background-color: #fff;
      transition: border-color 0.2s;

      &:focus {
        outline: none;
        border-color: #409eff;
      }

      &::placeholder {
        color: #c0c4cc;
      }
    }

    .enter-btn {
      height: 36px;
      padding: 0 20px;
      background-color: #33b4ea;
      border: none;
      border-radius: 4px;
      color: white;
      font-size: 14px;
      cursor: pointer;
      transition: background-color 0.2s;

      &:hover {
        background-color: #2aa3d9;
      }
    }
  }

  .contest-info-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
    
    th, td {
      padding: 12px;
      text-align: left;
      font-size: 14px;
      border: 1px solid #ebeef5;
    }

    th {
      background-color: #fafafa;
      color: #606266;
      font-weight: 500;
    }

    td {
      color: #606266;
    }
  }
}

.side-menu {
  height: 100%;
  width: 180px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  //overflow: hidden;
}

.el-menu-item {
  display: flex;
  align-items: center;
  padding: 6px 16px;
  height: 45px;
  font-size: 14px;

  &:hover {
    color: #409EFF;
    background-color: #f5f7fa;
  }

  .el-icon {
    margin-right: 6px;
    font-size: 16px;
  }
  
  &.is-disabled {
    cursor: not-allowed;
    opacity: 0.7;
  }
}


</style>
