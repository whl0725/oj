import request from '@/utils/request'
 
export default {
  // 获取首页公告
  getAnnouncements(page = 1, pageSize = 5) {
    return request({
      url: '/home',
      method: 'get',
      params: {
        page: page,
        page_size: pageSize
      }
    }).then(response => {
      console.log('API Response:', response)  // 添加调试日志
      return response
    }).catch(error => {
      console.error('API Error:', error)  // 添加错误日志
      throw error
    })
  },
} 