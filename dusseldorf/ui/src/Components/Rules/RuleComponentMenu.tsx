// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Menu, MenuButton, MenuItem, MenuList, MenuPopover, MenuTrigger } from "@fluentui/react-components";
import { AddRegular } from "@fluentui/react-icons";
import { useEffect, useState } from "react";

import { RuleComponent } from "../../Types/RuleComponent";

const createDictionary = (isPredicate: boolean): Record<string, { label: string; onlyOne: boolean }> => {
    return {
        "dns.data": {
            label: "DNS Data",
            onlyOne: true
        },
        "dns.type": {
            label: "DNS Type",
            onlyOne: true
        },
        "http.body": {
            label: isPredicate ? "HTTP Body Regex" : "HTTP Body",
            onlyOne: true
        },
        "http.code": {
            label: "HTTP Code",
            onlyOne: true
        },
        "http.header": {
            label: "HTTP Header",
            onlyOne: false
        },
        "http.method": {
            label: "HTTP Method(s)",
            onlyOne: true
        },
        "http.passthru": {
            label: "HTTP Passthru",
            onlyOne: true
        },
        "http.path": {
            label: isPredicate ? "HTTP Path Regex" : "HTTP Path",
            onlyOne: true
        }
    };
};

const getItemList = (isHttp: boolean, isPredicate: boolean) => {
    if (isHttp && isPredicate) {
        return ["http.method", "http.path", "http.body", "http.header"];
    } else if (isHttp) {
        return ["http.code", "http.header", "http.body", "http.passthru"];
    } else if (isPredicate) {
        return ["dns.type"];
    } else {
        return ["dns.data"];
    }
};

interface RuleComponentMenuProps {
    isDisabled: boolean;
    isHttp: boolean;
    isPredicate: boolean;
    onCreate: (componentName: string) => void;
    ruleComponents: RuleComponent[];
}

export const RuleComponentMenu = ({
    isDisabled,
    isPredicate,
    isHttp,
    ruleComponents,
    onCreate
}: RuleComponentMenuProps) => {
    const [dictionary] = useState<Record<string, { label: string; onlyOne: boolean }>>(createDictionary(isPredicate));
    const [itemList, setItemList] = useState<string[]>(getItemList(isHttp, isPredicate));

    useEffect(() => {
        setItemList(getItemList(isHttp, isPredicate));
    }, [isHttp]);

    return (
        <Menu>
            <MenuTrigger disableButtonEnhancement>
                <MenuButton
                    style={{ width: 140 }}
                    icon={<AddRegular />}
                    disabled={
                        isDisabled ||
                        ( // dns results dropdown, disabled if we do not yet have a type
                            isHttp == false &&
                            isPredicate == false &&
                            ruleComponents.find((value) => value.actionname === "dns.type") == undefined)
                    }
                >
                    {isPredicate ? "Add Filter" : "Add Result"}
                </MenuButton>
            </MenuTrigger>

            <MenuPopover>
                <MenuList>
                    {itemList.map((item) => {
                        return (
                            <MenuItem
                                key={item}
                                icon={<AddRegular />}
                                disabled={
                                    dictionary[item]?.onlyOne
                                        ? ruleComponents.find(
                                              (value) => value.actionname === item && value.ispredicate === isPredicate
                                          ) !== undefined
                                        : false
                                }
                                onClick={() => {
                                    onCreate(item);
                                }}
                            >
                                {dictionary[item]?.label ?? item}
                            </MenuItem>
                        );
                    })}
                </MenuList>
            </MenuPopover>
        </Menu>
    );
};
