<template>
<el-tab-pane>
  <template #label>
      <div style="display: flex; align-items: center;">
          <el-icon><Notebook /></el-icon>
          <span style="margin-left: 5px;">题解</span>
        </div>
  </template>

</el-tab-pane>
</template>

<script>
import { Notebook } from '@element-plus/icons-vue'
export default {
  name: 'Solution',
  components: {
    Notebook  // 注册Notebook图标组件
  },
  data() {
    return {
        
    }
  }
}
</script>

<style>


</style>