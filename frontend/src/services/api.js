// src/services/api.js

import axios from 'axios';

// 1. SET THE BASE URL
// This is your FastAPI backend
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000'
});

// 2. CREATE A "REQUEST INTERCEPTOR"
// This function runs *before* any request is sent.
api.interceptors.request.use(config => {
  // Get the token from local storage
  const token = localStorage.getItem('token');
  
  // If a token exists, add it to the 'Authorization' header
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;

}, error => {
  return Promise.reject(error);
});

export default api;