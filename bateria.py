

from abc import ABC, abstractmethod
from enum import Enum
import sqlite3


def titulo(texto):
    print()
    print("=" * 64)
    print(texto)
    print("=" * 64)

# EJERCICIO 1: Magic Numbers

# Tipos de cliente
CLIENTE_REGULAR = 1
CLIENTE_PREMIUM = 2
CLIENTE_VIP = 3

# Porcentajes de descuento por tipo de cliente
DESCUENTO_REGULAR = 0.10
DESCUENTO_PREMIUM = 0.20
DESCUENTO_VIP = 0.35
SIN_DESCUENTO = 0.0

DESCUENTOS_POR_CLIENTE = {
    CLIENTE_REGULAR: DESCUENTO_REGULAR,
    CLIENTE_PREMIUM: DESCUENTO_PREMIUM,
    CLIENTE_VIP: DESCUENTO_VIP,
}

# Impuesto según el monto de la compra
MONTO_LIMITE_IMPUESTO_ALTO = 1000
TASA_IMPUESTO_ALTA = 0.18
TASA_IMPUESTO_BAJA = 0.10

# Envío según el monto de la compra
MONTO_MINIMO_ENVIO_GRATIS = 500
COSTO_ENVIO_GRATIS = 0
COSTO_ENVIO_ESTANDAR = 25


def calcular_precio_final(tipo_cliente, monto):
    # Un tipo de cliente desconocido no recibe descuento. El código original
    # fallaba con UnboundLocalError en ese caso.
    descuento = monto * DESCUENTOS_POR_CLIENTE.get(tipo_cliente, SIN_DESCUENTO)

    if monto > MONTO_LIMITE_IMPUESTO_ALTO:
        impuesto = monto * TASA_IMPUESTO_ALTA
    else:
        impuesto = monto * TASA_IMPUESTO_BAJA

    if monto > MONTO_MINIMO_ENVIO_GRATIS:
        envio = COSTO_ENVIO_GRATIS
    else:
        envio = COSTO_ENVIO_ESTANDAR

    return monto - descuento + impuesto + envio


def _precio_final_original(tipo_cliente, monto):
    """Versión original con números mágicos, solo para comparar resultados."""
    if tipo_cliente == 1:
        descuento = monto * 0.10
    elif tipo_cliente == 2:
        descuento = monto * 0.20
    elif tipo_cliente == 3:
        descuento = monto * 0.35
    if monto > 1000:
        impuesto = monto * 0.18
    else:
        impuesto = monto * 0.10
    if monto > 500:
        envio = 0
    else:
        envio = 25
    return monto - descuento + impuesto + envio


def ejercicio_1():
    titulo("EJERCICIO 1: Magic Numbers")
    precio = calcular_precio_final(CLIENTE_PREMIUM, 1500)
    print(f"Precio final: ${precio}")

    casos = 0
    for tipo in (CLIENTE_REGULAR, CLIENTE_PREMIUM, CLIENTE_VIP):
        for monto in (0, 100, 500, 501, 999, 1000, 1001, 1500, 5000):
            assert calcular_precio_final(tipo, monto) == _precio_final_original(tipo, monto)
            casos += 1
    print(f"Verificación: {casos} casos dan el mismo resultado que el código original")


# EJERCICIO 2: Shotgun Surgery

class CategoriaStrategy(ABC):
    @abstractmethod
    def tasa_iva(self):
        ...

    @abstractmethod
    def garantia(self):
        ...

    @abstractmethod
    def costo_envio(self):
        ...

    def calcular_total(self, precio):
        return precio * (1 + self.tasa_iva())


_CATEGORIAS = {}


def registrar_categoria(nombre):
    """Decorador que registra una categoría. Es el único punto de alta."""
    def decorador(clase):
        _CATEGORIAS[nombre] = clase()
        return clase
    return decorador


@registrar_categoria("electronica")
class Electronica(CategoriaStrategy):
    def tasa_iva(self):
        return 0.18

    def garantia(self):
        return "2 años"

    def costo_envio(self):
        return 25  # envío seguro


@registrar_categoria("alimento")
class Alimento(CategoriaStrategy):
    def tasa_iva(self):
        return 0.05

    def garantia(self):
        return "Fecha de vencimiento"

    def costo_envio(self):
        return 10  # envío refrigerado


@registrar_categoria("general")
class General(CategoriaStrategy):
    def tasa_iva(self):
        return 0.15

    def garantia(self):
        return "6 meses"

    def costo_envio(self):
        return 15  # envío estándar


