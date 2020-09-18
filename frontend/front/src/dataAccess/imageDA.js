import axios from 'axios';

export function doSearchImages(top, bottom, left, right, startDate, endDate) {
    let url = "http://localhost:9997/api/searchImages/";

    console.log(url)

    var body = {
        "start_date": startDate,
        "end_date": endDate,
        "top": parseFloat(top),
        "bottom": parseFloat(bottom),
        "left": parseFloat(left),
        "right": parseFloat(right)
    };

    console.log(body);
    console.log("Antes de mandar request")
    return axios.post(url,body);
}

export function doCheckFiles(path){
    let url = "http://localhost:9997/api/checkFiles/?name=" + path;
    
    return axios.get(url)
}

export function doPredict(path){
    let url = "http://localhost:9997/api/predict/";
    console.log(url);

    var body = {
        filepath : path
    }
    console.log(body)

    return axios.post(url, body)
}