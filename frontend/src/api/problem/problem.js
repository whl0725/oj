import request from '@/utils/request'

export default {
   getProblemtag() {
    return request({
        url: '/problem/tag/',
        method: 'get'
    }).then(response => {
        return response.data
    }).catch(error => {
        console.error('获取题目标签失败:', error);
        return { data: { msg: '获取题目标签失败' } };
    })
   },
   getProblemList(page = 1, pageSize = 10, difficulty = '', keyword = '') {
       return request({
           url: '/problem/list',
           method: 'get',
           params: {
               page,
               page_size: pageSize,
               difficulty,
               keyword
           }
       }).then(response => {
           return response.data
       }) 
   },
}