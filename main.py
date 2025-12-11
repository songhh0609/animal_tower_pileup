# -*- coding: utf-8 -*-
"""
Animal Tower Stacking Game
동물 탑 쌓기 게임 - 메인 진입점

물리 엔진을 활용한 탑 쌓기 게임입니다.
하늘에서 떨어지는 동물들을 쌓아 최대한 높이 올려보세요!

조작법:
- ← → : 좌우 이동
- SPACE 또는 ↓ : 동물 떨어뜨리기
- ESC : 게임 종료

필요한 라이브러리:
- pygame
- pymunk
"""

import pygame
import sys
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE,
    GameState
)
from game_manager import GameManager
from ui_manager import UIManager
from background import Background


class Game:
    """
    메인 게임 클래스
    게임 루프와 전체 흐름을 관리합니다.
    """
    
    def __init__(self):
        """게임을 초기화합니다."""
        pygame.init()
        pygame.display.set_caption(GAME_TITLE)
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # 매니저 초기화
        self.game_manager = GameManager()
        self.ui_manager = UIManager()
        self.background = Background()
        
        # 게임 상태
        self.running = True
        self.debug_mode = False
        
        # 입력 상태
        self.keys_pressed = {
            'left': False,
            'right': False
        }
    
    def run(self):
        """메인 게임 루프를 실행합니다."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # 델타 타임 (초)
            
            self._handle_events()
            self._update(dt)
            self._draw()
        
        pygame.quit()
        sys.exit()
    
    def _handle_events(self):
        """이벤트를 처리합니다."""
        key_down_event = None
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_LEFT:
                    self.keys_pressed['left'] = True
                elif event.key == pygame.K_RIGHT:
                    self.keys_pressed['right'] = True
                elif event.key == pygame.K_SPACE:
                    key_down_event = 'space'
                elif event.key == pygame.K_DOWN:
                    key_down_event = 'down'
                elif event.key == pygame.K_F1:
                    self.debug_mode = not self.debug_mode
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.keys_pressed['left'] = False
                elif event.key == pygame.K_RIGHT:
                    self.keys_pressed['right'] = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 왼쪽 클릭
                    mouse_clicked = True
        
        # 게임 상태에 따른 입력 처리
        mouse_pos = pygame.mouse.get_pos()
        
        if self.game_manager.state == GameState.MENU:
            if self.ui_manager.check_start_clicked(mouse_pos, mouse_clicked):
                self.game_manager.start_game()
        
        elif self.game_manager.state == GameState.PLAYING:
            self.game_manager.handle_input(self.keys_pressed, key_down_event)
        
        elif self.game_manager.state == GameState.GAME_OVER:
            if self.ui_manager.check_restart_clicked(mouse_pos, mouse_clicked):
                self.game_manager.start_game()
    
    def _update(self, dt: float):
        """게임 상태를 업데이트합니다."""
        # 배경 업데이트 (구름 이동)
        self.background.update(dt)
        
        # 게임 매니저 업데이트
        if self.game_manager.state == GameState.PLAYING:
            self.game_manager.update(dt)
    
    def _draw(self):
        """화면을 그립니다."""
        # 배경
        self.background.draw(self.screen)
        
        # 게임 객체
        self.game_manager.draw(self.screen)
        
        # 디버그 모드
        if self.debug_mode:
            self.game_manager.draw_debug(self.screen)
        
        # UI
        mouse_pos = pygame.mouse.get_pos()
        
        if self.game_manager.state == GameState.MENU:
            self.ui_manager.draw_title_screen(self.screen, mouse_pos)
        
        elif self.game_manager.state == GameState.PLAYING:
            self.ui_manager.draw_score(
                self.screen, 
                self.game_manager.score,
                self.game_manager.tower_height
            )
            self.ui_manager.draw_next_preview(
                self.screen, 
                self.game_manager.next_animal_name
            )
        
        elif self.game_manager.state == GameState.GAME_OVER:
            self.ui_manager.draw_game_over_screen(
                self.screen,
                self.game_manager.score,
                self.game_manager.max_height,
                mouse_pos
            )
        
        # FPS 표시 (디버그)
        if self.debug_mode:
            fps_text = pygame.font.Font(None, 24).render(
                f"FPS: {int(self.clock.get_fps())}", True, (255, 255, 255)
            )
            self.screen.blit(fps_text, (10, SCREEN_HEIGHT - 30))
        
        pygame.display.flip()


def main():
    """게임 진입점"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
