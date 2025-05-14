// static/js/script.js

// Get references to the HTML elements we need to update
const emaScoreText = document.querySelector('.ema-score-text');
const semiCircleFill = document.querySelector('.semi-circle-fill');
const totalProcessedSpan = document.getElementById('total-processed');
const posCountSpan = document.getElementById('pos-count');
const neuCountSpan = document.getElementById('neu-count');
const negCountSpan = document.getElementById('neg-count');
const recentCommentsList = document.getElementById('recent-comments-list');

// Function to fetch data from the backend API
async function fetchSentimentData() {
    try {
        // Make a GET request to the Flask API endpoint
        const response = await fetch('/api/sentiment_data');

        // Check if the request was successful
        if (!response.ok) {
            console.error(`HTTP error! status: ${response.status}`);
            return null;
        }

        // Parse the JSON response
        const data = await response.json();
        return data;

    } catch (error) {
        console.error('Error fetching sentiment data:', error);
        return null;
    }
}

// Function to update the EMA semi-circle gauge
function updateEmaGauge(clampedScore) {
    emaScoreText.textContent = clampedScore.toFixed(1); // Display with 1 decimal place

    // Calculate the percentage to fill (0-100%)
    const fillPercentage = clampedScore;
    
    // Create a clip path that fills from left to right based on the score
    // This creates a polygon that shows only a portion of the gradient
    // The polygon coordinates are:
    // (0,0) = top-left corner
    // (fillPercentage%, 0) = top edge, depending on score
    // (fillPercentage%, 100%) = bottom edge, depending on score
    // (0, 100%) = bottom-left corner
    
    const clipPath = `polygon(0 0, ${fillPercentage}% 0, ${fillPercentage}% 100%, 0 100%)`;
    
    // Apply the clip path to the semi-circle fill element
    semiCircleFill.style.clipPath = clipPath;
    semiCircleFill.style.webkitClipPath = clipPath;
}

// Function to update the sentiment counts and total processed
function updateStats(counts, totalProcessed) {
    totalProcessedSpan.textContent = totalProcessed;
    posCountSpan.textContent = counts.POS || 0; // Use 0 if key is missing
    neuCountSpan.textContent = counts.NEU || 0;
    negCountSpan.textContent = counts.NEG || 0;
}

// Function to update the list of recent comments
function updateRecentComments(comments) {
    // Clear the current list
    recentCommentsList.innerHTML = '';

    // Add each recent comment to the list
    comments.forEach(comment => {
        const commentItem = document.createElement('div');
        commentItem.classList.add('comment-item');

        // Add class based on sentiment label for styling (red, yellow, green background)
        if (comment.label === 'POS') {
            commentItem.classList.add('positive');
        } else if (comment.label === 'NEU') {
            commentItem.classList.add('neutral');
        } else if (comment.label === 'NEG') {
            commentItem.classList.add('negative');
        }

        // Create a div for the comment text
        const commentTextDiv = document.createElement('div');
        commentTextDiv.classList.add('comment-text'); // Use the existing comment-text class for styling
        commentTextDiv.textContent = comment.text; // Use comment.text from backend data

        // Create a div for the comment score
        const commentScoreDiv = document.createElement('div');
        commentScoreDiv.classList.add('comment-score'); // Use the existing comment-score class for styling
        commentScoreDiv.textContent = comment.comment_score.toFixed(1); // Use comment.comment_score from backend data

        // Append the text div and score div to the comment item
        commentItem.appendChild(commentTextDiv);
        commentItem.appendChild(commentScoreDiv);


        // Add the comment item to the list
        recentCommentsList.appendChild(commentItem);
    });
}

// Main function to periodically fetch and update the dashboard
async function updateDashboard() {
    const data = await fetchSentimentData();

    if (data) {
        // Update EMA gauge
        updateEmaGauge(data.ema_score);

        // Update stats
        updateStats(data.sentiment_counts, data.total_processed);

        // Update recent comments list
        updateRecentComments(data.recent_comments);
    }
}

// Set up a timer to update the dashboard periodically (e.g., every 1 second)
const updateInterval = 1000; // milliseconds
setInterval(updateDashboard, updateInterval);

// Initial dashboard update when the page loads
updateDashboard();
