import request from '@/utils/request'
import axios from 'axios'

export default {
    getDialogue(data) {
        return request({
            url: '/ai/',
            method: 'post',
            data: data
        }).then(res => {
            return res.data
        }).catch(err => {
            return err
        })
    },
    //获取最近十条记录
    getHistory(){
        return request({
            url: '/ai/history/',
            method: 'get'
        }).then(res => {
            return res
        }).catch(err => {
            return err
        })
    },
    getDetails(chatId){
        return request({
            url: 'ai/details_process/',
            method: 'post',
            data: {
                chat_id: chatId
            }
        }).then(res => {
            //console.log(res)
            return res.data
        }).catch(err => {
            return err
        })
    },
    // 获取聊天历史
    getChatHistory(chatId) {
        return request({
            url: `/ai/chat/${chatId}/history/`,
            method: 'get'
        }).then(res => {
            return res
        }).catch(err => {
            return err
        })
    },

    async sendStreamMessage(content, userId, kb_id, chat_id) {
        console.log('Sending message with chat_id:', chat_id) // 添加日志
        const response = await fetch('http://localhost:8000/ai/', {
            method: 'POST',
            headers: {
                'Accept': 'text/event-stream',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: content,
                user_id: userId,
                kb_id: kb_id,
                chat_id: chat_id || '' // 确保传递chat_id
            })
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response;
    }
} 