class Producto:
    def __init__(self, nombre, precio, categoria):
        self.nombre = nombre
        self.precio = precio
        self.categoria = categoria
        # Una categoría desconocida usa la estrategia general, igual que el else original
        self._estrategia = _CATEGORIAS.get(categoria, _CATEGORIAS["general"])

    def calcular_total(self):
        return self._estrategia.calcular_total(self.precio)

    def generar_factura(self):
        return f"Garantía: {self._estrategia.garantia()}"

    def calcular_envio(self):
        return self._estrategia.costo_envio()

    def resumen(self):
        print(f"{self.nombre} ({self.categoria}): total ${self.calcular_total():.2f}, "
              f"envío ${self.calcular_envio()}, {self.generar_factura()}")


def ejercicio_2():
    titulo("EJERCICIO 2: Shotgun Surgery -> Strategy")
    Producto("Laptop", 1000, "electronica").resumen()
    Producto("Arroz", 10, "alimento").resumen()

    print("\nAntes de agregar 'ropa' (cae en la estrategia general):")
    Producto("Polera", 100, "ropa").resumen()

    # ---- ÚNICO CAMBIO NECESARIO PARA AGREGAR LA CATEGORÍA "ropa" ----
    @registrar_categoria("ropa")
    class Ropa(CategoriaStrategy):
        def tasa_iva(self):
            return 0.18

        def garantia(self):
            return "30 días por defectos de fábrica"

        def costo_envio(self):
            return 12
    # -----------------------------------------------------------------

    print("\nDespués de agregar 'ropa' (sin tocar Producto ni otra clase):")
    Producto("Polera", 100, "ropa").resumen()

# EJERCICIO 3: Observer

class Observador(ABC):
    @abstractmethod
    def actualizar(self, precio):
        ...


class UsuarioEmail(Observador):
    def __init__(self, correo):
        self.correo = correo

    def actualizar(self, precio):
        print(f"  [Email a {self.correo}] Bitcoin ahora vale ${precio:,}")


class UsuarioSMS(Observador):
    def __init__(self, telefono):
        self.telefono = telefono

    def actualizar(self, precio):
        print(f"  [SMS a {self.telefono}] BTC: ${precio:,}")


class SistemaPrecio:
    """Sujeto (Subject) del patrón Observer."""

    def __init__(self):
        self.precio_btc = 50000
        self._observadores = []

    def agregar_observador(self, observador):
        if observador not in self._observadores:
            self._observadores.append(observador)

    def eliminar_observador(self, observador):
        if observador in self._observadores:
            self._observadores.remove(observador)

    def _notificar(self):
        for observador in self._observadores:
            observador.actualizar(self.precio_btc)

    def actualizar_precio(self, nuevo_precio):
        self.precio_btc = nuevo_precio
        self._notificar()


def ejercicio_3():
    titulo("EJERCICIO 3: Observer")
    sistema = SistemaPrecio()
    ana = UsuarioEmail("ana@correo.com")
    luis = UsuarioSMS("+51 999 111 222")
    sistema.agregar_observador(ana)
    sistema.agregar_observador(luis)

    print("Precio sube a 51200:")
    sistema.actualizar_precio(51200)

    # Usuario nuevo: se crea una clase nueva y no se modifica SistemaPrecio
    class UsuarioPush(Observador):
        def __init__(self, dispositivo):
            self.dispositivo = dispositivo

        def actualizar(self, precio):
            print(f"  [Push a {self.dispositivo}] BTC cambió a ${precio:,}")

    sistema.agregar_observador(UsuarioPush("celular-de-marta"))
    print("\nSe suma un tercer usuario (Push). Precio baja a 49800:")
    sistema.actualizar_precio(49800)

    sistema.eliminar_observador(ana)
    print("\nSe elimina a Ana. Precio sube a 52000:")
    sistema.actualizar_precio(52000)

# EJERCICIO 4: Caso organizacional TechSolutions S.A.C.

ANTIPATRONES_TECHSOLUTIONS = [
    ("Gestión autocrática (Irrational Management)",
     "Don Roberto decide todo sin consultar.",
     "Delegar decisiones por nivel con una matriz RACI y un comité técnico."),
    ("Silos entre equipos (Stovepipe / Throw it over the wall)",
     "Frontend, Backend y QA en pisos distintos, casi sin comunicación.",
     "Equipos multifuncionales con daily compartida y definición de 'hecho' común."),
    ("Cultura de culpa (Blame Game)",
     "El responsable del error se señala y se amonesta en público.",
     "Postmortems sin culpa, enfocados en el proceso y no en la persona."),
    ("Marcha de la muerte (Death March)",
     "Se asigna el triple de tareas de las que el equipo puede completar.",
     "Planificar según capacidad real, backlog priorizado y límite de trabajo en curso."),
    ("Martillo de oro (Golden Hammer)",
     "Carlos impone Java en todo porque es lo que domina.",
     "Criterios técnicos documentados (ADR) para elegir el lenguaje de cada proyecto."),
]


