import request from '@/utils/request'
export default {
    sendCode(email) {
        return request({
            url: '/utils/send-reset-code/',
            method: 'post',
            data: { 
                "email": email
            }
        }).then(response => {
            console.log(response.data)
            return response;
        }).catch(error => {
            return error;
        });
    },
    resetPassword(data) {
        return request({
            url: '/utils/reset-password/',
            method: 'post',
            data: data
        }).then(response => {
            return response;
        }).catch(error => {
            return error;
        });
    }
} 

