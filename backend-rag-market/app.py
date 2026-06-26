import requests
import urllib3

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Monkeypatch requests to disable SSL verification globally
original_request = requests.Session.request
requests.Session.request = lambda self, method, url, **kwargs: original_request(self, method, url, **dict(kwargs, verify=False))

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.utils import secure_filename
from rag_service import RAGService
from config import Config
import database

app = Flask(__name__)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

# Initialize JWT
jwt = JWTManager(app)

# Enable CORS for Angular frontend (running on port 4203 or default 4200)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:4203", "http://localhost:4200"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize database
database.init_database()

# Initialize RAG service
rag_service = RAGService()

# Register blueprints
from auth import auth_bp
from admin_routes import admin_bp
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

ALLOWED_EXTENSIONS = {'pdf', 'csv', 'json', 'xml'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/market/news', methods=['GET'])
def load_market_news():
    """Seed / load general market news into FAISS vector store"""
    try:
        result = rag_service.load_market_news()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/market/upload', methods=['POST'])
def upload_portfolio():
    """Upload a portfolio file (PDF, CSV, JSON, XML) and cleanse it with LLM"""
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
            
        if not allowed_file(file.filename):
            return jsonify({"success": False, "error": "Supported formats: PDF, CSV, JSON, XML"}), 400
            
        filename = secure_filename(file.filename)
        file_content = file.read()
        
        print(f"Received portfolio file: {filename}, size: {len(file_content)} bytes")
        
        # 1. Parse document to text
        raw_text = rag_service.parse_portfolio_document(file_content, filename)
        
        # 2. Extract structured holdings using LLM
        holdings = rag_service.cleanse_holdings(raw_text)
        
        return jsonify({
            "success": True,
            "filename": filename,
            "holdings": holdings
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/market/analyze', methods=['POST'])
def analyze_portfolio():
    """Enrich holdings with Finnhub live quotes, news sentiment, and generate risk summary"""
    try:
        data = request.json or {}
        holdings = data.get("holdings", [])
        
        if not holdings:
            return jsonify({"success": False, "error": "No holdings provided for analysis"}), 400
            
        # 1. Enrich each holding with Finnhub data
        enriched_holdings = []
        for h in holdings:
            symbol = h.get("symbol", "").upper().strip()
            shares = float(h.get("shares", 0))
            purchase_price = float(h.get("purchasePrice", 0))
            
            market_data = rag_service.get_market_data(symbol)
            quote = market_data["quote"]
            sentiment = market_data["sentiment"]
            news = market_data["news"]
            
            current_price = quote["c"]
            cost_basis = shares * purchase_price
            current_value = shares * current_price
            daily_change = quote["d"] * shares
            daily_change_percent = quote["dp"]
            
            enriched_holdings.append({
                "symbol": symbol,
                "name": h.get("name", symbol),
                "shares": shares,
                "purchasePrice": purchase_price,
                "costBasis": cost_basis,
                "currentPrice": current_price,
                "currentValue": current_value,
                "dailyChange": daily_change,
                "dailyChangePercent": daily_change_percent,
                "sentiment": sentiment["sentiment"],
                "sentimentScore": sentiment["companyNewsScore"],
                "news": news
            })
            
        # 2. Calculate portfolio-wide statistics
        total_cost_basis = sum(h["costBasis"] for h in enriched_holdings)
        total_current_value = sum(h["currentValue"] for h in enriched_holdings)
        total_gain_loss = total_current_value - total_cost_basis
        total_gain_loss_percent = (total_gain_loss / total_cost_basis * 100.0) if total_cost_basis > 0 else 0
        
        # Portfolio daily change is computed based on yesterday's value
        total_daily_change = sum(h["dailyChange"] for h in enriched_holdings)
        previous_day_value = total_current_value - total_daily_change
        total_daily_change_percent = (total_daily_change / previous_day_value * 100.0) if previous_day_value > 0 else 0
        
        total_stats = {
            "costBasis": total_cost_basis,
            "currentValue": total_current_value,
            "gainLoss": total_gain_loss,
            "gainLossPercent": total_gain_loss_percent,
            "dailyChange": total_daily_change,
            "dailyChangePercent": total_daily_change_percent
        }
        
        # 3. Generate Risk Summary Report (combines holdings + RAG context)
        risk_report = rag_service.generate_risk_report(enriched_holdings, total_stats)
        
        return jsonify({
            "success": True,
            "enrichedHoldings": enriched_holdings,
            "totalStats": total_stats,
            "riskReport": risk_report
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/market/chat', methods=['POST'])
def chat():
    """Interactive RAG chat + optional Image OCR/Vision"""
    try:
        data = request.json or {}
        message = data.get("message", "")
        history = data.get("history", [])
        image_base64 = data.get("image", None)
        holdings = data.get("holdings", None)
        
        if not message and not image_base64:
            return jsonify({"success": False, "error": "Query message or image is required"}), 400
            
        response = rag_service.chat_response(message, history, image_base64, holdings)
        
        return jsonify({
            "success": True,
            "response": response
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/market/documents', methods=['GET'])
def get_documents():
    """Retrieve vector database news documents status"""
    try:
        result = rag_service.get_documents()
        return jsonify({"success": True, "documents": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/market/documents/clear', methods=['DELETE'])
def clear_documents():
    """Clear indexed market news vector database"""
    try:
        success = rag_service.clear_documents()
        return jsonify({
            "success": success,
            "message": "Market news vector store cleared successfully" if success else "Failed to clear vector store"
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print(f"Starting Capital Markets Backend on port {Config.FLASK_PORT}...")
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.DEBUG)
