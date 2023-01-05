import React, { useState, useEffect } from "react";
import {
    MapContainer,
    TileLayer,
    Marker,
    Popup,
    Tooltip,
    Circle,
    CircleMarker,
} from "react-leaflet";
import sampleData from "../../data/data.json";
// import sampleData2 from "../../data/data2.json";

// import { L } from "leaflet";
// import { faBicycle } from "@fortawesome/free-solid-svg-icons";

// const fillBlueOptions = { fillColor: "blue" };
const purpleOptions = { color: "purple" };
const limeOptions = { color: "lime", fillColor: "rgb(100,100,100,0.8)" };
const redOptions = { color: "red" };

const departure = sampleData.departure.data[0];
const departure_group = sampleData.departure_group.data;
const destination = sampleData.destination.data[0];
const destination_group = sampleData.destination_group.data;

// const myIcon = new L.Icon({
//     iconUrl:
//         'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="' +
//         faBicycle.icon[4] +
//         '"/></svg>',
//     // iconRetinaUrl: "marker",
//     popupAnchor: [-0, -0],
//     iconSize: [32, 45],
// });

const MyMap = () => {
    const [position, setPosition] = useState([37.5, 127.0]);

    useEffect(() => {
        setPosition(departure["위도"], departure["경도"]);
    }, []);

    return (
        <div id="map">
            <MapContainer
                style={{ height: "100vh" }}
                center={position}
                zoom={13}
            >
                <TileLayer
                    attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
                    url="http://{s}.tile.osm.org/{z}/{x}/{y}.png"
                />

                <Marker
                    position={[departure["위도"], departure["경도"]]}
                    // icon={myCustomIcon}
                >
                    <Popup>
                        <span>
                            보관소(대여소)명: {departure["보관소(대여소)명"]}
                            <br />
                            대여소번호: {departure["대여소번호"]}
                            <br />
                            자전거 대수: {departure["자전거대수"]}
                        </span>
                    </Popup>
                    <Tooltip sticky>출발 - 대여소</Tooltip>
                </Marker>
                <Circle
                    center={[departure["위도"], departure["경도"]]}
                    pathOptions={limeOptions}
                    radius={5000}
                />
                <Marker position={[destination["위도"], destination["경도"]]}>
                    <Popup>
                        <span>
                            대여소 명: {destination["보관소(대여소)명"]}
                            <br />
                            대여소 번호: {destination["대여소번호"]}
                            <br />
                            자전거 대수: {destination["자전거대수"]}
                        </span>
                    </Popup>
                    <Tooltip sticky>도착 - 대여소</Tooltip>
                </Marker>
                <Circle
                    center={[destination["위도"], destination["경도"]]}
                    pathOptions={purpleOptions}
                    radius={5000}
                />
                {departure_group.map((station) => (
                    <CircleMarker
                        center={[station["위도"], station["경도"]]}
                        pathOptions={{
                            fillColor: `rgb(100, 100, 255, ${
                                station["자전거대수"] / 10
                            } )`,
                        }}
                        radius={80 * (station["자전거대수"] / 100)}
                    >
                        <Popup>
                            <span>
                                보관소(대여소)명: {station["보관소(대여소)명"]}
                                <br />
                                대여소번호: {station["대여소번호"]}
                                <br />
                                자전거 대수: {station["자전거대수"]}
                            </span>
                        </Popup>
                        <Tooltip sticky>{station["자전거대수"]}</Tooltip>
                    </CircleMarker>
                ))}
                {destination_group.map((station) => (
                    <CircleMarker
                        center={[station["위도"], station["경도"]]}
                        pathOptions={redOptions}
                        radius={80 * (station["자전거대수"] / 100)}
                    >
                        <Popup>
                            <span>
                                보관소(대여소)명: {station["보관소(대여소)명"]}
                                <br />
                                대여소번호: {station["대여소번호"]}
                                <br />
                                자전거 대수: {station["자전거대수"]}
                            </span>
                        </Popup>
                        <Tooltip sticky>{station["자전거대수"]}</Tooltip>
                    </CircleMarker>
                ))}
            </MapContainer>
        </div>
    );
};

export default MyMap;
