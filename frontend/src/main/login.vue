<template>
  <el-dialog
    v-model="dialogVisible"
    width="400"
    :before-close="handleClose"
    style="color: #495060;"
  >
    <template #header>
      <div class="login-header">Welcome to PBOJ</div>
    </template>
    
    <el-form 
      :model="form" 
      :rules="rules"
      ref="loginForm"
      class="login-form"
    >
      <el-form-item prop="username">
        <el-input 
          v-model="form.username" 
          placeholder="用户名"
          :prefix-icon="User"
          class="custom-input"
        />
      </el-form-item>
      
      <el-form-item prop="password">
        <el-input 
          v-model="form.password" 
          type="password" 
          placeholder="密码"
          :prefix-icon="Lock"
          show-password
          class="custom-input"
        />
      </el-form-item>
    </el-form>

    <footer class="dialog-footer">
      <div class="">
        <el-button type="primary" class="login-button" @click="submitloginform">登录</el-button>
        <div class="links-container">
          <el-link type="primary" @click="toRegister">没有账号？立即注册</el-link>
          <el-link type="primary" @click="toReset">忘记密码？</el-link>
        </div>
      </div>
    </footer>
  </el-dialog>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Check, Close } from '@element-plus/icons-vue'
import api from '../api/user/login'
import { useStore } from '../store/user.js'
export default {
  name: 'Login',
  data() {
    return {
      dialogVisible: false,
      form: {
        username: '',
        password: ''
      },
      userimg: "",
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    //打开
    open() {
      this.dialogVisible = true
    },
    //关闭
    handleClose() {
      this.form.username = ''
      this.form.password = ''
      this.dialogVisible = false
    },
    //登录
    submitloginform(){
      if(this.form.username === '' || this.form.password === ''){
        ElMessage({
          message: '请输入用户名和密码',
          type: 'error',
          duration: 2000
        })
        return
      }
      api.submitloginform(this.form).then(res => {
        console.log(res.data)
        if (res.data.code == '200') {  // 登录成功
          // 使用pinia存储用户信息
          const store = useStore()
          store.setUsername(res.data.username)
          store.setid(res.data.id)
          store.setAvatar(res.data.avatar)
          store.set_refresh_token(res.data.refresh_token)
          store.set_access_token(res.data.access_token)
          store.setEmail(res.data.email)
          // 发送登录成功事件
          this.$emit('login-success', {
            username: res.data.username,
            avatar: res.data.avatar
          })
          this.handleClose()    
          ElMessage({
            message: '登录成功',
            type: 'success',
            duration: 2000
          })
        } else {  // 登录失败
          ElMessage({
            message: res.data.message,
            type: 'error',
            duration: 2000
          })
        }
      }).catch(err => {
        ElMessage({
          message: '登录失败，请重试',
          type: 'error',
          duration: 2000
        })
      })
    },
    //注册
    toRegister() {
      this.dialogVisible = false
      this.$emit('switch-to-register')
    },
    //重置密码
    toReset() {
      this.dialogVisible = false
      this.$emit('switch-to-reset')
    }
  }
}
</script>

<style>
.login-header {
  font-family: Helvetica Neue, Helvetica, PingFang SC, Hiragino Sans GB, Microsoft YaHei, Arial, sans-serif;
  color: #495060;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid #e9eaec;
  padding: 14px 16px;
  padding-left: 7px;
  line-height: 1;
}

.el-dialog__footer {
    box-sizing: border-box;
    /* padding-top: var(--el-dialog-padding-primary); */
    text-align: right;
    color: #495060;
}
.links-container {
  display: flex;
  justify-content: space-between;
  width: 100%;
  margin-bottom: 20px;
}
.login-form{
  font-size: 12px;
}
.login-button {
  width: 100%;
  margin-bottom: 10px;
  font-size: 12px;
}

</style>