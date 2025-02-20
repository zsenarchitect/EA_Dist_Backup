"""
Bubble Shooter Game
A classic arcade-style bubble shooter with different shapes and special effects.

Controls:
    - Left/Right Arrow: Adjust cannon angle
    - Spacebar: Fire ball
    - ESC: Pause game
    
Scoring:
    - Circle: 1 point
    - Triangle: 5 points + explosion (radius 3)
    - Square: -10 points
    - Star: +5 seconds bonus time
"""

import pygame
import random
import math
from urllib.request import urlopen
import io
import concurrent.futures
from enum import Enum

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

class Colors(Enum):
    """Game color palette using modern flat design"""
    WHITE = (255, 255, 255)
    BLACK = (20, 20, 30)      # Softer black for background
    BLUE = (41, 128, 185)     # Flat blue
    RED = (231, 76, 60)       # Flat red
    GREEN = (46, 204, 113)    # Emerald green
    YELLOW = (241, 196, 15)   # Sunflower yellow
    PURPLE = (155, 89, 182)   # Amethyst purple
    ORANGE = (230, 126, 34)   # Carrot orange
    TURQUOISE = (26, 188, 156)  # Turquoise

    @property
    def rgb(self):
        """Get RGB tuple"""
        return self.value

class GameAssets:
    """Manages game assets and resources loaded from URLs with caching"""
    
    SHAPE_URLS = {
        'circle': "https://www.transparentpng.com/thumb/circle/blue-circle-png-4.png",
        'triangle': "https://www.transparentpng.com/thumb/triangle/triangle-free-transparent-6.png",
        'square': "https://www.transparentpng.com/thumb/square/square-png-4.png",
        'star': "https://www.transparentpng.com/thumb/star/gold-star-png-8.png",
        'cannon': "https://www.transparentpng.com/thumb/cannon/cannon-png-5.png",
        'turtle': "https://www.transparentpng.com/thumb/turtle/green-turtle-png-5.png"
    }
    
    _image_cache = {}  # Class variable for caching images
    
    @classmethod
    def load_image_from_url(cls, url):
        """Load image from cache or URL with fallback"""
        # Return cached image if available
        if url in cls._image_cache:
            return cls._image_cache[url]
        
        try:
            image_str = urlopen(url, timeout=2).read()  # Add timeout
            image_file = io.BytesIO(image_str)
            image = pygame.image.load(image_file)
            cls._image_cache[url] = image  # Cache the loaded image
            return image
        except:
            # Fallback to colored rectangles if image loading fails
            surf = pygame.Surface((30, 30))
            surf.fill(Colors.BLUE.rgb)
            cls._image_cache[url] = surf  # Cache the fallback surface
            return surf
    
    @classmethod
    def preload_images(cls):
        """Preload all game images in parallel"""
        def load_single_image(url_pair):
            name, url = url_pair
            try:
                cls.load_image_from_url(url)
            except:
                pass  # Silently fail for preloading
        
        # Use thread pool for parallel loading
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(load_single_image, cls.SHAPE_URLS.items())

class Shape:
    """Base class for all game shapes"""
    def __init__(self, x, y, shape_type):
        self.x = x
        self.y = y
        self.type = shape_type
        self.radius = 15
        self.image = GameAssets.load_image_from_url(GameAssets.SHAPE_URLS[shape_type])
        self.image = pygame.transform.scale(self.image, (30, 30))
        
    def draw(self, screen):
        screen.blit(self.image, (self.x - 15, self.y - 15))

