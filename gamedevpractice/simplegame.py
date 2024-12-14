#imports
import pygame
import random
import math

#initialization
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

clock = pygame.time.Clock()

num_agents = 10

#screen creation
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Map with Agents")

#create walls
walls = [
    pygame.Rect(100, 100, 200, 20),
    pygame.Rect(400, 300, 20, 200),
    pygame.Rect(600, 150, 150, 20),
]

def draw_walls():
    for wall in walls:
        pygame.draw.rect(screen, BLACK, wall)
        
#agent class
class Agent:
    def __init__(self, x, y, agent_id, radius=8, color=RED):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = random.uniform(1, 3)
        self.angle = random.uniform(0, 2 * math.pi)
        self.direction_timer = random.randint(20, 80)
        self.speed_timer = random.randint(30, 120)
        self.id = agent_id
        
    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        #boundary check
        if self.x - self.radius < 0 or self.x + self.radius > SCREEN_WIDTH:
            self.angle = math.pi - self.angle  # Reflect angle horizontally
        if self.y - self.radius < 0 or self.y + self.radius > SCREEN_HEIGHT:
            self.angle = -self.angle
            
        self.direction_timer -= 1
        if self.direction_timer <= 0:
            self.angle = random.uniform(0, 2 * math.pi)
            self.direction_timer = random.randint(20, 80)
            
        self.speed_timer -= 1
        if self.speed_timer <= 0:
            self.speed = random.uniform(1, 3)
            self.speed_timer = random.randint(30, 120)
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        #directional line
        end_x = self.x + math.cos(self.angle) * self.radius * 2
        end_y = self.y + math.sin(self.angle) * self.radius * 2
        pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 2)
        #id label
        font = pygame.font.Font(None, 24)
        text = font.render(str(self.id), True, WHITE)
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, text_rect)
        
def is_position_valid(x, y, radius, walls, agents):
    agent_rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
    for wall in walls:
        if agent_rect.colliderect(wall):
            return False
        
    for agent in agents:
        distance = ((x - agent.x) ** 2 + (y - agent.y) ** 2) ** 0.5
        if distance < radius * 2: 
            return False
        
    return True

def create_agent(agent_id, radius, walls, agents):
    while True:
        x = random.randint(radius, SCREEN_WIDTH - radius)
        y = random.randint(radius, SCREEN_HEIGHT - radius)
        if is_position_valid(x, y, radius, walls, agents):
            return Agent(x, y, agent_id, radius=radius)
        
agents = []
for i in range(num_agents):
    agent = create_agent(i + 1, radius=10, walls=walls, agents=agents)
    agents.append(agent)

#collision detection
def check_wall_collision(agent):
    agent_rect = pygame.Rect(
        agent.x - agent.radius, agent.y - agent.radius, agent.radius * 2, agent.radius * 2
    )
    for wall in walls:
        if agent_rect.colliderect(wall):
            if agent_rect.right > wall.left and agent_rect.left < wall.right:
                if agent_rect.bottom > wall.top and agent_rect.top < wall.bottom:
                    if abs(agent.x - wall.left) < agent.radius or abs(agent.x - wall.right) < agent.radius:
                        agent.angle = math.pi - agent.angle
                    if abs(agent.y - wall.top) < agent.radius or abs(agent.y - wall.bottom) < agent.radius:
                        agent.angle = -agent.angle
        
def check_agent_collision(agent, other_agents):
    for other in other_agents:
        if agent != other:
            distance = math.sqrt((agent.x - other.x) ** 2 + (agent.y - other.y) ** 2)
            if distance < agent.radius * 2: 
                angle_between = math.atan2(other.y - agent.y, other.x - agent.x)
                agent.angle = math.pi + angle_between
                other.angle = math.pi - angle_between
                
#main game loop
running = True
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    for agent in agents:
        agent.move()
        check_wall_collision(agent)
        check_agent_collision(agent, agents)
        agent.draw()
        
    draw_walls()
    pygame.display.flip()
    clock.tick(FPS)
    
pygame.quit()