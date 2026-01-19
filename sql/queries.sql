-- 1) Bugs abiertos por severidad
SELECT severity, COUNT(*) AS bugs_open
FROM bug
WHERE status IN ('Open','In Progress','Blocked')
GROUP BY 1
ORDER BY CASE severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END;

-- 2) Lead time promedio (días) para bugs resueltos/cerrados
SELECT AVG(resolved_date - created_date) AS avg_resolution_days
FROM bug
WHERE status IN ('Resolved','Closed')
  AND resolved_date IS NOT NULL;

-- 3) Backlog total (abiertos)
SELECT COUNT(*) AS backlog
FROM bug
WHERE status IN ('Open','In Progress','Blocked');

-- 4) Módulos con más bugs (últimos 90 días)
SELECT module, COUNT(*) AS bugs_90d
FROM bug
WHERE created_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY 1
ORDER BY 2 DESC;

-- 5) WIP por asignado
SELECT assigned_to,
       COUNT(*) FILTER (WHERE status='In Progress') AS in_progress,
       COUNT(*) FILTER (WHERE status='Blocked')     AS blocked,
       COUNT(*) FILTER (WHERE status='Open')        AS open
FROM bug
GROUP BY 1
ORDER BY (COUNT(*) FILTER (WHERE status='In Progress')) DESC;