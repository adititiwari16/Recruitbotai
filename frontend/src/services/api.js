import axios from 'axios';

// API base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Handle API errors
const handleApiError = (error) => {
  console.error('API Error:', error);
  
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    const errorMsg = error.response.data.error || 'An error occurred';
    throw new Error(errorMsg);
  } else if (error.request) {
    // The request was made but no response was received
    throw new Error('No response from server. Please try again later.');
  } else {
    // Something happened in setting up the request
    throw new Error(error.message);
  }
};

// API functions
export const registerUser = async (userData) => {
  try {
    const response = await api.post('/users/register', userData);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const getUser = async (userId) => {
  try {
    const response = await api.get(`/users/${userId}`);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const updateUser = async (userId, userData) => {
  try {
    const response = await api.put(`/users/${userId}`, userData);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const startInterview = async (interviewData) => {
  try {
    const response = await api.post('/interview/start', interviewData);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const getInterview = async (interviewId) => {
  try {
    const response = await api.get(`/interview/${interviewId}`);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const getUserInterviews = async (userId) => {
  try {
    const response = await api.get(`/interview/user/${userId}`);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const submitAnswer = async (questionId, answer) => {
  try {
    const response = await api.post(`/interview/question/${questionId}/answer`, { answer });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const completeInterview = async (interviewId) => {
  try {
    const response = await api.post(`/interview/${interviewId}/complete`);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};