def ejercicio_4():
    titulo("EJERCICIO 4: Antipatrones de TechSolutions (resumen)")
    for i, (nombre, caso, solucion) in enumerate(ANTIPATRONES_TECHSOLUTIONS, start=1):
        print(f"{i}. {nombre}")
        print(f"   Caso:     {caso}")
        print(f"   Solución: {solucion}")
    print("\nEl plan de acción de 5 pasos está en el informe PDF.")

# EJERCICIO 5: State

class EstadoSemaforo(ABC):
    @abstractmethod
    def accion_auto(self):
        ...

    @abstractmethod
    def accion_peaton(self):
        ...

    @abstractmethod
    def siguiente_estado(self):
        ...

    @property
    def nombre(self):
        return type(self).__name__.replace("Estado", "").lower()


class EstadoRojo(EstadoSemaforo):
    def accion_auto(self):
        print("Auto: DETENERSE")

    def accion_peaton(self):
        print("Peatón: CRUZAR")

    def siguiente_estado(self):
        return EstadoVerde()


class EstadoVerde(EstadoSemaforo):
    def accion_auto(self):
        print("Auto: AVANZAR")

    def accion_peaton(self):
        print("Peatón: NO CRUZAR")

    def siguiente_estado(self):
        return EstadoAmarillo()


class EstadoAmarillo(EstadoSemaforo):
    def accion_auto(self):
        print("Auto: PRECAUCIÓN")

    def accion_peaton(self):
        print("Peatón: ESPERAR")

    def siguiente_estado(self):
        return EstadoRojo()


class Semaforo:
    """Contexto del patrón State: delega todo en el estado actual."""

    def __init__(self):
        self._estado = EstadoRojo()

    def establecer_estado(self, estado):
        self._estado = estado

    def accion_auto(self):
        self._estado.accion_auto()

    def accion_peaton(self):
        self._estado.accion_peaton()

    def cambiar_estado(self):
        self._estado = self._estado.siguiente_estado()

    @property
    def nombre_estado(self):
        return self._estado.nombre


def ejercicio_5():
    titulo("EJERCICIO 5: State (semáforo)")
    semaforo = Semaforo()
    for _ in range(4):
        print(f"Estado: {semaforo.nombre_estado}")
        semaforo.accion_auto()
        semaforo.accion_peaton()
        semaforo.cambiar_estado()
        print()

    # Estado nuevo: solo se agrega esta clase. Semaforo no cambia.
    class EstadoIntermitente(EstadoSemaforo):
        def accion_auto(self):
            print("Auto: PRECAUCIÓN, CEDER EL PASO")

        def accion_peaton(self):
            print("Peatón: ESPERAR, SEMÁFORO EN FALLA")

        def siguiente_estado(self):
            return EstadoRojo()  # al repararse vuelve al ciclo normal

    print("Se agrega EstadoIntermitente sin modificar la clase Semaforo:")
    semaforo.establecer_estado(EstadoIntermitente())
    print(f"Estado: {semaforo.nombre_estado}")
    semaforo.accion_auto()
    semaforo.accion_peaton()
    semaforo.cambiar_estado()
    print(f"Tras repararse, el estado es: {semaforo.nombre_estado}")

# EJERCICIO 6: BiblioTech v1.0 (auditoría y refactorización)

# Constantes descriptivas
MULTA_POR_DIA_EXTRA = 2.5
DIAS_MAXIMOS_OTRO_USUARIO = 5


class TipoUsuario(Enum):
    ESTUDIANTE = 1
    PROFESOR = 2
    OTRO = 3

    @classmethod
    def desde_codigo(cls, codigo):
        for tipo in (cls.ESTUDIANTE, cls.PROFESOR):
            if tipo.value == codigo:
                return tipo
        return cls.OTRO  # cualquier otro código, como el else original


class TipoLibro(Enum):
    TEXTO = "texto"
    NOVELA = "novela"
    OTRO = "otro"

    @classmethod
    def desde_nombre(cls, nombre):
        for tipo in (cls.TEXTO, cls.NOVELA):
            if tipo.value == nombre:
                return tipo
        return cls.OTRO


