CREATE TABLE mensajes (
    id_message SERIAL PRIMARY KEY,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('usuario', 'asistente')),
    contenido TEXT NOT NULL,
    fecha TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE hechos (
    id_hecho SERIAL PRIMARY KEY,
    categoria VARCHAR(50) NOT NULL CHECK (categoria IN (
        'identidad', 'gustos', 'disgustos', 'cosas_preciadas',
        'intereses', 'rutinas', 'relaciones', 'otros'
    )),
    valor TEXT NOT NULL
);