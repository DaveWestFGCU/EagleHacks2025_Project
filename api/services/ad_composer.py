from PIL import Image, ImageDraw, ImageFont


def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        candidate = word if not current_line else current_line + " " + word
        bbox = draw.textbbox((0, 0), candidate, font=font)
        candidate_width = bbox[2] - bbox[0]
        if candidate_width <= max_width:
            current_line = candidate
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def draw_bold_text(draw, position, text, font, fill, boldness=0):
    """
    Draws text with a simulated bold effect.
    If boldness is 0, the text is drawn only once.
    Otherwise, for boldness=1, draws the text at every offset in the grid:
    (-1, -1) to (1, 1) resulting in 9 draws.
    """
    x, y = position
    if boldness == 0:
        draw.text((x, y), text, font=font, fill=fill)
    else:
        for dx in range(-boldness, boldness+1):
            for dy in range(-boldness, boldness+1):
                draw.text((x+dx, y+dy), text, font=font, fill=fill)


def draw_custom_bold_text(draw, position, text, font, fill, offsets):
    """
    Draws text at the given offsets to simulate a custom bold effect.
    """
    x, y = position
    for dx, dy in offsets:
        draw.text((x+dx, y+dy), text, font=font, fill=fill)


color_values = {
    'red':    '#C70000',
    'orange': '#FF5733',
    'yellow': '#FFC300',
    'green':  '#33C700',
    'blue':   '#00AAC7',
    'purple': '#9339FA',
    'pink':   '#FA39F6',
    'black':  '#747474',
    'white':  '#D6D6D6'
}


class AdComposer:
    def __init__(self, campaign):
        self.image_filepath = campaign['ad_filepath']
        self.color_value = color_values[campaign['mood']['color']]
        self.headline_text = campaign['copy']['headline']
        self.body_text = campaign['copy']['body_text']
        self.call_to_action_text = campaign['copy']['call_to_action']


    def compose_advertisement(self):
        original = Image.open(self.image_filepath)
        # Assume that `original` has already been defined earlier in the program.
        width, height = original.size

        # Create a new image with an extra 600 pixels on the left filled with black
        new_width = width + 600
        new_image = Image.new("RGB", (new_width, height), "black")
        new_image.paste(original, (600, 0))
        draw = ImageDraw.Draw(new_image)

        # --- Color the Bottom 20% of the Left Bar with a Slightly Darker Yellow ---
        yellow_start = int(height * 0.8)
        draw.rectangle([(0, yellow_start), (600, height)], fill=self.color_value)

        # --- Headline Text Block ---
        try:
            headline_font = ImageFont.truetype("arialbd.ttf", 50)  # Bold, blocky font for headline
        except IOError:
            headline_font = ImageFont.load_default()

        horizontal_padding = 50
        effective_width = 600 - 2 * horizontal_padding  # Padded width for text wrapping

        # Wrap headline text
        headline_lines = wrap_text(self.headline_text, headline_font, effective_width, draw)

        # Calculate total height for the headline block (with 20 pixels between lines)
        headline_line_heights = []
        for line in headline_lines:
            bbox = draw.textbbox((0, 0), line, font=headline_font)
            headline_line_heights.append(bbox[3] - bbox[1])
        headline_spacing = 20
        total_headline_height = sum(headline_line_heights) + headline_spacing * (len(headline_lines) - 1)

        # Position the headline block so its vertical center is at 5/24 of the image height
        new_center = int(height * 5/24)
        headline_start_y = new_center - (total_headline_height // 2)
        current_y = headline_start_y

        # Draw headline text with full bold effect (boldness=1) in dark yellow "#FFCC00"
        for i, line in enumerate(headline_lines):
            draw_bold_text(draw, (horizontal_padding, current_y), line, headline_font, fill=self.color_value, boldness=1)
            current_y += headline_line_heights[i] + headline_spacing

        # --- Body Text Block ---
        try:
            body_font = ImageFont.truetype("arial.ttf", 24)  # Regular font for body text
        except IOError:
            body_font = ImageFont.load_default()

        # Wrap body text using the same effective width
        body_lines = wrap_text(self.body_text, body_font, effective_width, draw)

        # Calculate total height for the body text block (with 16 pixels between lines)
        body_line_heights = []
        for line in body_lines:
            bbox = draw.textbbox((0, 0), line, font=body_font)
            body_line_heights.append(bbox[3] - bbox[1])
        body_spacing = 16
        total_body_height = sum(body_line_heights) + body_spacing * (len(body_lines) - 1)

        # Compute available vertical space for the body text block:
        # It is the space between the bottom of the headline block and the top of the yellow area.
        bottom_headline = headline_start_y + total_headline_height
        available_body_space = yellow_start - bottom_headline

        # Center the body text block in that available space
        body_start_y = bottom_headline + (available_body_space - total_body_height) // 2

        # Define custom offsets for a moderate bold effect for the body text
        custom_offsets = [(0, 0), (1, 0), (0, 1)]

        # Draw each line of the body text left-justified using the custom bold effect in white
        for i, line in enumerate(body_lines):
            draw_custom_bold_text(draw, (horizontal_padding, body_start_y), line, body_font, fill="white",
                                  offsets=custom_offsets)
            body_start_y += body_line_heights[i] + body_spacing

        # --- Call to Action (CTA) Block in the Yellow Box ---
        try:
            call_to_action_font = ImageFont.truetype("arialbd.ttf", 30)  # CTA font size set to 30
        except IOError:
            call_to_action_font = ImageFont.load_default()

        # Wrap the CTA text (if needed)
        cta_lines = wrap_text(self.call_to_action_text, call_to_action_font, effective_width, draw)

        # Calculate total height of the CTA block (with 10 pixels between lines)
        cta_line_heights = []
        for line in cta_lines:
            bbox = draw.textbbox((0, 0), line, font=call_to_action_font)
            cta_line_heights.append(bbox[3] - bbox[1])
        cta_spacing = 10
        total_cta_height = sum(cta_line_heights) + cta_spacing * (len(cta_lines) - 1)

        # Center the CTA block vertically within the yellow area
        yellow_height = height - yellow_start
        cta_start_y = yellow_start + (yellow_height - total_cta_height) // 2

        # Define custom offsets for the CTA text (using four draws for an intermediate bold effect)
        cta_custom_offsets = [(0, 0), (1, 0), (0, 1), (1, 1)]

        # Draw each line of the CTA text, centering it horizontally within the padded area in black
        for line in cta_lines:
            bbox = draw.textbbox((0, 0), line, font=call_to_action_font)
            line_width = bbox[2] - bbox[0]
            x = horizontal_padding + (effective_width - line_width) // 2
            draw_custom_bold_text(draw, (x, cta_start_y), line, call_to_action_font, fill="black",
                                  offsets=cta_custom_offsets)
            cta_start_y += (bbox[3] - bbox[1]) + cta_spacing

        # Save the final image
        new_image.save(self.image_filepath)
