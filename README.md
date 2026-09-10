# 🎨 Advanced Gradient QR Code Generator

A modern, customizable desktop application built with Python and CustomTkinter for generating stylized, high-resolution QR codes with custom color gradients, module shapes, and automatic file saving.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## ✨ Features

- **Custom Module Shapes:** Choose between Square, Gapped Square, Circle, Rounded, Vertical Bars, and Horizontal Bars.
- **Color Distributions:**
  - Solid / Plain Color
  - Vertical Gradient
  - Horizontal Gradient
  - Radial Gradient
- **Interactive RGB Sliders:** Real-time color previews with 0-255 RGB sliders for Primary, Secondary, and Background colors.
- **Dynamic Sizing & Formatting:** Adjust QR Version (1–40), Box Size (pixels per module), and Border Thickness.
- **Auto-Increment Filenames:** Automatically names outputs as `qr_code_001.png`, `qr_code_002.png`, etc., if left blank.
- **Instant Preview:** Automatically opens the generated `.png` image using your system's default viewer upon creation.

---

## 🚀 Downloading the Executable (No Python Required)

If you just want to run the app on Windows without installing Python:

1. Go to the **[Releases](https://github.com/NameOneSan/qr-code-generator/releases)** section on the right side of this repository.
2. Download the latest `qrcodegen_v1.0.zip` file.
3. Extract the ZIP archive and run `qrcodegen.exe`.

---

## 🛠️ Running from Source

### Prerequisites

Ensure you have Python 3.10+ installed. Install the required dependencies using `pip`:

```bash
pip install customtkinter qrcode pillow