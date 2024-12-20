# TFT Shop Image Generator

<div align="center">
  <img src="https://raw.githubusercontent.com/jacksonjost/tft-shop-image-generator/main/coverimage.png" alt="TFT Shop Image Generator Example" width="680"/>
</div>

A Python script to generate the icons seen in the shop for Teamfight Tactics (TFT). The script automatically pulls the latest set image data from Data Dragon (image, name, cost) and generates the corresponding images. Traits (synergies) will also be added to the generated image in the future.

## Requirements

- Python 3.x
- [Pillow](https://python-pillow.org/)
- [Requests](https://docs.python-requests.org/)

## How to Use

1. **Clone the repo:**

    ```bash
    git clone https://github.com/yourusername/tft-icon-generator.git
    cd tft-icon-generator
    ```

2. **Install packages:**

    ```bash
    pip install pillow requests
    ```
    
3. **Run:**
   ```bash
    python tft_icon_generate.py
   ```

## Notes

TFT uses *Beaufort Pro Heavy* for the text font. I cannot include it here, so you need to source it yourself. I've included a similar font, *Spectral Extra Bold*, in its place for you to use immediately. See the citation below for more details on Spectral.

**Production Type.** (2024). *Spectral* (Version 2.005) [GitHub repository]. Retrieved 2024 from [https://github.com/productiontype/Spectral](https://github.com/productiontype/Spectral)
