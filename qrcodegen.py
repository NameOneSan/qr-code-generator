import os
import sys
import subprocess
import customtkinter as ctk
import qrcode
from PIL import Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    SquareModuleDrawer,
    GappedSquareModuleDrawer,
    CircleModuleDrawer,
    RoundedModuleDrawer,
    VerticalBarsDrawer,
    HorizontalBarsDrawer,
)
from qrcode.image.styles.colormasks import (
    SolidFillColorMask,
    VerticalGradiantColorMask,
    HorizontalGradiantColorMask,
    RadialGradiantColorMask,
)

# Set global CustomTkinter theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class QRCodeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Advanced QR Code Generator")
        self.geometry("700x850")
        self.resizable(False, False)

        # Set Window Icon if pfp.png exists
        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(os.path.abspath(__file__))

        icon_path = os.path.join(app_dir, "pfp.png")
        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(32, 32))
                self.wm_iconphoto(True, photo)
            except Exception:
                pass

        self.save_counter = 1

        # Main Layout: Scrollable Frame
        self.main_frame = ctk.CTkScrollableFrame(self, width=660, height=820)
        self.main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # --- SECTION 1: PAYLOAD & FILENAME ---
        self.add_header("1. Input Data & Output File")

        self.data_entry = ctk.CTkEntry(
            self.main_frame, placeholder_text="Paste your link or text here...", corner_radius=10, height=40
        )
        self.data_entry.pack(fill="x", padx=10, pady=(0, 10))

        self.filename_entry = ctk.CTkEntry(
            self.main_frame, placeholder_text="Filename (leave empty for auto qr_code_XXX.png)", corner_radius=10, height=40
        )
        self.filename_entry.pack(fill="x", padx=10, pady=(0, 15))

        # --- SECTION 2: STRUCTURE & DIMENSIONS ---
        self.add_header("2. Structure & Size Settings")

        shape_label = ctk.CTkLabel(self.main_frame, text="Module Shape / Style:")
        shape_label.pack(anchor="w", padx=10)
        self.shape_var = ctk.StringVar(value="Rounded")
        self.shape_dropdown = ctk.CTkOptionMenu(
            self.main_frame,
            values=["Square", "Gapped Square", "Circle", "Rounded", "Vertical Bars", "Horizontal Bars"],
            variable=self.shape_var,
        )
        self.shape_dropdown.pack(fill="x", padx=10, pady=(0, 10))

        self.version_slider = self.create_slider_setting("QR Version (Size auto-fits if too small):", 1, 40, 1)
        self.box_size_slider = self.create_slider_setting("Box Size (Pixels per module):", 5, 30, 10)
        self.border_slider = self.create_slider_setting("Border Thickness (Modules):", 1, 10, 4)

        # --- SECTION 3: COLORS & GRADIENTS ---
        self.add_header("3. Color Configuration")

        mode_label = ctk.CTkLabel(self.main_frame, text="Color Style Distribution:")
        mode_label.pack(anchor="w", padx=10)
        self.color_mode_var = ctk.StringVar(value="Radial Gradient")
        self.mode_dropdown = ctk.CTkOptionMenu(
            self.main_frame,
            values=["Solid / Plain", "Vertical Gradient", "Horizontal Gradient", "Radial Gradient"],
            variable=self.color_mode_var,
            command=self.toggle_color_sections,
        )
        self.mode_dropdown.pack(fill="x", padx=10, pady=(0, 15))

        # Primary Color
        self.c1_label = ctk.CTkLabel(self.main_frame, text="Primary Color (R, G, B):", font=ctk.CTkFont(weight="bold"))
        self.c1_label.pack(anchor="w", padx=10)
        self.r1 = self.create_rgb_slider("Red", 75)
        self.g1 = self.create_rgb_slider("Green", 0)
        self.b1 = self.create_rgb_slider("Blue", 130)
        self.c1_preview = ctk.CTkFrame(self.main_frame, height=20, corner_radius=5)
        self.c1_preview.pack(fill="x", padx=10, pady=(0, 15))

        # Secondary Color
        self.c2_label = ctk.CTkLabel(self.main_frame, text="Secondary Color (R, G, B):", font=ctk.CTkFont(weight="bold"))
        self.c2_label.pack(anchor="w", padx=10)
        self.r2 = self.create_rgb_slider("Red", 0)
        self.g2 = self.create_rgb_slider("Green", 0)
        self.b2 = self.create_rgb_slider("Blue", 139)
        self.c2_preview = ctk.CTkFrame(self.main_frame, height=20, corner_radius=5)
        self.c2_preview.pack(fill="x", padx=10, pady=(0, 15))

        # Background Color
        self.bg_label = ctk.CTkLabel(self.main_frame, text="Background Color (R, G, B):", font=ctk.CTkFont(weight="bold"))
        self.bg_label.pack(anchor="w", padx=10)
        self.r_bg = self.create_rgb_slider("Red", 255)
        self.g_bg = self.create_rgb_slider("Green", 255)
        self.b_bg = self.create_rgb_slider("Blue", 255)
        self.bg_preview = ctk.CTkFrame(self.main_frame, height=20, corner_radius=5)
        self.bg_preview.pack(fill="x", padx=10, pady=(0, 15))

        self.update_previews()

        # --- SECTION 4: GENERATE BUTTON ---
        self.generate_btn = ctk.CTkButton(
            self.main_frame,
            text="Generate & Open QR Code",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            corner_radius=10,
            command=self.generate_qr,
        )
        self.generate_btn.pack(fill="x", padx=10, pady=20)

    # --- UI HELPERS ---
    def add_header(self, text):
        lbl = ctk.CTkLabel(self.main_frame, text=text, font=ctk.CTkFont(size=16, weight="bold"))
        lbl.pack(anchor="w", padx=10, pady=(15, 5))

    def create_slider_setting(self, label_text, min_val, max_val, default_val):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=2)
        
        val_label = ctk.CTkLabel(frame, text=f"{label_text} {default_val}")
        val_label.pack(anchor="w")

        slider = ctk.CTkSlider(
            frame, from_=min_val, to=max_val, number_of_steps=max_val - min_val,
            command=lambda v: val_label.configure(text=f"{label_text} {int(v)}")
        )
        slider.set(default_val)
        slider.pack(fill="x", pady=(0, 5))
        return slider

    def create_rgb_slider(self, color_name, default_val):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=1)

        val_label = ctk.CTkLabel(frame, text=f"{color_name}: {default_val}")
        val_label.pack(side="left")

        slider = ctk.CTkSlider(
            frame, from_=0, to=255, number_of_steps=255,
            command=lambda v: [val_label.configure(text=f"{color_name}: {int(v)}"), self.update_previews()]
        )
        slider.set(default_val)
        slider.pack(side="right", fill="x", expand=True, padx=(10, 0))
        return slider

    def update_previews(self):
        c1_hex = f"#{int(self.r1.get()):02x}{int(self.g1.get()):02x}{int(self.b1.get()):02x}"
        c2_hex = f"#{int(self.r2.get()):02x}{int(self.g2.get()):02x}{int(self.b2.get()):02x}"
        bg_hex = f"#{int(self.r_bg.get()):02x}{int(self.g_bg.get()):02x}{int(self.b_bg.get()):02x}"

        self.c1_preview.configure(fg_color=c1_hex)
        self.c2_preview.configure(fg_color=c2_hex)
        self.bg_preview.configure(fg_color=bg_hex)

    def toggle_color_sections(self, choice):
        if choice == "Solid / Plain":
            self.c2_label.pack_forget()
            self.c2_preview.pack_forget()
        else:
            self.c2_label.pack(anchor="w", padx=10)
            self.c2_preview.pack(fill="x", padx=10, pady=(0, 15))

    # --- QR GENERATION ---
    def get_module_drawer(self):
        shape_map = {
            "Square": SquareModuleDrawer(),
            "Gapped Square": GappedSquareModuleDrawer(),
            "Circle": CircleModuleDrawer(),
            "Rounded": RoundedModuleDrawer(),
            "Vertical Bars": VerticalBarsDrawer(),
            "Horizontal Bars": HorizontalBarsDrawer(),
        }
        return shape_map.get(self.shape_var.get(), RoundedModuleDrawer())

    def get_color_mask(self):
        c1 = (int(self.r1.get()), int(self.g1.get()), int(self.b1.get()))
        c2 = (int(self.r2.get()), int(self.g2.get()), int(self.b2.get()))
        bg = (int(self.r_bg.get()), int(self.g_bg.get()), int(self.b_bg.get()))

        mode = self.color_mode_var.get()
        if mode == "Solid / Plain":
            return SolidFillColorMask(back_color=bg, front_color=c1)
        elif mode == "Vertical Gradient":
            return VerticalGradiantColorMask(back_color=bg, top_color=c1, bottom_color=c2)
        elif mode == "Horizontal Gradient":
            return HorizontalGradiantColorMask(back_color=bg, left_color=c1, right_color=c2)
        elif mode == "Radial Gradient":
            return RadialGradiantColorMask(back_color=bg, center_color=c1, edge_color=c2)

    def generate_qr(self):
        data = self.data_entry.get().strip()
        if not data:
            self.data_entry.configure(placeholder_text="⚠️ PLEASE ENTER TEXT OR A URL FIRST!")
            return

        custom_name = self.filename_entry.get().strip()
        if custom_name:
            if not custom_name.lower().endswith(".png"):
                custom_name += ".png"
            filename = custom_name
        else:
            filename = f"qr_code_{self.save_counter:03d}.png"
            while os.path.exists(filename):
                self.save_counter += 1
                filename = f"qr_code_{self.save_counter:03d}.png"
            self.save_counter += 1

        qr = qrcode.QRCode(
            version=int(self.version_slider.get()),
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=int(self.box_size_slider.get()),
            border=int(self.border_slider.get()),
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=self.get_module_drawer(),
            color_mask=self.get_color_mask(),
        )

        img.save(filename)
        print(f"File saved successfully as: {filename}")

        filepath = os.path.abspath(filename)
        if sys.platform == "win32":
            os.startfile(filepath)
        elif sys.platform == "darwin":
            subprocess.run(["open", filepath])
        else:
            subprocess.run(["xdg-open", filepath])


if __name__ == "__main__":
    app = QRCodeApp()
    app.mainloop()