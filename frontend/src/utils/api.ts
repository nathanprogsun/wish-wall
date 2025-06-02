import axios from 'axios';
import Cookies from 'js-cookie';

// 创建axios实例
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加认证token
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理token过期
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token过期，尝试刷新
      const refreshToken = getRefreshToken();
      if (refreshToken) {
        try {
          const response = await refreshAccessToken();
          // 重试原请求
          error.config.headers.Authorization = `Bearer ${response.access_token}`;
          return api.request(error.config);
        } catch (refreshError) {
          // 刷新失败，清除所有token并跳转登录
          clearTokens();
          window.location.href = '/auth/login';
        }
      } else {
        // 没有refresh token，直接跳转登录
        clearTokens();
        window.location.href = '/auth/login';
      }
    }
    return Promise.reject(error);
  }
);

// Token管理
export const setTokens = (accessToken: string, refreshToken?: string) => {
  Cookies.set('access_token', accessToken, { expires: 1 }); // 1天
  if (refreshToken) {
    Cookies.set('refresh_token', refreshToken, { expires: 30 }); // 30天
  }
};

export const getAccessToken = () => {
  return Cookies.get('access_token');
};

export const getRefreshToken = () => {
  return Cookies.get('refresh_token');
};

export const clearTokens = () => {
  Cookies.remove('access_token');
  Cookies.remove('refresh_token');
};

export const isAuthenticated = () => {
  return !!getAccessToken();
};

// 刷新访问令牌
const refreshAccessToken = async () => {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    throw new Error('No refresh token');
  }

  const response = await axios.post('/api/auth/refresh', {}, {
    headers: {
      Authorization: `Bearer ${refreshToken}`,
    },
  });

  const { access_token } = response.data;
  setTokens(access_token);
  return response.data;
};

// 认证相关API
export const authAPI = {
  register: async (userData: {
    username: string;
    email: string;
    password: string;
  }) => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },

  login: async (loginData: {
    login: string;
    password: string;
    remember_me?: boolean;
  }) => {
    const response = await api.post('/api/auth/login', loginData);
    const { access_token, refresh_token } = response.data;
    setTokens(access_token, refresh_token);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  validateUsername: async (username: string) => {
    const response = await api.post('/api/auth/validate-username', { username });
    return response.data;
  },

  validateEmail: async (email: string) => {
    const response = await api.post('/api/auth/validate-email', { email });
    return response.data;
  },

  validatePassword: async (password: string) => {
    const response = await api.post('/api/auth/validate-password', { password });
    return response.data;
  },

  logout: () => {
    clearTokens();
  },
};

// 评论相关API
export const commentsAPI = {
  getComments: async () => {
    const response = await api.get('/api/comments');
    return response.data;
  },

  createComment: async (commentData: {
    content: string;
    parent_id?: number;
  }) => {
    const response = await api.post('/api/comments', commentData);
    return response.data;
  },

  getComment: async (commentId: number) => {
    const response = await api.get(`/api/comments/${commentId}`);
    return response.data;
  },

  getCommentReplies: async (commentId: number) => {
    const response = await api.get(`/api/comments/${commentId}/replies`);
    return response.data;
  },

  validateComment: async (content: string) => {
    const response = await api.post('/api/comments/validate', { content });
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/api/comments/stats');
    return response.data;
  },

  getUserComments: async (userId: number) => {
    const response = await api.get(`/api/comments/user/${userId}`);
    return response.data;
  },

  deleteComment: async (commentId: number) => {
    const response = await api.delete(`/api/comments/${commentId}`);
    return response.data;
  },
};

export default api; 