from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from search_engine_improved import EnhancedFacultySearchEngine
import sys
import os
import traceback

app = Flask(__name__)
CORS(app)

search_engine = None

def initialize_search_engine():
    """Initialize the enhanced search engine"""
    global search_engine
    try:
        print("="*80)
        print("Initializing Enhanced Faculty Search Engine...")
        print("="*80)
        
        # Check if data file exists
        data_file = 'faculty_data.csv'
        if not os.path.exists(data_file):
            print(f"Error: {data_file} not found!")
            print(f"Current directory: {os.getcwd()}")
            print(f"Files in directory: {os.listdir('.')}")
            return False
        
        print(f"Found data file: {data_file}")
        
        # Initialize search engine
        search_engine = EnhancedFacultySearchEngine(data_file)
        search_engine.initialize(force_rebuild=False, use_multi_field=True)
        
        print("Search engine initialized successfully!")
        return True
        
    except Exception as e:
        print(f"Error initializing search engine: {e}")
        traceback.print_exc()
        return False

# Initialize on module load (for Gunicorn workers)
print("\n" + "="*80)
print("Starting Faculty Finder Application")
print("="*80)
initialization_success = initialize_search_engine()
if not initialization_success:
    print("WARNING: Search engine failed to initialize!")
    print("App will start but search functionality will not work")
print("="*80 + "\n")

# ==================== ROUTES ====================

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

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'ok',
        'search_engine_ready': search_engine is not None
    })

# ==================== API ENDPOINTS ====================

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
    """
    try:
        if not search_engine:
            return jsonify({
                'success': False,
                'error': 'Search engine not initialized. Please contact administrator.'
            }), 500
        
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
        print(f"Search error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Get search engine statistics"""
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
    """Get detailed faculty information by ID"""
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

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('500.html'), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    # This only runs in development (not with Gunicorn)
    port = int(os.environ.get('PORT', 8081))
    print(f"\nDevelopment Server Starting on http://localhost:{port}")
    print("Available endpoints:")
    print("  GET  /              - Main page")
    print("  GET  /search        - Search interface")
    print("  GET  /about         - About page")
    print("  GET  /health        - Health check")
    print("  POST /api/search    - Search API")
    print("  GET  /api/stats     - Statistics API")
    print("="*80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=port)
