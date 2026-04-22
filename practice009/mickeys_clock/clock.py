import pygame
import os
import math
import datetime
 
 
class MickeyClock:
    def __init__(self, width, height):
        self.width = width
        self.height = height
 
        img_dir = os.path.join(os.path.dirname(__file__), "images")
 
        # Load background clock image (mickeyclock.jpeg)
        bg_path = os.path.join(img_dir, "mickeyclock.jpeg")
        self.bg = pygame.image.load(bg_path)
        self.bg = pygame.transform.scale(self.bg, (width, height))
 
        # Create Mickey hand surface (white glove shape drawn programmatically)
        self.hand_img = self._create_hand_image()
 
        # Clock center
        self.cx = width // 2
        self.cy = height // 2
 
    def _create_hand_image(self):
        """Draw a Mickey Mouse white-glove hand programmatically."""
        hand_w, hand_h = 30, 100
        surf = pygame.Surface((hand_w, hand_h), pygame.SRCALPHA)
 
        # Glove (white oval / rounded rectangle)
        glove_color = (255, 255, 255)
        outline_color = (30, 30, 30)
 
        # Arm / stick part
        arm_rect = pygame.Rect(hand_w // 2 - 5, 30, 10, 70)
        pygame.draw.rect(surf, glove_color, arm_rect, border_radius=5)
        pygame.draw.rect(surf, outline_color, arm_rect, 2, border_radius=5)
 
        # Glove (top circle)
        pygame.draw.ellipse(surf, glove_color, (0, 0, hand_w, 45))
        pygame.draw.ellipse(surf, outline_color, (0, 0, hand_w, 45), 2)
 
        # Finger bumps on top of glove
        for i in range(3):
            fx = 3 + i * 9
            pygame.draw.ellipse(surf, glove_color, (fx, 0, 10, 14))
            pygame.draw.ellipse(surf, outline_color, (fx, 0, 10, 14), 2)
 
        return surf
 
    def _rotate_hand(self, angle_deg, length_factor=1.0):
        """Rotate hand image and return (surface, rect) centered on clock."""
        scaled_h = int(self.hand_img.get_height() * length_factor)
        scaled = pygame.transform.scale(
            self.hand_img,
            (self.hand_img.get_width(), scaled_h)
        )
        rotated = pygame.transform.rotate(scaled, angle_deg)
        rect = rotated.get_rect(center=(self.cx, self.cy))
        return rotated, rect
 
    def draw(self, screen):
        now = datetime.datetime.now()
        minutes = now.minute
        seconds = now.second
 
        # Draw background
        screen.blit(self.bg, (0, 0))
 
        # Angle: 0 = 12 o'clock (pointing up), clockwise positive
        # pygame.transform.rotate rotates counter-clockwise, so negate
        # Minutes hand (right hand in Mickey = minutes)
        min_angle = -(minutes / 60 * 360 - 90)  # offset so 0 min = top
        min_angle = 90 - (minutes / 60 * 360)
 
        # Seconds hand (left hand in Mickey = seconds)
        sec_angle = 90 - (seconds / 60 * 360)
 
        # Draw minute hand (slightly longer)
        min_surf, min_rect = self._rotate_hand(min_angle, length_factor=1.0)
        screen.blit(min_surf, min_rect)
 
        # Draw second hand (slightly shorter)
        sec_surf, sec_rect = self._rotate_hand(sec_angle, length_factor=0.85)
        screen.blit(sec_surf, sec_rect)
 
        # Center dot
        pygame.draw.circle(screen, (30, 30, 30), (self.cx, self.cy), 8)
        pygame.draw.circle(screen, (200, 50, 50), (self.cx, self.cy), 5)
 
        # Display time as text
        font = pygame.font.SysFont("Arial", 28, bold=True)
        time_str = now.strftime("%M:%S")
        text = font.render(time_str, True, (255, 255, 255))
        shadow = font.render(time_str, True, (0, 0, 0))
        tx = self.width // 2 - text.get_width() // 2
        ty = self.height - 45
        screen.blit(shadow, (tx + 2, ty + 2))
        screen.blit(text, (tx, ty))
 