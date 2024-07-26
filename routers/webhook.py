from fastapi import APIRouter, Request
from services.webhook import WebhookServices

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(request: Request):
    result = await WebhookServices().verify(request)
    return result

@router.post("/webhook")
async def handle_message_webhook(request: Request):
    result = await WebhookServices().handle_message(request)
    return result
