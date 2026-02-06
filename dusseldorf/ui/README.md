# Dusseldorf UI

This component is the graphical user interface for Project Dusseldorf, for more info on the project, please check https://aka.ms/dusseldorf.

This component provides a simple but rich UI to make it easier to work with Dusseldorf.  It's a static web page build in React, and talks to the REST API.  By default, it is hosted as a static component within the API repository under the `/ui` path.  



# Running Locally

To load this locally, do the following:

``` bash
$ npm install 
$ npm test # <-- this runs our tests, to make sure your site will run. 
$ HTTPS=true npm start 
```

Then go to localhost:3000 to see the UI working.  It will connect to a relative endpoint being `api/`, as this is the default 
location of the API.  You can override it if needed, by setting the `api_host` key in localstorage.  For example, you can do the following: 

``` javascript
localStorage['api_host'] = "localhost:5001"
```
in the console of the DevTools in your favourite browser to any value to change which API endpoint you talk to. 

# Design 
This UI is built upon the amazing [Fluent2](https://fluent2.microsoft.design/) design framework.


# Changelog
- 2025-11-28: set API host precedence to  `REACT_APP_API_HOST` > `localStorage['api_host']` > `"/api"` and split panel resize.


