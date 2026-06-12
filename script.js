/**
 * Social Media Sentiment Analysis Project - Main JavaScript
 * This file handles all the interactive functionality of the sentiment analysis demo page
 * including smooth scrolling, sentiment analysis, animations, and mobile menu.
 * @author Social Media Sentiment Analysis Team
 * @version 1.0.0
 */

// Initialize all components when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Initialize all interactive elements
        initSmoothScrolling();
        initDemoFunctionality();
        initAnimations();
        initMobileMenu();
        console.log('Application initialized successfully');
    } catch (error) {
        console.error('Error initializing application:', error);
        showNotification('There was an error initializing the application. Please refresh the page.', 'error');
    }
});

/**
 * Initializes smooth scrolling functionality for navigation links
 * Prevents default anchor behavior and smoothly scrolls to target sections
 * @returns {void}
 */
function initSmoothScrolling() {
    try {
        const navLinks = document.querySelectorAll('nav a');
        
        if (!navLinks || navLinks.length === 0) {
            console.warn('No navigation links found for smooth scrolling');
            return;
        }
        
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                if (!targetId) {
                    console.warn('Navigation link has no href attribute');
                    return;
                }
                
                const targetSection = document.querySelector(targetId);
                
                if (targetSection) {
                    // Calculate offset based on header height
                    const headerOffset = 80;
                    const elementPosition = targetSection.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                    
                    // Use scrollTo with smooth behavior for modern browsers
                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                } else {
                    console.warn(`Target section ${targetId} not found in the document`);
                }
            });
        });
        
        console.log('Smooth scrolling initialized successfully');
    } catch (error) {
        console.error('Error initializing smooth scrolling:', error);
    }
}

// Demo functionality for sentiment analysis
function initDemoFunctionality() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const tweetInput = document.getElementById('tweet-input');
    const resultContainer = document.getElementById('result-container');
    const loadingIndicator = document.getElementById('loading-indicator');
    const resultDisplay = document.getElementById('result-display');
    const sentimentIcon = document.getElementById('sentiment-icon');
    const sentimentLabel = document.getElementById('sentiment-label');
    const confidenceInfo = document.getElementById('confidence-info');
    const scoresGrid = document.getElementById('sentiment-scores-grid');

    // API endpoint
    const host = window.location.hostname;
    const isLocalHost = host === 'localhost' || host === '127.0.0.1' || host === '::1';
    const API_HOST = isLocalHost ? '127.0.0.1' : host;
    const API_URL = `http://${API_HOST}:8001/api/analyze`;

    // Sample posts for demo (3-class)
    const sampleTweets = {
        positive: "I absolutely love this new product! It's amazing!",
        negative: "This is absolutely terrible, I'm so disappointed.",
        neutral: "It works as expected. Nothing special to mention."
    };

    // Add sample post buttons
    const sampleButtonsContainer = document.createElement('div');
    sampleButtonsContainer.className = 'flex flex-wrap gap-2 mb-4';
    let buttonsHTML = '';
    const sentimentColors = {
        positive: 'green',
        negative: 'red',
        neutral: 'gray'
    };
    for (const sentiment in sampleTweets) {
        const color = sentimentColors[sentiment] || 'gray';
        buttonsHTML += `<button class="px-3 py-1 bg-${color}-100 text-${color}-800 rounded text-sm sample-tweet" data-type="${sentiment}">Sample ${sentiment}</button>`;
    }
    sampleButtonsContainer.innerHTML = buttonsHTML;
    
    tweetInput.parentNode.insertBefore(sampleButtonsContainer, tweetInput);

    // Add event listeners to sample buttons
    document.querySelectorAll('.sample-tweet').forEach(button => {
        button.addEventListener('click', function() {
            const type = this.getAttribute('data-type');
            tweetInput.value = sampleTweets[type];
            resultContainer.classList.add('hidden');
        });
    });

    // Analyze button functionality
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', function() {
            const tweet = tweetInput.value.trim();
            if (tweet === '') {
                showNotification('Please enter a post to analyze', 'error');
                return;
            }
            analyzeSentiment(tweet);
        });
    }

    /**
     * Analyzes sentiment by sending a request to the backend API.
     * @param {string} tweet - The post text to analyze.
     */
    async function analyzeSentiment(tweet) {
        resultContainer.classList.remove('hidden');
        loadingIndicator.style.display = 'block';
        resultDisplay.style.display = 'none';

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: tweet })
            });

            if (!response.ok) {
                // Gracefully handle non-2xx responses that may return HTML instead of JSON
                let message = `API request failed with status ${response.status}`;
                try {
                    const ct = response.headers.get('content-type') || '';
                    if (ct.includes('application/json')) {
                        const errorData = await response.json();
                        if (errorData && errorData.error) {
                            message = errorData.error;
                        }
                    } else {
                        const text = await response.text();
                        if (text) {
                            message = text.slice(0, 200);
                        }
                    }
                } catch (e) {
                    // Ignore parse errors and keep default message
                }
                throw new Error(`${message}. Switching to demo mode.`);
            }

            const data = await response.json();
            updateResultUI(data);

        } catch (error) {
            console.error('Error during sentiment analysis:', error);
            showNotification('API unavailable. Switching to demo mode.', 'warning');
            // Fallback to demo mode if API fails
            runDemoMode();
        } finally {
            loadingIndicator.style.display = 'none';
            resultDisplay.style.display = 'block';
            resultContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    /**
     * Fallback function to show random results if the API is down.
     */
    function runDemoMode() {
        const demoSentiments = ['positive', 'negative', 'neutral'];
        const randomSentiment = demoSentiments[Math.floor(Math.random() * demoSentiments.length)];
        
        let total = 100;
        const scores = { positive: 0, negative: 0, neutral: 0 };
        scores[randomSentiment] = Math.floor(Math.random() * 50) + 50; // 50-99
        total -= scores[randomSentiment];

        // Distribute the rest
        while (total > 0) {
            const s = demoSentiments[Math.floor(Math.random() * demoSentiments.length)];
            const val = Math.min(total, Math.floor(Math.random() * total) + 1);
            scores[s] += val;
            total -= val;
        }

        updateResultUI({ sentiment: randomSentiment, scores: scores });
    }

    /**
     * Updates the UI with sentiment analysis results from the API.
     * @param {object} data - The data object from the API, containing sentiment and scores.
     */
    function updateResultUI(data) {
        const { sentiment, scores } = data;
        const highestSentiment = sentiment;

        // Map sentiments to colors and icons (3-class)
        const sentimentDetails = {
            positive: { color: 'green', icon: '😊' },
            negative: { color: 'red', icon: '😠' },
            neutral: { color: 'gray', icon: '😐' }
        };

        const details = sentimentDetails[highestSentiment] || { color: 'gray', icon: '📊' };
        
        sentimentIcon.innerHTML = details.icon;
        sentimentLabel.textContent = `This text is primarily ${highestSentiment} (${scores[highestSentiment]}%)!`;
        sentimentLabel.className = `text-2xl font-bold text-${details.color}-600`;

        // Update confidence info
        const confidence = scores[highestSentiment];
        if (confidence > 70) {
            confidenceInfo.textContent = `High confidence prediction (${confidence}% certainty)`;
        } else if (confidence > 50) {
            confidenceInfo.textContent = `Moderate confidence prediction (${confidence}% certainty)`;
        } else {
            confidenceInfo.textContent = `Low confidence prediction (${confidence}% certainty)`;
        }
        confidenceInfo.style.display = 'block';

        // Dynamically create and update score bars
        scoresGrid.innerHTML = ''; // Clear previous scores
        for (const s in scores) {
            const score = scores[s];
            const detail = sentimentDetails[s] || { color: 'gray' };
            const scoreElement = `
                <div class="text-center">
                    <div class="text-lg font-semibold mb-1 capitalize">${s}</div>
                    <div class="text-${detail.color}-500 font-bold">${score}%</div>
                    <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
                        <div class="bg-${detail.color}-500 h-2 rounded-full" style="width: ${score}%"></div>
                    </div>
                </div>
            `;
            scoresGrid.innerHTML += scoreElement;
        }
    }
}

