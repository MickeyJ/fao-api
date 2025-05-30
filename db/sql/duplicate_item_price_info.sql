SELECT 
    areas.name as area_name,
    items.name as item_name,
    ip.year,
    COUNT(*) as duplicate_count,
    MIN(ip.value) as min_value,
    MAX(ip.value) as max_value,
    AVG(ip.value) as avg_value,
    STRING_AGG(DISTINCT ip.currency, ', ') as currencies,
    STRING_AGG(ip.value::text, ', ' ORDER BY ip.value) as all_values,
    STRING_AGG(ip.id::text, ', ' ORDER BY ip.id) as record_ids
FROM item_prices ip
JOIN areas ON ip.area_id = areas.id  
JOIN items ON ip.item_id = items.id
GROUP BY areas.name, items.name, ip.year, ip.item_id, ip.area_id
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC, area_name, item_name, ip.year;