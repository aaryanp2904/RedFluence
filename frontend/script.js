document.addEventListener('DOMContentLoaded', () => {
    const API_URL = 'http://localhost:5000'; // Update this if your backend is hosted elsewhere
    const loginBtn = document.getElementById('login-btn');
    const userInfoSection = document.getElementById('user-info');
    const headlinesSection = document.getElementById('headlines-section');
    const headlinesList = document.getElementById('headlines-list');
    const articleSection = document.getElementById('article-section');
    const chosenHeadline = document.getElementById('chosen-headline');
    const generatedImage = document.getElementById('generated-image');
    const articleContent = document.getElementById('article-content');
    const sentimentAnalysis = document.getElementById('sentiment-analysis');
    const hashtagsContainer = document.getElementById('hashtags-container');
    const loadingIndicator = document.getElementById('loading-indicator');
    const logoutBtn = document.createElement('button');
    logoutBtn.textContent = 'Logout';
    logoutBtn.style.display = 'none';

    let accessToken = null;

    function showLoading() {
        loadingIndicator.style.display = 'block';
    }

    function hideLoading() {
        loadingIndicator.style.display = 'none';
    }

    function getCodeFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('code');
    }

    function clearUrlParameters() {
        window.history.replaceState({}, document.title, window.location.pathname);
    }

    const authCode = getCodeFromUrl();
    if (authCode) {
        showLoading();
        sendCodeToBackend(authCode);
    } else {
        checkExistingSession();
    }

    loginBtn.addEventListener('click', () => {
        window.location.href = `${API_URL}/auth/instagram`;
    });

    logoutBtn.addEventListener('click', logout);

    function sendCodeToBackend(code) {
        fetch(`${API_URL}/auth/instagram/callback`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code: code }),
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            accessToken = data.access_token;
            handleSuccessfulLogin(data.profile_data);
            clearUrlParameters();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during authentication. Please try again.');
        })
        .finally(() => {
            hideLoading();
        });
    }
    
    function checkExistingSession() {
        fetch(`${API_URL}/check_session`, {
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            if (data.authenticated) {
                accessToken = data.access_token;
                handleSuccessfulLogin(data.profile_data);
            } else {
                loginBtn.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error checking session:', error);
            loginBtn.style.display = 'block';
        });
    }

    function handleSuccessfulLogin(userData) {
        loginBtn.style.display = 'none';
        logoutBtn.style.display = 'block';
        document.body.appendChild(logoutBtn);
        displayUserInfo(userData);
        generateHeadlines(userData);
    }
    
    function displayUserInfo(userData) {
        userInfoSection.innerHTML = `
            <h2>${userData.username}</h2>
            <p>Account Type: ${userData.account_type}</p>
            <p>Posts: ${userData.media_count}</p>
            <p>Bio: ${userData.biography}</p>
        `;
        userInfoSection.style.display = 'block';
    }

    async function generateHeadlines(userData) {
        showLoading();
        try {
            const response = await fetch(`${API_URL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                },
                credentials: 'include'
            });

            if (!response.ok) {
                if (response.status === 401) {
                    throw new Error('Not authenticated. Please log in again.');
                }
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }
            displayHeadlines(data.headlines);
        } catch (error) {
            console.error('Error:', error);
            alert(`An error occurred: ${error.message}`);
            if (error.message === 'Not authenticated. Please log in again.') {
                logout();
            }
        } finally {
            hideLoading();
        }
    }

    function displayHeadlines(headlines) {
        headlinesList.innerHTML = '';
        headlines.forEach((headline) => {
            const headlineElement = document.createElement('div');
            headlineElement.classList.add('headline-option');
            headlineElement.textContent = headline;
            headlineElement.addEventListener('click', () => selectHeadline(headline));
            headlinesList.appendChild(headlineElement);
        });
        headlinesSection.style.display = 'block';
        articleSection.style.display = 'none';
    }

    async function selectHeadline(headline) {
        showLoading();
        try {
            const response = await fetch(`${API_URL}/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                },
                body: JSON.stringify({ chosen_headline: headline }),
                credentials: 'include'
            });

            if (!response.ok) {
                if (response.status === 401) {
                    throw new Error('Not authenticated. Please log in again.');
                }
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }
            displayArticle(headline, data.article, data.image_url, data.sentiment, data.hashtags);
        } catch (error) {
            console.error('Error:', error);
            alert(`An error occurred: ${error.message}`);
            if (error.message === 'Not authenticated. Please log in again.') {
                logout();
            }
        } finally {
            hideLoading();
        }
    }

    function displayArticle(headline, article, imageUrl, sentiment, hashtags) {
        chosenHeadline.textContent = headline;
        generatedImage.src = imageUrl;
        articleContent.textContent = article;
        sentimentAnalysis.textContent = `Sentiment Analysis: ${sentiment}`;
        
        hashtagsContainer.innerHTML = '';
        hashtags.forEach(hashtag => {
            const hashtagElement = document.createElement('span');
            hashtagElement.classList.add('hashtag');
            hashtagElement.textContent = hashtag;
            hashtagsContainer.appendChild(hashtagElement);
        });

        headlinesSection.style.display = 'none';
        articleSection.style.display = 'block';
    }

    function logout() {
        fetch(`${API_URL}/logout`, {
            method: 'POST',
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                accessToken = null;
                loginBtn.style.display = 'block';
                logoutBtn.style.display = 'none';
                userInfoSection.style.display = 'none';
                headlinesSection.style.display = 'none';
                articleSection.style.display = 'none';
                alert('Logged out successfully');
            } else {
                throw new Error('Logout failed');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during logout. Please try again.');
        });
    }

    const backButton = document.getElementById('back-to-headlines');
    backButton.addEventListener('click', () => {
        articleSection.style.display = 'none';
        headlinesSection.style.display = 'block';
    });

    const shareButton = document.getElementById('share-article');
    shareButton.addEventListener('click', () => {
        const articleUrl = window.location.href;
        const shareText = `Check out this article: ${chosenHeadline.textContent}\n${articleUrl}`;
        navigator.clipboard.writeText(shareText).then(() => {
            alert('Article link copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy: ', err);
        });
    });
});