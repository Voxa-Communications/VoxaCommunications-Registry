# VoxaCommunications Registry

A central security and identity management system for the decentralized VoxaCommunications Network.
THIS IS ARCHIVED AS OF 6/21/25

## Vision

The VoxaCommunications Registry serves as the sole centralized component in an otherwise fully decentralized communications network. It's designed with a specific purpose: to provide secure identity management, node registration, and authentication services while preserving user privacy and network integrity.

## Core Purpose

This registry acts as the trusted authority for:

1. **Node Registration & Management**: Maintaining an authoritative record of all legitimate nodes operating on the network
2. **Anonymous Identity Provision**: Creating and managing anonymous user identifiers that enable secure communication without compromising privacy
3. **Authentication Services**: Providing robust authentication mechanisms including JWT-based authentication and two-factor authentication (2FA)
4. **Security Gateway**: Serving as a security checkpoint to prevent malicious nodes from participating in the network

## Key Features

- **Secure Node Registration**: Allows new nodes to register with the network using cryptographic verification
- **Two-Factor Authentication**: Implements TOTP-based 2FA for enhanced security
- **JWT Token Management**: Issues and validates JSON Web Tokens for secure API access
- **Database Migration System**: Includes a comprehensive migration system for schema evolution
- **Dynamic API Endpoints**: Utilizes a flexible system for handling API requests
- **Comprehensive Logging**: Provides detailed logging for security audit and debugging purposes

## Security Philosophy

The registry is designed with a "security-first" mindset:

- All communications are secured with robust encryption
- User identities are kept anonymous through tokenization
- Two-factor authentication is available for administrative access
- Database migrations provide controlled schema evolution
- Comprehensive logging enables security auditing

## Future Vision

While currently implemented as a centralized service, the long-term roadmap includes exploring ways to distribute registry functionality across trusted nodes while maintaining the security and reliability benefits of centralization.

## Technical Implementation

Built using:
- Python Flask for API services
- MySQL for data persistence
- JWT for secure token-based authentication
- TOTP for two-factor authentication
- KVProcessor for configuration management

## Getting Started

See [SETUP.md](SETUP.md) for instructions on deploying and configuring the Registry.

---

**Note**: This registry is the only centralized component in the VoxaCommunications Network architecture. All other communications occur directly between nodes without central coordination once identity and authentication are established.

## License

This project is licensed under the Attribution-NonCommercial-ShareAlike 4.0 Internation License - see the [LICENSE](LICENSE) file for details.
