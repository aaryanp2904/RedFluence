document.addEventListener('DOMContentLoaded', () => {
    const API_URL = 'http://localhost:5000'; // Update this if your backend is hosted elsewhere
    const instagramUrlInput = document.getElementById('instagram-url');
    const analyzeBtn = document.getElementById('analyze-btn');
    const headlinesSection = document.getElementById('headlines-section');
    const headlinesList = document.getElementById('headlines-list');
    const articleSection = document.getElementById('article-section');
    const chosenHeadline = document.getElementById('chosen-headline');
    const generatedImage = document.getElementById('generated-image');
    const articleContent = document.getElementById('article-content');
    const loadingIndicator = document.getElementById('loading-indicator');

    let profileData = null;

    function showLoading() {
        loadingIndicator.style.display = 'block';
    }

    function hideLoading() {
        loadingIndicator.style.display = 'none';
    }

    function isValidInstagramUrl(url) {
        const regex = /^https?:\/\/(www\.)?instagram\.com\/[a-zA-Z0-9_.]{1,30}\/?$/;
        return regex.test(url);
    }

    analyzeBtn.addEventListener('click', async () => {
        const instagramUrl = instagramUrlInput.value.trim();
        if (!instagramUrl) {
            alert('Please enter an Instagram profile URL');
            return;
        }

        if (!isValidInstagramUrl(instagramUrl)) {
            alert('Please enter a valid Instagram profile URL');
            return;
        }

        showLoading();

        try {
            const response = await fetch(`${API_URL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ instagram_url: instagramUrl }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }
            profileData = data.profile_data;
            displayHeadlines(data.headlines);
        } catch (error) {
            console.error('Error:', error);
            alert(`An error occurred: ${error.message}`);
        } finally {
            hideLoading();
        }
    });

    function displayHeadlines(headlines) {
        headlinesList.innerHTML = '';
        headlines.forEach((headline, index) => {
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
                },
                body: JSON.stringify({ chosen_headline: headline, profile_data: profileData }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }
            displayArticle(headline, data.article, data.image_url);
        } catch (error) {
            console.error('Error:', error);
            alert(`An error occurred: ${error.message}`);
        } finally {
            hideLoading();
        }
    }

    function displayArticle(headline, article, imageUrl) {
        chosenHeadline.textContent = headline;
        generatedImage.src = imageUrl;
        articleContent.textContent = article;
        headlinesSection.style.display = 'none';
        articleSection.style.display = 'block';

        const backButton = document.createElement('button');
        backButton.textContent = 'Back to Headlines';
        backButton.addEventListener('click', () => {
            articleSection.style.display = 'none';
            headlinesSection.style.display = 'block';
        });
        articleSection.appendChild(backButton);

        const shareButton = document.createElement('button');
        shareButton.textContent = 'Share Article';
        shareButton.addEventListener('click', () => {
            const articleUrl = window.location.href;
            const shareText = `Check out this article: ${headline}\n${articleUrl}`;
            navigator.clipboard.writeText(shareText).then(() => {
                alert('Article link copied to clipboard!');
            }).catch(err => {
                console.error('Failed to copy: ', err);
            });
        });
        articleSection.appendChild(shareButton);
    }
});