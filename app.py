"""
Flask Web Application for Faculty Search Engine
Main application file with API endpoints
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os

# Import our enhanced search engine
from search_engine_improved import EnhancedFacultySearchEngine

app = Flask(__name__)
CORS(app)  # Enable CORS for API access

# Global search engine instance
search_engine = None

def initialize_search_engine():
    """Initialize the search engine on startup"""
    global search_engine
    try:
        print("Initializing search engine...")
        search_engine = EnhancedFacultySearchEngine('faculty_data.csv')
        search_engine.initialize(use_multi_field=True)
        print("✓ Search engine initialized successfully!")
        return True
    except Exception as e:
        print(f"✗ Error initializing search engine: {e}")
        return False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/search')
def search_page():
    """Search interface page"""
    return render_template('search.html')

@app.route('/about')
def about():
    """About page"""
    stats = search_engine.get_statistics() if search_engine else {}
    return render_template('about.html', stats=stats)

@app.route('/api/search', methods=['POST'])
def api_search():
    """
    API endpoint for searching faculty
    
    Request JSON:
    {
        "query": "machine learning",
        "top_k": 5,
        "use_hybrid": true
    }
    
    Response JSON:
    {
        "success": true,
        "query": "machine learning",
        "results": [...],
        "count": 5,
        "search_time": 0.123
    }
    """
    try:
        if not search_engine:
            return jsonify({
                'success': False,
                'error': 'Search engine not initialized'
            }), 500
        
        # Get request data
        data = request.get_json()
        query = data.get('query', '').strip()
        top_k = data.get('top_k', 10)
        use_hybrid = data.get('use_hybrid', True)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        # Perform search
        import time
        start_time = time.time()
        results = search_engine.search(query, top_k=top_k, use_hybrid=use_hybrid)
        search_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results),
            'search_time': round(search_time, 3)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """
    API endpoint for getting search engine statistics
    
    Response JSON:
    {
        "success": true,
        "stats": {...}
    }
    """
    try:
        if not search_engine:
            return jsonify({
                'success': False,
                'error': 'Search engine not initialized'
            }), 500
        
        stats = search_engine.get_statistics()
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/faculty/<int:faculty_id>', methods=['GET'])
def api_faculty_details(faculty_id):
    """
    API endpoint for getting detailed faculty information
    """
    try:
        if not search_engine:
            return jsonify({
                'success': False,
                'error': 'Search engine not initialized'
            }), 500
        
        if faculty_id < 0 or faculty_id >= len(search_engine.faculty_data):
            return jsonify({
                'success': False,
                'error': 'Faculty ID not found'
            }), 404
        
        faculty = search_engine.faculty_data.iloc[faculty_id]
        
        return jsonify({
            'success': True,
            'faculty': {
                'name': faculty['name'],
                'specialization': faculty['areaSpecialization'],
                'biography': faculty['biography'],
                'publications': faculty['publications'],
                'education': faculty['facultyEducation'],
                'email': faculty.get('email', ''),
                'number': faculty.get('number', ''),
                'address': faculty.get('address', '')
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/compare', methods=['POST'])
def api_compare():
    """
    API endpoint for comparing semantic-only vs hybrid search
    
    Request JSON:
    {
        "query": "machine learning",
        "top_k": 5
    }
    """
    try:
        if not search_engine:
            return jsonify({
                'success': False,
                'error': 'Search engine not initialized'
            }), 500
        
        data = request.get_json()
        query = data.get('query', '').strip()
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        # Semantic only
        semantic_results = search_engine.search(query, top_k=top_k, use_hybrid=False)
        
        # Hybrid
        hybrid_results = search_engine.search(query, top_k=top_k, use_hybrid=True)
        
        return jsonify({
            'success': True,
            'query': query,
            'semantic_results': semantic_results,
            'hybrid_results': hybrid_results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Initialize search engine before starting server
    if initialize_search_engine():
        print("\n" + "="*80)
        print("🚀 Faculty Search Engine Web App")
        print("="*80)
        print("Server starting at: http://localhost:8081")
        print("API documentation: http://localhost:8081/api/docs")
        print("\nAvailable endpoints:")
        print("  GET  /              - Main page")
        print("  GET  /search        - Search interface")
        print("  GET  /about         - About page")
        print("  POST /api/search    - Search API")
        print("  GET  /api/stats     - Statistics API")
        print("  POST /api/compare   - Compare search methods")
        print("="*80 + "\n")
        
        # Run the Flask app
        app.run(debug=True, host='0.0.0.0', port=8081)
    else:
        print("Failed to initialize search engine. Please check your faculty_data.csv file.")
        sys.exit(1)
