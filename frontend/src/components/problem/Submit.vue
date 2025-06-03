<template>
    <el-tab-pane>
        <template #label>
            <div style="display: flex; align-items: center;">
                <el-icon><List /></el-icon>
                <span style="margin-left: 5px;">提交记录</span>
            </div>
        </template>
    </el-tab-pane>
</template>


<script>
import { List } from '@element-plus/icons-vue'
export default {
    name: "Submit",
    components: {
        List
    }
    
}
</script>

<style scoped>
:deep(.el-tabs__item) {
    padding: 0 5px;
  }

</style>