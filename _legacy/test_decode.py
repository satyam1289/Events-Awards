
import base64
import requests

def try_decode(data):
    try:
        # Base64 padding
        padding = 4 - (len(data) % 4)
        if padding < 4:
            data += "=" * padding
        
        decoded = base64.b64decode(data).decode('latin-1', errors='ignore')
        print(f"Decoded: {decoded}")
    except:
        pass

# The part after /articles/
data = "CBMiigFBVV95cUxNSDBhREVyUE1wM0paLUdoa3cxUWVpZUJoUm43LVFFRW5WU3ZTbHlUX0V4LVdENjlOT2x2NUpTb3RpNmJpSXE3d2JrMzhnSHlmREJSTXExcEFDekJrSnBFb0pwZEdpVHZLMTcxOUFpZ0Z3eU9hQldyM2o5WWJONjd1QkhxQ2xJb05OaWc"
try_decode(data)
