import React, { useState } from 'react';
import './App.css';

function App() {
  const [username, setUsername] = useState('');
  const [subreddits, setSubreddits] = useState([]);
  const [images, setImages] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubreddits([]);
    setImages([]);
    setError('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/get_active_subreddits', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      setSubreddits(data.subreddits);
      setImages(data.images);
    } catch (error) {
      console.error('Error:', error);
      setError('An error occurred while fetching data.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Reddit User Activity</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Enter Reddit username"
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Loading...' : 'Get Active Subreddits'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      {subreddits.length > 0 && (
        <div>
          <h2>Most Active Subreddits:</h2>
          <ul className="subreddit-list">
            {images.map((item, index) => (
              <li key={index}>
                <h3>{item.subreddit}</h3>
                {item.image_url ? (
                  <img src={item.image_url} alt={`${item.subreddit} representation`} />
                ) : (
                  <p>Image generation failed</p>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;