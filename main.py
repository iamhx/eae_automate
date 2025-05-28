from PIL import Image, ImageDraw, ImageFont
import os
import html
import sys
import time

# Define constants for input/output and asset paths
INPUT_IMAGE = ""
DEFAULT_IMAGE = "input/default.png"

# Generate output image with timestamp
timestamp = int(time.time())
OUTPUT_IMAGE = f"output/image_{timestamp}.png"

MASCOT_PATH = "assets/mascot.png"
FONT_PATH = "assets/font.ttf"

# Define layout ratios and style constants
FONT_SIZE_RATIO = 0.0375
MASCOT_SIZE_RATIO = 0.2


LEFT_GAP_RATIO = 0.01  
CHAT_BG_RGBA = (190, 226, 236, int(255 * 0.9))  # #bee2ec
MIN_PADDING = 10
MIN_GAP = 10
MIN_BOTTOM_MARGIN = 25

CORNER_RADIUS = 20
USER_CHAT_BG_RGBA = (252, 232, 178, int(255 * 0.8))  # #fce8b2

MASCOT_MAX_HEIGHT_RATIO = 0.35
USER_MAX_HEIGHT_RATIO = 0.25

# Helper function to find the largest font size that fits within a given area
def find_fitting_font(draw, text, font_path, max_width, max_height, max_font_size):
    for size in range(max_font_size, 5, -1):
        font = ImageFont.truetype(font_path, size)
        lines = wrap_text(text, font, max_width, draw)
        line_height = font.getbbox("Ay")[3] - font.getbbox("Ay")[1]
        total_height = line_height * len(lines)

        if total_height <= max_height:
            max_line_width = max(draw.textlength(line, font=font) for line in lines)
            if max_line_width <= max_width:
                return font, lines

    # Fallback if no suitable size is found
    font = ImageFont.truetype(font_path, 5)
    return font, wrap_text(text, font, max_width, draw)

# Resize image while maintaining aspect ratio
def resize_keep_aspect(img, target_width):
    w, h = img.size
    ratio = target_width / w
    return img.resize((int(w * ratio), int(h * ratio)))

# Wrap text to fit within specified width
def wrap_text(text, font, max_width, draw):
    lines = []
    words = text.split()
    line = ""

    for word in words:
        test_line = line + word + " "
        test_width = draw.textlength(test_line, font=font)

        if test_width <= max_width:
            line = test_line
        else:
            lines.append(line.strip())
            line = word + " "

    if line:
        lines.append(line.strip())

    return lines

