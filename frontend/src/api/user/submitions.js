import request from '@/utils/request'
export default {
    GetSubmitions(params){
        return request({
            url: '/user/submitions/',
            method: 'post',
            data: {
                id: params.id,
                page: params.page,
                page_size: params.page_size
            }
        }).then(response => {
            return response.data;
        }).catch(error => {
            return error;
        });
    }
} 

