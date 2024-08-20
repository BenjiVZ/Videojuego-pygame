import sys
import time
import pygame
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QGraphicsOpacityEffect
from PyQt5.QtCore import QTimer, QPropertyAnimation, Qt
from PyQt5.QtGui import QPixmap

# Definir algunas constantes para el juego
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Definir los colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

#==================================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Mi Juego')
        self.setGeometry(300, 300, 800, 600)

        self.background = QLabel(self)
        self.background.setPixmap(QPixmap('fondo.jpg'))
        self.background.resize(1920, 1080)

        self.startButton = QPushButton('Empezar', self)
        startButtonX = int(self.width()/2 - self.startButton.width()/2)
        startButtonY = int(self.height()/2 - self.startButton.height()/2)
        self.startButton.move(startButtonX, startButtonY)
        self.startButton.clicked.connect(self.startGame)
        self.startButton.setStyleSheet("background-color: green; color: white; border-radius: 15px;")

        self.quitButton = QPushButton('Salir', self)
        quitButtonX = int(self.width() - self.quitButton.width())
        quitButtonY = int(self.height() - self.quitButton.height())
        self.quitButton.move(quitButtonX, quitButtonY)
        self.quitButton.clicked.connect(QApplication.instance().quit)
        self.quitButton.setStyleSheet("background-color: red; color: white; border-radius: 15px;")

#=======================================================================================================================================

        # Inicializar Pygame al inicio, pero no crear la ventana del juego
        pygame.init()

    def startGame(self):
        self.close()
        game()

#=======================================================================================================================================

def game():
    # Crear la ventana del juego
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Cargar el fondo del juego
    background = pygame.image.load('fondojuego.jpg')

    # Clase para el jugador
    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.image = pygame.image.load('pato.png')
            self.image = pygame.transform.scale(self.image, (50, 50))  # Escala la imagen a 50x50 píxeles
            self.rect = self.image.get_rect()
            self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
            self.lives = 3

        def update(self):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.rect.x -= 5
            if keys[pygame.K_RIGHT]:
                self.rect.x += 5

            # Limitar la posición del jugador dentro de la pantalla
            self.rect.x = max(0, min(SCREEN_WIDTH - self.rect.width, self.rect.x))

    # Clase para los objetos que caen
    class FallingObject(pygame.sprite.Sprite):
        def __init__(self, image_path, damage, healing, immunity):
            super().__init__()
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (20, 20))  # Escala la imagen a 20x20 píxeles
            self.rect = self.image.get_rect()
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randint(-SCREEN_HEIGHT, -50)  # Añade un retraso aleatorio antes de que el objeto comience a caer
            self.damage = damage
            self.healing = healing
            self.immunity = immunity

        def update(self):
            self.rect.y += 5  # Aumentar la velocidad de caída a 5 píxeles por actualización

            # Reiniciar en la parte superior cuando llega al fondo
            if self.rect.y > SCREEN_HEIGHT:
                self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
                self.rect.y = random.randint(-SCREEN_HEIGHT, -50)  # Añade un retraso aleatorio antes de que el objeto comience a caer

    # Crear grupos de sprites
    all_sprites = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    falling_objects_group = pygame.sprite.Group()

    # Crear al jugador
    player = Player()
    all_sprites.add(player)
    player_group.add(player)

    # Crear objetos que caen
    for _ in range(10):  # Aumentar el número de objetos que caen a 10
        object_types = [('aguila.png', 1, 0, 0), ('meteorito.png', 2, 0, 0),
                        ('estrella.png', 0, 0, 5), ('corazon.png', 0, 1, 0),
                        ('escudo.png', 0, 0, 5), ('nube.png', 0, 0, 0)]

        object_info = random.choice(object_types)
        falling_object = FallingObject(*object_info)
        all_sprites.add(falling_object)
        falling_objects_group.add(falling_object)

    # Bucle principal del juego
    running = True
    clock = pygame.time.Clock()
    start_ticks = pygame.time.get_ticks()  # Tiempo de inicio

    while running:
        clock.tick(FPS)

        # Procesar eventos (p. ej., entrada del teclado)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Actualizar el juego
        all_sprites.update()

        # Detección de colisiones entre jugador y objetos que caen
        collisions = pygame.sprite.spritecollide(player, falling_objects_group, True)
        for collision in collisions:
            if collision.damage > 0:
                player.lives -= collision.damage
                print(f"¡Te quitaron {collision.damage} corazones!")
            elif collision.healing > 0:
                player.lives += collision.healing
                print(f"¡Te curaron {collision.healing} corazones!")
            elif collision.immunity > 0:
                print("¡Inmunidad activada!")

        # Dibujar en la pantalla
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)

        # Mostrar la vida y el tiempo
        font = pygame.font.Font(None, 36)
        text = font.render(f"Vida: {player.lives}", True, WHITE)
        screen.blit(text, (20, 20))

        seconds = (pygame.time.get_ticks() - start_ticks) / 1000  # Calcular el tiempo transcurrido
        text = font.render(f"Tiempo: {int(seconds)}", True, WHITE)
        screen.blit(text, (20, 60))  # Asegúrate de que el texto del tiempo no se superponga con el texto de la vida

        pygame.display.flip()  # Actualizar la pantalla para mostrar los cambios

        # Verificar si el jugador se quedó sin vidas
        if player.lives <= 0:
            running = False

    # Mostrar el menú de fin de juego
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Si se presiona la tecla 'r', reiniciar el juego
                    game()
                elif event.key == pygame.K_c:  # Si se presiona la tecla 'c', cerrar el juego
                    pygame.quit()
                    sys.exit()

        screen.fill((0, 0, 0))  # Llenar la pantalla de negro

        font = pygame.font.Font(None, 36)
        text = font.render("¡Juego terminado! Presiona 'R' para reiniciar o 'C' para cerrar", True, WHITE)
        screen.blit(text, (20, SCREEN_HEIGHT // 2))

        pygame.display.flip()  # Actualizar la pantalla para mostrar los cambios

pygame.quit()



#======================================================================================================================

def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

    sys.exit()