# Main function to generate the image
def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <mascot_response_text> <user_message> [<image_path>]")
        sys.exit(1)

    TEXT = html.unescape(sys.argv[1]) # Mascot response
    USER_TEXT = html.unescape(sys.argv[2])  # User message

    # Determine which input image to use
    if len(sys.argv) > 3:
        candidate_image = sys.argv[3]
        if os.path.exists(candidate_image) and os.path.isfile(candidate_image):
            INPUT_IMAGE = candidate_image
        else:
            print(f"Warning: Image path '{candidate_image}' is invalid. Falling back to default.")
            INPUT_IMAGE = DEFAULT_IMAGE
    else:
        print("No image path provided. Using default image.")
        INPUT_IMAGE = DEFAULT_IMAGE

    # Load images and set base parameters
    base_img = Image.open(INPUT_IMAGE).convert("RGBA")
    mascot = Image.open(MASCOT_PATH).convert("RGBA")

    width, height = base_img.size

    bottom_margin = max(MIN_BOTTOM_MARGIN, int(height * 0.02))  
    gap_between_bubbles = max(MIN_GAP, int(height * 0.015)) 

    mascot_text_padding = max(MIN_PADDING, int(height * 0.015))
    user_padding_x = max(MIN_PADDING, int(width * 0.015))
    user_padding_y = max(MIN_PADDING, int(height * 0.015))

    mascot = resize_keep_aspect(mascot, int(width * MASCOT_SIZE_RATIO))

    # Position mascot image at the bottom left
    mascot_x = int(width * 0.025)
    mascot_y = height - mascot.height - int(height * 0.025)
    base_img.paste(mascot, (mascot_x, mascot_y), mascot)

    # For testing, override text inputs
    #USER_TEXT = ""
    #TEXT = ""

    overlay = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
    draw_overlay = ImageDraw.Draw(overlay)

    # Calculate layout and max dimensions for chat bubbles
    mascot_max_height = int(height * MASCOT_MAX_HEIGHT_RATIO)
    user_max_height = int(height * USER_MAX_HEIGHT_RATIO)

    mascot_available_max_height = min(height - mascot_y - bottom_margin, mascot_max_height)

    # Process mascot bubble text and position
    MAX_MASCOT_BUBBLE_WIDTH = int(width * 0.6)
    mascot_font, mascot_lines = find_fitting_font(
        draw_overlay, TEXT, FONT_PATH,
        MAX_MASCOT_BUBBLE_WIDTH,
        mascot_available_max_height,
        int(height * FONT_SIZE_RATIO)
    )
    mascot_line_height = mascot_font.getbbox("Ay")[3] - mascot_font.getbbox("Ay")[1]
    mascot_total_text_height = mascot_line_height * len(mascot_lines)
    mascot_max_line_width = max(draw_overlay.textlength(line, font=mascot_font) for line in mascot_lines)

    mascot_bubble_width = mascot_max_line_width + mascot_text_padding * 2
    mascot_bubble_height = mascot_total_text_height + mascot_text_padding * 2

    chat_left = mascot_x + mascot.width + int(width * LEFT_GAP_RATIO)
    chat_right = chat_left + mascot_bubble_width
    chat_center_y = mascot_y + mascot.height // 2
    chat_top = max(0, chat_center_y - mascot_bubble_height // 2)
    chat_bottom = chat_top + mascot_bubble_height

    # Process user bubble text and position
    user_available_max_height = min(
        chat_top - gap_between_bubbles - bottom_margin,
        user_max_height
    )

    MAX_USER_BUBBLE_WIDTH = int(width * 0.6)
    user_font, user_lines = find_fitting_font(
        draw_overlay, USER_TEXT, FONT_PATH,
        MAX_USER_BUBBLE_WIDTH,
        user_available_max_height,
        int(height * FONT_SIZE_RATIO)
    )

    user_line_height = user_font.getbbox("Ay")[3] - user_font.getbbox("Ay")[1]
    user_total_text_height = user_line_height * len(user_lines)
    user_max_line_width = max(draw_overlay.textlength(line, font=user_font) for line in user_lines)

    user_bubble_width = user_max_line_width + user_padding_x * 2
    user_bubble_height = user_total_text_height + user_padding_y * 2

    user_right = width - int(width * 0.035)
    user_left = user_right - user_bubble_width
    user_bottom = chat_top - gap_between_bubbles
    user_top = max(0, user_bottom - user_bubble_height)

    # Draw rounded rectangles for chat bubbles
    draw_overlay.rounded_rectangle([
        chat_left, chat_top, chat_right, chat_bottom
    ], radius=CORNER_RADIUS, fill=CHAT_BG_RGBA)

    draw_overlay.rounded_rectangle([
        user_left, user_top, user_right, user_bottom
    ], radius=CORNER_RADIUS, fill=USER_CHAT_BG_RGBA)

    # Composite overlay onto base image
    base_img = Image.alpha_composite(base_img, overlay)
    draw_base = ImageDraw.Draw(base_img)

    # Draw user text onto image
    user_start_y = user_top + user_padding_y
    for i, line in enumerate(user_lines):
        text_x = user_left + user_padding_x
        text_y = user_start_y + i * user_line_height
        draw_base.text((text_x, text_y), line, font=user_font, fill="black")

    # Draw mascot text onto image
    text_start_y = chat_top + mascot_text_padding
    for i, line in enumerate(mascot_lines):
        text_x = chat_left + mascot_text_padding
        text_y = text_start_y + i * mascot_line_height
        draw_base.text((text_x, text_y), line, font=mascot_font, fill="black")

    # Save the final image
    os.makedirs("output", exist_ok=True)
    base_img.save(OUTPUT_IMAGE)
    print(f"{OUTPUT_IMAGE}")


if __name__ == "__main__":
    main()
