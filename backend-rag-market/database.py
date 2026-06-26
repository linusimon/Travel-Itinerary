"""
Database models and initialization for Capital Markets Risk Summarizer
"""
import sqlite3
import bcrypt
import os
from datetime import datetime
from typing import List, Dict, Optional

DATABASE_PATH = "capital_markets.db"

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with required tables and default admin user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create ExpertAnalysis table (key-value store with repeatable keys)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expert_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL,
            data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create index on key for faster lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_expert_key ON expert_analysis(key)
    ''')
    
    conn.commit()
    
    # Check if admin user exists, if not create it
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    admin = cursor.fetchone()
    
    if not admin:
        # Create default admin user (password: admin123)
        password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin", password_hash, "admin")
        )
        conn.commit()
        print("[DATABASE] Created default admin user (username: admin, password: admin123)")
    
    # Seed expert analysis data if table is empty
    cursor.execute("SELECT COUNT(*) as count FROM expert_analysis")
    count = cursor.fetchone()['count']
    
    if count == 0:
        seed_expert_analysis(cursor)
        conn.commit()
        print("[DATABASE] Seeded expert analysis data")
    
    conn.close()
    print("[DATABASE] Database initialized successfully")

def seed_expert_analysis(cursor):
    """Seed the database with sample expert analysis for popular tickers"""
    expert_data = [
        # Apple Inc.
        ("AAPL", "Apple demonstrates strong fundamentals with consistent revenue growth driven by iPhone sales and services expansion. The company's ecosystem lock-in provides durable competitive advantages. However, valuation remains elevated at ~30x P/E ratio. Recent headwinds include China regulatory concerns and slowing hardware growth."),
        ("AAPL", "Technical Analysis: AAPL is trading above its 200-day moving average, showing bullish momentum. Support level at $170, resistance at $195. RSI indicates neutral territory at 55. Long-term trend remains positive."),
        ("AAPL", "Risk Assessment: Key risks include antitrust scrutiny in EU/US, supply chain dependencies on China, and potential iPhone market saturation. Services segment growth at 15% YoY provides diversification."),
        
        # Microsoft Corporation
        ("MSFT", "Microsoft's cloud business (Azure) continues to outperform with 30%+ growth, driven by AI integration and enterprise adoption. GitHub Copilot and OpenAI partnership position the company well for the AI revolution. Office 365 subscriptions provide stable recurring revenue. Gaming segment shows promise post-Activision acquisition."),
        ("MSFT", "Valuation appears reasonable at 28x forward P/E given growth trajectory. Free cash flow generation of $70B+ annually supports dividend growth and buybacks. Maintain overweight rating with $450 price target."),
        
        # NVIDIA Corporation  
        ("NVDA", "NVIDIA dominates the AI chip market with 80%+ market share in data center GPUs. Blackwell architecture delays present near-term headwinds, but demand remains robust from hyperscalers (Google, Microsoft, Meta, Amazon). Gaming segment stabilizing after crypto downturn."),
        ("NVDA", "Extreme valuation at 60x P/E requires continued hypergrowth to justify. Competition from AMD, Intel, and custom chips (Google TPU, Amazon Trainium) poses long-term risks. Options market shows elevated volatility premiums."),
        ("NVDA", "Earnings Catalyst: Next earnings call expected to guide on Blackwell production ramp and H200 adoption. Consensus estimates: $32B revenue (+110% YoY), EPS $0.65."),
        
        # Tesla Inc.
        ("TSLA", "Tesla faces increasing competition from legacy automakers and Chinese EV manufacturers (BYD, NIO). Gross margins compressing due to price cuts. FSD (Full Self-Driving) remains years away from regulatory approval. Cybertruck production ramp slower than expected."),
        ("TSLA", "Bull case hinges on energy storage business (Megapack) and robotaxi potential. Current valuation implies 50%+ annual growth for next 5 years, which appears aggressive. Downgrade to neutral with $180 target."),
        
        # Amazon.com Inc.
        ("AMZN", "Amazon Web Services (AWS) remains the cash cow with 30% operating margins. Retail segment shows improving profitability post-cost optimization. Advertising business growing 20%+ as third pillar. Logistics network provides competitive moat."),
        ("AMZN", "Concerns: Regulatory pressure on marketplace practices, unionization efforts affecting labor costs, and AWS growth deceleration to mid-teens. Fair value range: $160-$180 based on sum-of-parts analysis."),
        
        # Alphabet Inc.
        ("GOOGL", "Google Search remains dominant with 90%+ market share, generating massive cash flows. YouTube advertising accelerating with Shorts monetization. Cloud (GCP) growing but still #3 behind AWS and Azure. Waymo represents long-term optionality."),
        ("GOOGL", "AI threat from ChatGPT/Microsoft overstated - Google has leading AI research (DeepMind, Brain). Recent Gemini launch shows competitive positioning. Attractive valuation at 20x P/E with $70B+ buyback program. Strong buy recommendation."),
        
        # Meta Platforms
        ("META", "Meta's 'Year of Efficiency' driving margin expansion from 25% to 35%+. Reality Labs losses narrowing, though metaverse vision remains unclear. Instagram Reels monetization improving, competing effectively with TikTok. WhatsApp business messaging represents untapped revenue opportunity."),
        ("META", "Advertising recovery in 2026 supports 15% revenue growth. Valuation compelling at 22x P/E. Key risks: EU privacy regulations, teen engagement decline, Apple iOS restrictions on tracking."),
        
        # JPMorgan Chase
        ("JPM", "Strongest US bank with diversified revenue streams: investment banking, asset management, consumer banking. Net interest income benefiting from higher rates. Credit quality remains solid with <1% net charge-off rate. Fortress balance sheet with CET1 ratio of 15%."),
        ("JPM", "Concerns about NII headwinds if Fed cuts rates in 2027. Trading revenue volatility. Target price $180, reflecting 1.6x book value multiple."),
        
        # Visa Inc.
        ("V", "Global payment network with 60%+ operating margins. Digital payment adoption accelerating post-pandemic. Cross-border transaction volumes recovering to pre-COVID levels. Limited credit risk as payment processor, not lender."),
        ("V", "Growth drivers: emerging market penetration, B2B payment digitization, buy-now-pay-later partnerships. Risks: regulatory caps on interchange fees, competitive pressure from Mastercard and digital wallets. Maintain outperform rating."),
        
        # Johnson & Johnson
        ("JNJ", "Defensive healthcare conglomerate with pharma, medtech, and consumer health segments. Recent Kenvue spin-off clarifies pure-play pharma/medtech focus. Strong drug pipeline including cancer and immunology treatments. Dividend aristocrat with 60+ years of increases."),
        ("JNJ", "Talc litigation overhang pressuring valuation. Keytruda biosimilar competition emerging 2028+. Fair value $170-$175 based on DCF. Suitable for conservative portfolios seeking stability."),
    ]
    
    for key, data in expert_data:
        cursor.execute(
            "INSERT INTO expert_analysis (key, data) VALUES (?, ?)",
            (key, data)
        )

# User management functions
def verify_user(username: str, password: str) -> Optional[Dict]:
    """Verify user credentials and return user data if valid"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return {
            "id": user['id'],
            "username": user['username'],
            "role": user['role']
        }
    return None

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return dict(user)
    return None

# Expert Analysis functions
def add_expert_analysis(key: str, data: str) -> int:
    """Add a new expert analysis entry"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO expert_analysis (key, data) VALUES (?, ?)",
        (key, data)
    )
    conn.commit()
    analysis_id = cursor.lastrowid
    conn.close()
    
    return analysis_id

def get_expert_analysis_by_key(key: str) -> List[Dict]:
    """Get all expert analysis entries for a given key (ticker)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM expert_analysis WHERE UPPER(key) = UPPER(?) ORDER BY created_at DESC",
        (key,)
    )
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]

def get_all_expert_analysis(limit: int = 100, offset: int = 0) -> List[Dict]:
    """Get all expert analysis entries with pagination"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM expert_analysis ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset)
    )
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]

def get_expert_analysis_count() -> int:
    """Get total count of expert analysis entries"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM expert_analysis")
    count = cursor.fetchone()['count']
    conn.close()
    
    return count

def delete_expert_analysis(analysis_id: int) -> bool:
    """Delete an expert analysis entry"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM expert_analysis WHERE id = ?", (analysis_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    
    return deleted

def update_expert_analysis(analysis_id: int, data: str) -> bool:
    """Update an expert analysis entry"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE expert_analysis SET data = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (data, analysis_id)
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    
    return updated

# Initialize database on module import
if __name__ == "__main__":
    init_database()
