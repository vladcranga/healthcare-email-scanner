import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If unauthorized and not already retried, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post(`${BASE_URL}/api/auth/login/refresh/`, { refresh: refreshToken });
        
        const { access } = response.data;
        localStorage.setItem('token', access);
        
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Logout user if refresh fails
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        // Dispatch logout action or redirect
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export const authService = {
  login: (email: string, password: string) => 
    api.post('/api/auth/login/', { username: email, password }),
  
  register: (userData: { email: string, password: string, password2: string, username: string, first_name: string, profile: { role: string } }) => 
    api.post('/api/auth/register/', userData),
  
  refreshToken: () => 
    api.post('/api/auth/login/refresh/'),
  
  logout: async () => {
    try {
      // Call backend logout endpoint to invalidate the token
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        await api.post('/api/auth/logout/', { refresh: refreshToken });
      }
    } finally {
      // Clear local storage regardless of backend response
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('userEmail');
    }
  }
};

export const emailService = {
  getEmails: (params: { 
    status?: string;
    search?: string;
    page?: number;
  }) => {
    return api.get<{
      count: number;
      next: string | null;
      previous: string | null;
      results: any[];
    }>('/api/emails/', { params });
  },
  
  getEmail: (id: number) => {
    return api.get(`/api/emails/${id}/`);
  },
  
  getSuspiciousEmails: () => 
    api.get('/api/emails/?status=suspicious'),
  
  analyzeEmail: (emailContent: string) => 
    api.post('/api/emails/analyze_email/', { content: emailContent }),
  
  quarantineEmail: (emailId: number) => 
    api.post(`/api/emails/${emailId}/quarantine/`),
  
  getSuspiciousSummary: () => 
    api.get('/api/emails/suspicious_summary/'),
  
  getPublicStats: () => 
    api.get('/api/emails/public_stats/'),
  
  exportEmails(format: 'json') {
    return api.get(`/api/export/`, {
      responseType: 'blob',
      headers: {
        'Accept': 'application/json',
      },
    });
  },

  importEmails(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/import/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  deleteEmail: (emailId: number) => 
    api.delete(`/api/emails/${emailId}/`),
};

export default api;
