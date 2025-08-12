# Dusseldorf

Dusseldorf is a versatile out-of-band application security testing (OAST) tool.  It is designed to provide a platform that analyzes incoming network requests and craft automated responses.  This initiative is part of Microsoft's increasing investment in Open Source and security research.  

It is aimed to empower security professionals to help automate the detection and exploitation of OOB (out of band) security vulnerabilities such as *Server Side Request Forgery* (SSRF), *Cross Site Scripting* (XSS), *Server Side Template Injection* (SSTI), *eXternal XML Entities* (XXE) and many other classes of security defects.  

> This project is often stylized as *duSSeldoRF*, following a [common practice](https://en.wikipedia.org/wiki/List_of_Microsoft_codenames) to use place names.  The beautiful city Düsseldorf is one of the few places in the world with the letters *SSRF* in its name.  For ease of use we substituted the umlaut character (alt-0252) ü for a normal u.

Dusseldorf deploys DNS, HTTP, and HTTPS network listeners and listens on a domain name, such as `*.yourdomain.net`.  All requests to this domain name, and any subdomain in it (called _zones_, such as `foo.yourdomain.net` and `foo.bar.yourdomain.net`) are captured by these network listeners.  

Using the protected graphical user interface (and corresponding REST API), you can see these captured requests and their responses.  Furthermore, you can configure your own custom responses and filters.  



## Getting Started

Dusseldorf is designed to run on the Internet, and it is natively build to run on Azure's public cloud.  To run Dusseldorf, you'd need the following prerequisites:

 - a machine on the Internet with one or more public IPv4 address(es)
 - a domain name with its `NS` record (name server) pointed at this IP address/addresses. 

If you have this machine setup, then follow the steps in the [installation guide](docs/install.md) to install Dusseldorf onto your infrastructure.  This includes to run Dusseldorf both in Azure, or as a standalone installation.


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
