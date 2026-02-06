

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os
from typing import List, Dict, Tuple
import re
from collections import Counter


class EnhancedFacultySearchEngine:
    """Enhanced semantic search engine with improved scoring and context awareness"""
    
    def __init__(self, data_path: str = 'faculty_data.csv', model_name: str = 'all-MiniLM-L6-v2'):
      
        self.data_path = data_path
        self.model_name = model_name
        self.model = None
        self.index = None
        self.faculty_data = None
        self.embeddings = None
        
        # Field weights for different components
        self.field_weights = {
            'specialization': 3.0,  
            'publications': 2.0,     
            'biography': 2.0,        
            'education': 1.5,        
            'name': 0.5           
        }
        
        # Separate embeddings for each field
        self.field_embeddings = {}
        
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if pd.isna(text) or text in ['', 'not provided', 'Not Provided', 'N/A', 'NA']:
            return ''
        return str(text).strip()
    
    def _is_meaningful_content(self, text: str) -> bool:
        """Check if text contains meaningful content (not just 'not provided')"""
        cleaned = self._clean_text(text).lower()
        if not cleaned:
            return False
        # Check for common placeholder values
        placeholders = ['not provided', 'n/a', 'na', 'none', 'nil', '-']
        return cleaned not in placeholders and len(cleaned) > 5
    
    def load_and_process_data(self) -> pd.DataFrame:
       
        print(f"Loading data from {self.data_path}...")
        df = pd.read_csv(self.data_path)
        
        # Clean all text fields
        text_columns = ['name', 'areaSpecialization', 'biography', 'publications', 'facultyEducation']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._clean_text)
        
        # Create enhanced text representations for each field
        df['name_text'] = df['name'].apply(lambda x: f"Professor {x}" if x else "")
        
        df['specialization_text'] = df['areaSpecialization'].apply(
            lambda x: f"Expert in {x}. Research focus: {x}. Specialization: {x}" if x else ""
        )
        
        df['biography_text'] = df['biography'].apply(
            lambda x: f"Background and experience: {x}" if self._is_meaningful_content(x) else ""
        )
        
        df['publications_text'] = df['publications'].apply(
            lambda x: f"Research publications and contributions: {x}" if self._is_meaningful_content(x) else ""
        )
        
        df['education_text'] = df['facultyEducation'].apply(
            lambda x: f"Academic credentials: {x}" if self._is_meaningful_content(x) else ""
        )
        
        # Create weighted combined text (for fallback single embedding)
        df['combined_text'] = df.apply(lambda row: self._create_weighted_text(row), axis=1)
        
        self.faculty_data = df
        print(f"Loaded {len(df)} faculty members")
        
        # Print data quality statistics
        print("\n=== Data Quality Statistics ===")
        for col in ['areaSpecialization', 'biography', 'publications', 'facultyEducation']:
            if col in df.columns:
                meaningful_count = df[col].apply(self._is_meaningful_content).sum()
                print(f"{col}: {meaningful_count}/{len(df)} ({meaningful_count/len(df)*100:.1f}%) have meaningful content")
        
        return df
    
    def _create_weighted_text(self, row) -> str:
        """Create a weighted combined text that emphasizes important fields"""
        parts = []
        
        # Repeat important fields to give them more weight in the embedding
        if row['specialization_text']:
            # Repeat specialization 3 times for emphasis
            parts.extend([row['specialization_text']] * 3)
        
        if row['publications_text']:
            # Repeat publications 2 times
            parts.extend([row['publications_text']] * 2)
        
        if row['biography_text']:
            parts.append(row['biography_text'])
        
        if row['education_text']:
            parts.append(row['education_text'])
        
        if row['name_text']:
            parts.append(row['name_text'])
        
        return " ".join(parts)
    
    def generate_embeddings(self, use_multi_field: bool = True) -> np.ndarray:
        
        print(f"Loading model: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)
        
        if use_multi_field:
            print("Generating multi-field embeddings...")
            
            # Generate embeddings for each field separately
            for field in ['name', 'specialization', 'biography', 'publications', 'education']:
                field_col = f'{field}_text'
                if field_col in self.faculty_data.columns:
                    texts = self.faculty_data[field_col].tolist()
                    # Only embed non-empty texts
                    embeddings = self.model.encode(texts, show_progress_bar=True, 
                                                  batch_size=32)
                    self.field_embeddings[field] = embeddings
                    print(f"  {field}: {embeddings.shape}")
            
            # Create weighted combined embedding
            print("Creating weighted combined embeddings...")
            combined_embeddings = np.zeros_like(self.field_embeddings['specialization'])
            
            total_weight = sum(self.field_weights.values())
            for field, weight in self.field_weights.items():
                if field in self.field_embeddings:
                    combined_embeddings += (weight / total_weight) * self.field_embeddings[field]
            
            self.embeddings = combined_embeddings
        else:
            print("Generating single combined embeddings...")
            texts = self.faculty_data['combined_text'].tolist()
            self.embeddings = self.model.encode(texts, show_progress_bar=True, batch_size=32)
        
        print(f"Final embeddings shape: {self.embeddings.shape}")
        return self.embeddings
    
    def build_index(self):
        """Build FAISS index with L2 normalization for cosine similarity"""
        print("Building FAISS index...")
        
        # Normalize embeddings for cosine similarity
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1
        embeddings_normalized = self.embeddings / norms
        dimension = embeddings_normalized.shape[1]
        
        # Use IndexFlatIP for inner product (cosine similarity after normalization)
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings_normalized.astype('float32'))
        
        print(f"Index built with {self.index.ntotal} vectors")
    
    def _extract_keywords(self, text: str) -> set:
        """Extract meaningful keywords from text"""
        # Remove common words and extract meaningful terms
        text = text.lower()
        words = re.findall(r'\b[a-z]{3,}\b', text)
        
        # Common stop words to remove
        stop_words = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have', 'has',
                     'are', 'was', 'were', 'been', 'being', 'about', 'into', 'through',
                     'during', 'before', 'after', 'above', 'below', 'between', 'under',
                     'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
                     'why', 'how', 'all', 'both', 'each', 'few', 'more', 'most', 'other',
                     'some', 'such', 'only', 'own', 'same', 'than', 'too', 'very', 'can',
                     'will', 'just', 'should', 'now'}
        
        return set(w for w in words if w not in stop_words)
    
    def _keyword_match_score(self, query: str, faculty_row: pd.Series) -> float:
        """Calculate keyword matching score"""
        query_keywords = self._extract_keywords(query)
        
        if not query_keywords:
            return 0.0
        
        score = 0.0
        
        # Check each field with different weights
        field_keyword_weights = {
            'areaSpecialization': 3.0,
            'publications': 2.0,
            'biography': 2,
            'facultyEducation': 1.5,
            'name': 0.5
        }
        
        for field, weight in field_keyword_weights.items():
            if field in faculty_row.index:
                content = str(faculty_row[field]).lower()
                if self._is_meaningful_content(content):
                    content_keywords = self._extract_keywords(content)
                    matches = query_keywords.intersection(content_keywords)
                    if matches:
                        # Score based on percentage of query keywords matched
                        match_ratio = len(matches) / len(query_keywords)
                        score += weight * match_ratio
        
        return score
    
    def _expand_query(self, query: str) -> str:
        """Expand query with related terms for better matching"""
        # Add common academic synonyms and related terms
        expansions = {
            'ml': 'machine learning ',
            'ai': 'artificial intelligence',
            'nlp': 'natural language processing',
            'renewable energy': 'renewable energy sustainable energy clean energy solar wind',
            'wireless': 'wireless communication telecommunication',
            'quantum': 'quantum computing quantum mechanics quantum physics',
            'data': 'data science data analytics big data data mining',
            'cyber': 'cybersecurity security network security information security',
            'cloud': 'cloud computing distributed systems',
            'iot': 'internet of things iot embedded systems sensors',
            'blockchain': 'blockchain distributed ledger cryptocurrency',
        }
        
        query_lower = query.lower()
        expanded = query
        
        for term, expansion in expansions.items():
            if term in query_lower:
                expanded = f"{query} {expansion}"
                break
        
        return expanded
    
    def search(self, query: str, top_k: int = 5, use_hybrid: bool = True) -> List[Dict]:
        """
        Enhanced search with hybrid scoring
        
        Args:
            query: Natural language search query
            top_k: Number of results to return
            use_hybrid: If True, combine semantic and keyword matching
        """
        if self.model is None or self.index is None:
            raise ValueError("Search engine not initialized. Call initialize() first.")
        
        # Expand query for better matching
        expanded_query = self._expand_query(query)
        
        # Generate query embedding
        query_embedding = self.model.encode([expanded_query])
        query_normalized = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
        
        # Get more candidates for re-ranking
        search_k = min(top_k * 3, len(self.faculty_data))
        scores, indices = self.index.search(query_normalized.astype('float32'), search_k)
        
        # Prepare results with hybrid scoring
        results = []
        for idx, semantic_score in zip(indices[0], scores[0]):
            faculty = self.faculty_data.iloc[idx]
            
            # Calculate keyword matching score
            keyword_score = 0.0
            if use_hybrid:
                keyword_score = self._keyword_match_score(query, faculty)
            
            # Combine scores (70% semantic, 30% keyword)
            if use_hybrid and keyword_score > 0:
                final_score = 0.75 * float(semantic_score) + 0.25 * keyword_score
            else:
                final_score = float(semantic_score)
            
            # Field-specific boosting
            boost = 1.0
            query_lower = query.lower()
            spec_lower = str(faculty['areaSpecialization']).lower()
            
            # Exact phrase match in specialization gets high boost
            if query_lower in spec_lower or any(word in spec_lower for word in query_lower.split()):
                boost = 1.3
            
            final_score *= boost
            
            result = {
                'name': faculty['name'],
                'specialization': faculty['areaSpecialization'],
                'biography': faculty['biography'] if self._is_meaningful_content(faculty['biography']) else 'Not provided',
                'publications': faculty['publications'][:500] + '...' if len(str(faculty['publications'])) > 500 else faculty['publications'] if self._is_meaningful_content(faculty['publications']) else 'Not provided',
                'education': faculty['facultyEducation'] if self._is_meaningful_content(faculty['facultyEducation']) else 'Not provided',
                'email': faculty['email'],
                'number': faculty['number'] if 'number' in faculty.index else '',
                'address': faculty['address'] if 'address' in faculty.index else '',
                'final_score': final_score,
                'semantic_score': float(semantic_score),
                'keyword_score': keyword_score,
                'boost_applied': boost
            }
            results.append(result)
        
        # Sort by final score and take top_k
        results.sort(key=lambda x: x['final_score'], reverse=True)
        results = results[:top_k]
        
        # Add rank
        for i, result in enumerate(results):
            result['rank'] = i + 1
        
        return results
    
    def initialize(self, force_rebuild: bool = False, use_multi_field: bool = True):
        cache_file = f'enhanced_search_cache_{"multi" if use_multi_field else "single"}.pkl'
        
        if not force_rebuild and os.path.exists(cache_file):
            print("Loading from cache...")
            try:
                with open(cache_file, 'rb') as f:
                    cache = pickle.load(f)
                    self.faculty_data = cache['faculty_data']
                    self.embeddings = cache['embeddings']
                    self.field_embeddings = cache.get('field_embeddings', {})
                    self.model = SentenceTransformer(self.model_name)
                    
                    # Rebuild index
                    embeddings_normalized = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)
                    dimension = embeddings_normalized.shape[1]
                    self.index = faiss.IndexFlatIP(dimension)
                    self.index.add(embeddings_normalized.astype('float32'))
                    
                print("✓ Loaded from cache successfully!")
                return
            except Exception as e:
                print(f"Cache loading failed: {e}. Rebuilding...")
        
        # Build from scratch
        self.load_and_process_data()
        self.generate_embeddings(use_multi_field=use_multi_field)
        self.build_index()
        
        # Save to cache
        print("Saving to cache...")
        with open(cache_file, 'wb') as f:
            pickle.dump({
                'faculty_data': self.faculty_data,
                'embeddings': self.embeddings,
                'field_embeddings': self.field_embeddings
            }, f)
        print("Initialization complete!")
    
    def get_statistics(self) -> Dict:
        """Get detailed statistics"""
        stats = {
            'total_faculty': len(self.faculty_data) if self.faculty_data is not None else 0,
            'embedding_dimension': self.embeddings.shape[1] if self.embeddings is not None else 0,
            'model_name': self.model_name,
            'index_size': self.index.ntotal if self.index is not None else 0,
            'multi_field_embeddings': len(self.field_embeddings) > 0
        }
        
        if self.faculty_data is not None:
            for field in ['areaSpecialization', 'biography', 'publications', 'facultyEducation']:
                if field in self.faculty_data.columns:
                    meaningful = self.faculty_data[field].apply(self._is_meaningful_content).sum()
                    stats[f'{field}_coverage'] = f"{meaningful}/{len(self.faculty_data)} ({meaningful/len(self.faculty_data)*100:.1f}%)"
        
        return stats
    
    def compare_search_methods(self, query: str, top_k: int = 5):
        """Compare semantic-only vs hybrid search"""
        print(f"\n{'='*80}")
        print(f"COMPARING SEARCH METHODS")
        print(f"Query: '{query}'")
        print(f"{'='*80}")
        
        # Semantic only
        print("\n--- SEMANTIC ONLY ---")
        semantic_results = self.search(query, top_k, use_hybrid=False)
        for r in semantic_results:
            print(f"{r['rank']}. {r['name']} - Score: {r['semantic_score']:.3f}")
            print(f"   {r['specialization']}")
        
        # Hybrid
        print("\n--- HYBRID (Semantic + Keyword) ---")
        hybrid_results = self.search(query, top_k, use_hybrid=True)
        for r in hybrid_results:
            print(f"{r['rank']}. {r['name']} - Final: {r['final_score']:.3f} (Sem: {r['semantic_score']:.3f}, Kw: {r['keyword_score']:.3f}, Boost: {r['boost_applied']:.2f}x)")
            print(f"   {r['specialization']}")


