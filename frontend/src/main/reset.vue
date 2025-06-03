<template>
    <el-dialog
      v-model="dialogVisible"
      title="重置密码"
      width="400px"
      :before-close="handleClose"
      :show-close="true"
      :close-on-click-modal="false"
      class="reset-dialog"
      style="color: #495060;"
    >
      <el-form 
        :model="form"
        :rules="rules"
        ref="resetForm"
        label-position="top"
      >
        <el-form-item prop="email">
          <el-input
            v-model="form.email"
            placeholder="Email Address"
            :prefix-icon="Message"
          />
        </el-form-item>
  
        <el-form-item prop="code" class="code-item">
          <el-input
            v-model="form.code"
            placeholder="验证码"
            :prefix-icon="Key"
            class="code-input"
          />
          <el-button 
            class="code-btn"
            :disabled="countdown > 0 || !form.email"
            @click="sendCode"
          >
            {{ countdown > 0 ? `${countdown}s后重试` : '获取验证码' }}
          </el-button>
        </el-form-item>
  
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="新密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
  
        <el-form-item prop="passwordConfirm">
          <el-input
            v-model="form.passwordConfirm"
            type="password"
            placeholder="确认新密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
  
        <el-form-item>
          <el-button 
            type="primary" 
            class="reset-button"
            :loading="loading"
            @click="submitForm"
          >
            重置密码
          </el-button>
        </el-form-item>
  
        <div class="login-link">
          已有账号？
          <el-link type="primary" @click="toLogin">立即登录</el-link>
        </div>
      </el-form>
    </el-dialog>
  </template>
  
<script>
import { ElMessage } from 'element-plus'
import reset_api from '@/api/user/reset'

export default {
  name: 'Reset',
  data(){
    return {
      dialogVisible: false,
      form: {
        email: '',
        code: '',
        password: '',
        passwordConfirm: ''
      },
      countdown: 0,
      timer: null,
      loading: false,
      rules: {
        email: [
          { required: true, message: '请输入邮箱',  },
          { type: 'email', message: '邮箱格式不正确',  }
        ],
        code: [
          { required: true, message: '请输入验证码',  }
        ],
        password: [
          { required: true, message: '请输入新密码', },
          { min: 6, max: 20, message: '长度在 6 到 20 个字符',  }
        ],
        passwordConfirm: [
          { required: true, message: '请再次输入新密码', },
          { validator: (rule, value, callback) => {
              if (value !== this.form.password) {
                callback(new Error('两次输入的密码不一致'))
              } else {
                callback()
              }
            }, trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    handleClose() {
      this.form.email = ''
      this.form.code = ''
      this.form.password = ''
      this.form.passwordConfirm = ''
      this.dialogVisible = false
    },
    open() {
      this.dialogVisible = true
    },
    toLogin() {
      this.dialogVisible = false
      this.$emit('switch-to-login')
    },
    sendCode() {
      if (!this.form.email) {
        ElMessage.error('请输入邮箱')
        return
      }
      this.countdown = 60
      this.timer = setInterval(() => {
        this.countdown--
        if (this.countdown <= 0) {
          clearInterval(this.timer)
        }
      }, 1000)

      reset_api.sendCode(this.form.email).then(res => {
        if (res.data) {
          ElMessage.success('验证码已发送，请查收邮箱')
        }
      }).catch(err => {
        ElMessage.error(err.response?.data?.message || '验证码发送失败')
      })
    },
    submitForm() {
      this.$refs.resetForm.validate(valid => {
        if (!valid) return
        if (this.form.password !== this.form.passwordConfirm) {
          ElMessage.error('两次输入的密码不一致')
          return
        }
        this.loading = true
        reset_api.resetPassword({
          email: this.form.email,
          code: this.form.code,
          password: this.form.password
        }).then(res => {
          if (res.data) {
            ElMessage.success('密码重置成功')
            this.dialogVisible = false
            this.$emit('reset-success')
          }
        }).catch(err => {
          ElMessage.error(err.response?.data?.message || '密码重置失败')
        }).finally(() => {
          this.loading = false
        })
      })
    }
  },
  beforeUnmount() {
    if (this.timer) clearInterval(this.timer)
  }
}
</script>
  
  <style lang="less" scoped>
  .reset-dialog {
    :deep(.el-dialog__header) {
      text-align: center;
      font-size: 18px;
      font-weight: 500;
      padding: 20px;
      margin: 0;
      border-bottom: 1px solid #e8eaec;
    }
    :deep(.el-dialog__body) {
      padding: 30px;
    }
    .code-item {
      display: flex;
      gap: 10px;
      .code-input {
        flex: 1;
      }
      .code-btn {
        width: 120px;
        height: 40px;
        font-size: 14px;
      }
    }
    .reset-button {
      width: 100%;
      height: 40px;
      font-size: 14px;
    }
    .login-link {
      text-align: center;
      margin-top: 16px;
      font-size: 14px;
      color: #606266;
    }
  }
  :deep(.el-input__wrapper) {
    background-color: #f8f8f9;
    box-shadow: none;
    border: 1px solid #dcdee2;
    &:hover, &:focus {
      border-color: #409eff;
    }
    .el-input__inner {
      height: 40px;
    }
  }
  :deep(.el-input__prefix) {
    color: #808695;
  }
  </style> 