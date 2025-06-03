import request from '@/utils/request'
export default {
    GetSubmissions(id) {
        return request({
            url: '/competition/submissions/',
            method: 'post',
            data: {
                id:id
            }
        }).then(response => {
            return response.data;
        }).catch(error => {
            return error;
        });
    }
} 

