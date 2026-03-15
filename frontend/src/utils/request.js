import axios from "axios";
import { useStore } from '@/store/user'; // 引入Pinia用户store
import router from '@/router';  // 引入router
const baseURL = "http://43.138.0.117:8000"
//import user from '@/store/user'
const errorHandle = (status, info) => {
    switch (status) {
        case 400: console.log("语义有误"); break;
        case 401: console.log("服务器认证失败"); break;
        case 403: console.log("服务器拒绝访问"); break;
        case 404: console.log("地址错误"); break;
        case 500: console.log("服务器遇到意外"); break;
        case 502: console.log("服务器无响应"); break;
        default: console.log(info); break;
    }
}

// 1.创建网络请求对象
const instance = axios.create({
    baseURL: baseURL,
    timeout: 60000,  // 增加超时时间
    withCredentials: true  // 允许跨域携带认证信息
})

// 2.1.请求拦截的作用
instance.interceptors.request.use(
    config => {
        const userInfo = localStorage.getItem('user');
        if (userInfo) {
            try {
                const user = JSON.parse(userInfo);
                if (user.access_token) {
                    // 确保所有请求都带上token
                    config.headers = {
                        ...config.headers,
                        'Authorization': `Bearer ${user.access_token}`
                    };
                }
            } catch (e) {
                console.error('解析用户信息失败:', e);
            }
        }
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

let isRefreshing = false;
let requests = [];

// 拦截器----获取数据之前
instance.interceptors.response.use(
    response => {  // 拦截器成功函数
        return response.status == 200 ? Promise.resolve(response) : Promise.reject(response)
    },
    async error => {  // 拦截器失败函数
        const { response, config } = error;
        const store = useStore();
        if (response && response.status === 401) {
            // access_token 失效
            if (!isRefreshing) {
                isRefreshing = true;
                try {
                    const refresh_token = store.user.refresh_token || JSON.parse(localStorage.getItem('user'))?.refresh_token;
                    if (!refresh_token) {
                        store.logout();
                        localStorage.removeItem('user');
                        router.replace('/');  // 使用Vue Router进行重定向
                        return Promise.reject(error);
                    }
                    const res = await axios.post(baseURL + '/utils/token/refresh/', {
                        refresh_token: refresh_token
                    });
                    const new_access_token = res.data.access_token;
                    // 更新缓存
                    store.set_access_token(new_access_token);
                    // 更新localStorage
                    let user = JSON.parse(localStorage.getItem('user'));
                    user.access_token = new_access_token;
                    localStorage.setItem('user', JSON.stringify(user));
                    // 重新发起原请求
                    config.headers['Authorization'] = 'Bearer ' + new_access_token;
                    // 处理队列
                    requests.forEach(cb => cb(new_access_token));
                    requests = [];
                    return instance(config);
                } catch (e) {
                    store.logout();
                    window.location.href = '/learn';
                    ElMessage({
                        message: '登录已过期，请重新登录',
                        type: 'error',
                        duration: 2000
                    })
                    return Promise.reject(e);
                } finally {
                    isRefreshing = false;
                }
            } else {
                // 正在刷新，返回一个Promise，等刷新完再请求
                return new Promise(resolve => {
                    requests.push(token => {
                        config.headers['Authorization'] = 'Bearer ' + token;
                        resolve(instance(config));
                    });
                });
            }
        }
        return Promise.reject(error);
    }
)

//2.导出网络请求对象
export default instance;