import { useState, useEffect, useCallback } from 'react';
import { bikeApiService } from '../services/bikeApi';

// 실시간 대여소 데이터 훅
export const useRealTimeStations = (refreshInterval = 60000) => {
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchStations = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await bikeApiService.getRealTimeStations();
      
      if (response.success && response.data) {
        // API 응답 데이터를 지도 컴포넌트에서 사용할 형태로 변환
        const formattedStations = response.data.map(station => ({
          stationId: station.stationId,
          stationName: station.stationName,
          parkingBikeTotCnt: station.parkingBikeTotCnt,
          rackTotCnt: station.rackTotCnt,
          stationLatitude: parseFloat(station.stationLatitude),
          stationLongitude: parseFloat(station.stationLongitude),
          shared: station.shared,
          // 추가 계산 필드
          availabilityRate: station.parkingBikeTotCnt / station.rackTotCnt,
          status: getStationStatus(station.parkingBikeTotCnt, station.rackTotCnt)
        }));
        
        setStations(formattedStations);
        setLastUpdated(new Date());
      }
    } catch (err) {
      setError(err.message);
      console.error('실시간 데이터 로드 오류:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStations();
    
    // 자동 새로고침 설정
    const interval = setInterval(fetchStations, refreshInterval);
    
    return () => clearInterval(interval);
  }, [fetchStations, refreshInterval]);

  return {
    stations,
    loading,
    error,
    lastUpdated,
    refetch: fetchStations
  };
};

// 주변 대여소 추천 훅
export const useNearbyRecommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getRecommendations = useCallback(async (params) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await bikeApiService.getNearbyRecommendations(params);
      
      if (response.success) {
        setRecommendations(response.data);
      }
    } catch (err) {
      setError(err.message);
      console.error('추천 데이터 로드 오류:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    recommendations,
    loading,
    error,
    getRecommendations
  };
};

// 경로 추천 훅
export const useRouteRecommendations = () => {
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getRouteRecommendations = useCallback(async (params) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await bikeApiService.getRouteRecommendations(params);
      
      if (response.success) {
        setRouteData(response.data);
      }
    } catch (err) {
      setError(err.message);
      console.error('경로 추천 오류:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    routeData,
    loading,
    error,
    getRouteRecommendations
  };
};

// 서버 상태 확인 훅
export const useServerHealth = () => {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const healthData = await bikeApiService.checkHealth();
        setHealth(healthData);
      } catch (err) {
        console.error('서버 상태 확인 실패:', err);
        setHealth({ status: 'unhealthy', error: err.message });
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
    
    // 주기적으로 서버 상태 확인 (5분마다)
    const interval = setInterval(checkHealth, 300000);
    
    return () => clearInterval(interval);
  }, []);

  return { health, loading };
};

// 사용자 위치 훅
export const useUserLocation = () => {
  const [location, setLocation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!navigator.geolocation) {
      setError('위치 서비스를 지원하지 않습니다');
      setLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy
        });
        setLoading(false);
      },
      (err) => {
        setError('위치 정보를 가져올 수 없습니다');
        setLoading(false);
        // 기본값으로 서울 중심 설정
        setLocation({
          latitude: 37.5665,
          longitude: 126.9780,
          accuracy: null
        });
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // 5분 캐시
      }
    );
  }, []);

  return { location, loading, error };
};

// 헬퍼 함수
const getStationStatus = (parkingBikes, totalRacks) => {
  const rate = parkingBikes / totalRacks;
  
  if (parkingBikes === 0) return 'empty';
  if (rate <= 0.2) return 'low';
  if (rate >= 0.8) return 'high';
  return 'medium';
};