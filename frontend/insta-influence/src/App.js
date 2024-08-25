import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [username, setUsername] = useState('');
  const [subredditData, setSubredditData] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [expandedPost, setExpandedPost] = useState(null);
  const [aiInsights, setAiInsights] = useState('');

  useEffect(() => {
    if (expandedPost) {
      trackArticleClick(expandedPost);
    }
  }, [expandedPost]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubredditData([]);
    setError('');
    setLoading(true);
    setExpandedPost(null);
    setAiInsights('');

    const eventSource = new EventSource(`http://localhost:5000/get_active_subreddits?username=${username}`);

    eventSource.onmessage = (event) => {
      if (event.data === "DONE") {
        eventSource.close();
        setLoading(false);
      }         
      else {
        const articleData = JSON.parse(event.data);

        if (articleData.insights) {
          setAiInsights(articleData.insights)
        }
        else {
          setSubredditData(prevData => [...prevData, articleData]);
        }
      }
    };

    eventSource.onerror = (error) => {
      console.error('EventSource failed:', error);
      setError('An error occurred while fetching data.');
      setLoading(false);
      eventSource.close();
    };
  };

  const expandPost = (post) => {
    setExpandedPost(post);
    trackArticleClick(post);
  };

  const trackArticleClick = async (article) => {
    try {
      const response = await fetch('http://localhost:5000/track_article_click', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, article }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      setAiInsights(aiInsights + "\n" + data.ai_insights);
    } catch (error) {
      console.error('Error tracking article click:', error);
      // setAiInsights('Failed to load AI insights. Please try again.');
    }
  };

  const goBack = () => {
    setExpandedPost(null);
    //setAiInsights('');
  };

  return (
    <div className="App">
      <h1>Red-Fluence</h1>
      <form onSubmit={handleSubmit} className="username-form">
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Enter username..."
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Loading...' : 'Submit'}
        </button>
      </form>
      <div className="content-container">
        <div className="subreddit-container">
          {error && <p className="error">{error}</p>}
          {subredditData.length > 0 && (
            <div className="scrollable-content">
              {expandedPost === null ? (
                subredditData.map((item, index) => (
                  <div
                    key={index}
                    className="subreddit-item"
                    onClick={() => expandPost(item)}
                  >
                    <div className="post-header">
                      <p className="subreddit-name">r/{item.subreddit}</p>
                      <p className="post-title">{item.title}</p>
                    </div>
                    <img
                      src={item.image_url}
                      alt={`${item.subreddit} representation`}
                      className="subreddit-image"
                    />
                  </div>
                ))
              ) : (
                <div className="expanded-post">
                  <button className="back-button" onClick={goBack}>
                    ← Back
                  </button>
                  <div className="post-details-expanded">
                    <h3>r/{expandedPost.subreddit}</h3>
                    <h4>{expandedPost.title}</h4>
                    <img
                      src={expandedPost.image_url}
                      alt={`${expandedPost.subreddit} representation`}
                      className="subreddit-image-expanded"
                    />
                    <p>{expandedPost.story}</p>
                    <div className="post-actions">
                      <div className="vote-buttons">
                        <button>⬆️</button>
                        <span>{expandedPost.votes}</span>
                        <button>⬇️</button>
                      </div>
                      <button className="comment-button">💬 {expandedPost.comments}</button>
                      <button className="share-button">🔗</button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
        <div className="explanation-container">
          <h2>AI Insights</h2>
          <pre>{aiInsights}</pre>
        </div>
      </div>
    </div>
  );
}

export default App;
