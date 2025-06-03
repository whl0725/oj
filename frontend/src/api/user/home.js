import request from '@/utils/request'
export default {
    GetUserHome(id){
        return request({
            url: '/user/info/',
            method: 'post',
            data: {id: id}
        }).then(response => {
            return response.data;
        }).catch(error => {
            return error;
        });
    }
} 

