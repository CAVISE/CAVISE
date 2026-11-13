"""Run the component API with a single Uvicorn worker."""

import logging

import uvicorn


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    uvicorn.run("api.main:app", host="0.0.0.0", port=8080, workers=1, reload=False)
