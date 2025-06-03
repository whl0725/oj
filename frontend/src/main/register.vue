<template>
  <el-dialog
    v-model="dialogVisible"
    title="Welcome to PBOJ"
    width="400px"
    :before-close="handleClose"
    :show-close="true"
    :close-on-click-modal="false"
    class="register-dialog"
  >
    <el-form 
      :model="form"
      :rules="rules"
      ref="registerForm"
      label-position="top"
    >
      <el-form-item prop="username">
        <el-input
          v-model="form.username"
          placeholder="Username"
          :prefix-icon="User"
        />
      </el-form-item>

      <el-form-item prop="email">
        <el-input
          v-model="form.email"
          placeholder="Email Address"
          :prefix-icon="Message"
        />
      </el-form-item>

      <el-form-item prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="Password"
          :prefix-icon="Lock"
          show-password
        />
      </el-form-item>

      <el-form-item prop="passwordConfirm">
        <el-input
          v-model="form.passwordConfirm"
          type="password"
          placeholder="Password Again"
          :prefix-icon="Lock"
          show-password
        />
      </el-form-item>

      <el-form-item prop="captcha" class="captcha-item">
        <el-input
          v-model="form.captcha"
          placeholder="Captcha"
          :prefix-icon="Key"
          class="captcha-input"
        />
        <div class="captcha-image" @click="refreshCaptcha">
          <img :src="'data:image/jpeg;base64,' + captchaUrl"  alt="Base64 Image">
        </div>
      </el-form-item>

      <el-form-item>
        <el-button 
          type="primary" 
          class="register-button"
          :loading="loading"
          @click="submitForm"
        >
          Register
        </el-button>
      </el-form-item>

      <div class="login-link">
        Already registered? 
        <el-link type="primary" @click="toLogin">Login now!</el-link>
      </div>
    </el-form>
  </el-dialog>
</template>

<script>
import { ElMessage } from 'element-plus'
import register_api from '@/api/user/register';

export default {
  name: 'Register',
  data(){
    return {
      dialogVisible: false,
      form: {
        username: '',
        email: '',
        password: '',
        passwordConfirm: '',
        captcha: '',
        hashkey:'',
      },
      captchaUrl:"",
      userimg:"",
      rules: 
      {
        username:[]
      }
    };
  },

  methods: {
    open(){
      this.refreshCaptcha()
      this.dialogVisible = true
    },
    refreshCaptcha() {
        register_api.Captcha().then(res=>{
          this.captchaUrl=res.image_base64
          this.form.hashkey=res.hashkey
        }).catch(err=>{
            
        })
    },
    handleClose() {
      this.form.username = ''
      this.form.password = ''
      this.dialogVisible = false
    },
    submitForm(){
      register_api.submitregisterform(this.form).then(res=>{
        this.userimg=res.avatar
        this.dialogVisible = false

        this.$emit('register-success', this.userimg)
      }).catch(err=>{
            
      })
    },
    toLogin() {
      this.dialogVisible = false
      this.$emit('switch-to-login')
    }
  }



}
</script>

<style lang="less" scoped>
.register-dialog {
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

  :deep(.el-form-item__label) {
    padding: 0;
    line-height: 1;
    margin-bottom: 8px;
  }

  .captcha-item {
    display: flex;
    gap: 10px;

    .captcha-input {
      flex: 1;
    }

    .captcha-image {
      width: 120px;
      height: 40px;
      cursor: pointer;
      
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }
  }

  .register-button {
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

// 输入框样式优化
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

// 图标样式
:deep(.el-input__prefix) {
  color: #808695;
}
</style>