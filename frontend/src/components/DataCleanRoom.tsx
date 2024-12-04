'use client'

import React, { useState, useEffect } from 'react'
import { ethers } from 'ethers'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Loader2 } from 'lucide-react'
import { io, Socket } from 'socket.io-client'

// Extend Window interface to include ethereum property
declare global {
  interface Window {
    ethereum?: any;
  }
}

const contractABI = [
  "function requestEnclaveCreation(string memory publicKey) public payable returns (bytes32 requestId)",
  "function getEnclaveDetails(bytes32 requestId) public view returns (string memory)",
  "function userRequests(address user, uint256 index) public view returns (bytes32)",
  "function enclaveRequests(bytes32 requestId) public view returns (address user, string encryptedDetails, uint256 createdAt)",
  "event EnclaveRequested(bytes32 indexed requestId, address indexed user)",
  "event EnclaveFulfilled(bytes32 indexed requestId, string encryptedDetails)"
]

const contractAddress = "0xB2a1d19F5f9A7c3b97062C83f993447C96559e25"


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
  const [keyPair, setKeyPair] = useState<{ publicKey: string; privateKey: string } | null>(null)
  const [retrievedData, setRetrievedData] = useState<string>('')
  const [decryptedData, setDecryptedData] = useState<string>('')
  const [socket, setSocket] = useState<Socket | null>(null)
  const [deploymentStatus, setDeploymentStatus] = useState<{
    status: 'idle' | 'deploying' | 'completed';
    enclaveDetails?: {
      name: string;
      domain: string;
      pcrs: {
        pcr0: string;
        pcr1: string;
        pcr2: string;
        pcr8: string;
      };
      uuid: string;
    };
  }>({ status: 'idle' });

  useEffect(() => {
    const init = async () => {
      if (typeof window.ethereum !== 'undefined') {
        try {
          const web3Provider = new ethers.providers.Web3Provider(window.ethereum)
          setProvider(web3Provider)

          const signer = web3Provider.getSigner()
          const enclaveContract = new ethers.Contract(contractAddress, contractABI, signer)
          setContract(enclaveContract)

          window.ethereum.on('accountsChanged', handleAccountsChanged)
        } catch (error) {
          console.error('Initialization error:', error)
          setError('Failed to initialize Web3')
        }
      }
    }

    init()

    return () => {
      if (window.ethereum?.removeListener) {
        window.ethereum.removeListener('accountsChanged', handleAccountsChanged)
      }
      if (socket) {
        socket.disconnect()
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
      
      // Keep fetching until we hit an error (indicating end of list) or reach MAX_USER_REQUESTS
      while (index < 20) { // MAX_USER_REQUESTS from contract
        try {
          const requestId = await contract.userRequests(userAddress, index)
          if (requestId !== '0x0000000000000000000000000000000000000000000000000000000000000000') {
            requests.push(requestId)
          }
          index++
        } catch (error) {
          break
        }
      }
      setUserRequests(requests)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred'
      setError("Failed to fetch user requests: " + errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const requestEnclaveCreation = async () => {
    if (!contract || !keyPair) return;
    setIsLoading(true);
    setError(null);
    
    try {
      // The public key is already properly encoded, send it directly
      console.log('Sending encoded public key:', keyPair.publicKey);
      
      const tx = await contract.requestEnclaveCreation(keyPair.publicKey);
      const receipt = await tx.wait();
      
      const event = receipt.events?.find((e: any) => e.event === 'EnclaveRequested');
      if (event) {
        setRequestId(event.args.requestId);
        fetchUserRequests(account!);
      }
    } catch (error: any) {
      console.error('Error requesting enclave creation:', error);
      setError(error.message || "Failed to create enclave. Please ensure the public key is valid.");
    } finally {
      setIsLoading(false);
    }
  };

  const getEnclaveDetails = async (requestId: string, retryCount = 0) => {
    if (!contract || !keyPair) return;
    setIsLoading(true);
    setError(null);
    
    try {
      console.log(`Attempt ${retryCount + 1} - Fetching details for requestId:`, requestId);
      
      const encryptedDetails = await contract.getEnclaveDetails(requestId);
      console.log('Received encrypted details:', encryptedDetails);
      setRetrievedData(encryptedDetails);

      // Decrypt the retrieved data
      try {
        // Step 5: Decode Base64 encrypted message (matches Python's base64.b64decode)
        const encryptedBytes = Uint8Array.from(atob(encryptedDetails), c => c.charCodeAt(0));
        console.log('Decoded encrypted bytes:', encryptedBytes);

        // Import private key from PEM format
        // First remove PEM headers and decode base64
        const privateKeyBase64 = keyPair.privateKey
          .replace('-----BEGIN PRIVATE KEY-----', '')
          .replace('-----END PRIVATE KEY-----', '')
          .replace(/\n/g, '');
        
        const privateKeyDER = Uint8Array.from(atob(privateKeyBase64), c => c.charCodeAt(0));
        
        // Import the private key with the same parameters as Python
        const privateKey = await window.crypto.subtle.importKey(
          "pkcs8",
          privateKeyDER,
          {
            name: "RSA-OAEP",
            hash: { name: "SHA-256" }, // Matches Python's hashes.SHA256()
          },
          false, // not extractable
          ["decrypt"]
        );

        // Step 6: Decrypt using RSA-OAEP with SHA-256 (matches Python's padding.OAEP)
        const decryptedBytes = await window.crypto.subtle.decrypt(
          {
            name: "RSA-OAEP"
          },
          privateKey,
          encryptedBytes
        );

        // Convert decrypted bytes to UTF-8 string (matches Python's decode('utf-8'))
        const decryptedText = new TextDecoder('utf-8').decode(decryptedBytes);
        console.log('Decrypted text:', decryptedText);
        
        // Try to parse as JSON and check for socket information
        try {
          const jsonData = JSON.parse(decryptedText)
          setDecryptedData(decryptedText)
          
          // If we have socket information, connect to the socket
          if (jsonData.socket_server_url && jsonData.socket_room) {
            connectToSocket(jsonData)
          }
        } catch (jsonError) {
          // If it's not JSON, just set it as regular text
          setDecryptedData(decryptedText)
        }
        
        setEnclaveDetails(decryptedText);
      } catch (error: any) {
        console.error('Decryption error:', error);
        setError(`Failed to decrypt data: ${error.message}`);
      }
    } catch (error: any) {
      console.error('Error details:', {
        requestId,
        error: error.message,
        retryCount,
      });
      
      if (error.message.includes('Enclave details not available') && retryCount < 3) {
        setError('Waiting for enclave details... Will retry automatically.');
        setTimeout(() => {
          getEnclaveDetails(requestId, retryCount + 1);
        }, 5000);
      } else {
        setError(
          retryCount >= 3 
            ? 'Enclave details not available after several attempts. Please try again later.'
            : `Failed to fetch enclave details: ${error.message}`
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  const generateKeyPair = async () => {
    try {
      // Generate RSA key pair
      const keyPair = await window.crypto.subtle.generateKey(
        {
          name: "RSA-OAEP",
          modulusLength: 2048,
          publicExponent: new Uint8Array([1, 0, 1]),
          hash: "SHA-256",
        },
        true,
        ["encrypt", "decrypt"]
      );

      // Export public key to SPKI format
      const publicKeySpki = await window.crypto.subtle.exportKey(
        "spki",
        keyPair.publicKey
      );

      // Create PEM format first
      const publicKeyPEM = [
        '-----BEGIN PUBLIC KEY-----',
        btoa(String.fromCharCode(...new Uint8Array(publicKeySpki)))
          .match(/.{1,64}/g)
          ?.join('\n'),
        '-----END PUBLIC KEY-----'
      ].join('\n');

      // Then encode the entire PEM as base64
      const finalEncodedPublicKey = btoa(publicKeyPEM);

      // Export private key for later decryption
      const privateKeyPkcs8 = await window.crypto.subtle.exportKey(
        "pkcs8",
        keyPair.privateKey
      );
      const privateKeyPEM = [
        '-----BEGIN PRIVATE KEY-----',
        btoa(String.fromCharCode(...new Uint8Array(privateKeyPkcs8)))
          .match(/.{1,64}/g)
          ?.join('\n'),
        '-----END PRIVATE KEY-----'
      ].join('\n');

      return {
        publicKey: finalEncodedPublicKey,
        privateKey: privateKeyPEM
      };
    } catch (error) {
      console.error('Error generating key pair:', error);
      throw error;
    }
  }

  const handleGenerateKeyPair = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const newKeyPair = await generateKeyPair();
      setKeyPair(newKeyPair); // Set the generated key pair in state
      console.log('Generated key pair:', newKeyPair); // Debug log
    } catch (error: any) {
      console.error('Error generating keys:', error);
      setError('Failed to generate keys: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const sendPublicKey = async () => {
    try {
      if (!keyPair) {
        throw new Error('Please generate a key pair first')
      }

      if (!window.ethereum) {
        throw new Error('Web3 provider not found')
      }

      const provider = new ethers.providers.Web3Provider(window.ethereum)
      await provider.send('eth_requestAccounts', [])
      const signer = provider.getSigner()
      const contract = new ethers.Contract(contractAddress, contractABI, signer)

      const publicKeyBase64 = btoa(keyPair.publicKey)
      const tx = await contract.submitPublicKey(publicKeyBase64)
      await tx.wait()
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred'
      setError('Error sending public key: ' + errorMessage)
    }
  }

  const retrieveAndDecrypt = async () => {
    try {
      if (!keyPair) {
        throw new Error('Please generate a key pair first')
      }

      const provider = new ethers.providers.Web3Provider(window.ethereum)
      const contract = new ethers.Contract(contractAddress, contractABI, provider)
      
      const encryptedData = await contract.retrieveDetails()
      setRetrievedData(encryptedData)

      const encryptedBytes = Uint8Array.from(atob(encryptedData), c => c.charCodeAt(0))

      const privateKeyDER = atob(keyPair.privateKey.replace(/-----BEGIN PRIVATE KEY-----|\n|-----END PRIVATE KEY-----/g, ''))
      const privateKeyBytes = Uint8Array.from(privateKeyDER, c => c.charCodeAt(0))
      const privateKey = await window.crypto.subtle.importKey(
        "pkcs8",
        privateKeyBytes,
        {
          name: "RSA-OAEP",
          hash: "SHA-256",
        },
        true,
        ["decrypt"]
      )

      const decryptedBytes = await window.crypto.subtle.decrypt(
        {
          name: "RSA-OAEP"
        },
        privateKey,
        encryptedBytes
      )

      const decryptedText = new TextDecoder().decode(decryptedBytes)
      setDecryptedData(decryptedText)
    } catch (err: any) {
      setError('Error retrieving/decrypting data: ' + err.message)
    }
  }

  const connectToSocket = (socketData: any) => {
    try {
      const { socket_server_url, socket_room } = socketData
      
      // Disconnect existing socket if any
      if (socket) {
        socket.disconnect()
      }

      // Create new socket connection
      const newSocket = io(socket_server_url, {
        path: '/socket.io'
      })

      // Set up socket event listeners
      newSocket.on('connect', () => {
        console.log('Connected to deployment socket')
        // Join the specific room
        newSocket.emit('join', socket_room)
      })

      newSocket.on('joined', (data: any) => {
        console.log('Successfully joined room:', data)
      })

      newSocket.on('deployment_update_client', (data) => {
        console.log('Deployment update:', data);
        setDeploymentStatus(prev => ({
          ...prev,
          status: 'deploying'
        }));
      });

      newSocket.on('deployment_complete_client', ([eventName, data]: [string, any]) => {
        console.log('Deployment complete:', data);
        setDeploymentStatus({
          status: 'completed',
          enclaveDetails: data.enclave
        });
      });

      setDeploymentStatus({ status: 'deploying' });
      setSocket(newSocket);
    } catch (error) {
      console.error('Error connecting to socket:', error)
      setError('Failed to connect to deployment socket')
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
              <Button 
                onClick={handleGenerateKeyPair} 
                className="bg-blue-500 text-white"
                disabled={isLoading || keyPair !== null}
              >
                {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Generate Key Pair
              </Button>

              {keyPair && (
                <>
                  <div className="mt-4 space-y-2">
                    <h3 className="font-bold">Generated Keys:</h3>
                    <div className="bg-gray-100 p-2 rounded text-xs">
                      <p className="break-all">Public Key: {keyPair.publicKey}</p>
                      <p className="break-all">Private Key: {keyPair.privateKey}</p>
                    </div>
                  </div>

                  <Button 
                    onClick={requestEnclaveCreation} 
                    className="bg-green-500 text-white"
                    disabled={isLoading}
                  >
                    {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                    Create Data Clean Room
                  </Button>
                </>
              )}

              {requestId && (
                <div className="space-y-2">
                  <p className="text-sm font-medium">Latest Request ID:</p>
                  <p className="text-xs break-all bg-gray-100 p-2 rounded">{requestId}</p>
                  <Button 
                    onClick={() => getEnclaveDetails(requestId)} 
                    disabled={isLoading}
                    className="w-full"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Fetching Details...
                      </>
                    ) : (
                      'Get Enclave Details'
                    )}
                  </Button>
                  <p className="text-xs text-gray-500">
                    Note: It may take a few moments for the enclave details to be available after creation
                  </p>
                </div>
              )}

              {userRequests.length > 0 && (
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold">Your Data Clean Rooms:</h3>
                  <div className="max-h-40 overflow-y-auto space-y-2">
                    {userRequests.map((req, index) => (
                      <div key={index} className="bg-gray-100 p-2 rounded">
                        <p className="text-xs break-all mb-2">{req}</p>
                        <Button 
                          onClick={() => getEnclaveDetails(req)} 
                          disabled={isLoading} 
                          size="sm"
                          className="w-full"
                        >
                          View Details
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {retrievedData && (
                <div className="space-y-2">
                  <h3 className="font-bold">Retrieved Encrypted Data:</h3>
                  <p className="text-xs break-all bg-gray-100 p-2 rounded">{retrievedData}</p>
                </div>
              )}

              {decryptedData && (
                <div className="space-y-2">
                  <h3 className="font-bold">Decrypted Data:</h3>
                  <p className="text-xs break-all bg-gray-100 p-2 rounded">{decryptedData}</p>
                </div>
              )}

              {decryptedData && (
                <div className="space-y-4 mt-4">
                  <h3 className="font-bold">Enclave Deployment Status:</h3>
                  
                  {deploymentStatus.status === 'deploying' && (
                    <div className="bg-yellow-50 p-4 rounded-md">
                      <div className="flex items-center space-x-3">
                        <Loader2 className="h-6 w-6 animate-spin text-yellow-500" />
                        <p className="text-sm text-yellow-700">Enclave deployment in progress...</p>
                      </div>
                    </div>
                  )}

                  {deploymentStatus.status === 'completed' && deploymentStatus.enclaveDetails && (
                    <div className="bg-green-50 p-4 rounded-md space-y-3">
                      <div className="flex items-center space-x-2">
                        <div className="h-2 w-2 rounded-full bg-green-500" />
                        <p className="text-sm font-medium text-green-800">
                          Enclave Deployment Completed
                        </p>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="grid grid-cols-3 gap-2 text-sm">
                          <div className="col-span-1 font-medium">Name:</div>
                          <div className="col-span-2 font-mono text-xs">
                            {deploymentStatus.enclaveDetails.name}
                          </div>
                          
                          <div className="col-span-1 font-medium">Domain:</div>
                          <div className="col-span-2 font-mono text-xs break-all">
                            {deploymentStatus.enclaveDetails.domain}
                          </div>
                          
                          <div className="col-span-1 font-medium">UUID:</div>
                          <div className="col-span-2 font-mono text-xs">
                            {deploymentStatus.enclaveDetails.uuid}
                          </div>
                        </div>

                        <div className="mt-3">
                          <p className="text-sm font-medium mb-2">PCR Values:</p>
                          <div className="bg-white bg-opacity-50 p-2 rounded space-y-1">
                            {Object.entries(deploymentStatus.enclaveDetails.pcrs).map(([key, value]) => (
                              <div key={key} className="grid grid-cols-4 gap-2 text-xs">
                                <div className="font-medium">{key}:</div>
                                <div className="col-span-3 font-mono break-all">{value}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </CardContent>
      <CardFooter className="flex flex-col gap-4">
        {error && (
          <Alert variant="destructive" className="w-full">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        {account && (
          <p className="text-sm w-full text-center">
            Connected: {account.slice(0, 6)}...{account.slice(-4)}
          </p>
        )}
      </CardFooter>
    </Card>
  )
}

function chunk(str: string, size: number): string[] {
  const chunks: string[] = [];
  for (let i = 0; i < str.length; i += size) {
    chunks.push(str.slice(i, i + size));
  }
  return chunks;
}

