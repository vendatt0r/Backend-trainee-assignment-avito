CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('client', 'moderator'))
);
"""
CREATE_PICKUP_POINTS_TABLE = """
CREATE TABLE IF NOT EXISTS pickup_points (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    city TEXT NOT NULL CHECK (city IN ('Москва', 'Санкт-Петербург', 'Казань'))
);
"""
CREATE_INTAKES_TABLE = """
CREATE TABLE IF NOT EXISTS intakes (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL CHECK (status IN ('in_progress', 'close')),
    pickup_point_id INTEGER NOT NULL REFERENCES pickup_points(id)
);
"""
CREATE_ITEMS_TABLE = """
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    type TEXT NOT NULL CHECK (type IN ('электроника', 'одежда', 'обувь')),
    intake_id INTEGER NOT NULL REFERENCES intakes(id)
);
"""
