// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Zone } from '../Types/Zone';
import { ZoneCard } from './ZoneCard';

import '../Styles/Stack.css';

interface IHomepageCardsProps {
    zones: Zone[];
    onClick: (zone: Zone) => void;
    onNewClick: () => void;
}

export const HomepageCards = ({ zones, onClick, onNewClick }: IHomepageCardsProps) => {
    return (
        <div className='stack stack-horizontalgap'
            style={{width: 300, maxWidth: 300}}>
            <ZoneCard
                title={"Create a new zone"}
                subTitle={"Create a new DNS zone to get started."}
                addIcon={true}
                onClick={onNewClick}
            />

            {
                zones.slice(0, 3).map((zone: Zone) => {
                    return (
                        <ZoneCard
                            key={zone.fqdn}
                            title={zone.fqdn}
                            subTitle={`Analyze network traffic to ${zone.fqdn}`}
                            addIcon={false}
                            onClick={() => {
                                onClick(zone)
                            }} />)
                })
            }
        </div>
    )
}