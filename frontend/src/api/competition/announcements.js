import request from '@/utils/request'
export default {
    GetAnnouncements(id) {
        return request({
            url: `/competition/announcements/${id}/`,
            method: 'get'
        }).then(response => {
            return response;
        }).catch(error => {
            return error;
        });
    }
} 

