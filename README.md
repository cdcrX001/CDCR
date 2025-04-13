# CDCR (Confidential Decentralized Data Clean Room)

CDCR is a decentralized platform that combines blockchain technology with confidential computing using Evervault enclaves to provide secure and verifiable computation resources.

## 🏗️ Architecture
![mermaid-diagram-2025-04-04-012851](https://github.com/user-attachments/assets/bf66af31-cf8e-48d3-bedf-0ec7e08ab0f9)


The project consists of four main components:

### 1. Smart Contracts (Blockchain Layer)
- Located in `/Contracts`
- Manages enclave requests and verifications on-chain
- Integrates with Chainlink for secure off-chain data
- Key contracts:
  - `EnclaveManager.sol`: Main contract for managing enclave requests
  - `ChainlinkConfig.sol`: Configuration for Chainlink integration

### 2. Backend Service
- Located in `/backend`
- FastAPI server handling enclave deployment requests
- Provides encryption services for secure communication
- RESTful API endpoints for enclave management

### 3. Frontend Application
- Located in `/frontend`
- Next.js based web interface
- Modern UI with Tailwind CSS
- Secure communication with backend and blockchain

### 4. Evervault Auto Enclave
- Located in `/evervault auto enclave`
- Manages automated enclave deployment
- Real-time deployment status updates via WebSocket
- Celery-based task queue for async operations

## 🚀 Getting Started

### Prerequisites
- Node.js 16+
- Python 3.8+
- Solidity compiler 0.8.7+
- Evervault API credentials
- Chainlink testnet/mainnet setup

### Environment Setup

1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.template .env
# Fill in your environment variables
```

2. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
# Fill in your environment variables
```

3. Evervault Enclave Setup
```bash
cd "evervault auto enclave"
pip install -r requirements.txt
cp .env.template .env
# Fill in your Evervault credentials
```

4. Smart Contract Deployment
```bash
# Deploy using your preferred Ethereum development framework
# Configure ChainlinkConfig.sol with your network's values
```

## 🔒 Security Features

1. **Encryption Layer**
   - RSA encryption for sensitive data
   - Public key encryption for enclave communication

2. **Blockchain Security**
   - Chainlink oracle integration for trusted data
   - Smart contract access controls
   - Request expiry mechanisms

3. **Confidential Computing**
   - Evervault enclaves for secure computation
   - Isolated execution environments
   - Encrypted data processing

## 📡 API Endpoints

### Backend API
- `GET /api/test`: Test endpoint with encryption
- `GET /`: Health check endpoint

### Enclave Management API
- `POST /deploy-enclaves`: Deploy new enclaves
- WebSocket endpoints for real-time deployment status

## 🔧 Configuration

### Smart Contract Configuration
- Chainlink oracle address
- LINK token address
- Job ID and fee configuration

### Backend Configuration
- `ENCLAVE_DEPLOYMENT_URL`: Evervault deployment endpoint
- API encryption keys

### Frontend Configuration
- API endpoints
- Web3 provider configuration
- Environment variables in `.env`

## 📦 Project Structure

```
CDCR/
├── backend/                 # FastAPI backend service
├── frontend/               # Next.js frontend application
│   └── src/               # Frontend source code
├── Contracts/             # Solidity smart contracts
└── evervault auto enclave/ # Enclave management service
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Evervault for confidential computing infrastructure
- Chainlink for decentralized oracle network
- OpenZeppelin for secure smart contract components 
