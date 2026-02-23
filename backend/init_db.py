#!/usr/bin/env python3
"""
Script para inicializar la BD con datos de prueba.
Uso: python init_db.py
"""

from datetime import datetime, timedelta
from app.database import SessionLocal, Base, engine
from app.models import Usuario, Cliente, ArchivoProcesado, EnergiaExcedentaria, TipoAutoconsumo
from app.utils.auth import get_password_hash
from decimal import Decimal

def init_db():
    """Crea tablas y agrega datos de prueba."""
    
    # Drop and recreate for schema changes in development
    print("Sincronizando esquema de tablas...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Crear tipos de autoconsumo (necesarios para las claves foráneas)
        print("Creando tipos de autoconsumo...")
        tipos = [
            TipoAutoconsumo(codigo=12, descripcion="Individual con excedentes y compensación"),
            TipoAutoconsumo(codigo=41, descripcion="Colectivo sin excedentes"),
            TipoAutoconsumo(codigo=42, descripcion="Colectivo con excedentes y compensación"),
            TipoAutoconsumo(codigo=43, descripcion="Colectivo con excedentes no acogido a compensación"),
            TipoAutoconsumo(codigo=51, descripcion="Próxima a través de red"),
        ]
        db.add_all(tipos)
        db.commit()
        print(f"✓ {len(tipos)} tipos de autoconsumo creados")

        # Crear usuarios (contraseñas reales para login API)
        print("Creando usuarios...")
        usuarios = [
            Usuario(
                username="admin",
                email="admin@example.com",
                password_hash=get_password_hash("admin123"),
                nombre_completo="Administrador",
                rol="admin",
                activo=True
            ),
            Usuario(
                username="operador1",
                email="operador1@example.com",
                password_hash=get_password_hash("operador123"),
                nombre_completo="Operador Uno",
                rol="operador",
                activo=True
            ),
            Usuario(
                username="operador2",
                email="operador2@example.com",
                password_hash=get_password_hash("operador123"),
                nombre_completo="Operador Dos",
                rol="operador",
                activo=True
            ),
            Usuario(
                username="consultor",
                email="consultor@example.com",
                password_hash=get_password_hash("consultor123"),
                nombre_completo="Consultor",
                rol="consultor",
                activo=True
            ),
        ]
        db.add_all(usuarios)
        db.commit()
        print(f"✓ {len(usuarios)} usuarios creados")
        
        # Crear clientes
        print("Creando clientes...")
        clientes = [
            Cliente(
                cups="ES0031405098401001",
                nombre_cliente="Cliente Solar S.L.",
                email="cliente1@example.com",
                telefono="912345678",
                direccion="Calle Principal 123",
                municipio="Madrid",
                provincia="Madrid",
                codigo_postal="28001",
                activo=True
            ),
            Cliente(
                cups="ES0031405098401002",
                nombre_cliente="Energía Renovable Ltd",
                email="cliente2@example.com",
                telefono="934567890",
                direccion="Avenida Central 456",
                municipio="Barcelona",
                provincia="Barcelona",
                codigo_postal="08002",
                activo=True
            ),
            Cliente(
                cups="ES0031405098401003",
                nombre_cliente="Panel Power Spain",
                email="cliente3@example.com",
                telefono="954321098",
                direccion="Paseo Marítimo 789",
                municipio="Sevilla",
                provincia="Sevilla",
                codigo_postal="41001",
                activo=True
            ),
            Cliente(
                cups="ES0031405098401004",
                nombre_cliente="EcoEnergy Solutions",
                email="cliente4@example.com",
                telefono="963987654",
                direccion="Plaza Mayor 321",
                municipio="Valencia",
                provincia="Valencia",
                codigo_postal="46001",
                activo=True
            ),
        ]
        db.add_all(clientes)
        db.commit()
        print(f"✓ {len(clientes)} clientes creados")
        
        # Crear archivos procesados
        print("Creando archivos procesados...")
        ahora = datetime.utcnow()
        archivos = [
            ArchivoProcesado(
                usuario_id=usuarios[0].id,
                nombre_archivo="peajes_enero_2024.xml",
                hash_archivo="abc123def456" + "0" * 48,
                estado="completado",
                ruta_archivo="/uploads/peajes_enero_2024.xml",
                total_registros=10,
                registros_exitosos=9,
                registros_con_error=1,
                fecha_carga=ahora - timedelta(days=5),
                fecha_procesamiento=ahora - timedelta(days=5, hours=1)
            ),
            ArchivoProcesado(
                usuario_id=usuarios[1].id,
                nombre_archivo="peajes_febrero_2024.xml",
                hash_archivo="def789ghi012" + "0" * 48,
                estado="completado",
                ruta_archivo="/uploads/peajes_febrero_2024.xml",
                total_registros=15,
                registros_exitosos=15,
                registros_con_error=0,
                fecha_carga=ahora - timedelta(days=3),
                fecha_procesamiento=ahora - timedelta(days=3, hours=1)
            ),
            ArchivoProcesado(
                usuario_id=usuarios[1].id,
                nombre_archivo="peajes_marzo_2024.xml",
                hash_archivo="ghi345jkl678" + "0" * 48,
                estado="procesando",
                ruta_archivo="/uploads/peajes_marzo_2024.xml",
                total_registros=12,
                registros_exitosos=8,
                registros_con_error=2,
                fecha_carga=ahora - timedelta(hours=2),
                fecha_procesamiento=None
            ),
        ]
        db.add_all(archivos)
        db.commit()
        print(f"✓ {len(archivos)} archivos creados")
        
        # Crear registros de energía
        print("Creando registros de energía...")
        registros_energia = [
            EnergiaExcedentaria(
                archivo_id=archivos[0].id,
                cliente_id=clientes[0].id,
                cups_cliente=clientes[0].cups,
                instalacion_gen="ES0031405098401001_GEN",
                tipo_autoconsumo=12,
                linea_archivo=1,
                fecha_desde=(ahora - timedelta(days=35)).date(),
                fecha_hasta=(ahora - timedelta(days=5)).date(),
                energia_neta_gen=[Decimal("100.50"), Decimal("105.25"), Decimal("98.75"), Decimal("110.00"), Decimal("102.30"), Decimal("101.45")],
                energia_autoconsumida=[Decimal("50.25"), Decimal("52.10"), Decimal("49.80"), Decimal("55.00"), Decimal("51.15"), Decimal("50.70")],
                pago_tda=[Decimal("25.12"), Decimal("26.05"), Decimal("24.90"), Decimal("27.50"), Decimal("25.58"), Decimal("25.35")]
            ),
            EnergiaExcedentaria(
                archivo_id=archivos[0].id,
                cliente_id=clientes[1].id,
                cups_cliente=clientes[1].cups,
                instalacion_gen="ES0031405098401002_GEN",
                tipo_autoconsumo=41,
                linea_archivo=2,
                fecha_desde=(ahora - timedelta(days=35)).date(),
                fecha_hasta=(ahora - timedelta(days=5)).date(),
                energia_neta_gen=[Decimal("200.00"), Decimal("205.00"), Decimal("198.00"), Decimal("210.00"), Decimal("202.00"), Decimal("201.00")],
                energia_autoconsumida=[Decimal("100.00"), Decimal("102.50"), Decimal("99.00"), Decimal("105.00"), Decimal("101.00"), Decimal("100.50")],
                pago_tda=[Decimal("50.00"), Decimal("51.25"), Decimal("49.50"), Decimal("52.50"), Decimal("50.50"), Decimal("50.25")]
            ),
            EnergiaExcedentaria(
                archivo_id=archivos[1].id,
                cliente_id=clientes[2].id,
                cups_cliente=clientes[2].cups,
                instalacion_gen="ES0031405098401003_GEN",
                tipo_autoconsumo=12,
                linea_archivo=1,
                fecha_desde=(ahora - timedelta(days=65)).date(),
                fecha_hasta=(ahora - timedelta(days=35)).date(),
                energia_neta_gen=[Decimal("150.75"), Decimal("155.50"), Decimal("148.25"), Decimal("160.00"), Decimal("152.50"), Decimal("151.25")],
                energia_autoconsumida=[Decimal("75.37"), Decimal("77.75"), Decimal("74.12"), Decimal("80.00"), Decimal("76.25"), Decimal("75.62")],
                pago_tda=[Decimal("37.68"), Decimal("38.87"), Decimal("37.06"), Decimal("40.00"), Decimal("38.12"), Decimal("37.81")]
            ),
            EnergiaExcedentaria(
                archivo_id=archivos[1].id,
                cliente_id=clientes[3].id,
                cups_cliente=clientes[3].cups,
                instalacion_gen="ES0031405098401004_GEN",
                tipo_autoconsumo=51,
                linea_archivo=2,
                fecha_desde=(ahora - timedelta(days=65)).date(),
                fecha_hasta=(ahora - timedelta(days=35)).date(),
                energia_neta_gen=[Decimal("300.00"), Decimal("310.00"), Decimal("290.00"), Decimal("320.00"), Decimal("305.00"), Decimal("295.00")],
                energia_autoconsumida=[Decimal("150.00"), Decimal("155.00"), Decimal("145.00"), Decimal("160.00"), Decimal("152.50"), Decimal("147.50")],
                pago_tda=[Decimal("75.00"), Decimal("77.50"), Decimal("72.50"), Decimal("80.00"), Decimal("76.25"), Decimal("73.75")]
            ),
        ]
        db.add_all(registros_energia)
        db.commit()
        print(f"✓ {len(registros_energia)} registros de energía creados")
        
        print("\n✅ Base de datos inicializada correctamente!")
        print(f"  - Usuarios: {db.query(Usuario).count()}")
        print(f"  - Clientes: {db.query(Cliente).count()}")
        print(f"  - Tipos Autoconsumo: {db.query(TipoAutoconsumo).count()}")
        print(f"  - Archivos: {db.query(ArchivoProcesado).count()}")
        print(f"  - Registros de energía: {db.query(EnergiaExcedentaria).count()}")
        print("\n📋 Credenciales de login (API usa 'username', no email):")
        print("   admin     / admin123")
        print("   operador1 / operador123")
        print("   operador2 / operador123")
        print("   consultor / consultor123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
