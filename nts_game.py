#imports
import pygame
import random
import math
import numpy as np

#game initialization
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
clock = pygame.time.Clock()
score = 0
time_limit = 60
start_ticks = pygame.time.get_ticks()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Neural Tactics Simulation")

class ControlledAgent:
    def __init__(self, x, y, radius=10):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = BLUE
        self.speed = 4
        self.angle = 0
        self.shots = []
        self.can_shoot = True
        
    def move(self, inputs):
        if inputs[0]:  # Move up
            self.y -= self.speed
        if inputs[1]:  # Move down
            self.y += self.speed
        if inputs[2]:  # Move left
            self.x -= self.speed
        if inputs[3]:  # Move right
            self.x += self.speed
            
        self.x = max(self.radius, min(self.x, SCREEN_WIDTH - self.radius))
        self.y = max(self.radius, min(self.y, SCREEN_HEIGHT - self.radius))
    
        if inputs[4]:
            self.angle -= 0.1
        if inputs[5]:
            self.angle += 0.1
        
        if inputs[6] and self.can_shoot:
            self.shoot()
            self.can_shoot = False
        if not inputs[6]:
            self.can_shoot = True
    
    def shoot(self):
        start_x = self.x + math.cos(self.angle) * self.radius
        start_y = self.y + math.sin(self.angle) * self.radius
        dx = math.cos(self.angle) * 10
        dy = math.sin(self.angle) * 10
        self.shots.append([(start_x, start_y), (start_x + dx, start_y + dy), dx, dy])
        
    def update_shots(self):
        for shot in self.shots[:]:
            shot[0] = (shot[0][0] + shot[2], shot[0][1] + shot[3])
            shot[1] = (shot[1][0] + shot[2], shot[1][1] + shot[3])
            if shot[1][0] < 0 or shot[1][0] > SCREEN_WIDTH or shot[1][1] < 0 or shot[1][1] > SCREEN_HEIGHT:
                self.shots.remove(shot)
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        gun_end_x = self.x + math.cos(self.angle) * (self.radius + 10)
        gun_end_y = self.y + math.sin(self.angle) * (self.radius + 10)
        pygame.draw.line(screen, WHITE, (self.x, self.y), (gun_end_x, gun_end_y), 3)
        for shot in self.shots:
            pygame.draw.line(screen, WHITE, shot[0], shot[1], 2)
            
class RandomAgent:
    def __init__(self, x, y, radius=10):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = RED
        self.speed = random.uniform(1, 3)
        self.angle = random.uniform(0, 2 * math.pi)

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
    
        if self.x - self.radius < 0 or self.x + self.radius > SCREEN_WIDTH:
            self.angle = math.pi - self.angle
        if self.y - self.radius < 0 or self.y + self.radius > SCREEN_HEIGHT:
            self.angle = -self.angle
            
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
class Target:
    def __init__(self, x, y, radius=10):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = YELLOW

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
def check_collision(x1, y1, r1, x2, y2, r2):
    distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return distance < r1 + r2

def line_circle_collision(line_start, line_end, circle_center, circle_radius):
    x1, y1 = line_start
    x2, y2 = line_end
    cx, cy = circle_center
    
    dx, dy = x2 - x1, y2 - y1
    fx, fy = x1 - cx, y1 - cy
    
    a = dx**2 + dy**2
    b = 2 * (fx * dx + fy * dy)
    c = fx**2 + fy**2 - circle_radius**2
    
    discriminant = b**2 - 4 * a * c
    
    if discriminant < 0:
        return False
    
    discriminant = math.sqrt(discriminant)
    t1 = (-b - discriminant) / (2 * a)
    t2 = (-b + discriminant) / (2 * a)

    return 0 <= t1 <= 1 or 0 <= t2 <= 1

controlled_agent = ControlledAgent(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
random_agents = [RandomAgent(random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 200)) for _ in range(5)]
targets = [Target(random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 200)) for _ in range(5)]

running = True
while running:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
    remaining_time = max(0, time_limit - elapsed_time)
    if remaining_time == 0:
        running = False
        
    keys = pygame.key.get_pressed()
    inputs = [
        keys[pygame.K_w],  # Forward
        keys[pygame.K_s],  # Backward
        keys[pygame.K_a],  # Move left
        keys[pygame.K_d],  # Move right
        keys[pygame.K_LEFT],  # Rotate left
        keys[pygame.K_RIGHT],  # Rotate right
        keys[pygame.K_SPACE],  # Shoot
    ]
    controlled_agent.move(inputs)
    
    for agent in random_agents:
        agent.move()
        
    controlled_agent.update_shots()
    
    for shot in controlled_agent.shots[:]:
        for agent in random_agents[:]:
            if line_circle_collision(shot[0], shot[1], (agent.x, agent.y), agent.radius):
                random_agents.remove(agent)
                controlled_agent.shots.remove(shot)
                score += 1
                break
            
    for shot in controlled_agent.shots[:]:
        for target in targets[:]:
            if line_circle_collision(shot[0], shot[1], (target.x, target.y), target.radius):
                targets.remove(target)
                controlled_agent.shots.remove(shot)
                score += 1
                break
            
    controlled_agent.draw()
    for agent in random_agents:
        agent.draw()
    for target in targets:
        target.draw()
        
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    time_text = font.render(f"Time: {int(remaining_time)}s", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(time_text, (10, 50))
    
    pygame.display.flip()
    clock.tick(FPS)
    
print(f"Final Score: {score}")
pygame.quit()