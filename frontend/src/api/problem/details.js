import request from '@/utils/request'

export default {
    ProblemSubmit(problemId, code, language, username,competitionId) {
        return request({
            url: '/judger/submit/',
            method: 'post',
            data: {
                problem_id: problemId,
                code: code,
                language: language,
                user_id: username || localStorage.getItem('user_id'),
                competition_id: competitionId
            }
        }).then(response => {
            // 直接返回完整响应，保留所有判题数据
            return response;
        }).catch(error => {
            console.error('提交错误:', error);
            // 返回标准格式的错误对象
            return { data: { msg: '提交失败，请稍后重试' } };
        });
    },
 
    getProblemDetails(problemId) {
        return request({
            url: `/problem/details/?problem_id=${problemId}`,
            method: 'get'
        }).then(response => {
            return response.data;
        }).catch(error => {
            console.error('获取题目详情失败:', error);
            return { data: { msg: '获取题目详情失败' } };
        });
    },
    // 获取提交结果
    getSubmissionResult(submissionId) {
        return request({
            url: `/judger/result/`,
            method: 'post',
            data: {
              "submit_id": submissionId
            }
        }).then(response => {
            return response;
        }).catch(error => {
            console.error('获取判题结果失败:', error);
            return { 
                data: { 
                    code: 500,
                    msg: '获取判题结果失败', 
                    data: { status: '获取结果出错' } 
                } 
            };
        });
    },
    // 运行代码
    runCode(problemId, code, language, username,test_case) {
        return request({
            url: '/judger/run/',
            method: 'post',
            data: {
                problem_id: problemId,
                code: code,
                language: language,
                user_id: username || localStorage.getItem('user_id'),
                test: test_case
            }
        }).then(response => {
            // 直接返回完整响应，保留所有判题数据
            console.log(response)
            return response;
        }).catch(error => {
            console.error('提交错误:', error);
            // 返回标准格式的错误对象
            return { data: { msg: '提交失败，请稍后重试' } };
        });
    },
    getRunResult(runId){
        console.log(runId)
        return request({
            url: '/judger/run_result/',
            method: 'post',
            data: {
                run_id: runId
            }
        }).then(response => {
            return response;
        }).catch(error => {
            console.error('获取运行结果失败:', error);
            return { data: { msg: '获取运行结果失败' } };
        });
    }
} 