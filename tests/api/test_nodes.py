"""
Tests for the node management API endpoints.
Covers register_node.py and update_node.py
"""
import json
import pytest
import uuid


class TestNodes:
    """Test class for node management API endpoints."""
    
    def test_register_node(self, client, authenticated_client):
        """Test registering a new node."""
        client, token = authenticated_client
        
        # Generate unique node identifier
        node_id = str(uuid.uuid4())
        
        # Create test data for node registration
        test_data = {
            "node_name": f"_TEST_Node_{node_id[:8]}",
            "node_type": "endpoint",
            "ip_address": "192.168.1.100",
            "port": 5060,
            "capabilities": ["voice", "sms"]
        }
        
        response = client.post(
            '/api/v1/register_node',
            data=json.dumps(test_data),
            content_type='application/json',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = json.loads(response.data)
        assert response.status_code == 201
        assert "message" in data
        assert "node_id" in data
        
        # Store the node_id for use in update test
        return data["node_id"]
    
    def test_register_node_invalid_data(self, client, authenticated_client):
        """Test node registration with invalid data."""
        client, token = authenticated_client
        
        test_cases = [
            # Missing required fields
            ({"node_name": "_TEST_Node"}, "Missing required fields"),
            ({"ip_address": "192.168.1.100"}, "Missing required fields"),
            # Invalid data types
            ({"node_name": "_TEST_Node", "node_type": "endpoint", 
              "ip_address": "not_an_ip", "port": 5060}, "Invalid IP address format"),
            ({"node_name": "_TEST_Node", "node_type": "endpoint", 
              "ip_address": "192.168.1.100", "port": "not_a_port"}, "Invalid port format")
        ]
        
        for test_data, expected_error in test_cases:
            response = client.post(
                '/api/v1/register_node',
                data=json.dumps(test_data),
                content_type='application/json',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            data = json.loads(response.data)
            assert response.status_code == 400
            assert "error" in data
            assert expected_error in data["error"] or data["error"].startswith(expected_error)
    
    def test_update_node(self, client, authenticated_client):
        """Test updating an existing node."""
        client, token = authenticated_client
        
        # First create a node to update
        node_id = self.test_register_node(client, authenticated_client)
        
        # Data for updating node
        update_data = {
            "node_id": node_id,
            "node_name": "_TEST_Updated_Node",
            "port": 5061,
            "capabilities": ["voice", "sms", "video"]
        }
        
        response = client.post(
            '/api/v1/update_node',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = json.loads(response.data)
        assert response.status_code == 200
        assert "message" in data
        assert "Node updated successfully" in data["message"]
    
    def test_update_nonexistent_node(self, client, authenticated_client):
        """Test updating a node that doesn't exist."""
        client, token = authenticated_client
        
        update_data = {
            "node_id": 9999,  # Non-existent node ID
            "node_name": "_TEST_Updated_Node"
        }
        
        response = client.post(
            '/api/v1/update_node',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = json.loads(response.data)
        assert response.status_code == 404
        assert "error" in data
        assert "Node not found" in data["error"]
    
    def test_unauthorized_access(self, client):
        """Test accessing endpoints without authentication."""
        endpoints = ["/api/v1/register_node", "/api/v1/update_node"]
        
        test_data = {"node_name": "_TEST_Node"}
        
        for endpoint in endpoints:
            response = client.post(
                endpoint,
                data=json.dumps(test_data),
                content_type='application/json'
            )
            
            assert response.status_code == 401