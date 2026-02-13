import axios from "axios";

const BASE_URL = "http://localhost:8000"; // change if backend hosted

export const analyzeProduct = (comment) =>
  axios.post(`${BASE_URL}/analyze-product`, { comment });

export const getProductReviews = (id, sentiment) =>
  axios.get(`${BASE_URL}/product/${id}/reviews`, {
    params: { sentiment }
  });

export const getCompanyAnalytics = (company) =>
  axios.get(`${BASE_URL}/company/${company}/analytics`);
