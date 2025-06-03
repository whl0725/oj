<template>
        <div class="box-card">
            <div class="title">
                <span>Avatar Setting</span>
            </div>
            <div class="avatar-upload">
              <el-upload
                    class="upload-demo"
                    drag
                    :action="null"  
                    :auto-upload="false"
                    :multiple="false"
                    :limit="1"
                    :on-change="handleAvatarChange"
                    :before-upload="beforeAvatarUpload"
                    :on-exceed="handleExceed"
                  >
                    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                    <div class="el-upload__text">
                        Drop file here or <em>click to upload</em>
                    </div>
              </el-upload>
              <!-- 头像预览 -->
              <div v-if="imageUrl" style="margin-top: 10px; text-align: center;">
                  <img :src="imageUrl" alt="头像预览" style="max-width: 120px; max-height: 120px; border-radius: 50%;" />
              </div>
            </div>
            <div class="profile-title">
                <span>Profile Setting</span>
            </div>
            
            <div class="form-container">
                <!-- 左侧表单 -->
                <el-form :model="userInfo" :rules="rules" ref="userFormLeft" label-position="top" class="left-form">
                    <el-form-item label="Real Name" prop="realName">
                        <el-input v-model="userInfo.realName" placeholder=""></el-input>
                    </el-form-item>
                    <el-form-item label="School" prop="school">
                        <el-input v-model="userInfo.school" placeholder=""></el-input>
                    </el-form-item>
                    <el-form-item label="Major" prop="major">
                        <el-input v-model="userInfo.major" placeholder=""></el-input>
                    </el-form-item>
                    <el-form-item label="Language">
                        <el-select v-model="userInfo.language" placeholder="Please select your language">
                            <el-option label="简体中文" value="zh-CN"></el-option>
                            <el-option label="English" value="en"></el-option>
                        </el-select>
                    </el-form-item>
                </el-form>

                <!-- 右侧表单 -->
                <el-form :model="userInfo" :rules="rules" ref="userFormRight" label-position="top" class="right-form">
                    <el-form-item label="Mood">
                        <el-input type="textarea" v-model="userInfo.mood" placeholder=""></el-input>
                    </el-form-item>
                    <el-form-item label="blog">
                        <el-input v-model="userInfo.blog" placeholder="Please enter your blog address"></el-input>
                    </el-form-item>
                    <el-form-item label="Github">
                        <el-input v-model="userInfo.github" placeholder="Please enter your Github address"></el-input>
                    </el-form-item>
                </el-form>
            </div>

            <!-- 按钮显示 -->
            <div class="button-container">
                <el-button type="primary" @click="saveUserInfo(['userFormLeft', 'userFormRight'])">保存修改</el-button>
                <el-button @click="resetForm(['userFormLeft', 'userFormRight'])">重置</el-button>
            </div>
        </div>
</template>

