#!/usr/bin/env python3
"""
Logo Designer - A GUI application for designing logos with text
Features:
- 2D and 3D text rendering
- Multiple font selection
- Color and gradient options for text and background
- PNG export functionality
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter, ImageOps
import numpy as np
from typing import Tuple, List, Optional, Dict, Any

class GradientFrame(ttk.Frame):
    """A frame with a gradient background"""
    def __init__(self, parent, color1, color2, **kwargs):
        super().__init__(parent, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind("<Configure>", self._create_gradient)
        
    def _create_gradient(self, event=None):
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Create gradient image
        gradient_img = Image.new('RGBA', (width, height), color=self.color1)
        draw = ImageDraw.Draw(gradient_img)
        
        # Draw gradient (horizontal)
        for i in range(width):
            r1, g1, b1 = int(self.color1[1:3], 16), int(self.color1[3:5], 16), int(self.color1[5:7], 16)
            r2, g2, b2 = int(self.color2[1:3], 16), int(self.color2[3:5], 16), int(self.color2[5:7], 16)
            
            # Calculate gradient color at position
            r = int(r1 + (r2 - r1) * i / width)
            g = int(g1 + (g2 - g1) * i / width)
            b = int(b1 + (b2 - b1) * i / width)
            
            # Draw vertical line with the calculated color
            draw.line([(i, 0), (i, height)], fill=(r, g, b, 255))
        
        self.gradient = ImageTk.PhotoImage(gradient_img)
        self.canvas = tk.Canvas(self, width=width, height=height, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.gradient)


class ColorSelector(ttk.Frame):
    """A widget for selecting colors or gradients"""
    def __init__(self, parent, label_text, initial_color="#000000", callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.callback = callback  # Optional callback function for when colors change
        self.is_gradient = tk.BooleanVar(value=False)
        self.color1 = initial_color
        self.color2 = "#FFFFFF"
        
        # Create widgets
        ttk.Label(self, text=label_text).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Color display
        self.color_frame = ttk.Frame(self, width=30, height=20, style="ColorFrame.TFrame")
        self.color_frame.grid(row=0, column=1, padx=5, pady=5)
        
        # Color button
        self.color_btn = ttk.Button(self, text="Choose Color", command=self.choose_color)
        self.color_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Gradient checkbox
        self.gradient_check = ttk.Checkbutton(self, text="Gradient", variable=self.is_gradient,
                                             command=self.toggle_gradient)
        self.gradient_check.grid(row=0, column=3, padx=5, pady=5)
        
        # Second color (initially hidden)
        self.color2_frame = ttk.Frame(self, width=30, height=20, style="Color2Frame.TFrame")
        self.color2_btn = ttk.Button(self, text="Choose Color 2", command=self.choose_color2)
        
        # Update color display
        self.update_color_display()
    
    def toggle_gradient(self):
        if self.is_gradient.get():
            self.color2_frame.grid(row=0, column=4, padx=5, pady=5)
            self.color2_btn.grid(row=0, column=5, padx=5, pady=5)
        else:
            self.color2_frame.grid_forget()
            self.color2_btn.grid_forget()
            
        # Notify about the change
        if self.callback:
            self.callback()
        elif hasattr(self.parent, 'update_preview') and callable(self.parent.update_preview):
            self.parent.update_preview()
    
    def choose_color(self):
        color = colorchooser.askcolor(self.color1)[1]
        if color:
            self.color1 = color
            self.update_color_display()
            # Try multiple ways to notify about the color change
            if self.callback:
                # Use the provided callback if available
                self.callback()
            elif hasattr(self.parent, 'update_preview') and callable(self.parent.update_preview):
                # Try the parent's update_preview method
                self.parent.update_preview()
    
    def choose_color2(self):
        color = colorchooser.askcolor(self.color2)[1]
        if color:
            self.color2 = color
            self.update_color_display()
            # Try multiple ways to notify about the color change
            if self.callback:
                # Use the provided callback if available
                self.callback()
            elif hasattr(self.parent, 'update_preview') and callable(self.parent.update_preview):
                # Try the parent's update_preview method
                self.parent.update_preview()
    
    def update_color_display(self):
        # Update style for color display frames
        style = ttk.Style()
        style.configure("ColorFrame.TFrame", background=self.color1)
        style.configure("Color2Frame.TFrame", background=self.color2)
        
        # Force redraw
        self.color_frame.update_idletasks()
        self.color2_frame.update_idletasks()
    
    def get_colors(self):
        if self.is_gradient.get():
            return (self.color1, self.color2)
        return (self.color1,)


class LogoDesigner(tk.Tk):
    """Main application window for logo design"""
    def __init__(self):
        super().__init__()
        self.title("Logo Designer")
        self.geometry("1200x800")
        
        # Set up styles
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use a modern-looking theme
        
        # Configure grid layout
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)
        
        # Create main frames
        self.sidebar = ttk.Frame(self, padding="10")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.content = ttk.Frame(self, padding="10")
        self.content.grid(row=0, column=1, sticky="nsew")
        
        # Configure content layout
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)
        self.content.rowconfigure(1, weight=0)
        
        # Initialize variables
        self.logo_text = tk.StringVar(value="A")
        self.selected_font = tk.StringVar()
        self.font_size = tk.IntVar(value=72)
        self.is_3d = tk.BooleanVar(value=False)
        self.depth = tk.IntVar(value=5)
        self.canvas_width = tk.IntVar(value=500)
        self.canvas_height = tk.IntVar(value=500)
        
        # Create sidebar controls
        self._create_sidebar_controls()
        
        # Create preview canvas
        self.preview_frame = ttk.Frame(self.content, borderwidth=2, relief="groove")
        self.preview_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.preview_frame, width=500, height=500, 
                             background="white", highlightthickness=1, highlightbackground="gray")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create button bar
        self.button_bar = ttk.Frame(self.content)
        self.button_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        # Add buttons
        ttk.Button(self.button_bar, text="Save Logo", command=self.save_logo).pack(side="right", padx=5)
        ttk.Button(self.button_bar, text="Reset", command=self.reset_design).pack(side="right", padx=5)
        
        # Load available fonts
        self._load_fonts()
        
        # Generate initial preview
        self.update_preview()
    
    def _create_sidebar_controls(self):
        """Create all sidebar control widgets"""
        # Text input
        ttk.Label(self.sidebar, text="Logo Text:").pack(anchor="w", padx=5, pady=5)
        text_entry = ttk.Entry(self.sidebar, textvariable=self.logo_text)
        text_entry.pack(fill="x", padx=5, pady=5)
        text_entry.bind("<KeyRelease>", lambda e: self.update_preview())
        
        # Font selection
        ttk.Label(self.sidebar, text="Font:").pack(anchor="w", padx=5, pady=5)
        self.font_combo = ttk.Combobox(self.sidebar, textvariable=self.selected_font, state="readonly")
        self.font_combo.pack(fill="x", padx=5, pady=5)
        self.font_combo.bind("<<ComboboxSelected>>", lambda e: self.update_preview())
        
        # Font size
        ttk.Label(self.sidebar, text="Font Size:").pack(anchor="w", padx=5, pady=5)
        size_slider = ttk.Scale(self.sidebar, from_=10, to=200, variable=self.font_size, 
                             orient="horizontal", command=self.on_font_size_change)
        size_slider.pack(fill="x", padx=5, pady=5)
        
        # Display font size value
        self.size_value_label = ttk.Label(self.sidebar, text=f"Size: {self.font_size.get()}")
        self.size_value_label.pack(anchor="w", padx=5)
        
        # 3D effect
        ttk.Label(self.sidebar, text="3D Effect:").pack(anchor="w", padx=5, pady=5)
        ttk.Checkbutton(self.sidebar, text="Enable 3D", variable=self.is_3d, 
                      command=self.toggle_3d).pack(anchor="w", padx=5, pady=5)
        
        # 3D depth (initially hidden)
        self.depth_frame = ttk.Frame(self.sidebar)
        ttk.Label(self.depth_frame, text="3D Depth:").pack(anchor="w", padx=5, pady=5)
        depth_slider = ttk.Scale(self.depth_frame, from_=1, to=20, variable=self.depth, 
                              orient="horizontal", command=lambda e: self.update_preview())
        depth_slider.pack(fill="x", padx=5, pady=5)
        
        # Canvas size
        ttk.Label(self.sidebar, text="Canvas Size:").pack(anchor="w", padx=5, pady=5)
        size_frame = ttk.Frame(self.sidebar)
        size_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(size_frame, text="Width:").grid(row=0, column=0, sticky="w")
        width_entry = ttk.Entry(size_frame, textvariable=self.canvas_width, width=7)
        width_entry.grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(size_frame, text="Height:").grid(row=1, column=0, sticky="w")
        height_entry = ttk.Entry(size_frame, textvariable=self.canvas_height, width=7)
        height_entry.grid(row=1, column=1, sticky="w", padx=5)
        
        ttk.Button(size_frame, text="Apply", command=self.resize_canvas).grid(row=0, column=2, 
                                                                           rowspan=2, padx=5)
        
        # Text Color
        self.text_color = ColorSelector(self.sidebar, "Text Color:", 
                                     initial_color="#000000", 
                                     callback=self.update_preview)
        self.text_color.pack(fill="x", padx=5, pady=10)
        
        # Background Color
        self.bg_color = ColorSelector(self.sidebar, "Background Color:", 
                                    initial_color="#FFFFFF", 
                                    callback=self.update_preview)
        self.bg_color.pack(fill="x", padx=5, pady=10)
    
    def _load_fonts(self):
        """Load available fonts for the combo box"""
        print("Looking for available fonts on your system...")
        
        # Find available system fonts
        font_list = self._find_system_fonts()
        
        # Store the font paths for later use
        self.font_paths = {name: path for name, path in font_list}
        
        # Get just the font names for the dropdown
        font_names = [name for name, _ in font_list]
        
        # Check if we found any fonts
        if len(font_names) <= 1:  # Just "Default"
            print("Warning: No system fonts found. Only the default font will be available.")
            print("You may want to install additional fonts using the install_fonts.sh script.")
            
            # Make sure "Default" is always available
            if "Default" not in font_names:
                font_list.append(("Default", "default"))
                self.font_paths["Default"] = "default"
                font_names = [name for name, _ in font_list]
        else:
            print(f"Found {len(font_names)} fonts on your system.")
        
        # Update combobox
        self.font_combo['values'] = font_names
        if font_names:
            # Set default to a known good font if available, otherwise first in list
            if "DejaVu Sans" in font_names:
                self.selected_font.set("DejaVu Sans")
            elif "Liberation Sans" in font_names:
                self.selected_font.set("Liberation Sans")
            elif "Arial" in font_names:
                self.selected_font.set("Arial")
            else:
                self.selected_font.set(font_names[0])
    
    def on_font_size_change(self, value):
        """Update the font size label and refresh the preview"""
        # Convert from Scale's string value to integer
        size = int(float(value))
        self.font_size.set(size)
        
        # Debug output to confirm the font size change
        print(f"Font size changed to: {size}")
        
        # Update the label showing the size
        self.size_value_label.config(text=f"Size: {size}")
        
        # Force to integer to avoid any issues
        self.font_size.set(int(size))
        
        # Update the preview with a slight delay to ensure variable is updated
        self.after(10, self.update_preview)
    
    def toggle_3d(self):
        """Show/hide 3D depth controls based on the 3D toggle"""
        if self.is_3d.get():
            self.depth_frame.pack(fill="x", padx=5, pady=5)
        else:
            self.depth_frame.pack_forget()
        self.update_preview()
    
    def resize_canvas(self):
        """Resize the preview canvas"""
        width = self.canvas_width.get()
        height = self.canvas_height.get()
        
        # Validate sizes
        if width < 50 or height < 50:
            messagebox.showerror("Invalid Size", "Canvas dimensions must be at least 50x50")
            return
        
        # Update canvas
        self.canvas.config(width=width, height=height)
        self.update_preview()
    
    def update_preview(self):
        """Update the logo preview based on current settings"""
        try:
            # Create a new image with the current canvas size
            width = self.canvas_width.get()
            height = self.canvas_height.get()
            
            # Make sure we have the latest font size
            current_font_size = self.font_size.get()
            # Update the size value label if it exists
            if hasattr(self, 'size_value_label'):
                self.size_value_label.config(text=f"Size: {current_font_size}")
            
            # Create background
            bg_colors = self.bg_color.get_colors()
            if len(bg_colors) == 1:
                # Solid background
                background = Image.new('RGBA', (width, height), color=bg_colors[0])
            else:
                # Gradient background
                background = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
                draw = ImageDraw.Draw(background)
                
                try:
                    for i in range(width):
                        # Parse colors
                        r1, g1, b1 = int(bg_colors[0][1:3], 16), int(bg_colors[0][3:5], 16), int(bg_colors[0][5:7], 16)
                        r2, g2, b2 = int(bg_colors[1][1:3], 16), int(bg_colors[1][3:5], 16), int(bg_colors[1][5:7], 16)
                        
                        # Calculate gradient color at position
                        r = int(r1 + (r2 - r1) * i / width)
                        g = int(g1 + (g2 - g1) * i / width)
                        b = int(b1 + (b2 - b1) * i / width)
                        
                        # Draw vertical line with the calculated color
                        draw.line([(i, 0), (i, height)], fill=(r, g, b, 255))
                except (ValueError, IndexError) as e:
                    print(f"Error creating gradient background: {e}")
                    # Fall back to solid color
                    background = Image.new('RGBA', (width, height), color="#FFFFFF")
            
            # Get text and font information
            text = self.logo_text.get()
            font_name = self.selected_font.get()
            font_size = self.font_size.get()
            text_colors = self.text_color.get_colors()
            
            # Create a blank image for drawing text
            text_layer = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(text_layer)
            
            # Get the correct font path and create the font
            try:
                font_path = self._get_font_path(font_name)
                font = self._better_font_selection(font_path, font_size)
            except Exception as e:
                print(f"Error loading font: {e}")
                # Fall back to default font
                font = ImageFont.load_default()
            
            # Calculate text size to center it
            try:
                left, top, right, bottom = font.getbbox(text)
                text_width = right - left
                text_height = bottom - top
                text_x = (width - text_width) // 2
                text_y = (height - text_height) // 2
            except Exception as e:
                print(f"Error calculating text size: {e}")
                # Use default values
                text_width = width // 2
                text_height = height // 4
                text_x = width // 4
                text_y = height // 3
            
            # Apply 3D effect if enabled
            if self.is_3d.get():
                try:
                    depth = self.depth.get()
                    
                    # Parse text color
                    r, g, b = int(text_colors[0][1:3], 16), int(text_colors[0][3:5], 16), int(text_colors[0][5:7], 16)
                    
                    # Create 3D effect by drawing multiple layers with decreasing intensity
                    for i in range(depth, 0, -1):
                        # Calculate offset color (darker for depth)
                        depth_factor = 0.7 - (0.5 * i / depth)
                        offset_color = (int(r * depth_factor), int(g * depth_factor), int(b * depth_factor), 255)
                        
                        # Draw offset text
                        draw.text((text_x + i, text_y + i), text, font=font, fill=offset_color)
                except Exception as e:
                    print(f"Error rendering 3D effect: {e}")
            
            # Draw the main text
            try:
                if len(text_colors) == 1:
                    # Solid text color
                    draw.text((text_x, text_y), text, font=font, fill=text_colors[0])
                else:
                    # For gradient text, we need to create a mask and apply colors
                    # Create a mask with the text
                    mask = Image.new('L', (width, height), 0)
                    mask_draw = ImageDraw.Draw(mask)
                    mask_draw.text((text_x, text_y), text, font=font, fill=255)
                    
                    # Create a gradient image for the text
                    gradient = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
                    grad_draw = ImageDraw.Draw(gradient)
                    
                    r1, g1, b1 = int(text_colors[0][1:3], 16), int(text_colors[0][3:5], 16), int(text_colors[0][5:7], 16)
                    r2, g2, b2 = int(text_colors[1][1:3], 16), int(text_colors[1][3:5], 16), int(text_colors[1][5:7], 16)
                    
                    for y in range(text_height):
                        # Calculate color at this position
                        r = int(r1 + (r2 - r1) * y / text_height)
                        g = int(g1 + (g2 - g1) * y / text_height)
                        b = int(b1 + (b2 - b1) * y / text_height)
                        
                        # Draw a horizontal line with this color
                        y_pos = text_y + y
                        if 0 <= y_pos < height:  # Ensure we're drawing within the image
                            grad_draw.line([(0, y_pos), (width, y_pos)], fill=(r, g, b, 255))
                    
                    # Apply the mask to the gradient
                    gradient.putalpha(mask)
                    
                    # Paste the gradient text onto the text layer
                    text_layer = Image.alpha_composite(text_layer, gradient)
            except Exception as e:
                print(f"Error rendering text: {e}")
                # Try a simpler approach
                try:
                    draw.text((width//4, height//4), text, font=font, fill="#000000")
                except Exception:
                    print("Failed to render text with any method")
            
            # Combine background and text
            try:
                final_image = Image.alpha_composite(background, text_layer)
                
                # Display the preview
                self.preview_image = ImageTk.PhotoImage(final_image)
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor="nw", image=self.preview_image)
            except Exception as e:
                print(f"Error displaying preview: {e}")
                # Create a simple error message on canvas
                self.canvas.delete("all")
                self.canvas.create_text(width//2, height//2, text="Error rendering preview", 
                                     fill="red", font=("TkDefaultFont", 16))
        
        except Exception as e:
            print(f"Unexpected error in update_preview: {e}")
            # Show error on canvas
            self.canvas.delete("all")
            self.canvas.create_text(self.canvas.winfo_width()//2, self.canvas.winfo_height()//2, 
                                 text="Error updating preview", fill="red", font=("TkDefaultFont", 16))
    
    def save_logo(self):
        """Save the current logo design as a PNG file"""
        # Get file path from user
        filetypes = [("PNG files", "*.png"), ("All files", "*.*")]
        filepath = filedialog.asksaveasfilename(defaultextension=".png", filetypes=filetypes)
        
        if not filepath:
            return  # User cancelled
        
        # Generate the logo image
        width = self.canvas_width.get()
        height = self.canvas_height.get()
        
        # Create background
        bg_colors = self.bg_color.get_colors()
        if len(bg_colors) == 1:
            # Solid background
            background = Image.new('RGBA', (width, height), color=bg_colors[0])
        else:
            # Gradient background
            background = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(background)
            
            for i in range(width):
                # Parse colors
                r1, g1, b1 = int(bg_colors[0][1:3], 16), int(bg_colors[0][3:5], 16), int(bg_colors[0][5:7], 16)
                r2, g2, b2 = int(bg_colors[1][1:3], 16), int(bg_colors[1][3:5], 16), int(bg_colors[1][5:7], 16)
                
                # Calculate gradient color at position
                r = int(r1 + (r2 - r1) * i / width)
                g = int(g1 + (g2 - g1) * i / width)
                b = int(b1 + (b2 - b1) * i / width)
                
                # Draw vertical line with the calculated color
                draw.line([(i, 0), (i, height)], fill=(r, g, b, 255))
        
        # Get text and font information
        text = self.logo_text.get()
        font_name = self.selected_font.get()
        font_size = self.font_size.get()
        text_colors = self.text_color.get_colors()
        
        # Create a blank image for drawing text
        text_layer = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)
        
        # Get the correct font path and create the font
        font_path = self._get_font_path(font_name)
        font = self._better_font_selection(font_path, font_size)
        
        # Calculate text size to center it
        left, top, right, bottom = font.getbbox(text)
        text_width = right - left
        text_height = bottom - top
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        
        # Apply 3D effect if enabled
        if self.is_3d.get():
            depth = self.depth.get()
            
            # Parse text color
            r, g, b = int(text_colors[0][1:3], 16), int(text_colors[0][3:5], 16), int(text_colors[0][5:7], 16)
            
            # Create 3D effect by drawing multiple layers with decreasing intensity
            for i in range(depth, 0, -1):
                # Calculate offset color (darker for depth)
                depth_factor = 0.7 - (0.5 * i / depth)
                offset_color = (int(r * depth_factor), int(g * depth_factor), int(b * depth_factor), 255)
                
                # Draw offset text
                draw.text((text_x + i, text_y + i), text, font=font, fill=offset_color)
        
        # Draw the main text
        if len(text_colors) == 1:
            # Solid text color
            draw.text((text_x, text_y), text, font=font, fill=text_colors[0])
        else:
            # For gradient text, we need to create a mask and apply colors
            # Create a mask with the text
            mask = Image.new('L', (width, height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.text((text_x, text_y), text, font=font, fill=255)
            
            # Create a gradient image for the text
            gradient = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
            grad_draw = ImageDraw.Draw(gradient)
            
            r1, g1, b1 = int(text_colors[0][1:3], 16), int(text_colors[0][3:5], 16), int(text_colors[0][5:7], 16)
            r2, g2, b2 = int(text_colors[1][1:3], 16), int(text_colors[1][3:5], 16), int(text_colors[1][5:7], 16)
            
            for y in range(text_height):
                # Calculate color at this position
                r = int(r1 + (r2 - r1) * y / text_height)
                g = int(g1 + (g2 - g1) * y / text_height)
                b = int(b1 + (b2 - b1) * y / text_height)
                
                # Draw a horizontal line with this color
                y_pos = text_y + y
                if 0 <= y_pos < height:  # Ensure we're drawing within the image
                    grad_draw.line([(0, y_pos), (width, y_pos)], fill=(r, g, b, 255))
            
            # Apply the mask to the gradient
            gradient.putalpha(mask)
            
            # Paste the gradient text onto the text layer
            text_layer = Image.alpha_composite(text_layer, gradient)
        
        # Combine background and text
        final_image = Image.alpha_composite(background, text_layer)
        
        # Save the image
        try:
            final_image.save(filepath)
            messagebox.showinfo("Success", f"Logo saved to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save logo: {str(e)}")
    
    def reset_design(self):
        """Reset all design options to defaults"""
        self.logo_text.set("A")
        self.font_size.set(72)
        self.is_3d.set(False)
        self.depth.set(5)
        self.canvas_width.set(500)
        self.canvas_height.set(500)
        
        # Reset color selectors
        self.text_color.color1 = "#000000"
        self.text_color.color2 = "#FFFFFF"
        self.text_color.is_gradient.set(False)
        self.text_color.update_color_display()
        self.text_color.toggle_gradient()
        
        self.bg_color.color1 = "#FFFFFF"
        self.bg_color.color2 = "#FFFFFF"
        self.bg_color.is_gradient.set(False)
        self.bg_color.update_color_display()
        self.bg_color.toggle_gradient()
        
        # Hide depth frame
        self.depth_frame.pack_forget()
        
        # Reset canvas
        self.canvas.config(width=500, height=500)
        
        # Update preview
        self.update_preview()
    
    def _better_font_selection(self, font_path, font_size):
        """Improved font selection with better fallbacks"""
        # Ensure font size is an integer and at least 10
        try:
            font_size = max(10, int(font_size))
        except (ValueError, TypeError):
            print(f"Invalid font size: {font_size}, using 12")
            font_size = 12
        
        print(f"Creating font with path={font_path}, size={font_size}")
        
        # Special handling for our internal marker
        if font_path == "__USE_INTERNAL_DEFAULT__":
            print(f"Using scaled PIL default font for size {font_size}")
            
            # Since we couldn't load a TrueType font, we'll create a bitmap font
            # that approximates the requested size by using PIL's default font
            # and scaling it with PIL's image operations
            
            # Create a base image with default font of a certain size
            base_size = 24  # A reasonable base size
            base_img = Image.new('L', (base_size*10, base_size*2), 0)
            base_draw = ImageDraw.Draw(base_img)
            base_font = ImageFont.load_default()
            
            # Draw some text
            base_draw.text((0, 0), "Aa", font=base_font, fill=255)
            
            # Scale it to requested size
            scale_factor = font_size / base_size
            scaled_width = int(base_img.width * scale_factor)
            scaled_height = int(base_img.height * scale_factor)
            
            try:
                # Try to resize using LANCZOS filter for better quality
                scaled_img = base_img.resize((scaled_width, scaled_height), 
                                            Image.Resampling.LANCZOS)
                
                # Create a custom font object that mimics PIL's font interface
                # but returns the scaled dimensions when asked for size
                class ScaledFont:
                    def __init__(self, base_font, scale_factor):
                        self.base_font = base_font
                        self.scale_factor = scale_factor
                        self.size = font_size
                    
                    def getbbox(self, text):
                        bbox = self.base_font.getbbox(text)
                        return (
                            int(bbox[0] * self.scale_factor),
                            int(bbox[1] * self.scale_factor),
                            int(bbox[2] * self.scale_factor),
                            int(bbox[3] * self.scale_factor)
                        )
                    
                    def getsize(self, text):
                        if hasattr(self.base_font, 'getsize'):
                            base_size = self.base_font.getsize(text)
                            return (
                                int(base_size[0] * self.scale_factor),
                                int(base_size[1] * self.scale_factor)
                            )
                        else:
                            # PIL 9.0+ removed getsize, use getbbox instead
                            bbox = self.getbbox(text)
                            return (bbox[2] - bbox[0], bbox[3] - bbox[1])
                
                print(f"Created scaled font with size {font_size}")
                return ScaledFont(base_font, scale_factor)
                
            except Exception as e:
                print(f"Error creating scaled font: {e}")
                print("Using default font without scaling")
                return ImageFont.load_default()
                
        # Special case for the default font
        elif font_path == "default" or font_path.lower() == "default":
            print(f"Using PIL's default font (may not respect size {font_size})")
            # PIL's default font doesn't support custom sizes well
            # We'll try to create a better default font at the specified size
            try:
                # Check different system fonts that might be available
                system_fonts = [
                    # Common fonts that might be available system-wide
                    "DejaVuSans.ttf", "Arial.ttf", "LiberationSans-Regular.ttf", 
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                    "/usr/share/fonts/TTF/DejaVuSans.ttf",
                    # Add more system-specific paths
                    "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
                    "/usr/share/fonts/dejavu/DejaVuSans.ttf"
                ]
                
                # Try each system font
                for system_font in system_fonts:
                    try:
                        print(f"  - Trying system font: {system_font}")
                        return ImageFont.truetype(system_font, font_size)
                    except Exception as e:
                        print(f"  - Failed to load {system_font}: {e}")
                        continue
                
                # If none of the above work, try the default PIL approach
                print("  - All system fonts failed, using PIL default font (size might not apply)")
                # Call our internal method with special marker
                return self._better_font_selection("__USE_INTERNAL_DEFAULT__", font_size)
                
            except Exception as e:
                print(f"  - Error creating default font: {e}")
                # Call our internal method with special marker
                return self._better_font_selection("__USE_INTERNAL_DEFAULT__", font_size)
        
        # For regular font paths
        try:
            print(f"Loading TrueType font: {font_path}")
            font = ImageFont.truetype(font_path, font_size)
            print(f"Successfully loaded font: {font_path} at size {font_size}")
            return font
        except Exception as e:
            print(f"Error loading font {font_path} at size {font_size}: {e}")
            print("Falling back to default font")
            # Call our internal method with special marker
            return self._better_font_selection("__USE_INTERNAL_DEFAULT__", font_size)
    
    def _find_system_fonts(self):
        """Find available fonts on the system"""
        available_fonts = []
        
        # Common font directories to check
        font_dirs = [
            # Linux
            "/usr/share/fonts/truetype",
            "/usr/local/share/fonts",
            # macOS
            "/Library/Fonts",
            "/System/Library/Fonts",
            # Windows
            "C:\\Windows\\Fonts"
        ]
        
        # Add user font directory if exists
        home = os.path.expanduser("~")
        user_font_dirs = [
            os.path.join(home, ".fonts"),  # Linux
            os.path.join(home, "Library", "Fonts"),  # macOS
        ]
        font_dirs.extend([d for d in user_font_dirs if os.path.exists(d)])
        
        # Find font files (.ttf, .otf)
        font_files = []
        for font_dir in font_dirs:
            if os.path.exists(font_dir):
                try:
                    for root, _, files in os.walk(font_dir):
                        for file in files:
                            if file.lower().endswith(('.ttf', '.otf')):
                                font_files.append(os.path.join(root, file))
                except (IOError, OSError, PermissionError):
                    # Skip directories we can't access
                    pass
        
        # Test each font file
        for font_file in font_files:
            try:
                # Try to create a font to test availability
                font = ImageFont.truetype(font_file, 12)
                # Extract font name from path (simplified)
                font_name = os.path.basename(font_file).split('.')[0]
                available_fonts.append((font_name, font_file))
            except Exception:
                pass
        
        # Add some common font names (which PIL might find through its own mechanism)
        common_font_names = ["Arial", "Times New Roman", "Courier New", "Verdana", "Georgia", 
                           "Tahoma", "Trebuchet MS", "Impact", "Comic Sans MS"]
        
        for font_name in common_font_names:
            try:
                # Check if we can load the font by name
                ImageFont.truetype(font_name, 12)
                available_fonts.append((font_name, font_name))
            except Exception:
                pass
        
        # Add default as a fallback option
        available_fonts.append(("Default", "default"))
        
        # Remove duplicates and sort by font name
        unique_fonts = []
        seen_names = set()
        
        for name, path in available_fonts:
            if name not in seen_names:
                seen_names.add(name)
                unique_fonts.append((name, path))
        
        return sorted(unique_fonts, key=lambda x: x[0].lower())
    
    def _debug_font(self, font_obj, message="Font debug"):
        """Helper method to debug font properties"""
        try:
            # Get font attributes if possible
            attributes = dir(font_obj)
            print(f"{message}:")
            print(f"  - Font type: {type(font_obj)}")
            print(f"  - Available attributes: {', '.join(attr for attr in attributes if not attr.startswith('_'))}")
            
            # Try to get size information
            if hasattr(font_obj, 'size'):
                print(f"  - Size attribute: {font_obj.size}")
            
            # Try to get font name
            if hasattr(font_obj, 'getname'):
                print(f"  - Font name: {font_obj.getname()}")
                
            # Test with a sample text
            test_text = "Ag"
            if hasattr(font_obj, 'getbbox'):
                bbox = font_obj.getbbox(test_text)
                print(f"  - Bounding box for '{test_text}': {bbox}")
                print(f"  - Height: {bbox[3] - bbox[1]}")
                
            print("") # Empty line for readability
        except Exception as e:
            print(f"Error in font debug: {e}")
    
    def _get_font_path(self, font_name):
        """Get the correct font path for a given font name"""
        # If we have stored font paths, use them
        if hasattr(self, 'font_paths') and font_name in self.font_paths:
            font_path = self.font_paths.get(font_name)
            print(f"Using font path from dictionary: {font_name} -> {font_path}")
            if font_path == "default" or font_name.lower() == "default":
                # Get a real system font path instead of "default"
                return self._find_default_system_font()
            return font_path
        
        # Handle the Default font specially
        if font_name.lower() == "default":
            return self._find_default_system_font()
        
        # If we get here, just return the name
        print(f"Using font name directly: {font_name}")
        return font_name
        
    def _find_default_system_font(self):
        """Find a usable system font for the 'Default' option"""
        print("Finding a suitable system font for 'Default'...")
        
        # Try common system font locations with more paths
        system_fonts = [
            # Linux fonts - most common locations
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/gnu-free/FreeSans.ttf",
            # Windows fonts
            "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\segoeui.ttf", 
            # Mac fonts
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            # Generic names that PIL might recognize
            "DejaVuSans.ttf",
            "Arial.ttf",
            "Helvetica.ttf",
            "Arial",
            "Helvetica"
        ]
        
        # Try to load each font
        for font_path in system_fonts:
            try:
                # Just test if we can load it
                ImageFont.truetype(font_path, 12)
                print(f"Found system font for 'Default': {font_path}")
                return font_path
            except Exception as e:
                print(f"Could not load font {font_path}: {e}")
                continue
        
        # If no system font works, return a special marker that will
        # tell the better_font_selection method to handle the default case
        print("No system fonts found, using special handling for default font")
        return "__USE_INTERNAL_DEFAULT__"


def main():
    """Main entry point when running as a script or package"""
    # Enable basic logging for PIL
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Create the application
    app = LogoDesigner()
    
    # Print basic system information
    print("\nLogo Designer Debug Information:")
    print(f"Python version: {sys.version}")
    print(f"PIL version: {Image.__version__}")
    print(f"Tkinter version: {tk.TkVersion}")
    print(f"Running on: {sys.platform}")
    
    # Start the application
    app.mainloop()

if __name__ == "__main__":
    main()
