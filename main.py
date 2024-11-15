import pygame
from pygame.locals import *
import random

pygame.init()

# Configuración de pantalla
ancho = 500
alto = 500
pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption('Evita los carros')

# Colores
gris = (100, 100, 100)
verde = (76, 208, 56)
rojo = (200, 0, 0)
blanco = (255, 255, 255)
amarillo = (255, 232, 0)

# Configuración del carril
ancho_carretera = 300
ancho_marcador = 10
alto_marcador = 50
carril_izquierdo = 150
carril_central = 250
carril_derecho = 350
carriles = [carril_izquierdo, carril_central, carril_derecho]

# Inicialización del jugador
jugador_x = 250
jugador_y = 400
velocidad = 2
puntuacion = 0
juego_terminado = False
fps = 120

# Cargar sonidos
pygame.mixer.music.load('audios/main.mp3')
pygame.mixer.music.play(-1)  # Sonido de fondo en bucle
sonido_turnon = pygame.mixer.Sound('audios/turnon.mp3')
sonido_carro = pygame.mixer.Sound('audios/car_sound.mp3')
sonido_crash = pygame.mixer.Sound('audios/crash.mp3')
sonido_beep = pygame.mixer.Sound('audios/beep.mp3')

# Cargar imágenes
carro_jugador = pygame.image.load('images/car.png')
choque = pygame.image.load('images/crash.png')
nombres_imagenes = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png']
imagenes_vehiculos = [pygame.image.load(f'images/{nombre}') for nombre in nombres_imagenes]

# Clase Vehiculo
class Vehiculo(pygame.sprite.Sprite):
    def __init__(self, imagen, x, y):
        pygame.sprite.Sprite.__init__(self)
        escala_imagen = 45 / imagen.get_rect().width
        nuevo_ancho = int(imagen.get_rect().width * escala_imagen)
        nuevo_alto = int(imagen.get_rect().height * escala_imagen)
        self.image = pygame.transform.scale(imagen, (nuevo_ancho, nuevo_alto))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

# Clase para el jugador
class VehiculoJugador(Vehiculo):
    def __init__(self, x, y):
        super().__init__(carro_jugador, x, y)

# Grupos de sprites
grupo_jugador = pygame.sprite.Group()
grupo_vehiculos = pygame.sprite.Group()
jugador = VehiculoJugador(jugador_x, jugador_y)
grupo_jugador.add(jugador)

# Bucle principal
reloj = pygame.time.Clock()
ejecutando = True

while ejecutando:
    reloj.tick(fps)

    for evento in pygame.event.get():
        if evento.type == QUIT:
            ejecutando = False

        if evento.type == KEYDOWN:
            if evento.key == K_LEFT and jugador.rect.center[0] > carril_izquierdo:
                jugador.rect.x -= 100
            elif evento.key == K_RIGHT and jugador.rect.center[0] < carril_derecho:
                jugador.rect.x += 100
            elif evento.key == K_p:  # Sonido al presionar "P"
                sonido_beep.play()

            # Verificar colisiones laterales
            for vehiculo in grupo_vehiculos:
                if pygame.sprite.collide_rect(jugador, vehiculo):
                    sonido_crash.play()
                    juego_terminado = True
                    rect_choque = choque.get_rect(center=(jugador.rect.center[0], jugador.rect.top))

    # Dibujo de elementos en pantalla
    pantalla.fill(verde)
    pygame.draw.rect(pantalla, gris, (100, 0, ancho_carretera, alto))
    pygame.draw.rect(pantalla, amarillo, (95, 0, ancho_marcador, alto))
    pygame.draw.rect(pantalla, amarillo, (395, 0, ancho_marcador, alto))

    # Dibujar los marcadores de carril
    movimiento_marcador_carril_y = (pygame.time.get_ticks() // 10) % alto_marcador * 2
    for y in range(-alto_marcador * 2, alto, alto_marcador * 2):
        pygame.draw.rect(pantalla, blanco, (carril_izquierdo + 45, y + movimiento_marcador_carril_y, ancho_marcador, alto_marcador))
        pygame.draw.rect(pantalla, blanco, (carril_central + 45, y + movimiento_marcador_carril_y, ancho_marcador, alto_marcador))

    # Dibujo del jugador y vehículos
    grupo_jugador.draw(pantalla)
    grupo_vehiculos.draw(pantalla)

    # Agregar vehículos
    if len(grupo_vehiculos) < 2 and all(v.rect.top > alto * 0.3 for v in grupo_vehiculos):
        carril = random.choice(carriles)
        imagen = random.choice(imagenes_vehiculos)
        vehiculo = Vehiculo(imagen, carril, -alto_marcador)
        grupo_vehiculos.add(vehiculo)
        sonido_carro.play()

    # Movimiento de vehículos
    for vehiculo in grupo_vehiculos:
        vehiculo.rect.y += velocidad
        if vehiculo.rect.top >= alto:
            vehiculo.kill()
            puntuacion += 1
            if puntuacion % 5 == 0:
                velocidad += 1

    # Colisión frontal
    if pygame.sprite.spritecollide(jugador, grupo_vehiculos, True):
        sonido_crash.play()
        juego_terminado = True
        rect_choque = choque.get_rect(center=(jugador.rect.center[0], jugador.rect.top))

    # Juego terminado
    if juego_terminado:
        pantalla.blit(choque, rect_choque)
        pygame.draw.rect(pantalla, rojo, (0, 50, ancho, 150))  # Ajustar el tamaño del rectángulo para más texto

        # Configuración de la fuente
        fuente = pygame.font.Font(None, 32)

        # Mensaje 1: "Juego terminado"
        texto1 = fuente.render('Juego terminado.', True, blanco)
        pantalla.blit(texto1, texto1.get_rect(center=(ancho // 2, 90)))

        # Mensaje 2: "¿Jugar de nuevo?"
        texto2 = fuente.render('¿Jugar de nuevo?', True, blanco)
        pantalla.blit(texto2, texto2.get_rect(center=(ancho // 2, 120)))

        # Mensaje 3: "(S continuar, N salir)"
        texto3 = fuente.render('(S para continuar, N para salir)', True, blanco)
        pantalla.blit(texto3, texto3.get_rect(center=(ancho // 2, 150)))
    # Actualizar pantalla y mostrar puntuación
    fuente = pygame.font.Font(None, 32)
    texto = fuente.render(f'Puntuación: {puntuacion}', True, blanco)
    pantalla.blit(texto, (20, 20))
    pygame.display.flip()

    # Repetir al terminar
    while juego_terminado:
        for evento in pygame.event.get():
            if evento.type == QUIT:
                ejecutando = False
                juego_terminado = False
            if evento.type == KEYDOWN:
                if evento.key == K_s:
                    juego_terminado = False
                    velocidad = 2
                    puntuacion = 0
                    grupo_vehiculos.empty()
                    jugador.rect.center = (jugador_x, jugador_y)
                elif evento.key == K_n:
                    ejecutando = False
                    juego_terminado = False

pygame.quit()
