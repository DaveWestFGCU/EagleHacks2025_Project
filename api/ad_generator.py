
import requests, asyncio, os, shutil
import ollama
from openai import AsyncOpenAI
import json, re
from PIL import Image, ImageDraw, ImageFont

from .prompts.ad_concepts import prompt_text as ad_concept_prompt
from .prompts.ad_text import prompt_text as ad_text_prompt
from .prompts.image_generation import prompt_text as image_prompt

from .api_key import OPENAI_API_KEY

class AdGenerator:
    def __init__(self, job_id, product, audience, goal):
        self.id = job_id
        self.product = product
        self.audience = audience
        self.goal = goal
        self.status = 'new'
        self.text_model = 'gpt-4o-mini'
        self.image_model = 'dall-e-3'
        self.concept0 = {}


    async def run(self):
        self.status = 'processing'
        successful = False
        while not successful:
            try:
                ad_concepts = await self.generate_ad_concepts()
            except Exception as e:
                print(e)
            else:
                successful = True

        # for i, concept in enumerate(ad_concepts):  ## TODO: Remove index
        i = 0
        await self.generate_ad_text(ad_concepts[i])
        await self.generate_image(i, ad_concepts[i])
        await self.add_text_to_image(i, ad_concepts[i])

        self.move_files_to_static(i)
        self.status = "done"


    async def generate_ad_concepts(self):
        self.status = 'Processing'
        prompt = ad_concept_prompt
        replace_dict = {'<product>': self.product, '<audience>': self.audience, '<goal>': self.goal}
        for key, value in replace_dict.items():
            prompt = prompt.replace(key, value)

        successful = False
        while not successful:
            client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            completion = await client.chat.completions.create(
                model=self.text_model,
                messages =[
                    {
                        "role": "user",
                        "content": prompt
                     }
                ]
            )

            try:
                response_text = completion.choices[0].message.content
                json_match = response_text[response_text.find('{'):response_text.rfind('}')+1]
                if json_match:
                    parsed_json = json.loads(json_match)  # Convert to Python dictionary

                    print(parsed_json.get("ads", []))

                    return parsed_json.get("ads", [])  # Return just the ads array

                else:
                    raise Exception("No JSON block found in API response.")

            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {e}")
                raise


    async def generate_image(self, concept_num, image_concept):
        prompt = image_prompt.replace('<product>', self.product).replace('<audience>', self.audience).replace('<details>', image_concept['image']['details']).replace('<description>', image_concept['description']).replace('<emotion>', image_concept['image']['emotion'])
        print(prompt)
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        response = await client.images.generate(
            model=self.image_model,
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        print(response.data[0].url)

        # Download image from OpenAI
        img_data = requests.get(response.data[0].url).content
        os.makedirs('jobs', exist_ok=True)
        os.makedirs(f'jobs/{self.id}', exist_ok=True)

        with open(f'jobs/{self.id}/concept_{concept_num}.png', 'wb') as handler:  # TODO: Implement different file names for more than 1 image
            handler.write(img_data)


    async def generate_ad_text(self, ad_concept):
        prompt = ad_text_prompt.replace('<keyword>', self.product).replace('<title>', ad_concept['title']).replace('<description>',ad_concept['description']).replace('<key_message>',ad_concept['key_message'])
        print()
        print(prompt)
        print()
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        completion = await client.chat.completions.create(
            model=self.text_model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = completion.choices[0].message.content
        ad_copy = {'headline': response_text[response_text.find('<headline>')+10:response_text.rfind('</headline>')]}
        print(ad_copy['headline'])
        ad_copy['body_text'] = response_text[response_text.find('<body_text>')+11:response_text.rfind('</body_text>')]
        print(ad_copy['body_text'])
        ad_copy['call_to_action'] = response_text[response_text.find('<call_to_action>')+16:response_text.rfind('</call_to_action>')]
        print(ad_copy['call_to_action'])

        ad_concept['copy'] = ad_copy


    async def add_text_to_image(self, concept_num, ad_concept):
        img = Image.open(f"./jobs/{self.id}/concept_{concept_num}.png")  # Load the image file

        # Create an ImageDraw object
        draw = ImageDraw.Draw(img)

        # Define the text and its properties
        text = ad_concept['copy']['headline']
        font = ImageFont.truetype("arial.ttf", size=30)

        # Calculate text bounding box (left, top, right, bottom)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

        # Center the text
        x = (img.width - text_width) / 2
        y = 50

        # Define shadow offset
        shadow_offset = 2

        # Draw the drop shadow (black text, slightly offset)
        draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill="black")

        # Draw the main text (white text, centered)
        draw.text((x, y), text, font=font, fill="white")

        # Save the edited image
        img.save(f"./jobs/{self.id}/concept_{concept_num}.png")
        print("done")


    def move_files_to_static(self, concept_num):
        os.makedirs(os.path.join('api','static'), exist_ok=True)
        shutil.move(f'jobs/{self.id}', f'api/static/{self.id}')
        self.concept0['url'] = os.path.join('static', self.id, f'concept_{concept_num}.png')
