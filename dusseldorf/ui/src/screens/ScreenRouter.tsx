// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Navigate, Route, Routes } from 'react-router-dom';

import { HomePage } from './HomePage';
import { TemplatesScreen }    from './TemplatesScreen';
import { AllZonesScreen } from './AllZonesScreen';
import { ZoneDetailsScreen } from './ZoneDetailsScreen';

/**
 * Renders/routes the "current" active screen.  All hashes are handled here
 * @returns JSX component which is our current screen
 */
export const ScreenRouter = () => {
    return (
        <Routes>
            <Route path="home" element={<HomePage />}/>
            <Route path="templates" element={<TemplatesScreen />}/>
            <Route path="templates/:template" element={<TemplatesScreen />}/>
            <Route path="zones" element={<AllZonesScreen />}/>
            <Route path="zones/:zone" element={<ZoneDetailsScreen showRules={false} />} />
            <Route path="zones/:zone/requests/:request?" element={<ZoneDetailsScreen showRules={false} />}/>
            <Route path="zones/:zone/rules/:rule?" element={<ZoneDetailsScreen showRules={true} />}/>
            <Route path=":anything?" element={<Navigate to="home" replace />}/>
        </Routes>
    )
}
