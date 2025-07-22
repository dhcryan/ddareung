import React, { useState } from "react";
import RealTimeMap from "../components/home/RealTimeMap";
import MyMap from "../components/home/MyMap";
import { Box, Typography, Switch, FormControlLabel } from "@mui/material";
import { useServerHealth } from "../hooks/useBikeData";

function Home() {
    const [useRealTimeMode, setUseRealTimeMode] = useState(true);
    const { health, loading: healthLoading } = useServerHealth();

    // 서버 연결 상태에 따라 모드 결정
    const canUseRealTime = health && health.status === 'healthy';
    const shouldUseRealTime = useRealTimeMode && canUseRealTime;

    return (
        <div className="">
            {/* 제목 */}
            <Typography
                variant="h3"
                component="div"
                gutterBottom
                style={{
                    position: "fixed",
                    right: "60px",
                    top: "20px",
                    zIndex: 1000,
                    pointerEvents: "auto",
                    color: shouldUseRealTime ? "#007bff" : "#6c757d"
                }}
            >
                따릉이 프로젝트 {shouldUseRealTime ? "(실시간)" : "(데모)"}
            </Typography>

            {/* 모드 전환 스위치 */}
            <Box
                sx={{
                    position: "fixed",
                    right: "60px",
                    top: "80px",
                    zIndex: 1000,
                    pointerEvents: "auto",
                    background: "rgba(255,255,255,0.9)",
                    padding: "10px",
                    borderRadius: "5px",
                    boxShadow: "0 2px 10px rgba(0,0,0,0.1)"
                }}
            >
                <FormControlLabel
                    control={
                        <Switch
                            checked={useRealTimeMode}
                            onChange={(e) => setUseRealTimeMode(e.target.checked)}
                            disabled={!canUseRealTime}
                        />
                    }
                    label="실시간 모드"
                />
                
                {!healthLoading && (
                    <div style={{ fontSize: '12px', marginTop: '5px' }}>
                        서버: 
                        <span style={{ 
                            color: canUseRealTime ? '#198754' : '#dc3545',
                            fontWeight: 'bold',
                            marginLeft: '5px'
                        }}>
                            {canUseRealTime ? '연결됨' : '연결 안됨'}
                        </span>
                    </div>
                )}
            </Box>

            {/* 지도 컴포넌트 */}
            {shouldUseRealTime ? (
                <RealTimeMap />
            ) : (
                <MyMap />
            )}

            {/* 상태 정보 (실시간 모드가 아닐 때만) */}
            {!shouldUseRealTime && (
                <Box
                    sx={{
                        position: "fixed",
                        left: "20px",
                        bottom: "20px",
                        zIndex: 1000,
                        background: "rgba(255,255,255,0.9)",
                        padding: "15px",
                        borderRadius: "10px",
                        boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
                        maxWidth: "300px"
                    }}
                >
                    <Typography variant="h6" gutterBottom>
                        데모 모드
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        {!canUseRealTime ? 
                            "서버에 연결할 수 없어 샘플 데이터를 표시합니다." :
                            "실시간 모드를 활성화하여 최신 데이터를 확인하세요."
                        }
                    </Typography>
                </Box>
            )}
        </div>
    );
}

export default Home;
