from enum import Enum
from typing import NamedTuple


class SubCategory(Enum):
    # Subcategorías definidas
    SUPERMERCADOS_ALIMENTACION = "Supermercados y alimentación"

    # Compras
    BELLEZA_PELUQUERIA_PERFUMERIA = "Belleza, peluquería y perfumería"
    COMPRAS_OTROS = "Compras (otros)"
    REGALOS_JUGUETES = "Regalos y juguetes"
    ROPA_COMPLEMENTOS = "Ropa y complementos"

    # Educación, salud y deporte
    DENTISTA_MEDICO = "Dentista, médico"
    DEPORTE_GIMNASIO = "Deporte y gimnasio"
    EDUCACION = "Educación"
    FARMACIA_HERBOLARIO_NUTRICION = "Farmacia, herbolario y nutrición"
    MATERIAL_DEPORTIVO = "Material deportivo"

    # Hogar
    AGUA = "Agua"
    CALEFACCION = "Calefacción"
    COMUNIDAD = "Comunidad"
    INTERNET = "Internet"
    LUZ_GAS = "Luz y gas"
    LUZ = "Luz"
    MANTENIMIENTO_HOGAR = "Mantenimiento del hogar"
    MENAJE = "Menaje"
    MOVIL = "Móvil"
    SEGURO_HOGAR = "Seguro de hogar"
    TLF_TV_NET = "Teléfono, TV e internet"
    DECORACION_MOBILIARIO = "Decoración y mobiliario"
    HOGAR_OTROS = "Hogar (otros)"

    # Impuestos
    IBI = "IBI"
    IRPF = "IRPF"
    IMPUESTOS_OTROS = "Impuestos (otros)"
    VISADO_ALQUILER = "Visado Alquiler"

    # Inversión
    ABONO_INTERESES = "Abono de intereses"
    FONDOS = "Fondos de inversión"
    OTRAS_INVERSIONES = "Inversión (otros)"

    # Transferencia
    TRANSFERENCIA_BANCARIA = "Transferencia recibida"
    TRANSACCION_CUENTAS = "Transacción entre cuentas"

    # Nómina o Pensión
    NOMINA_PENSION = "Nómina o Pensión"

    # Ocio y viajes
    BILLETES_VIAJE = "Billetes de viaje"
    CAFETERIAS_RESTAURANTES = "Cafeterías y restaurantes"
    CINE_TEATRO_ESPECTACULOS = "Cine, teatro y espectáculos"
    HOTEL_ALOJAMIENTO = "Hotel y alojamiento"
    LIBROS_MUSICA_JUEGOS = "Libros, música y juegos"
    OCIO_VIAJES_OTROS = "Ocio y viajes (otros)"

    # Otros gastos
    CAJEROS = "Cajeros"
    COMISIONES_INTERESES = "Comisiones e intereses"
    ONG = "ONG"
    OTROS_GASTOS_OTROS = "Otros gastos (otros)"
    TRANSFERENCIAS = "Transferencias"

    # Otros ingresos
    ALQUILER = "Alquiler"
    OTROS_INGRESOS = "Otros ingresos (otros)"
    SEGUNDA_MANO = "Segunda mano"
    INGRESO_EFECTIVO = "Ingresos de efectivo"
    INGRESO_OTRA_ENTIDAD = "Ingresos de otras entidades"

    # Saldo inicial
    SALDO_INICIAL = "Saldo inicial"

    # Sin subcategoría
    SIN_SUBCATEGORIA = "Sin subcategoría"

    # Vehículo y transporte
    TAXI_CARSHARING = "Taxi y Carsharing"
    TRANSPORTE_PUBLICO = "Transporte público"
    VEHICULO = "Mantenimiento de vehículo"

    def __str__(self) -> str:
        return self.value

    def parent(self):
        return Category.of(self)

    @staticmethod
    def find(s: str):
        for sub in SubCategory:
            if sub.value == s:
                return sub
        raise ValueError(f"Subcategory {s} not found")


class CategoryVal(NamedTuple):
    category: str
    subs: tuple[SubCategory, ...]

    def __str__(self):
        return self.category


def mkCat(s: str, *subs: SubCategory) -> CategoryVal:
    return CategoryVal(s, subs)


