import pygame
import random
import json
import os
import sys

# --- الإعدادات والأبعاد (مضبوطة لتناسب شاشات الهواتف) ---
CELL_SIZE = 40
GRID_WIDTH = 12
GRID_HEIGHT = 18
WIDTH = GRID_WIDTH * CELL_SIZE
HEIGHT = GRID_HEIGHT * CELL_SIZE + 80  # مساحة للبار العلوي (HUD)
HIGH_SCORE_FILE = "highscore.json"

class SnakeGameMobile:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Mobile - OMAR_PRO")
        self.clock = pygame.time.Clock()
        
        # محاولة تحميل الخط الافتراضي أو استخدام خط النظام
        try:
            self.font_sm = pygame.font.SysFont("segoeui", 18, bold=True)
            self.font_md = pygame.font.SysFont("segoeui", 22, bold=True)
            self.font_lg = pygame.font.SysFont("segoeui", 32, bold=True)
        except:
            self.font_sm = pygame.font.Font(None, 24)
            self.font_md = pygame.font.Font(None, 28)
            self.font_lg = pygame.font.Font(None, 40)

        self.high_score = self.load_high_score()
        self.reset_game()
        
        # متغيرات التحكم باللمس (Swipe)
        self.touch_start_pos = None

    def load_high_score(self):
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, "r") as f:
                    return json.load(f).get("highscore", 0)
            except:
                return 0
        return 0

    def save_high_score(self):
        with open(HIGH_SCORE_FILE, "w") as f:
            json.dump({"highscore": self.high_score}, f)

    def reset_game(self):
        self.snake = [(6, 9), (5, 9), (4, 9)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.game_speed = 140  # سرعة مناسبة للموبايل
        self.game_over = False
        self.game_started = False
        self.is_paused = False
        self.is_new_high_score = False
        self.apple_eaten_anim = 0
        self.go_frame = 0
        self.spawn_apple()

    def spawn_apple(self):
        while True:
            gx = random.randint(0, GRID_WIDTH - 1)
            gy = random.randint(0, GRID_HEIGHT - 1)
            if (gx, gy) not in self.snake:
                self.apple = (gx, gy)
                break

    def run(self):
        last_update = pygame.time.get_ticks()
        
        while True:
            current_time = pygame.time.get_ticks()
            
            # --- معالجة الأحداث (اللمس والماوس) ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    
                    # 1. فحص الضغط على زر Pause في الزاوية اليمنى العليا
                    if WIDTH - 80 <= pos[0] <= WIDTH - 10 and 10 <= pos[1] <= 50:
                        if self.game_started and not self.game_over:
                            self.is_paused = not self.is_paused
                        continue

                    # 2. الشاشات التفاعلية (البداية، الخسارة، الإيقاف)
                    if not self.game_started:
                        self.game_started = True
                        continue
                    if self.is_paused:
                        self.is_paused = False
                        continue
                    if self.game_over:
                        self.reset_game()
                        self.game_started = True
                        continue

                    # تسجيل بداية السحب (Swipe)
                    self.touch_start_pos = pos

                elif event.type == pygame.MOUSEBUTTONUP and self.touch_start_pos:
                    if self.game_started and not self.game_over and not self.is_paused:
                        end_pos = event.pos
                        dx = end_pos[0] - self.touch_start_pos[0]
                        dy = end_pos[1] - self.touch_start_pos[1]
                        
                        # تحديد اتجاه السحب إذا تجاوزت المسافة الحد الأدنى
                        if max(abs(dx), abs(dy)) > 25:
                            if abs(dx) > abs(dy):
                                if dx > 0 and self.direction != (-1, 0):
                                    self.next_direction = (1, 0)
                                elif dx < 0 and self.direction != (1, 0):
                                    self.next_direction = (-1, 0)
                            else:
                                if dy > 0 and self.direction != (0, -1):
                                    self.next_direction = (0, 1)
                                elif dy < 0 and self.direction != (0, 1):
                                    self.next_direction = (0, -1)
                    self.touch_start_pos = None

            # --- تحديث منطق اللعبة حسب السرعة ---
            if self.game_started and not self.game_over and not self.is_paused:
                if current_time - last_update > self.game_speed:
                    last_update = current_time
                    self.direction = self.next_direction
                    hx, hy = self.snake[0]
                    dx, dy = self.direction
                    new_head = (hx + dx, hy + dy)

                    # فحص الاصطدام
                    if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
                        new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or 
                        new_head in self.snake):
                        self.game_over = True
                        if self.score > self.high_score:
                            self.high_score = self.score
                            self.is_new_high_score = True
                            self.save_high_score()
                    else:
                        self.snake.insert(0, new_head)
                        if new_head == self.apple:
                            self.score += 1
                            self.apple_eaten_anim = 10
                            if self.game_speed > 75:
                                self.game_speed = max(75, 140 - (self.score * 2))
                            if self.score > self.high_score:
                                self.high_score = self.score
                                self.save_high_score()
                            self.spawn_apple()
                        else:
                            self.snake.pop()

            if self.game_over:
                self.go_frame += 1

            if self.apple_eaten_anim > 0:
                self.apple_eaten_anim -= 1

            # --- الرسم والتصميم ---
            self.render()
            self.clock.tick(60)

    def grid_to_screen(self, gx, gy):
        return gx * CELL_SIZE, gy * CELL_SIZE + 80

    def render(self):
        # 1. خلفية المربعات (طراز شطرنج)
        self.screen.fill("#aad759")
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                x1, y1 = self.grid_to_screen(c, r)
                color = "#aad759" if (r + c) % 2 == 0 else "#a2d149"
                pygame.draw.rect(self.screen, color, (x1, y1, CELL_SIZE, CELL_SIZE))

        # 2. رسم التفاحة
        ax, ay = self.grid_to_screen(*self.apple)
        cx, cy = ax + CELL_SIZE // 2, ay + CELL_SIZE // 2
        bounce = int(self.apple_eaten_anim * 0.6)
        r_apple = 14 + bounce
        pygame.draw.circle(self.screen, "#eb2223", (cx, cy + 2), r_apple)
        # ورقة التفاحة الصغيرة
        pygame.draw.polygon(self.screen, "#2ecc71", [
            (cx, cy - 14 - bounce), (cx + 8, cy - 20 - bounce), (cx + 4, cy - 12 - bounce)
        ])

        # 3. جسم الثعبان
        for i in range(len(self.snake) - 1):
            x1, y1 = self.grid_to_screen(*self.snake[i])
            x2, y2 = self.grid_to_screen(*self.snake[i+1])
            cx1, cy1 = x1 + CELL_SIZE//2, y1 + CELL_SIZE//2
            cx2, cy2 = x2 + CELL_SIZE//2, y2 + CELL_SIZE//2
            pygame.draw.line(self.screen, "#4674e9", (cx1, cy1), (cx2, cy2), CELL_SIZE - 6)

        # 4. رأس الثعبان والعينين
        hx, hy = self.snake[0]
        sx, sy = self.grid_to_screen(hx, hy)
        hcx, hcy = sx + CELL_SIZE // 2, sy + CELL_SIZE // 2
        pygame.draw.rect(self.screen, "#4674e9", (sx + 2, sy + 2, CELL_SIZE - 4, CELL_SIZE - 4), border_radius=8)
        
        dx, dy = self.direction
        e1_x = hcx + dx * 6 + (dy * 8 if dx == 0 else 0)
        e1_y = hcy + dy * 6 + (dx * 8 if dy == 0 else 0)
        pygame.draw.circle(self.screen, (255, 255, 255), (e1_x, e1_y), 4)

        # 5. البار العلوي (HUD) وزر الـ Pause
        pygame.draw.rect(self.screen, "#4a752c", (0, 0, WIDTH, 80))
        
        score_surf = self.font_md.render(f"🍎 {self.score}", True, (255, 255, 255))
        best_surf = self.font_sm.render(f"BEST: {self.high_score}", True, (255, 255, 255))
        self.screen.blit(score_surf, (20, 25))
        self.screen.blit(best_surf, (WIDTH - 130, 30))

        # زر الـ Pause في الزاوية اليمنى العليا
        pause_btn_rect = pygame.Rect(WIDTH - 75, 18, 55, 42)
        pygame.draw.rect(self.screen, "#385e1f", pause_btn_rect, border_radius=8)
        pause_text = self.font_sm.render("PAUSE", True, (255, 255, 255))
        self.screen.blit(pause_text, (WIDTH - 70, 29))

        # 6. شاشة البداية (Start Screen)
        if not self.game_started:
            overlay = pygame.Surface((WIDTH, HEIGHT - 80))
            overlay.set_alpha(200)
            overlay.fill((30, 41, 59))
            self.screen.blit(overlay, (0, 80))
            
            title_surf = self.font_lg.render("SNAKE MOBILE", True, (56, 189, 248))
            tap_surf = self.font_md.render("Tap Anywhere to Start", True, (74, 222, 128))
            desc_surf = self.font_sm.render("Swipe to move | Tap top-right to Pause", True, (148, 163, 184))
            
            self.screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, HEIGHT//2 - 60))
            self.screen.blit(tap_surf, (WIDTH//2 - tap_surf.get_width()//2, HEIGHT//2 + 10))
            self.screen.blit(desc_surf, (WIDTH//2 - desc_surf.get_width()//2, HEIGHT//2 + 60))

        # 7. شاشة الإيقاف المؤقت (Pause Screen)
        elif self.is_paused:
            overlay = pygame.Surface((WIDTH, HEIGHT - 80))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 80))
            
            paused_surf = self.font_lg.render("PAUSED", True, (255, 255, 255))
            resume_surf = self.font_md.render("Tap Anywhere to Resume", True, (200, 200, 200))
            self.screen.blit(paused_surf, (WIDTH//2 - paused_surf.get_width()//2, HEIGHT//2 - 30))
            self.screen.blit(resume_surf, (WIDTH//2 - resume_surf.get_width()//2, HEIGHT//2 + 20))

        # 8. شاشة الخسارة (Game Over)
        elif self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT - 80))
            overlay.set_alpha(210)
            overlay.fill((17, 17, 17))
            self.screen.blit(overlay, (0, 80))
            
            go_surf = self.font_lg.render("GAME OVER", True, (255, 89, 94))
            final_score = self.font_md.render(f"Score: {self.score}", True, (255, 209, 102))
            restart_surf = self.font_sm.render("Tap Anywhere to Play Again", True, (255, 255, 255))
            
            self.screen.blit(go_surf, (WIDTH//2 - go_surf.get_width()//2, HEIGHT//2 - 50))
            self.screen.blit(final_score, (WIDTH//2 - final_score.get_width()//2, HEIGHT//2 + 5))
            self.screen.blit(restart_surf, (WIDTH//2 - restart_surf.get_width()//2, HEIGHT//2 + 55))

        pygame.display.flip()

if __name__ == "__main__":
    game = SnakeGameMobile()
    game.run()