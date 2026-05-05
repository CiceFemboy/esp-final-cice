import pygame
import sys
import tkinter as tk
from tkinter import filedialog
import json

BG       = (15,  14,  20)
ACCENT   = (80, 220, 140)
ACCENT2  = (40, 160, 100)
DIM      = (55,  53,  70)
WHITE    = (230, 230, 230)
DARK     = (10,  10,  14)

W, H = 960, 600
FPS  = 60

class Button:
    def __init__(self, rect, label, primary=False):
        self.rect    = pygame.Rect(rect)
        self.label   = label
        self.primary = primary
        self._hover  = 0.0

    def update(self, mx, my, dt):
        target      = 1.0 if self.rect.collidepoint(mx, my) else 0.0
        self._hover += (target - self._hover) * 8 * dt
        self._hover  = max(0.0, min(1.0, self._hover))

    def draw(self, surf, font):
        t = self._hover
        if self.primary:
            col = tuple(int(ACCENT2[i] + (ACCENT[i] - ACCENT2[i]) * t) for i in range(3))
            border = ACCENT
            txt_col = DARK if t > 0.4 else WHITE
        else:
            col = tuple(int(DIM[i] + 10 * t) for i in range(3))
            border = tuple(int(80 + 140 * t) for i in range(3))
            txt_col = WHITE

        pygame.draw.rect(surf, col,    self.rect, border_radius=5)
        pygame.draw.rect(surf, border, self.rect, width=2, border_radius=5)
        lbl = font.render(self.label, True, txt_col)
        surf.blit(lbl, lbl.get_rect(center=self.rect.center))

    def clicked(self, mx, my):
        return self.rect.collidepoint(mx, my)


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
    pygame.display.set_caption("Evolution Simulator")
    clock  = pygame.time.Clock()
    process = True

    font_title = pygame.font.SysFont("Courier New", 64, bold=True)
    font_btn_lg = pygame.font.SysFont("Courier New", 30, bold=True)
    font_btn_md = pygame.font.SysFont("Courier New", 22, bold=True)
    font_credit = pygame.font.SysFont("Courier New", 14)

    cx, cy = W // 2, H // 2

    btn_start  = Button((cx - 120, cy - 20,  240, 64), "START", primary=True)
    btn_import = Button((cx - 120, cy + 60, 240, 44), "IMPORT STATE")
    btn_editor = Button((cx - 120, cy + 120, 240, 44), "CREATURE EDITOR")

    while process:
        dt = clock.tick(FPS) / 1000.0
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_start.clicked(mx, my):
                    root = tk.Tk()
                    root.withdraw()
                    path = filedialog.askopenfilename(
                        initialdir="creatures",
                        filetypes=[("JSON files","*.json")]
                    )
                    root.destroy()
                    if path:
                        with open(path) as f:
                            creature_data = json.load(f)
                        from neat_munk.main import run_neat
                        run_neat(creature_data=creature_data)
                        return
                if btn_import.clicked(mx, my):
                    root = tk.Tk()
                    root.withdraw()   # hide the tkinter window
                    path = filedialog.askopenfilename(
                        initialdir="states",
                        filetypes=[("Pickle files", "*.pkl")]
                    )
                    root.destroy()
                    if path:
                        from neat_munk.main import run_neat
                        run_neat(import_path=path)
                        return
                if btn_editor.clicked(mx, my) :
                    exec(open("ESP-scripts\\editor.py").read())
                    process = False

            btn_import.update(mx, my, dt)
            btn_start.update(mx, my, dt)
            btn_editor.update(mx, my, dt)

        screen.fill(BG)

        title = font_title.render("ÉVOSIM", True, WHITE)
        screen.blit(title, title.get_rect(center=(cx, cy - 110)))

        pygame.draw.line(screen, ACCENT,
                         (cx - title.get_width()//2, cy - 78),
                         (cx + title.get_width()//2, cy - 78), 2)

        btn_start.draw(screen, font_btn_lg)
        btn_import.draw(screen, font_btn_md)
        btn_editor.draw(screen, font_btn_md)

        authors = ["Thomas Prévost-Langevin", "Christopher Plantevin"]

        for i, a in enumerate(authors):
            ct = font_credit.render(a, True, ACCENT2)
            screen.blit(ct, ct.get_rect(topleft=(5,0 + i * 16)))

        pygame.display.flip()


if __name__ == "__main__":
    main()