DIAS_MAXIMOS_ESTUDIANTE = {
    TipoLibro.TEXTO: 15,
    TipoLibro.NOVELA: 7,
    TipoLibro.OTRO: 3,
}

DIAS_MAXIMOS_PROFESOR = {
    TipoLibro.TEXTO: 30,
    TipoLibro.NOVELA: 15,
    TipoLibro.OTRO: 7,
}


class PoliticaPrestamo(ABC):
    """Strategy: cada tipo de usuario define sus días máximos."""

    @abstractmethod
    def dias_maximos(self, tipo_libro):
        ...

    def calcular_multa(self, tipo_libro, dias):
        exceso = dias - self.dias_maximos(tipo_libro)
        return exceso * MULTA_POR_DIA_EXTRA if exceso > 0 else 0


class PoliticaEstudiante(PoliticaPrestamo):
    def dias_maximos(self, tipo_libro):
        return DIAS_MAXIMOS_ESTUDIANTE[tipo_libro]


class PoliticaProfesor(PoliticaPrestamo):
    def dias_maximos(self, tipo_libro):
        return DIAS_MAXIMOS_PROFESOR[tipo_libro]


class PoliticaOtroUsuario(PoliticaPrestamo):
    def dias_maximos(self, tipo_libro):
        return DIAS_MAXIMOS_OTRO_USUARIO


POLITICAS = {
    TipoUsuario.ESTUDIANTE: PoliticaEstudiante(),
    TipoUsuario.PROFESOR: PoliticaProfesor(),
    TipoUsuario.OTRO: PoliticaOtroUsuario(),
}


class PrestamoRepositorio:
    """Guarda los préstamos. Usa consultas parametrizadas, sin concatenar SQL."""

    def __init__(self, conexion=None):
        self._conexion = conexion or sqlite3.connect(":memory:")
        self._conexion.execute(
            "CREATE TABLE IF NOT EXISTS prestamos ("
            "tipo_usuario INTEGER, tipo_libro TEXT, dias INTEGER, multa REAL)"
        )

    def guardar(self, tipo_usuario, tipo_libro, dias, multa):
        self._conexion.execute(
            "INSERT INTO prestamos VALUES (?, ?, ?, ?)",
            (tipo_usuario.value, tipo_libro.value, dias, multa),
        )
        self._conexion.commit()

    def listar(self):
        return self._conexion.execute("SELECT * FROM prestamos").fetchall()


class ServicioPrestamo:
    def __init__(self, repositorio):
        self._repositorio = repositorio

    def procesar_prestamo(self, codigo_usuario, nombre_libro, dias):
        tipo_usuario = TipoUsuario.desde_codigo(codigo_usuario)
        tipo_libro = TipoLibro.desde_nombre(nombre_libro)
        multa = POLITICAS[tipo_usuario].calcular_multa(tipo_libro, dias)
        self._repositorio.guardar(tipo_usuario, tipo_libro, dias, multa)
        return multa


def _multa_original(tipo_usuario, tipo_libro, dias):
    """Lógica original de BiblioTech, solo para comparar resultados."""
    if tipo_usuario == 1:
        if tipo_libro == "texto":
            max_dias = 15
        elif tipo_libro == "novela":
            max_dias = 7
        else:
            max_dias = 3
    elif tipo_usuario == 2:
        if tipo_libro == "texto":
            max_dias = 30
        elif tipo_libro == "novela":
            max_dias = 15
        else:
            max_dias = 7
    else:
        max_dias = 5
    return (dias - max_dias) * 2.5 if dias > max_dias else 0


def ejercicio_6():
    titulo("EJERCICIO 6: BiblioTech refactorizado")
    repositorio = PrestamoRepositorio()
    servicio = ServicioPrestamo(repositorio)

    costo = servicio.procesar_prestamo(1, "novela", 10)
    print(f"Multa: ${costo}")
    print(f"Registro guardado: {repositorio.listar()}")

    casos = 0
    for usuario in (1, 2, 3, 9):
        for libro in ("texto", "novela", "revista"):
            for dias in range(0, 41):
                esperado = _multa_original(usuario, libro, dias)
                assert servicio.procesar_prestamo(usuario, libro, dias) == esperado
                casos += 1
    print(f"Verificación: {casos} casos dan la misma multa que el código original")

# PROGRAMA PRINCIPAL

if __name__ == "__main__":
    ejercicio_1()
    ejercicio_2()
    ejercicio_3()
    ejercicio_4()
    ejercicio_5()
    ejercicio_6()