class Category(Enum):
    ALIMENTACION = mkCat(
        "Alimentación", 
        SubCategory.SUPERMERCADOS_ALIMENTACION
    )

    COMPRAS = mkCat(
        "Compras",
        SubCategory.BELLEZA_PELUQUERIA_PERFUMERIA,
        SubCategory.COMPRAS_OTROS,
        SubCategory.REGALOS_JUGUETES,
        SubCategory.ROPA_COMPLEMENTOS
    )

    EDUCACION_SALUD_DEPORTE = mkCat(
        "Educación, salud y deporte",
        SubCategory.DENTISTA_MEDICO,
        SubCategory.DEPORTE_GIMNASIO,
        SubCategory.EDUCACION,
        SubCategory.FARMACIA_HERBOLARIO_NUTRICION,
        SubCategory.MATERIAL_DEPORTIVO
    )

    HOGAR = mkCat(
        "Hogar",
        SubCategory.AGUA,
        SubCategory.CALEFACCION,
        SubCategory.COMUNIDAD,
        SubCategory.INTERNET,
        SubCategory.LUZ_GAS,
        SubCategory.LUZ,
        SubCategory.MANTENIMIENTO_HOGAR,
        SubCategory.MENAJE,
        SubCategory.MOVIL,
        SubCategory.SEGURO_HOGAR,
        SubCategory.TLF_TV_NET,
        SubCategory.DECORACION_MOBILIARIO,
        SubCategory.HOGAR_OTROS
    )

    IMPUESTOS = mkCat(
        "Impuestos",
        SubCategory.IBI,
        SubCategory.IRPF,
        SubCategory.IMPUESTOS_OTROS,
        SubCategory.VISADO_ALQUILER
    )

    INVERSION = mkCat(
        "Inversión",
        SubCategory.ABONO_INTERESES,
        SubCategory.FONDOS,
        SubCategory.OTRAS_INVERSIONES
    )

    TRANSFERENCIA = mkCat(
        "Transferencia",
        SubCategory.TRANSACCION_CUENTAS,
        SubCategory.TRANSFERENCIA_BANCARIA
    )

    NOMINA_PRESTACIONES = mkCat(
        "Nómina y otras prestaciones",
        SubCategory.NOMINA_PENSION
    )

    OCIO_VIAJES = mkCat(
        "Ocio y viajes",
        SubCategory.BILLETES_VIAJE,
        SubCategory.CAFETERIAS_RESTAURANTES,
        SubCategory.CINE_TEATRO_ESPECTACULOS,
        SubCategory.HOTEL_ALOJAMIENTO,
        SubCategory.LIBROS_MUSICA_JUEGOS,
        SubCategory.OCIO_VIAJES_OTROS
    )

    OTROS_GASTOS = mkCat(
        "Otros gastos",
        SubCategory.CAJEROS,
        SubCategory.COMISIONES_INTERESES,
        SubCategory.ONG,
        SubCategory.OTROS_GASTOS_OTROS,
        SubCategory.TRANSFERENCIAS
    )

    OTROS_INGRESOS = mkCat(
        "Otros ingresos",
        SubCategory.ALQUILER,
        SubCategory.OTROS_INGRESOS,
        SubCategory.SEGUNDA_MANO,
        SubCategory.INGRESO_OTRA_ENTIDAD,
        SubCategory.INGRESO_EFECTIVO
    )

    SALDO_INICIAL = mkCat(
        "Saldo inicial",
        SubCategory.SALDO_INICIAL
    )

    SIN_SUBCATEGORIA = mkCat(
        "Sin subcategoría",
        SubCategory.SIN_SUBCATEGORIA
    )

    VEHICULO_TRANSPORTE = mkCat(
        "Vehículo y transporte",
        SubCategory.TAXI_CARSHARING,
        SubCategory.TRANSPORTE_PUBLICO,
        SubCategory.VEHICULO
    )

    def __str__(self) -> str:
        return self.value.category

    @staticmethod
    def of(sub: SubCategory):
        for c in Category:
            if sub in c.value.subs:
                return c
        raise ValueError(f"Subcategory {sub} not found in any category")

