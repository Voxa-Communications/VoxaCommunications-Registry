import datetime
from flask import Request, jsonify
from util.sqlExecutor import SQLExecutor
from util.logging import log
from lib.jwt_manager import token_required

@token_required
def handler(current_user_id: int, request: Request):
    logger = log()
    logger.info(f"Node update API called, w/ method: {request.method}")
    
    if request.method == "PUT":
        data: dict = request.get_json()
        if not data:
            logger.warning("Node update attempt with no data provided")
            return jsonify({"error": "No data provided"}), 400
        
        # Check required fields
        if 'node_id' not in data:
            logger.warning("Node update missing required field: node_id")
            return jsonify({"error": "Missing node_id field"}), 400
        
        node_id = data.get('node_id')
        
        # Fetch the node to verify it exists and belongs to the user
        fetch_sql = "SELECT creator_id FROM nodes WHERE id = %s;"
        sql_executor = SQLExecutor("", None)
        sql_executor.DBManager.cursor.execute(fetch_sql, (node_id,))
        node = sql_executor.DBManager.cursor.fetchone()
        
        if not node:
            logger.warning(f"Node update failed: Node {node_id} not found")
            return jsonify({"error": "Node not found"}), 404
            
        creator_id = str(node[0])
        if str(current_user_id) != creator_id:
            logger.warning(f"Node update failed: User {current_user_id} not authorized to update node {node_id}")
            return jsonify({"error": "Not authorized to update this node"}), 403
        
        # Prepare update fields
        update_fields = []
        update_values = []
        
        if 'name' in data:
            update_fields.append("callsign = %s")
            update_values.append(data.get('name'))
            
        if 'ip' in data:
            update_fields.append("ip_address = %s")
            update_values.append(data.get('ip'))
            
        if 'key' in data:
            update_fields.append("crypto_key = %s")
            update_values.append(data.get('key'))
            
        if 'type' in data:
            update_fields.append("node_type = %s")
            update_values.append(data.get('type'))
            
        if 'active' in data:
            update_fields.append("is_active = %s")
            update_values.append(bool(data.get('active')))
        
        # Add updated_at field
        update_fields.append("updated_at = %s")
        update_values.append(datetime.datetime.now().isoformat())
        
        # Add node_id to values
        update_values.append(node_id)
        
        if not update_fields:
            logger.warning("Node update failed: No fields to update")
            return jsonify({"error": "No fields to update"}), 400
            
        # Build and execute update query
        update_sql = f"UPDATE nodes SET {', '.join(update_fields)} WHERE id = %s;"
        
        try:
            sql_executor.DBManager.cursor.execute(update_sql, tuple(update_values))
            sql_executor.DBManager.connection.commit()
            
            logger.info(f"Node {node_id} updated successfully")
            return jsonify({"message": "Node updated successfully"}), 200
        except Exception as e:
            sql_executor.DBManager.connection.rollback()
            logger.error(f"Error updating node {node_id}: {e}")
            return jsonify({"error": f"Error updating node: {str(e)}"}), 500
    else:
        logger.warning(f"Invalid request method for node update: {request.method}")
        return jsonify({"error": "Invalid request method, use PUT"}), 405