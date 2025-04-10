prompt_text = \
"""Generate a short, attention grabbing headline, a few sentences of body text, and a punchy call to action for <keyword>. Each area must include \'<keyword>\' in its text.
The title for this ad campaign is <title>.
The concept for this ad campaign is <description>.
The main takeaway that we want to impart is <key_message>.
The mood for the ad is \'<association>\'.

Return the response in the following format:
<headline>Your Headline</headline>
<body_text>your body text</body_text>
<call_to_action>your call to action</call_to_action> 
"""