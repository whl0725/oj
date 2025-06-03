<template>
<div>
    <div class="content-wrapper">
      <!-- 主要内容区域 -->
      <div class="main-content">
        <div class="problem-header" style="padding: 15px;">
          <div class="header-content">
            <h2>Submissions</h2>
          </div>
        </div>
        <div class="problem-list">
        <!-- 题目列表 -->
        <el-table
          :data="submissions"
          style="width: 100%"
          @row-click="handleProblemClick"
        >
          <el-table-column label="" width="20" align="center">

          </el-table-column>
          <el-table-column prop="submit_time" label="Time" width="150" align="center">
            <template #default="{ row }">
              <span>{{formatDate(row.submit_time)}}</span>
            </template>
          </el-table-column>
          <el-table-column prop="" label="" width="" align="center" />
          <el-table-column prop="problem" label="Problem" width="" align="left" />
          <el-table-column prop="language" label="Language" width="" align="left" />
          <!-- <el-table-column label="Level" width="248" >
            <template #default="{ row
             }">
              <span class="tag-item" v-if="row.level == '1'">Easy</span>
              <span class="tag-item" v-if="row.level == '2'">Med</span>
              <span class="tag-item" v-if="row.level == '3'">Hard</span>
            </template>
          </el-table-column> -->
          <el-table-column prop="status" label="Status" width="245"  />
          <el-table-column label="User" width="245" >
            <template #default="{ row }">
              {{ row.user["username"] }}
            </template>
          </el-table-column>
        </el-table>
        </div>
      </div>
    </div>
    
  </div>
</template>

<script>
import submissions_api from '@/api/competition/submissions'
import { formatDate } from '@/utils/format.js'
export default {
  name: 'ContestSubmissions',
  data() {
    return {
      competitionId: this.$route.params.id,
      status: '',
      searchAuthor: '',
      submissions: [],
      total: 0,
      currentPage: 1,
      pageSize: 10
    }
  },
  computed: {
    filteredSubmissions() {
      let data = this.submissions
      if (this.status) {
        data = data.filter(item => item.status === this.status)
      }
      if (this.searchAuthor) {
        data = data.filter(item => item.author && item.author.includes(this.searchAuthor))
      }
      this.total = data.length
      // 分页
      const start = (this.currentPage - 1) * this.pageSize
      return data.slice(start, start + this.pageSize)
    }
  },
  methods: {
		formatDate,
    handlePageChange(page) {
      this.currentPage = page
    }
  },
  created() {
    console.log(this.competitionId)
    submissions_api.GetSubmissions(this.competitionId).then(res => {
      console.log(res)

      this.submissions = res
    })
  }
}
</script>

<style lang="less" scoped>
@import '@/assets/less/problem.less';
</style> 