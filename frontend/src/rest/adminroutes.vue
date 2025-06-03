<template>
  <div class="admin-container">
    <el-container>
      <el-aside width="200px">
        <el-menu
          router
          :default-active="$route.path"
        >
          <el-menu-item index="/admin">
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/admin/problems">
            <span>题目管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header>
          <h2>后台管理系统</h2>
        </el-header>
        <el-main>
          <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>


export default {
    name: 'adminroutes'
}
</script>

<style scoped>
.admin-container {
  height: 100vh;
}

.el-header {
  background-color: #fff;
  line-height: 60px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}

.el-aside {
  background-color: #001529;
  color: white;
}

.el-menu {
  border-right: none;
  background-color: #001529;
}

.el-menu-item {
  color: white;
}

.el-menu-item:hover {
  background-color: #1890ff;
}

.el-menu-item.is-active {
  background-color: #1890ff;
  color: white;
}

/* 路由过渡动画 */
.route-enter-active {
  transition: opacity 0.25s ease 0.15s;
}
.route-leave-active {
  transition: opacity 0.25s ease;
}

.route-enter-from,
.route-leave-to {
  opacity: 0;
}

/* 可以添加另一种过渡效果 */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* .fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
} */
/* .fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active in <2.1.8 */ 
  /* opacity: 0; */

</style>
