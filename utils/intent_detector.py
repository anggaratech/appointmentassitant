import openai

from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from config.settings import settings

class Intent_Detector():

    async def detect(self, sentence:str):
        chat_completion = ChatOpenAI(
            openai_api_key=settings.OPENAI_KEY,
            temperature=0.25,
            model="gpt-4-0125-preview"
        )
        prompt = f"""You're intent detector from a user inquiry from user input base on this intent knowledge about user intent.
user_input: \"{sentence}\" 

Intent Knowledge:

Appointment: This function will be used when the user discusses or requests an appointment, regardless of the topic, such as scheduling an appointment, cancellation, updating, or checking availability.

can you analyze the user intent? 
Is it related to these categories  Appointment ? if note related response with None.
Conclude in this format, Answer in this format: 
The user falls under the category of \"categories\". Because of \"your reasoning\"."""

        try:
            ai_response = chat_completion([SystemMessage(content=prompt)])

            response = str(ai_response.content)
            print(f"INTENT DETECTION: {response}")

            if 'Appointment' in response:
                return 'Appointment'
            else:
                return None

        except Exception as e:
            logger.error(f"ERROR detect intent: {e}")