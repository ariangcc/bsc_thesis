import axios from 'axios';

export function doLogin(username,password){

    let url = process.env.BACK_API + 'api/login'; 

    var body ={
        "username" : username,
        "password" : password
    }
    
    return axios.post(url,body);
}