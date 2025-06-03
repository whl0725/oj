import axios from "../../utils/request.js"
const base_URL = "http://localhost:8000"
const api = {
    // 成品详细地址
    submitloginform(from) {
        return axios.post("/user/login/", from).then(res => {
            //console.log("fdsa")
            return res
        }).catch(err => {
            console.log(err)
        })
    }
}

export default api;