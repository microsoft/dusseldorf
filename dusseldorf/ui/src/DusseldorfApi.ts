// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { PERMISSION } from "./Components/ZoneDetails/AuthDialog";
import DusseldorfConfig from "./DusseldorfConfig";
import { CacheHelper } from "./Helpers/CacheHelper";
import { DssldrfRequest } from "./Types/DssldrfRequest";
import { Logger } from "./Helpers/Logger";
import { Rule } from "./Types/Rule";
import { NewRuleComponent, RuleComponent } from "./Types/RuleComponent";
import { User } from "./Types/User";
import { Zone } from "./Types/Zone";

/**
 * helper class to talk to Dusseldorf API
 */
export class DusseldorfAPI {
    static makeRequest = (url: string, method: string, httpBody: any): Promise<Response> => {
        const hdrs = new Headers({
            "Content-Type": "application/json",
            Accept: "application/json",
            Authorization: "Bearer " + CacheHelper.GetToken()
        });

        const full_url:string = `${DusseldorfConfig.api_host}/${url}`.replace(/([^:]\/)\/+/g, "$1");;

        const req = new Request(full_url, {
            method: method,
            headers: hdrs,
            body: httpBody ? JSON.stringify(httpBody) : null
        });

        return fetch(req);
    };

    static get = (url: string): Promise<Response> => {
        return this.makeRequest(url, "GET", null);
    };

    static delete = (url: string): Promise<Response> => {
        return this.makeRequest(url, "DELETE", null);
    };

    static put = (url: string, httpBody: any): Promise<Response> => {
        return this.makeRequest(url, "PUT", httpBody);
    };

    static post = (url: string, httpBody: any): Promise<Response> => {
        return this.makeRequest(url, "POST", httpBody);
    };

    // ------------------ API calls ------------------

    // read only property endpoint
    static ENDPOINT = DusseldorfConfig.api_host;

    /**
     * GET /zones Get all the zones the user has any permission on.
     */
    static GetZones = async (): Promise<Zone[]> => {
        Logger.Info(`API.GetZones()`);

        return this.get("zones")
            .then((resp) => {
                if (resp.ok) {
                    return resp.json();
                } else {
                    throw Error(`API.GetZones() failed`);
                }
            })
            .then((data) => {
                return data as Zone[];
            });
    };

    /**
     * GET /zones/myzone GET /zones/myzone Get a specific zone by its {pattern}.
     *
     * Then return true or false.
     */
    static DoesZoneExist = async (fqdn: string): Promise<boolean> => {
        Logger.Info(`API.DoesZoneExist(${fqdn})`);

        if (!fqdn) {
            throw Error(`API.DoesZoneExist(${fqdn}) bad arguments`);
        }

        return this.get(`zones/${fqdn}`).then((resp) => {
            if (resp.ok || resp.status == 403) {
                return true;
            } else if (resp.status == 404) {
                return false;
            } else {
                throw Error(`API.DoesZoneExist(${fqdn}) failed`);
            }
        });
    };

    /**
     * Delete a zone. You must have owner permission to do so.
     */
    static DeleteZone = async (fqdn: string): Promise<void> => {
        Logger.Info(`DeleteZone(${fqdn})`);

        if (!fqdn) {
            throw Error(`API.DeleteZone(${fqdn}) bad arguments`);
        }

        return this.delete(`zones/${fqdn}`).then((resp) => {
            if (!resp.ok) {
                throw Error(`API.DeleteZone(${fqdn}) failed`);
            }
        });
    };

    /**
     * GET /requests/{zone} Get the requests for this zone, if authorized.
     */
    static GetRequests = async (
        zone: string,
        num: number,
        skip: number,
        protocols: string
    ): Promise<DssldrfRequest[]> => {
        Logger.Info(`API.GetRequests(${zone}, ${num}, ${skip}, ${protocols})`);

        if (!zone) {
            throw Error(`API.GetRequests(${zone}, ${num}, ${skip}, ${protocols}) bad arguments`);
        }

        const MAX_REQS = 1024;
        if (num > MAX_REQS) {
            Logger.Info(`Reducing # of GetRequests(${zone}) from ${num} to ${MAX_REQS}`);
            num = MAX_REQS;
        }

        return this.get(`requests/${zone}?limit=${num}&skip=${skip}&protocols=${protocols}`)
            .then((resp) => {
                if (resp.ok) {
                    return resp.json();
                } else {
                    throw Error(`API.GetRequests(${zone}, ${num}, ${skip}, ${protocols}) failed`);
                }
            })
            .then((data) => {
                return data as DssldrfRequest[];
            });
    };

    /**
     * Get all the rules for a zone if the user has access to it. Silently fails (returns an empty list) if the user doesn't have read access or the zone doesn't exist.
     */
    static GetRules = async (zone: string): Promise<Rule[]> => {
        Logger.Info(`API.GetRules(${zone})`);

        if (!zone) {
            throw Error(`API.GetRules(${zone}) bad arguments`);
        }

        return this.get(`rules/${zone}`)
            .then((resp) => {
                if (resp.ok) {
                    return resp.json();
                } else {
                    throw Error(`API.GetRules(${zone}) failed`);
                }
            })
            .then((data) => {
                return data as Rule[];
            });
    };

