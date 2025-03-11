# Introduction

This is the HTTP listener for Dusseldorf, which listens for network requests on an HTTP or HTTPS interface.  Dusseldorf 
analyzes the request, and respond with a particular payload if configured in the rules, or a normal default answer.

# Running locally
You need to download a few packages to build a local library, this is automated in a script called `setenv.sh`, which you can run in the following way:

```shell
$ . setenv.sh
(wait for install to finish...)
$ python3 src/run.py
```

# Development
Please clone the repo, and submit a PR with a branch name in the form of: `users/<alias>/feature`, such as: `users/mihendri/http2_responses`.  When done, submit a PR, and when approved - it'll roll out automatically.

# Test locally
to run on a higher port, so you don't need root privs.

```shell
$ . setenv.sh
$  LSTNER_HTTP_TLS=0 LSTNER_HTTP_PORT=10080 python3 src/run.py 
```