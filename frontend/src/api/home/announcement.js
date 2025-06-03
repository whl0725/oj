import request from '@/utils/request'

export default {
    // 获取公告列表（只包含基本信息）
    getAnnouncements() {
        return request({
            url: '/home/announcements/list',
            method: 'get'
        })
    },
    // 获取单个公告详情
    getAnnouncementDetail(id) {
        return request({
            url: '/home/announcement/',
            method: 'get',
            params: { id: id }  // 添加 id 参数
        }).then(response => {
            console.log(response)
            return response.data
        }).catch(error => {
            throw error
        })
    }
} 