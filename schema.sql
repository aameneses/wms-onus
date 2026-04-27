-- ============================================================
-- WMS - Warehouse Management System
-- Script SQL para Supabase (PostgreSQL)
-- ============================================================

-- Tabla de Tarifas
CREATE TABLE IF NOT EXISTS tarifas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio_pallet_dia NUMERIC(10,2) NOT NULL DEFAULT 0,
    precio_picking NUMERIC(10,2) NOT NULL DEFAULT 0,
    precio_carga NUMERIC(10,2) NOT NULL DEFAULT 0,
    precio_descarga NUMERIC(10,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    empresa VARCHAR(150),
    condiciones_pago VARCHAR(200),
    tarifa_id INTEGER REFERENCES tarifas(id) ON DELETE SET NULL,
    email VARCHAR(150),
    telefono VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de Stock
CREATE TABLE IF NOT EXISTS stock (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    pallet VARCHAR(100) NOT NULL,
    referencia VARCHAR(100),
    cantidad INTEGER NOT NULL DEFAULT 1,
    fecha_entrada DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_salida DATE,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    observaciones TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de Movimientos
CREATE TABLE IF NOT EXISTS movimientos (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('almacenaje','picking','packing','carga','descarga')),
    cantidad NUMERIC(10,2) NOT NULL DEFAULT 1,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    observaciones TEXT,
    coste NUMERIC(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para rendimiento
CREATE INDEX IF NOT EXISTS idx_movimientos_cliente ON movimientos(cliente_id);
CREATE INDEX IF NOT EXISTS idx_movimientos_fecha ON movimientos(fecha);
CREATE INDEX IF NOT EXISTS idx_movimientos_tipo ON movimientos(tipo);
CREATE INDEX IF NOT EXISTS idx_stock_cliente ON stock(cliente_id);
CREATE INDEX IF NOT EXISTS idx_stock_activo ON stock(activo);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tarifas_updated_at BEFORE UPDATE ON tarifas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clientes_updated_at BEFORE UPDATE ON clientes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- DATOS DE EJEMPLO
-- ============================================================

INSERT INTO tarifas (nombre, precio_pallet_dia, precio_picking, precio_carga, precio_descarga) VALUES
('Tarifa Básica',    0.50, 1.20, 25.00, 25.00),
('Tarifa Estándar',  0.75, 1.80, 35.00, 35.00),
('Tarifa Premium',   1.20, 2.50, 50.00, 50.00),
('Tarifa Especial',  0.60, 1.50, 30.00, 28.00)
ON CONFLICT DO NOTHING;

INSERT INTO clientes (nombre, empresa, condiciones_pago, tarifa_id, email, telefono) VALUES
('Carlos Martínez',  'Logística Sur S.L.',     '30 días neto',   1, 'carlos@logisticasur.com',  '654 321 098'),
('Ana García',       'Distribuciones Norte',    '15 días neto',   2, 'ana@distnorte.com',        '612 456 789'),
('Pedro Fernández',  'Almacenes Ibéricos S.A.', 'Contado',        3, 'pedro@almiberi.com',       '699 123 456'),
('Laura Sánchez',    'Grupo Logístico XYZ',     '60 días neto',   2, 'laura@grupoxyz.com',       '677 890 123'),
('Miguel Torres',    'Fast Delivery S.L.',      '30 días neto',   1, 'miguel@fastdelivery.com',  '611 234 567')
ON CONFLICT DO NOTHING;

INSERT INTO stock (cliente_id, pallet, referencia, cantidad, fecha_entrada, activo) VALUES
(1, 'PAL-001', 'REF-A100', 1, CURRENT_DATE - 15, TRUE),
(1, 'PAL-002', 'REF-A101', 1, CURRENT_DATE - 10, TRUE),
(2, 'PAL-003', 'REF-B200', 1, CURRENT_DATE - 8,  TRUE),
(2, 'PAL-004', 'REF-B201', 1, CURRENT_DATE - 8,  TRUE),
(3, 'PAL-005', 'REF-C300', 1, CURRENT_DATE - 20, TRUE),
(3, 'PAL-006', 'REF-C301', 1, CURRENT_DATE - 5,  TRUE),
(4, 'PAL-007', 'REF-D400', 1, CURRENT_DATE - 3,  TRUE),
(5, 'PAL-008', 'REF-E500', 1, CURRENT_DATE - 12, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO movimientos (cliente_id, tipo, cantidad, fecha, observaciones, coste) VALUES
(1, 'descarga',   5,  CURRENT_DATE - 15, 'Recepción inicial lote A',    125.00),
(1, 'almacenaje', 15, CURRENT_DATE - 15, 'Almacenaje pallets lote A',   11.25),
(1, 'picking',    20, CURRENT_DATE - 10, 'Preparación pedido #1001',    24.00),
(2, 'descarga',   8,  CURRENT_DATE - 8,  'Recepción mercancía cliente', 280.00),
(2, 'almacenaje', 8,  CURRENT_DATE - 8,  'Almacenaje inicial',          12.00),
(2, 'carga',      4,  CURRENT_DATE - 5,  'Expedición pedido #2001',    140.00),
(3, 'descarga',   12, CURRENT_DATE - 20, 'Gran recepción C',            600.00),
(3, 'almacenaje', 20, CURRENT_DATE - 20, 'Stock inicial',               24.00),
(3, 'picking',    35, CURRENT_DATE - 12, 'Picking masivo',               87.50),
(3, 'packing',    35, CURRENT_DATE - 12, 'Empaquetado pedidos',         52.50),
(4, 'descarga',   3,  CURRENT_DATE - 3,  'Recepción urgente',           84.00),
(5, 'descarga',   6,  CURRENT_DATE - 12, 'Descarga programada',        150.00),
(5, 'carga',      6,  CURRENT_DATE - 2,  'Expedición completa',        150.00)
ON CONFLICT DO NOTHING;
