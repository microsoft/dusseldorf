# Dusseldorf UI
Admin UI for [Dusseldorf](https://aka.ms/dusseldorf).

This runs as its own component, it's a static web page build in the React Framework, hosted on https://dusseldorf.security.azure/ 

# Running Locally

To load this locally, do the following:

``` bash
$ npm install 
$ npm test # <-- this runs our tests, to make sure your site will run. 
$ npm start 
```

Then go to localhost:3000 to see the UI working.  It WILL connect to the following endpoint `https://api.dusseldorf.security.azure/`.  You can override it if needed, by setting the `api_host` key in localstorage to an HTTPS (!) endopint.  For canary, you can use: 

 * Canary API : `https://api.dusseldorf.security.azure/` 

Simply execute `localStorage['api_host'] = "your.api.endpoint"` in the console of the DevTools in your favourite browser to any value to change whwhich API endpoint you talk to.  For example, in your favourite browser; press F12 and co to the *console*, and type:
``` javascript
localStorage['api_host'] = "localhost:5001"
```
If you want the API host to be localhost, on port 5001 (such as a local instance of Kestrel or Visual Studio).

# Design 
This UI is build upon the amazing [FluentUI](https://developer.microsoft.com/en-us/fluentui#/) framework.

