interface Config {
  contractAddress: string
  networkId: string
  networkName: string
  apiBaseUrl: string
  isDev: boolean
}

export const config: Config = {
  contractAddress: process.env.NEXT_PUBLIC_CONTRACT_ADDRESS || '',
  networkId: process.env.NEXT_PUBLIC_NETWORK_ID || '',
  networkName: process.env.NEXT_PUBLIC_NETWORK_NAME || '',
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || '',
  isDev: process.env.NEXT_PUBLIC_DEV_MODE === 'true'
}

// Validate required configuration
const requiredConfig = ['contractAddress', 'networkId', 'networkName', 'apiBaseUrl'] as const

export function validateConfig() {
  for (const key of requiredConfig) {
    if (!config[key]) {
      throw new Error(`Missing required configuration: ${key}`)
    }
  }
}

// Helper function to get the ABI
export async function getContractABI() {
  try {
    const response = await fetch('/abi/contract.json')
    if (!response.ok) {
      throw new Error('Failed to load contract ABI')
    }
    return await response.json()
  } catch (error) {
    console.error('Error loading contract ABI:', error)
    throw error
  }
} 