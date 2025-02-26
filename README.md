# Dusseldorf

Dusseldorf is a versatile out-of-band application security testing (OAST) tool. It is designed to provide security professionals a platform that analyzes incoming network requests and craft automated responses.  This initiative is part of Microsoft's increasing investment in Open Source and security research.  

It is aimed to help automate the detection and exploitation of OOB (out of band) security vulnerabilities such as *Server Side Request Forgery* (SSRF), *Cross Site Scripting* (XSS), *Server Side Template Injection* (SSTI), *eXternal XML Entities* (XXE) and many other classes of security defects.  

> This project is often stylized as *duSSeldoRF*, following a [common practice](https://en.wikipedia.org/wiki/List_of_Microsoft_codenames) to use place names.  The beautiful Bavarian city Dusseldorf is one of the few places in the world with the letters *SSRF* in its name.  

Dusseldorf provides a platform that deploys DNS, HTTP, and HTTPS network listeners and listens on a domain name, such as `*.yourdomain.net`.  All requests to this domain name, and any subdomain in it (called _zones_, such as `foo.yourdomain.net` and `foo.bar.yourdomain.net`) are captured by these listeners.  A clear user interface (and corresponding REST API) provide the ability to see these captured requests and their reponses, and you can configure your own custom responses.  To enable collaboration with others, you can add other users from the your EntraID tenant to analyze your network requests.

For more information on how to use Dusseldorf, and how it can be used to find security vulnerabilities, please see [this guide](/docs/using).


## Getting Started
Dusseldorf is designed to run on the Internet, and it is natively build to runs on Azure public cloud.  To setup your own instance, we have instructions for how to deploy Dusseldorf into your [Azure](docs/deploy/azure/) environment, or on your own [local server](/docs/deploy/local).

Prebuild container images are available [here]().  And instructions on how to build the source code from scratch can be found in our [build documentation](docs/build).

If you want to build custom listeners for any network protocol, you can follow [this page](docs/develop/listeners) on how to get started.


## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