    /**
     * Get all the rules for a zone if the user has access to it. Silently fails (returns an empty list) if the user doesn't have read access or the zone doesn't exist.
     */
    static GetRuleDetails = async (zone: string, id: string): Promise<Rule> => {
        Logger.Info(`API.GetRuleDetails(${zone}, ${id})`);

        if (!zone || !id) {
            throw Error(`API.GetRuleDetails(${zone}, ${id}) bad arguments`);
        }

        return this.get(`rules/${zone}/${id}`)
            .then((resp) => {
                if (resp.ok) {
                    return resp.json();
                } else {
                    throw Error(`API.GetRuleDetails(${zone}, ${id}) failed`);
                }
            })
            .then((data) => {
                return data as Rule;
            });
    };

    /**
     * Create a new rule. After creating the rule, you can add components.
     */
    static AddRule = (zone: string, protocol: string, priority: number, name: string): Promise<Rule> => {
        Logger.Info(`API.AddRule(${zone}, ${protocol}, ${priority}, ${name})`);

        // Enforce name
        if (!name) {
            name = `${protocol} ${zone}`;
        }

        const payload = {
            zone: zone,
            priority: priority,
            networkprotocol: protocol,
            name: name
        };

        return this.post("rules", payload)
            .then((resp) => {
                if (resp.ok) {
                    return resp.json();
                } else {
                    throw Error(`API.AddRule(${zone}, ${protocol}, ${priority}, ${name}) failed`);
                }
            })
            .then((data) => {
                return data as Rule;
            });
    };

    /**
     * Edit the priority of a rule. You can't edit anything else about a rule, sorry bud.
     */
    static UpdateRule = async (rule: Rule, priority: number): Promise<Rule> => {
        Logger.Info(`API.UpdateRule(${rule.zone}, ${rule.ruleid})`);

        if (!rule.zone || !rule.ruleid) {
            throw Error(`API.UpdateRule(${rule.zone}, ${rule.ruleid}) bad arguments`);
        }

        return this.put(`rules/${rule.zone}/${rule.ruleid}`, priority).then((resp) => {
            if (resp.ok) {
                rule.priority = priority;
                return rule;
            } else {
                throw Error(`API.UpdateRule(${rule.zone}, ${rule.ruleid}) failed`);
            }
        });
    };

    /**
     * Delete a rule.
     */
    static DeleteRule = async (rule: Rule): Promise<void> => {
        Logger.Info(`API.DeleteRule(${rule.zone}, ${rule.ruleid})`);

        if (!rule.zone || !rule.ruleid) {
            throw Error(`API.DeleteRule(${rule.zone}, ${rule.ruleid}) bad arguments`);
        }

        return this.delete(`rules/${rule.zone}/${rule.ruleid}`).then((resp) => {
            if (!resp.ok) {
                throw Error(`API.DeleteRule(${rule.zone}, ${rule.ruleid}) failed`);
            }
        });
    };

    /**
     * Add a component (a condition or result) to a rule. Refer to TODO for condition and result values.
     */
    static AddRuleComponent = (rule: Rule, component: NewRuleComponent): Promise<RuleComponent> => {
        Logger.Info(`API.AddRuleComponent(${rule.zone}, ${rule.name}, ${component.actionname})`);

        if (!rule.zone || !rule.ruleid) {
            throw Error(`API.AddRuleComponent(${rule.zone}, ${rule.name}, ${component.actionname}) bad arguments`);
        }

        return this.post(`rules/${rule.zone}/${rule.ruleid}/components`, component)
            .then((resp) => {
                if (resp.ok) {
                    return resp.json();
                } else {
                    throw Error(`API.AddRuleComponent(${rule.zone}, ${rule.name}, ${component.actionname}) failed`);
                }
            })
            .then((data) => {
                return data as RuleComponent;
            });
    };

    /**
     * Edit an existing component's action value. No other fields can be edited.
     */
    static EditRuleComponent = async (rule: Rule, component: RuleComponent, newValue: string): Promise<void> => {
        Logger.Info(`API.EditRuleComponent(${rule.zone}, ${rule.ruleid}, ${component.componentid})`);

        if (!rule.zone || !rule.ruleid || !component.componentid) {
            throw Error(`API.EditRuleComponent(${rule.zone}, ${rule.ruleid}, ${component.componentid}) bad arguments`);
        }

        const putValue = { "actionvalue": newValue };

        return this.put(`rules/${rule.zone}/${rule.ruleid}/components/${component.componentid}`, putValue).then((resp) => {
            if (!resp.ok) {
                throw Error(`API.EditRuleComponent(${rule.zone}, ${rule.ruleid}, ${component.componentid}) failed`);
            }
        });
    };

