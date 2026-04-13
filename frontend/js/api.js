const BASE_URL = window.location.origin.includes('localhost') ? "http://localhost:8000/api" : "/api";

async function fetchAPI(endpoint, method="GET", body=null) {
    try {
        const options = {
            method,
            headers: { "Content-Type": "application/json" }
        };
        if (body) options.body = JSON.stringify(body);
        
        const response = await fetch(`${BASE_URL}${endpoint}`, options);
        return await response.json();
    } catch (e) {
        console.error("API Error:", e);
        return { error: e.message };
    }
}

const api = {
    saveProfile: (data) => fetchAPI("/student/profile", "POST", data),
    getProfile: (id) => fetchAPI(`/student/${id}`, "GET"),
    getUniversities: () => fetchAPI("/universities", "GET"),
    recommendUniversities: (data) => fetchAPI("/universities/recommend", "POST", data),
    calculateROI: (data) => fetchAPI("/roi/calculate", "POST", data),
    predictAdmission: (data) => fetchAPI("/admission/predict", "POST", data),
    chat: (data) => fetchAPI("/chat", "POST", data),
    getChatHistory: (id) => fetchAPI(`/chat/history/${id}`, "GET"),
    calcLoan: (data) => fetchAPI("/loan/calculate", "POST", data),
    applyLoan: (data) => fetchAPI("/loan/apply", "POST", data)
};
