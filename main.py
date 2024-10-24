import pygame
from pygame.locals import *
import random

pygame.init()

# crear la ventana
ancho = 500
alto = 500
tamano_pantalla = (ancho, alto)
pantalla = pygame.display.set_mode(tamano_pantalla)
pygame.display.set_caption('Evita los carros')

# colores
gris = (100, 100, 100)
verde = (76, 208, 56)
rojo = (200, 0, 0)
blanco = (255, 255, 255)
amarillo = (255, 232, 0)

# tamaños de la carretera y los marcadores
ancho_carretera = 300
ancho_marcador = 10
alto_marcador = 50

# coordenadas de los carriles
carril_izquierdo = 150
carril_central = 250
carril_derecho = 350
carriles = [carril_izquierdo, carril_central, carril_derecho]

# carretera y marcadores de borde
carretera = (100, 0, ancho_carretera, alto)
marcador_borde_izquierdo = (95, 0, ancho_marcador, alto)
marcador_borde_derecho = (395, 0, ancho_marcador, alto)

# para animar el movimiento de los marcadores de carril
movimiento_marcador_carril_y = 0

# coordenadas iniciales del jugador
jugador_x = 250
jugador_y = 400

# configuración de los fotogramas
reloj = pygame.time.Clock()
fps = 120

# configuración del juego
juego_terminado = False
velocidad = 2
puntuacion = 0


class Vehiculo(pygame.sprite.Sprite):

    def __init__(self, imagen, x, y):
        pygame.sprite.Sprite.__init__(self)

        # escalar la imagen para que no sea más ancha que el carril
        escala_imagen = 45 / imagen.get_rect().width
        nuevo_ancho = imagen.get_rect().width * escala_imagen
        nuevo_alto = imagen.get_rect().height * escala_imagen
        self.image = pygame.transform.scale(imagen, (nuevo_ancho, nuevo_alto))

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]


class VehiculoJugador(Vehiculo):

    def __init__(self, x, y):
        imagen = pygame.image.load('images/car.png')
        super().__init__(imagen, x, y)


# grupos de sprites
grupo_jugador = pygame.sprite.Group()
grupo_vehiculos = pygame.sprite.Group()

# crear el coche del jugador
jugador = VehiculoJugador(jugador_x, jugador_y)
grupo_jugador.add(jugador)

# cargar las imágenes de los vehículos
nombres_imagenes = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png']
imagenes_vehiculos = []
for nombre_imagen in nombres_imagenes:
    imagen = pygame.image.load('images/' + nombre_imagen)
    imagenes_vehiculos.append(imagen)

# cargar la imagen de choque
choque = pygame.image.load('images/crash.png')
rect_choque = choque.get_rect()

