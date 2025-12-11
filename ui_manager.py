# -*- coding: utf-8 -*-
"""
UI 매니저 (UI Manager)
점수, 다음 동물 미리보기, 타이틀/게임오버 화면을 관리합니다.
"""

import pygame
import os
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    IMAGES_PATH, ANIMAL_IMAGES, ANIMAL_SCALE,
    NEXT_PREVIEW_SIZE, NEXT_PREVIEW_POS, SCORE_POS,
    WHITE, BLACK, UI_BG, UI_BORDER, SCORE_COLOR,
    TITLE_COLOR, BUTTON_COLOR, BUTTON_HOVER, BUTTON_TEXT,
    SKY_BLUE_LIGHT
)


class Button:
    """간단한 버튼 클래스"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, font: pygame.font.Font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False
    
    def update(self, mouse_pos: tuple):
        """마우스 호버 상태 업데이트"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos: tuple, mouse_pressed: bool) -> bool:
        """클릭 여부 확인"""
        return self.rect.collidepoint(mouse_pos) and mouse_pressed
    
    def draw(self, screen: pygame.Surface):
        """버튼 그리기"""
        color = BUTTON_HOVER if self.is_hovered else BUTTON_COLOR
        
        # 버튼 배경 (둥근 모서리)
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 3, border_radius=10)
        
        # 텍스트
        text_surface = self.font.render(self.text, True, BUTTON_TEXT)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class UIManager:
    """
    게임 UI 관리 클래스
    - 점수 표시
    - 다음 동물 미리보기
    - 메뉴/게임오버 화면
    """
    
    def __init__(self):
        """UI 매니저를 초기화합니다."""
        pygame.font.init()
        
        # 폰트 설정
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        # 한글 폰트 시도 (시스템에 있는 경우)
        try:
            self.font_korean = pygame.font.SysFont('malgungothic', 36)
            self.font_korean_large = pygame.font.SysFont('malgungothic', 64)
        except:
            self.font_korean = self.font_medium
            self.font_korean_large = self.font_large
        
        # 버튼
        self.start_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50,
            200, 60, "START", self.font_medium
        )
        self.restart_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80,
            200, 60, "RESTART", self.font_medium
        )
        
        # 미리보기 이미지 캐시
        self.preview_images = {}
        self._load_preview_images()
    
    def _load_preview_images(self):
        """미리보기용 작은 이미지들을 로드합니다."""
        preview_scale = 0.08  # 미리보기용 작은 스케일
        
        for image_name in ANIMAL_IMAGES:
            try:
                path = os.path.join(IMAGES_PATH, image_name)
                original = pygame.image.load(path).convert_alpha()
                
                # 미리보기 크기에 맞게 조정
                aspect = original.get_width() / original.get_height()
                preview_height = NEXT_PREVIEW_SIZE[1] - 20
                preview_width = int(preview_height * aspect)
                
                if preview_width > NEXT_PREVIEW_SIZE[0] - 20:
                    preview_width = NEXT_PREVIEW_SIZE[0] - 20
                    preview_height = int(preview_width / aspect)
                
                scaled = pygame.transform.smoothscale(original, (preview_width, preview_height))
                self.preview_images[image_name] = scaled
            except Exception as e:
                print(f"미리보기 이미지 로드 실패 ({image_name}): {e}")
    
    def draw_score(self, screen: pygame.Surface, score: int, height: float):
        """
        점수를 화면에 표시합니다.
        
        Args:
            screen: Pygame 화면
            score: 현재 점수
            height: 현재 탑 높이
        """
        # 점수 배경
        bg_rect = pygame.Rect(SCORE_POS[0] - 10, SCORE_POS[1] - 5, 180, 70)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill(UI_BG)
        screen.blit(bg_surface, bg_rect)
        pygame.draw.rect(screen, UI_BORDER, bg_rect, 2, border_radius=5)
        
        # 점수 텍스트
        score_text = self.font_small.render(f"Score: {score}", True, SCORE_COLOR)
        screen.blit(score_text, (SCORE_POS[0], SCORE_POS[1]))
        
        # 높이 표시
        height_text = self.font_small.render(f"Height: {int(height)}px", True, WHITE)
        screen.blit(height_text, (SCORE_POS[0], SCORE_POS[1] + 30))
    
    def draw_next_preview(self, screen: pygame.Surface, next_animal_name: str):
        """
        다음 동물 미리보기를 표시합니다.
        
        Args:
            screen: Pygame 화면
            next_animal_name: 다음 동물 이미지 이름
        """
        x, y = NEXT_PREVIEW_POS
        w, h = NEXT_PREVIEW_SIZE
        
        # 배경 박스
        bg_rect = pygame.Rect(x, y, w, h + 30)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill(UI_BG)
        screen.blit(bg_surface, bg_rect)
        pygame.draw.rect(screen, UI_BORDER, bg_rect, 2, border_radius=5)
        
        # "NEXT" 라벨
        next_label = self.font_small.render("NEXT", True, WHITE)
        label_rect = next_label.get_rect(centerx=x + w // 2, top=y + 5)
        screen.blit(next_label, label_rect)
        
        # 동물 이미지
        if next_animal_name in self.preview_images:
            preview = self.preview_images[next_animal_name]
            img_rect = preview.get_rect(center=(x + w // 2, y + 30 + h // 2))
            screen.blit(preview, img_rect)
    
    def draw_title_screen(self, screen: pygame.Surface, mouse_pos: tuple):
        """
        타이틀 화면을 그립니다.
        
        Args:
            screen: Pygame 화면
            mouse_pos: 마우스 위치
        """
        # 반투명 오버레이
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 180))
        screen.blit(overlay, (0, 0))
        
        # 타이틀
        title_text = self.font_korean_large.render("동물 탑 쌓기", True, TITLE_COLOR)
        title_rect = title_text.get_rect(centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 3)
        screen.blit(title_text, title_rect)
        
        # 부제목
        subtitle = self.font_korean.render("Animal Tower Stacking", True, TITLE_COLOR)
        subtitle_rect = subtitle.get_rect(centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 3 + 60)
        screen.blit(subtitle, subtitle_rect)
        
        # 시작 버튼
        self.start_button.update(mouse_pos)
        self.start_button.draw(screen)
        
        # 조작법 안내
        controls = self.font_small.render("← → : Move   |   SPACE / ↓ : Drop", True, BLACK)
        controls_rect = controls.get_rect(centerx=SCREEN_WIDTH // 2, bottom=SCREEN_HEIGHT - 30)
        screen.blit(controls, controls_rect)
    
    def draw_game_over_screen(self, screen: pygame.Surface, score: int, 
                              height: float, mouse_pos: tuple):
        """
        게임 오버 화면을 그립니다.
        
        Args:
            screen: Pygame 화면
            score: 최종 점수
            height: 최종 높이
            mouse_pos: 마우스 위치
        """
        # 반투명 오버레이
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # 게임 오버 텍스트
        game_over_text = self.font_large.render("GAME OVER", True, WHITE)
        go_rect = game_over_text.get_rect(centerx=SCREEN_WIDTH // 2, 
                                          centery=SCREEN_HEIGHT // 3)
        screen.blit(game_over_text, go_rect)
        
        # 점수 표시
        score_text = self.font_medium.render(f"Score: {score}", True, SCORE_COLOR)
        score_rect = score_text.get_rect(centerx=SCREEN_WIDTH // 2, 
                                         centery=SCREEN_HEIGHT // 2 - 20)
        screen.blit(score_text, score_rect)
        
        # 높이 표시
        height_text = self.font_medium.render(f"Max Height: {int(height)}px", True, WHITE)
        height_rect = height_text.get_rect(centerx=SCREEN_WIDTH // 2, 
                                           centery=SCREEN_HEIGHT // 2 + 30)
        screen.blit(height_text, height_rect)
        
        # 재시작 버튼
        self.restart_button.update(mouse_pos)
        self.restart_button.draw(screen)
    
    def check_start_clicked(self, mouse_pos: tuple, mouse_pressed: bool) -> bool:
        """시작 버튼 클릭 확인"""
        return self.start_button.is_clicked(mouse_pos, mouse_pressed)
    
    def check_restart_clicked(self, mouse_pos: tuple, mouse_pressed: bool) -> bool:
        """재시작 버튼 클릭 확인"""
        return self.restart_button.is_clicked(mouse_pos, mouse_pressed)
