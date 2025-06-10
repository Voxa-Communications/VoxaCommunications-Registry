SELECT 
    node_type,
    COUNT(*) as total_nodes,
    COUNT(CASE WHEN is_active = TRUE THEN 1 END) as online_nodes,
    COUNT(CASE WHEN is_active = FALSE THEN 1 END) as offline_nodes
FROM nodes 
GROUP BY node_type;