    /**
     * Delete a rule.
     */
    static DeleteRuleComponent = async (rule: Rule, component: RuleComponent): Promise<void> => {
        Logger.Info(`API.DeleteRuleComponent(${rule.zone}, ${rule.ruleid}, ${component.componentid})`);

        if (!rule.zone || !rule.ruleid || !component.componentid) {
            throw Error(`API.DeleteRuleComponent(${rule.zone}, ${rule.ruleid}, ${component.componentid}) bad arguments`);
        }

        return this.delete(`rules/${rule.zone}/${rule.ruleid}/components/${component.componentid}`).then((resp) => {
            if (!resp.ok) {
                throw Error(`API.DeleteRuleComponent(${rule.zone}, ${rule.ruleid}, ${component.componentid}) failed`);
            }
        });
    };

    /**
     * `POST /zones` Create a new zone.
     */
    static AddZone = async (zone: string, domain: string, num: number): Promise<boolean> => {
        Logger.Info(`API.AddZone(${zone}, ${domain}, ${num})`);

        const httpBody = {
            zone: zone,
            domain: domain,
            num: num
        };

        return this.post("zones", httpBody).then((resp) => {
            if (resp.ok) {
                return true;
            } else if (resp.status == 404) {
                return false;
            } else {
                throw Error(`API.AddZone(${zone}, ${domain}, ${num}) failed`);
            }
        });
    };

    /**
     * GET /authz Get all permissions upon a given zone.
     */
    static GetUsers = async (zone: string): Promise<User[]> => {
        Logger.Info(`API.GetUsers(${zone})`);

        if (!zone) {
            throw Error(`API.GetUsers(${zone}) bad arguments`);
        }

        return this.get(`authz/${zone}`)
            .then((resp) => {
                if (resp.ok) {
                    return resp.json();
                } else {
                    throw Error(`API.GetUsers(${zone}) failed`);
                }
            })
            .then((data) => {
                return data as User[];
            });
    };

    /**
     * POST /authz/{zone}/{user} Grant permissions on {zone} to {user}. Caller must have a permission equal to or higher than permission to be assigned.
     */
    static AddUserToZone = async (zone: string, user: string, permission: number): Promise<void> => {
        Logger.Info(`API.AddUserToZone(${zone}, ${user}, ${permission})`);

        if (!zone || !user) {
            throw Error(`API.AddUserToZone(${zone}, ${user}, ${permission}) bad arguments`);
        }

        // show uppercase permission based on number
        let permissionString = "READONLY";
        if (permission == PERMISSION.READWRITE) permissionString = "READWRITE";
        if (permission == PERMISSION.ASSIGNROLES) permissionString = "ASSIGNROLES";
        if (permission == PERMISSION.OWNER) permissionString = "OWNER";


        // try old API, may throw a 405
        try {
            await this.post(`authz/${zone}/${user}`, { permission: permissionString })
            .then(resp => {
                if (!resp.ok) {
                    throw Error(`API.AddUserToZone(${zone}, ${user}, ${permission}) failed`);
                }
            });
            
        } 
        catch {
            Logger.Warn(`API.AddUserToZone(${zone}, ${user}, ${permission}) failed [expected], trying the new API`);            
        }

        // new API coming up
        try {
            await this.post(`authz/${zone}/`, { 
                alias: user, 
                permission: permissionString.toLowerCase()
            })
            .then((resp) => {
                if (!resp.ok) {
                    throw Error(`API.AddUserToZone(${zone}, ${user}, ${permission}) failed [expected, if old API didn't fail]`);
                }
                return;
            });        
        } 
        catch { /* will fail for now (early feb 2025) */ }
    }

    /**
     * DELETE /authz/{zone}/{user} Revoke the permission that USER has on ZONE. Only owners can revoke other owners.
     */
    static RemoveUserFromZone = async (zone: string, user: string): Promise<void> => {
        Logger.Info(`API.RemoveUserFromZone(${zone}, ${user})`);

        if (!zone || !user) {
            throw Error(`API.RemoveUserFromZone(${zone}, ${user}) bad arguments`);
        }

        return this.delete(`authz/${zone}/${user}`).then((resp) => {
            if (!resp.ok) {
                throw Error(`API.RemoveUserFromZone(${zone}, ${user}) failed`);
            }
        });
    };

    /**
     * Static method that displays current time (to detect cached responses)
     */
    static HeartBeat = async (): Promise<void> => {
        Logger.Info(`API.HeartBeat()`);

        return this.get("ping").then((resp) => {
            if (!resp.ok) {
                throw Error(`API.HeartBeat() failed`);
            }
        });
    };


    /**
     * GET /domains: Get all the domains the user has any permission on.
     */
    static GetDomains = async (): Promise<string[]> => {
        Logger.Info(`API.GetDomains()`);

        return this.get("domains")
            .then((resp) => {
                console.log(resp);
                if (resp.ok) {
                    return resp.json();
                } else {
                    throw Error(`API.GetDomains() failed`);
                }
            })
            .then((data) => {
                return data as string[];
            });
    };
}
