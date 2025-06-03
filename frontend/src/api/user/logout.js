import axios from "../../utils/request.js"
const base_URL = "http://localhost:8000"
const logout_api = {
    // 成品详细地址
    submitlogoutform() {
        return axios.get("/utils/captcha/").then(res => {
            return res.data
        }).catch(err => {
            
        })
    },
}

export default logout_api;