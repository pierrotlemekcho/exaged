import axios from "axios";
import Cookies from "js-cookie";

const getCSRFToken = () => {
  return Cookies.get("csrftoken");
};

const axiosInstance = axios.create({
  headers: {
    "Content-Type": "application/json",
    accept: "application/json",
  },
});

axiosInstance.interceptors.request.use((request) => {
  request.headers["X-CSRFToken"] = getCSRFToken();
  return request;
});

export default axiosInstance;
