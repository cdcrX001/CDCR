'use client'

import { useState, useEffect } from 'react'
import { ethers } from 'ethers'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Loader2 } from 'lucide-react'

const contractABI = [
  "function requestEnclaveCreation(string memory publicKey) public payable returns (bytes32 requestId)",
  "function getEnclaveDetails(bytes32 requestId) public view returns (string memory)",
  "function userRequests(address user, uint256 index) public view returns (bytes32)",
  "event EnclaveRequested(bytes32 indexed requestId, address indexed user)",
  "event EnclaveFulfilled(bytes32 indexed requestId, string encryptedDetails)"
]

const contractAddress = "YOUR_CONTRACT_ADDRESS_HERE"

export function DataCleanRoom() {
  const [provider, setProvider] = useState<ethers.providers.Web3Provider | null>(null)
  const [contract, setContract] = useState<ethers.Contract | null>(null)
  const [account, setAccount] = useState<string | null>(null)
  const [publicKey, setPublicKey] = useState('')
  const [requestId, setRequestId] = useState<string | null>(null)
  const [enclaveDetails, setEnclaveDetails] = useState<string | null>(null)
  const [userRequests, setUserRequests] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const init = async () => {
      if (typeof window.ethereum !== 'undefined') {
        const web3Provider = new ethers.providers.Web3Provider(window.ethereum)
        setProvider(web3Provider)

        const signer = web3Provider.getSigner()
        const enclaveContract = new ethers.Contract(contractAddress, contractABI, signer)
        setContract(enclaveContract)

        window.ethereum.on('accountsChanged', handleAccountsChanged)
      }
    }

    init()

    return () => {
      if (window.ethereum && window.ethereum.removeListener) {
        window.ethereum.removeListener('accountsChanged', handleAccountsChanged)
      }
    }
  }, [])

  const handleAccountsChanged = (accounts: string[]) => {
    if (accounts.length > 0) {
      setAccount(accounts[0])
      fetchUserRequests(accounts[0])
    } else {
      setAccount(null)
      setUserRequests([])
    }
  }

  const connectWallet = async () => {
    if (provider) {
      try {
        const accounts = await provider.send("eth_requestAccounts", [])
        handleAccountsChanged(accounts)
      } catch (error) {
        console.error("Failed to connect wallet:", error)
        setError("Failed to connect wallet. Please try again.")
      }
    }
  }

  const fetchUserRequests = async (userAddress: string) => {
    if (!contract) return
    setIsLoading(true)
    setError(null)
    try {
      const requests = []
      let index = 0
      while (true) {
        try {
          const request = await contract.userRequests(userAddress, index)
          requests.push(request)
          index++
        } catch (error) {
          break
        }
      }
      setUserRequests(requests)
    } catch (error) {
      console.error('Error fetching user requests:', error)
      setError("Failed to fetch user requests. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const requestEnclaveCreation = async () => {
    if (!contract || !publicKey) return
    setIsLoading(true)
    setError(null)
    try {
      const tx = await contract.requestEnclaveCreation(publicKey)
      const receipt = await tx.wait()
      const event = receipt.events?.find((e: any) => e.event === 'EnclaveRequested')
      if (event) {
        setRequestId(event.args.requestId)
        fetchUserRequests(account!)
      }
    } catch (error) {
      console.error('Error requesting enclave creation:', error)
      setError("Failed to create enclave. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const getEnclaveDetails = async (requestId: string) => {
    if (!contract) return
    setIsLoading(true)
    setError(null)
    try {
      const details = await contract.getEnclaveDetails(requestId)
      setEnclaveDetails(details)
    } catch (error) {
      console.error('Error getting enclave details:', error)
      setError("Failed to fetch enclave details. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="w-[400px]">
      <CardHeader>
        <CardTitle>Data Clean Room</CardTitle>
        <CardDescription>Create and manage your data clean rooms</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid w-full items-center gap-4">
          {!account ? (
            <Button onClick={connectWallet}>Connect Wallet</Button>
          ) : (
            <>
              <div className="flex flex-col space-y-1.5">
                <Input
                  placeholder="Enter public key"
                  value={publicKey}
                  onChange={(e) => setPublicKey(e.target.value)}
                />
              </div>
              <Button onClick={requestEnclaveCreation} disabled={isLoading || !publicKey}>
                {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Create Data Clean Room
              </Button>
              {requestId && (
                <div>
                  <p className="text-sm font-medium">Latest Request ID: {requestId}</p>
                  <Button onClick={() => getEnclaveDetails(requestId)} disabled={isLoading}>
                    Get Enclave Details
                  </Button>
                </div>
              )}
              {enclaveDetails && (
                <Alert>
                  <AlertTitle>Enclave Details</AlertTitle>
                  <AlertDescription>{enclaveDetails}</AlertDescription>
                </Alert>
              )}
              <div>
                <h3 className="text-lg font-semibold mb-2">Your Data Clean Rooms:</h3>
                {userRequests.length > 0 ? (
                  <ul className="space-y-2">
                    {userRequests.map((req, index) => (
                      <li key={index} className="flex items-center justify-between">
                        <span className="text-sm truncate w-48">{req}</span>
                        <Button onClick={() => getEnclaveDetails(req)} disabled={isLoading} size="sm">
                          View Details
                        </Button>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500">No data clean rooms created yet.</p>
                )}
              </div>
            </>
          )}
        </div>
      </CardContent>
      <CardFooter>
        {error && (
          <Alert variant="destructive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        {account && (
          <p className="text-sm">Connected Account: {account.slice(0, 6)}...{account.slice(-4)}</p>
        )}
      </CardFooter>
    </Card>
  )
}

