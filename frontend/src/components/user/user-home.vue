<template>
  <div class="user-home">
    <div class="home">
    <div class="stats-container">
      <!-- 环形图表 -->
      <div class="circle-container">
        <!-- 背景环（淡色） -->
        <div class="progress-bg" :style="[bgStyle, { transform: 'rotate(210deg)' }]" ></div>
        <!-- 前景环（深色） -->
        <div class="progress-fg" :style="[fgStyle, { transform: 'rotate(210deg)' }]" ></div>
        <!-- 内部白色圆 -->
        <div class="circle-inner"></div>
        <!-- 中心内容 -->
        <div class="center-content">
          <div class="solved-row">
            <div class="solved-count">{{ solved }}</div>
            <div class="total-count">/{{ total }}</div>
          </div>
          <div class="solved-text">✓ 已解答</div>
        </div>
        <!-- 尝试中文本 -->
        <div class="in-progress">{{ inProgress }} 尝试中</div>
      </div>
      <!-- 右侧统计 -->
      <div class="stats-sidebar">
        <div class="difficulty-stats easy">
          <div class="difficulty-name">简单</div>
          <div class="difficulty-count">{{ easySolved }}/{{ easyTotal }}</div>
        </div>
        <div class="difficulty-stats medium">
          <div class="difficulty-name">中等</div>
          <div class="difficulty-count">{{ mediumSolved }}/{{ mediumTotal }}</div>
        </div>
        <div class="difficulty-stats hard">
          <div class="difficulty-name">困难</div>
          <div class="difficulty-count">{{ hardSolved }}/{{ hardTotal }}</div>
        </div>
      </div>
    </div>
  </div>
    <div class="profile-container">
      <h2 class="section-title">个人信息</h2>
      <div class="profile-content">
        <div class="profile-left">
          <div class="info-group">
            <div class="info-item">
              <span class="info-label">realName：</span>
              <span class="info-value">{{ userInfo.realName || '未设置' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">school：</span>
              <span class="info-value">{{ userInfo.school || '未设置' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">major：</span>
              <span class="info-value">{{ userInfo.major || '未设置' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">language：</span>
              <span class="info-value">{{ userInfo.language || '中文' }}</span>
            </div>
          </div>
        </div>
        <div class="profile-right">
          <div class="info-group">
            <div class="info-item">
              <span class="info-label">mood：</span>
              <span class="info-value">{{ userInfo.mood || '未设置' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">blog：</span>
              <a v-if="userInfo.blog" :href="userInfo.blog" target="_blank" class="link">{{ userInfo.blog }}</a>
              <span v-else class="info-value">未设置</span>
            </div>
            <div class="info-item">
              <span class="info-label">GitHub：</span>
              <a v-if="userInfo.github" :href="userInfo.github" target="_blank" class="link">{{ userInfo.github }}</a>
              <span v-else class="info-value">未设置</span>
            </div>
            <!-- <div class="info-item">
              <span class="info-label">注册时间：</span>
              <span class="info-value">{{ userInfo.create_time ? new Date(userInfo.create_time).toLocaleDateString() : '未知' }}</span>
            </div> -->
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue';
import * as echarts from 'echarts';
import userHomeApi from '@/api/user/home';
import { useStore } from '../../store/user.js'

// 创建一个响应式引用来保存DOM元素
const chartDom = ref(null);
let chartInstance = null;

const store = useStore()

const userInfo = ref({
  username: '',
  email: '',
  realName: '',
  school: '',
  major: '',
  language: '',
  mood: '',
  blog: '',
  github: '',
  avatar: '',
  create_time: ''
});

// 数据
const total = ref(11)
const solved = ref(7)
const inProgress = ref(2)

const easyTotal = ref(2)
const easySolved = ref(1)
const mediumTotal = ref(4)
const mediumSolved = ref(3)
const hardTotal = ref(5)
const hardSolved = ref(3)

// 获取用户信息
const getUserInfo = async () => {
  try {
    const userId = store.user.id
    if (!userId) {
      console.error('未找到用户ID');
      return;
    }

    const response = await userHomeApi.GetUserHome(userId);
    if (response.code == 0) {
      console.log(response.data)
      const data = response.data;
      userInfo.value = {
        username: data.username || '',
        email: data.email || '',
        realName: data.real_name || '',
        school: data.school || '',
        major: data.major || '',
        language: data.language || '中文',
        mood: data.mood || '',
        blog: data.blog || '',
        github: data.github || '',
        avatar: data.avatar || '',
        create_time: data.create_time || ''
      };
    } else {
      console.error('获取用户信息失败:', response.message);
    }
  } catch (error) {
    console.error('获取用户信息出错:', error);
  }
};

// 各段总角度（总共300度，底部缺口60度）
const easyAngle = computed(() => (easyTotal.value / total.value) * 300)
const mediumAngle = computed(() => (mediumTotal.value / total.value) * 300)
const hardAngle = computed(() => (hardTotal.value / total.value) * 300)

// 各段已完成角度
const easyDone = computed(() => easyAngle.value * (easySolved.value / easyTotal.value))
const mediumDone = computed(() => mediumAngle.value * (mediumSolved.value / mediumTotal.value))
const hardDone = computed(() => hardAngle.value * (hardSolved.value / hardTotal.value))

// 分段间隔角度
const gap = 2;

// 背景环（淡色，分段+间隔）
const bgStyle = computed(() => {
  const e = easyAngle.value;
  const m = mediumAngle.value;
  const h = hardAngle.value;
  return {
    background: `conic-gradient(
      #b8e9d0 0deg ${e - gap / 2}deg,
      transparent ${e - gap / 2}deg ${e + gap / 2}deg,
      #ffe7a8 ${e + gap / 2}deg ${e + m - gap / 2}deg,
      transparent ${e + m - gap / 2}deg ${e + m + gap / 2}deg,
      #f7bdbd ${e + m + gap / 2}deg ${e + m + h - gap / 2}deg,
      transparent ${e + m + h - gap / 2}deg 360deg
    )`
  }
})

// 前景环（深色，分段已完成+间隔）
const fgStyle = computed(() => {
  const e = easyAngle.value;
  const m = mediumAngle.value;
  const ed = easyDone.value;
  const md = mediumDone.value;
  const hd = hardDone.value;
  return {
    background: `conic-gradient(
      #33cc99 0deg ${ed - gap / 2}deg,
      transparent ${ed - gap / 2}deg ${e + gap / 2}deg,
      #ffc53d ${e + gap / 2}deg ${e + md - gap / 2}deg,
      transparent ${e + md - gap / 2}deg ${e + m + gap / 2}deg,
      #ff7875 ${e + m + gap / 2}deg ${e + m + hd - gap / 2}deg,
      transparent ${e + m + hd - gap / 2}deg 360deg
    )`
  }
})

// 初始化
onMounted(async () => {
  await getUserInfo(); // 获取用户信息
  await nextTick();
  
  chartInstance = echarts.init(chartDom.value);
  
  // 计算各难度占比
  const totalProblems = 333 + 333 + 333; // 总题目数
  const easyRatio = 333 / totalProblems;
  const mediumRatio = 333 / totalProblems;
  const hardRatio = 333 / totalProblems;
  
  // 计算总通过率
  const solvedTotal = 115 + 239 + 19;
  const problemTotal = 996 + 2038 + 903;
  const passRate = (solvedTotal / problemTotal * 100).toFixed(2);

  const option = {
    series: [{
      type: 'gauge',
      startAngle: 150,
      endAngle: -210,
      pointer: {
        show: false
      },
      progress: {
        show: true,
        overlap: false,
        roundCap: true,
        clip: false,
        itemStyle: {
          borderWidth: 0
        }
      },
      axisLine: {
        lineStyle: {
          width: 15,
          color: [
            [easyRatio, '#83b46b'],      // 简单题占比
            [easyRatio + mediumRatio, '#eabf52'],  // 中等题占比
            [1, '#df0d0d']               // 困难题占比
          ]
        }
      },
      splitLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        show: false
      },
      data: [{
        value: passRate,
        detail: {
          show: true
        }
      }],
      detail: {
        show: true,
        offsetCenter: [0, -20],
        formatter: function() {
          return `{value|${passRate}}%\n{label|通过率}\n{submit|1K 次提交}`;
        },
        rich: {
          value: {
            fontSize: 36,
            fontWeight: 'bold',
            color: '#262626',
            padding: [0, 0, 0, 0],
            lineHeight: 40
          },
          label: {
            fontSize: 14,
            color: '#262626',
            padding: [0, 0, 10, 0]
          },
          submit: {
            fontSize: 12,
            color: '#8C8C8C',
            padding: [10, 0, 0, 0]
          }
        }
      }
    }]
  };
  chartInstance.setOption(option);
});

// 销毁ECharts实例
onUnmounted(() => {
  if (chartInstance != null && chartInstance.dispose) {
    chartInstance.dispose();
  }
});
</script>

<style scoped>
.user-home {
  padding: 10px 40px;
}

.stats-container {
  display: flex;
  align-items: center;
  border-radius: 8px;
  padding: 20px;
}

.chart-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.chart-container {
  width: 300px;
  height: 300px;
}

.attempts {
  position: absolute;
  bottom: 20px;
  font-size: 14px;
  color: #8C8C8C;
}

.difficulty-stats {
  margin-left: 40px;
}

.stat-item {
  margin: 15px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 200px;
}

.profile-container {
  border-radius: 8px;
  margin-left: 60px;  /* 向右偏移，与圆环图对齐 */
  margin-top: 10px;
  margin-bottom: 20px;
  width: 600px;  /* 固定宽度 */
}

.section-title {
  font-size: 18px;
  color: #303133;
  margin: 0 0 20px 0;
  padding-bottom: 10px;
  /* border-bottom: 1px solid #EBEEF5; */
}

.profile-content {
  display: flex;
  gap: 40px;
}

.profile-left, .profile-right {
  flex: 1;
  min-width: 0;
}

.info-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: flex-start;
}

.info-label {
  min-width: 80px;
  color: #606266;
  font-size: 14px;
}

.info-value {
  color: #303133;
  font-size: 14px;
  flex: 1;
  word-break: break-all;
}

.link {
  color: #303133;
  text-decoration: none;
  font-size: 14px;
  &:hover {
    color: #409EFF;
    text-decoration: underline;
  }
}

.label {
  font-size: 16px;
}

.value {
  font-size: 14px;
  color: #606266;
}

.easy .label {
  color: #83b46b;
}

.medium .label {
  color: #eabf52;
}

.hard .label {
  color: #df0d0d;
}
.home {
  max-width: 800px;
  /* margin: 0 auto; */
  padding: 30px 0;
}
.stats-container {
  /* display: flex;
  align-items: center;
  justify-content: center; */
  /* margin-left: 20px; */
  /* margin-top: 30px; */
  /* background: #fff; */
  border-radius: 18px;
  /* box-shadow: 0 4px 24px 0 rgba(202, 198, 198, 0.06); */
  padding: 40px 40px 32px 40px;
}
.circle-container {
  position: relative;
  width: 260px;
  height: 260px;
  margin-right: 40px;
}
.progress-bg, .progress-fg {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  border-radius: 50%;
  z-index: 1;
}
.progress-fg { z-index: 2; }
.circle-inner {
  position: absolute;
  top: 2%; left: 2%;
  width: 96%; height: 96%;
  border-radius: 50%;
  background: #fff;
  z-index: 3;
}
.center-content {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  width: 80%;
  z-index: 4;
}
.solved-row {
  display: flex;
  align-items: baseline;
  justify-content: center;
}
.solved-count {
  font-size: 40px;
  font-weight: bold;
  line-height: 1;
}
.total-count {
  font-size: 18px;
  color: #999;
  margin-top: 0;
  line-height: 1;
}
.solved-text {
  color: #33cc99;
  font-size: 14px;
  margin-top: 10px;
}
.in-progress {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  color: #666;
  font-size: 14px;
  z-index: 4;
}
.stats-sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-left: 40px;
}
.difficulty-stats {
  background-color: #f5f5f5;
  padding: 15px 30px;
  border-radius: 8px;
  text-align: center;
  min-width: 130px;
}
.difficulty-name {
  font-size: 14px;
  margin-bottom: 4px;
}
.difficulty-count {
  font-size: 16px;
  font-weight: bold;
}
.easy .difficulty-name { color: #33cc99; }
.medium .difficulty-name { color: #ffc53d; }
.hard .difficulty-name { color: #ff7875; }
</style>