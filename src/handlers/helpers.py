from fastapi import Request, HTTPException
import base64
import json

def extract_authorization_token_from_headers(authorization: str):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    # Split the 'Authorization' header to get the scheme and token
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Authorization scheme must be Bearer")
        
        return extract_payload_from_token(token)

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

def decode_base64url(base64url_str):
    # Make the string Base64 compatible by replacing characters
    base64_str = base64url_str.replace('-', '+').replace('_', '/')
    
    # Ensure the string length is a multiple of 4 by padding with '='
    padding = '=' * (4 - len(base64_str) % 4)
    base64_str += padding

    # Decode Base64 and return the result
    return base64.b64decode(base64_str)

def extract_payload_from_token(token: str):
    # Split the JWT into its three parts
    parts = token.split('.')

    if len(parts) != 3:
        raise ValueError("Invalid token format")

    # The second part is the payload
    payload_base64 = parts[1]

    # Decode the payload from Base64 URL encoding
    payload_json = decode_base64url(payload_base64)

    # Parse the payload (JSON) into a dictionary
    payload = json.loads(payload_json)
    
    return payload