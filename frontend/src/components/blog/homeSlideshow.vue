<template>
  <el-card v-if="contests.length" class="contest-card" shadow="hover">
    <!-- <template #header>
      <el-button 
        link 
        class="contest-title" 
        @click="goContest"
      >
        近期比赛
      </el-button>
    </template> -->

    <div class="carousel-wrapper">
      <el-carousel 
        ref="carousel"
        trigger="hover" 
        :interval="6000"
        :height="'80px'"
        indicator-position="none"
        class="contest"
        arrow="never"
      >
        <el-carousel-item 
          v-for="(contest, idx) in contests" 
          :key="idx"
        >
          <div class="contest-content">
            <div class="contest-title">
              {{ contest.title }}
            </div>
            <div class="contest-info">
              <div class="info-tag time">
                <el-icon><Calendar /></el-icon>
                {{ formatDate(contest.start_time) }}
              </div>
              <div class="info-tag duration">
                <el-icon><Timer /></el-icon>
                {{ getDuration(contest.start_time, contest.end_time) }}
              </div>
              <div class="info-tag type">
                <el-icon><Trophy /></el-icon>
                {{ contest.rule_type }}
              </div>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
      
      <div class="carousel-controls">
        <el-button 
          class="control-btn prev" 
          @click="prev"
          circle
        >
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <el-button 
          class="control-btn next" 
          @click="next"
          circle
        >
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script>
import { Calendar, Timer, Trophy, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { formatDate } from '@/utils/format.js'

export default {
  name: "HomeSlideshow",
  components: {
    Calendar,
    Timer,
    Trophy,
    ArrowLeft,
    ArrowRight
  },
  data() {
    return {
      contests: [
        {
        title: 'python期中考试',
        start_time: '2025-1-31 08:00',
        end_time: '2025-1-31 08:00',
        rule_type: 'ACM',
      },

      {
        title: '计算机协会算法比赛',
        start_time: '2018-1-1 08:00',
        end_time: '2018-1-1 08:00',
        rule_type: 'ACM',
      }
    ]
    }
  },
  methods: {
    formatDate,
    getDuration(start, end) {
      return '0 hours'
    },
    goContest() {
      this.$router.push('/competition')
    },
    prev() {
      this.$refs.carousel.prev()
    },
    next() {
      this.$refs.carousel.next()
    }
  }
}
</script>

<style scoped>
.contest-card {
  width: 90%;
  height: 180px;
  margin: 0 auto 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.contest {
  padding: 15px 20px;
}

.contest-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.contest-title {
  font-size: 21px;
  color: #495060;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 12px;
}

.contest-info {
  display: flex;
  align-items: center;
  padding-left: 20px;
}

.info-tag {
  display: inline-flex;
  align-items: center;
  padding: 0 8px;
  height: 24px;
  line-height: 24px;
  font-size: 12px;
  color: #fff;
  border-radius: 12px;
  margin-right: 10px;
}

.info-tag .el-icon {
  margin-right: 3px;
  font-size: 14px;
}

.time {
  background-color: #20a0ff;
}

.duration {
  background-color: #13ce66;
}

.type {
  background-color: #f7ba2a;
}

:deep(.el-carousel__container) {
  position: relative;
  z-index: 1;
}

:deep(.el-carousel__item) {
  opacity: 0;
  transition: all 0.5s ease;
}

:deep(.el-carousel__item.is-active) {
  opacity: 1;
}

.carousel-wrapper {
  position: relative;
}

.carousel-controls {
  position: absolute;
  width: 100%;
  bottom: -40px;
  left: 0;
  transform: none;
  display: flex;
  justify-content: space-between;
  padding: 0 20px;
  z-index: 2;
}

.control-btn {
  width: 40px !important;
  height: 40px !important;
  min-height: auto !important;
  padding: 0 !important;
  background: rgba(31, 45, 61, 0.11) !important;
  border: none !important;
  color: #fff !important;
  opacity: 0;
  transition: opacity 0.3s;
}

.contest-card:hover .control-btn {
  opacity: 1;
}

.control-btn:hover {
  background: rgba(31, 45, 61, 0.23) !important;
}

:deep(.el-icon) {
  font-size: 20px;
  line-height: 1;
}
</style>
