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
                        "image": 
                            {
                                "details": "specific details of the Ad Concept 1 product to showcase",
                                "emotion": "emotion Ad Concept 1 intends to envoke"
                            }
                    },
                    {
                        "title": "Ad Concept 2 Title",
                        "description": "Brief description of Ad Concept 2",
                        "key_message": "Main takeaway of Ad Concept 2",
                        "image": 
                            {
                                "details": "specific details of the Ad Concept 2 product to showcase",
                                "emotion": "emotion Ad Concept 2 intends to envoke"
                            }
                    },
                    {
                        "title": "Ad Concept 3 Title",
                        "description": "Brief description of Ad Concept 3",
                        "key_message": "Main takeaway of Ad Concept 3",
                        "image": 
                            {
                                "details": "specific details of the Ad Concept 3 product to showcase",
                                "emotion": "emotion Ad Concept 3 intends to envoke"
                            }
                    }
                ]
            }
        '''