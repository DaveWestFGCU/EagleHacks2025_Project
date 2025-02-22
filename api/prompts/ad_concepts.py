prompt_text = '''
            Generate 3 ad concepts based on the following criteria:

            Product/Service Overview: <product>
            Target Audience: <audience>
            Campaign Goal: <goal>

            Return the response in the following JSON format:

            {
                "ads": [
                    {
                        "title": "Ad Concept 1 Title",
                        "description": "Brief description of Ad Concept 1",
                        "key_message": "Main takeaway of Ad Concept 1",
                        "image": "Description of an image to be used for Ad Concept 1"
                    },
                    {
                        "title": "Ad Concept 2 Title",
                        "description": "Brief description of Ad Concept 2",
                        "key_message": "Main takeaway of Ad Concept 2",
                        "image": "Description of an image to be used for Ad Concept 2"
                    },
                    {
                        "title": "Ad Concept 3 Title",
                        "description": "Brief description of Ad Concept 3",
                        "key_message": "Main takeaway of Ad Concept 3",
                        "image": "Description of an image to be used for Ad Concept 3"
                    }
                ]
            }
        '''