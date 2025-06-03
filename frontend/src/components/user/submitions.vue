<template>
    <div class="content">
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
              :data="problems"
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
              <el-table-column prop="id" label="ID" width="110" align="center"/>
              <el-table-column prop="problem" label="Problem" width="" align="center" />
              <el-table-column prop="language" label="Language" width="" align="center" />
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
        <div class="pagination" style="height: 100px; margin-top: 20px;">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50, 100]"
            layout="prev, pager, next,sizes"
            background
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </template>
    
<script>
import submitions_api from '@/api/user/submitions'
import { useStore } from '../../store/user.js'
import { formatDate } from '@/utils/format.js'
export default {
      name: 'UserSubmissions',
      setup(){
        const store = useStore()
        return {
          store
        }
      },
      data() {
        return {
          status: '',
          searchAuthor: '',
          problems: [],
          total: 0,
          currentPage: 1,
          pageSize: 10
        }
      },
      computed: {
        filteredSubmissions() {
          let data = this.problems
          if (this.status) {
            data = data.filter(item => item.status === this.status)
          }
          if (this.searchAuthor) {
            data = data.filter(item => item.author && item.author.includes(this.searchAuthor))
          }
          this.total = data.length
          const start = (this.currentPage - 1) * this.pageSize
          return data.slice(start, start + this.pageSize)
        }
      },
      methods: {
        formatDate,
        handleSizeChange(val) {
          this.pageSize = val
          this.getSubmissions()
        },
        handleCurrentChange(val) {
          this.currentPage = val
          this.getSubmissions()
        },
        getSubmissions() {
          submitions_api.GetSubmitions({
            id: this.store.user.id,
            page: this.currentPage,
            page_size: this.pageSize
          }).then(res => {
            this.problems = res.data.submissions
            this.total = res.data.total
          })
        }
      },
      created() {
        this.getSubmissions()
      }
    }
</script>
    
<style lang="less" scoped>
@import '@/assets/less/problem.less';

.content{
    width: 90%;
    height: 100%;
    //background-color: #f5f7fa;
    margin: 30px auto;
}
.pagination {
    padding-right: 0%;
    //padding: 20px;
    display: flex;
    justify-content: flex-end;
    //margin-right: 20px;
  
    :deep(.el-pagination) {
      .el-pagination__sizes {
        .el-input__inner {
          height: 32px;
          line-height: 32px;
        }
      }
  
      .btn-prev,
      .btn-next,
      .el-pager li {
        min-width: 32px;
        height: 32px;
        line-height: 32px;
        font-size: 12px;
        background: #ffffff;
  
        &.is-active {
          background-color: #2d8cf0 !important;  // 设置激活状态的背景色
          color: #fff;
        }
      }
  
      .el-pagination__jump .el-input__inner {
        height: 32px;
        line-height: 32px;
      }
  
      // 设置鼠标悬停时的背景色
      .el-pager li:hover {
        color: #2d8cf0;
      }
    }
  }
</style> 