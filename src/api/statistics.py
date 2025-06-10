from flask import Request, jsonify
from util.sqlExecutor import SQLExecutor
from util.logging import log

def handler(request: Request):
    logger = log()
    logger.info(f"Statistics API called, w/ method: {request.method}")
    
    # Initialize response data with default values
    response_data = {
        "users": {
            "registered": 0,
            "active": 0,
            "inactive": 0
        },
        "nodes": {
            "total": 0,
            "online": 0,
            "mainnet": {
                "total": 0,
                "online": 0,
                "offline": 0
            },
            "testnet": {
                "total": 0,
                "online": 0,
                "offline": 0
            }
        },
        "relays": {
            "total": 0, # estimation based on active nodes
            "active": 0
        }
    }

    if request.method == "GET":
        try:
            # Get user statistics
            user_stats_executor = SQLExecutor("get_user_stats", param_validation=False)
            user_stats = user_stats_executor.fetch_one()
            
            if user_stats:
                response_data["users"]["registered"] = user_stats[0] or 0  # total_users
                response_data["users"]["active"] = user_stats[1] or 0     # active_users
                response_data["users"]["inactive"] = user_stats[2] or 0   # inactive_users
            
            # Get node statistics
            node_stats_executor = SQLExecutor("get_node_stats", param_validation=False)
            node_stats = node_stats_executor.fetch_all()
            
            other_nodes = 0
            if node_stats:
                for row in node_stats:
                    node_type = row[0].lower() if row[0] else ""
                    total_nodes = row[1] or 0
                    online_nodes = row[2] or 0
                    offline_nodes = row[3] or 0
                    
                    if node_type == "mainnet":
                        response_data["nodes"]["mainnet"]["total"] = total_nodes
                        response_data["nodes"]["mainnet"]["online"] = online_nodes
                        response_data["nodes"]["mainnet"]["offline"] = offline_nodes
                    elif node_type == "testnet":
                        response_data["nodes"]["testnet"]["total"] = total_nodes
                        response_data["nodes"]["testnet"]["online"] = online_nodes
                        response_data["nodes"]["testnet"]["offline"] = offline_nodes
                    else:
                        other_nodes += 1
            
            # Calculate relay statistics (estimation based on active nodes)
            total_active_nodes = (response_data["nodes"]["mainnet"]["online"] + 
                                response_data["nodes"]["testnet"]["online"])
            response_data["nodes"]["total"] = (response_data["nodes"]["mainnet"]["total"] + 
                                                response_data["nodes"]["testnet"]["total"]) + other_nodes
            response_data["nodes"]["online"] = total_active_nodes
            #response_data["relays"]["active"] = total_active_nodes
            #response_data["relays"]["total"] = total_active_nodes  # Simple estimation
            
            logger.info("Statistics retrieved successfully")
            return jsonify(response_data), 200
        except Exception as e:
            logger.error(f"Error retrieving statistics: {e}")
            return jsonify({"error": str(e)}), 500
    else:
        logger.warning(f"Invalid request method for statistics: {request.method}")
        return jsonify({"error": "Invalid request method"}), 405