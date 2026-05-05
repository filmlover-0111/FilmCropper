#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FilmCropper Final UI
- 中文 / English / 日本語 / Español
- 默认中文
- 左侧设置区可用鼠标滚轮上下滚动
- 左右方向键切换上一张 / 下一张
- Debug 图默认不输出
- RAW / JPG / PNG / TIFF
- 预览缩小，导出全尺寸
- JPG 质量默认 100
- TIFF / PNG 可选
- 自动倾斜校正

Install:
    conda create -n filmcrop python=3.11 -y
    conda activate filmcrop
    pip install opencv-python pillow numpy rawpy imageio

Run:
    python filmcrop_final_ui_app.py

Build:
    pyinstaller --onefile --windowed --name FilmCropper --hidden-import=rawpy filmcrop_final_ui_app.py
"""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import numpy as np
from PIL import Image, ImageTk

try:
    import rawpy
    RAWPY_AVAILABLE = True
except Exception:
    RAWPY_AVAILABLE = False


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}
RAW_EXTS = {".cr2", ".cr3", ".nef", ".arw", ".raf", ".dng", ".orf", ".rw2", ".pef", ".srw"}
SUPPORTED_EXTS = IMAGE_EXTS | RAW_EXTS


LANGS = {
    "中文": {
        "app_title": "FilmCropper",
        "subtitle": "点击边框颜色，快速预览，全画质导出。",
        "language": "语言",
        "folders": "1. 文件夹",
        "input": "选择输入文件夹",
        "output": "选择输出文件夹",
        "no_input": "未选择输入文件夹",
        "no_output": "未选择输出文件夹",
        "crop_settings": "2. 裁切设置",
        "deskew": "自动校正倾斜",
        "preview_size": "预览大小",
        "refresh": "刷新预览",
        "tolerance": "颜色容差",
        "margin": "边距",
        "smooth": "平滑",
        "min_area": "最小主体面积 %",
        "export_settings": "3. 导出设置",
        "format": "输出格式",
        "quality": "JPG 质量",
        "raw16": "RAW 导出 TIFF 时使用 16-bit",
        "debug": "保存 Debug 图",
        "export": "4. 导出",
        "export_current": "导出当前图片",
        "export_all": "批量导出全部图片",
        "prev": "← 上一张",
        "next": "下一张 →",
        "status_initial": "请选择输入文件夹，然后在预览图上点击边框颜色。",
        "no_color": "未选择边框颜色",
        "loaded": "已加载。请点击预览图中的边框颜色。",
        "ready": "准备导出全画质图像",
        "no_content": "没有找到主体区域。请调大颜色容差，或重新点击边框。",
        "missing_output": "请先选择输出文件夹。",
        "missing_border": "请先点击边框颜色。",
        "done_current": "当前图片已导出。",
        "failed_current": "导出失败。请调整颜色容差或重新点击边框。",
        "done_all": "批量导出完成",
        "failed": "失败",
        "no_images": "文件夹里没有支持的图片或 RAW 文件。",
        "read_fail": "读取失败",
        "raw_on": "RAW 支持：已启用",
        "raw_off": "RAW 支持：未启用，请安装 rawpy",
        "click_border": "点击图片上的边框颜色",
        "tips": "黄色 = 识别出的边框；绿色 = 裁切区域。左/右方向键可切换图片。",
    },
    "English": {
        "app_title": "FilmCropper",
        "subtitle": "Click border color, preview fast, export full quality.",
        "language": "Language",
        "folders": "1. Folders",
        "input": "Choose Input Folder",
        "output": "Choose Output Folder",
        "no_input": "No input selected",
        "no_output": "No output selected",
        "crop_settings": "2. Crop Settings",
        "deskew": "Auto deskew tilted photos",
        "preview_size": "Preview size",
        "refresh": "Refresh Preview",
        "tolerance": "Color tolerance",
        "margin": "Margin",
        "smooth": "Smooth",
        "min_area": "Minimum content area %",
        "export_settings": "3. Export Settings",
        "format": "Output format",
        "quality": "JPG quality",
        "raw16": "Use 16-bit when exporting RAW to TIFF",
        "debug": "Save debug image",
        "export": "4. Export",
        "export_current": "Export Current Image",
        "export_all": "Export All Images",
        "prev": "← Previous",
        "next": "Next →",
        "status_initial": "Choose an input folder, then click the border color in the preview.",
        "no_color": "No border color",
        "loaded": "loaded. Click the border color in the preview.",
        "ready": "ready to export full quality",
        "no_content": "Could not find content. Try increasing tolerance or click another border area.",
        "missing_output": "Please choose an output folder first.",
        "missing_border": "Please click the border color first.",
        "done_current": "Current image exported.",
        "failed_current": "Export failed. Try adjusting tolerance or clicking another border color.",
        "done_all": "Export complete",
        "failed": "Failed",
        "no_images": "No supported image or RAW files found.",
        "read_fail": "Read failed",
        "raw_on": "RAW support: enabled",
        "raw_off": "RAW support: disabled. Please install rawpy.",
        "click_border": "Click the border color",
        "tips": "Yellow = detected border; green = crop area. Use Left/Right arrow keys to switch images.",
    },
    "日本語": {
        "app_title": "FilmCropper",
        "subtitle": "枠の色をクリックして、高速プレビュー、高画質で書き出し。",
        "language": "言語",
        "folders": "1. フォルダー",
        "input": "入力フォルダーを選択",
        "output": "出力フォルダーを選択",
        "no_input": "入力フォルダー未選択",
        "no_output": "出力フォルダー未選択",
        "crop_settings": "2. 切り抜き設定",
        "deskew": "傾きを自動補正",
        "preview_size": "プレビューサイズ",
        "refresh": "プレビュー更新",
        "tolerance": "色の許容範囲",
        "margin": "余白",
        "smooth": "スムーズ",
        "min_area": "最小領域 %",
        "export_settings": "3. 書き出し設定",
        "format": "出力形式",
        "quality": "JPG 品質",
        "raw16": "RAW を TIFF に書き出す時 16-bit を使用",
        "debug": "Debug 画像を保存",
        "export": "4. 書き出し",
        "export_current": "現在の画像を書き出し",
        "export_all": "すべて書き出し",
        "prev": "← 前へ",
        "next": "次へ →",
        "status_initial": "入力フォルダーを選択し、プレビューで枠の色をクリックしてください。",
        "no_color": "枠色未選択",
        "loaded": "読み込み完了。プレビューで枠の色をクリックしてください。",
        "ready": "高画質で書き出し可能",
        "no_content": "領域が見つかりません。許容範囲を上げるか、別の枠をクリックしてください。",
        "missing_output": "先に出力フォルダーを選択してください。",
        "missing_border": "先に枠の色をクリックしてください。",
        "done_current": "現在の画像を書き出しました。",
        "failed_current": "書き出しに失敗しました。設定を調整してください。",
        "done_all": "書き出し完了",
        "failed": "失敗",
        "no_images": "対応する画像または RAW ファイルがありません。",
        "read_fail": "読み込み失敗",
        "raw_on": "RAW 対応：有効",
        "raw_off": "RAW 対応：無効。rawpy をインストールしてください。",
        "click_border": "画像上の枠色をクリック",
        "tips": "黄色＝検出された枠、緑＝切り抜き範囲。左右キーで画像切替。",
    },
    "Español": {
        "app_title": "FilmCropper",
        "subtitle": "Haz clic en el color del borde, vista rápida y exportación en alta calidad.",
        "language": "Idioma",
        "folders": "1. Carpetas",
        "input": "Elegir carpeta de entrada",
        "output": "Elegir carpeta de salida",
        "no_input": "Sin carpeta de entrada",
        "no_output": "Sin carpeta de salida",
        "crop_settings": "2. Ajustes de recorte",
        "deskew": "Corregir inclinación automáticamente",
        "preview_size": "Tamaño de vista previa",
        "refresh": "Actualizar vista previa",
        "tolerance": "Tolerancia de color",
        "margin": "Margen",
        "smooth": "Suavizado",
        "min_area": "Área mínima %",
        "export_settings": "3. Ajustes de exportación",
        "format": "Formato de salida",
        "quality": "Calidad JPG",
        "raw16": "Usar 16-bit al exportar RAW a TIFF",
        "debug": "Guardar imagen Debug",
        "export": "4. Exportar",
        "export_current": "Exportar imagen actual",
        "export_all": "Exportar todas",
        "prev": "← Anterior",
        "next": "Siguiente →",
        "status_initial": "Elige una carpeta de entrada y haz clic en el color del borde.",
        "no_color": "Sin color de borde",
        "loaded": "cargada. Haz clic en el color del borde.",
        "ready": "lista para exportar en alta calidad",
        "no_content": "No se encontró contenido. Aumenta la tolerancia o haz clic en otro borde.",
        "missing_output": "Primero elige una carpeta de salida.",
        "missing_border": "Primero haz clic en el color del borde.",
        "done_current": "Imagen actual exportada.",
        "failed_current": "Error al exportar. Ajusta la tolerancia o elige otro borde.",
        "done_all": "Exportación completa",
        "failed": "Falló",
        "no_images": "No se encontraron imágenes o archivos RAW compatibles.",
        "read_fail": "Error de lectura",
        "raw_on": "RAW: activado",
        "raw_off": "RAW: desactivado. Instala rawpy.",
        "click_border": "Haz clic en el color del borde",
        "tips": "Amarillo = borde detectado; verde = área de recorte. Usa flechas izquierda/derecha para cambiar imagen.",
    },
}


def is_raw(path):
    return Path(path).suffix.lower() in RAW_EXTS


def read_image_any(path, raw_bps=8):
    path = Path(path)
    ext = path.suffix.lower()

    if ext in RAW_EXTS:
        if not RAWPY_AVAILABLE:
            raise RuntimeError("Need rawpy: pip install rawpy imageio")
        with rawpy.imread(str(path)) as raw:
            rgb = raw.postprocess(
                use_camera_wb=True,
                no_auto_bright=True,
                output_bps=raw_bps,
                gamma=(1, 1),
                bright=1.0,
            )
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    data = np.fromfile(str(path), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
    if img is None:
        return None
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    return img


def to_uint8(img):
    if img.dtype == np.uint8:
        return img
    if img.dtype == np.uint16:
        return np.clip(img / 256, 0, 255).astype(np.uint8)
    return np.clip(img, 0, 255).astype(np.uint8)


def imwrite_output(path, img, output_format="jpg", jpg_quality=100):
    fmt = output_format.lower()
    if fmt == "jpg":
        img8 = to_uint8(img)
        ok, buf = cv2.imencode(".jpg", img8, [int(cv2.IMWRITE_JPEG_QUALITY), int(jpg_quality)])
    elif fmt == "png":
        ok, buf = cv2.imencode(".png", img)
    elif fmt == "tiff":
        ok, buf = cv2.imencode(".tiff", img)
    else:
        img8 = to_uint8(img)
        ok, buf = cv2.imencode(".jpg", img8, [int(cv2.IMWRITE_JPEG_QUALITY), int(jpg_quality)])
    if ok:
        buf.tofile(str(path))
    return ok


def resize_to_max_side(img, max_side):
    h, w = img.shape[:2]
    scale = min(max_side / max(h, w), 1.0)
    if scale >= 1:
        return img.copy(), 1.0
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA), scale


def resize_for_view(img, max_w, max_h):
    h, w = img.shape[:2]
    scale = min(max_w / w, max_h / h, 1.0)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA), scale


def sample_color_lab(img8, x, y, radius=10):
    h, w = img8.shape[:2]
    x1, x2 = max(0, x - radius), min(w, x + radius + 1)
    y1, y2 = max(0, y - radius), min(h, y + radius + 1)
    patch = img8[y1:y2, x1:x2]
    lab = cv2.cvtColor(patch, cv2.COLOR_BGR2LAB)
    return lab.reshape(-1, 3).mean(axis=0), patch.reshape(-1, 3).mean(axis=0)


def create_border_mask(img8, border_lab, tolerance=24, smooth=7):
    lab = cv2.cvtColor(img8, cv2.COLOR_BGR2LAB).astype(np.float32)
    target = np.array(border_lab, dtype=np.float32).reshape(1, 1, 3)
    dist = np.linalg.norm(lab - target, axis=2)
    mask = (dist <= tolerance).astype(np.uint8) * 255

    k = max(3, int(smooth))
    if k % 2 == 0:
        k += 1
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    mask = cv2.medianBlur(mask, k)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    return mask


def largest_content_contour(img8, border_mask, min_area_ratio=0.02):
    h, w = img8.shape[:2]
    total = h * w
    content = cv2.bitwise_not(border_mask)

    k = max(5, int(min(h, w) * 0.006))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    content = cv2.morphologyEx(content, cv2.MORPH_OPEN, kernel, iterations=1)
    content = cv2.morphologyEx(content, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(content, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < total * min_area_ratio:
            continue
        if area > total * 0.985:
            continue
        x, y, cw, ch = cv2.boundingRect(c)
        aspect = cw / max(ch, 1)
        if 0.2 <= aspect <= 6.5:
            candidates.append(c)
    if not candidates:
        return None
    return max(candidates, key=cv2.contourArea)


def rect_from_contour(img, contour, margin=0):
    h, w = img.shape[:2]
    x, y, cw, ch = cv2.boundingRect(contour)
    x1 = max(0, x - margin)
    y1 = max(0, y - margin)
    x2 = min(w, x + cw + margin)
    y2 = min(h, y + ch + margin)
    return (x1, y1, x2 - x1, y2 - y1)


def normalize_angle(min_rect):
    (_, _), (rw, rh), angle = min_rect
    if rw < rh:
        angle += 90
    if angle > 45:
        angle -= 90
    if angle < -45:
        angle += 90
    if abs(angle) < 0.15:
        angle = 0.0
    return float(angle)


def estimate_corner_color(img):
    h, w = img.shape[:2]
    p = max(10, min(h, w) // 80)
    corners = np.vstack([
        img[0:p, 0:p].reshape(-1, img.shape[2]),
        img[0:p, max(0, w-p):w].reshape(-1, img.shape[2]),
        img[max(0, h-p):h, 0:p].reshape(-1, img.shape[2]),
        img[max(0, h-p):h, max(0, w-p):w].reshape(-1, img.shape[2]),
    ])
    vals = corners.mean(axis=0)
    return tuple(int(v) for v in vals)


def rotate_keep_all(img, angle):
    h, w = img.shape[:2]
    center = (w / 2, h / 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    cos = abs(M[0, 0])
    sin = abs(M[0, 1])
    new_w = int(h * sin + w * cos)
    new_h = int(h * cos + w * sin)

    M[0, 2] += new_w / 2 - center[0]
    M[1, 2] += new_h / 2 - center[1]

    rotated = cv2.warpAffine(
        img,
        M,
        (new_w, new_h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=estimate_corner_color(img),
    )
    return rotated, M


def transform_contour(contour, M, scale_factor=1.0):
    pts = contour.reshape(-1, 2).astype(np.float32) * scale_factor
    ones = np.ones((pts.shape[0], 1), dtype=np.float32)
    pts_h = np.hstack([pts, ones])
    new_pts = pts_h @ M.T
    return new_pts.reshape(-1, 1, 2).astype(np.int32)


def crop_rect(img, rect):
    x, y, w, h = rect
    return img[y:y+h, x:x+w]


def detect_preview(preview_img, border_lab, tolerance, smooth, margin, min_area_ratio, deskew):
    mask = create_border_mask(preview_img, border_lab, tolerance=tolerance, smooth=smooth)
    contour = largest_content_contour(preview_img, mask, min_area_ratio=min_area_ratio)
    if contour is None:
        return None, mask, {"ok": False}
    angle = normalize_angle(cv2.minAreaRect(contour)) if deskew else 0.0
    rect = rect_from_contour(preview_img, contour, margin=margin)
    return contour, mask, {"ok": True, "angle": angle, "rect": rect}


def process_fullres(full_img, preview_contour, preview_scale, angle, margin_preview):
    scale_factor = 1.0 / preview_scale
    full_margin = int(round(margin_preview * scale_factor))

    if abs(angle) < 0.15:
        full_contour = (preview_contour.astype(np.float32) * scale_factor).astype(np.int32)
        rect = rect_from_contour(full_img, full_contour, margin=full_margin)
        return crop_rect(full_img, rect), rect

    rotated, M = rotate_keep_all(full_img, angle)
    rotated_contour = transform_contour(preview_contour, M, scale_factor=scale_factor)
    rect = rect_from_contour(rotated, rotated_contour, margin=full_margin)
    return crop_rect(rotated, rect), rect


def draw_debug(preview_img, rect=None, mask=None, angle=None, alpha=0.32):
    out = preview_img.copy()
    if mask is not None:
        overlay = out.copy()
        overlay[mask > 0] = (0, 215, 255)
        out = cv2.addWeighted(overlay, alpha, out, 1 - alpha, 0)

    if rect is not None:
        x, y, w, h = rect
        t = max(2, preview_img.shape[1] // 700)
        cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 90), t)
        cv2.putText(out, "CROP", (x + 12, y + 42), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 90), 3)

    if angle is not None:
        cv2.putText(out, f"deskew {angle:.2f} deg", (24, 46), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 90), 3)
    return out


def resource_path(relative_path):
    """
    Works for normal Python run and PyInstaller onefile exe.
    """
    import sys
    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).resolve().parent
    return base_path / relative_path


class FilmCropperFinalUI:
    def __init__(self, root):
        self.root = root
        self.lang_name = "中文"
        self.t = LANGS[self.lang_name]

        self.input_dir = None
        self.output_dir = None
        self.files = []
        self.index = 0

        self.preview_img = None
        self.preview_scale = 1.0
        self.display_img = None
        self.view_img = None
        self.view_scale = 1.0
        self.photo = None

        self.border_lab = None
        self.border_bgr = None
        self.current_contour = None
        self.current_mask = None
        self.current_info = None

        self.labels = {}
        self.buttons = {}
        self.checks = {}

        self.setup_style()
        self.build_ui()
        self.apply_language()

        self.root.bind("<Left>", lambda e: self.prev_file())
        self.root.bind("<Right>", lambda e: self.next_file())

    def setup_style(self):
        self.root.title("FilmCropper")
        self.root.geometry("1320x880")
        self.root.minsize(1080, 720)
        self.root.configure(bg="#f4f5f7")

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        self.root.option_add("*Font", ("Segoe UI", 10))
        style.configure("TFrame", background="#f4f5f7")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("TLabel", background="#f4f5f7", foreground="#222222")
        style.configure("Card.TLabel", background="#ffffff", foreground="#222222")
        style.configure("Title.TLabel", background="#ffffff", font=("Segoe UI", 19, "bold"), foreground="#111111")
        style.configure("Section.TLabel", background="#ffffff", font=("Segoe UI", 11, "bold"), foreground="#111111")
        style.configure("Hint.TLabel", background="#ffffff", foreground="#666666")
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(10, 10))
        style.configure("Secondary.TButton", padding=(8, 8))
        style.configure("TCheckbutton", background="#ffffff", foreground="#222222")
        style.configure("Horizontal.TScale", background="#ffffff")

    def L(self, key):
        return self.t.get(key, key)

    def card(self, parent):
        return ttk.Frame(parent, style="Card.TFrame", padding=14)

    def build_ui(self):
        main = ttk.Frame(self.root, padding=14)
        main.pack(fill=tk.BOTH, expand=True)

        left_container = ttk.Frame(main, width=395)
        left_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 14))
        left_container.pack_propagate(False)

        # Fixed top language bar
        lang_bar = ttk.Frame(left_container, style="Card.TFrame", padding=10)
        lang_bar.pack(fill=tk.X, pady=(0, 10))
        self.labels["language"] = ttk.Label(lang_bar, style="Card.TLabel")
        self.labels["language"].pack(side=tk.LEFT)
        self.lang_var = tk.StringVar(value=self.lang_name)
        lang_box = ttk.Combobox(lang_bar, textvariable=self.lang_var, values=list(LANGS.keys()), state="readonly", width=12)
        lang_box.pack(side=tk.RIGHT)
        lang_box.bind("<<ComboboxSelected>>", self.change_language)

        # Scrollable settings panel
        scroll_wrap = ttk.Frame(left_container)
        scroll_wrap.pack(fill=tk.BOTH, expand=True)

        self.side_canvas = tk.Canvas(scroll_wrap, bg="#f4f5f7", highlightthickness=0)
        self.side_scrollbar = ttk.Scrollbar(scroll_wrap, orient="vertical", command=self.side_canvas.yview)
        self.scroll_frame = ttk.Frame(self.side_canvas)

        self.scroll_window = self.side_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.side_canvas.configure(yscrollcommand=self.side_scrollbar.set)

        self.scroll_frame.bind("<Configure>", lambda e: self.side_canvas.configure(scrollregion=self.side_canvas.bbox("all")))
        self.side_canvas.bind("<Configure>", lambda e: self.side_canvas.itemconfig(self.scroll_window, width=e.width))

        self.side_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.side_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Enable wheel only when mouse is over left scroll panel
        self.side_canvas.bind("<Enter>", lambda e: self.bind_sidebar_wheel())
        self.side_canvas.bind("<Leave>", lambda e: self.unbind_sidebar_wheel())
        self.scroll_frame.bind("<Enter>", lambda e: self.bind_sidebar_wheel())
        self.scroll_frame.bind("<Leave>", lambda e: self.unbind_sidebar_wheel())

        self.build_left_cards()

        right = ttk.Frame(main)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        top = ttk.Frame(right, padding=(0, 0, 0, 10))
        top.pack(fill=tk.X)

        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(top, textvariable=self.status_var, wraplength=820)
        self.status_label.pack(side=tk.LEFT, anchor=tk.W)

        self.color_chip = tk.Canvas(top, width=34, height=34, bg="#dddddd", highlightthickness=1, highlightbackground="#aaaaaa")
        self.color_chip.pack(side=tk.RIGHT, padx=(8, 0))
        self.color_text_var = tk.StringVar()
        ttk.Label(top, textvariable=self.color_text_var).pack(side=tk.RIGHT)

        viewer_card = ttk.Frame(right, style="Card.TFrame", padding=8)
        viewer_card.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(viewer_card, bg="#1f2024", cursor="crosshair", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Configure>", lambda e: self.render())

        file_card = ttk.Frame(right, style="Card.TFrame", padding=8)
        file_card.pack(fill=tk.X, pady=(10, 0))

        self.file_list = tk.Listbox(file_card, height=5, font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#dddddd")
        self.file_list.pack(fill=tk.X)
        self.file_list.bind("<<ListboxSelect>>", self.on_select_file)

    def bind_sidebar_wheel(self):
        self.root.bind_all("<MouseWheel>", self.on_sidebar_wheel)
        self.root.bind_all("<Button-4>", self.on_sidebar_wheel)
        self.root.bind_all("<Button-5>", self.on_sidebar_wheel)

    def unbind_sidebar_wheel(self):
        self.root.unbind_all("<MouseWheel>")
        self.root.unbind_all("<Button-4>")
        self.root.unbind_all("<Button-5>")
        self.root.bind("<Left>", lambda e: self.prev_file())
        self.root.bind("<Right>", lambda e: self.next_file())

    def on_sidebar_wheel(self, event):
        if getattr(event, "num", None) == 5 or getattr(event, "delta", 0) < 0:
            self.side_canvas.yview_scroll(3, "units")
        else:
            self.side_canvas.yview_scroll(-3, "units")

    def build_left_cards(self):
        header = self.card(self.scroll_frame)
        header.pack(fill=tk.X, pady=(0, 10))
        self.labels["app_title"] = ttk.Label(header, style="Title.TLabel")
        self.labels["app_title"].pack(anchor=tk.W)
        self.labels["subtitle"] = ttk.Label(header, style="Hint.TLabel", wraplength=330)
        self.labels["subtitle"].pack(anchor=tk.W, pady=(4, 0))

        raw_status_key = "raw_on" if RAWPY_AVAILABLE else "raw_off"
        self.labels["raw_status"] = ttk.Label(header, text=LANGS[self.lang_name][raw_status_key], style="Hint.TLabel", wraplength=330)
        self.labels["raw_status"].pack(anchor=tk.W, pady=(8, 0))

        folder = self.card(self.scroll_frame)
        folder.pack(fill=tk.X, pady=(0, 10))
        self.labels["folders"] = ttk.Label(folder, style="Section.TLabel")
        self.labels["folders"].pack(anchor=tk.W, pady=(0, 8))
        self.buttons["input"] = ttk.Button(folder, style="Secondary.TButton", command=self.choose_input)
        self.buttons["input"].pack(fill=tk.X)
        self.input_label = ttk.Label(folder, style="Hint.TLabel", wraplength=330)
        self.input_label.pack(anchor=tk.W, pady=(5, 10))
        self.buttons["output"] = ttk.Button(folder, style="Secondary.TButton", command=self.choose_output)
        self.buttons["output"].pack(fill=tk.X)
        self.output_label = ttk.Label(folder, style="Hint.TLabel", wraplength=330)
        self.output_label.pack(anchor=tk.W, pady=(5, 0))

        crop = self.card(self.scroll_frame)
        crop.pack(fill=tk.X, pady=(0, 10))
        self.labels["crop_settings"] = ttk.Label(crop, style="Section.TLabel")
        self.labels["crop_settings"].pack(anchor=tk.W, pady=(0, 8))

        self.deskew_var = tk.BooleanVar(value=True)
        self.checks["deskew"] = ttk.Checkbutton(crop, variable=self.deskew_var, command=self.update_detection)
        self.checks["deskew"].pack(anchor=tk.W)

        self.labels["preview_size"] = ttk.Label(crop, style="Card.TLabel")
        self.labels["preview_size"].pack(anchor=tk.W, pady=(10, 2))
        self.preview_side_var = tk.IntVar(value=1200)
        ttk.Combobox(crop, textvariable=self.preview_side_var, values=[800, 1000, 1200, 1400, 1800, 2200], state="readonly").pack(fill=tk.X)
        self.buttons["refresh"] = ttk.Button(crop, style="Secondary.TButton", command=self.reload_preview)
        self.buttons["refresh"].pack(fill=tk.X, pady=(6, 0))

        self.tolerance_var = tk.IntVar(value=24)
        self.margin_var = tk.IntVar(value=0)
        self.smooth_var = tk.IntVar(value=7)
        self.min_area_var = tk.DoubleVar(value=2.0)

        self.add_slider(crop, "tolerance", self.tolerance_var, 5, 90)
        self.add_slider(crop, "margin", self.margin_var, -120, 180)
        self.add_slider(crop, "smooth", self.smooth_var, 3, 41)
        self.add_slider(crop, "min_area", self.min_area_var, 0.2, 20.0)

        out = self.card(self.scroll_frame)
        out.pack(fill=tk.X, pady=(0, 10))
        self.labels["export_settings"] = ttk.Label(out, style="Section.TLabel")
        self.labels["export_settings"].pack(anchor=tk.W, pady=(0, 8))

        self.labels["format"] = ttk.Label(out, style="Card.TLabel")
        self.labels["format"].pack(anchor=tk.W)
        self.output_format_var = tk.StringVar(value="jpg")
        ttk.Combobox(out, textvariable=self.output_format_var, values=["jpg", "tiff", "png"], state="readonly").pack(fill=tk.X, pady=(2, 8))

        self.jpg_quality_var = tk.IntVar(value=100)
        self.add_slider(out, "quality", self.jpg_quality_var, 70, 100, update=False)

        self.raw16_var = tk.BooleanVar(value=True)
        self.checks["raw16"] = ttk.Checkbutton(out, variable=self.raw16_var)
        self.checks["raw16"].pack(anchor=tk.W, pady=(6, 0))

        self.save_debug_var = tk.BooleanVar(value=False)
        self.checks["debug"] = ttk.Checkbutton(out, variable=self.save_debug_var)
        self.checks["debug"].pack(anchor=tk.W, pady=(4, 0))

        tips = self.card(self.scroll_frame)
        tips.pack(fill=tk.X, pady=(0, 10))
        self.labels["click_border"] = ttk.Label(tips, style="Section.TLabel")
        self.labels["click_border"].pack(anchor=tk.W)
        self.labels["tips"] = ttk.Label(tips, style="Hint.TLabel", wraplength=330)
        self.labels["tips"].pack(anchor=tk.W, pady=(4, 0))

        # Fixed export card inside scroll frame, still visible via scroll; with wheel this is accessible.
        action = self.card(self.scroll_frame)
        action.pack(fill=tk.X, pady=(0, 20))
        self.labels["export"] = ttk.Label(action, style="Section.TLabel")
        self.labels["export"].pack(anchor=tk.W, pady=(0, 8))
        self.buttons["export_current"] = ttk.Button(action, style="Primary.TButton", command=self.export_current)
        self.buttons["export_current"].pack(fill=tk.X, pady=(0, 8))
        self.buttons["export_all"] = ttk.Button(action, style="Primary.TButton", command=self.export_all)
        self.buttons["export_all"].pack(fill=tk.X)

        nav = ttk.Frame(action, style="Card.TFrame")
        nav.pack(fill=tk.X, pady=(10, 0))
        self.buttons["prev"] = ttk.Button(nav, style="Secondary.TButton", command=self.prev_file)
        self.buttons["prev"].pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.buttons["next"] = ttk.Button(nav, style="Secondary.TButton", command=self.next_file)
        self.buttons["next"].pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

    def add_slider(self, parent, label_key, var, minv, maxv, update=True):
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(fill=tk.X, pady=(10, 0))
        lbl = ttk.Label(row, style="Card.TLabel")
        lbl.pack(side=tk.LEFT)
        self.labels[label_key] = lbl
        ttk.Label(row, textvariable=var, style="Card.TLabel").pack(side=tk.RIGHT)
        cmd = (lambda e: self.update_detection()) if update else None
        ttk.Scale(parent, from_=minv, to=maxv, orient=tk.HORIZONTAL, variable=var, command=cmd).pack(fill=tk.X)

    def change_language(self, event=None):
        self.lang_name = self.lang_var.get()
        self.t = LANGS[self.lang_name]
        self.apply_language()

    def apply_language(self):
        for key, label in self.labels.items():
            if key == "raw_status":
                label.config(text=self.L("raw_on") if RAWPY_AVAILABLE else self.L("raw_off"))
            elif key in self.t:
                label.config(text=self.L(key))

        for key, btn in self.buttons.items():
            btn.config(text=self.L(key))

        for key, chk in self.checks.items():
            chk.config(text=self.L(key))

        self.status_var.set(self.L("status_initial"))
        self.color_text_var.set(self.L("no_color"))
        if self.input_dir is None:
            self.input_label.config(text=self.L("no_input"))
        if self.output_dir is None:
            self.output_label.config(text=self.L("no_output"))

    def choose_input(self):
        folder = filedialog.askdirectory(title=self.L("input"))
        if not folder:
            return
        self.input_dir = Path(folder)
        self.input_label.config(text=str(self.input_dir))

        self.files = [p for p in sorted(self.input_dir.iterdir()) if p.suffix.lower() in SUPPORTED_EXTS]
        self.file_list.delete(0, tk.END)
        for f in self.files:
            self.file_list.insert(tk.END, f.name)

        if not self.files:
            messagebox.showwarning("FilmCropper", self.L("no_images"))
            return

        self.index = 0
        self.file_list.selection_clear(0, tk.END)
        self.file_list.selection_set(0)
        self.load_file()

    def choose_output(self):
        folder = filedialog.askdirectory(title=self.L("output"))
        if folder:
            self.output_dir = Path(folder)
            self.output_label.config(text=str(self.output_dir))

    def on_select_file(self, event):
        sel = self.file_list.curselection()
        if not sel:
            return
        self.index = sel[0]
        self.load_file()

    def load_file(self):
        if not self.files:
            return
        path = self.files[self.index]
        self.current_contour = None
        self.current_mask = None
        self.current_info = None

        try:
            img = read_image_any(path, raw_bps=8)
        except Exception as e:
            self.preview_img = None
            self.display_img = None
            self.status_var.set(f"{self.L('read_fail')}: {path.name} | {e}")
            return

        if img is None:
            self.status_var.set(f"{self.L('read_fail')}: {path.name}")
            return

        img8 = to_uint8(img)
        self.preview_img, self.preview_scale = resize_to_max_side(img8, int(self.preview_side_var.get()))

        if self.border_lab is not None:
            self.update_detection()
        else:
            self.display_img = self.preview_img
            self.status_var.set(f"{path.name} {self.L('loaded')}")
            self.render()

    def reload_preview(self):
        self.load_file()

    def prev_file(self):
        if not self.files:
            return
        self.index = max(0, self.index - 1)
        self.file_list.selection_clear(0, tk.END)
        self.file_list.selection_set(self.index)
        self.file_list.see(self.index)
        self.load_file()

    def next_file(self):
        if not self.files:
            return
        self.index = min(len(self.files) - 1, self.index + 1)
        self.file_list.selection_clear(0, tk.END)
        self.file_list.selection_set(self.index)
        self.file_list.see(self.index)
        self.load_file()

    def on_canvas_click(self, event):
        if self.preview_img is None or self.view_img is None:
            return

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        view_h, view_w = self.view_img.shape[:2]

        ox = (canvas_w - view_w) // 2
        oy = (canvas_h - view_h) // 2
        vx = event.x - ox
        vy = event.y - oy

        if vx < 0 or vy < 0 or vx >= view_w or vy >= view_h:
            return

        x = int(vx / self.view_scale)
        y = int(vy / self.view_scale)
        x = max(0, min(self.preview_img.shape[1] - 1, x))
        y = max(0, min(self.preview_img.shape[0] - 1, y))

        self.border_lab, self.border_bgr = sample_color_lab(self.preview_img, x, y, radius=10)
        b, g, r = [int(v) for v in self.border_bgr]
        self.color_text_var.set(f"BGR≈({b}, {g}, {r})")
        self.color_chip.configure(bg=f"#{r:02x}{g:02x}{b:02x}")
        self.update_detection()

    def update_detection(self):
        if self.preview_img is None or self.border_lab is None:
            return

        contour, mask, info = detect_preview(
            self.preview_img,
            self.border_lab,
            tolerance=int(self.tolerance_var.get()),
            smooth=int(self.smooth_var.get()),
            margin=int(self.margin_var.get()),
            min_area_ratio=float(self.min_area_var.get()) / 100.0,
            deskew=bool(self.deskew_var.get()),
        )

        self.current_contour = contour
        self.current_mask = mask
        self.current_info = info

        if info.get("ok"):
            rect = info["rect"]
            angle = info["angle"]
            self.display_img = draw_debug(self.preview_img, rect=rect, mask=mask, angle=angle)
            name = self.files[self.index].name if self.files else ""
            self.status_var.set(f"{name} | scale {self.preview_scale:.4f} | deskew {angle:.2f}° | {self.L('ready')}")
        else:
            self.display_img = draw_debug(self.preview_img, rect=None, mask=mask, angle=None)
            self.status_var.set(self.L("no_content"))

        self.render()

    def render(self):
        if self.display_img is None:
            return
        cw = max(300, self.canvas.winfo_width())
        ch = max(300, self.canvas.winfo_height())
        self.view_img, self.view_scale = resize_for_view(self.display_img, cw, ch)
        rgb = cv2.cvtColor(self.view_img, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        self.photo = ImageTk.PhotoImage(pil)
        self.canvas.delete("all")
        self.canvas.create_image(cw // 2, ch // 2, image=self.photo, anchor=tk.CENTER)

    def get_ext(self):
        fmt = self.output_format_var.get().lower()
        if fmt == "tiff":
            return ".tiff"
        if fmt == "png":
            return ".png"
        return ".jpg"

    def read_fullres_for_export(self, path):
        fmt = self.output_format_var.get().lower()
        raw_bps = 16 if (fmt == "tiff" and self.raw16_var.get()) else 8
        return read_image_any(path, raw_bps=raw_bps)

    def export_one(self, path):
        if self.border_lab is None:
            return False
        try:
            preview_source = read_image_any(path, raw_bps=8)
            if preview_source is None:
                return False
            preview8 = to_uint8(preview_source)
            preview, preview_scale = resize_to_max_side(preview8, int(self.preview_side_var.get()))

            contour, mask, info = detect_preview(
                preview,
                self.border_lab,
                tolerance=int(self.tolerance_var.get()),
                smooth=int(self.smooth_var.get()),
                margin=int(self.margin_var.get()),
                min_area_ratio=float(self.min_area_var.get()) / 100.0,
                deskew=bool(self.deskew_var.get()),
            )
            if contour is None or not info.get("ok"):
                return False

            full_img = self.read_fullres_for_export(path)
            if full_img is None:
                return False

            crop, _ = process_fullres(
                full_img,
                contour,
                preview_scale,
                info.get("angle", 0.0),
                int(self.margin_var.get()),
            )

            self.output_dir.mkdir(parents=True, exist_ok=True)
            fmt = self.output_format_var.get().lower()
            out_path = self.output_dir / f"{path.stem}_cropped{self.get_ext()}"

            ok = imwrite_output(
                out_path,
                crop,
                output_format=fmt,
                jpg_quality=int(self.jpg_quality_var.get()),
            )

            if ok and self.save_debug_var.get():
                debug_img = draw_debug(preview, rect=info.get("rect"), mask=mask, angle=info.get("angle"))
                imwrite_output(
                    self.output_dir / f"{path.stem}_debug.jpg",
                    debug_img,
                    output_format="jpg",
                    jpg_quality=95,
                )
            return ok
        except Exception as e:
            print(f"Failed: {path.name}: {e}")
            return False

    def export_current(self):
        if self.output_dir is None:
            messagebox.showwarning("FilmCropper", self.L("missing_output"))
            return
        if self.border_lab is None:
            messagebox.showwarning("FilmCropper", self.L("missing_border"))
            return
        if not self.files:
            return
        ok = self.export_one(self.files[self.index])
        if ok:
            messagebox.showinfo("FilmCropper", self.L("done_current"))
        else:
            messagebox.showwarning("FilmCropper", self.L("failed_current"))

    def export_all(self):
        if self.output_dir is None:
            messagebox.showwarning("FilmCropper", self.L("missing_output"))
            return
        if self.border_lab is None:
            messagebox.showwarning("FilmCropper", self.L("missing_border"))
            return
        total = 0
        failed = []
        for path in self.files:
            if self.export_one(path):
                total += 1
            else:
                failed.append(path.name)
        msg = f"{self.L('done_all')}: {total}"
        if failed:
            msg += f"\n\n{self.L('failed')}:\n" + "\n".join(failed[:12])
            if len(failed) > 12:
                msg += f"\n... {len(failed)-12}"
        messagebox.showinfo("FilmCropper", msg)


def main():
    root = tk.Tk()

    # Set window/taskbar icon when running from Python or packaged exe.
    icon_file = resource_path("icon.ico")
    if icon_file.exists():
        try:
            root.iconbitmap(str(icon_file))
        except Exception:
            pass

    app = FilmCropperFinalUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
