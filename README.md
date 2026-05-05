# FilmCropper

A simple desktop tool for automatically cropping film negatives and photos.

## Features

- Click border color to detect frame
- Automatic cropping
- Deskew (tilt correction)
- Batch export
- Supports JPG / TIFF / PNG / RAW
- Multi-language UI (中文 / English / 日本語 / Español)

## Usage

1. Select input folder
2. Select output folder
3. Click border color in preview
4. Export images

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python filmcrop_final_ui_app.py
```

## Build EXE

```bash
pyinstaller --onefile --windowed --name FilmCropper --icon=icon.ico --hidden-import=rawpy filmcrop_final_ui_app.py
```

## License

MIT
