import requests
import os
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def download_image(url, path):
    if not os.path.exists(path):
        r = requests.get(url)
        r.raise_for_status()
        with open(path, 'wb') as f:
            f.write(r.content)

def get_latest_version():
    versions_url = "https://ddragon.leagueoflegends.com/api/versions.json"
    res = requests.get(versions_url)
    res.raise_for_status()
    versions = res.json()
    return versions[0]

def main():
    version = get_latest_version()

    assets_dir = "assets"
    temp_dir = "temp_images"
    output_dir = "generated_shop_icons"
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # CHANGE NAME / ADD FONT BELOW. TFT uses "Beaufort Pro Heavy" for the shop icons, but this is a premium font. You must source it yourself.
    # I've included an open-source alternative font, "Spectral Extra Bold", in its place for you to use immediately.
    font_path = os.path.join(assets_dir, "font.ttf")
    title_font_size = 18
    cost_font_size = 18
    name_x = 10
    name_y = 136
    gold_x = 177
    gold_y = 134
    icon_y = gold_y
    text_y = gold_y + 2
    shadow_offset = 1
    shadow_color = "black"
    blur_radius = 2
    # Get Champ Data
    champ_data_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/tft-champion.json"
    champ_res = requests.get(champ_data_url)
    champ_res.raise_for_status()
    champs = champ_res.json().get("data", {})

    # Get Newest Set
    set_pattern = re.compile(r"TFTSet(\d+)")
    set_nums = []
    for champion_id in champs.keys():
        m = set_pattern.search(champion_id)
        if m:
            set_nums.append(int(m.group(1)))

    if not set_nums:
        print("No recognizable TFTSetXX patterns found in champion IDs.")
        return

    newest_set = max(set_nums)

    # Load font
    title_font = ImageFont.truetype(font_path, title_font_size)
    cost_font = ImageFont.truetype(font_path, cost_font_size)

    # Get gold icon
    gold_icon_path = os.path.join(assets_dir, "gold.png")
    if not os.path.exists(gold_icon_path):
        raise FileNotFoundError("Gold icon not found at assets/gold.png.")

    # Process each champ from newest set
    for champion_id, champion_info in champs.items():
        m = set_pattern.search(champion_id)
        if not m or int(m.group(1)) != newest_set:
            continue

        champion_name = champion_info["name"]
        champion_cost = champion_info["tier"]
        champion_image_name = champion_info["image"]["full"]

        # Download champ image
        champ_img_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/tft-champion/{champion_image_name}"
        champion_image_path = os.path.join(temp_dir, champion_image_name)
        download_image(champ_img_url, champion_image_path)

        # Figure out frame by cost
        frame_image_path = os.path.join(assets_dir, f"{champion_cost}cost.png")
        if not os.path.exists(frame_image_path):
            print(f"Frame for cost {champion_cost} does not exist. Skipping {champion_id}.")
            continue

        # Create image
        champion_img = Image.open(champion_image_path).convert("RGBA")
        frame_img = Image.open(frame_image_path).convert("RGBA")
        frame_width, frame_height = frame_img.size

        # Resize champ image to frame
        champion_img = champion_img.resize((frame_width, frame_height), Image.LANCZOS)

        final_img = Image.new("RGBA", frame_img.size, (0, 0, 0, 0))
        final_img.paste(champion_img, (0, 0), champion_img)
        final_img.paste(frame_img, (0, 0), frame_img)

        draw = ImageDraw.Draw(final_img)

        # Draw CHAMPION NAME with drop shadow
        name_shadow_layer = Image.new("RGBA", final_img.size, (0,0,0,0))
        name_shadow_draw = ImageDraw.Draw(name_shadow_layer)
        name_shadow_draw.text((name_x + shadow_offset, name_y + shadow_offset), 
                              champion_name, fill=shadow_color, font=title_font, anchor='lt')
        name_shadow_layer = name_shadow_layer.filter(ImageFilter.GaussianBlur(blur_radius))
        final_img = Image.alpha_composite(final_img, name_shadow_layer)
        draw = ImageDraw.Draw(final_img)
        draw.text((name_x, name_y), champion_name, fill="white", font=title_font, anchor='lt')

        # Draw GOLD ICON with drop shadow
        gold_img = Image.open(gold_icon_path).convert("RGBA")
        gold_size = 15
        gold_img = gold_img.resize((gold_size, gold_size), Image.LANCZOS)

        gold_shadow = Image.new("RGBA", gold_img.size, (0,0,0,0))
        black_bg = Image.new("RGBA", gold_img.size, shadow_color)
        gold_shadow = Image.composite(black_bg, gold_shadow, gold_img)

        icon_shadow_layer = Image.new("RGBA", final_img.size, (0,0,0,0))
        icon_shadow_layer.paste(gold_shadow, (gold_x + shadow_offset, icon_y + shadow_offset), gold_shadow)
        icon_shadow_layer = icon_shadow_layer.filter(ImageFilter.GaussianBlur(blur_radius))
        final_img = Image.alpha_composite(final_img, icon_shadow_layer)

        final_img.paste(gold_img, (gold_x, icon_y), gold_img)

        # Draw COST TEXT with drop shadow
        cost_text = str(champion_cost)
        cost_x = gold_x + gold_size + 5
        cost_y = text_y

        cost_shadow_layer = Image.new("RGBA", final_img.size, (0,0,0,0))
        cost_shadow_draw = ImageDraw.Draw(cost_shadow_layer)
        cost_shadow_draw.text((cost_x + shadow_offset, cost_y + shadow_offset), 
                              cost_text, fill=shadow_color, font=cost_font, anchor='lt')
        cost_shadow_layer = cost_shadow_layer.filter(ImageFilter.GaussianBlur(blur_radius))
        final_img = Image.alpha_composite(final_img, cost_shadow_layer)

        draw = ImageDraw.Draw(final_img)
        draw.text((cost_x, cost_y), cost_text, fill="white", font=cost_font, anchor='lt')

        # Create image file as COST_NAME.png
        clean_name = champion_name.replace(" ", "_")
        output_filename = f"{champion_cost}_{clean_name}.png"
        output_path = os.path.join(output_dir, output_filename)
        final_img.save(output_path, format="PNG")
        print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()
