# Silent Auction Card Generator

This tool automates the creation of printable informational cards for silent auction items. It reads item details from a CSV file, generates a unique QR code pointing to the bidding URL, and places text and images onto designated graphic templates.

## Features
- **Batch Processing:** Generates dozens of cards instantly from a single CSV spreadsheet.
- **Dynamic QR Codes:** Automatically creates QR codes linking directly to the item's auction page.
- **Configurable Layouts:** Uses a JSON configuration file to precisely position text and QR codes for different template designs.
- **Text Wrapping:** Automatically wraps long item names to fit within specified areas on the card.

## Prerequisites
To run this tool, you need Python installed on your computer.
- [How to install Python](https://www.python.org/about/gettingstarted/)
- [How to install pip](https://pip.pypa.io/en/stable/installation/) (usually included with modern Python installers)

## Installation
It is highly recommended to use a virtual environment to keep dependencies organized.
1. Clone or download this repository to your local machine.
2. Open a terminal (command prompt) in the project folder.
3. Create a virtual environment: 
    ```Bash
    python -m venv venv
    ```
4. Activate the virtual environment:
    - *Windows:*
    ```Bash
    .\venv\Scripts\activate
    ```
    - *macOS/Linux:*
    ```Bash
    source venv/bin/activate
    ```
5. Install dependencies:
    ```Bash
    pip install -r requirements.txt
    ```

## Configuration

### Items Spreadsheet (`auction_items.csv`)
This file holds the data for each card. It requires the following headers:
| **Header**     | **Description**                                                        |
|----------------|------------------------------------------------------------------------|
| `ItemName`     |                                          The display name of the item. |
| `StartingBid`  |                                   The starting price (e.g., "$31.99"). |
| `AuctionURL`   |                       The web address where users can bid on the item. |
| `TemplateFile` | The filename of the background image to use (e.g., `pizza-skate.png`). |

> ⚠️ **Important CSV Note:** If your `ItemName` (or any other field) contains a comma, you must wrap that entire field in double quotes. Otherwise, the CSV reader will think the comma marks the start of the next field, breaking the data for that row.
> - *Incorrect:* `Basket of goodies, gift cards, and wine`,$50.00...
> - *Correct:* `"Basket of goodies, gift cards, and wine"`,$50.00...

### Template Config (`template_config.json`)
This JSON file tells the script exactly where to place elements for each specific background template. Each template filename (e.g., `pizza-skate.png`) has its own section:
```JSON
"pizza-skate.png": {
    "Item": { ... },
    "Bid": { ... },
    "QR": { ... }
}
```

**Key Definitions:**
- `X` / `Y`: The coordinates (in pixels) for the top-left corner of the text or QR code.
- `Font`: The filename of the TrueType font (.ttf) to use. Must be saved within the `fonts` folder.
- `Size`: The standard font size.
- `Size_Max`: (For 'Item' only) The maximum allowed font size. The script may shrink text to fit, but it won't exceed this.
- `Width` / `Height`: (For 'Item' only) Defines the bounding box for text wrapping.

## Usage
1. Create and/or update the `auction_items.csv` file in the project root folder, using the [required schema](#items-spreadsheet-auction_itemscsv) and details for your auction items.
2. Make sure all background template images are present in the `templates` folder.
3. Run the script:
    ```Bash
    python generate_cards.py
    ```
4. The finished cards will be saved in the `generated_cards` folder. A `_manifest.json` file is also created, listing all successfully generated cards.

## Acknowledgments
- The `wrap_text` method was updated from the version shared in [Edun Rilwan's "Wrap and Render Multiline Text on Images Using Python's Pillow Library" Tutorial](https://dev.to/emiloju/wrap-and-render-multiline-text-on-images-using-pythons-pillow-library-2ppp)
- Border template graphic designs were generated with the assistance of Google Gemini.

## License
Distributed under the MIT License. See `LICENSE` for more information.