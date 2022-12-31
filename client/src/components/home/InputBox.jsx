import React, { useState } from "react";
import axios from "../../api/axios";

import {
    Box,
    Select,
    TextField,
    Typography,
    MenuItem,
    Button,
} from "@mui/material";

const InputBox = () => {
    const [fromStation, setFromStation] = React.useState("");
    const [toStation, setToStation] = React.useState("");
    const [timeline, setTimeline] = React.useState("");

    const handleFromStation = (e) => {
        setFromStation(e.target.value);
        console.log(fromStation);
    };

    const handleToStation = (e) => {
        setToStation(e.target.value);
        console.log(toStation);
    };

    const onClickSubmit = () => {
        const data = {
            fromStation: fromStation,
            toStation: toStation,
        };
        console.log(data);

        axios
            .post("/users", data)
            .then((res) => {
                console.log(res);
            })
            .catch((err) => {
                console.log(err);
            });
    };

    return (
        <Box
            sx={{
                width: "300px",
                border: "3px solid #415363",
                padding: "20px",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-around",
                background: "rgb(0, 160, 90, .9)",
                borderRadius: "20px",
                padding: "20px",
                width: "300px",
                height: "220px",
                boxSizing: "border-box",
            }}
        >
            <Box
                className="search_box"
                sx={{
                    marginBottom: "20px",
                    display: "flex",
                    flexDirection: "column",
                }}
            >
                <Box
                    sx={{
                        backgroundColor: "rgb(255,255,255, 0.9)",
                        borderRadius: "5px",
                        marginBottom: "10px",
                        padding: "0px",
                    }}
                >
                    <TextField
                        id="filled-basic"
                        label="출발지"
                        variant="outlined"
                        name="keyword1"
                        style={{ width: "100%", padding: "0px" }}
                        inputProps={{ style: { fontSize: 16 } }}
                        InputLabelProps={{ style: { fontSize: 16 } }}
                        onChange={handleFromStation}
                    />
                </Box>

                <Box
                    sx={{
                        backgroundColor: "rgb(255,255,255, 0.9)",
                        borderRadius: "5px",
                    }}
                >
                    <TextField
                        id="filled-basic"
                        label="도착지"
                        variant="outlined"
                        name="keyword2"
                        style={{ width: "100%" }}
                        inputProps={{ style: { fontSize: 16 } }}
                        InputLabelProps={{ style: { fontSize: 16 } }}
                        onChange={handleToStation}
                    />
                </Box>
            </Box>
            <Box
                className="btn_box"
                sx={{
                    display: "flex",
                    justifyContent: "flex-end",
                }}
            >
                <Button
                    variant="contained"
                    color="success"
                    type="submit"
                    onClick={onClickSubmit}
                >
                    확인
                </Button>
            </Box>
        </Box>
    );
};

export default InputBox;
