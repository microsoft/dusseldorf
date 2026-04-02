# Dusseldorf Deployment Guide

This guide is the entry point for deploying and operating Dusseldorf as a private, customizable OAST platform.

## Who This Is For

- Security researchers and operators who want to deploy and run a private OAST environment.
- Developers and platform engineers who want to extend listeners, API behavior, and deployment workflows.

## Private and Customizable by Design

- Dusseldorf is intended for private deployment in your own environment.
- You control identity integration, infrastructure footprint, domains, and runtime policies.
- You can customize request handling and response behavior through rules and service-level changes.

## Prerequisites

Ensure you have the following installed:

- Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- Docker Compose
- Azure CLI (`az`)
- OpenSSL (for TLS certificate generation)
- Python 3 with `pip`
- jq (`sudo apt-get install jq` or `brew install jq`)
- Helm (`https://helm.sh/docs/intro/install/`)

## Deployment Paths

### Local Development and Validation

Use this path for private lab setups, fast local validation, and developer iteration.

- Start here: [docs/local/readme.md](local/readme.md)
- Includes credential generation, certificate setup, and local compose workflows

### Azure Deployment

Use this path for private cloud deployment using Azure resources and Helm.

- Start here: [docs/azure/readme.md](azure/readme.md)
- Includes infrastructure provisioning and database initialization

## End-User Operations

After deployment, use the platform through UI and API workflows:

- Usage guide: [docs/using.md](using.md)
- CLI workflows: [cli/README.md](../cli/README.md)

## Developer Extensibility

For contributors extending the system:

- Service architecture and runtime composition: [dusseldorf/README.md](../dusseldorf/README.md)
- CLI implementation and usage: [cli/README.md](../cli/README.md)
- Local component stack for rapid testing: [dusseldorf/compose.yml](../dusseldorf/compose.yml)

## Troubleshooting

- Local deployment issues: [docs/local/readme.md](local/readme.md)
- Azure deployment issues: [docs/azure/readme.md](azure/readme.md)
- Auth and CLI token setup: [cli/ENTRAID_SETUP.md](../cli/ENTRAID_SETUP.md)