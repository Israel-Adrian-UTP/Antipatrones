import itertools
import queue
from abc import ABC, abstractmethod

# ACTIVIDAD 1: Identificar y corregir un antipatrón (Spaghetti Code)
class Cuenta:
    def __init__(self, saldo=0):
        self.saldo = saldo

    def _cantidad_valida(self, cantidad):
        if cantidad <= 0:
            print("Cantidad no válida")
            return False
        return True

    def depositar(self, cantidad):
        if not self._cantidad_valida(cantidad):
            return
        self.saldo += cantidad
        print(f"Depositando ${cantidad}")

    def retirar(self, cantidad):
        if not self._cantidad_valida(cantidad):
            return
        if cantidad > self.saldo:
            print("Fondos insuficientes")
            return
        self.saldo -= cantidad
        print(f"Retirando ${cantidad}")

    def consultar(self):
        print(f"Consultando balance... ${self.saldo}")


class ProcesadorTransacciones:
    def __init__(self, cuenta):
        self.cuenta = cuenta
        # Para agregar un tipo nuevo basta con registrar una entrada aquí.
        self._acciones = {
            "depósito": self.cuenta.depositar,
            "retiro": self.cuenta.retirar,
            "consulta": lambda cantidad: self.cuenta.consultar(),
        }

    def manejar(self, tipo, cantidad):
        accion = self._acciones.get(tipo)
        if accion is None:
            print("Tipo de transacción no reconocido")
            return
        accion(cantidad)


def actividad_1():
    print("=== ACTIVIDAD 1: Refactorización de Spaghetti Code ===")
    procesador = ProcesadorTransacciones(Cuenta())

    pruebas = [
        ("depósito", 100),       # válido
        ("retiro", -50),         # cantidad negativa
        ("consulta", 0),         # consulta no necesita cantidad
        ("transferencia", 200),  # tipo no reconocido
        ("retiro", 30),          # válido
        ("retiro", 500),         # más que el saldo
        ("consulta", 0),
    ]
    for tipo, cantidad in pruebas:
        procesador.manejar(tipo, cantidad)
    print()

# ACTIVIDAD 2: Patrón Command (control remoto)
class Luz:
    def encender(self):
        print("La luz está encendida")

    def apagar(self):
        print("La luz está apagada")


class Ventilador:
    def encender(self):
        print("El ventilador está encendido")

    def apagar(self):
        print("El ventilador está apagado")


# Interfaz Command
class Command(ABC):
    @abstractmethod
    def ejecutar(self):
        pass

    @abstractmethod
    def deshacer(self):
        pass


# Comandos concretos
class EncenderLuzCommand(Command):
    def __init__(self, luz):
        self.luz = luz

    def ejecutar(self):
        self.luz.encender()

    def deshacer(self):
        self.luz.apagar()


class ApagarLuzCommand(Command):
    def __init__(self, luz):
        self.luz = luz

    def ejecutar(self):
        self.luz.apagar()

    def deshacer(self):
        self.luz.encender()


class EncenderVentiladorCommand(Command):
    def __init__(self, ventilador):
        self.ventilador = ventilador

    def ejecutar(self):
        self.ventilador.encender()

    def deshacer(self):
        self.ventilador.apagar()


class ApagarVentiladorCommand(Command):
    def __init__(self, ventilador):
        self.ventilador = ventilador

    def ejecutar(self):
        self.ventilador.apagar()

    def deshacer(self):
        self.ventilador.encender()


# Invocador
class ControlRemoto:
    def __init__(self):
        self._historial = []

    def ejecutar_comando(self, comando):
        comando.ejecutar()
        self._historial.append(comando)

    def deshacer_ultimo(self):
        if not self._historial:
            print("No hay comandos para deshacer")
            return
        self._historial.pop().deshacer()


def actividad_2():
    print("=== ACTIVIDAD 2: Patrón Command ===")
    luz = Luz()
    ventilador = Ventilador()
    control = ControlRemoto()

    control.ejecutar_comando(EncenderLuzCommand(luz))
    control.ejecutar_comando(EncenderVentiladorCommand(ventilador))
    control.ejecutar_comando(ApagarLuzCommand(luz))
    control.ejecutar_comando(ApagarVentiladorCommand(ventilador))

    print("--- Deshaciendo los dos últimos comandos ---")
    control.deshacer_ultimo()
    control.deshacer_ultimo()
    print()

# ACTIVIDAD 3: Evitar el antipatrón Golden Hammer
class NotificacionEmail:
    def enviar(self, mensaje):
        print("Enviando correo electrónico:", mensaje)


class NotificacionSMS:
    def enviar(self, mensaje):
        print("Enviando SMS:", mensaje)


PRIORIDAD_ALTA = 1
PRIORIDAD_MEDIA = 2
PRIORIDAD_BAJA = 3


def elegir_notificacion(prioridad):
    """Alta prioridad va por SMS (llega más rápido). El resto va por correo."""
    if prioridad == PRIORIDAD_ALTA:
        return NotificacionSMS()
    return NotificacionEmail()


class ColaNotificaciones:
    def __init__(self):
        self._cola = queue.PriorityQueue()
        # El contador desempata prioridades iguales y respeta el orden de llegada.
        self._orden = itertools.count()

    def agregar(self, prioridad, mensaje):
        self._cola.put((prioridad, next(self._orden), mensaje))

    def enviar_todas(self):
        while not self._cola.empty():
            prioridad, _, mensaje = self._cola.get()
            elegir_notificacion(prioridad).enviar(mensaje)


def actividad_3():
    print("=== ACTIVIDAD 3: Notificaciones con cola de prioridad ===")
    cola = ColaNotificaciones()
    cola.agregar(PRIORIDAD_BAJA, "Promoción de la semana")
    cola.agregar(PRIORIDAD_ALTA, "Servidor caído")
    cola.agregar(PRIORIDAD_MEDIA, "Reunión mañana a las 9:00")
    cola.agregar(PRIORIDAD_ALTA, "Intento de acceso sospechoso")
    cola.agregar(PRIORIDAD_BAJA, "Resumen semanal")

    cola.enviar_todas()
    print()

# Programa principal
if __name__ == "__main__":
    actividad_1()
    actividad_2()
    actividad_3()
