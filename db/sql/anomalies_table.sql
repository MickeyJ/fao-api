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


SELECT 
    areas.name AS area_name,
    items.name AS item_name,
    item_prices.year AS item_year,
    item_prices.currency AS item_currency,
    item_prices.value AS item_price
FROM anomalies
JOIN item_prices ON anomalies.item_id = item_prices.item_id 
                 AND anomalies.area_id = item_prices.area_id
JOIN areas ON anomalies.area_id = areas.id
JOIN items ON anomalies.item_id = items.id
ORDER BY areas.name, items.name, item_prices.year;