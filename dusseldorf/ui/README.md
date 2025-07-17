# Dusseldorf UI
This is the graphical user interface for [Dusseldorf](https://aka.ms/dusseldorf), which provides an easy 
human way to interface with Dusseldorf's API. 

This runs as its own component, it's a static web page build in the React Framework, hosted as a static component within the API repository. 

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
This UI is build upon the amazing [Fluent2](https://fluent2.microsoft.design/) design framework.

