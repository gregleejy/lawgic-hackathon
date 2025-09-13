import json
import os
from main import process_legal_query

def lambda_handler(event, context):
    """AWS Lambda handler for lawgic legal analysis API"""
    
    # Enable CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    # Handle preflight CORS requests
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        query = body.get('query', '').strip()
        
        if not query:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Query parameter is required',
                    'message': 'Please provide a legal scenario to analyze'
                })
            }
        
        # Process the legal query using your existing function
        # Set save_output=False since Lambda doesn't persist files
        result = process_legal_query(query, save_output=False)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(result, ensure_ascii=False)
        }
        
    except Exception as e:
        print(f"Error processing legal query: {str(e)}")
        
        # Return detailed error for debugging
        error_response = {
            'error': 'Internal server error',
            'message': str(e),
            'query': body.get('query', '') if 'body' in locals() else ''
        }
        
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps(error_response)
        }