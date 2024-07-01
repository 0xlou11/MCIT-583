import requests
import json

#API Key: 48a344fca70329f949bf
#API Secret: 638c93aed44c93008100f32dd6f006f0181e4137e60ef500b85c6871976df5a3
#JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiJjOTM1MjQyZi1lNjY4LTQ2NjgtYjE2OS00ZTRkM2MyYzdhNTEiLCJlbWFpbCI6ImxvdXh1YW55aUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicGluX3BvbGljeSI6eyJyZWdpb25zIjpbeyJkZXNpcmVkUmVwbGljYXRpb25Db3VudCI6MSwiaWQiOiJGUkExIn0seyJkZXNpcmVkUmVwbGljYXRpb25Db3VudCI6MSwiaWQiOiJOWUMxIn1dLCJ2ZXJzaW9uIjoxfSwibWZhX2VuYWJsZWQiOmZhbHNlLCJzdGF0dXMiOiJBQ1RJVkUifSwiYXV0aGVudGljYXRpb25UeXBlIjoic2NvcGVkS2V5Iiwic2NvcGVkS2V5S2V5IjoiNDhhMzQ0ZmNhNzAzMjlmOTQ5YmYiLCJzY29wZWRLZXlTZWNyZXQiOiI2MzhjOTNhZWQ0NGM5MzAwODEwMGYzMmRkNmYwMDZmMDE4MWU0MTM3ZTYwZWY1MDBiODVjNjg3MTk3NmRmNWEzIiwiZXhwIjoxNzUxMzQyOTkyfQ.eFpPSS3-ctvP6m53-K3Y7qdP9A5tb-3s-39KedAZP1M
PINATA_API_URL = "https://api.pinata.cloud"

def pin_to_ipfs(data):
	assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	#YOUR CODE HERE
	json_data = json.dumps(data)
	files = {'file': ('data.json', json_data)}
  response = requests.post(f"{IPFS_API_URL}/add", files=files)
	if response.status_code == 200:
        res_json = response.json()
        cid = res_json['Hash']
        return cid
    else:
        raise Exception(f"Error pinning to IPFS: {response.content}")

	return cid

def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE	
	response = requests.get(f"{IPFS_API_URL}/cat?arg={cid}")
    
    if response.status_code == 200:
        json_data = response.text      
				data = json.loads(json_data)
				assert isinstance(data,dict), f"get_from_ipfs should return a dict"
				return data

    else:
        raise Exception(f"Error getting data from IPFS: {response.content}")

