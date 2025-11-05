import csv
import qrcode
import os
import json
from PIL import Image, ImageDraw, ImageFont
import hashlib

# --- SETUP ---
CSV_FILE = "auction_items.csv"
CONFIG_FILE = "template_config.json"
OUTPUT_DIR = "generated_cards"
QR_CODE_SIZE_PX = 300

with open(CONFIG_FILE, "r") as file:
    CONFIG = json.load(file)
# ---------------------

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

def find_best_fit_font(text, font_file, max_width, max_height, start_size, min_size, draw):
    """
    Finds the largest font size that allows text to fit in a bounding box.
    """
    font_size = start_size
    font = None # Default
    wrapped_text = ""

    while font_size >= min_size:
        # Load the font at the current size
        font = ImageFont.truetype(font=font_file, size=font_size)

        # Wrap the text
        wrapped_text = wrap_text(text=text, font=font, max_width=max_width, draw=draw)

        # Get the *actual* bounding box of the wrapped, multiline text
        # We use (0,0) as a temp origin; we only care about the width and height
        bbox = draw.multiline_textbbox((0,0), wrapped_text, font=font, align="center")
        text_height = bbox[3] - bbox[1] # bottom - top

        # Check if it fits
        if text_height <= max_height:
            # Success! This font size fits.
            return font, wrapped_text
        
        # If not, shring the font size and try again
        font_size -= 2
    
    # If we fall out of the loop, it means even the min_size didn't fit.
    # We'll just return the smallest font and its wrapped text.
    print(f"  -> Warning: Text overflowed even at min size {min_size}pt.")
    return font, wrapped_text

def create_card(item_name, starting_bid, auction_url, template_file):
    """Generates a single auction card."""
    
    print(f"Generating card for: {item_name} (Template: {template_file})")

    try:
        # 1. Open the base template image
        base_image = Image.open(f"templates/{template_file}").convert("RGBA")
        draw = ImageDraw.Draw(base_image)

        # 2. Get the template-specific configuration
        template_config = CONFIG[template_file]

        # Item
        font_file_item = f"fonts/{template_config["Item"]["Font"]}"
        font_size_min_item = template_config["Item"]["Size"]
        font_size_max_item = template_config["Item"]["Size_Max"]
        item_pos = (template_config["Item"]["X"], template_config["Item"]["Y"])
        item_width = template_config["Item"]["Width"]
        item_height = template_config["Item"]["Height"]

        # Bid / QR
        font_file_bid = f"fonts/{template_config["Bid"]["Font"]}"
        font_size_bid = template_config["Bid"]["Size"]
        bid_pos = (template_config["Bid"]["X"], template_config["Bid"]["Y"])
        qr_pos = (template_config["QR"]["X"], template_config["QR"]["Y"])

        # 3. Load bid font only (item font is dynamic)
        font_bid = ImageFont.truetype(font_file_bid, font_size_bid)

        # 4. Generate the QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(auction_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").resize((QR_CODE_SIZE_PX, QR_CODE_SIZE_PX))

        # 5. Draw text onto the image
        # Find the best font size and wrapped text for the item name
        font_item, item_name_wrapped = find_best_fit_font(
            text=item_name,
            font_file=font_file_item,
            max_width=item_width,
            max_height=item_height,
            start_size=font_size_max_item,
            min_size=font_size_min_item,
            draw=draw
        )
        
        # Calculate the center of the item name's bounding box
        box_center_x = item_pos[0] + (item_width / 2)
        box_center_y = item_pos[1] + (item_height / 2)

        # Draw the item name text centered in the box
        draw.multiline_text(
            (box_center_x, box_center_y),
            item_name_wrapped,
            font=font_item,
            fill="black",
            align="center",
            anchor="mm"
        )

        # Draw the starting bid text
        draw.text(bid_pos, f"Starting Bid:\n{starting_bid}", font=font_bid, fill="black", align="center")
        
        # 6. Paste the QR code onto the image
        base_image.paste(qr_img, qr_pos)

        # 7. Save the final image
        
        # Create a unique, consistent hash for the filename.
        # We combine item_name and template_file to ensure the hash is
        # unique for each item *and* each template it's applied to.
        unique_string = f"{item_name}::{template_file}"
        
        # Create a SHA-1 hash, encode the string to bytes,
        # get the hex digest, and take the first 10 characters.
        h = hashlib.sha1(unique_string.encode('utf-8'))
        short_hash = h.hexdigest()[:10] 
        
        output_filename = f"{short_hash}.png"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        base_image.save(output_path)
        
        print(f"  -> Saved as: {output_filename}")

        # Return info for the manifest file
        return {
            "filename": output_filename,
            "item_name": item_name,
            "template": template_file
        }

    except Exception as e:
        print(f"Error processing {item_name}: {e}")
        return None  # <-- Return None on failure

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    manifest_data = []

    # Read the CSV and generate cards
    with open(CSV_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Capture the return value from the function
            result = create_card(
                item_name=row['ItemName'],
                starting_bid=row['StartingBid'],
                auction_url=row['AuctionURL'],
                template_file=row['TemplateFile']
            )

            # Add to manifest if card creation was successful
            if result:
                manifest_data.append(result)

    manifest_path = os.path.join(OUTPUT_DIR, "_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=4)

    print(f"\nDone! All cards saved in '{OUTPUT_DIR}' folder.")
    print(f"A manifest file '_manifest.json' has been created mapping filenames to item names.")