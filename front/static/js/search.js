// Faculty Finder - Search Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const searchForm = document.getElementById('searchForm');
    const searchQuery = document.getElementById('searchQuery');
    const searchButton = document.getElementById('searchButton');
    const loading = document.getElementById('loading');
    const searchResults = document.getElementById('searchResults');
    const noResults = document.getElementById('noResults');
    const quickSearches = document.getElementById('quickSearches');
    const toggleOptions = document.getElementById('toggleOptions');
    const optionsPanel = document.getElementById('optionsPanel');
    const facultyModal = document.getElementById('facultyModal');
    const closeModal = document.querySelector('.close-modal');

    // Get query parameters from URL
    const urlParams = new URLSearchParams(window.location.search);
    const initialQuery = urlParams.get('q');

    // If there's a query in URL, search immediately
    if (initialQuery) {
        searchQuery.value = initialQuery;
        performSearch(initialQuery);
    }

    // Toggle advanced options
    toggleOptions.addEventListener('click', function() {
        if (optionsPanel.style.display === 'none') {
            optionsPanel.style.display = 'block';
        } else {
            optionsPanel.style.display = 'none';
        }
    });

    // Handle form submission
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = searchQuery.value.trim();
        if (query) {
            // Update URL with query
            const newUrl = window.location.pathname + '?q=' + encodeURIComponent(query);
            window.history.pushState({}, '', newUrl);
            
            performSearch(query);
        }
    });

    // Quick search tags
    document.querySelectorAll('.search-tag').forEach(tag => {
        tag.addEventListener('click', function() {
            const query = this.getAttribute('data-query');
            searchQuery.value = query;
            
            // Update URL
            const newUrl = window.location.pathname + '?q=' + encodeURIComponent(query);
            window.history.pushState({}, '', newUrl);
            
            performSearch(query);
        });
    });

    // Close modal
    closeModal.addEventListener('click', function() {
        facultyModal.style.display = 'none';
    });

    window.addEventListener('click', function(event) {
        if (event.target === facultyModal) {
            facultyModal.style.display = 'none';
        }
    });

    // Perform search function
    async function performSearch(query) {
        // Hide previous results and quick searches
        searchResults.innerHTML = '';
        noResults.style.display = 'none';
        quickSearches.style.display = 'none';
        
        // Show loading
        loading.style.display = 'block';
        searchButton.disabled = true;

        // Get search parameters
        const topK = parseInt(document.getElementById('topK').value);
        const searchMode = document.getElementById('searchMode').value;
        const useHybrid = searchMode === 'hybrid';
        const showScores = document.getElementById('showScores').checked;

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    top_k: topK,
                    use_hybrid: useHybrid
                })
            });

            const data = await response.json();

            // Hide loading
            loading.style.display = 'none';
            searchButton.disabled = false;

            if (data.success) {
                if (data.results.length === 0) {
                    noResults.style.display = 'block';
                } else {
                    displayResults(data.results, showScores);
                }
            } else {
                showError(data.error || 'An error occurred while searching');
            }
        } catch (error) {
            loading.style.display = 'none';
            searchButton.disabled = false;
            showError('Network error. Please try again.');
            console.error('Search error:', error);
        }
    }

    // Display search results
    function displayResults(results, showScores) {
        searchResults.innerHTML = '';

        results.forEach(result => {
            const card = createResultCard(result, showScores);
            searchResults.appendChild(card);
        });

        // Animate results
        const cards = searchResults.querySelectorAll('.result-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            setTimeout(() => {
                card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 50);
        });
    }

    // Create result card
    function createResultCard(result, showScores) {
        const card = document.createElement('div');
        card.className = 'result-card';
        
        // Calculate score color
        const scoreColor = getScoreColor(result.final_score);
        
        // Build score display
        let scoreHTML = '';
        if (showScores) {
            scoreHTML = `
                <div class="result-score">
                    <div class="score-main" style="color: ${scoreColor}">
                        ${result.final_score.toFixed(3)}
                    </div>
                    <div class="score-breakdown">
                        S: ${result.semantic_score.toFixed(2)} | 
                        K: ${result.keyword_score.toFixed(2)} | 
                        B: ${result.boost_applied.toFixed(2)}x
                    </div>
                </div>
            `;
        }

        card.innerHTML = `
            <div class="result-header">
                <div class="result-rank">${result.rank}</div>
                <div class="result-title">
                    <h2 class="result-name">${escapeHtml(result.name)}</h2>
                    <div class="result-specialization">${escapeHtml(result.specialization)}</div>
                </div>
                ${scoreHTML}
            </div>
            <div class="result-content">
                ${createResultSection('Biography', result.biography)}
                ${createResultSection('Publications', result.publications)}
                ${createResultSection('Education', result.education)}
                <div class="result-contact">
                    ${result.email ? `
                        <div class="contact-item">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="2" y="4" width="20" height="16" rx="2"></rect>
                                <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path>
                            </svg>
                            ${escapeHtml(result.email)}
                        </div>
                    ` : ''}
                    ${result.number ? `
                        <div class="contact-item">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                            </svg>
                            ${escapeHtml(result.number)}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        // Add click handler for modal
        card.addEventListener('click', function() {
            showFacultyDetails(result);
        });

        return card;
    }

    // Create result section
    function createResultSection(label, content) {
        if (!content || content === 'Not provided' || content.trim() === '') {
            return '';
        }

        return `
            <div class="result-section">
                <div class="result-label">${label}</div>
                <div class="result-text">${escapeHtml(content)}</div>
            </div>
        `;
    }

    // Show faculty details in modal
    function showFacultyDetails(result) {
        const modalBody = document.getElementById('modalBody');
        
        modalBody.innerHTML = `
            <h2 style="margin-bottom: 0.5rem;">${escapeHtml(result.name)}</h2>
            <p style="color: var(--primary-color); font-weight: 600; margin-bottom: 2rem;">
                ${escapeHtml(result.specialization)}
            </p>
            
            ${result.biography && result.biography !== 'Not provided' ? `
                <div style="margin-bottom: 2rem;">
                    <h3 style="margin-bottom: 0.5rem;">Biography</h3>
                    <p style="color: var(--text-secondary); line-height: 1.7;">
                        ${escapeHtml(result.biography)}
                    </p>
                </div>
            ` : ''}
            
            ${result.publications && result.publications !== 'Not provided' ? `
                <div style="margin-bottom: 2rem;">
                    <h3 style="margin-bottom: 0.5rem;">Publications</h3>
                    <p style="color: var(--text-secondary); line-height: 1.7;">
                        ${escapeHtml(result.publications)}
                    </p>
                </div>
            ` : ''}
            
            ${result.education && result.education !== 'Not provided' ? `
                <div style="margin-bottom: 2rem;">
                    <h3 style="margin-bottom: 0.5rem;">Education</h3>
                    <p style="color: var(--text-secondary); line-height: 1.7;">
                        ${escapeHtml(result.education)}
                    </p>
                </div>
            ` : ''}
            
            <div style="padding: 1.5rem; background: var(--bg-secondary); border-radius: var(--radius-lg);">
                <h3 style="margin-bottom: 1rem;">Contact Information</h3>
                ${result.email ? `
                    <p style="margin-bottom: 0.5rem;">
                        <strong>Email:</strong> ${escapeHtml(result.email)}
                    </p>
                ` : ''}
                ${result.number ? `
                    <p style="margin-bottom: 0.5rem;">
                        <strong>Phone:</strong> ${escapeHtml(result.number)}
                    </p>
                ` : ''}
                ${result.address ? `
                    <p style="margin-bottom: 0.5rem;">
                        <strong>Address:</strong> ${escapeHtml(result.address)}
                    </p>
                ` : ''}
            </div>
            
            ${result.final_score ? `
                <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid var(--border-color);">
                    <h3 style="margin-bottom: 0.5rem;">Match Details</h3>
                    <p style="color: var(--text-secondary);">
                        <strong>Final Score:</strong> ${result.final_score.toFixed(3)}<br>
                        <strong>Semantic Score:</strong> ${result.semantic_score.toFixed(3)}<br>
                        <strong>Keyword Score:</strong> ${result.keyword_score.toFixed(3)}<br>
                        <strong>Boost Applied:</strong> ${result.boost_applied.toFixed(2)}x
                    </p>
                </div>
            ` : ''}
        `;

        facultyModal.style.display = 'block';
    }

    // Get score color based on value
    function getScoreColor(score) {
        if (score >= 0.8) return '#10b981'; // Green
        if (score >= 0.6) return '#3b82f6'; // Blue
        if (score >= 0.4) return '#f59e0b'; // Orange
        return '#6b7280'; // Gray
    }

    // Show error message
    function showError(message) {
        searchResults.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">⚠️</div>
                <h3>Error</h3>
                <p>${escapeHtml(message)}</p>
            </div>
        `;
    }

    // Escape HTML to prevent XSS
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Handle browser back/forward
    window.addEventListener('popstate', function() {
        const urlParams = new URLSearchParams(window.location.search);
        const query = urlParams.get('q');
        if (query) {
            searchQuery.value = query;
            performSearch(query);
        } else {
            searchResults.innerHTML = '';
            noResults.style.display = 'none';
            quickSearches.style.display = 'block';
        }
    });
});
