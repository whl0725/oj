import axios from "../../utils/request.js"

const personal_api = {
    updateUserInfo(userInfo, user_id) {
        return axios.put("/user/update/", {
            user_id: user_id,
            real_name: userInfo.real_name,
            school: userInfo.school,
            major: userInfo.major,
            language: userInfo.language,
            mood: userInfo.mood,
            blog: userInfo.blog,
            github: userInfo.github,
        }).then(res => {
            console.log(res.data)
            return res.data
        }).catch(err => {
            console.log(err)
            throw err
        })
    },
    // 添加上传头像的方法
    uploadAvatar(file,id) {
        const formData = new FormData()
        formData.append('avatar', file)
        formData.append('id', id)
        return axios.post("/user/avatar/", formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        }).then(res => {
            return res.data
        }).catch(err => {
            console.log(err)
            throw err
        })
    }
}

export default personal_api;