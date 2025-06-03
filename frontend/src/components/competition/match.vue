<template>
  <div class="overview-content" style="padding: 15px;">
      <h1 class="contest-title">{{ contestInfo.title }}</h1>
      <div class="contest-time">
        <span class="status-dot" :class="{ 'running': contestInfo.status === 'Underway' }"></span>
        {{ contestInfo.remainingTime }}
      </div>

      <div class="contest-description" v-html="contestInfo.description"></div>
        
      <div class="password-input-container" v-if="contestInfo.ContestType == '1' && !isPasswordCorrect && !store.isAuthenticated($route.params.id)">
        <input 
          type="text"
          class="contest-password"
          placeholder="contest password"
          v-model="passwordDialog.form.password"
        />
        <button class="enter-btn" @click="verifyPassword">Enter</button>
      </div>
      <table class="contest-info-table">
        <thead>
          <tr>
            <th>StartAt</th>
            <th>EndAt</th>
            <th>ContestType</th>
            <th>Rule</th>
            <th>Creator</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{{ contestInfo.startTime }}</td>
            <td>{{ contestInfo.endTime }}</td>
            <td>{{ contestInfo.ContestType == '1' ? 'Password Protected' : 'Public' }}</td>
            <td>{{ contestInfo.rule_type == '0' ? 'ACM' : 'OI' }}</td>
            <td>{{ contestInfo.created_by }}</td>
          </tr>
        </tbody>
      </table>     
    </div>
</template>

<script>
import { HomeFilled, Message, Document, List, TrendCharts } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import match from '@/api/competition/match'
import { useCompetitionStore } from '@/store/competition'
import { storeToRefs } from 'pinia'
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'ContestMatch',
  components: {
    HomeFilled,
    Message,
    Document,
    List,
    TrendCharts
  },
  setup() {
    const store = useCompetitionStore()
    const route = useRoute()
    return {
      store,
      route
    }
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
        rule_type: '',
        created_by: '',
        status: '',
        remainingTime: '',
        real_time_rank: '',
        visible: '',
        ContestType: '',
      },
      passwordDialog: {
        form: {
          password: ''
        }
      },
      timer: null,
      isPasswordCorrect: false
    }
  },
  created() {
    // 初始化时从 store 中读取认证状态
    const matchId = this.$route.params.id
    if (this.store.isAuthenticated(matchId)) {
      this.isPasswordCorrect = true
      // 通知父组件更新状态
      this.$emit('password-verified', true)
      if (this.$parent && this.$parent.updatePasswordStatus) {
        this.$parent.updatePasswordStatus(true)
      }
    }

    match.Description(matchId).then(response => {
      const data = response.data[0];
      // 格式化时间
      if (data) {
        this.contestInfo = {
          ...data,
          startTime: this.formatDate(data.startTime || data.start_time),
          endTime: this.formatDate(data.endTime || data.end_time)
        };
        
        // 启动倒计时
        this.startCountdown();
      }
    })
  },
  beforeUnmount() {
    // 清除定时器
    if (this.timer) {
      clearInterval(this.timer);
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '';
      
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return dateString; // 如果解析失败，返回原字符串
      
      const year = date.getFullYear();
      const month = date.getMonth() + 1; // 月份从0开始
      const day = date.getDate();
      const hours = date.getHours().toString().padStart(2, '0');
      const minutes = date.getMinutes().toString().padStart(2, '0');
      
      return `${year}-${month}-${day} ${hours}:${minutes}`;
    },
    startCountdown() {
      // 清除旧的定时器
      if (this.timer) {
        clearInterval(this.timer);
      }
      
      // 更新一次时间
      this.updateRemainingTime();
      
      // 每秒更新一次
      this.timer = setInterval(() => {
        this.updateRemainingTime();
      }, 1000);
    },
    updateRemainingTime() {
      const now = new Date();
      const startTime = new Date(this.contestInfo.start_time);
      const endTime = new Date(this.contestInfo.end_time);
      
      // 处理时间无效的情况
      if (isNaN(startTime.getTime()) || isNaN(endTime.getTime())) {
        this.contestInfo.remainingTime = "无效";
        this.contestInfo.status = "未知";
        return;
      }
      
      // 计算比赛状态
      if (now < startTime) {
        // 比赛未开始
        this.contestInfo.status = "未开始";
        const diff = startTime - now;
        this.contestInfo.remainingTime = this.formatTimeRemaining(diff);
      } else if (now > endTime) {
        // 比赛已结束
        this.contestInfo.status = "已结束";
        this.contestInfo.remainingTime = "00:00:00";
      } else {
        // 比赛进行中
        this.contestInfo.status = "Underway"; // 使用原有的"Underway"值保持样式一致
        const diff = endTime - now;
        this.contestInfo.remainingTime = this.formatTimeRemaining(diff);
      }
    },
    formatTimeRemaining(ms) {
      // 计算总小时数（不拆分为天）
      const totalHours = Math.floor(ms / (60 * 60 * 1000));
      ms -= totalHours * 60 * 60 * 1000;
      
      const minutes = Math.floor(ms / (60 * 1000));
      ms -= minutes * 60 * 1000;
      
      const seconds = Math.floor(ms / 1000);
      
      // 格式化为 -HHH:MM:SS 格式
      return `-${totalHours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    },
    verifyPassword() {
      match.Password(this.$route.params.id, this.passwordDialog.form.password).then(response => {
        
        //data = response.data
        if(response.data == 'ok'){
          ElMessage.success('Password is Correct')
          
          // 更新密码验证状态
          this.isPasswordCorrect = true
          
          // 发送事件通知父组件更新密码状态
          this.$emit('password-verified', true)
          
          // 更新父组件的状态 (访问父组件的方法)
          if (this.$parent && this.$parent.updatePasswordStatus) {
            this.$parent.updatePasswordStatus(true)
          }
          
          // 跳转到问题页面
          this.$router.push({ path: '/match/' + this.$route.params.id + '/problem' })
        }else{
          ElMessage.error('Password is Incorrect')
        }
      }).catch(error => {
        console.error('获取比赛密码失败:', error);
      });
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
}

.contest-container {
  flex: 1;
  width: auto;
  margin: 0 auto;
  display: flex;
}

.contest-main {
  width: 1400px;
  background: #fff;
  padding: 15px;
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
    font-size: 16px;
    width: auto;
    height: 36px;
    padding: 0 15px;
    border-radius: 4px;
    background-color: #fff;
    border: 1px solid #e4e7ed;

    .status-dot {
      width: 10px;
      height: 10px;
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
  height: 230px;
  background: #fff;
  width: 200px;
  padding: 0;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

  .menu-item {
    padding: 15px 20px;
    color: #606266;
    font-size: 14px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: all 0.3s;
    border-left: 3px solid transparent;

    &:hover:not(.disabled) {
      color: #409EFF;
      background-color: #f5f7fa;
    }

    &.active {
      color: #409EFF;
      background-color: #f5f7fa;
      border-left: 3px solid #409EFF;
    }

    &.disabled {
      color: #c0c4cc;
      cursor: not-allowed;
      background-color: #fafafa;
      opacity: 0.7;

      .el-icon {
        color: #c0c4cc;
      }

      &:hover {
        color: #c0c4cc;
        background-color: #fafafa;
      }
    }

    .el-icon {
      font-size: 16px;
      color: inherit;
      width: 20px;
    }
  }
}
</style>
