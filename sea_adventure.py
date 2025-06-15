import pygame
import random
import sys
import math
import time

# 初始化pygame
pygame.init()

# 游戏窗口设置
WIDTH, HEIGHT = 1500, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("温州商人的航海冒险")

# 尝试加载字体，如果失败则使用默认字体
try:
    font_large = pygame.font.SysFont('simhei', 36)  # 尝试使用黑体
    font_small = pygame.font.SysFont('simhei', 24)
except:
    font_large = pygame.font.SysFont(None, 36)  # 使用系统默认字体
    font_small = pygame.font.SysFont(None, 24)

# 颜色定义
OCEAN_BLUE = (50, 150, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BOAT_BROWN = (150, 100, 50)
SHARK_GRAY = (120, 120, 130)
SHARK_BELLY = (200, 200, 210)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# 游戏状态
class GameState:
    START_SCREEN = 0
    PLAYING = 1
    GAME_OVER = 2
    VICTORY = 3

# 像素风格小船设置
class Boat:
    def __init__(self, rocks):
        self.width = 30
        self.height = 40
        self.speed = 6
        self.angle = 0
        
        # 确保小船不会生成在礁石附近
        safe_spawn = False
        while not safe_spawn:
            self.x = random.randint(self.width, WIDTH - self.width)
            self.y = random.randint(self.height, HEIGHT - self.height)
            
            # 检查与所有礁石的距离
            safe_spawn = True
            for rock in rocks:
                distance = math.sqrt((self.x - rock.x)**2 + (self.y - rock.y)**2)
                if distance < rock.radius + max(self.width, self.height):
                    safe_spawn = False
                    break
        
    def draw(self):
        # 计算旋转后的四个角点
        rad = math.radians(self.angle)
        cos_val = math.cos(rad)
        sin_val = math.sin(rad)
        
        # 定义船的原始点
        points = [
            (0, -self.height//2),  # 船头
            (self.width//2, self.height//2),  # 船尾右
            (-self.width//2, self.height//2)  # 船尾左
        ]
        
        # 旋转点
        rotated_points = []
        for (x, y) in points:
            new_x = x * cos_val - y * sin_val + self.x
            new_y = x * sin_val + y * cos_val + self.y
            rotated_points.append((new_x, new_y))
        
        # 绘制船体
        pygame.draw.polygon(screen, BOAT_BROWN, rotated_points)
        
        # 绘制桅杆
        mast_top = (0 * cos_val - (-self.height//2 + 10) * sin_val + self.x, 
                   0 * sin_val + (-self.height//2 + 10) * cos_val + self.y)
        mast_bottom = (0 * cos_val - (0) * sin_val + self.x, 
                      0 * sin_val + (0) * cos_val + self.y)
        pygame.draw.line(screen, BLACK, mast_top, mast_bottom, 2)
        
        # 绘制船帆
        sail_top = (0 * cos_val - (-self.height//2 + 5) * sin_val + self.x, 
                   0 * sin_val + (-self.height//2 + 5) * cos_val + self.y)
        sail_right = (10 * cos_val - (5) * sin_val + self.x, 
                     10 * sin_val + (5) * cos_val + self.y)
        sail_left = (-10 * cos_val - (5) * sin_val + self.x, 
                    -10 * sin_val + (5) * cos_val + self.y)
        pygame.draw.polygon(screen, WHITE, [sail_top, sail_right, sail_left])

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.angle += 5
        if keys[pygame.K_RIGHT]:
            self.angle -= 5
        if keys[pygame.K_UP]:
            rad = math.radians(self.angle)
            self.x += self.speed * math.sin(rad)
            self.y -= self.speed * math.cos(rad)
        if keys[pygame.K_DOWN]:
            rad = math.radians(self.angle)
            self.x -= self.speed * math.sin(rad)
            self.y += self.speed * math.cos(rad)
            
        self.x = max(self.width // 2, min(WIDTH - self.width // 2, self.x))
        self.y = max(self.height // 2, min(HEIGHT - self.height // 2, self.y))
    
    def get_mask(self):
        return pygame.Rect(self.x - self.width//3, self.y - self.height//3, 
                         self.width*2//3, self.height*2//3)

# 鲨鱼设置
class Shark:
    def __init__(self):
        self.width = 70
        self.height = 40
        if random.random() < 0.5:
            self.x = random.choice([-self.width, WIDTH + self.width])
            self.y = random.randint(0, HEIGHT)
        else:
            self.x = random.randint(0, WIDTH)
            self.y = random.choice([-self.height, HEIGHT + self.height])
        
        self.speed = random.uniform(2.0, 3.5)
        self.angle = 0
        self.tail_wag = 0
    
    def draw(self):
        # 创建临时表面用于旋转
        shark_surf = pygame.Surface((self.width*2, self.height*2), pygame.SRCALPHA)
        
        # 尾巴摆动动画
        self.tail_wag += 0.1
        tail_offset = math.sin(self.tail_wag) * 5
        
        # 绘制鲨鱼身体
        body_points = [
            (self.width//2, 0),  # 头部中心
            (self.width//2 - 20, -self.height//3),  # 背部
            (-self.width//2 + 20 + tail_offset, -5),  # 尾部上
            (-self.width//2 + tail_offset, 0),  # 尾部尖
            (-self.width//2 + 20 + tail_offset, 5),  # 尾部下
            (self.width//2 - 20, self.height//3)  # 腹部
        ]
        pygame.draw.polygon(shark_surf, SHARK_GRAY, body_points)
        
        # 绘制腹部
        belly_points = [
            (self.width//2 - 10, 0),
            (self.width//2 - 20, self.height//6),
            (-self.width//4, 0),
            (self.width//2 - 20, -self.height//6)
        ]
        pygame.draw.polygon(shark_surf, SHARK_BELLY, belly_points)
        
        # 绘制眼睛
        pygame.draw.circle(shark_surf, BLACK, (self.width//2 - 10, -5), 3)
        
        # 绘制鳃裂
        for i in range(3):
            x = self.width//2 - 25 - i*5
            pygame.draw.line(shark_surf, (100, 100, 100), (x, -5), (x, 5), 1)
        
        # 绘制背鳍
        fin_points = [
            (self.width//2 - 30, -self.height//4),
            (self.width//2 - 40, -self.height//2),
            (self.width//2 - 35, -self.height//3)
        ]
        pygame.draw.polygon(shark_surf, SHARK_GRAY, fin_points)
        
        # 旋转并绘制
        angle_deg = math.degrees(math.atan2(math.sin(math.radians(self.angle)), 
                                math.cos(math.radians(self.angle))))
        rotated_surf = pygame.transform.rotate(shark_surf, angle_deg)
        new_rect = rotated_surf.get_rect(center=(self.x, self.y))
        screen.blit(rotated_surf, new_rect.topleft)
    
    def move(self, boat):
        dx = boat.x - self.x
        dy = boat.y - self.y
        target_angle = math.degrees(math.atan2(dy, dx))
        
        angle_diff = (target_angle - self.angle + 180) % 360 - 180
        self.angle += angle_diff * 0.1
        
        rad = math.radians(self.angle)
        self.x += self.speed * math.cos(rad)
        self.y += self.speed * math.sin(rad)
    
    def get_mask(self):
        return pygame.Rect(self.x - self.width//3, self.y - self.height//3, 
                         self.width*2//3, self.height*2//3)

# 礁石设置
class Rock:
    def __init__(self):
        self.radius = random.randint(10, 25)
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(self.radius, HEIGHT - self.radius)
        
    def draw(self):
        pygame.draw.circle(screen, BLACK, (self.x, self.y), self.radius)
    
    def get_mask(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                         self.radius * 2, self.radius * 2)

def draw_text(surface, text, font, color, x, y, center=False):
    """通用的文字绘制函数"""
    text_surface = font.render(text, True, color)
    if center:
        x = x - text_surface.get_width() // 2
    surface.blit(text_surface, (x, y))

# 游戏主函数
def main():
    clock = pygame.time.Clock()
    
    # 游戏状态
    game_state = GameState.START_SCREEN
    start_time = 0
    game_duration = 5 * 60  # 5分钟(300秒)
    
    rocks = [Rock() for _ in range(30)]
    boat = Boat(rocks)
    sharks = []
    shark_spawn_timer = 0
    
    while True:
        current_time = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_state == GameState.START_SCREEN:
                        game_state = GameState.PLAYING
                        start_time = current_time
                    elif game_state in (GameState.GAME_OVER, GameState.VICTORY):
                        # 重新开始游戏
                        return main()
        
        if game_state == GameState.PLAYING:
            # 计算剩余时间
            elapsed = current_time - start_time
            remaining = max(0, game_duration - elapsed)
            
            if remaining <= 0:
                game_state = GameState.VICTORY
            
            # 移动船
            keys = pygame.key.get_pressed()
            boat.move(keys)
            
            # 生成鲨鱼
            shark_spawn_timer += 1
            if shark_spawn_timer >= 120:  # 每2秒生成一只鲨鱼
                sharks.append(Shark())
                shark_spawn_timer = 0
            
            # 移动鲨鱼
            for shark in sharks[:]:
                shark.move(boat)
                if (shark.x < -100 or shark.x > WIDTH + 100 or 
                    shark.y < -100 or shark.y > HEIGHT + 100):
                    sharks.remove(shark)
            
            # 碰撞检测 - 礁石
            boat_mask = boat.get_mask()
            for rock in rocks:
                rock_mask = rock.get_mask()
                if boat_mask.colliderect(rock_mask):
                    game_state = GameState.GAME_OVER
            
            # 碰撞检测 - 鲨鱼
            for shark in sharks:
                shark_mask = shark.get_mask()
                if boat_mask.colliderect(shark_mask):
                    game_state = GameState.GAME_OVER
        
        # 绘制
        screen.fill(OCEAN_BLUE)
        
        # 绘制礁石
        for rock in rocks:
            rock.draw()
        
        # 绘制鲨鱼
        for shark in sharks:
            shark.draw()
        
        # 绘制船
        boat.draw()
        
        if game_state == GameState.START_SCREEN:
            # 绘制开场白背景
            s = pygame.Surface((WIDTH-100, HEIGHT-200), pygame.SRCALPHA)
            s.fill((0, 0, 0, 200))
            screen.blit(s, (50, 100))
            
            # 绘制开场白文字
            lines = [
                "温州商人的船误入小丑鲨的领地",
                "商人们要想办法避开礁石和小丑鲨",
                "坚持五分钟之后就可以离开小丑鲨的领地",
                "",
                "控制方式:",
                "↑键 - 前进",
                "↓键 - 后退",
                "←→键 - 转向",
                "",
                "按空格键开始游戏"
            ]
            
            for i, line in enumerate(lines):
                draw_text(screen, line, font_large, WHITE, 
                         WIDTH//2, 150 + i*40, center=True)
        
        elif game_state == GameState.PLAYING:
            # 显示剩余时间
            minutes = int(remaining) // 60
            seconds = int(remaining) % 60
            draw_text(screen, f"剩余时间: {minutes:02d}:{seconds:02d}", 
                     font_large, WHITE, 20, 20)
            
            # 显示提示
            draw_text(screen, "避开黑色礁石和灰色鲨鱼，坚持5分钟", 
                     font_small, WHITE, 20, 70)
        
        elif game_state == GameState.GAME_OVER:
            # 游戏结束画面
            s = pygame.Surface((500, 150), pygame.SRCALPHA)
            s.fill((0, 0, 0, 200))
            screen.blit(s, (WIDTH//2 - 250, HEIGHT//2 - 75))
            
            draw_text(screen, "游戏结束! 被袭击了", 
                     font_large, RED, WIDTH//2, HEIGHT//2 - 50, center=True)
            draw_text(screen, "按空格键重新开始", 
                     font_large, WHITE, WIDTH//2, HEIGHT//2 + 10, center=True)
        
        elif game_state == GameState.VICTORY:
            # 胜利画面
            s = pygame.Surface((500, 150), pygame.SRCALPHA)
            s.fill((0, 0, 0, 200))
            screen.blit(s, (WIDTH//2 - 250, HEIGHT//2 - 75))
            
            draw_text(screen, "胜利! 成功逃离小丑鲨领地", 
                     font_large, GREEN, WIDTH//2, HEIGHT//2 - 50, center=True)
            draw_text(screen, "按空格键重新开始", 
                     font_large, WHITE, WIDTH//2, HEIGHT//2 + 10, center=True)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
