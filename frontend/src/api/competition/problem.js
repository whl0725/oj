import request from '@/utils/request'
export default {
    getProblemList(id) {
        return request({
            url: `/competition/problemslist/${id}/`,
            method: 'get'
        }).then(response => {
            return response;
        }).catch(error => {
            return error;
        });
    },
    getProblemDetails(competition_id, problem_id){
        console.log("进入")
        console.log("competition_id",competition_id, "problem_id",problem_id)
        return request({
            url: `/competition/problemslist/${competition_id}/problem/${problem_id}/`,
            method: 'get'
        }).then(response => {
            return response;
        }).catch(error => {
            return error;
        });
    }
} 

