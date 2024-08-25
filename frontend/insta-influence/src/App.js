// import React, { useState } from 'react';
// import './App.css';

// function App() {
//   const [username, setUsername] = useState('');
//   const [subreddits, setSubreddits] = useState([]);
//   const [storiesAndImages, setStoriesAndImages] = useState([]);
//   const [error, setError] = useState('');
//   const [loading, setLoading] = useState(false);
//   const [expandedPost, setExpandedPost] = useState(null); // For tracking expanded post

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     setSubreddits([]);
//     setStoriesAndImages([]);
//     setError('');
//     setLoading(true);

//     try {
//       const response = await fetch('http://localhost:5000/get_active_subreddits', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ username }),
//       });

//       if (!response.ok) {
//         throw new Error('Network response was not ok');
//       }

//       const data = await response.json();
//       setSubreddits(data.subreddits || []);
//       setStoriesAndImages(data.stories_and_images || []);
//     } catch (error) {
//       console.error('Error:', error);
//       setError('An error occurred while fetching data.');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const toggleExpandPost = (index) => {
//     if (expandedPost === index) {
//       setExpandedPost(null); // Collapse if the same post is clicked again
//     } else {
//       setExpandedPost(index); // Expand the selected post
//     }
//   };

//   return (
//     <div className="App">
//       <h1>Red-Fluence</h1>
//       <form onSubmit={handleSubmit} className="username-form">
//         <input
//           type="text"
//           value={username}
//           onChange={(e) => setUsername(e.target.value)}
//           placeholder="Enter username..."
//           required
//         />
//         <button type="submit" disabled={loading}>
//           {loading ? 'Loading...' : 'Submit'}
//         </button>
//       </form>
//       <div className="content-container">
//         <div className="subreddit-container">
//           {error && <p className="error">{error}</p>}
//           {subreddits.length > 0 && (
//             <div className="scrollable-content">
//               {storiesAndImages.map((item, index) => (
//                 <div
//                   key={index}
//                   className={`subreddit-item ${expandedPost === index ? 'expanded' : ''}`}
//                   onClick={() => toggleExpandPost(index)}
//                 >
//                   <div className="post-header">
//                     <p className="subreddit-name">r/{item.subreddit}</p>
//                     <p className="post-title">{item.title}</p>
//                   </div>
//                   <img
//                     src={item.image_url}
//                     alt={`${item.subreddit} representation`}
//                     className="subreddit-image"
//                   />
//                   {expandedPost === index && (
//                     <div className="post-details">
//                       <p>{item.story}</p>
//                       {/* Add vote/comment/share buttons */}
//                       <div className="post-actions">
//                         <div className="vote-buttons">
//                           <button>⬆️</button>
//                           <span>{item.votes}</span>
//                           <button>⬇️</button>
//                         </div>
//                         <button className="comment-button">💬 {item.comments}</button>
//                         <button className="share-button">🔗</button>
//                       </div>
//                     </div>
//                   )}
//                 </div>
//               ))}
//             </div>
//           )}
//         </div>
//         <div className="explanation-container">
//           <p>This section uses the get_explanation API of the :5000 backend to get data for now</p>
//         </div>
//       </div>
//     </div>
//   );
// }

// export default App;

import React, { useState } from 'react';
import './App.css';

function App() {
  const [username, setUsername] = useState('');
  const [subreddits, setSubreddits] = useState([]);
  const [storiesAndImages, setStoriesAndImages] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [expandedPost, setExpandedPost] = useState(null); // Track the expanded post

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubreddits([]);
    setStoriesAndImages([]);
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
      setSubreddits(data.subreddits || []);
      setStoriesAndImages(data.stories_and_images || []);
    } catch (error) {
      console.error('Error:', error);
      setError('An error occurred while fetching data.');
    } finally {
      setLoading(false);
    }
  };

  const expandPost = (index) => {
    setExpandedPost(index);
  };

  const goBack = () => {
    setExpandedPost(null); // Reset the expanded post to show the list again
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
          {subreddits.length > 0 && (
            <div className="scrollable-content">
              {expandedPost === null ? (
                storiesAndImages.map((item, index) => (
                  <div
                    key={index}
                    className="subreddit-item"
                    onClick={() => expandPost(index)}
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
                    <h3>r/{storiesAndImages[expandedPost].subreddit}</h3>
                    <h4>{storiesAndImages[expandedPost].title}</h4>
                    <img
                      src={storiesAndImages[expandedPost].image_url}
                      alt={`${storiesAndImages[expandedPost].subreddit} representation`}
                      className="subreddit-image-expanded"
                    />
                    <p>{storiesAndImages[expandedPost].story}</p>
                    <div className="post-actions">
                      <div className="vote-buttons">
                        <button>⬆️</button>
                        <span>{storiesAndImages[expandedPost].votes}</span>
                        <button>⬇️</button>
                      </div>
                      <button className="comment-button">💬 {storiesAndImages[expandedPost].comments}</button>
                      <button className="share-button">🔗</button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
        <div className="explanation-container">
          <p>This section uses the get_explanation API of the :5000 backend to get data for now</p>
        </div>
      </div>
    </div>
  );
}

export default App;
