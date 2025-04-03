import type { NextConfig } from 'next'

const config: NextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_CONTRACT_ADDRESS: process.env.NEXT_PUBLIC_CONTRACT_ADDRESS ?? '',
    NEXT_PUBLIC_CONTRACT_ABI_PATH: process.env.NEXT_PUBLIC_CONTRACT_ABI_PATH ?? '',
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL ?? '',
    NEXT_PUBLIC_NETWORK_ID: process.env.NEXT_PUBLIC_NETWORK_ID ?? '',
    NEXT_PUBLIC_NETWORK_NAME: process.env.NEXT_PUBLIC_NETWORK_NAME ?? '',
    NEXT_PUBLIC_DEV_MODE: process.env.NEXT_PUBLIC_DEV_MODE ?? 'false',
  },
}

export default config
