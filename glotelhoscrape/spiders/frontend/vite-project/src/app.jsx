import React, { useState, useEffect, useRef } from 'react';
import './app.css';

const App = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [imageErrors, setImageErrors] = useState({});
  const inputRef = useRef(null);

  // Focus sur l'input au chargement
  useEffect(() => {
    if (inputRef.current && !hasSearched) {
      inputRef.current.focus();
    }
  }, [hasSearched]);

  // Fonction pour obtenir l'URL de l'image via le proxy Flask
  const getImageUrl = (imageUrl) => {
    if (!imageUrl) return null;
    return `http://localhost:5000/image?url=${encodeURIComponent(imageUrl)}`;
  };

  const handleSearch = async (e) => {
    e?.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setHasSearched(true);
    setImageErrors({});

    try {
      const response = await fetch(`http://localhost:5000/search?query=${encodeURIComponent(query)}`);
      const data = await response.json();
      
      // Traiter les résultats pour s'assurer qu'on a les images
      const processedResults = data.results?.map(product => ({
        ...product,
        // S'assurer que 'images' est un tableau
        images: Array.isArray(product.images) ? product.images : [product.images].filter(Boolean)
      })) || [];
      
      setResults(processedResults);
    } catch (error) {
      console.error('Erreur:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSearch(e);
    }
    if (e.key === 'Escape' && query) {
      setQuery('');
    }
  };

  const resetSearch = () => {
    setQuery('');
    setResults([]);
    setHasSearched(false);
    setImageErrors({});
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const handleImageError = (index) => {
    setImageErrors(prev => ({
      ...prev,
      [index]: true
    }));
  };

  return (
    <div className="app">
      {/* Header fixe en haut */}
      <header className={`header ${hasSearched ? 'compact' : ''}`}>
        <div className="header-content">
          <div className="logo" onClick={resetSearch}>
            <span className="logo-letter">KMERSEARCH</span>
            {!hasSearched && <span className="logo-text">Search</span>}
          </div>
          
          {hasSearched && (
            <div className="search-bar">
              <div className="search-input-wrapper">
                <div className="search-icon">🔍</div>
                <input
                  ref={inputRef}
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Rechercher des produits..."
                  className="search-input"
                />
                {query && (
                  <button 
                    type="button" 
                    onClick={() => setQuery('')}
                    className="clear-btn"
                  >
                    ✕
                  </button>
                )}
              </div>
            </div>
          )}

          {hasSearched && (
            <div className="header-actions">
              <button onClick={handleSearch} className="search-action-btn">
                Rechercher
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Contenu principal */}
      <main className={`main-content ${hasSearched ? 'with-results' : 'centered'}`}>
        {!hasSearched ? (
          // Vue initiale - plein écran
          <div className="hero-section">
            <div className="hero-logo">
              <div className="hero-logo-letter">KMERSEARCH</div>
              <div className="hero-logo-text">Search</div>
            </div>
            
            <form className="hero-search" onSubmit={handleSearch}>
              <div className="hero-input-wrapper">
                <div className="hero-search-icon">🔍</div>
                <input
                  ref={inputRef}
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Rechercher des produits..."
                  className="hero-search-input"
                />
                {query && (
                  <button 
                    type="button" 
                    onClick={() => setQuery('')}
                    className="hero-clear-btn"
                  >
                    ✕
                  </button>
                )}
              </div>
              
              <div className="hero-actions">
                <button type="submit" className="hero-search-btn">
                  Recherche sur KMERSEARCH
                </button>
              </div>
            </form>

            <div className="hero-hint">
              Appuyez sur Entrée pour rechercher • Esc pour effacer
            </div>
          </div>
        ) : (
          // Vue résultats - plein écran
          <div className="results-section">
            {loading ? (
              <div className="loading-full">
                <div className="spinner-large"></div>
                <div className="loading-text">Recherche en cours...</div>
              </div>
            ) : results.length > 0 ? (
              <>
                <div className="results-stats">
                  {results.length} résultat{results.length > 1 ? 's' : ''} pour "{query}"
                </div>
                
                <div className="results-grid">
                  {results.map((product, index) => {
                    const hasImages = product.images && product.images.length > 0;
                    const firstImageUrl = hasImages ? product.images[0] : null;
                    const imageFailed = imageErrors[index];
                    
                    return (
                      <div key={index} className="product-card">
                        {/* Section image */}
                        <div className="product-image-container">
                          {hasImages && !imageFailed ? (
                            <img
                              src={getImageUrl(firstImageUrl)}
                              alt={product.title || 'Produit'}
                              className="product-image"
                              loading="lazy"
                              onError={() => handleImageError(index)}
                              onLoad={(e) => {
                                // Optionnel: gérer le chargement réussi
                                e.target.style.opacity = '1';
                              }}
                            />
                          ) : (
                            <div className="product-image-placeholder">
                              <div className="placeholder-icon">📦</div>
                              <div className="placeholder-text">Pas d'image</div>
                            </div>
                          )}
                        </div>
                        
                        {/* Contenu du produit */}
                        <div className="product-content">
                          <div className="product-header">
                            <div className="product-source">
                              {product.url?.replace('https://', '').split('/')[0] || 'glotelho.com'}
                            </div>
                            {product.price && (
                              <div className="product-price">
                                {product.price} FCFA
                              </div>
                            )}
                          </div>
                          
                          <a 
                            href={product.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="product-title"
                          >
                            {product.title || 'Produit sans nom'}
                          </a>
                          
                          <div className="product-description">
                            {product.description || 'Aucune description disponible'}
                          </div>
                          
                          <div className="product-footer">
                            <span className="tech-badge">KMERSEARCH</span>
                            <button 
                              onClick={() => window.open(product.url, '_blank')}
                              className="view-btn"
                            >
                              Voir →
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">🔍</div>
                <div className="empty-title">
                  Aucun résultat pour "{query}"
                </div>
                <div className="empty-subtitle">
                  Essayez avec d'autres termes de recherche
                </div>
                <button 
                  onClick={resetSearch}
                  className="empty-action-btn"
                >
                  Nouvelle recherche
                </button>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer minimal fixe en bas */}
      <footer className={`footer ${hasSearched ? 'compact' : ''}`}>
        <div className="footer-content">
          <div className="footer-left">
            <span>Cameroun</span>
          </div>
          <div className="footer-right">
            <a href="#" className="footer-link">Confidentialité</a>
            <a href="#" className="footer-link">Conditions</a>
            <span className="footer-tech">Powered by KMERSEARCH</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;