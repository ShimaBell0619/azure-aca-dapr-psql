from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import os

app = FastAPI(title="Dapr State Management Demo")

# Dapr設定
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_STATE_STORE = "state_store_psql"
DAPR_URL = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{DAPR_STATE_STORE}"


class Item(BaseModel):
    key: str
    value: str


@app.get("/")
def read_root():
    return {
        "message": "Dapr State Management API with PostgreSQL",
        "endpoints": {
            "health": "/health",
            "save": "POST /state",
            "get": "GET /state/{key}",
            "delete": "DELETE /state/{key}",
            "list": "GET /states"
        }
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/state")
def save_state(item: Item):
    """状態をDapr経由でPostgreSQLに保存"""
    try:
        state_data = [
            {
                "key": item.key,
                "value": item.value
            }
        ]
        
        response = requests.post(
            DAPR_URL,
            json=state_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201, 204]:
            return {
                "message": "State saved successfully",
                "key": item.key,
                "value": item.value
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to save state: {response.text}"
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with Dapr: {str(e)}"
        )


@app.get("/state/{key}")
def get_state(key: str):
    """Dapr経由でPostgreSQLから状態を取得"""
    try:
        response = requests.get(
            f"{DAPR_URL}/{key}",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            value = response.text.strip('"') if response.text else None
            if value:
                return {
                    "key": key,
                    "value": value
                }
            else:
                raise HTTPException(status_code=404, detail="Key not found")
        elif response.status_code == 204:
            raise HTTPException(status_code=404, detail="Key not found")
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to get state: {response.text}"
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with Dapr: {str(e)}"
        )


@app.delete("/state/{key}")
def delete_state(key: str):
    """Dapr経由でPostgreSQLから状態を削除"""
    try:
        response = requests.delete(
            f"{DAPR_URL}/{key}",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 204]:
            return {
                "message": "State deleted successfully",
                "key": key
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to delete state: {response.text}"
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with Dapr: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