# bucle del juego
ejecutando = True
while ejecutando:

    reloj.tick(fps)

    for evento in pygame.event.get():
        if evento.type == QUIT:
            ejecutando = False

        # mover el coche del jugador usando las teclas de flecha izquierda/derecha
        if evento.type == KEYDOWN:

            if evento.key == K_LEFT and jugador.rect.center[0] > carril_izquierdo:
                jugador.rect.x -= 100
            elif evento.key == K_RIGHT and jugador.rect.center[0] < carril_derecho:
                jugador.rect.x += 100

            # verificar si hay una colisión lateral después de cambiar de carril
            for vehiculo in grupo_vehiculos:
                if pygame.sprite.collide_rect(jugador, vehiculo):

                    juego_terminado = True

                    # colocar el coche del jugador junto al otro vehículo
                    # y determinar dónde posicionar la imagen de choque
                    if evento.key == K_LEFT:
                        jugador.rect.left = vehiculo.rect.right
                        rect_choque.center = [jugador.rect.left, (jugador.rect.center[1] + vehiculo.rect.center[1]) / 2]
                    elif evento.key == K_RIGHT:
                        jugador.rect.right = vehiculo.rect.left
                        rect_choque.center = [jugador.rect.right, (jugador.rect.center[1] + vehiculo.rect.center[1]) / 2]

    # dibujar el césped
    pantalla.fill(verde)

    # dibujar la carretera
    pygame.draw.rect(pantalla, gris, carretera)

    # dibujar los marcadores de borde
    pygame.draw.rect(pantalla, amarillo, marcador_borde_izquierdo)
    pygame.draw.rect(pantalla, amarillo, marcador_borde_derecho)

    # dibujar los marcadores de carril
    movimiento_marcador_carril_y += velocidad * 2
    if movimiento_marcador_carril_y >= alto_marcador * 2:
        movimiento_marcador_carril_y = 0
    for y in range(alto_marcador * -2, alto, alto_marcador * 2):
        pygame.draw.rect(pantalla, blanco, (carril_izquierdo + 45, y + movimiento_marcador_carril_y, ancho_marcador, alto_marcador))
        pygame.draw.rect(pantalla, blanco, (carril_central + 45, y + movimiento_marcador_carril_y, ancho_marcador, alto_marcador))

    # dibujar el coche del jugador
    grupo_jugador.draw(pantalla)

    # agregar un vehículo
    if len(grupo_vehiculos) < 2:

        # asegurar que haya suficiente espacio entre vehículos
        agregar_vehiculo = True
        for vehiculo in grupo_vehiculos:
            if vehiculo.rect.top < vehiculo.rect.height * 1.5:
                agregar_vehiculo = False

        if agregar_vehiculo:
            # seleccionar un carril aleatorio
            carril = random.choice(carriles)

            # seleccionar una imagen de vehículo aleatoria
            imagen = random.choice(imagenes_vehiculos)
            vehiculo = Vehiculo(imagen, carril, alto / -2)
            grupo_vehiculos.add(vehiculo)

    # hacer que los vehículos se muevan
    for vehiculo in grupo_vehiculos:
        vehiculo.rect.y += velocidad

        # eliminar el vehículo una vez que salga de la pantalla
        if vehiculo.rect.top >= alto:
            vehiculo.kill()

            # agregar a la puntuación
            puntuacion += 1

            # acelerar el juego después de pasar 5 vehículos
            if puntuacion > 0 and puntuacion % 5 == 0:
                velocidad += 1

    # dibujar los vehículos
    grupo_vehiculos.draw(pantalla)

    # mostrar la puntuación
    fuente = pygame.font.Font(pygame.font.get_default_font(), 16)
    texto = fuente.render('Puntuación: ' + str(puntuacion), True, blanco)
    rect_texto = texto.get_rect()
    rect_texto.center = (50, 400)
    pantalla.blit(texto, rect_texto)

    # verificar si hay una colisión frontal
    if pygame.sprite.spritecollide(jugador, grupo_vehiculos, True):
        juego_terminado = True
        rect_choque.center = [jugador.rect.center[0], jugador.rect.top]

    # mostrar juego terminado
    if juego_terminado:
        pantalla.blit(choque, rect_choque)

        pygame.draw.rect(pantalla, rojo, (0, 50, ancho, 100))

        fuente = pygame.font.Font(pygame.font.get_default_font(), 16)
        texto = fuente.render('Juego terminado. ¿Jugar de nuevo? (Presiona S o N)', True, blanco)
        rect_texto = texto.get_rect()
        rect_texto.center = (ancho / 2, 100)
        pantalla.blit(texto, rect_texto)

    pygame.display.update()

    # esperar la entrada del usuario para jugar de nuevo o salir
    while juego_terminado:

        reloj.tick(fps)

        for evento in pygame.event.get():

            if evento.type == QUIT:
                juego_terminado = False
                ejecutando = False

            # obtener la entrada del usuario (y o n)
            if evento.type == KEYDOWN:
                if evento.key == K_s:
                    # reiniciar el juego
                    juego_terminado = False
                    velocidad = 2
                    puntuacion = 0
                    grupo_vehiculos.empty()
                    jugador.rect.center = [jugador_x, jugador_y]
                elif evento.key == K_n:
                    # salir de los bucles
                    juego_terminado = False
                    ejecutando = False

pygame.quit()