import pygame
import random
import json
import time
import math
from pygame import mixer
from pathlib import Path

# 초기화
pygame.init()
mixer.init()

# 상수 정의
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_OFFSET_X = (WINDOW_WIDTH - GRID_WIDTH * BLOCK_SIZE) // 2
GRID_OFFSET_Y = (WINDOW_HEIGHT - GRID_HEIGHT * BLOCK_SIZE) // 2

# 색상 정의
COLORS = {
    'background': (240, 240, 255),
    'grid': (230, 230, 250),
    'text': (60, 60, 80),
    'shadow': (200, 200, 220),
    'pieces': [
        (255, 181, 181),  # 파스텔 빨강
        (255, 228, 181),  # 파스텔 주황
        (181, 255, 181),  # 파스텔 초록
        (181, 181, 255),  # 파스텔 파랑
        (255, 181, 255),  # 파스텔 보라
        (181, 255, 255),  # 파스텔 하늘
        (255, 255, 181)   # 파스텔 노랑
    ]
}

# 테트리스 블록 모양
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]]   # L
]

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        self.lifetime = 60

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, screen):
        alpha = int((self.lifetime / 60) * 255)
        particle_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        particle_color = (*self.color, alpha)
        pygame.draw.circle(particle_surface, particle_color, (self.size/2, self.size/2), self.size/2)
        screen.blit(particle_surface, (self.x, self.y))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris Premium")
        
        # 리소스 로딩
        self.load_resources()
        
        # 게임 상태
        self.reset_game()
        
        # 파티클 시스템
        self.particles = []
        
        # 게임 설정
        self.settings = self.load_settings()

    def load_resources(self):
        # 폰트
        self.fonts = {
            'large': pygame.font.Font(None, 64),
            'medium': pygame.font.Font(None, 32),
            'small': pygame.font.Font(None, 24)
        }
        
        # 사운드
        self.sounds = {
            'rotate': pygame.mixer.Sound('rotate.wav'),
            'clear': pygame.mixer.Sound('clear.wav'),
            'drop': pygame.mixer.Sound('drop.wav'),
            'gameover': pygame.mixer.Sound('gameover.wav')
        }
        
        # BGM 설정
        pygame.mixer.music.load('bgm.mp3')
        pygame.mixer.music.set_volume(0.5)

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                return json.load(f)
        except:
            return {
                'music_volume': 0.5,
                'sfx_volume': 0.7,
                'high_scores': []
            }

    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)

    def reset_game(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.pause = False

    def new_piece(self):
        shape = random.choice(SHAPES)
        color = random.choice(COLORS['pieces'])
        return {
            'shape': shape,
            'color': color,
            'x': GRID_WIDTH // 2 - len(shape[0]) // 2,
            'y': 0
        }

    def add_particles(self, x, y, color):
        for _ in range(10):
            self.particles.append(Particle(x, y, color))

    def update_particles(self):
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()

    def draw_particles(self):
        for particle in self.particles:
            particle.draw(self.screen)

    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, COLORS['grid'],
                               (GRID_OFFSET_X + x * BLOCK_SIZE,
                                GRID_OFFSET_Y + y * BLOCK_SIZE,
                                BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_piece(self, piece, offset_x=0, offset_y=0):
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, piece['color'],
                                   (GRID_OFFSET_X + (piece['x'] + x + offset_x) * BLOCK_SIZE,
                                    GRID_OFFSET_Y + (piece['y'] + y + offset_y) * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

    def draw_shadow(self):
        shadow_y = self.current_piece['y']
        while self.is_valid_move(self.current_piece['shape'],
                               self.current_piece['x'],
                               shadow_y + 1):
            shadow_y += 1
        
        shadow_piece = self.current_piece.copy()
        shadow_piece['y'] = shadow_y
        shadow_piece['color'] = COLORS['shadow']
        self.draw_piece(shadow_piece)

    def draw_ui(self):
        # 점수
        score_text = self.fonts['medium'].render(f'Score: {self.score}', True, COLORS['text'])
        self.screen.blit(score_text, (20, 20))
        
        # 레벨
        level_text = self.fonts['medium'].render(f'Level: {self.level}', True, COLORS['text'])
        self.screen.blit(level_text, (20, 60))
        
        # 다음 블록
        next_text = self.fonts['small'].render('Next:', True, COLORS['text'])
        self.screen.blit(next_text, (WINDOW_WIDTH - 150, 20))
        
        # 다음 블록 그리기
        next_piece = self.next_piece.copy()
        next_piece['x'] = GRID_WIDTH + 3
        next_piece['y'] = 2
        self.draw_piece(next_piece)

    def is_valid_move(self, shape, x, y):
        for row_i, row in enumerate(shape):
            for col_i, cell in enumerate(row):
                if cell:
                    if (y + row_i >= GRID_HEIGHT or
                        x + col_i < 0 or
                        x + col_i >= GRID_WIDTH or
                        y + row_i < 0 or
                        self.grid[y + row_i][x + col_i]):
                        return False
        return True

    def rotate_piece(self):
        shape = self.current_piece['shape']
        new_shape = [[shape[j][i] for j in range(len(shape)-1, -1, -1)]
                    for i in range(len(shape[0]))]
        
        if self.is_valid_move(new_shape,
                            self.current_piece['x'],
                            self.current_piece['y']):
            self.current_piece['shape'] = new_shape
            self.sounds['rotate'].play()

    def hard_drop(self):
        while self.move_down():
            pass
        self.sounds['drop'].play()

    def move_down(self):
        if self.is_valid_move(self.current_piece['shape'],
                            self.current_piece['x'],
                            self.current_piece['y'] + 1):
            self.current_piece['y'] += 1
            return True
        
        self.freeze_piece()
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        
        if not self.is_valid_move(self.current_piece['shape'],
                                self.current_piece['x'],
                                self.current_piece['y']):
            self.game_over = True
            self.sounds['gameover'].play()
        return False

    def move_sideways(self, dx):
        if self.is_valid_move(self.current_piece['shape'],
                            self.current_piece['x'] + dx,
                            self.current_piece['y']):
            self.current_piece['x'] += dx

    def freeze_piece(self):
        for y, row in enumerate(self.current_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece['y'] + y][self.current_piece['x'] + x] = self.current_piece['color']

    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(cell is not None for cell in self.grid[y]):
                lines_to_clear.append(y)
        
        if lines_to_clear:
            self.sounds['clear'].play()
            for y in lines_to_clear:
                # 파티클 효과 추가
                for x in range(GRID_WIDTH):
                    self.add_particles(
                        GRID_OFFSET_X + x * BLOCK_SIZE,
                        GRID_OFFSET_Y + y * BLOCK_SIZE,
                        self.grid[y][x]
                    )
                
                del self.grid[y]
                self.grid.insert(0, [None for _ in range(GRID_WIDTH)])
            
            # 점수 계산
            self.lines_cleared += len(lines_to_clear)
            self.score += (100 * len(lines_to_clear)) * self.level
            
            # 레벨 업
            self.level = self.lines_cleared // 10 + 1

    def run(self):
        clock = pygame.time.Clock()
        fall_time = 0
        fall_speed = 1000  # 초기 낙하 속도 (ms)
        
        pygame.mixer.music.play(-1)  # BGM 재생
        
        while True:
            # 이벤트 처리
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                
                if event.type == pygame.KEYDOWN:
                    if not self.game_over and not self.pause:
                        if event.key == pygame.K_LEFT:
                            self.move_sideways(-1)
                        elif event.key == pygame.K_RIGHT:
                            self.move_sideways(1)
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            self.hard_drop()
                    
                    if event.key == pygame.K_p:
                        self.pause = not self.pause
                    elif event.key == pygame.K_r:
                        self.reset_game()
            
            if self.game_over or self.pause:
                self.draw_game_over() if self.game_over else self.draw_pause()
                pygame.display.flip()
                continue
            
            # 자동 낙하
            fall_speed = max(50, 1000 - (self.level - 1) * 100)  # 레벨에 따른 속도 조정
            fall_time += clock.get_rawtime()
            if fall_time >= fall_speed:
                self.move_down()
                fall_time = 0
            
            # 화면 그리기
            self.screen.fill(COLORS['background'])
            self.draw_grid()
            self.draw_shadow()
            self.draw_piece(self.current_piece)
            
            # 고정된 블록 그리기
            for y, row in enumerate(self.grid):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, cell,
                                       (GRID_OFFSET_X + x * BLOCK_SIZE,
                                        GRID_OFFSET_Y + y * BLOCK_SIZE,
                                        BLOCK_SIZE - 1, BLOCK_SIZE - 1))
            
            # UI 업데이트
            self.update_particles()
            self.draw_particles()
            self.draw_ui()
            
            pygame.display.flip()
            clock.tick(60)

    def draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.fonts['large'].render('GAME OVER', True, (255, 255, 255))
        score_text = self.fonts['medium'].render(f'Final Score: {self.score}', True, (255, 255, 255))
        restart_text = self.fonts['small'].render('Press R to Restart', True, (255, 255, 255))
        
        self.screen.blit(game_over_text,
                        (WINDOW_WIDTH//2 - game_over_text.get_width()//2,
                         WINDOW_HEIGHT//2 - 60))
        self.screen.blit(score_text,
                        (WINDOW_WIDTH//2 - score_text.get_width()//2,
                         WINDOW_HEIGHT//2))
        self.screen.blit(restart_text,
                        (WINDOW_WIDTH//2 - restart_text.get_width()//2,
                         WINDOW_HEIGHT//2 + 60))

    def draw_pause(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.fonts['large'].render('PAUSED', True, (255, 255, 255))
        continue_text = self.fonts['small'].render('Press P to Continue', True, (255, 255, 255))
        
        self.screen.blit(pause_text,
                        (WINDOW_WIDTH//2 - pause_text.get_width()//2,
                         WINDOW_HEIGHT//2 - 30))
        self.screen.blit(continue_text,
                        (WINDOW_WIDTH//2 - continue_text.get_width()//2,
                         WINDOW_HEIGHT//2 + 30))

if __name__ == '__main__':
    game = Game()
    game.run()