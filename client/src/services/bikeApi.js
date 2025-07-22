import axios from 'axios';

// API 베이스 URL 설정
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const bikeApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 (로딩 상태 등)
bikeApi.interceptors.request.use(
  (config) => {
    console.log('API 요청:', config.baseURL + config.url);
    console.log('전체 설정:', config);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 (에러 처리)
bikeApi.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API 에러:', error.message);
    if (error.response) {
      console.error('응답 데이터:', error.response.data);
    }
    return Promise.reject(error);
  }
);

// API 함수들
export const bikeApiService = {
  // 서버 상태 확인
  checkHealth: async () => {
    try {
      const response = await bikeApi.get('/health');
      return response.data;
    } catch (error) {
      throw new Error('서버 연결 실패');
    }
  },

  // 실시간 대여소 전체 정보 조회
  getRealTimeStations: async () => {
    try {
      const response = await bikeApi.get('/api/stations/realtime');
      return response.data;
    } catch (error) {
      throw new Error('실시간 데이터 로드 실패');
    }
  },

  // 주변 대여소 추천
  getNearbyRecommendations: async (params) => {
    try {
      const response = await bikeApi.post('/api/recommendations/nearby', params);
      return response.data;
    } catch (error) {
      throw new Error('추천 데이터 로드 실패');
    }
  },

  // 경로 기반 추천
  getRouteRecommendations: async (params) => {
    try {
      const response = await bikeApi.post('/api/recommendations/route', params);
      return response.data;
    } catch (error) {
      throw new Error('경로 추천 실패');
    }
  },

  // 특정 대여소 예측
  getStationPrediction: async (stationId, hoursAhead = 2) => {
    try {
      const response = await bikeApi.get(`/api/stations/${stationId}/predict`, {
        params: { hours: hoursAhead }
      });
      return response.data;
    } catch (error) {
      throw new Error('예측 데이터 로드 실패');
    }
  },

  // 특정 대여소 변화 추이
  getStationTrend: async (stationId, hours = 24) => {
    try {
      const response = await bikeApi.get(`/api/stations/${stationId}/trend`, {
        params: { hours }
      });
      return response.data;
    } catch (error) {
      throw new Error('추이 데이터 로드 실패');
    }
  },

  // 수동 데이터 수집 트리거
  triggerDataCollection: async () => {
    try {
      const response = await bikeApi.post('/api/data/collect');
      return response.data;
    } catch (error) {
      throw new Error('데이터 수집 실패');
    }
  }
};

export default bikeApi;