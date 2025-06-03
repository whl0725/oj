<template>
  <div class="page-container">
    <!-- 原有的问题列表内容 -->
    <router-view v-if="$route.name === 'problem-detail'"></router-view>
    <div v-else class="content-wrapper">
      <!-- 主要内容区域 -->
      <div class="main-content">
        <div class="problem-header">
          <div class="header-content">
            <h2>Problem List</h2>
            <div class="filter-area">
              <el-select 
                v-model="difficulty" 
                placeholder="Difficulty" 
                class="filter-select"
                clearable
              >
                <el-option label="All" value="" />
                <el-option label="Easy" value="easy" />
                <el-option label="Medium" value="medium" />
                <el-option label="Hard" value="hard" />
              </el-select>

              <el-input
                v-model="keyword"
                placeholder="Search problems..."
                :prefix-icon="Search"
                clearable
                @keyup.enter="handleSearch"
                class="search-input"
              />

              <el-button type="primary" class="reset-btn" @click="handleReset">
                Reset
              </el-button>
            </div>
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
          <el-table-column label="Level" width="248" >
            <template #default="{ row
             }">
              <span class="tag-item" style="background-color: #19be6b !important;" v-if="row.level == '1'">Easy</span>
              <span class="tag-item" style="width: 42px;" v-if="row.level == '2'">Med</span>
              <span class="tag-item" style="background-color: #f90 !important ;" v-if="row.level == '3'">Hard</span>
            </template>
          </el-table-column>
          <el-table-column prop="total" label="Total" width="245"  />
          <el-table-column label="AC Rate" width="245" >
            <template #default="{ row }">
              {{ row.acRate }}%
            </template>
          </el-table-column>
        </el-table>
        </div>
        <!-- 分页 -->
        <div class="pagination" style="margin-top: 20px;">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="totalProblems"
            :page-sizes="[10, 20, 50, 100]"
            layout="prev, pager, next,sizes"
            background
          />
        </div>
      </div>

      <!-- 标签栏 -->
      <div class="tags-panel">
        <div class="panel-header">
          <h3>Tags</h3>
        </div>
        <div class="tags-content">
          <el-tag
            v-for="tag in tags"
            :key="tag.name"
            :class="{ 'active': tag.selected }"
            
            @click="handleTagClick(tag)"
            effect="plain"
          >
            {{ tag.name }}
          </el-tag>
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
import api from '@/api/problem/problem'
import { ElMessage } from 'element-plus'

export default {
  name: 'ProblemList',
  setup() {
    // 响应式数据
    const tags = ref([])
    const problemlist = ref([])
    
    // 获取标签数据
    onBeforeMount(() => {
      api.getProblemtag()
        .then(res => {
          tags.value = res
        })
        .catch(err => {
          ElMessage.error('获取题目标签失败')
        })
    })
    
    // 获取题目列表数据
    onBeforeMount(() => {
      api.getProblemList()
        .then(response => {
          problemlist.value = response
        })
        .catch(err => {
          console.log(err)
          ElMessage.error('获取题目列表失败')
        })
    })
    
    return {
      tags, 
      problemlist
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
    this.fetchProblems();
  },

  methods: {
    fetchProblems() {
      api.getProblemList(this.currentPage, this.pageSize, this.difficulty, this.keyword)
        .then(response => {
          if (response.code === 200) {
            const data = response.data;
            // 更新题目列表
            this.problems = data.problems.map(item => ({
              id: item.id || item._id,
              title: item.title,
              level: item.difficulty || 'Medium',
              total: item.submission_number || 0,
              acRate: item['AC Rate'] || '0.00',
              solved: false
            }));
            
            // 更新总数
            this.totalProblems = data.total;
          } else {
            ElMessage.error(response.msg || '获取题目列表失败');
          }
        })
        .catch(err => {
          console.error(err);
          ElMessage.error('获取题目列表失败');
        });
    },

    handleSearch() {
      this.currentPage = 1;
      this.fetchProblems();
    },
    
    handleProblemClick(row) {
      const routeUrl = `/problem/${row.id}`
      window.open(routeUrl, '_blank')
    },

    handleReset() {
      this.difficulty = ''
      this.keyword = ''
      this.tagsEnabled = false
      this.currentPage = 1;
      this.fetchProblems();
    }
  },

  watch: {
    currentPage() {
      this.fetchProblems();
    },
    pageSize() {
      this.currentPage = 1;
      this.fetchProblems();
    },
    difficulty() {
      this.currentPage = 1;
      this.fetchProblems();
    }
  }
}
</script>