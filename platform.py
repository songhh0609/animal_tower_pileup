# -*- coding: utf-8 -*-
"""
플랫폼 클래스 (Platform Class)
게임의 기본 바닥 플랫폼을 정의합니다.
"""

import pygame
from constants import (
    SCREEN_WIDTH, PLATFORM_WIDTH, PLATFORM_HEIGHT, PLATFORM_Y,
    GRASS_GREEN, GRASS_DARK, GROUND_BROWN
)


class Platform:
    """
    게임 플랫폼 (바닥)
    - 정적 Pymunk 바디
    - 시각적 렌더링 (잔디 스타일)
    """
    
    def __init__(self, physics_manager):
        """
        플랫폼을 초기화합니다.
        
        Args:
            physics_manager: PhysicsManager 인스턴스
        """
        self.physics_manager = physics_manager
        self.x = SCREEN_WIDTH / 2
        self.y = PLATFORM_Y
        self.width = PLATFORM_WIDTH
        self.height = PLATFORM_HEIGHT
        
        # 물리 바디 생성
        self.body, self.shape = physics_manager.create_static_platform(
            self.x, self.y, self.width, self.height
        )
        
        # 시각적 영역 정의
        self.rect = pygame.Rect(
            self.x - self.width / 2,
            self.y - self.height / 2,
            self.width,
            self.height
        )
    
    def draw(self, screen: pygame.Surface, camera):
        """
        플랫폼을 화면에 렌더링합니다.
        
        Args:
            screen: Pygame 화면 Surface
            camera: Camera 인스턴스
        """
        # 화면 좌표로 변환
        left_top = camera.world_to_screen(
            self.x - self.width / 2,
            self.y - self.height / 2
        )
        right_bottom = camera.world_to_screen(
            self.x + self.width / 2,
            self.y + self.height / 2
        )
        
        # 스케일된 크기 계산
        screen_width = right_bottom[0] - left_top[0]
        screen_height = right_bottom[1] - left_top[1]
        
        if screen_width < 1 or screen_height < 1:
            return
        
        # 플랫폼 메인 (갈색)
        platform_rect = pygame.Rect(
            int(left_top[0]),
            int(left_top[1]),
            int(screen_width),
            int(screen_height)
        )
        pygame.draw.rect(screen, GROUND_BROWN, platform_rect)
        
        # 잔디 레이어 (상단)
        grass_height = max(2, int(screen_height * 0.4))
        grass_rect = pygame.Rect(
            int(left_top[0]),
            int(left_top[1]),
            int(screen_width),
            grass_height
        )
        pygame.draw.rect(screen, GRASS_GREEN, grass_rect)
        
        # 잔디 하이라이트
        highlight_rect = pygame.Rect(
            int(left_top[0]),
            int(left_top[1]),
            int(screen_width),
            max(1, grass_height // 3)
        )
        pygame.draw.rect(screen, GRASS_DARK, highlight_rect)
        
        # 테두리
        pygame.draw.rect(screen, GRASS_DARK, platform_rect, 2)
    
    def draw_ground(self, screen: pygame.Surface, camera):
        """
        플랫폼 아래 땅을 그립니다.
        
        Args:
            screen: Pygame 화면 Surface
            camera: Camera 인스턴스
        """
        # 화면 하단 영역을 땅으로 채움
        ground_top_world = self.y + self.height / 2
        ground_top_screen = camera.world_to_screen(0, ground_top_world)[1]
        
        if ground_top_screen < screen.get_height():
            ground_rect = pygame.Rect(
                0,
                int(ground_top_screen),
                screen.get_width(),
                screen.get_height() - int(ground_top_screen)
            )
            pygame.draw.rect(screen, GROUND_BROWN, ground_rect)
