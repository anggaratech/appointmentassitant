from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import json
import hashlib
import hmac

from config.settings import settings
from utils.whatsapp_utils import (
    process_whatsapp_message,
    is_valid_whatsapp_message,
)

VERIFY_TOKEN = settings.VERIFY_TOKEN

class WhatsAppWebhookPayload(BaseModel):
    entry: list

class WebhookServices:

    async def verify(self, request: Request):
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")

        # Check if a token and mode were sent
        if mode and token:
            # Check the mode and token sent are correct
            if mode == "subscribe" and token == VERIFY_TOKEN:
                # Respond with 200 OK and challenge token from the request
                logging.info("WEBHOOK_VERIFIED")
                return JSONResponse(content=challenge, status_code=200)
            else:
                # Responds with '403 Forbidden' if verify tokens do not match
                logging.info("VERIFICATION_FAILED")
                raise HTTPException(status_code=403, detail="Verification failed")
        else:
            # Responds with '400 Bad Request' if verify tokens do not match
            logging.info("MISSING_PARAMETER")
            raise HTTPException(status_code=400, detail="Missing parameters")

    async def handle_message(self, request: Request):
        body = await request.json()
        if (
                body.get("entry", [{}])[0]
                        .get("changes", [{}])[0]
                        .get("value", {})
                        .get("statuses")
        ):
            logging.info("Received a WhatsApp status update.")
            return JSONResponse(content={"status": "ok"}, status_code=200)

        try:
            if await is_valid_whatsapp_message(body):
                await process_whatsapp_message(body, settings)
                return JSONResponse(content={"status": "ok"}, status_code=200)
            else:
                # if the request is not a WhatsApp API event, return an error
                return JSONResponse(content={"status": "error", "message": "Not a WhatsApp API event"}, status_code=404)
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON")
            return JSONResponse(content={"status": "error", "message": "Invalid JSON provided"}, status_code=400)
