import request from '@/utils/request'
export default {
    UpdatePassword(data) {
        return request({
            url: '/user/update_password/',
            method: 'post',
            data: {
                username: data.username,
                old_password: data.old_password,
                new_password: data.new_password
            }
        })
    },
    UpdateEmail(data) {
        return request({
            url: '/user/update_email/',
            method: 'post',
            data: {
                username: data.username,
                old_password: data.old_password,
                new_email: data.new_email
            }
        }).then(response => {
            return response;
        }).catch(error => {
            return error;
        });
    },
} 

