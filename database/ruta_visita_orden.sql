INSERT IGNORE INTO ruta_visita_orden (ruta_visita, establecimiento, orden)
SELECT
    rv.numero,
    e.numero,
    ROW_NUMBER() OVER (PARTITION BY rv.numero ORDER BY e.numero)
FROM ruta_visita rv
INNER JOIN establecimiento e ON e.zona = rv.zona
WHERE e.edo_establecimiento = 'EST001';