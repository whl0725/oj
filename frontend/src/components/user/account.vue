<template>
    <div class="account-container">
        <!-- 修改密码部分 -->
        <div class="change-section">
            <p class="section-title">Change Password</p>
            <el-form 
                :model="passwordForm" 
                :rules="passwordRules" 
                ref="passwordFormRef" 
                label-position="top"
            >
                <el-form-item 
                    label="Old Password" 
                    prop="oldPassword"
                    :rules="[{ required: true, message: 'Please input old password', trigger: 'blur' }]"
                >
                    <el-input 
                        v-model="passwordForm.oldPassword" 
                        type="password" 
                        placeholder="Enter your old password"
                    />
                </el-form-item>

                <el-form-item 
                    label="New Password" 
                    prop="newPassword"
                    :rules="[{ required: true, message: 'Please input new password', trigger: 'blur' }]"
                >
                    <el-input 
                        v-model="passwordForm.newPassword" 
                        type="password" 
                        placeholder="Enter your new password"
                    />
                </el-form-item>

                <el-form-item 
                    label="Confirm New Password" 
                    prop="confirmPassword"
                    :rules="[
                        { required: true, message: 'Please confirm your password', trigger: 'blur' },
                        { validator: validateConfirmPassword, trigger: 'blur' }
                    ]"
                >
                    <el-input 
                        v-model="passwordForm.confirmPassword" 
                        type="password" 
                        placeholder="Confirm your new password"
                    />
                </el-form-item>

                <el-form-item>
                    <el-button 
                        type="primary" 
                        @click="updatePassword" 
                        class="submit-button"
                    >Update Password</el-button>
                </el-form-item>
            </el-form>
        </div>

        <!-- 修改邮箱部分 -->
        <div class="change-section">
            <h2 class="section-title">Change Email</h2>
            <el-form 
                :model="emailForm" 
                :rules="emailRules" 
                ref="emailFormRef"
                label-position="top"
            >
                <el-form-item 
                    label="Current Password" 
                    prop="currentPassword"
                    :rules="[{ required: true, message: 'Please input current password', trigger: 'blur' }]"
                >
                    <el-input 
                        v-model="emailForm.currentPassword" 
                        type="password" 
                        placeholder="Enter your current password"
                    />
                </el-form-item>

                <el-form-item label="Old Email">
                    <el-input 
                        v-model="emailForm.oldEmail" 
                        disabled 
                        placeholder="Your current email"
                    />
                </el-form-item>

                <el-form-item 
                    label="New Email" 
                    prop="newEmail"
                    :rules="[
                        { required: true, message: 'Please input new email', trigger: 'blur' },
                        { type: 'email', message: 'Please input correct email address', trigger: 'blur' }
                    ]"
                >
                    <el-input 
                        v-model="emailForm.newEmail" 
                        placeholder="Enter your new email"
                    />
                </el-form-item>

                <el-button type="primary" @click="updateEmail">Change Email</el-button>
            </el-form>
        </div>
    </div>
</template>

<script>
import { useStore } from '../../store/user.js'
import { storeToRefs } from 'pinia'
import accountApi from '@/api/user/account.js'
import { ElMessage } from 'element-plus'

export default {
    name: 'account',
    setup() {
        const store = useStore()
        return {
            store
        }
    },
    data() {
        const validateConfirmPassword = (rule, value, callback) => {
            if (value !== this.passwordForm.newPassword) {
                callback(new Error('Two passwords do not match!'));
            } else {
                callback();
            }
        };
        return {
            passwordForm: {
                oldPassword: '',
                newPassword: '',
                confirmPassword: ''
            },
            emailForm: {
                currentPassword: '',
                oldEmail: '',  // 初始化为空字符串
                newEmail: ''
            },
            username: '',
            passwordRules: {
                oldPassword: [
                    { required: true, message: 'Please input old password', trigger: 'blur' }
                ],
                newPassword: [
                    { required: true, message: 'Please input new password', trigger: 'blur' }
                ],
                confirmPassword: [
                    { required: true, message: 'Please confirm password', trigger: 'blur' },
                    { validator: validateConfirmPassword, trigger: 'blur' }
                ]
            },
            emailRules: {
                currentPassword: [
                    { required: true, message: 'Please input current password', trigger: 'blur' }
                ],
                newEmail: [
                    { required: true, message: 'Please input new email', trigger: 'blur' },
                    { type: 'email', message: 'Please input correct email address', trigger: 'blur' }
                ]
            }
        }
    },
    methods: {
        updatePassword() {
            accountApi.UpdatePassword({
                username: this.store.user.username,
                old_password: this.passwordForm.oldPassword,
                new_password: this.passwordForm.newPassword
            }).then(res => {
                if(res.data.code == 200){
                    ElMessage.success('密码修改成功')
                    this.store.set_access_token(res.data.access_token)
                    let user = JSON.parse(localStorage.getItem('user'))
                    user.access_token = res.data.access_token
                    user.refresh_token=res.data.refresh_token
                    localStorage.setItem('user', JSON.stringify(user))
                    this.$refs.passwordFormRef.resetFields()
                } else {
                    ElMessage.error(res.data.message || '密码修改失败')
                    this.$refs.passwordFormRef.resetFields()
                }
            })
        },
        updateEmail() {
            accountApi.UpdateEmail({
                username: this.store.user.username,
                //old_email: this.emailForm.oldEmail,
                old_password: this.emailForm.currentPassword,
                new_email: this.emailForm.newEmail
            }).then(res => {
                if(res.data.code == 200){
                    ElMessage.success('邮箱修改成功')
                    this.store.set_access_token(res.data.access_token)
                    let user = JSON.parse(localStorage.getItem('user'))
                    user.access_token = res.data.access_token
                    user.refresh_token=res.data.refresh_token
                    user.email = this.emailForm.newEmail
                    localStorage.setItem('user', JSON.stringify(user))
                    this.$refs.emailFormRef.resetFields()
                } else {
                    ElMessage.error(res.data.message || '邮箱修改失败')
                    this.$refs.emailFormRef.resetFields()
                }
            })
        }
    }
}
</script>

<style scoped>
.account-container {
    display: flex;
    gap: 40px;
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.change-section {
    flex: 1;
    background: #fff;
    padding: 24px;
    border-radius: 8px;
}

.section-title {
    font-size: 21px;
    font-weight: 500;
    padding-top: 10px;
    padding-bottom: 20px;
    line-height: 30px;
}

:deep(.el-form-item__label) {
    font-weight: 500;
    color: #606266;
}

:deep(.el-input__inner) {
    height: 32px;
}

:deep(.el-form-item) {
    margin-bottom: 20px;
}

:deep(.el-button) {
    width: auto;
    height: 32px;
    font-size: 12px;
    padding: 0 20px;
    background-color: #2d8cf0;
}

:deep(.el-form-item:last-child) {
    margin-bottom: 0;
    display: flex;
    justify-content: flex-start;
}
</style>