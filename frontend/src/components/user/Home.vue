<template>
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
</template>

<script setup>
import { computed, ref } from 'vue'

// 数据
const total = ref(11)
const solved = ref(8)
const inProgress = ref(18)

const easyTotal = ref(2)
const easySolved = ref(1)
const mediumTotal = ref(4)
const mediumSolved = ref(3)
const hardTotal = ref(5)
const hardSolved = ref(4)

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
</script>

<style scoped>
.home {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 0;
}
.stats-container {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 30px;
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 4px 24px 0 rgba(0,0,0,0.06);
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

