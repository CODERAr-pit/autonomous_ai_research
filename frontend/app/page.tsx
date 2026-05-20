'use client'
import { useState } from "react";

interface ResponseData {
  status?: string;
  goal?: string;
  message?: string;
}

export default function Home() {
const [response, setResponse] = useState<ResponseData>({});
async function handleclick() {
  const response =await fetch('http://127.0.0.1:8000/run-agent',{
    method:'POST',
    headers:{
      'content-type':'application/json'
    },
    body:JSON.stringify({"goal":"Write a poem on the topic of AI"})
    })
    const data = await response.json()
    setResponse(data);

  }
  return (
    <div>
      <h1 className="text-3xl font-bold underline">Welcome To AI World</h1>
      <div className='button bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded' onClick={handleclick}>
        Go
      </div>
      {response?<div>
        <h2 className="text-2xl font-bold">Response:</h2>
        <p>{response.message}</p>
      </div>:null}
    </div>
  );
}