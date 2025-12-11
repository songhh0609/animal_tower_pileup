# -*- coding: utf-8 -*-
"""
물리 매니저 (Physics Manager)
Pymunk 물리 공간을 관리하고 시뮬레이션을 처리합니다.
"""

import pymunk
from constants import (
    GRAVITY, DAMPING, PHYSICS_STEPS,
    PLATFORM_FRICTION, PLATFORM_ELASTICITY
)


class PhysicsManager:
    """
    Pymunk 물리 엔진을 관리하는 클래스
    - 물리 공간(space) 생성 및 설정
    - 바디/셰이프 추가/제거
    - 물리 시뮬레이션 스텝 실행
    """
    
    def __init__(self):
        """물리 공간을 초기화합니다."""
        self.space = pymunk.Space()
        self.space.gravity = GRAVITY
        self.space.damping = DAMPING
        
        # 충돌 핸들러 설정 (필요시 확장)
        self.setup_collision_handlers()
    
    def setup_collision_handlers(self):
        """충돌 핸들러를 설정합니다."""
        # 동물-동물 충돌 (타입 1)
        # 동물-플랫폼 충돌 (타입 1, 2)
        # 필요에 따라 콜백 추가 가능
        pass
    
    def add_body(self, body: pymunk.Body, shapes: list):
        """
        바디와 셰이프를 물리 공간에 추가합니다.
        
        Args:
            body: Pymunk Body 객체
            shapes: Pymunk Shape 객체 리스트
        """
        self.space.add(body)
        for shape in shapes:
            self.space.add(shape)
    
    def remove_body(self, body: pymunk.Body, shapes: list):
        """
        바디와 셰이프를 물리 공간에서 제거합니다.
        
        Args:
            body: Pymunk Body 객체
            shapes: Pymunk Shape 객체 리스트
        """
        for shape in shapes:
            if shape in self.space.shapes:
                self.space.remove(shape)
        if body in self.space.bodies:
            self.space.remove(body)
    
    def step(self, dt: float):
        """
        물리 시뮬레이션을 한 스텝 진행합니다.
        
        Args:
            dt: 델타 타임 (초)
        """
        # 여러 번 나눠서 시뮬레이션 (정확도 향상)
        step_dt = dt / PHYSICS_STEPS
        for _ in range(PHYSICS_STEPS):
            self.space.step(step_dt)
    
    def create_static_platform(self, x: float, y: float, 
                               width: float, height: float) -> tuple:
        """
        정적 플랫폼을 생성합니다.
        
        Args:
            x: 중심 X 좌표
            y: 중심 Y 좌표
            width: 플랫폼 너비
            height: 플랫폼 높이
        
        Returns:
            (body, shape) 튜플
        """
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = (x, y)
        
        # 사각형 꼭짓점 (중심 기준)
        hw = width / 2
        hh = height / 2
        vertices = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
        
        shape = pymunk.Poly(body, vertices)
        shape.friction = PLATFORM_FRICTION
        shape.elasticity = PLATFORM_ELASTICITY
        shape.collision_type = 2  # 플랫폼 타입
        
        self.space.add(body, shape)
        
        return body, shape
    
    def create_static_walls(self, screen_width: float, screen_height: float):
        """
        화면 양쪽에 보이지 않는 벽을 생성합니다 (옵션).
        
        Args:
            screen_width: 화면 너비
            screen_height: 화면 높이
        
        Returns:
            (left_wall, right_wall) 튜플
        """
        wall_thickness = 50
        wall_height = screen_height * 3
        
        # 왼쪽 벽
        left_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        left_body.position = (-wall_thickness / 2, screen_height / 2)
        left_shape = pymunk.Poly.create_box(left_body, (wall_thickness, wall_height))
        left_shape.friction = 0.5
        left_shape.elasticity = 0.3
        
        # 오른쪽 벽
        right_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        right_body.position = (screen_width + wall_thickness / 2, screen_height / 2)
        right_shape = pymunk.Poly.create_box(right_body, (wall_thickness, wall_height))
        right_shape.friction = 0.5
        right_shape.elasticity = 0.3
        
        self.space.add(left_body, left_shape, right_body, right_shape)
        
        return (left_body, left_shape), (right_body, right_shape)
    
    def clear(self):
        """물리 공간의 모든 객체를 제거합니다."""
        for body in list(self.space.bodies):
            self.space.remove(body)
        for shape in list(self.space.shapes):
            self.space.remove(shape)
        for constraint in list(self.space.constraints):
            self.space.remove(constraint)
