SELECT areas.name, COUNT(*) as duplicate_records
FROM item_prices ip
JOIN areas ON ip.area_id = areas.id
WHERE (ip.item_id, ip.area_id, ip.year) IN (
    SELECT item_id, area_id, year FROM item_prices 
    GROUP BY item_id, area_id, year HAVING COUNT(*) > 1
)
GROUP BY areas.name
ORDER BY duplicate_records DESC;