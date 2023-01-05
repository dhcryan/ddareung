import React from "react";
import { HashRouter, Route, Routes } from "react-router-dom";

import Home from "./pages/Home";
import Subpage from "./pages/SubPage";

const Router = () => {
    return (
        <HashRouter>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/subpage" element={<Subpage />} />
            </Routes>
        </HashRouter>
    );
};

export default Router;
