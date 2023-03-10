import { React, useEffect } from "react";
import axios from "axios";

import MyMap from "../components/home/MyMap";
import InputBox from "../components/home/InputBox";
// import MySlider from "../components/home/MySlider";

import { Box, Typography } from "@mui/material";

axios.defaults.withCredentials = true;

function Home() {
    // const [data, setData] = useState([{}]);

    useEffect(() => {
        axios
            .get("http://localhost:5000/users")
            .then((response) => {
                // setData(response.data);
                console.log(response.data);
            })
            .catch((err) => console.log(err));
    }, []);

    return (
        <div className="">
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
                }}
            >
                따릉이 프로젝트
            </Typography>
            <MyMap></MyMap>
            <Box
                sx={{
                    position: "fixed",
                    left: "60px",
                    top: "20px",
                    zIndex: 1000,
                    pointerEvents: "auto",
                }}
            >
                <InputBox />
                {/* <Box
                    sx={{
                        marginTop: "20px",
                        background: "rgb(255,255,255,0.9)",
                        width: "300px",
                        height: "100px",
                        paddingTop: "20px",
                    }}
                >
                    <MySlider />
                </Box> */}
            </Box>
        </div>
    );
}

export default Home;
