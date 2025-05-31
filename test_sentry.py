from fastapi import FastAPI
import sentry_sdk
from fastapi.testclient import TestClient

sentry_sdk.init(
    dsn="https://7f82a47c7229433750c1840f66a5ee8a@o4509418510024704.ingest.us.sentry.io/4509418515398656",
    send_default_pii=True,
)

app = FastAPI()

@app.get("/sentry-test-error")
def sentry_test_error():
    # This will raise an error and send it to Sentry
    raise RuntimeError("Sentry test error!")

# For local test run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8010, reload=True)

# For pytest or script test
client = TestClient(app)
def test_sentry_error():
    response = client.get("/sentry-test-error")
    assert response.status_code == 500

# NOTE: To test Sentry on Render, add the following endpoint to your main FastAPI app:
# @app.get("/sentry-test-error")
# def sentry_test_error():
#     raise RuntimeError("Sentry test error!")
# Then deploy and visit /sentry-test-error on your Render URL.
