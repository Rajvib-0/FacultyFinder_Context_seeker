from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os
import traceback

app = Flask(__name__)
CORS(app)
 
def get_search_engine():
    try:
        # Import here to avoid loading unless needed
        from search_engine_improved import EnhancedFacultySearchEngine
        
        data_file = 'faculty_data.csv'
        if not os.path.exists(data_file):
            print(f"Data file not found: {data_file}")
            return None
        
        # Create new instance each time or cache it
        if not hasattr(get_search_engine, 'cached_engine'):
            print("Initializing search engine (lazy load)...")
            search_engine = EnhancedFacultySearchEngine(data_file)
            search_engine.initialize(force_rebuild=False, use_multi_field=True)
            get_search_engine.cached_engine = search_engine
            print("Search engine initialized!")
        
        return get_search_engine.cached_engine
        
    except Exception as e:
        print(f"Error loading search engine: {e}")
        traceback.print_exc()
        return None

# Initialize cache attribute
get_search_engine.cached_engine = None

print("\n" + "="*80)
print("Faculty Finder Application Starting")
print("Search engine will load on first request")
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
    search_engine = get_search_engine()
    stats = search_engine.get_statistics() if search_engine else {}
    return render_template('about.html', stats=stats)

@app.route('/health')
def health():
    """Health check endpoint"""
    search_engine = get_search_engine()
    return jsonify({
        'status': 'ok',
        'search_engine_ready': search_engine is not None
    })

# ==================== API ENDPOINTS ====================

@app.route('/api/search', methods=['POST'])
def api_search():
    """
    API endpoint for searching faculty
    """
    try:
        search_engine = get_search_engine()  # Load here
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

# ==================== MAIN ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8081))
    print(f"\nDevelopment Server Starting on http://localhost:{port}")
    print("="*80 + "\n")
    app.run(debug=True, host='0.0.0.0', port=port)