<script>
import personal_api from "../../api/user/Personal.js"
import { ElMessage } from 'element-plus'
import { useStore } from '../../store/user.js'
export default {
    name: 'PersonalCenter',
    setup() {
        const store = useStore()
        return {
            store
        }
    },
    data() {
        return {
            userInfo: {
                realName: '',
                school: '',
                major: '',
                language: '',
                mood: '',
                blog: '',
                github: '',
                avatar: null  // 添加avatar字段
            },
            imageUrl: '', // 新增头像预览字段
            rules: {
                realName: [
                    { required: false, message: '请输入真实姓名', trigger: 'blur' },
                    { min:1, max: 5, message: '长度在 1 到 5 个字符', trigger: 'blur' }
                ],
                school: [
                    { required: false, message: '请输入学校名称', trigger: 'blur' }
                ],
                major: [
                    { required: false, message: '请输入专业名称', trigger: 'blur' }
                ],
                blog: [
                    { required: false, message: '请输入博客地址', trigger: 'blur' },
                    { type: 'url', message: '请输入正确的博客地址', trigger: 'blur' }
                ],
                github: [
                    { required: false, message: '请输入Github地址', trigger: 'blur' },
                    { type: 'url', message: '请输入正确的Github地址', trigger: 'blur' }
                ],
                email: [
                    { required: true, message: '请输入邮箱',  },
                    { type: 'email', message: '邮箱格式不正确',  }
                ],
            }
        };
    },
    methods: {
        handleExceed(){
            this.$message.warning('只能上传一个头像文件！');
        },
        handleAvatarChange(file) {
            // 保存文件对象
            this.userInfo.avatar = file.raw
            // 可以在这里预览图片
            if (file.raw) {
                this.imageUrl = URL.createObjectURL(file.raw)
            }
        },
        beforeAvatarUpload(file) {
            const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
            const isLt2M = file.size / 1024 / 1024 < 2

            if (!isJPG) {
                this.$message.error('Avatar must be JPG/PNG format!')
                return false
            }
            if (!isLt2M) {
                this.$message.error('Avatar size can not exceed 2MB!')
                return false
            }
            return true
        },
        saveUserInfo(formNames) {
            // 检查是否所有字段都为空
            const { realName, school, major, language, mood, blog, github, avatar } = this.userInfo;
            if (
                !realName &&
                !school &&
                !major &&
                !language &&
                !mood &&
                !blog &&
                !github &&
                !avatar
            ) {
                this.$message.warning('请至少填写一个信息再保存！');
                return;
            }
            try {
                // 如果有新的头像文件，先上传头像
                if (this.userInfo.avatar) {
                    personal_api.uploadAvatar(this.userInfo.avatar, this.store.user.id).then(res => {
                        // 假设后端返回头像URL
                        const newAvatarUrl = 'http://localhost:8000' + res.url
                        this.userInfo.avatarUrl = newAvatarUrl
                        // 更新pinia全局头像
                        this.store.setAvatar(res.url)
                        // 更新localStorage
                        let user = JSON.parse(localStorage.getItem('user'))
                        user.avatar = newAvatarUrl
                        localStorage.setItem('user', JSON.stringify(user))
                    })
                }
                personal_api.updateUserInfo(this.userInfo,this.store.user.id).then(res => {
                    if (res.code == "0") {
                        this.$message.success('保存成功')
                    } else {
                        this.$message.error(res.message || '保存失败')
                    }
                })
            } catch (error) {
                this.$message.error('保存失败：' + error.message)
            }
        },
        resetForm(formNames) {
            formNames.forEach(formName => {
                this.$refs[formName].resetFields();
            });
        },
        async getUserInfo() {
            try {
                // const response = await this.$api.getUserInfo();
                // this.userInfo = response.data;
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
.title{
    color: #495060;
    font-size: 21px;
    font-weight: 500;
    padding-top: 10px;
    padding-bottom: 10px;
    line-height: 30px;
    margin-top: 10px;
}
.box-card{
  margin: 10px 40px;
} 
.avatar-upload{
  margin-top: 20px;
  width: 500px;
}
.upload-tip {
    color: #666;
    font-size: 14px;
    margin-top: 10px;
}
.profile-title{
    color: #495060;
    font-size: 21px;
    font-weight: 500;
    padding-top: 10px;
    padding-bottom: 10px;
    line-height: 30px;
}
.el-form {
    margin-top: 20px;
    --el-upload-dragger-padding-horizontal: 0px;
}

/* 添加以下样式来减小内边距 */
:deep(.el-upload-dragger) {
    padding: 10px !important;
    height: 120px !important;
}

:deep(.el-icon--upload) {
    margin: 0 !important;
}

:deep(.el-upload__text) {
    margin: 5px 0 0 0 !important;
    line-height: 1.2;
}

/* 如果需要调整拖拽区域的整体高度 */
:deep(.el-upload) {
    width: 100%;
}

:deep(.el-upload-dragger) {
    width: 100%;
}

.form-container {
    display: flex;
    justify-content: space-between;
    gap: 0px;
}

.left-form, .right-form {
    flex: 1;
    max-width: 48%;
}

/* 添加以下样式来调整表单项的布局 */
:deep(.el-form-item__label) {
    color: #606266;
    font-size: 14px;
    line-height: 1.5;
}

:deep(.el-form-item) {
    margin-bottom: 24px;
}

:deep(.el-input__inner) {
    height: 36px;
    line-height: 36px;
}

:deep(.el-textarea__inner) {
    min-height: 36px;
}

:deep(.el-select) {
    width: 100%;
}

.button-container {
    display: flex;
    /* justify-content: center; */
    margin-top: 10px; 
    gap: 20px;
}
</style>