class Cannon:
    """Player controlled cannon"""
    def __init__(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT - 50
        self.angle = 0
        self.image = GameAssets.load_image_from_url(GameAssets.SHAPE_URLS['cannon'])
        self.image = pygame.transform.scale(self.image, (50, 50))
    
    def rotate(self, direction):
        self.angle = max(-75, min(75, self.angle + direction * 2))
    
    def draw(self, screen):
        rotated = pygame.transform.rotate(self.image, self.angle)
        screen.blit(rotated, (self.x - 25, self.y - 25))

class Ball:
    """Projectile fired by the cannon"""
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.base_speed = 10
        self.speed = self.base_speed
        self.angle = math.radians(angle)
        self.radius = 5
        self.update_velocity()
        self.bounce_count = 0
        self.max_bounces = 3
        self.is_slow = False
    
    def bounce(self, is_vertical):
        """Handle ball bouncing off walls
        Args:
            is_vertical (bool): True for vertical walls, False for horizontal
        """
        if is_vertical:
            self.dx = -self.dx
        else:
            self.dy = -self.dy
        self.bounce_count += 1
    
    def move(self):
        """Move ball and handle boundary collisions"""
        next_x = self.x + self.dx
        next_y = self.y + self.dy
        
        # Bounce off walls if within bounce limit
        if self.bounce_count < self.max_bounces:
            # Left and right walls
            if next_x - self.radius < 0 or next_x + self.radius > WINDOW_WIDTH:
                self.bounce(is_vertical=True)
                next_x = max(self.radius, min(WINDOW_WIDTH - self.radius, next_x))
            
            # Top wall only (don't bounce off bottom)
            if next_y - self.radius < 0:
                self.bounce(is_vertical=False)
                next_y = self.radius
        
        self.x = next_x
        self.y = next_y
    
    def _interpolate_color(self, color1, color2, factor):
        """Interpolate between two colors"""
        return tuple(
            int(c1 + (c2 - c1) * factor) 
            for c1, c2 in zip(color1, color2)
        )
    
    def draw(self, screen):
        """Draw ball with flashing effect when slowed"""
        if not self.is_slow:
            pygame.draw.circle(screen, Colors.TURQUOISE.rgb, 
                             (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, Colors.WHITE.rgb, 
                             (int(self.x), int(self.y)), self.radius - 2)
            return

        # Create flashing effect using sine wave
        flash_speed = 0.008
        flash_intensity = abs(math.sin(pygame.time.get_ticks() * flash_speed))
        
        # Interpolate between purple and turquoise
        color = self._interpolate_color(
            Colors.PURPLE.rgb,
            Colors.TURQUOISE.rgb,
            flash_intensity
        )
        
        # Draw outer glow with flashing color
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, Colors.WHITE.rgb, 
                         (int(self.x), int(self.y)), self.radius - 2)
    
    def set_speed(self, new_speed):
        """Update ball speed and slow status"""
        self.speed = new_speed
        self.is_slow = (new_speed < self.base_speed)
        self.update_velocity()

    def update_velocity(self):
        """Update velocity based on current speed and angle"""
        self.dx = math.sin(self.angle) * self.speed
        self.dy = -math.cos(self.angle) * self.speed

class Button:
    """Interactive button class for menu"""
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = self._get_hover_color(color)
        self.is_hovered = False
        
    def _get_hover_color(self, base_color):
        """Create lighter version of color for hover effect"""
        return tuple(min(255, c + 30) for c in base_color)
    
    def draw(self, screen):
        """Draw button with hover effect"""
        color = self.hover_color if self.is_hovered else self.color
        
        # Draw button with rounded corners
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        pygame.draw.rect(screen, Colors.WHITE.rgb, self.rect, 2, border_radius=12)
        
        # Draw text
        font = pygame.font.Font(None, 48)
        text_surface = font.render(self.text, True, Colors.WHITE.rgb)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        """Handle mouse events"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Game:
    """Main game controller"""
    def __init__(self):
        """Initialize game with preloading"""
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Shape Shooter")
        self.clock = pygame.time.Clock()
        
        # Create start button
        button_width = 200
        button_height = 60
        button_x = WINDOW_WIDTH//2 - button_width//2
        button_y = 450
        self.start_button = Button(button_x, button_y, button_width, button_height, 
                                 "Start Game", Colors.GREEN.rgb)
        
        # Show loading screen
        self.screen.fill(Colors.BLACK.rgb)
        font = pygame.font.Font(None, 36)
        loading_text = font.render("Loading...", True, Colors.WHITE.rgb)
        text_rect = loading_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        self.screen.blit(loading_text, text_rect)
        pygame.display.flip()
        
        # Preload assets
        GameAssets.preload_images()
        
        # Initialize game variables
        self.slow_effect_timer = 0
        self.reset_game()
    
    def reset_game(self):
        """Initialize/Reset game state"""
        self.shapes = []
        self.cannon = Cannon()
        self.ball = None
        self.score = 0
        self.time_left = 60
        self.game_state = "menu"
        self.slow_effect_timer = 0  # Reset timer when game resets
        self._populate_shapes()
    
    def _populate_shapes(self):
        """Create initial shape layout"""
        shape_types = ['circle', 'triangle', 'square', 'star']
        for row in range(5):
            for col in range(10):
                x = col * 70 + 100
                y = row * 40 + 50
                shape_type = random.choice(shape_types)
                self.shapes.append(Shape(x, y, shape_type))
    
    def handle_collision(self):
        """Handle ball collision with shapes"""
        if not self.ball:
            return
            
        for shape in self.shapes[:]:
            dx = self.ball.x - shape.x
            dy = self.ball.y - shape.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance >= shape.radius + self.ball.radius:
                continue
                
            self._handle_shape_collision(shape)
            self.shapes.remove(shape)
            self.ball = None
            break
    
    def _handle_shape_collision(self, shape):
        """Handle collision effects for different shapes"""
        if shape.type == 'circle':
            self.score += 1
        elif shape.type == 'triangle':
            self.score += 5
            self._explosion(shape.x, shape.y)
        elif shape.type == 'square':
            self.score = max(0, self.score - 10)
        elif shape.type == 'star':
            self.time_left = min(60, self.time_left + 5)
        elif shape.type == 'turtle':
            self.slow_effect_timer = 10
            if self.ball:
                self.ball.set_speed(self.ball.base_speed * 0.5)
    
    def _explosion(self, x, y):
        """Handle triangle explosion effect"""
        for shape in self.shapes[:]:
            dx = x - shape.x
            dy = y - shape.y
            if math.sqrt(dx*dx + dy*dy) < 90:  # 3 shape radius
                self.shapes.remove(shape)
    
    def draw_menu(self):
        """Draw game menu screen with enhanced visuals"""
        self.screen.fill(Colors.BLACK.rgb)
        font = pygame.font.Font(None, 48)
        small_font = pygame.font.Font(None, 36)
        
        # Draw title and instructions
        title = font.render("Shape Shooter", True, Colors.YELLOW.rgb)
        controls = small_font.render("Controls:", True, Colors.WHITE.rgb)
        arrow_keys = small_font.render("← → Arrow Keys: Aim Cannon", True, Colors.TURQUOISE.rgb)
        space_key = small_font.render("Space: Fire Ball", True, Colors.TURQUOISE.rgb)
        
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 150))
        self.screen.blit(title, title_rect)
        self.screen.blit(controls, (WINDOW_WIDTH//2 - 150, 250))
        self.screen.blit(arrow_keys, (WINDOW_WIDTH//2 - 150, 300))
        self.screen.blit(space_key, (WINDOW_WIDTH//2 - 150, 350))
        
        # Draw start button
        self.start_button.draw(self.screen)
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.game_state == "menu":
                    if self.start_button.handle_event(event):
                        self.game_state = "playing"
                        self.reset_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "menu"
                    elif self.game_state == "playing" and event.key == pygame.K_SPACE and not self.ball:
                        self.ball = Ball(self.cannon.x, self.cannon.y, self.cannon.angle)
                        if self.slow_effect_timer > 0:
                            self.ball.set_speed(self.ball.base_speed * 0.5)
                        else:
                            self.ball.set_speed(self.ball.base_speed)
            
            if self.game_state == "menu":
                self.draw_menu()
            else:
                self._update_game()
                self._draw_game()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
    
    def _update_game(self):
        """Update game state"""
        self._handle_input()
        self._update_ball()
        self._update_timers()
    
    def _handle_input(self):
        """Handle keyboard input"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.cannon.rotate(-1)
        if keys[pygame.K_RIGHT]:
            self.cannon.rotate(1)
    
    def _update_ball(self):
        """Update ball position and collisions"""
        if not self.ball:
            return
            
        self.ball.move()
        self.handle_collision()
        
        if (self.ball.y > WINDOW_HEIGHT or 
            self.ball.bounce_count >= self.ball.max_bounces):
            self.ball = None
    
    def _update_timers(self):
        """Update game timers"""
        self._update_slow_effect()
        self._update_game_time()
    
    def _update_slow_effect(self):
        """Update slow effect timer"""
        if self.slow_effect_timer <= 0:
            return
            
        self.slow_effect_timer -= 1/FPS
        if self.slow_effect_timer <= 0:
            self.slow_effect_timer = 0
            if self.ball:
                self.ball.set_speed(self.ball.base_speed)
    
    def _update_game_time(self):
        """Update game time"""
        if self.time_left <= 0:
            self.game_state = "menu"
            self.reset_game()
            return
            
        self.time_left -= 1/FPS
    
    def _draw_game(self):
        """Draw game screen with enhanced visuals"""
        self.screen.fill(Colors.BLACK.rgb)
        
        for shape in self.shapes:
            shape.draw(self.screen)
        
        self.cannon.draw(self.screen)
        if self.ball:
            self.ball.draw(self.screen)
        
        # Draw HUD with enhanced visuals
        font = pygame.font.Font(None, 36)
        
        # Score with color based on value
        score_color = (Colors.GREEN.rgb if self.score > 0 
                      else Colors.RED.rgb if self.score < 0 
                      else Colors.WHITE.rgb)
        score_text = font.render("Score: {}".format(self.score), True, score_color)
        
        # Time with color based on remaining time
        time_color = (Colors.RED.rgb if self.time_left < 10 
                     else Colors.YELLOW.rgb if self.time_left < 30 
                     else Colors.GREEN.rgb)
        time_text = font.render("Time: {:.1f}".format(max(0, self.time_left)), True, time_color)
        
        # Add slight shadow effect to HUD
        shadow_offset = 2
        score_shadow = font.render("Score: {}".format(self.score), True, Colors.BLACK.rgb)
        time_shadow = font.render("Time: {:.1f}".format(max(0, self.time_left)), True, Colors.BLACK.rgb)
        
        # Draw shadows first
        self.screen.blit(score_shadow, (12, 12))
        self.screen.blit(time_shadow, (WINDOW_WIDTH - 148, 12))
        
        # Draw text
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(time_text, (WINDOW_WIDTH - 150, 10))
        
        # Draw slow effect indicator if active
        if self.slow_effect_timer > 0:
            slow_text = font.render("SLOW!", True, Colors.PURPLE.rgb)
            slow_rect = slow_text.get_rect(center=(WINDOW_WIDTH//2, 30))
            self.screen.blit(slow_text, slow_rect)

if __name__ == "__main__":
    game = Game()
    game.run()
