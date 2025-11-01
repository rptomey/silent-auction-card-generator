import csv
import qrcode
import os
import json
from PIL import Image, ImageDraw, ImageFont
import hashlib  # <-- NEW: Import the hash library

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
    
    print(f"Generating card for: {item_name} (Template: {template_file})")

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

        # --- MODIFIED SECTION: 7. Save the final image ---
        
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
        # --- END OF MODIFIED SECTION ---

    except Exception as e:
        print(f"Error processing {item_name}: {e}")
        return None  # <-- Return None on failure

# --- Main execution ---
if __name__ == "__main__":
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    manifest_data = []  # <-- NEW: To store a map of hashes to item names

    # Read the CSV and generate cards
    with open(CSV_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # --- MODIFIED SECTION ---
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
            # --- END OF MODIFIED SECTION ---
            
    # --- NEW SECTION: Save the manifest file ---
    manifest_path = os.path.join(OUTPUT_DIR, "_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=4)
    # --- END OF NEW SECTION ---

    print(f"\nDone! All cards saved in '{OUTPUT_DIR}' folder.")
    print(f"A manifest file '_manifest.json' has been created mapping filenames to item names.")