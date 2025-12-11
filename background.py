# -*- coding: utf-8 -*-
"""
배경 클래스 (Background Class)
하늘과 구름 배경을 렌더링합니다.
"""

import pygame
import math
import random
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    SKY_BLUE, SKY_BLUE_LIGHT, WHITE
)


class Cloud:
    """간단한 구름 오브젝트"""
    
    def __init__(self, x: float, y: float, scale: float):
        self.x = x
        self.y = y
        self.scale = scale
        self.speed = random.uniform(5, 15)  # 이동 속도
    
    def update(self, dt: float, camera_offset_y: float):
        """구름 위치 업데이트 (천천히 이동)"""
        self.x += self.speed * dt
        if self.x > SCREEN_WIDTH + 100:
            self.x = -100
    
    def draw(self, screen: pygame.Surface):
        """구름 그리기"""
        # 여러 원으로 구름 모양 생성
        base_radius = int(25 * self.scale)
        
        # 구름 중심 부분
        pygame.draw.circle(screen, WHITE, 
                          (int(self.x), int(self.y)), 
                          base_radius)
        pygame.draw.circle(screen, WHITE, 
                          (int(self.x - base_radius * 0.7), int(self.y + 5)), 
                          int(base_radius * 0.8))
        pygame.draw.circle(screen, WHITE, 
                          (int(self.x + base_radius * 0.7), int(self.y + 5)), 
                          int(base_radius * 0.8))
        pygame.draw.circle(screen, WHITE, 
                          (int(self.x - base_radius * 0.3), int(self.y - base_radius * 0.4)), 
                          int(base_radius * 0.6))
        pygame.draw.circle(screen, WHITE, 
                          (int(self.x + base_radius * 0.4), int(self.y - base_radius * 0.3)), 
                          int(base_radius * 0.7))


class Background:
    """
    게임 배경 렌더러
    - 그라데이션 하늘
    - 움직이는 구름
    """
    
    def __init__(self):
        """배경을 초기화합니다."""
        self.clouds = []
        self._generate_clouds()
        
        # 하늘 그라데이션 캐시
        self.sky_surface = None
        self._create_sky_gradient()
    
    def _generate_clouds(self):
        """랜덤 구름 생성"""
        for _ in range(6):
            x = random.uniform(0, SCREEN_WIDTH)
            y = random.uniform(50, SCREEN_HEIGHT * 0.6)
            scale = random.uniform(0.8, 1.5)
            self.clouds.append(Cloud(x, y, scale))
    
    def _create_sky_gradient(self):
        """하늘 그라데이션 서피스 생성"""
        self.sky_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        for y in range(SCREEN_HEIGHT):
            # 위에서 아래로 그라데이션
            ratio = y / SCREEN_HEIGHT
            r = int(SKY_BLUE_LIGHT[0] + (SKY_BLUE[0] - SKY_BLUE_LIGHT[0]) * ratio)
            g = int(SKY_BLUE_LIGHT[1] + (SKY_BLUE[1] - SKY_BLUE_LIGHT[1]) * ratio)
            b = int(SKY_BLUE_LIGHT[2] + (SKY_BLUE[2] - SKY_BLUE_LIGHT[2]) * ratio)
            pygame.draw.line(self.sky_surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    def update(self, dt: float, camera_offset_y: float = 0):
        """
        배경 업데이트
        
        Args:
            dt: 델타 타임
            camera_offset_y: 카메라 Y 오프셋 (패럴랙스용)
        """
        for cloud in self.clouds:
            cloud.update(dt, camera_offset_y)
    
    def draw(self, screen: pygame.Surface):
        """
        배경을 화면에 렌더링합니다.
        
        Args:
            screen: Pygame 화면 Surface
        """
        # 하늘 그라데이션
        if self.sky_surface:
            screen.blit(self.sky_surface, (0, 0))
        else:
            screen.fill(SKY_BLUE)
        
        # 구름
        for cloud in self.clouds:
            cloud.draw(screen)