# Example usage
if __name__ == "__main__":
    # Initialize enhanced search engine
    engine = EnhancedFacultySearchEngine('faculty_data.csv')
    engine.initialize(use_multi_field=True)
    
    # Test queries
    test_queries = [
        "sustainable energy and carbon capture",
        "machine learning and AI",
        "wireless communication networks",
        "migration and diaspora studies",
        "quantum computing research",
        "renewable energy systems",
        "natural language processing",
        "cybersecurity"
    ]
    
    print("\n" + "="*80)
    print("TESTING ENHANCED SEMANTIC SEARCH ENGINE")
    print("="*80)
    
    # Test first query with comparison
    if test_queries:
        engine.compare_search_methods(test_queries[0], top_k=5)
    
    # Test remaining queries with hybrid search
    for query in test_queries[1:]:
        print(f"\n{'='*80}")
        print(f"Query: '{query}'")
        print("-" * 80)
        
        results = engine.search(query, top_k=5, use_hybrid=True)
        
        for result in results:
            print(f"\n{result['rank']}. {result['name']}")
            print(f"   Score: {result['final_score']:.3f} (Semantic: {result['semantic_score']:.3f}, Keyword: {result['keyword_score']:.3f})")
            print(f"   Specialization: {result['specialization']}")
            print(f"   Biography: {result['biography'][:150]}..." if len(result['biography']) > 150 else f"   Biography: {result['biography']}")
    
    # Print statistics
    print("\n" + "="*80)
    print("SEARCH ENGINE STATISTICS")
    print("="*80)
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

