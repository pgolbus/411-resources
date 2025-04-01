DROP TABLE IF EXISTS boxers;
CREATE TABLE boxers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    weight REAL NOT NULL CHECK (weight > 0),
    height REAL NOT NULL CHECK (height > 0),
    reach REAL CHECK (reach > 0),
    age INTEGER NOT NULL CHECK (age >= 18 AND age <= 40),
    fights INTEGER DEFAULT 0 CHECK (fights >= 0),
    wins INTEGER DEFAULT 0 CHECK (wins >= 0 AND wins <= fights)  -- Wins cannot exceed fights
);

CREATE UNIQUE INDEX idx_boxers_name ON boxers(name);
