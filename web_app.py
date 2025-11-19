#!/usr/bin/env python3
"""
AI Brand Studio - Flask Web Chat Interface

A beautiful, lightweight web interface for brand identity creation.
"""

from flask import Flask, render_template, request, jsonify, session
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import secrets
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
load_dotenv()

from google.adk.runners import InMemoryRunner
from src.agents.orchestrator import create_orchestrator
from src.infrastructure.logging import get_logger

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Global orchestrator (initialized on first use)
orchestrator = None
runner = None

def get_runner():
    """Get or create the ADK runner."""
    global orchestrator, runner
    if orchestrator is None:
        orchestrator = create_orchestrator()
        runner = InMemoryRunner(agent=orchestrator)
    return runner

@app.route('/')
def index():
    """Render the main chat interface."""
    # Initialize session
    if 'messages' not in session:
        session['messages'] = []
        session['stats'] = {'brands_created': 0, 'messages': 0}

    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        data = request.json
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        # Get messages from session
        if 'messages' not in session:
            session['messages'] = []

        # Add user message
        session['messages'].append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })

        # Process with orchestrator
        runner = get_runner()
        result = runner.run(user_message)

        # Extract response
        if hasattr(result, 'text'):
            response = result.text
        elif isinstance(result, dict):
            response = str(result)
        else:
            response = str(result)

        # Add assistant message
        session['messages'].append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat()
        })

        # Update stats
        if 'stats' not in session:
            session['stats'] = {'brands_created': 0, 'messages': 0}
        session['stats']['brands_created'] += 1
        session['stats']['messages'] = len(session['messages'])

        session.modified = True

        return jsonify({
            'success': True,
            'response': response,
            'stats': session['stats']
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history')
def get_history():
    """Get chat history."""
    return jsonify({
        'messages': session.get('messages', []),
        'stats': session.get('stats', {'brands_created': 0, 'messages': 0})
    })

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear chat history."""
    session['messages'] = []
    session['stats'] = {'brands_created': 0, 'messages': 0}
    session.modified = True

    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║          AI BRAND STUDIO - WEB INTERFACE                  ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  🌐 URL: http://localhost:{port}                             ║
    ║  🎨 Multi-Agent Brand Creation System                     ║
    ║  🚀 Powered by Google ADK & Gemini 2.0                    ║
    ╚═══════════════════════════════════════════════════════════╝

    Press Ctrl+C to stop the server
    """)

    app.run(host='0.0.0.0', port=port, debug=debug)
