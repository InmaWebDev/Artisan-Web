-- Tabla de Usuarios
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    correo TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    rol TEXT DEFAULT 'cliente' -- 'admin' o 'cliente'
);

-- Tabla de Productos
CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio REAL NOT NULL,
    cantidad_disponible INTEGER NOT NULL,
    categoria TEXT, -- Filtro: Cerámica, Textil, Madera, etc.
    material TEXT,  -- Filtro: Barro, Lana, Roble...
    imagen_url TEXT,  -- Ruta de la foto
    img2 TEXT,         -- segunda imagen opcional
    img3 TEXT,         -- tercera imagen opcional
    parent_id INTEGER      -- id del producto padre si es subproducto
);