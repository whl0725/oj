<template>
  <div>
    <div class="content-wrapper">
      <!-- 主要内容区域 -->
      <div class="main-content">
        <div class="problem-header" style="padding: 15px;">
          <div class="header-content">
            <h2>Problem List</h2>
          </div>
        </div>
        <div class="problem-list">
        <!-- 题目列表 -->
        <el-table
          :data="problems"
          style="width: 100%"
          @row-click="handleProblemClick"
        >
          <el-table-column label="" width="80" align="center">
            <template #default="{ row }">
              <span style="color: #67c23a;" align="left" v-if="row.solved">✓</span>
            </template>

          </el-table-column>
          <el-table-column prop="id" label="#" width="70" >
            <template #default="{ row }">
              <span>{{ row.id }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="Title" width="" align="left" />
          <!-- <el-table-column label="Level" width="248" >
            <template #default="{ row
             }">
              <span class="tag-item" v-if="row.level == '1'">Easy</span>
              <span class="tag-item" v-if="row.level == '2'">Med</span>
              <span class="tag-item" v-if="row.level == '3'">Hard</span>
            </template>
          </el-table-column> -->
          <el-table-column prop="total" label="Total" width="450"  />
          <el-table-column label="AC Rate" width="245" >
            <template #default="{ row }">
              {{ row.acRate }}%
            </template>
          </el-table-column>
        </el-table>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="less" scoped>

@import '@/assets/less/problem.less';
</style>

<script>
import { ref, onBeforeMount } from 'vue'
import { Search } from '@element-plus/icons-vue'
import api from '@/api/competition/problem'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'

export default {
  name: 'ProblemList',
  setup() {
    const route = useRoute()
    // 响应式数据
    const problemlist = ref([])
    
    // 获取题目列表数据
    onBeforeMount(() => {
      api.getProblemList(route.params.id)
        .then(response => {
          console.log(response.data)
          problemlist.value = response.data.data
        })
        .catch(err => {
          console.log(err)
          ElMessage.error('获取题目列表失败')
        })
    })
    
    // 处理题目点击
    const handleProblemClick = (row) => {
      const routeUrl = `/competition/problemslist/${route.params.id}/problem/${row.id}`
      window.open(routeUrl, '_blank')
    }

    return {
      problemlist,
      handleProblemClick
    }
  },
  
  data() {
    return {
      keyword: '',
      difficulty: '',
      currentPage: 1,
      pageSize: 10,
      totalProblems: 150,
      tagsEnabled: false,
      problems: [] // 初始化为空数组，后面会用后端数据填充
    }
  },
  
  mounted() {
    // 在组件挂载后，使用 setup 中获取的 problemlist 数据更新 problems 数组
    this.$watch('problemlist', (newVal) => {
      if (newVal && newVal.length > 0) {
        // 将后端数据映射到符合当前展示格式的数据结构
        this.problems = newVal.map(item => ({
          id: item.id || item._id,
          title: item.title,
          level: item.difficulty || 'Medium', // 根据后端实际字段调整
          total: item.submission_number || 0,
          acRate: item['AC Rate'] || '0.00',
          solved: false // 这个可能需要通过用户信息判断
        }));
        
        // 更新题目总数
        this.totalProblems = this.problems.length;
      }
    }, { immediate: true });
  },

  methods: {
    handleSearch() {
      // 实现搜索逻辑
    },
    
    handleTagClick(tag) {
      tag.selected = !tag.selected
      this.handleSearch()
    },
    
    handleReset() {
      this.difficulty = ''
      this.keyword = ''
      this.tagsEnabled = false
      this.handleSearch()
    }
  }
}
</script>