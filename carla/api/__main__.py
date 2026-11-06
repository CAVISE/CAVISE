"""Run the component API with a single Uvicorn worker."""

import uvicorn


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8080, workers=1, reload=False)
