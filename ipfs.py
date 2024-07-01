import requests
import json

PINATA_API_KEY = "48a344fca70329f949bf"
PINATA_SECRET_API_KEY = "638c93aed44c93008100f32dd6f006f0181e4137e60ef500b85c6871976df5a3"
#JWT: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiJjOTM1MjQyZi1lNjY4LTQ2NjgtYjE2OS00ZTRkM2MyYzdhNTEiLCJlbWFpbCI6ImxvdXh1YW55aUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicGluX3BvbGljeSI6eyJyZWdpb25zIjpbeyJkZXNpcmVkUmVwbGljYXRpb25Db3VudCI6MSwiaWQiOiJGUkExIn0seyJkZXNpcmVkUmVwbGljYXRpb25Db3VudCI6MSwiaWQiOiJOWUMxIn1dLCJ2ZXJzaW9uIjoxfSwibWZhX2VuYWJsZWQiOmZhbHNlLCJzdGF0dXMiOiJBQ1RJVkUifSwiYXV0aGVudGljYXRpb25UeXBlIjoic2NvcGVkS2V5Iiwic2NvcGVkS2V5S2V5IjoiNDhhMzQ0ZmNhNzAzMjlmOTQ5YmYiLCJzY29wZWRLZXlTZWNyZXQiOiI2MzhjOTNhZWQ0NGM5MzAwODEwMGYzMmRkNmYwMDZmMDE4MWU0MTM3ZTYwZWY1MDBiODVjNjg3MTk3NmRmNWEzIiwiZXhwIjoxNzUxMzQyOTkyfQ.eFpPSS3-ctvP6m53-K3Y7qdP9A5tb-3s-39KedAZP1M'
PINATA_API_URL = "https://api.pinata.cloud"

def pin_to_ipfs(data):
	assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	#YOUR CODE HERE
	json_data = json.dumps(data)
	files = {'file': ('data.json', json_data)}
	headers = {
        'pinata_api_key': PINATA_API_KEY,
        'pinata_secret_api_key': PINATA_SECRET_API_KEY
    }
	payload = {
        'pinataContent': data,
    }

  response = requests.post(f"{PINATA_API_URL}/Pinning/pinJSONToIPFS", headers=headers, json=payload)
	if response.status_code == 200:
        res_json = response.json()
        cid = res_json['IpfsHash']
        return cid
    else:
        raise Exception(f"Error pinning to IPFS: {response.content}")

def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE	
	response = requests.get(f"https://gateway.pinata.cloud/ipfs/{cid}")
    
  if response.status_code == 200:
        json_data = response.text
				data = json.loads(json_data)
				assert isinstance(data, dict), f"Error: get_from_ipfs should return a dict"
				return data

    else:
        raise Exception(f"Error getting data from IPFS: {response.content}")

