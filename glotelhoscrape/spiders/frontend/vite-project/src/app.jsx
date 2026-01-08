// src/App.jsx
import { useState, useEffect } from "react";
import "./App.css";
import Logo1 from "./logo.png";

export default function App() {
  const [q, setQ] = useState("");
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [scrollDarkness, setScrollDarkness] = useState(0);

  // Scroll = ambiance (overlay + blur)
  useEffect(() => {
  const handleScroll = () => {
    const centre = document.querySelector(".centre");
    if (!centre) return;

    const centreBottom = centre.offsetTop + centre.offsetHeight;
    const scrollY = window.scrollY;

    // Tant qu’on est au-dessus des résultats → clair
    if (scrollY < centreBottom - 100) {
      setScrollDarkness(0);
      document.documentElement.style.setProperty("--blur", 0);
      return;
    }

    // Assombrissement progressif APRÈS la zone search
    const delta = scrollY - centreBottom;
    const maxScroll = 400;

    const darkness = Math.min(delta / maxScroll, 0.4);
    const blur = Math.min(delta / 40, 12);

    setScrollDarkness(darkness);
    document.documentElement.style.setProperty("--blur", blur);
  };

  window.addEventListener("scroll", handleScroll);
  return () => window.removeEventListener("scroll", handleScroll);
}, []);


  const onSubmit = async (e) => {
    e.preventDefault();
    if (!q.trim()) return;

    setError(null);
    setLoading(true);
    setResults([]);

    try {
      const res = await fetch(
        `http://127.0.0.1:5000/search?query=${encodeURIComponent(q)}`
      );
      if (!res.ok) throw new Error(`Erreur serveur ${res.status}`);
      const data = await res.json();
      setResults(data.results || []);
    } catch (err) {
      setError("Erreur lors de la récupération des produits.");
    } finally {
      setLoading(false);
    }
  };

  const hasResults = results.length > 0;

  return (
    <div className="page">
      <main className={`main ${hasResults ? "searched" : ""}`}>
        
        
      <div className="background1">
          <div className="content">
            <div className="centre">
              <img src={Logo1} className="logo-img" alt="Logo" />

              <div className="logo">KMERSEARCH</div>

              <form className="search" onSubmit={onSubmit}>
                <div className="searchbox">
                  <input
                    type="text"
                    value={q}
                    onChange={(e) => setQ(e.target.value)}
                    placeholder="Search on KmerSearch"
                    autoFocus
                  />
                </div>

                <div className="actions">
                  <button type="submit" className="btn">
                    Research products
                  </button>
                </div>
              </form>
            </div>
          </div>
             <div className="background">
          <div
            className="overlay"
            style={{
              background: `linear-gradient(
                rgba(255,255,255,0.75) 0%,
                rgba(0,0,0,${scrollDarkness}) 100%
              )`,
            }}
          />
            {loading && <p className="loading">Recherche en cours…</p>}
            {error && <p className="error">{error}</p>}

            {hasResults && (
              <section className="results">
                <h2>Produits trouvés</h2>

                {results.map((item, idx) => (
                  <div
                    key={idx}
                    className="result-card"
                    style={{ "--i": idx }}
                  >
                    {item.image ? (
                      <div className="result-image">
                        <img
                          src={item.image}
                          alt={item.title}
                          className="result-image-img"
                        />
                      </div>
                    ) : (
                      <div className="placeholder-image">📦</div>
                    )}

                    <div className="result-info">
                      <h3 className="result-title">{item.title}</h3>
                      <p className="result-description">{item.text}</p>

                      {item.price !== undefined && (
                        <p className="result-price">
                          {item.price} FCFA
                        </p>
                      )}

                      {item.url && (
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="result-link"
                        >
                          Voir le produit
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </section>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
