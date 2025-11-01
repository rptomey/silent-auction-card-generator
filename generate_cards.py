import csv
import qrcode
import os
import json
from PIL import Image, ImageDraw, ImageFont

# --- SETUP ---
CSV_FILE = "auction_items.csv"
CONFIG_FILE = "template_config.json"
OUTPUT_DIR = "generated_cards"
QR_CODE_SIZE_PX = 300

with open(CONFIG_FILE, "r") as file:
    CONFIG = json.load(file)
# ---------------------

# https://dev.to/emiloju/wrap-and-render-multiline-text-on-images-using-pythons-pillow-library-2ppp
def wrap_text(text, font, max_width, draw):
    """
    Wraps text to fit within the max_width.
    """
    words = text.split()
    lines = [] # Holds each line in the text box
    current_line = [words[0]] # Holds the current line under evaluation.

    for word in words[1:]:
        # Check the width of the current line with the new word added
        test_line = ' '.join(current_line + [word])
        width = draw.textlength(test_line, font=font)
        if width <= max_width:
            current_line.append(word)
        else:
            # If the line is too wide, finalize the current line and start a new one
            lines.append(' '.join(current_line))
            current_line = [word]

    # Add the last line
    if current_line:
        lines.append(' '.join(current_line))

    return "\n".join(lines)

def create_card(item_name, starting_bid, auction_url, template_file):
    """Generates a single auction card."""
    
    print(f"Generating card for: {item_name}")

    try:
        # 1. Open the base template image
        base_image = Image.open(f"templates/{template_file}").convert("RGBA")
        draw = ImageDraw.Draw(base_image)

        # 2. Get the template-specific configuration
        template_config = CONFIG[template_file]
        font_file_item = f"fonts/{template_config["Item"]["Font"]}"
        font_size_item = template_config["Item"]["Size"]
        font_file_bid = f"fonts/{template_config["Bid"]["Font"]}"
        font_size_bid = template_config["Bid"]["Size"]
        item_pos = (template_config["Item"]["X"], template_config["Item"]["Y"])
        item_width = template_config["Item"]["Width"]
        bid_pos = (template_config["Bid"]["X"], template_config["Bid"]["Y"])
        qr_pos = (template_config["QR"]["X"], template_config["QR"]["Y"])

        # 3. Load fonts
        font_item = ImageFont.truetype(font_file_item, font_size_item)
        font_bid = ImageFont.truetype(font_file_bid, font_size_bid)

        # 4. Generate the QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(auction_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").resize((QR_CODE_SIZE_PX, QR_CODE_SIZE_PX))

        # 5. Draw text onto the image
        item_name_wrapped = wrap_text(text=item_name, font=font_item, max_width=item_width, draw=draw)
        draw.text(item_pos, item_name_wrapped, font=font_item, fill="black", align="center")
        draw.text(bid_pos, f"Starting Bid:\n{starting_bid}", font=font_bid, fill="black", align="center")
        
        # 6. Paste the QR code onto the image
        base_image.paste(qr_img, qr_pos)

        # 7. Save the final image
        # Create a safe filename
        safe_filename = "".join(c for c in item_name if c.isalnum() or c in (' ', '_')).rstrip()
        output_path = os.path.join(OUTPUT_DIR, f"{safe_filename}.png")
        base_image.save(output_path)

    except Exception as e:
        print(f"Error processing {item_name}: {e}")

# --- Main execution ---
if __name__ == "__main__":
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Read the CSV and generate cards
    with open(CSV_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            create_card(
                item_name=row['ItemName'],
                starting_bid=row['StartingBid'],
                auction_url=row['AuctionURL'],
                template_file=row['TemplateFile']
            )
            
    print(f"\nDone! All cards saved in '{OUTPUT_DIR}' folder.")