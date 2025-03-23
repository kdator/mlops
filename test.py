import requests
import sys
import json

HTTP_SERVER = "http://localhost:8080/preprocess"
TRITON_URL = "http://localhost:8000/v2/models/{}/infer"


def preprocess(image: str):
    response = requests.post(HTTP_SERVER, files={"file": open(image, "rb")})
    
    if response.status_code == 200:
        return {"status": "success", "data": response.json()}
    else:
        return {"status": "error", "message": response.text}


def infer(preproccesed: str, model: str):
    data = {
        "inputs": [
            {
                "name": "input",
                "shape": [1, 1, 28, 28],
                "datatype": "FP32",
                "data": preproccesed
            }
        ]
    }
    
    response = requests.post(TRITON_URL.format(model), json=data)
    
    if response.status_code == 200:
        return {"status": "success", "data": response.json()}, response.status_code
    else:
        return {"status": "error", "message": response.text}, response.status_code

if __name__ == "__main__":
    image, model = sys.argv[1], sys.argv[2]

    data = preprocess(image)
    msg, code = infer(data["data"]["processed_image"], model)

    output = json.dumps(msg)
    if code == 200:
        sys.stdout.write(output + "\n")
    else:
        sys.stderr.write(output + "\n")

    sys.exit(bool(code))
