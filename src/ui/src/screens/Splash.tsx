// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Button, Caption1, Link, Select, Text, Title3 } from "@fluentui/react-components";
import { LockClosedRegular } from "@fluentui/react-icons";
import { Logger } from "../Helpers/Logger";

import '../Styles/Stack.css';

interface ISplashProps {
    loginClick: () => void;
}

export const Splash = ({ loginClick }: ISplashProps) => {

    Logger.PageView("Splash")

    return (
        <div className='stack vstack-gap' style={{ padding: 100 }}>
            <Title3>Project Dusseldorf</Title3>

            <div className='stack'>
                <Text>
                    Please join the correct security group,
                    and select the respective endpoint.
                </Text>
                <Text>See{' '}
                    <Link href="//aka.ms/dusseldorf/docs" inline>aka.ms/dusseldorf/docs</Link>
                    {' '}for more information.</Text>
            </div>

            <Select
                value={"api.canary.dusseldorf.security.azure"}
                style={{ width: 300 }}
            >
                <option value="api.canary.dusseldorf.security.azure">Canary</option>
            </Select>

            <Text>
                Ensure that you allow pop-ups for authentication to work.
            </Text>

            <div>
                <Button
                    appearance="primary"
                    icon={<LockClosedRegular />}
                    onClick={loginClick}
                >
                    Sign in
                </Button>
            </div>

            <Caption1>
                <Link inline href="https://go.microsoft.com/fwlink/?LinkId=518021">
                    Privacy notification
                </Link>
            </Caption1>
        </div>
    );
}
