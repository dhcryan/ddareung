import Axios from "axios";

Axios.defaults.withCredentials = true;

const options = {
    // baseURL: process.env.REACT_APP_API_URL,
    baseURL: "http://localhost:5000",
    headers: {
        "Content-Type": "application/json",
    },
    withCredentials: true,
};

const axios = Axios.create(options);

export const setAuthHeader = (key) => {
    axios.defaults.headers["Graduate.sid"] = key;
};

export default axios;
