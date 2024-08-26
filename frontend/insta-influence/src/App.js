import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [username, setUsername] = useState('');
  const [subredditData, setSubredditData] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [expandedPost, setExpandedPost] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);

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
    setChatMessages([]);

    const eventSource = new EventSource("http://localhost:5000" + `/get_active_subreddits?username=${username}`);

    eventSource.onmessage = (event) => {
      if (event.data === "DONE") {
        eventSource.close();
        setLoading(false);
      }
      else {
        const articleData = JSON.parse(event.data);

        if (articleData.insights) {
          setChatMessages(prevMessages => [...prevMessages, { type: 'ai', content: articleData.insights }]);
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
    setChatMessages(prevMessages => [...prevMessages, { type: 'user', content: `You clicked on the article "${post.title}"` }]);
    // trackArticleClick(post);
  };

  const trackArticleClick = async (article) => {
    try {
      const response = await fetch("http://localhost:5000/track_article_click", {
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
      setChatMessages(prevMessages => [...prevMessages, { type: 'ai', content: data.ai_insights }]);
    } catch (error) {
      console.error('Error tracking article click:', error);
    }
  };

  const goBack = () => {
    setExpandedPost(null);
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
          <div className="reddit-navbar">
            <div className="navbar-left">
              <img src="https://www.redditstatic.com/avatars/defaults/v2/avatar_default_0.png" alt="User" className="user-avatar" />
            </div>
            <div className="navbar-center">Home</div>
            <div className="navbar-right">
              <button className="menu-button">☰</button>
            </div>
          </div>
          {error && <p className="error">{error}</p>}
          {subredditData.length > 0 && (
            <div className="scrollable-content">
              {expandedPost === null ? (
                subredditData.map((item, index) => (
                  <div key={index} className="reddit-post">
                    <div className="post-header">
                      <img src="https://www.redditstatic.com/avatars/defaults/v2/avatar_default_1.png" alt="Subreddit icon" className="subreddit-icon" />
                      <p className="subreddit-name">r/{item.subreddit}</p>
                      <p className="post-meta">• Posted by u/FakeUser • 1h</p>
                    </div>
                    <p className="post-title" onClick={() => expandPost(item)}>{item.title}</p>
                    <img
                      src={item.image_url}
                      alt={`${item.subreddit} representation`}
                      className="post-image"
                      onClick={() => expandPost(item)}
                    />
                    <div className="post-actions">
                      <button className="vote-button upvote">⬆️</button>
                      <span className="vote-count">{item.votes}</span>
                      <button className="vote-button downvote">⬇️</button>
                      <button className="action-button">💬 {item.comments}</button>
                      <button className="action-button">Share</button>
                    </div>
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
          <div className="chat-bubbles">
            {chatMessages.map((message, index) => (
              <div key={index} className={`chat-bubble ${message.type}-bubble`}>
                {message.content}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;