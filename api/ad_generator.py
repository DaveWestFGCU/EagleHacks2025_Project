
import asyncio, os
import ollama
from openai import OpenAI
import json, re

from .prompts.ad_concepts import prompt_text as ad_concept_prompt
from .prompts.image_generation import prompt_text as image_prompt

class AdGenerator:
    def __init__(self, job_id, product, audience, goal):
        self.id = job_id
        self.product = product
        self.audience = audience
        self.goal = goal
        self.status = 'New'


    async def run(self):
        successful = False
        while not successful:
            try:
                ad_concepts = await self.generate_ad_concepts()
            except Exception as e:
                print(e)
            else:
                successful = True

        for concept in ad_concepts:
            await self.generate_image(concept['image'])


    async def generate_ad_concepts(self):
        self.status = 'Processing'
        prompt = ad_concept_prompt
        replace_dict = {'<product>': self.product, '<audience>': self.audience, '<goal>': self.goal}
        for key, value in replace_dict.items():
            prompt = prompt.replace(key, value)

        successful = False
        while not successful:
            try:
                response = ollama.chat(
                    model='llama3.2',
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )

            except Exception as e:
                print(f"Ollama failed: {e}")

            try:
                response_text = response["message"]["content"]

                # Use regex to extract the JSON block inside triple backticks (```)
                json_match = re.search(r"```(.*?)```", response_text, re.DOTALL)

                if json_match:
                    json_str = json_match.group(1).strip()  # Extract JSON content
                    parsed_json = json.loads(json_str)  # Convert to Python dictionary

                    print(parsed_json.get("ads", []))

                    return parsed_json.get("ads", [])  # Return just the ads array

                else:
                    raise Exception("No JSON block found in API response.")

            except json.JSONDecodeError as e:
                raise



    async def generate_image(self, image_concept):
        print(image_concept
              )
        prompt = image_prompt.replace('<product>', image_concept['product']).replace('<audience>', image_concept['audience']).replace('<details>', image_concept['image']['details']).replace('<emotion>', image_concept['image']['emotion'])
        client = OpenAI(api_key=os.environ.get(')OPENAI_API_KEY'))
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        print(response.data[0].url)