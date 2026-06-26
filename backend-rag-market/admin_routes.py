"""
Admin-only routes for document and expert analysis management
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from werkzeug.utils import secure_filename
from functools import wraps
import database
from datetime import datetime
import hashlib

admin_bp = Blueprint('admin', __name__)

def admin_required():
    """Decorator to require admin role"""
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != "admin":
                return jsonify({"success": False, "error": "Admin access required"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

# RAG Document Management Endpoints

@admin_bp.route('/api/admin/rag/upload', methods=['POST'])
@admin_required()
def upload_to_rag():
    """Upload a document to RAG vector store"""
    from rag_service import RAGService
    
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        # Get RAG service instance
        from app import rag_service
        
        filename = secure_filename(file.filename)
        file_content = file.read()
        
        # Add document to RAG with metadata
        result = rag_service.add_document_to_rag(
            file_content,
            filename,
            {
                "filename": filename,
                "upload_date": datetime.now().isoformat(),
                "uploaded_by": get_jwt_identity(),
                "file_type": filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown'
            }
        )
        
        return jsonify(result), 200 if result["success"] else 500
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/api/admin/rag/stats', methods=['GET'])
@admin_required()
def get_rag_stats():
    """Get RAG vector store statistics"""
    try:
        from app import rag_service
        
        stats = rag_service.get_rag_statistics()
        
        return jsonify({
            "success": True,
            "stats": stats
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/api/admin/rag/documents', methods=['GET'])
@admin_required()
def list_rag_documents():
    """List all documents in RAG vector store"""
    try:
        from app import rag_service
        
        documents = rag_service.list_documents()
        
        return jsonify({
            "success": True,
            "documents": documents
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/api/admin/rag/documents/<doc_id>', methods=['DELETE'])
@admin_required()
def delete_rag_document(doc_id):
    """Delete a document from RAG vector store"""
    try:
        from app import rag_service
        
        result = rag_service.delete_document(doc_id)
        
        return jsonify(result), 200 if result["success"] else 404
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/api/admin/rag/reload-news', methods=['POST'])
@admin_required()
def reload_market_news():
    """Reload market news into RAG"""
    try:
        from app import rag_service
        
        result = rag_service.load_market_news()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Expert Analysis Management Endpoints

@admin_bp.route('/api/admin/expert-analysis', methods=['GET'])
@admin_required()
def get_all_expert_analysis():
    """Get all expert analysis entries with pagination"""
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        analyses = database.get_all_expert_analysis(limit, offset)
        total = database.get_expert_analysis_count()
        
        return jsonify({
            "success": True,
            "analyses": analyses,
            "total": total,
            "limit": limit,
            "offset": offset
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/api/admin/expert-analysis', methods=['POST'])
@admin_required()
def add_expert_analysis_entry():
    """Add a new expert analysis entry"""
    try:
        data = request.json
        print("[DEBUG] Received POST /api/admin/expert-analysis")
        print(f"[DEBUG] Request data: {data}")
        print(f"[DEBUG] Request headers: {dict(request.headers)}")
        
        key = data.get('key', '').strip().upper()
        analysis_data = data.get('data', '').strip()
        
        print(f"[DEBUG] Extracted key: '{key}', data length: {len(analysis_data)}")
        
        if not key or not analysis_data:
            print("[DEBUG] Validation failed: missing key or data")
            return jsonify({"success": False, "error": "Key and data are required"}), 400
        
        analysis_id = database.add_expert_analysis(key, analysis_data)
        print(f"[DEBUG] Successfully added analysis with ID: {analysis_id}")
        
        return jsonify({
            "success": True,
            "message": "Expert analysis added successfully",
            "id": analysis_id
        }), 201
        
    except Exception as e:
        print(f"[DEBUG] Exception in add_expert_analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/api/admin/expert-analysis/<int:analysis_id>', methods=['PUT'])
@admin_required()
def update_expert_analysis_entry(analysis_id):
    """Update an expert analysis entry"""
    try:
        data = request.json
        analysis_data = data.get('data', '').strip()
        
        if not analysis_data:
            return jsonify({"success": False, "error": "Data is required"}), 400
        
        success = database.update_expert_analysis(analysis_id, analysis_data)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Expert analysis updated successfully"
            }), 200
        else:
            return jsonify({"success": False, "error": "Analysis not found"}), 404
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/api/admin/expert-analysis/<int:analysis_id>', methods=['DELETE'])
@admin_required()
def delete_expert_analysis_entry(analysis_id):
    """Delete an expert analysis entry"""
    try:
        success = database.delete_expert_analysis(analysis_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Expert analysis deleted successfully"
            }), 200
        else:
            return jsonify({"success": False, "error": "Analysis not found"}), 404
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/api/admin/expert-analysis/by-key/<key>', methods=['GET'])
@admin_required()
def get_expert_analysis_by_key(key):
    """Get expert analysis entries for a specific key (ticker)"""
    try:
        analyses = database.get_expert_analysis_by_key(key)
        
        return jsonify({
            "success": True,
            "key": key.upper(),
            "analyses": analyses,
            "count": len(analyses)
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
