<template>
  <div class="rankings-container">
    <h2>比赛排名</h2>
    <div class="rankings-table">
      <el-table :data="rankings" style="width: 100%">
        <el-table-column prop="rank" label="排名" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="score" label="得分" width="100" />
        <el-table-column 
          v-for="problem in problems" 
          :key="problem.id"
          :label="problem.id"
          width="100"
        >
          <template #default="scope">
            <div class="problem-status" :class="getProblemStatusClass(scope.row.problemResults[problem.id])">
              {{ scope.row.problemResults[problem.id] }}
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ContestRankings',
  data() {
    return {
      problems: [
        { id: 'A' },
        { id: 'B' },
        { id: 'C' }
      ],
      rankings: [
        {
          rank: 1,
          username: 'user1',
          score: 300,
          problemResults: {
            'A': '+1',
            'B': '-2',
            'C': ''
          }
        },
        {
          rank: 2,
          username: 'user2',
          score: 200,
          problemResults: {
            'A': '+2',
            'B': '+1',
            'C': '-1'
          }
        },
        {
          rank: 3,
          username: 'user3',
          score: 100,
          problemResults: {
            'A': '+1',
            'B': '',
            'C': '-3'
          }
        }
      ]
    }
  },
  methods: {
    getProblemStatusClass(status) {
      if (!status) return ''
      if (status.startsWith('+')) return 'accepted'
      if (status.startsWith('-')) return 'wrong'
      return ''
    }
  }
}
</script>

<style lang="less" scoped>
.rankings-container {
  h2 {
    font-size: 20px;
    color: #333;
    margin: 0 0 20px 0;
  }

  .rankings-table {
    :deep(.el-table) {
      thead {
        th {
          background-color: #f5f7fa;
          color: #606266;
          font-weight: 500;
        }
      }

      .problem-status {
        text-align: center;

        &.accepted {
          color: #67c23a;
          font-weight: 500;
        }

        &.wrong {
          color: #f56c6c;
        }
      }
    }
  }
}
</style> 