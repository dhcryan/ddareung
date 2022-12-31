import React, { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import sampleData from "../../data/data.json";

const Map = () => {
    const position = [37.5, 127.0];
    console.log(sampleData);
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
                <Marker position={position}>
                    <Popup>
                        <span>
                            A pretty CSS3 popup. <br /> Easily customizable.
                        </span>
                    </Popup>
                </Marker>

                {sampleData.map((data) => {
                    return (
                        <Marker
                            key={data.stationName}
                            position={[
                                data.stationLatitude,
                                data.stationLongitude,
                            ]}
                        >
                            <Popup>
                                <span>
                                    {data.stationName} <br /> {data.stationId}
                                </span>
                            </Popup>
                        </Marker>
                    );
                })}
            </MapContainer>
        </div>
    );
};

export default Map;
