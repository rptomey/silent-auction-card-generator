import csv
import qrcode
import os
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION ---
CSV_FILE = 'auction_items.csv'
OUTPUT_DIR = 'generated_cards'
FONT_FILE = 'YourCool90sFont.ttf'  # <-- Change this to your downloaded .ttf file
FONT_SIZE_ITEM = 48
FONT_SIZE_BID = 40
QR_CODE_SIZE_PX = 300  # Size of the QR code in pixels

# --- POSITIONS (You will need to fine-tune these!) ---
# These are the (x, y) coordinates from the top-left corner.
# You'll find these by trial and error.
POSITIONS = {
    'template_a.png': {
        'item_name': (50, 600),
        'starting_bid': (50, 700),
        'qr_code': (950, 550)  # Position to paste the top-left corner of the QR code
    },
    'template_b.png': {
        'item_name': (75, 550),
        'starting_bid': (75, 650),
        'qr_code': (900, 500)
    }
}
# ---------------------

def create_card(item_name, starting_bid, auction_url, template_file):
    """Generates a single auction card."""
    
    print(f"Generating card for: {item_name}")

    try:
        # 1. Open the base template image
        base_image = Image.open(template_file).convert("RGBA")
        draw = ImageDraw.Draw(base_image)

        # 2. Load fonts
        font_item = ImageFont.truetype(FONT_FILE, FONT_SIZE_ITEM)
        font_bid = ImageFont.truetype(FONT_FILE, FONT_SIZE_BID)

        # 3. Generate the QR code on the fly
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(auction_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").resize((QR_CODE_SIZE_PX, QR_CODE_SIZE_PX))

        # 4. Get positions for this template
        pos = POSITIONS.get(template_file)
        if not pos:
            print(f"Warning: No positions defined for {template_file}. Skipping.")
            return

        # 5. Draw text onto the image
        draw.text(pos['item_name'], item_name, font=font_item, fill="black")
        draw.text(pos['starting_bid'], f"Starting Bid: {starting_bid}", font=font_bid, fill="black")
        
        # 6. Paste the QR code onto the image
        base_image.paste(qr_img, pos['qr_code'])

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