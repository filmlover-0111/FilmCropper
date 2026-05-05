# FilmCropper

A desktop tool for automatically cropping film negatives and scanned photos.

## ✨ Features

* Click-to-select border color for precise detection
* Automatic cropping based on border segmentation
* Deskew (tilt correction) using geometric estimation
* Batch export for entire folders
* Supports JPG / PNG / TIFF / RAW formats
* High-resolution output (preview is downscaled for speed)
* Multi-language UI (中文 / English / 日本語 / Español)

---

## 🖼️ Screenshot

*(Add your UI screenshot here)*

```text
Example:
![UI](screenshot.png)
```

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
python filmcrop_final_ui_app.py
```

---

## 📦 Download (Windows)

You can download the pre-built executable from:

👉 **Releases → FilmCropper.exe**

---

## 🧠 How It Works (Overview)

1. User clicks on the border color
2. Image is converted to LAB color space
3. Border pixels are detected via color distance
4. Morphological operations clean the mask
5. Contours are extracted to find the main content
6. Largest valid region is selected and cropped
7. Image is optionally deskewed using `minAreaRect`

For more details, see [TECHNICAL.md](TECHNICAL.md)

---

## 🧩 Project Structure

```text
FilmCropper/
├── filmcrop_final_ui_app.py   # Main application
├── requirements.txt          # Dependencies
├── README.md
├── TECHNICAL.md              # Implementation details
├── icon.ico                  # App icon
├── icon.png                  # Source icon
```

---

## ⚠️ Limitations

* Assumes relatively consistent border color
* May struggle with low contrast or noisy backgrounds
* Currently processes one frame per image (no multi-frame splitting)

---

## 🔮 Future Work

* Multi-frame detection (automatic strip splitting)
* More robust border detection under uneven lighting
* Improved batch parameter handling

---

## 📄 License

MIT License