// Animations for page elements
function initAnimations() {
    // Animate elements when they come into view
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.animate-on-scroll');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementPosition < windowHeight - 100) {
                element.classList.add('animated');
            }
        });
    };
    
    // Add animation classes to elements
    document.querySelectorAll('.card-hover').forEach(card => {
        card.classList.add('animate-on-scroll');
    });
    
    document.querySelectorAll('section > .container > h2').forEach(heading => {
        heading.classList.add('animate-on-scroll');
    });
    
    // Run on scroll
    window.addEventListener('scroll', animateOnScroll);
    
    // Run once on page load
    animateOnScroll();
}

// Mobile menu functionality
function initMobileMenu() {
    const menuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (menuButton && mobileMenu) {
        menuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
}

// Notification system
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg transform transition-all duration-500 translate-y-[-100px] opacity-0`;
    
    // Set style based on type
    switch(type) {
        case 'success':
            notification.classList.add('bg-green-500', 'text-white');
            break;
        case 'error':
            notification.classList.add('bg-red-500', 'text-white');
            break;
        case 'warning':
            notification.classList.add('bg-yellow-500', 'text-white');
            break;
        default:
            notification.classList.add('bg-blue-500', 'text-white');
    }
    
    // Set content
    notification.innerHTML = message;
    
    // Add to DOM
    document.body.appendChild(notification);
    
    // Trigger animation
    setTimeout(() => {
        notification.classList.remove('translate-y-[-100px]', 'opacity-0');
        notification.classList.add('translate-y-0', 'opacity-100');
    }, 10);
    
    // Remove after delay
    setTimeout(() => {
        notification.classList.remove('translate-y-0', 'opacity-100');
        notification.classList.add('translate-y-[-100px]', 'opacity-0');
        
        // Remove from DOM after animation
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 500);
    }, 3000);
}
