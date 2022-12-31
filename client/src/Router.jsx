import React from 'react';
import { BrowserRouter, Route, Routes, useLocation, Navigate } from 'react-router-dom';

import Home from './pages/Home';
import Subpage from './pages/SubPage';

const Router = () => {
    return (
        <BrowserRouter>
        <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/subpage" element={<Subpage />} />
        </Routes>
        </BrowserRouter>
    );
};

export default Router;
