from fastapi import FastAPI

from app.api.leads import router as leads_router

app = FastAPI(title="leads-service")
app.include_router(leads_router)
