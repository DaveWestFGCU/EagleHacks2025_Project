import requests, asyncio, os, shutil, time
from openai import AsyncOpenAI, BadRequestError
import json


from api.api_key import OPENAI_API_KEY

from .logging_setup import create_logger, create_handler, remove_queue_handler

from api.prompts.mood import prompt as mood_prompt
from api.prompts.ad_concepts import prompt as ad_concept_prompt
from api.prompts.ad_text import prompt_text as ad_text_prompt
from api.prompts.ad_image import prompt_text as image_prompt

from .ad_composer import AdComposer


class AdGenerator:
    def __init__(self, job_id, product, audience, goal):
        self.id = job_id
        self.product = product
        self.audience = audience if audience not in ["", None] else 'everyone'
        self.goal = goal if goal not in ["", None] else 'awareness'
        self.status = 'new'
        self.text_model = 'gpt-4o-mini'
        self.image_model = 'dall-e-3'
        self.ad_campaigns = []
        self.image_locations = []

        os.makedirs(os.path.join('jobs',self.id), exist_ok=True)
        self.logger = create_logger(job_id)
        self.handler = create_handler(job_id)
        self.logger.info(f"Job created! ID : {self.id}")


    async def sim_run(self):
        self.status = 'processing'
        await asyncio.sleep(16)
        for i in range(3):
            self.ad_campaigns[i]['ad_filepath'] = f'static/sim/concept_{i}.png'
        self.status = 'done'


    async def run(self):
        start_time = time.time()
        self.status = 'processing'

        # Generating ad campaign moods
        self.ad_campaigns = await self.generate_ad_colors()

        # Generate ads in parallel
        task_list = [asyncio.create_task(self.generate_ad(i, campaign)) for i, campaign in enumerate(self.ad_campaigns)]
        await asyncio.gather(*task_list)

        # Once ads are generated, move them to a directory for client access
        await self.move_files_to_static()
        self.status = 'done'
        print(f'Job {self.id} completed in {round(time.time()-start_time,2)} seconds.')


    async def generate_ad_colors(self):
        prompt = mood_prompt.replace('<keyword>', self.product)
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
        colors=[
            {'color': 'red',    'association': 'excitement, passion, urgency, danger'},
            {'color': 'orange', 'association': 'warmth, energy, creativity'},
            {'color': 'yellow', 'association': 'optimism, happiness, caution'},
            {'color': 'green',  'association': 'nature, growth, health'},
            {'color': 'blue',   'association': 'trust, security, professionalism'},
            {'color': 'purple', 'association': 'luxury, sophistication, creativity'},
            {'color': 'pink',   'association': 'femininity, romance, sensitivity'},
            {'color': 'black',  'association': 'sophistication, power, mystery'},
            {'color': 'white',  'association': 'purity, simplicity, cleanliness'}
        ]

        ad_colors = []
        for i in range(9):
            if str(i) in completion.choices[0].message.content:
                ad_colors.append({'mood': colors[i]})

        return ad_colors


    async def generate_ad(self, i, campaign):
        campaign['concept'] = await self.generate_ad_concept(campaign)
        campaign['copy'] = await self.generate_ad_text(campaign)
        campaign['ad_filepath'] = await self.generate_image(i, campaign)
        AdComposer(campaign).compose_advertisement()


    async def generate_ad_concept(self, campaign):
        self.status = 'Processing'
        self.logger.info('Generating Ad-Concepts...')
        prompt = ad_concept_prompt
        replace_dict = {
            '<product>': self.product,
            '<audience>': self.audience,
            '<goal>': self.goal,
            '<association>': campaign['mood']['association']
        }

        for key, value in replace_dict.items():
            prompt = prompt.replace(key, value)

        self.logger.info("Request: {prompt}")

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

            self.logger.info(f"Response: {response_text}")

            json_match = response_text[response_text.find('{'):response_text.rfind('}')+1]
            if json_match:
                parsed_json = json.loads(json_match)  # Convert to Python dictionary
                return parsed_json

            else:
                raise Exception("No JSON block found in API response.")

        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
            raise


    async def generate_ad_text(self, campaign):
        self.logger.info("Generating Ad-Text...")

        prompt = ad_text_prompt
        replace_dict = {
            '<keyword>': self.product,
            '<title>': campaign['concept']['title'],
            '<description>': campaign['concept']['description'],
            '<key_message>': campaign['concept']['key_message'],
            '<association>': campaign['mood']['association']
        }

        for key, value in replace_dict.items():
            prompt = prompt.replace(key, value)

        self.logger.info("Request: {prompt}")

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

        self.logger.info(f"Response: {response_text}")

        ad_copy = {'headline': response_text[response_text.find('<headline>')+10 : response_text.rfind('</headline>')],
                   'body_text': response_text[response_text.find('<body_text>')+11 : response_text.rfind('</body_text>')],
                   'call_to_action': response_text[response_text.find('<call_to_action>')+16 : response_text.rfind('</call_to_action>')]}

        return ad_copy


    async def generate_image(self, concept_num, campaign):
        self.logger.info("Generating Image...")

        prompt = image_prompt
        replace_dict = {
            '<keyword>': self.product,
            '<audience>': self.audience,
            '<details>': campaign['concept']['image']['details'],
            '<emotion>': campaign['concept']['image']['emotion'],
            '<color>': campaign['mood']['color']
        }

        for key, value in replace_dict.items():
            prompt = prompt.replace(key, value)

        self.logger.info(f"Request: {prompt}")

        try:
            client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            response = await client.images.generate(
                model=self.image_model,
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )

        except BadRequestError as e:
            print(f"GUARD RAILS STRUCK: {self.id} : Concept {concept_num}: {prompt}")
            await asyncio.sleep(1)
            raise

        self.logger.info(f"Response: {response.data[0].url}")

        # Download image from OpenAI
        img_data = requests.get(response.data[0].url).content

        filepath = os.path.join('jobs',self.id,f'concept_{concept_num}.png')
        with open(filepath, 'wb') as handler:
            handler.write(img_data)

        return filepath


    async def move_files_to_static(self):
        self.logger.info("Moving Files to static folder.")
        await asyncio.sleep(1)  # Allow logs in queue to be logged before closing.
        self.logger.removeHandler(self.handler)
        del self.logger
        remove_queue_handler(self.handler)    # Close the file handler so the log can be moved.
        del self.handler


        os.makedirs(os.path.join('api','static'), exist_ok=True)
        shutil.move(f'jobs/{self.id}', f'api/static/{self.id}')
        for filename in os.listdir(os.path.join('api', 'static', self.id)):
            if filename.lower().endswith(".png"):
                self.image_locations.append(os.path.join('static', self.id, filename).replace('\\', '/'))
