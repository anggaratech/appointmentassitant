from services import AppService
import openai
from config.settings import settings
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
import importlib
from utils.intent_detector import Intent_Detector
import random
from datetime import date
import json
from datetime import datetime
from flow.Appointment import Appointment

class OpenAIServices(AppService):
    async def get_message(self):
        chat_path = "utils/chat_story_palm.json"

        with open(chat_path, "r") as file:
            data = json.load(file)

        batch_messages = []
        for message in data["messages"]:
            role = message.get("role", "").lower()
            content = message.get("content", "")
            if role == "system":
                batch_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                batch_messages.append(AIMessage(content=content))
            elif role == "user":
                batch_messages.append(HumanMessage(content=content))

        return batch_messages

    async def conversation(self, sentence,wa_id, wa_name):
        """
            Azure OpenAI configuration, set all the config in .env file & consume by settings schema
        """
        openai.api_key = settings.OPENAI_KEY

        try:
            chat_completion = ChatOpenAI(
                openai_api_key=settings.OPENAI_KEY,
                temperature=0.25,
                model="gpt-4-0125-preview"
            )
            message = await self.get_message()

            chat_history_path = "utils/chat_history_palm.json"
            with open(chat_history_path, 'r') as file_history:
                existing_data = json.load(file_history)

            try:
                if existing_data["data"][f"{wa_id}"]:
                    wa_id = wa_id
            except Exception as e:
                existing_data['data'][f'{wa_id}'] = []

            history_message = await self.get_message()

            for history in existing_data["data"][f"{wa_id}"][-5:]:
                if history['question'] and history['answer']:
                    history_message.append(HumanMessage(content=history['question']))
                    history_message.append(AIMessage(content=history['answer']))

            CA_PROMPT = f"""pretend You are a chatbot user.
            Given previous chat chains and this follow up input, rephrase the Follow Up Input to be a standalone_user_input.
            Example : 
            - in previous message : "Saya mau booking atau janji temu buat Kamis, apakah masih tersedia? ", and in foolow up input : "gimana kalo di Jumat ?", so standalone_user_input may be : "Saya mau booking atau janji temu buat Jumat, apakah masih tersedia?"
            Don't clarify the question. 

            Follow_Up_Input: {sentence}\n
            standalone_user_input:"""

            history_message.append(SystemMessage(content=CA_PROMPT, ))
            ca_response = chat_completion(history_message)
            sentence = str(ca_response.content)

            print("CA PROMPT: " + str(ca_response.content))


            intent = await Intent_Detector().detect(sentence=sentence)
            if intent is not None:
                print("Func Call Knowledge")
                Base_Flow = globals()[intent]
                Selected_Flow = Base_Flow(wa_id= wa_id, wa_name=wa_name, sentence=sentence)

                internal_function = Selected_Flow.get_function_middleware()

                message.append(HumanMessage(content=sentence))
                ai_response = chat_completion(message, functions=internal_function)
            else:
                print("General Knowledge")
                message.append(HumanMessage(content=sentence))
                ai_response = chat_completion(message)

            response = ai_response.content


            if ai_response.additional_kwargs:
                fn_name = ai_response.additional_kwargs["function_call"]["name"]
                print(fn_name)
                function = getattr(Selected_Flow, fn_name)
                kwarg = json.loads(ai_response.additional_kwargs["function_call"]["arguments"])

                fc_result = await function(**kwarg) if kwarg else await function()

                print(fc_result)

                prompt =f"""
                Make the response : {fc_result} more human-readable
                """

                message.append(SystemMessage(content=prompt, ))
                ai_response = chat_completion(message)
                response = ai_response.content
                print("Response: " + response)

            if type(response) == list:
                for resps in response:
                    existing_data['data'][f'{wa_id}'].append({
                        "question": sentence,
                        "answer": resps
                    })
            else:
                existing_data['data'][f'{wa_id}'].append({
                    "question": sentence,
                    "answer": response
                })

            with open('utils/chat_history_palm.json', 'w') as file:
                json.dump(existing_data, file, indent=2)


            return response
        except Exception as e:
            print(e)
            response = "Mohon maaf saat ini kami kesulitan untuk mendapatkan informasi yang anda cari, silahkan tanyakan kembali beberapa saat lagi ! "
            return response