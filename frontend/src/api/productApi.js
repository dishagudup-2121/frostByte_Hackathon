import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000"; // keep consistent

export const analyzeProduct = (text) =>
  axios.post(`${BASE_URL}/ai/analyze-product`, { text });


export const getProductReviews = (id, sentiment) =>
  axios.get(`${BASE_URL}/analytics/product/${id}/reviews`, {
    params: { sentiment }
  });

export const getCompanyAnalytics = (company) =>
  axios.get(`${BASE_URL}/analytics/company-summary/${company}`);

export const compareProducts = (model1, model2) =>
  axios.get("http://127.0.0.1:8000/analytics/compare", {
    params: { model1, model2 }
  });

export const getCompanySummary = (company) =>
  axios.get(`${BASE_URL}/analytics/company-summary/${company}`);

