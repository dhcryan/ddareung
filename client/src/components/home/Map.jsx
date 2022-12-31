import React, { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import parkData from "../../data/station.json";

const Map = () => {
    const position = [37.5, 127.0];

    return (
        <div>
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
                {parkData.features.map((park) => (
                    <Marker
                        key={park.properties.PARK_ID}
                        position={[
                            park.geometry.coordinates[1],
                            park.geometry.coordinates[0],
                        ]}
                    ></Marker>
                ))}
            </MapContainer>
        </div>
    );
};

export default Map;
