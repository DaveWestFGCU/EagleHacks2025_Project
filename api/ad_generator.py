
import requests, asyncio, os
import ollama
from openai import OpenAI
import json, re
from PIL import Image, ImageDraw, ImageFont

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

        # for i, concept in enumerate(ad_concepts):  ## TODO: Remove index
        i = 0
        await self.generate_image(i, ad_concepts[i])


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


    async def generate_image(self, concept_num, image_concept):
        prompt = image_prompt.replace('<product>', self.product).replace('<audience>', self.audience).replace('<details>', image_concept['image']['details']).replace('<description>', image_concept['description']).replace('<emotion>', image_concept['image']['emotion'])
        print(prompt)
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        response = client.images.generate(
            model="dall-e-3",
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


    async def add_text_to_image(self):
        image = Image.open("./api/input_image.jpg")  # replace with your image file
        # Alternatively, create a new image:
        # image = Image.new("RGB", (400, 300), color="white")

        # Create an ImageDraw object
        draw = ImageDraw.Draw(image)

        # Define the text and its properties
        text = "Hello, World!"
        position = (50, 50)  # (x, y) coordinates
        fill_color = (255, 0, 0)  # red color in RGB

        # Optionally, load a custom font
        # Make sure the font file is accessible, and adjust the size as needed.
        try:
            font = ImageFont.truetype("arial".ttf", size=40)
        except IOError:
            # Fallback to default font if the specified font is not available
            font = ImageFont.load_default(size=40)

        # Add text to the image
        draw.text(position, text, fill=fill_color, font=font)

        # Save the edited image
        image.save("output_image.jpg")

        # Optionally, display the image (for example, in a GUI environment)
        image.show()
