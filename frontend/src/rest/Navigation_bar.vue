<template>
  <div id="header">
    <div class="logo"><span>PBOJ</span></div>
    <!-- 导航栏 -->
    <el-menu :default-active="$route.path" mode="horizontal" v-bind:router="true" :ellipsis="false" style="width: 100%; flex-wrap: wrap;">
      <el-menu-item index="/">
        <svg class="icon">
          <use xlink:href="#icon-home"></use>
        </svg> home
      </el-menu-item>
      <!-- <el-menu-item index="/learn">
        <svg class="icon">
          <use xlink:href="#icon-Learn"></use>
        </svg>
        Learn
      </el-menu-item> -->
      <el-menu-item index="/competition">
        <svg class="icon">
          <use xlink:href="#icon-bisai"></use>
        </svg>
        Competition
      </el-menu-item>
      <el-menu-item index="/problems">
        <svg class="icon">
          <use xlink:href="#icon-chengxu"></use>
        </svg>
        Problems
      </el-menu-item>
      <el-menu-item index="/ai">
        <svg class="icon">
          <use xlink:href="#icon-chengxu"></use>
        </svg>
        AI
      </el-menu-item>
      <el-sub-menu index="/about">
        <template #title>
          <svg class="icon">
            <use xlink:href="#icon-about-o"></use>
          </svg>
          About
        </template>
        <el-menu-item style="height: 40px;" index="/about/judger">Judger</el-menu-item>
        <el-menu-item style="height: 40px;" index="/about/faq">FAQ</el-menu-item>
      </el-sub-menu>
    </el-menu>
    <!-- 用户 -->
    <div class="user-section">
      <template v-if="!store.user.isLoggedIn">
        <el-button round id="login-button" @click="openLogin">Login</el-button>
        <el-button round id="register-button" @click="openRegister">Register</el-button>
      </template>
      <template v-else>
        <el-dropdown>
          <div class="user-avatar">
            <el-avatar 
              :size="40" 
              :src="store.user.avatar"
              @error="handleAvatarError"
            >
              <span>{{ store.user.username ? store.user.username.charAt(0).toUpperCase() : 'U' }}</span>
            </el-avatar>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="$router.push('/user/user-home')">个人中心</el-dropdown-item>
              <el-dropdown-item @click="$router.push('/user/submissions')">我的提交</el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
    </div>
    
    <!-- 登录和注册对话框 -->
    <Login ref="loginDialog" @login-success="handleLoginSuccess" @switch-to-register="openRegister" @switch-to-reset="openReset" />
    <Register ref="registerDialog" @switch-to-login="openLogin" />
    <reset ref="resetDialog" @switch-to-login="openLogin" />
  </div>
</template>

<script>
import Login from '../main/login.vue'
import Register from '../main/register.vue'
import logout_api from '../api/user/logout'
import reset from '@/main/reset.vue';
import '../assets/font_com/iconfont.js';
import '../assets/font/iconfont.js';
import { useStore } from '../store/user.js'
import { ElMessage } from 'element-plus'
export default {
  name: "Navigation_bar",
  components: {
    Login,
    Register,
    reset
  },
  setup() {
    const store = useStore()
    return {
      store
    }
  },
  data() {
    return {
      theNameOfTheProject: "Home",
      listOfQuestions: "Problems",
      user: {
        username: "",
        userimg: ""
      }
    };
  },
  methods: {
    openLogin() {
      this.$refs.loginDialog.open()
    },
    openRegister() {
      this.$refs.registerDialog.open()
    },
    openReset() {
      this.$refs.resetDialog.open()
    },
    handleLoginSuccess(userInfo) {
      this.store.user.isLoggedIn = true
    },
    handleAvatarError() {
      this.store.user.avatar = 'http://localhost:8000/static/default.jpg'
    },
    handleLogout() {
      const store = useStore()
      store.logout()
      
      logout_api.submitlogoutform().then(res => {
        this.$router.push('/')   // 退出后跳转到首页
        ElMessage({
          message: '退出成功',
          type: 'success',
          duration: 2000
        })
      })
    },
  },
  // mounted() {
  //   // 在组件挂载后添加一个全局样式元素
  //   const styleEl = document.createElement('style');
  //   styleEl.innerHTML = `
  //     .el-menu--popup {
  //       min-width: 80px !important;
  //       width: 100px !important;
  //     }
  //     .el-menu--popup .el-menu-item {
  //       min-width: 80px !important;
  //       width: 80px !important;
  //       padding: 0 5px !important;
  //       text-align: center;
  //     }
  //   `;
  //   document.head.appendChild(styleEl);
  // }
}
</script>

<style lang="less" scoped>
#header {
  min-width: 300px;
  position: relative;
  display: flex;
  align-items: center; /* 垂直居中对齐 */
  justify-content: space-between; /* 使内容分散对齐 */
  top: 0;
  left: 0;
  height: auto;
  width: 100%;
  z-index: 1000;
  background-color: #fff;
  box-shadow: 0 1px 5px 0 rgba(0, 0, 0, 0.1);
  color: #495060;
}

