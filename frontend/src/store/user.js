import {defineStore} from 'pinia';

export const useStore = defineStore("user", {
    state: () => ({
        user:{
            username: "",
            avatar: "",
            isLoggedIn: false,
            email: "",
            id: "",
            refresh_token: "",
            access_token: "",
        }
    }),
    
    actions: {
        setid(id) {
            this.user.id = id
        },
        setUser(user) {
            this.user = user
        },
        setUsername(username) {
            this.user.username = username
        },
        setAvatar(avatar) {
            this.user.avatar = 'http://localhost:8000'+avatar
            console.log(this.user.avatar)
        },
        setToken(token) {
            this.user.token = token
            this.user.isLoggedIn = true
        },
        setEmail(email) {
            this.user.email = email
        },
        logout() {
            this.user.username = ''
            this.user.avatar = ''
            this.user.token = ''
            this.user.isLoggedIn = false
            this.user.email = ''
            this.user.refresh_token = ''
            this.user.access_token = ''
        },
        set_refresh_token(refresh_token){
            this.user.refresh_token = refresh_token
        },
        set_access_token(access_token){
            this.user.access_token = access_token
        }
    },
    
    persist: {
        enabled: true,
        strategies: [
            {
                key: 'user',
                storage: localStorage,
                paths: ['username', 'avatar', 'isLoggedIn','email']  // 指定要持久化的字段
            }
        ]
    }
});
