import React, { useState, useEffect } from "react";
import { styled } from "@mui/material/styles";
import Slider from "@mui/material/Slider";

const PrettoSlider = styled(Slider)({
    color: "#52af77",
    height: 8,
    "& .MuiSlider-track": {
        border: "none",
    },
    "& .MuiSlider-thumb": {
        height: 24,
        width: 24,
        backgroundColor: "#fff",
        border: "2px solid currentColor",
        "&:focus, &:hover, &.Mui-active, &.Mui-focusVisible": {
            boxShadow: "inherit",
        },
        "&:before": {
            display: "none",
        },
    },
    "& .MuiSlider-valueLabel": {
        lineHeight: 1.2,
        fontSize: 12,
        background: "unset",
        padding: 0,
        width: 32,
        height: 32,
        borderRadius: "50% 50% 50% 0",
        backgroundColor: "#52af77",
        transformOrigin: "bottom left",
        transform: "translate(50%, -100%) rotate(-45deg) scale(0)",
        "&:before": { display: "none" },
        "&.MuiSlider-valueLabelOpen": {
            transform: "translate(50%, -100%) rotate(-45deg) scale(1)",
        },
        "& > *": {
            transform: "rotate(45deg)",
        },
    },
});

const marks = [
    {
        value: 0,
        label: "0h",
    },

    {
        value: 12,
        label: "12h",
    },
    {
        value: 24,
        label: "24h",
    },
];
function valuetext(value) {
    return `${value}h`;
}

const MySlider = (props) => {
    const [value, setValue] = React.useState(10);

    const sendTimelineValue = (value) => {
        props.getTimelineValue(value);
    };

    const handleChange = (event, newValue) => {
        setValue(newValue);
        sendTimelineValue(newValue);
    };

    // useEffect(() => {
    //     console.log(value);
    // }, [value]);

    return (
        <>
            <PrettoSlider
                aria-label="Timeline"
                defaultValue={10}
                getAriaValueText={valuetext}
                valueLabelDisplay="auto"
                step={1}
                marks={marks}
                min={0}
                max={24}
                style={{ width: "90%" }}
                onChange={handleChange}
            />
            <h2>{value}시</h2>
        </>
    );
};

export default MySlider;
