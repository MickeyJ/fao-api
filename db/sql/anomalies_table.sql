CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    area_id INTEGER NOT NULL REFERENCES areas(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
);

CREATE TABLE anomalies_details (
    id SERIAL PRIMARY KEY,
    anomaly_id INTEGER NOT NULL REFERENCES anomalies(id) ON DELETE CASCADE,
    anomaly_type VARCHAR(50) NOT NULL,
    anomaly_date DATE NOT NULL,
    details TEXT NOT NULL
);