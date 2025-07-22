import React, { useState, useEffect } from "react";
import {
    MapContainer,
    TileLayer,
    Marker,
    Popup,
    Tooltip,
    Circle,
    CircleMarker,
    useMap,
} from "react-leaflet";
import { Icon } from 'leaflet';
import { useRealTimeStations, useUserLocation, useNearbyRecommendations } from '../../hooks/useBikeData';

// 대여소 상태별 색상 설정
const getStationColor = (status) => {
    switch (status) {
        case 'empty': return '#dc3545'; // 빨강 - 자전거 없음
        case 'low': return '#fd7e14';   // 주황 - 부족
        case 'medium': return '#0d6efd'; // 파랑 - 보통
        case 'high': return '#198754';  // 초록 - 충분
        default: return '#6c757d';      // 회색 - 알 수 없음
    }
};

// 마커 아이콘 생성
const createStationIcon = (status, bikeCount) => {
    const color = getStationColor(status);
    
    return new Icon({
        iconUrl: `data:image/svg+xml;base64,${btoa(`
            <svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
                <circle cx="16" cy="16" r="12" fill="${color}" stroke="#fff" stroke-width="2"/>
                <text x="16" y="20" text-anchor="middle" fill="#fff" font-size="10" font-weight="bold">
                    ${bikeCount}
                </text>
            </svg>
        `)}`,
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, -16],
    });
};

// 사용자 위치 마커
const createUserIcon = () => {
    return new Icon({
        iconUrl: `data:image/svg+xml;base64,${btoa(`
            <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="8" fill="#007bff" stroke="#fff" stroke-width="2"/>
                <circle cx="12" cy="12" r="3" fill="#fff"/>
            </svg>
        `)}`,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
    });
};

// 지도 중심 이동 컴포넌트
const MapController = ({ center }) => {
    const map = useMap();
    
    useEffect(() => {
        if (center) {
            map.setView([center.latitude, center.longitude], 13);
        }
    }, [center, map]);
    
    return null;
};

