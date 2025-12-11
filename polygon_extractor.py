# -*- coding: utf-8 -*-
"""
다각형 추출기 (Polygon Extractor)
이미지의 투명하지 않은 영역에서 충돌 다각형을 추출합니다.
"""

import pygame
import math
from typing import List, Tuple

def extract_polygon_from_surface(surface: pygame.Surface, 
                                  simplify_tolerance: float = 2.0,
                                  max_vertices: int = 16) -> List[Tuple[float, float]]:
    """
    Pygame Surface에서 다각형 윤곽선을 추출합니다.
    
    Args:
        surface: 알파 채널이 있는 Pygame Surface
        simplify_tolerance: 다각형 단순화 허용치 (높을수록 단순한 다각형)
        max_vertices: 최대 꼭짓점 수
    
    Returns:
        중심점 기준 (x, y) 좌표 리스트
    """
    width = surface.get_width()
    height = surface.get_height()
    
    # 알파 마스크 생성 - 투명하지 않은 픽셀 찾기
    mask = pygame.mask.from_surface(surface, threshold=50)
    
    # 윤곽선 추출
    outline = mask.outline(every=2)  # every=2로 포인트 줄이기
    
    if len(outline) < 3:
        # 윤곽선이 너무 적으면 기본 사각형 반환
        hw, hh = width / 2, height / 2
        return [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
    
    # 중심점 기준으로 좌표 변환
    center_x = width / 2
    center_y = height / 2
    
    centered_outline = [(x - center_x, y - center_y) for x, y in outline]
    
    # 다각형 단순화 (Douglas-Peucker 알고리즘 기반)
    simplified = simplify_polygon(centered_outline, simplify_tolerance)
    
    # 볼록 껍질로 변환 (Pymunk은 볼록 다각형만 지원)
    convex = convex_hull(simplified)
    
    # 최대 꼭짓점 수 제한
    if len(convex) > max_vertices:
        convex = reduce_vertices(convex, max_vertices)
    
    # Pymunk은 반시계 방향 필요
    if not is_counter_clockwise(convex):
        convex = convex[::-1]
    
    return convex


def simplify_polygon(points: List[Tuple[float, float]], 
                     tolerance: float) -> List[Tuple[float, float]]:
    """
    Douglas-Peucker 알고리즘으로 다각형을 단순화합니다.
    """
    if len(points) <= 3:
        return points
    
    # 가장 먼 점 찾기
    max_dist = 0
    max_idx = 0
    
    start = points[0]
    end = points[-1]
    
    for i in range(1, len(points) - 1):
        dist = perpendicular_distance(points[i], start, end)
        if dist > max_dist:
            max_dist = dist
            max_idx = i
    
    # 허용치보다 멀면 분할하여 재귀
    if max_dist > tolerance:
        left = simplify_polygon(points[:max_idx + 1], tolerance)
        right = simplify_polygon(points[max_idx:], tolerance)
        return left[:-1] + right
    else:
        return [start, end]


def perpendicular_distance(point: Tuple[float, float],
                          line_start: Tuple[float, float],
                          line_end: Tuple[float, float]) -> float:
    """점에서 선분까지의 수직 거리를 계산합니다."""
    x, y = point
    x1, y1 = line_start
    x2, y2 = line_end
    
    dx = x2 - x1
    dy = y2 - y1
    
    if dx == 0 and dy == 0:
        return math.sqrt((x - x1) ** 2 + (y - y1) ** 2)
    
    t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    
    return math.sqrt((x - proj_x) ** 2 + (y - proj_y) ** 2)


def convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Graham scan 알고리즘으로 볼록 껍질을 계산합니다.
    """
    if len(points) < 3:
        return points
    
    # 가장 아래-왼쪽 점을 시작점으로
    start = min(points, key=lambda p: (p[1], p[0]))
    
    def polar_angle(p):
        if p == start:
            return -math.pi
        return math.atan2(p[1] - start[1], p[0] - start[0])
    
    # 극좌표 각도로 정렬
    sorted_points = sorted(points, key=polar_angle)
    
    # 스택으로 볼록 껍질 구성
    hull = []
    for p in sorted_points:
        while len(hull) >= 2 and cross_product(hull[-2], hull[-1], p) <= 0:
            hull.pop()
        hull.append(p)
    
    return hull


def cross_product(o: Tuple[float, float], 
                  a: Tuple[float, float], 
                  b: Tuple[float, float]) -> float:
    """세 점의 외적을 계산합니다 (방향 판별용)."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def is_counter_clockwise(points: List[Tuple[float, float]]) -> bool:
    """다각형이 반시계 방향인지 확인합니다."""
    area = 0
    n = len(points)
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    return area > 0


def reduce_vertices(points: List[Tuple[float, float]], 
                    max_count: int) -> List[Tuple[float, float]]:
    """
    꼭짓점 수를 줄입니다 (균등 샘플링).
    """
    if len(points) <= max_count:
        return points
    
    step = len(points) / max_count
    result = []
    for i in range(max_count):
        idx = int(i * step)
        result.append(points[idx])
    
    return result


def get_fallback_polygon(width: float, height: float) -> List[Tuple[float, float]]:
    """기본 타원형 다각형을 생성합니다 (폴백용)."""
    points = []
    num_points = 8
    hw = width / 2 * 0.9
    hh = height / 2 * 0.9
    
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        x = hw * math.cos(angle)
        y = hh * math.sin(angle)
        points.append((x, y))
    
    return points
