prompt = \
    '''
    Generate an ad concepts based on the following criteria:

    Product/Service Overview: <product>
    Target Audience: <audience>
    Campaign Goal: <goal>
    Associations: <association>

    Return the response in the following JSON format:
    {
        "title": "Ad Concept Title",
        "description": "Brief description of Ad Concept",
        "key_message": "Main takeaway of Ad Concept",
        "image": 
            {
                "details": "specific details of the Ad Concept product to showcase",
                "emotion": "emotion Ad Concept intends to envoke"
            }
    }
    '''