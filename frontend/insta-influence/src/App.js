import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = 'http://localhost:5000'; // Update if your backend is hosted elsewhere

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [instagramUrl, setInstagramUrl] = useState('');
  const [headlines, setHeadlines] = useState([]);
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [profileData, setProfileData] = useState(null);

  useEffect(() => {
    // Check if user is authenticated with Instagram
    fetch(`${API_URL}/check_auth`, {
      credentials: 'include' // Important for sending cookies
    })
      .then(response => response.json())
      .then(data => setIsAuthenticated(data.authenticated))
      .catch(error => console.error('Error checking auth:', error));
  }, []);

  const handleLogin = () => {
    window.location.href = `${API_URL}/auth/instagram`;
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ instagram_url: instagramUrl }),
        credentials: 'include', // Important for sending cookies
      });
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      setProfileData(data.profile_data);
      setHeadlines(data.headlines);
      setArticle(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectHeadline = async (headline) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chosen_headline: headline, profile_data: profileData }),
        credentials: 'include',
      });
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      setArticle({ headline, content: data.article, imageUrl: data.image_url });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleShare = () => {
    const shareText = `Check out this article: ${article.headline}\n${window.location.href}`;
    navigator.clipboard.writeText(shareText)
      .then(() => alert('Article link copied to clipboard!'))
      .catch(err => console.error('Failed to copy: ', err));
  };

  return (
    <div className="App">
      <h1>InstaInfluence</h1>
      {!isAuthenticated ? (
        <div>
          <p>Please log in with Instagram to use this app.</p>
          <button onClick={handleLogin}>Login with Instagram</button>
        </div>
      ) : (
        <div>
          <div id="input-section">
            <input
              type="text"
              value={instagramUrl}
              onChange={(e) => setInstagramUrl(e.target.value)}
              placeholder="Enter Instagram profile URL"
            />
            <button onClick={handleAnalyze} disabled={loading}>Analyze</button>
          </div>
          {loading && <div id="loading-indicator">Loading...</div>}
          {error && <div className="error">{error}</div>}
          {headlines.length > 0 && !article && (
            <div id="headlines-section">
              <h2>Choose a Headline:</h2>
              <div id="headlines-list">
                {headlines.map((headline, index) => (
                  <div key={index} className="headline-option" onClick={() => handleSelectHeadline(headline)}>
                    {headline}
                  </div>
                ))}
              </div>
            </div>
          )}
          {article && (
            <div id="article-section">
              <h2>{article.headline}</h2>
              <img id="generated-image" src={article.imageUrl} alt="Generated for article" />
              <div id="article-content">{article.content}</div>
              <button onClick={() => setArticle(null)}>Back to Headlines</button>
              <button onClick={handleShare}>Share Article</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;