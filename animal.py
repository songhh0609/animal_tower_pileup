# -*- coding: utf-8 -*-
"""
동물 클래스 (Animal Class)
물리 기반 동물 오브젝트를 정의합니다.
"""

import pygame
import pymunk
import os
from typing import List, Tuple, Optional

from constants import (
    IMAGES_PATH, ANIMAL_SCALE,
    ANIMAL_MASS, ANIMAL_FRICTION, ANIMAL_ELASTICITY,
    SETTLE_VELOCITY_THRESHOLD
)
from polygon_extractor import extract_polygon_from_surface, get_fallback_polygon


class AnimalState:
    """동물 상태 열거형"""
    CONTROLLED = "controlled"  # 플레이어가 조종 중
    FALLING = "falling"        # 떨어지는 중
    SETTLED = "settled"        # 안착됨


class Animal:
    """
    물리 기반 동물 오브젝트 클래스
    - Pymunk 바디와 폴리곤 셰이프
    - Pygame 이미지 렌더링
    - 상태 관리 (조종 중, 떨어지는 중, 안착됨)
    """
    
    # 클래스 레벨 캐시 (이미지, 폴리곤)
    _image_cache = {}
    _polygon_cache = {}
    
    def __init__(self, image_name: str, physics_manager, 
                 x: float, y: float, is_static: bool = False):
        """
        동물 오브젝트를 초기화합니다.
        
        Args:
            image_name: 이미지 파일명 (예: "bear.png")
            physics_manager: PhysicsManager 인스턴스
            x: 초기 X 좌표
            y: 초기 Y 좌표
            is_static: 정적 바디 여부 (조종 중일 때 True)
        """
        self.image_name = image_name
        self.physics_manager = physics_manager
        self.state = AnimalState.CONTROLLED if is_static else AnimalState.FALLING
        
        # 이미지 로드 (캐시 사용)
        self.image = self._load_image(image_name)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        # 폴리곤 추출 (캐시 사용)
        self.polygon = self._get_polygon(image_name)
        
        # Pymunk 바디 & 셰이프 생성
        self.body: Optional[pymunk.Body] = None
        self.shape: Optional[pymunk.Poly] = None
        self.is_static = is_static
        
        self._create_physics_body(x, y, is_static)
        
        # 안착 타이머
        self.settle_timer = 0.0
    
    @classmethod
    def _load_image(cls, image_name: str) -> pygame.Surface:
        """이미지를 로드하고 스케일링합니다 (캐시 사용)."""
        if image_name in cls._image_cache:
            return cls._image_cache[image_name]
        
        path = os.path.join(IMAGES_PATH, image_name)
        original = pygame.image.load(path).convert_alpha()
        
        # 스케일링
        new_width = int(original.get_width() * ANIMAL_SCALE)
        new_height = int(original.get_height() * ANIMAL_SCALE)
        scaled = pygame.transform.smoothscale(original, (new_width, new_height))
        
        cls._image_cache[image_name] = scaled
        return scaled
    
    @classmethod
    def _get_polygon(cls, image_name: str) -> List[Tuple[float, float]]:
        """이미지에서 폴리곤을 추출합니다 (캐시 사용)."""
        if image_name in cls._polygon_cache:
            return cls._polygon_cache[image_name]
        
        image = cls._load_image(image_name)
        
        try:
            polygon = extract_polygon_from_surface(image, 
                                                   simplify_tolerance=3.0, 
                                                   max_vertices=12)
        except Exception as e:
            print(f"폴리곤 추출 실패 ({image_name}): {e}")
            polygon = get_fallback_polygon(image.get_width(), image.get_height())
        
        cls._polygon_cache[image_name] = polygon
        return polygon
    
    def _create_physics_body(self, x: float, y: float, is_static: bool):
        """Pymunk 물리 바디를 생성합니다."""
        if is_static:
            # 조종 중일 때는 Kinematic 바디 (중력 영향 X, 수동 이동 가능)
            self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        else:
            # 동적 바디 (중력 영향 O)
            moment = pymunk.moment_for_poly(ANIMAL_MASS, self.polygon)
            self.body = pymunk.Body(ANIMAL_MASS, moment)
        
        self.body.position = (x, y)
        
        # 폴리곤 셰이프 생성
        try:
            self.shape = pymunk.Poly(self.body, self.polygon)
        except Exception as e:
            print(f"폴리곤 셰이프 생성 실패: {e}")
            # 폴백: 박스 셰이프
            hw = self.width / 2 * 0.9
            hh = self.height / 2 * 0.9
            self.shape = pymunk.Poly(self.body, [
                (-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)
            ])
        
        self.shape.friction = ANIMAL_FRICTION
        self.shape.elasticity = ANIMAL_ELASTICITY
        self.shape.collision_type = 1  # 동물 타입
        
        # 물리 공간에 추가
        self.physics_manager.add_body(self.body, [self.shape])
    
    def drop(self):
        """동물을 떨어뜨립니다 (Kinematic -> Dynamic 변환)."""
        if self.state != AnimalState.CONTROLLED:
            return
        
        # 현재 위치 저장
        pos = self.body.position
        
        # 기존 바디/셰이프 제거
        self.physics_manager.remove_body(self.body, [self.shape])
        
        # 동적 바디로 재생성
        self._create_physics_body(pos.x, pos.y, is_static=False)
        self.is_static = False
        self.state = AnimalState.FALLING
    
    def move(self, dx: float):
        """조종 중일 때 좌우로 이동합니다."""
        if self.state == AnimalState.CONTROLLED and self.body:
            self.body.position = (self.body.position.x + dx, self.body.position.y)
    
    def update(self, dt: float) -> bool:
        """
        동물 상태를 업데이트합니다.
        
        Args:
            dt: 델타 타임 (초)
        
        Returns:
            True if 안착됨
        """
        if self.state == AnimalState.CONTROLLED:
            return False
        
        if self.state == AnimalState.SETTLED:
            return True
        
        # 속도 체크로 안착 판정
        if self.body:
            velocity = self.body.velocity
            speed = (velocity.x ** 2 + velocity.y ** 2) ** 0.5
            
            if speed < SETTLE_VELOCITY_THRESHOLD:
                self.settle_timer += dt
                if self.settle_timer > 0.3:  # 0.3초 이상 느린 상태
                    self.state = AnimalState.SETTLED
                    return True
            else:
                self.settle_timer = 0
        
        return False
    
    def draw(self, screen: pygame.Surface, camera):
        """
        동물을 화면에 렌더링합니다.
        
        Args:
            screen: Pygame 화면 Surface
            camera: Camera 인스턴스 (좌표 변환용)
        """
        if not self.body:
            return
        
        # 월드 좌표에서 스크린 좌표로 변환
        world_pos = self.body.position
        screen_pos = camera.world_to_screen(world_pos.x, world_pos.y)
        
        # 회전 적용
        angle_degrees = -self.body.angle * 180 / 3.14159
        
        # 줌 적용
        zoom = camera.zoom
        scaled_width = int(self.width * zoom)
        scaled_height = int(self.height * zoom)
        
        if scaled_width < 1 or scaled_height < 1:
            return
        
        # 이미지 스케일 및 회전
        scaled_image = pygame.transform.smoothscale(self.image, 
                                                     (scaled_width, scaled_height))
        rotated_image = pygame.transform.rotate(scaled_image, angle_degrees)
        
        # 중심 위치 계산
        rect = rotated_image.get_rect(center=(int(screen_pos[0]), int(screen_pos[1])))
        screen.blit(rotated_image, rect)
    
    def draw_debug(self, screen: pygame.Surface, camera):
        """디버그용 폴리곤 윤곽선을 그립니다."""
        if not self.body or not self.shape:
            return
        
        # 셰이프의 실제 꼭짓점 가져오기
        vertices = self.shape.get_vertices()
        
        # 월드 좌표로 변환
        world_vertices = []
        for v in vertices:
            rotated = v.rotated(self.body.angle)
            world_x = self.body.position.x + rotated.x
            world_y = self.body.position.y + rotated.y
            screen_pos = camera.world_to_screen(world_x, world_y)
            world_vertices.append(screen_pos)
        
        if len(world_vertices) >= 3:
            pygame.draw.polygon(screen, (255, 0, 0), world_vertices, 2)
    
    @property
    def position(self) -> Tuple[float, float]:
        """현재 위치를 반환합니다."""
        if self.body:
            return (self.body.position.x, self.body.position.y)
        return (0, 0)
    
    @property
    def y(self) -> float:
        """Y 좌표를 반환합니다."""
        if self.body:
            return self.body.position.y
        return 0
    
    def cleanup(self):
        """물리 공간에서 제거합니다."""
        if self.body and self.shape:
            self.physics_manager.remove_body(self.body, [self.shape])
            self.body = None
            self.shape = None
