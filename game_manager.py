# -*- coding: utf-8 -*-
"""
게임 매니저 (Game Manager)
게임 로직을 총괄하고 게임플레이를 관리합니다.
"""

import random
from typing import List, Optional

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    ANIMAL_IMAGES, SPAWN_Y, MOVE_SPEED,
    GAME_OVER_Y, GAME_OVER_X_MARGIN, PLATFORM_Y,
    GameState
)
from physics_manager import PhysicsManager
from animal import Animal, AnimalState
from platform import Platform
from camera import Camera


class GameManager:
    """
    게임 로직 관리 클래스
    - 동물 스폰 및 관리
    - 플레이어 입력 처리
    - 점수 계산
    - 게임 오버 판정
    """
    
    def __init__(self):
        """게임 매니저를 초기화합니다."""
        self.physics_manager = PhysicsManager()
        self.camera = Camera()
        self.platform: Optional[Platform] = None
        
        # 동물 관련
        self.animals: List[Animal] = []
        self.current_animal: Optional[Animal] = None
        self.next_animal_name: str = ""
        
        # 게임 상태
        self.state = GameState.MENU
        self.score = 0
        self.max_height = 0
        self.tower_height = 0
        
        # 입력 상태
        self.moving_left = False
        self.moving_right = False
    
    def start_game(self):
        """새 게임을 시작합니다."""
        # 기존 객체 정리
        self._cleanup()
        
        # 물리 공간 초기화
        self.physics_manager = PhysicsManager()
        self.camera = Camera()
        
        # 플랫폼 생성
        self.platform = Platform(self.physics_manager)
        
        # 상태 초기화
        self.animals = []
        self.score = 0
        self.max_height = 0
        self.tower_height = 0
        
        # 첫 번째와 두 번째 동물 결정
        self.next_animal_name = random.choice(ANIMAL_IMAGES)
        self._spawn_next_animal()
        
        self.state = GameState.PLAYING
    
    def _cleanup(self):
        """게임 객체들을 정리합니다."""
        for animal in self.animals:
            animal.cleanup()
        self.animals.clear()
        
        if self.current_animal:
            self.current_animal.cleanup()
            self.current_animal = None
        
        self.physics_manager.clear()
    
    def _spawn_next_animal(self):
        """다음 동물을 스폰합니다."""
        # 현재 동물 설정
        animal_name = self.next_animal_name
        
        # 다음 동물 미리 선택
        self.next_animal_name = random.choice(ANIMAL_IMAGES)
        
        # 스폰 위치 계산 (탑 위쪽에 충분한 여유를 두고)
        spawn_x = SCREEN_WIDTH / 2
        spawn_y = SPAWN_Y
        
        # 탑이 높으면 더 위에서 스폰
        if self.tower_height > 100:
            spawn_y = min(spawn_y, PLATFORM_Y - self.tower_height - 150)
        
        # 새 동물 생성 (조종 가능한 상태)
        self.current_animal = Animal(
            animal_name, 
            self.physics_manager,
            spawn_x, spawn_y,
            is_static=True
        )
    
    def handle_input(self, keys_pressed: dict, key_down_event=None):
        """
        플레이어 입력을 처리합니다.
        
        Args:
            keys_pressed: 현재 눌린 키 상태
            key_down_event: 키 다운 이벤트 (옵션)
        """
        if self.state != GameState.PLAYING:
            return
        
        if not self.current_animal:
            return
        
        # 좌우 이동
        if keys_pressed.get('left', False):
            self.current_animal.move(-MOVE_SPEED)
        if keys_pressed.get('right', False):
            self.current_animal.move(MOVE_SPEED)
        
        # 드롭 (스페이스바 또는 아래 화살표)
        if key_down_event in ['space', 'down']:
            self._drop_current_animal()
    
    def _drop_current_animal(self):
        """현재 동물을 떨어뜨립니다."""
        if not self.current_animal:
            return
        
        if self.current_animal.state != AnimalState.CONTROLLED:
            return
        
        # 동물 드롭
        self.current_animal.drop()
        
        # 동물 리스트에 추가
        self.animals.append(self.current_animal)
        self.current_animal = None
    
    def update(self, dt: float):
        """
        게임 상태를 업데이트합니다.
        
        Args:
            dt: 델타 타임 (초)
        """
        if self.state != GameState.PLAYING:
            return
        
        # 물리 시뮬레이션
        self.physics_manager.step(dt)
        
        # 동물 업데이트
        settled_count = 0
        animals_to_remove = []
        
        for animal in self.animals:
            animal.update(dt)
            
            if animal.state == AnimalState.SETTLED:
                settled_count += 1
            
            # 게임 오버 체크 (화면 밖으로 떨어짐)
            pos = animal.position
            if pos[1] > GAME_OVER_Y:
                self._game_over()
                return
            
            # 옆으로 너무 멀리 벗어난 경우도 제거 (옵션)
            if pos[0] < -GAME_OVER_X_MARGIN or pos[0] > SCREEN_WIDTH + GAME_OVER_X_MARGIN:
                animals_to_remove.append(animal)
        
        # 벗어난 동물 제거
        for animal in animals_to_remove:
            animal.cleanup()
            self.animals.remove(animal)
        
        # 점수 계산
        self.score = settled_count
        
        # 탑 높이 계산
        self._calculate_tower_height()
        
        # 현재 동물이 없고 게임 진행 중이면 새 동물 스폰
        if self.current_animal is None and self.state == GameState.PLAYING:
            # 마지막 동물이 안착했는지 확인
            all_settled = all(a.state == AnimalState.SETTLED for a in self.animals)
            if all_settled or len(self.animals) == 0:
                self._spawn_next_animal()
        
        # 카메라 업데이트
        current_y = SPAWN_Y
        if self.current_animal:
            current_y = self.current_animal.y
        self.camera.update(self.tower_height, current_y, dt)
    
    def _calculate_tower_height(self):
        """탑 높이를 계산합니다."""
        if not self.animals:
            self.tower_height = 0
            return
        
        # 가장 높은(Y가 작은) 동물의 위치
        min_y = PLATFORM_Y
        for animal in self.animals:
            if animal.state == AnimalState.SETTLED:
                y = animal.y - animal.height / 2
                if y < min_y:
                    min_y = y
        
        self.tower_height = max(0, PLATFORM_Y - min_y)
        self.max_height = max(self.max_height, self.tower_height)
    
    def _game_over(self):
        """게임 오버 처리"""
        self.state = GameState.GAME_OVER
    
    def draw(self, screen):
        """
        게임 객체들을 화면에 그립니다.
        
        Args:
            screen: Pygame 화면
        """
        # 플랫폼
        if self.platform:
            self.platform.draw(screen, self.camera)
        
        # 쌓인 동물들
        for animal in self.animals:
            animal.draw(screen, self.camera)
        
        # 현재 조종 중인 동물
        if self.current_animal:
            self.current_animal.draw(screen, self.camera)
    
    def draw_debug(self, screen):
        """디버그 정보를 그립니다."""
        for animal in self.animals:
            animal.draw_debug(screen, self.camera)
        
        if self.current_animal:
            self.current_animal.draw_debug(screen, self.camera)
