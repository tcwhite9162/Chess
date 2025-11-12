from config import COLOR_PALETTES, HIGHLIGHT_COLORS

class ThemeManager:
    def __init__(self, active_palette_index=0, contrast_level=0):
        self.available_palettes   = list(COLOR_PALETTES.keys())
        self.active_palette_index = active_palette_index
        self.contrast_level       = contrast_level # 0 = low, 1 = high
        self.palette_count        = len(self.available_palettes)
        
    def active_colors(self):
        palette_name = self.available_palettes[self.active_palette_index]
        palette = COLOR_PALETTES[palette_name]
        colors = list(palette.values())[self.contrast_level]
        return (*colors, HIGHLIGHT_COLORS[self.active_palette_index])
    
    def next_palette(self):
        self.active_palette_index = (self.active_palette_index + 1) % self.palette_count

    def previous_palette(self):
        self.active_palette_index = (self.active_palette_index - 1) % self.palette_count

    def toggle_contrast_level(self):
        self.contrast_level = 0 if self.contrast_level else 1