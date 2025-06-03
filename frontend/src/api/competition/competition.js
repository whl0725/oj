import request from '@/utils/request'
export default {
    GetContests(page = 1, pageSize = 10) {
        return request({
            url: '/competition/list/',
            method: 'get',
            params: {
                page: page,
                page_size: pageSize
            }
        }).then(response => {
            console.log(response.data)
            return response;
        }).catch(error => {
            return error;
        });
    }
} 