const RealTimeMap = () => {
    const [selectedStation, setSelectedStation] = useState(null);
    const [showRecommendations, setShowRecommendations] = useState(false);
    
    // 데이터 훅 사용
    const { stations, loading, error, lastUpdated, refetch } = useRealTimeStations(30000); // 30초마다 업데이트
    const { location, loading: locationLoading } = useUserLocation();
    const { recommendations, getRecommendations, loading: recLoading } = useNearbyRecommendations();
    
    // 기본 지도 중심 (서울시청)
    const defaultCenter = { latitude: 37.5665, longitude: 126.9780 };
    const mapCenter = location || defaultCenter;

    // 주변 추천 요청
    const handleGetRecommendations = async () => {
        if (location) {
            setShowRecommendations(true);
            await getRecommendations({
                latitude: location.latitude,
                longitude: location.longitude,
                purpose: 'rental',
                top_n: 10
            });
        }
    };

    // 대여소 클릭 핸들러
    const handleStationClick = (station) => {
        setSelectedStation(station);
    };

    if (loading) {
        return (
            <div style={{ 
                height: '100vh', 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center',
                background: '#f8f9fa'
            }}>
                <div>
                    <div className="spinner-border text-primary" role="status">
                        <span className="visually-hidden">Loading...</span>
                    </div>
                    <p className="mt-3">실시간 따릉이 데이터 로딩 중...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ 
                height: '100vh', 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center',
                background: '#f8f9fa'
            }}>
                <div className="alert alert-danger text-center">
                    <h5>데이터 로드 오류</h5>
                    <p>{error}</p>
                    <button className="btn btn-primary" onClick={refetch}>
                        다시 시도
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div style={{ position: 'relative', height: '100vh' }}>
            {/* 컨트롤 패널 */}
            <div style={{
                position: 'absolute',
                top: '20px',
                left: '20px',
                zIndex: 1000,
                background: 'rgba(255,255,255,0.95)',
                padding: '15px',
                borderRadius: '10px',
                boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
                minWidth: '280px'
            }}>
                <h5 className="mb-3">실시간 따릉이 현황</h5>
                
                <div className="mb-3">
                    <small className="text-muted">
                        마지막 업데이트: {lastUpdated ? lastUpdated.toLocaleTimeString() : '없음'}
                    </small>
                    <br />
                    <small className="text-muted">
                        총 대여소: {stations.length}개
                    </small>
                </div>

                <div className="mb-3">
                    <button 
                        className="btn btn-outline-primary btn-sm me-2"
                        onClick={refetch}
                        disabled={loading}
                    >
                        새로고침
                    </button>
                    
                    <button 
                        className="btn btn-primary btn-sm"
                        onClick={handleGetRecommendations}
                        disabled={!location || recLoading}
                    >
                        {recLoading ? '로딩...' : '주변 추천'}
                    </button>
                </div>

                {/* 범례 */}
                <div className="mb-3">
                    <h6>상태 범례</h6>
                    <div style={{ fontSize: '12px' }}>
                        <div><span style={{color: '#dc3545'}}>●</span> 자전거 없음</div>
                        <div><span style={{color: '#fd7e14'}}>●</span> 부족 (20% 이하)</div>
                        <div><span style={{color: '#0d6efd'}}>●</span> 보통</div>
                        <div><span style={{color: '#198754'}}>●</span> 충분 (80% 이상)</div>
                    </div>
                </div>

                {/* 추천 결과 */}
                {showRecommendations && recommendations.length > 0 && (
                    <div>
                        <h6>주변 추천 대여소</h6>
                        <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                            {recommendations.slice(0, 5).map((rec, index) => (
                                <div key={rec.station_id} className="border-bottom py-1">
                                    <small>
                                        <strong>{index + 1}. {rec.station_name}</strong><br />
                                        자전거: {rec.current_bikes}대 | 거리: {rec.distance_km}km<br />
                                        점수: {(rec.recommendation_score * 100).toFixed(0)}점
                                    </small>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* 지도 */}
            <MapContainer
                style={{ height: "100vh", width: "100%" }}
                center={[mapCenter.latitude, mapCenter.longitude]}
                zoom={13}
            >
                <MapController center={mapCenter} />
                
                <TileLayer
                    attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {/* 사용자 위치 마커 */}
                {location && (
                    <Marker
                        position={[location.latitude, location.longitude]}
                        icon={createUserIcon()}
                    >
                        <Popup>
                            <div>
                                <strong>내 위치</strong><br />
                                정확도: {location.accuracy ? `${Math.round(location.accuracy)}m` : '알 수 없음'}
                            </div>
                        </Popup>
                    </Marker>
                )}

                {/* 대여소 마커들 */}
                {stations.map((station) => (
                    <Marker
                        key={station.stationId}
                        position={[station.stationLatitude, station.stationLongitude]}
                        icon={createStationIcon(station.status, station.parkingBikeTotCnt)}
                        eventHandlers={{
                            click: () => handleStationClick(station)
                        }}
                    >
                        <Popup maxWidth={300}>
                            <div>
                                <h6>{station.stationName}</h6>
                                <div className="mb-2">
                                    <strong>현재 자전거:</strong> {station.parkingBikeTotCnt}대<br />
                                    <strong>총 거치대:</strong> {station.rackTotCnt}대<br />
                                    <strong>이용률:</strong> {(station.availabilityRate * 100).toFixed(1)}%<br />
                                    <strong>상태:</strong> 
                                    <span style={{color: getStationColor(station.status), fontWeight: 'bold'}}>
                                        {' '}
                                        {station.status === 'empty' ? '자전거 없음' :
                                         station.status === 'low' ? '부족' :
                                         station.status === 'high' ? '충분' : '보통'}
                                    </span>
                                </div>
                                
                                {location && (
                                    <div className="mt-2">
                                        <small className="text-muted">
                                            내 위치에서 약 {
                                                Math.round(
                                                    Math.sqrt(
                                                        Math.pow(station.stationLatitude - location.latitude, 2) + 
                                                        Math.pow(station.stationLongitude - location.longitude, 2)
                                                    ) * 111 * 1000
                                                )
                                            }m
                                        </small>
                                    </div>
                                )}
                            </div>
                        </Popup>
                        
                        <Tooltip sticky>
                            {station.stationName}: {station.parkingBikeTotCnt}대
                        </Tooltip>
                    </Marker>
                ))}

                {/* 추천 대여소 하이라이트 */}
                {showRecommendations && recommendations.map((rec) => (
                    <Circle
                        key={`rec-${rec.station_id}`}
                        center={[rec.latitude, rec.longitude]}
                        radius={200}
                        pathOptions={{
                            color: '#007bff',
                            fillColor: '#007bff',
                            fillOpacity: 0.1
                        }}
                    />
                ))}
            </MapContainer>
        </div>
    );
};

export default RealTimeMap;