.logo {
  margin-left: 2%;
  margin-right: 1.5%;
  font-size: 20px;
  line-height: 60px;
}

.auth-buttons {
  display: flex; /* 使用 Flexbox 布局 */
  gap: 10px; /* 按钮之间的间距 */
}

.icon {
  width: 2em;
  height: 1.5em;
  vertical-align: -0.15em;
  fill: currentColor;
  overflow: hidden;
  margin-right: 10%;
}

.user-section {
  display: flex;
  align-items: center;
  margin-right: 20px;
}

/* 修改下拉菜单容器样式 */
:deep(.el-dropdown) {
  color: #495060;
  outline: none !important;   /* 强制移除轮廓 */
  border: none !important;    /* 强制移除边框 */
  box-shadow: none !important; /* 强制移除阴影 */
}

/* 修改头像容器样式 */
.user-avatar {
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover {
    opacity: 0.8;
  }
}

/* 修改头像组件样式 */
:deep(.el-avatar) {
  background-color: #fff;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  
  span {
    color: #495060;
    font-size: 16px;
    font-weight: bold;
  }
}

/* 移除下拉菜单的边框和阴影 */
:deep(.el-popper) {
  border: none !important;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,.1) !important;
}

:deep(.el-dropdown-menu) {
  border: none !important;
  box-shadow: none !important;
}

/* 移除所有可能的焦点样式 */
:deep(*:focus) {
  outline: none !important;
  border-color: transparent !important;
  box-shadow: none !important;
}

/* 移除所有可能的边框 */
:deep(*) {
  border-color: transparent !important;
}

/* 只针对About下拉菜单的样式 */
:deep(.el-menu--popup .el-menu-item) {
  min-width: 80px !important;
  width: 80px !important;
  padding: 0 5px !important;
  text-align: center;
}
:deep(.el-sub-menu[index="/about"]) {
  .el-sub-menu__title {
    &:hover {
      background-color: transparent;
    }
  }
  
  /* 只针对About下拉弹出菜单的样式 */
  & + .el-menu--popup {
    min-width: auto !important; /* 移除最小宽度限制 */
    width: 80px !important; /* 固定宽度 */
    padding: 0 !important; /* 移除内边距 */
  }
  
  /* 只针对About下拉菜单中的菜单项 */
  & + .el-menu--popup .el-menu-item {
    height: 40px;
    line-height: 40px;
    padding: 0 10px !important; /* 减小内边距 */
    width: 100% !important; /* 宽度等于父容器 */
    text-align: center; /* 文字居中 */
    font-size: 14px; /* 适当减小字体大小 */
    
    &:hover {
      background-color: #f5f7fa;
    }
  }
}
/* 移除之前可能影响所有菜单项的样式 */
:deep(.el-menu-item) {
  /* 不设置全局的min-width，避免影响其他菜单项 */
}

// 响应式样式
// @media screen and (max-width: 768px) {
//   .user-section {
//     margin-right: 10px;
//   }
  
//   .el-avatar {
//     width: 32px !important;
//     height: 32px !important;
//     font-size: 14px !important;
//   }
// }

// @media screen and (max-width: 480px) {
//   .logo {
//     font-size: 16px;
//   }
  
//   .user-section {
//     margin-right: 5px;
//   }
// }
</style>

<style lang="less">
/* 调整下拉菜单位置，确保在About正下方 */
.el-menu--popup{
  padding: 0 !important;
}
.el-menu--popup.el-menu--popup-bottom-start {
    min-width: 100px !important;
    box-shadow: none !important;
    margin-left: 0 !important;
    left: 20px !important; 
    transform: translateX(0) !important; /* 重置水平移动 */
    transform-origin: center top !important; /* 从顶部中心变换 */
    border-radius: 0 !important;
    //background-color: #f0f9ff !important;
    /* 使用定位来重新放置菜单 */
    position: absolute !important;
    top: 100% !important; /* 紧贴父元素底部 */
}

/* 确保下拉菜单的位置计算正确 */
// .el-menu--horizontal .el-sub-menu > .el-menu {
//     top: 65px !important; /* 固定顶部距离 */
//     left: auto !important; /* 自动左侧位置 */
// }

/* Popper相关样式 */
// .el-popper.is-pure {
//     box-shadow: none !important;
//     border: none !important;
// }

.el-popper[data-popper-placement="bottom"] {
    margin-top: 0 !important;
}

/* About子菜单相关样式 */
.el-sub-menu[index="/about"] .el-menu {
    top: 60px !important;
}

/* 确保无阴影和边框 */
.el-menu--popup {
    box-shadow: none !important;
    border: none !important;
}

/* 设置Judger菜单项的背景色 */
// .el-menu-item[index="/about/judger"] {
//     background-color: #f0f9ff !important;
// }
</style>