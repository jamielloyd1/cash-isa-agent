import os
import google.genai as genai


class GeminiClient:
    def __init__(self):
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            tools=[]
        )

    def set_tools(self, tools_schema):
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            tools=tools_schema
        )

    def chat(self, messages):
        response = self.model.generate_content(messages)
        return response
