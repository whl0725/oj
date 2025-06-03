<template>
    <el-container class="user-container">
        <el-aside width="250px" class="user-aside">
            <!-- 用户信息展示区 -->
            <div class="user-profile">
                <el-avatar :size="120" :src="store.user.avatar" @error="handleAvatarError">
                    <span>{{ user.username ? user.username.charAt(0).toUpperCase() : 'U' }}</span>
                </el-avatar>
                <p class="username">{{ user.username || 'whl' }}</p>
            </div>            
            <el-menu
                :default-active="$route.path"
                v-bind:router="true"
                class="el-menu-vertical"
                @select="handleSelect"
                background-color="#fff"
                text-color="#495060"
                active-text-color="#409eff">
                <div class="menu-wrapper">
                    <el-menu-item index="/user/user-home">
                        <span>Home</span>
                    </el-menu-item>
                    <el-menu-item index="/user/PersonalCenter">
                        <span>Profile</span>
                    </el-menu-item>
                    <el-menu-item index="/user/account">
                        <span>Account</span>
                    </el-menu-item>
                                        
                </div>
            </el-menu>
        </el-aside>
        <!-- 路由区 -->
        <el-main class="user-main">
            <transition name="route" mode="out-in">
                <router-view id="route"></router-view>
            </transition>
        </el-main>
    </el-container>
</template>

<script>
import { useStore } from '../store/user.js'
export default {
    name: 'user',
    setup() {
        const store = useStore()
        return {
            store
        }
    },
    data() {
        return {
            user: {
                userimg: this.store.user.avatar,
                username: this.store.user.username,
            }
        }
    },
    methods: {
        handleAvatarError() {
            this.user.userimg = ''; // 设置默认头像或清空
        },
        async getUserInfo() {
            try {
                // 这里添加获取用户信息的API调用
                // const response = await this.$api.getUserInfo();
                // this.user = response.data;
            } catch (error) {
                this.$message.error('获取用户信息失败');
            }
        }
    },
    created() {
        this.getUserInfo();
    }
};
</script>

<style scoped>
.user-container {
    border-radius: 5px;
    min-height: 400px;
    margin: 0 auto;
    width: 67%;
    margin-top: 20px;
    background-color: #f0f2f5;
    font-size: 14px;
}

.user-aside {
    background-color: #fff;
    border-radius: 4px;
    border-right: 1px solid #dddee1;
    /* margin-right: 20px; */
}

.user-profile {
    padding: 20px 0;
    text-align: center;
    /* border-bottom: 1px solid rgba(0, 0, 0, 0.1); */
}

.user-profile .username {
    margin-top: 30px;
    margin-left: 0;
    margin-right: 0;
    font-size: 20px;
}

.user-main {
    width: 100%;
    background-color: #fff;
    border-radius: 4px;
    padding: 0px;
    min-height: 500px;
}
/* 
.fade-enter-active, .fade-leave-active {
    transition: opacity .3s;
} */

/* .fade-enter, .fade-leave-to {
    opacity: 0;
} */

.el-menu-vertical {
    border-right: none;
    text-align: center;
}

.menu-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
}
.menu-wrapper :hover{
    background-color: #f3f3f3;
}

.el-menu-item {
    width: 80%;
    margin: 5px 0;
    justify-content:center;
    font-size: 14px;
}

.el-menu-item :hover {
    color: #409eff;
}

.el-menu-item i {
    margin-right: 5px;
}

.el-menu-item [class^="el-icon-"] {
    margin-left: 0;
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
</style>