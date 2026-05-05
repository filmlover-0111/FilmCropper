# Technical Overview

## Core Idea

This project performs automatic cropping of film negatives or photos by detecting the border region and extracting the main content area.

## Processing Pipeline

1. Image Input

   * Supports JPG, PNG, TIFF, and RAW formats
   * RAW images are processed using `rawpy`

2. Border Color Sampling

   * User clicks on the image to select the border color
   * A small patch around the click is sampled
   * Converted to LAB color space for robustness

3. Border Detection

   * Compute color distance in LAB space
   * Generate a mask of pixels similar to the border color
   * Apply morphological operations to clean the mask

4. Content Extraction

   * Invert mask to get content region
   * Find contours using OpenCV
   * Filter contours based on:

     * area
     * aspect ratio
     * size constraints

5. Cropping

   * Select the largest valid contour
   * Compute bounding rectangle
   * Apply optional margin

6. Deskew (Rotation Correction)

   * Use `cv2.minAreaRect` to estimate angle
   * Rotate image to correct tilt
   * Recompute bounding box

7. High-Resolution Output

   * Preview is downscaled for speed
   * Final export reprocesses the full-resolution image

## Key Design Decisions

* LAB color space for more stable color matching
* User-guided border selection instead of full automation
* Separation of preview vs full-resolution processing for performance
* Contour-based detection instead of fixed geometry assumptions

## Limitations

* Assumes relatively uniform border color
* May fail with extremely low contrast or noisy backgrounds
* Currently processes one frame per image (no multi-frame splitting)

## Future Work

* Multi-frame detection (automatic splitting)
* Improved robustness for uneven lighting
* Batch parameter tuning
