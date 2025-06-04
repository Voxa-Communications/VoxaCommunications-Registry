import uuid
import datetime
from flask import Request, jsonify
from util.sqlExecutor import SQLExecutor
from util.logging import log
from lib.jwt_manager import token_required

@token_required
def handler(current_user_id: int, request: Request, struct_loader=None):
    logger = log()
    logger.info(f"Node registration API called, w/ method: {request.method}")
    
    if request.method == "POST":
        data: dict = request.get_json()
        if not data:
            logger.warning("Node registration attempt with no data provided")
            return jsonify({"error": "No data provided"}), 400
        
        required_fields = ['name', 'type']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            logger.warning(f"Node registration missing required fields: {missing_fields}")
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        callsign = data.get('name')
        # Use provided IP or default to requester's IP
        ip = data.get('ip') or request.remote_addr
        crypto_key = data.get('key') or "none"
        node_type = data.get('type')
        
        logger.info(f"Processing node registration - Name: {callsign}, IP: {ip}, Type: {node_type}")
        
        try:
            node_id = str(uuid.uuid4())
            logger.debug(f"Generated node ID: {node_id}")
            
            # Create timestamps
            now = datetime.datetime.now().isoformat()
            
            # Create node
            sql_executor = SQLExecutor("input_node", None)
            sql_executor.execute_sql((node_id, current_user_id, ip, callsign, crypto_key, node_type, now, now, True))
            
            logger.info(f"Node registered successfully: {node_id}, Name: {callsign}, Type: {node_type}")
            return jsonify({
                "message": "Node registered successfully", 
                "node_id": node_id,
                "registered_by": current_user_id,
                "timestamp": now,
                "node_ip": ip
            }), 201
        except Exception as e:
            logger.error(f"Error during node registration for {callsign}: {e}")
            return jsonify({"error": str(e)}), 500
    else:
        logger.warning(f"Invalid request method for node registration: {request.method}")
        return jsonify({"error": "Invalid request method"}), 405