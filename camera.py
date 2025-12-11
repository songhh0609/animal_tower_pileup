# -*- coding: utf-8 -*-
"""
카메라 클래스 (Camera Class)
동적 줌아웃과 부드러운 카메라 추적을 처리합니다.
"""

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    MIN_ZOOM, MAX_ZOOM, ZOOM_SPEED, CAMERA_SMOOTH,
    PLATFORM_Y
)


class Camera:
    """
    동적 카메라 시스템
    - 탑 높이에 따른 줌아웃
    - 부드러운 수직 이동
    - 월드 좌표 <-> 스크린 좌표 변환
    """
    
    def __init__(self):
        """카메라를 초기화합니다."""
        self.zoom = MAX_ZOOM  # 현재 줌 레벨
        self.target_zoom = MAX_ZOOM  # 목표 줌 레벨
        
        # 카메라 중심 위치 (월드 좌표)
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2
        
        self.target_center_y = self.center_y
        
        # 기본 위치 (플랫폼 기준)
        self.base_y = PLATFORM_Y
    
    def update(self, tower_height: float, current_animal_y: float, dt: float):
        """
        카메라 상태를 업데이트합니다.
        
        Args:
            tower_height: 현재 탑의 높이 (픽셀)
            current_animal_y: 현재 조종 중인 동물의 Y 좌표
            dt: 델타 타임
        """
        # 줌 레벨 계산 (탑이 높을수록 줌아웃)
        # 탑 높이 0 -> 줌 1.0, 탑 높이 증가 -> 줌 감소
        height_factor = tower_height / 800  # 800픽셀 기준
        self.target_zoom = max(MIN_ZOOM, MAX_ZOOM - height_factor * 0.3)
        
        # 줌 부드럽게 보간
        self.zoom += (self.target_zoom - self.zoom) * ZOOM_SPEED
        
        # 카메라 Y 위치 계산
        # 탑 꼭대기와 현재 동물이 모두 화면에 보이도록
        visible_height = SCREEN_HEIGHT / self.zoom
        
        # 플랫폼 위치 기준으로 필요한 영역 계산
        min_y = min(current_animal_y, self.base_y - tower_height)
        max_y = self.base_y + 50
        
        # 카메라 중심은 보여야 할 영역의 중간 약간 아래
        content_height = max_y - min_y
        
        if content_height > visible_height * 0.8:
            # 컨텐츠가 화면보다 클 때 - 줌 아웃 필요
            self.target_center_y = (min_y + max_y) / 2
        else:
            # 컨텐츠가 화면에 들어올 때 - 기본 위치 유지
            self.target_center_y = SCREEN_HEIGHT / 2
        
        # 카메라 Y 부드럽게 보간
        self.center_y += (self.target_center_y - self.center_y) * CAMERA_SMOOTH
    
    def world_to_screen(self, world_x: float, world_y: float) -> tuple:
        """
        월드 좌표를 스크린 좌표로 변환합니다.
        
        Args:
            world_x: 월드 X 좌표
            world_y: 월드 Y 좌표
        
        Returns:
            (screen_x, screen_y) 튜플
        """
        # 카메라 중심 기준으로 오프셋 계산
        offset_x = world_x - self.center_x
        offset_y = world_y - self.center_y
        
        # 줌 적용
        screen_x = SCREEN_WIDTH / 2 + offset_x * self.zoom
        screen_y = SCREEN_HEIGHT / 2 + offset_y * self.zoom
        
        return (screen_x, screen_y)
    
    def screen_to_world(self, screen_x: float, screen_y: float) -> tuple:
        """
        스크린 좌표를 월드 좌표로 변환합니다.
        
        Args:
            screen_x: 스크린 X 좌표
            screen_y: 스크린 Y 좌표
        
        Returns:
            (world_x, world_y) 튜플
        """
        # 역변환
        offset_x = (screen_x - SCREEN_WIDTH / 2) / self.zoom
        offset_y = (screen_y - SCREEN_HEIGHT / 2) / self.zoom
        
        world_x = self.center_x + offset_x
        world_y = self.center_y + offset_y
        
        return (world_x, world_y)
    
    def reset(self):
        """카메라를 초기 상태로 리셋합니다."""
        self.zoom = MAX_ZOOM
        self.target_zoom = MAX_ZOOM
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2
        self.target_center_y = self.center_y
