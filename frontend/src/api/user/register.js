import axios from "../../utils/request.js"
const register_api = {
    submitregisterform(from) {
        return axios.post("/user/register/", from).then(res => {
            console.log(res)
            return res.data
        }).catch(err => {
            console.log(err)
        })
    },
    Captcha(){
        return axios.get("/utils/captcha/").then(res => {
            return res.data
        }).catch(err => {
            
        })
    }
}

export default register_api;