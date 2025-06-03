import request from '@/utils/request'

export default {
    ProblemSubmit(password) {
        return request({
            url: '/competition/match/',
            method: 'post',
            data: {
                password: password
            }
        }).then(response => {
            return response;
        }).catch(error => {
            console.log(error)
        });
    },
    Description(id) {
        return request({
            url: `/competition/description/${id}/`,
            method: 'get'
        }).then(response => {
            return response;
        }).catch(error => {
            console.error('获取比赛描述失败:', error);
            return Promise.reject(error);
        });
    },
    Password(id, password){
        return request({
            url: '/competition/password/',
            method: 'post',
            data: {
                id: id,
                password: password
            }
        }).then(response => {
            return response;
        }).catch(error => {
            console.error('获取比赛密码失败:', error);
        });
    }
} 