// DOM Elements - Welcome Screen
const welcomeContainer = document.getElementById('welcome-container');
const initialMessageInput = document.getElementById('initial-message-input');
const initialSendButton = document.getElementById('initial-send-button');
const exampleChips = document.querySelectorAll('.example-chip');

// DOM Elements - Chat Interface
const chatContainer = document.getElementById('chat-container');
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const resetButton = document.getElementById('reset-button');
const typingIndicator = document.getElementById('typing-indicator');
const newChatButton = document.getElementById('new-chat-button');

// State
let conversationId = null;
let isFirstMessage = true;
let isTyping = false;
let lastTypingTime = 0;

// Event Listeners - Welcome Screen
initialSendButton.addEventListener('click', handleInitialMessage);
initialMessageInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        handleInitialMessage();
    }
});

// Event Listeners - Example Questions
exampleChips.forEach(chip => {
    chip.addEventListener('click', function() {
        const question = this.getAttribute('data-question');
        initialMessageInput.value = question;
        // Add a pulse animation to the input
        initialMessageInput.classList.add('pulse-animation');
        // Focus and trigger a small delay to show the question before sending
        initialMessageInput.focus();
        setTimeout(() => {
            initialMessageInput.classList.remove('pulse-animation');
            handleInitialMessage();
        }, 400);
    });
});

// Event Listeners - Chat Interface
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault(); // Prevent default to avoid newline
        sendMessage();
    }
});

// Allow shift+enter for new lines
messageInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.shiftKey) {
        // Let the new line happen naturally
    }
});

// Typing indicator for input field - This is a UI enhancement, not actually sending typing status to server
messageInput.addEventListener('input', function() {
    // Just auto-resize the textarea for now
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

resetButton.addEventListener('click', resetConversation);
newChatButton.addEventListener('click', startNewChat);

// Auto-resize textarea as user types
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// Focus the input field when the page loads
window.addEventListener('load', () => {
    initialMessageInput.focus();
    
    // Add animation classes to features
    const features = document.querySelectorAll('.feature');
    features.forEach((feature, index) => {
        feature.style.animationDelay = `${0.1 * (index + 1)}s`;
    });
    
    // Setup parallax effect for the welcome screen
    document.addEventListener('mousemove', handleParallax);
});

/**
 * Handle parallax effect for welcome screen
 * @param {Event} e - The mouse move event
 */
function handleParallax(e) {
    const welcomeHeader = document.querySelector('.welcome-header');
    if (!welcomeHeader) return;
    
    const speed = 0.01;
    const x = (window.innerWidth / 2 - e.pageX) * speed;
    const y = (window.innerHeight / 2 - e.pageY) * speed;
    
    welcomeHeader.style.transform = `translateX(${x}px) translateY(${y}px)`;
    
    // Also apply subtle effect to welcome card
    const welcomeCard = document.querySelector('.welcome-card');
    if (welcomeCard) {
        welcomeCard.style.transform = `translateX(${x * -0.5}px) translateY(${y * -0.5}px)`;
    }
}

/**
 * Handle the initial message from the welcome screen
 */
function handleInitialMessage() {
    const message = initialMessageInput.value.trim();
    
    if (message === '') return;
    
    // Add a smooth transition effect
    welcomeContainer.style.opacity = '0';
    welcomeContainer.style.transform = 'translateY(-20px)';
    welcomeContainer.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    
    // After animation completes, hide welcome and show chat
    setTimeout(() => {
        // Switch from welcome view to chat view
        welcomeContainer.classList.add('d-none');
        chatContainer.classList.remove('d-none');
        
        // Fade in the chat container
        chatContainer.style.opacity = '0';
        chatContainer.style.transform = 'translateY(20px)';
        
        // Trigger reflow
        void chatContainer.offsetWidth;
        
        chatContainer.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        chatContainer.style.opacity = '1';
        chatContainer.style.transform = 'translateY(0)';
        
        // Start the conversation with the initial message
        // Add user message to chat
        addMessage(message, 'user');
        
        // Show typing indicator
        typingIndicator.style.display = 'flex';
        
        // Send message to API
        sendToAPI(message);
        
        // Focus the chat input for continuing the conversation
        messageInput.focus();
    }, 500);
}

/**
 * Send a message to the chatbot
 */
function sendMessage() {
    const message = messageInput.value.trim();
    
    if (message === '') return;
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear and reset input field height
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Show typing indicator with animation
    typingIndicator.style.display = 'flex';
    typingIndicator.style.opacity = '0';
    
    // Trigger animation
    setTimeout(() => {
        typingIndicator.style.transition = 'opacity 0.3s ease';
        typingIndicator.style.opacity = '1';
    }, 10);
    
    // Add a nice ripple effect to the send button
    addRippleEffect(sendButton);
    
    // Send message to API
    sendToAPI(message);
}

/**
 * Add ripple effect to button
 * @param {HTMLElement} button - The button element
 */
function addRippleEffect(button) {
    // Create ripple element
    const ripple = document.createElement('span');
    ripple.classList.add('ripple-effect');
    
    // Calculate size (should be at least as large as the button)
    const size = Math.max(button.offsetWidth, button.offsetHeight);
    ripple.style.width = ripple.style.height = `${size}px`;
    
    // Position ripple in center of button
    const rect = button.getBoundingClientRect();
    ripple.style.left = `${rect.width / 2 - size / 2}px`;
    ripple.style.top = `${rect.height / 2 - size / 2}px`;
    
    // Add ripple to button
    button.appendChild(ripple);
    
    // Remove ripple after animation
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

/**
 * Send message to the API
 * @param {string} message - The message to send
 */
function sendToAPI(message) {
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            conversation_id: conversationId,
            is_first_message: isFirstMessage
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Hide typing indicator
        typingIndicator.style.display = 'none';
        
        // Add bot message to chat
        addMessage(data.message, 'bot');
        
        // Store conversation ID if it's new
        if (!conversationId) {
            conversationId = data.conversation_id;
        }
        
        // No longer first message
        if (isFirstMessage) {
            isFirstMessage = false;
        }
        
        // Scroll to the latest message
        scrollToLatest();
    })
    .catch(error => {
        console.error('Error:', error);
        typingIndicator.style.display = 'none';
        
        // Show error message
        addErrorMessage('Sorry, there was an error processing your request. Please try again.');
    });
}

/**
 * Add a message to the chat UI
 * @param {string} content - Message content
 * @param {string} sender - Message sender ('user' or 'bot')
 */
function addMessage(content, sender) {
    // Create message container
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    
    // Initially set opacity to 0 for animation
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = sender === 'user' ? 'translateX(20px)' : 'translateX(-20px)';
    
    // Create message content container
    const contentDiv = document.createElement('div');
    contentDiv.classList.add('message-content');
    
// Add icon with appropriate icon
const iconSpan = document.createElement('i');
iconSpan.classList.add('fas');
if (sender === 'user') {
    iconSpan.classList.add('fa-user');
} else {
    // Instead of fa-robot, we'll add a custom class for the logo
    iconSpan.classList.add('fa-logo');
}
iconSpan.classList.add('message-icon');
    
    // Add bubble with text, handling markdown
    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    
    // Process content to handle markdown
    content = processMarkdown(content);
    bubble.innerHTML = content;
    
    // Add time
    const timeDiv = document.createElement('div');
    timeDiv.classList.add('message-time');
    
    // Format current time
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    timeDiv.textContent = `${hours}:${minutes}`;
    
    // Add message actions for bot messages (copy, thumbs up/down)
    if (sender === 'bot') {
        const actionsDiv = document.createElement('div');
        actionsDiv.classList.add('message-actions');
        
        // Copy button
        const copyBtn = document.createElement('button');
        copyBtn.classList.add('action-btn');
        copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy';
        copyBtn.addEventListener('click', function() {
            copyToClipboard(content.replace(/<[^>]*>/g, ''));
            
            // Show feedback
            copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
            setTimeout(() => {
                copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy';
            }, 1500);
        });
        
        // Thumbs up button
        const thumbsUpBtn = document.createElement('button');
        thumbsUpBtn.classList.add('action-btn');
        thumbsUpBtn.innerHTML = '<i class="fas fa-thumbs-up"></i>';
        thumbsUpBtn.addEventListener('click', function() {
            // Toggle active state for this button
            thumbsUpBtn.classList.toggle('active');
            // Remove active state from thumbs down if it's active
            if (thumbsDownBtn.classList.contains('active')) {
                thumbsDownBtn.classList.remove('active');
            }
            // Here you would typically send feedback to your backend
        });
        
        // Thumbs down button
        const thumbsDownBtn = document.createElement('button');
        thumbsDownBtn.classList.add('action-btn');
        thumbsDownBtn.innerHTML = '<i class="fas fa-thumbs-down"></i>';
        thumbsDownBtn.addEventListener('click', function() {
            // Toggle active state for this button
            thumbsDownBtn.classList.toggle('active');
            // Remove active state from thumbs up if it's active
            if (thumbsUpBtn.classList.contains('active')) {
                thumbsUpBtn.classList.remove('active');
            }
            // Here you would typically send feedback to your backend
        });
        
        actionsDiv.appendChild(copyBtn);
        actionsDiv.appendChild(thumbsUpBtn);
        actionsDiv.appendChild(thumbsDownBtn);
        
        messageDiv.appendChild(actionsDiv);
    }
    
    // Assemble all parts
    contentDiv.appendChild(iconSpan);
    contentDiv.appendChild(bubble);
    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timeDiv);
    
    // Add to chat container
    chatMessages.appendChild(messageDiv);
    
    // Trigger animation after a small delay
    setTimeout(() => {
        messageDiv.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateX(0)';
    }, 50);
    
    // Scroll to the bottom
    scrollToLatest();
    
    // If it's a bot message, enhance code blocks with syntax highlighting
    if (sender === 'bot') {
        // Run syntax highlighting on code blocks that were just added
        document.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 */
function copyToClipboard(text) {
    // Create a temporary textarea element to copy from
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'absolute';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    
    // Select and copy the text
    textarea.select();
    document.execCommand('copy');
    
    // Remove the temporary textarea
    document.body.removeChild(textarea);
}

/**
 * Process markdown in messages using marked.js and highlight.js
 * @param {string} text - The text to process
 * @returns {string} - HTML with markdown formatting
 */
function processMarkdown(text) {
    // Configure marked with highlight.js
    marked.setOptions({
        highlight: function(code, lang) {
            // If a language is specified and highlight.js supports it
            if (lang && hljs.getLanguage(lang)) {
                try {
                    return hljs.highlight(code, { language: lang }).value;
                } catch (err) {}
            }
            
            // Use auto-detection if no language is specified
            try {
                return hljs.highlightAuto(code).value;
            } catch (err) {}
            
            // Return as-is if highlighting fails
            return code;
        },
        breaks: true,
        gfm: true,
        smartLists: true,
        smartypants: true,
        xhtml: true
    });
    
    // Process the markdown
    let html = marked.parse(text);
    
    // Enhance code blocks with copy button and language label
    html = enhanceCodeBlocks(html);
    
    // Enhance tables with responsive wrapper and styling
    html = enhanceTables(html);
    
    // Enhance links to open in new tab
    html = enhanceLinks(html);
    
    return html;
}

/**
 * Enhance links to open in new tab and add security attributes
 * @param {string} html - HTML content
 * @returns {string} - Enhanced HTML
 */
function enhanceLinks(html) {
    const linkRegex = /<a\s+(?:[^>]*?\s+)?href=(["'])(.*?)\1/g;
    
    return html.replace(linkRegex, function(match, quote, url) {
        // Only modify external links (those that start with http)
        if (url.startsWith('http')) {
            return `<a href=${quote}${url}${quote} target="_blank" rel="noopener noreferrer"`;
        }
        return match;
    });
}

/**
 * Enhance code blocks with copy button and language label
 * @param {string} html - HTML with code blocks
 * @returns {string} - Enhanced HTML
 */
function enhanceCodeBlocks(html) {
    // RegExp to match code blocks with or without language specification
    const codeBlockRegex = /<pre><code class="language-([a-zA-Z0-9]+)?">([\s\S]*?)<\/code><\/pre>/g;
    
    return html.replace(codeBlockRegex, function(match, language, code) {
        const langLabel = language ? `<div class="code-lang-label">${language}</div>` : '';
        const uniqueId = 'code-' + Math.random().toString(36).substring(2, 9);
        
        return `
            <div class="code-block-container">
                <div class="code-header">
                    ${langLabel}
                    <button class="copy-code-btn" onclick="copyCode('${uniqueId}')">
                        <i class="fas fa-copy"></i> Copy
                    </button>
                </div>
                <pre class="code-block" id="${uniqueId}"><code class="language-${language || ''}">${code}</code></pre>
            </div>
        `;
    });
}

/**
 * Enhance tables with responsive wrapper
 * @param {string} html - HTML with tables
 * @returns {string} - Enhanced HTML
 */
function enhanceTables(html) {
    const tableRegex = /<table>([\s\S]*?)<\/table>/g;
    
    return html.replace(tableRegex, function(match, tableContent) {
        return `
            <div class="table-responsive">
                <table class="markdown-table">${tableContent}</table>
            </div>
        `;
    });
}

/**
 * Copy code to clipboard
 * @param {string} elementId - The ID of the code block
 */
function copyCode(elementId) {
    const codeBlock = document.getElementById(elementId);
    
    // Get the text content properly - need to get it from the code element inside the pre
    const codeElement = codeBlock.querySelector('code');
    const code = codeElement ? codeElement.innerText || codeElement.textContent : codeBlock.innerText || codeBlock.textContent;
    
    // Create a temporary textarea element to copy from
    const textarea = document.createElement('textarea');
    textarea.value = code;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'absolute';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    
    // Select and copy the text
    textarea.select();
    document.execCommand('copy');
    
    // Remove the temporary textarea
    document.body.removeChild(textarea);
    
    // Visual feedback on the button
    const copyBtn = codeBlock.parentNode.querySelector('.copy-code-btn');
    const originalText = copyBtn.innerHTML;
    
    copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
    setTimeout(function() {
        copyBtn.innerHTML = originalText;
    }, 1500);
}

/**
 * Add an error message to the chat
 * @param {string} message - Error message
 */
function addErrorMessage(message) {
    // Create error message element
    const errorDiv = document.createElement('div');
    errorDiv.classList.add('alert', 'alert-danger', 'mt-2', 'mb-2');
    errorDiv.textContent = message;
    
    // Add to chat container
    chatMessages.appendChild(errorDiv);
    
    // Scroll to the bottom
    scrollToLatest();
    
    // Remove after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

/**
 * Reset the conversation
 */
function resetConversation() {
    if (confirm('Are you sure you want to reset this conversation? This cannot be undone.')) {
        fetch('/api/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Clear the chat UI
            chatMessages.innerHTML = '';
            
            // Reset conversation ID and first message flag
            conversationId = null;
            isFirstMessage = true;
            
            // Add system message about reset
            addMessage('Conversation has been reset. How can I help you today? 😊', 'bot');
        })
        .catch(error => {
            console.error('Error:', error);
            addErrorMessage('Error resetting conversation. Please try again.');
        });
    }
}

/**
 * Smoothly scroll to the latest message
 */
function scrollToLatest() {
    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
}

/**
 * Add new particle effects dynamically
 */
function addParticles() {
    const particlesContainer = document.querySelector('.particles-container');
    if (!particlesContainer) return;
    
    // Add 3 more particles
    for (let i = 0; i < 3; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        // Random position
        particle.style.top = `${Math.random() * 100}%`;
        particle.style.left = `${Math.random() * 100}%`;
        
        // Random size
        const size = 2 + Math.random() * 4;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        
        // Random animation duration
        particle.style.animationDuration = `${20 + Math.random() * 20}s`;
        
        // Random delay
        particle.style.animationDelay = `${Math.random() * 5}s`;
        
        // Random opacity
        particle.style.opacity = `${0.2 + Math.random() * 0.3}`;
        
        particlesContainer.appendChild(particle);
    }
}

/**
 * Start a new chat (clears UI and returns to welcome screen)
 */
function startNewChat() {
    // Add exit animation to chat container
    chatContainer.style.opacity = '0';
    chatContainer.style.transform = 'translateY(20px)';
    chatContainer.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    
    setTimeout(() => {
        // Reset conversation ID and first message flag
        conversationId = null;
        isFirstMessage = true;
        
        // Clear chat messages
        chatMessages.innerHTML = '';
        
        // Show welcome screen, hide chat interface
        chatContainer.classList.add('d-none');
        welcomeContainer.classList.remove('d-none');
        
        // Fade in welcome container
        welcomeContainer.style.opacity = '0';
        welcomeContainer.style.transform = 'translateY(-20px)';
        
        // Trigger reflow
        void welcomeContainer.offsetWidth;
        
        welcomeContainer.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        welcomeContainer.style.opacity = '1';
        welcomeContainer.style.transform = 'translateY(0)';
        
        // Reset inputs
        messageInput.value = '';
        messageInput.style.height = 'auto';
        initialMessageInput.value = '';
        
        // Focus on initial input
        initialMessageInput.focus();
    }, 500);
}

// Add copyCode to window object so it can be called from inline onclick handlers
window.copyCode = copyCode;

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Create more particle effects
    addParticles();
    
    // Add special CSS for ripple effect
    const style = document.createElement('style');
    style.textContent = `
        .ripple-effect {
            position: absolute;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        }
        
        @keyframes ripple {
            to {
                transform: scale(2.5);
                opacity: 0;
            }
        }
        
        .pulse-animation {
            animation: pulse 0.4s ease-in-out;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.03); }
            100% { transform: scale(1); }
        }
    `;
    document.head.appendChild(style);
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});










































/**
 * Flooky AI Donation Page JavaScript
 * This file handles the interactive elements of the donation page
 */

// Update your document.addEventListener('DOMContentLoaded', ...) function in donation.js like this:

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // PayPal donation amount selection
    initPayPalDonation();
    
    // Ethereum donation handling
    initEthereumDonation();
    
    // Bizum donation handling
    initBizumDonation();
    
    // Generate QR code for Ethereum wallet
    generateEthQRCode();
    
    // Initialize FAQ accordion if exists
    initFaqAccordion();
    
    // Add subtle animation effects
    addAnimationEffects();
});
/**
 * Initialize PayPal donation functionality
 */
function initPayPalDonation() {
    const amountOptions = document.querySelectorAll('.amount-option');
    const customAmountContainer = document.querySelector('.custom-amount-container');
    const customAmountInput = document.querySelector('.custom-amount-input');
    const paypalAmountInput = document.getElementById('paypal-amount');
    const paypalForm = document.getElementById('paypal-form');
    const paypalDonateBtn = document.getElementById('paypal-donate-btn');
    const paypalCmd = document.getElementById('paypal-cmd');
    const frequencyOptions = document.querySelectorAll('input[name="paypalFrequency"]');

    if (!amountOptions.length || !paypalForm) return;

    // Handle amount selection
    amountOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove active class from all options
            amountOptions.forEach(opt => opt.classList.remove('active'));
            
            // Add active class to clicked option
            this.classList.add('active');
            
            // Handle custom amount
            if (this.dataset.amount === 'custom') {
                customAmountContainer.style.display = 'block';
                paypalAmountInput.value = customAmountInput.value || '10';
            } else {
                customAmountContainer.style.display = 'none';
                paypalAmountInput.value = this.dataset.amount;
            }
        });
    });

    // Handle custom amount input
    if (customAmountInput) {
        customAmountInput.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (value && value > 0) {
                paypalAmountInput.value = value.toFixed(2);
            } else {
                this.value = '';
                paypalAmountInput.value = '10.00';
            }
        });
    }

    // Handle frequency selection
    frequencyOptions.forEach(option => {
        option.addEventListener('change', function() {
            if (this.value === 'monthly') {
                paypalCmd.value = '_xclick-subscriptions';
                // Add subscription-specific fields
                // This is simplified - PayPal requires specific parameters for subscriptions
                const recurringInput = document.createElement('input');
                recurringInput.type = 'hidden';
                recurringInput.name = 'a3';
                recurringInput.value = paypalAmountInput.value;
                paypalForm.appendChild(recurringInput);
                
                const periodInput = document.createElement('input');
                periodInput.type = 'hidden';
                periodInput.name = 'p3';
                periodInput.value = '1';
                paypalForm.appendChild(periodInput);
                
                const unitInput = document.createElement('input');
                unitInput.type = 'hidden';
                unitInput.name = 't3';
                unitInput.value = 'M';
                paypalForm.appendChild(unitInput);
                
                const srcInput = document.createElement('input');
                srcInput.type = 'hidden';
                srcInput.name = 'src';
                srcInput.value = '1';
                paypalForm.appendChild(srcInput);
            } else {
                paypalCmd.value = '_donations';
                // Remove subscription-specific fields if they exist
                const subscriptionFields = ['a3', 'p3', 't3', 'src'];
                subscriptionFields.forEach(field => {
                    const input = paypalForm.querySelector(`input[name="${field}"]`);
                    if (input) paypalForm.removeChild(input);
                });
            }
        });
    });

    // Handle PayPal donation button
    if (paypalDonateBtn) {
        paypalDonateBtn.addEventListener('click', function() {
            // Validate amount
            const amount = parseFloat(paypalAmountInput.value);
            if (!amount || amount <= 0) {
                alert('Please enter a valid donation amount.');
                return;
            }
            
            // Create a pulse effect on button click
            this.classList.add('clicked');
            setTimeout(() => {
                this.classList.remove('clicked');
                paypalForm.submit();
            }, 300);
        });
    }
}

/**
 * Initialize Ethereum donation functionality
 */
function initEthereumDonation() {
    const copyEthBtn = document.getElementById('copy-eth-address');
    const ethAddress = document.getElementById('eth-address');
    
    if (!copyEthBtn || !ethAddress) return;
    
    copyEthBtn.addEventListener('click', function() {
        const textToCopy = ethAddress.textContent;
        
        navigator.clipboard.writeText(textToCopy).then(() => {
            // Update tooltip content
            const tooltip = bootstrap.Tooltip.getInstance(copyEthBtn);
            tooltip.hide();
            copyEthBtn.setAttribute('data-bs-original-title', 'Copied!');
            tooltip.show();
            
            // Add visual feedback
            ethAddress.classList.add('highlight-text');
            setTimeout(() => {
                ethAddress.classList.remove('highlight-text');
            }, 1000);
            
            // Reset tooltip after delay
            setTimeout(() => {
                copyEthBtn.setAttribute('data-bs-original-title', 'Copy to clipboard');
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
            alert('Failed to copy address. Please try selecting and copying manually.');
        });
    });

    // Handle MetaMask button if present
    const metamaskBtn = document.querySelector('.btn-outline.metamask');
    if (metamaskBtn) {
        metamaskBtn.addEventListener('click', function(e) {
            // Replace with your actual ETH address
            const ethAddress = document.getElementById('eth-address').textContent;
            
            // Check if MetaMask is installed
            if (typeof window.ethereum !== 'undefined') {
                // Open in MetaMask
                e.preventDefault();
                window.ethereum.request({
                    method: 'eth_sendTransaction',
                    params: [{
                        from: window.ethereum.selectedAddress,
                        to: ethAddress,
                        value: '0x00' // User will input the amount in MetaMask
                    }]
                }).catch(error => {
                    console.error(error);
                    window.open('https://metamask.io/', '_blank');
                });
            } else {
                // Will navigate to MetaMask website as set in the href
                return true;
            }
        });
    }
}


/**
 * Generate a QR code for the Ethereum wallet address
 * This is a placeholder implementation - in production, use a proper QR library
 */
function generateEthQRCode() {
    const qrPlaceholder = document.getElementById('eth-qr-placeholder');
    const qrGrid = document.querySelector('.qr-grid');
    
    if (!qrPlaceholder || !qrGrid) return;
    
    // Clear existing content
    qrGrid.innerHTML = '';
    
    // Create a simple pattern as a placeholder QR code
    // In a real app, you'd use a proper QR code library like qrious or qrcode.js
    for (let i = 0; i < 25; i++) {
        for (let j = 0; j < 25; j++) {
            const cell = document.createElement('div');
            cell.className = 'qr-cell';
            
            // Create a simple pattern for visualization
            if (
                // Corners for QR code positioning markers
                (i < 7 && j < 7) || // Top-left corner
                (i < 7 && j >= 18) || // Top-right corner
                (i >= 18 && j < 7) || // Bottom-left corner
                
                // Inner positioning elements
                (i === 7 && j % 2 === 0) ||
                (j === 7 && i % 2 === 0) ||
                
                // Borders
                (i === 0 || i === 24 || j === 0 || j === 24) ||
                
                // Random data bits for visual effect
                ((i * j) % 4 === 0 && i > 8 && j > 8)
            ) {
                cell.classList.add('qr-cell-filled');
                
                // Add animation delay based on position for a cool loading effect
                cell.style.animationDelay = `${(i + j) * 10}ms`;
            }
            
            qrGrid.appendChild(cell);
        }
    }
    
    // Add animation class after grid is generated
    setTimeout(() => {
        qrPlaceholder.classList.add('qr-loaded');
    }, 100);
}

/**
 * Initialize FAQ accordion functionality if present
 */
function initFaqAccordion() {
    const faqQuestions = document.querySelectorAll('.faq-question');
    
    if (!faqQuestions.length) return;
    
    faqQuestions.forEach(question => {
        question.addEventListener('click', function() {
            const answer = this.nextElementSibling;
            const isActive = this.classList.contains('active');
            
            // Close all other questions
            document.querySelectorAll('.faq-question').forEach(q => {
                if (q !== this) {
                    q.classList.remove('active');
                    q.nextElementSibling.classList.remove('show');
                }
            });
            
            // Toggle current question
            if (isActive) {
                this.classList.remove('active');
                answer.classList.remove('show');
            } else {
                this.classList.add('active');
                answer.classList.add('show');
            }
        });
    });
}

/**
 * Add subtle animation effects to donation page elements
 */
function addAnimationEffects() {
    // Animate benefits cards on scroll
    const benefitItems = document.querySelectorAll('.benefit-item');
    
    if (benefitItems.length) {
        const benefitsObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    // Add staggered animation delay
                    setTimeout(() => {
                        entry.target.classList.add('animate-in');
                    }, index * 150);
                    benefitsObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });
        
        benefitItems.forEach(item => {
            benefitsObserver.observe(item);
        });
    }
    
    // Add pulse effect to donation cards
    const donationCards = document.querySelectorAll('.donation-card');
    if (donationCards.length) {
        setTimeout(() => {
            donationCards.forEach((card, index) => {
                setTimeout(() => {
                    card.classList.add('pulse-attention');
                    setTimeout(() => {
                        card.classList.remove('pulse-attention');
                    }, 1500);
                }, index * 300);
            });
        }, 1000);
    }
}

// Add CSS classes for JS-added animations
document.head.insertAdjacentHTML('beforeend', `
<style>
    .pulse-attention {
        animation: pulseAttention 1.5s ease-in-out;
    }
    
    @keyframes pulseAttention {
        0% { transform: translateY(0); box-shadow: var(--card-shadow); }
        30% { transform: translateY(-8px); box-shadow: var(--hover-shadow); }
        50% { transform: translateY(-10px); box-shadow: var(--hover-shadow); }
        80% { transform: translateY(-4px); box-shadow: var(--hover-shadow); }
        100% { transform: translateY(0); box-shadow: var(--card-shadow); }
    }
    
    .highlight-text {
        background-color: rgba(17, 123, 244, 0.15);
        transition: background-color 0.3s ease;
    }
    
    .qr-cell {
        opacity: 0;
        animation: fadeIn 0.5s forwards;
    }
    
    .qr-loaded .qr-cell {
        opacity: 1;
    }
    
    .btn-donate.clicked {
        transform: scale(0.98);
    }
    
    .benefit-item {
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.5s ease, transform 0.5s ease;
    }
    
    .benefit-item.animate-in {
        opacity: 1;
        transform: translateY(0);
    }
</style>
`);
// Add these functions to your donation.js file

/**
 * Initialize Bizum donation functionality
 */
function initBizumDonation() {
    const copyBizumBtn = document.getElementById('copy-bizum-number');
    const bizumNumber = document.getElementById('bizum-number');
    
    if (!copyBizumBtn || !bizumNumber) return;
    
    copyBizumBtn.addEventListener('click', function() {
        const textToCopy = bizumNumber.textContent;
        
        navigator.clipboard.writeText(textToCopy).then(() => {
            // Update tooltip content
            const tooltip = bootstrap.Tooltip.getInstance(copyBizumBtn);
            tooltip.hide();
            copyBizumBtn.setAttribute('data-bs-original-title', '¡Copiado!');
            tooltip.show();
            
            // Add visual feedback
            bizumNumber.classList.add('highlight-text');
            setTimeout(() => {
                bizumNumber.classList.remove('highlight-text');
            }, 1000);
            
            // Reset tooltip after delay
            setTimeout(() => {
                copyBizumBtn.setAttribute('data-bs-original-title', 'Copiar número');
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
            alert('Error al copiar. Por favor, selecciona y copia manualmente.');
        });
    });
}

// Modify your document.addEventListener('DOMContentLoaded', ...) function
// to include a call to initBizumDonation():

// Add this to the existing DOMContentLoaded function:
// initBizumDonation();

// Add this CSS class if not already present
document.head.insertAdjacentHTML('beforeend', `
<style>
    .highlight-text {
        background-color: rgba(0, 172, 214, 0.2);
        transition: background-color 0.3s ease;
    }
</style>
`);




































/* ============================= Contact Me ====================================== */
/**
 * Flooky AI Contact Page JavaScript
 * This file handles the interactive elements of the contact page
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize copy functionality
    initCopyFunctionality();
    
    // Initialize contact form
    initContactForm();
    
    // Initialize Modern FAQ functionality
    initModernFAQ();
    
    // Add animation effects
    addAnimationEffects();
});

/**
 * Initialize copy to clipboard functionality
 */
function initCopyFunctionality() {
    const copyEmailBtn = document.getElementById('copy-email');
    const emailAddress = document.getElementById('email-address');
    
    if (!copyEmailBtn || !emailAddress) return;
    
    copyEmailBtn.addEventListener('click', function() {
        const textToCopy = emailAddress.textContent;
        
        navigator.clipboard.writeText(textToCopy).then(() => {
            // Update tooltip content
            const tooltip = bootstrap.Tooltip.getInstance(copyEmailBtn);
            tooltip.hide();
            copyEmailBtn.setAttribute('data-bs-original-title', 'Copied!');
            tooltip.show();
            
            // Add visual feedback
            emailAddress.classList.add('highlight-text');
            setTimeout(() => {
                emailAddress.classList.remove('highlight-text');
            }, 1000);
            
            // Reset tooltip after delay
            setTimeout(() => {
                copyEmailBtn.setAttribute('data-bs-original-title', 'Copy to clipboard');
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
            alert('Failed to copy email. Please try selecting and copying manually.');
        });
    });
}

/**
 * Initialize contact form functionality
 */
function initContactForm() {
    const contactForm = document.getElementById('contact-form');
    const formSuccess = document.getElementById('form-success');
    const formError = document.getElementById('form-error');
    
    if (!contactForm) return;
    
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Hide any existing feedback messages
        if (formSuccess) formSuccess.style.display = 'none';
        if (formError) formError.style.display = 'none';
        
        // Get form data
        const formData = new FormData(contactForm);
        const formDataObj = Object.fromEntries(formData.entries());
        
        // Simulate form submission with loading state
        const submitBtn = contactForm.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        
        // Simulate API call delay
        setTimeout(() => {
            // In a real implementation, you would send this data to your backend
            console.log('Form data:', formDataObj);
            
            // For demonstration purposes, we'll always show success
            // In a real implementation, you would check the response from your API
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
            
            if (Math.random() > 0.1) { // 90% success rate for demo
                // Show success message
                if (formSuccess) {
                    formSuccess.style.display = 'flex';
                    contactForm.reset();
                    
                    // Scroll to success message
                    formSuccess.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }
            } else {
                // Show error message
                if (formError) {
                    formError.style.display = 'flex';
                    
                    // Scroll to error message
                    formError.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }
            }
        }, 1500);
    });
}

/**
 * Initialize the modern FAQ accordion functionality
 */
function initModernFAQ() {
    const faqItems = document.querySelectorAll('.modern-faq-item');
    if (!faqItems.length) return;
    
    faqItems.forEach((item, index) => {
        const question = item.querySelector('.modern-faq-question');
        
        if (!question) return;
        
        question.addEventListener('click', () => {
            // Toggle active class on the clicked item
            const isActive = item.classList.contains('active');
            
            // Close all other FAQs
            faqItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove('active');
                }
            });
            
            // Toggle the current FAQ
            if (isActive) {
                item.classList.remove('active');
            } else {
                item.classList.add('active');
            }
        });
        
        // First FAQ is open by default
        if (index === 0) {
            item.classList.add('active');
        }
    });
}

/**
 * Add animation effects to contact page elements
 */
function addAnimationEffects() {
    // Animate social links on hover
    const socialLinks = document.querySelectorAll('.social-link');
    
    socialLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            const icon = this.querySelector('.social-icon');
            if (icon) {
                icon.classList.add('pulse-effect');
                
                setTimeout(() => {
                    icon.classList.remove('pulse-effect');
                }, 1000);
            }
        });
    });
    
    // Add entrance animations for cards
    const contactCards = document.querySelectorAll('.contact-card');
    if (contactCards.length) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.classList.add('animate-in');
                    }, index * 100);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        contactCards.forEach(card => {
            observer.observe(card);
            card.classList.add('pre-animation');
        });
    }
    
    // Add subtle animation to form submit button
    const submitBtn = document.querySelector('.btn-contact.submit');
    if (submitBtn) {
        submitBtn.addEventListener('mouseenter', function() {
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.add('paper-plane-effect');
                
                setTimeout(() => {
                    icon.classList.remove('paper-plane-effect');
                }, 1000);
            }
        });
    }
}

// Add CSS for JavaScript animations
document.head.insertAdjacentHTML('beforeend', `
<style>
    @keyframes pulseEffect {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
    
    .pulse-effect {
        animation: pulseEffect 0.5s ease-in-out;
    }
    
    @keyframes paperPlaneEffect {
        0% { transform: translateX(0); }
        50% { transform: translateX(5px) translateY(-5px) rotate(10deg); }
        100% { transform: translateX(0); }
    }
    
    .paper-plane-effect {
        animation: paperPlaneEffect 0.5s ease-in-out;
    }
    
    .pre-animation {
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.5s ease, transform 0.5s ease;
    }
    
    .animate-in {
        opacity: 1;
        transform: translateY(0);
    }
</style>
`);

// Functionality to handle backend form submission
// This is a placeholder - you'll need to implement the actual backend logic
async function sendContactForm(formData) {
    try {
        // In a real implementation, you would replace this with your actual API endpoint
        const response = await fetch('/api/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to send message');
        }
        
        return { success: true };
    } catch (error) {
        console.error('Error sending form:', error);
        return { success: false, error: error.message };
    }
}

// ============================= Voice Recording ======================================
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let audioButton;
let audioStream; // Variable to store the media stream

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize audio recording button
    audioButton = document.getElementById('audio-button');
    
    if (audioButton) {
        audioButton.addEventListener('click', toggleRecording);
    }
});

// Function to toggle recording state
function toggleRecording() {
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
}

// Function to start voice recording
async function startRecording() {
    audioChunks = [];
    
    try {
        // Get user media stream and store it in audioStream variable
        audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(audioStream);
        
        mediaRecorder.addEventListener('dataavailable', event => {
            audioChunks.push(event.data);
        });
        
        mediaRecorder.addEventListener('stop', processRecording);
        
        mediaRecorder.start();
        isRecording = true;
        
        // Update UI - just change the button appearance
        audioButton.classList.add('recording');
        audioButton.innerHTML = '<i class="fas fa-stop"></i>';
        
        // Disable the text input while recording to avoid confusion
        document.getElementById('message-input').disabled = true;
        document.getElementById('send-button').disabled = false;
        
    } catch (error) {
        console.error('Error accessing the microphone:', error);
        alert('Error: Unable to access microphone. Please check your permissions.');
    }
}

// Function to stop voice recording
function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        // Stop all audio tracks to release the microphone
        if (audioStream) {
            audioStream.getTracks().forEach(track => {
                track.stop();
            });
            audioStream = null;
        }
        
        // Update UI
        audioButton.classList.remove('recording');
        audioButton.classList.add('processing');
        audioButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }
}

// Function to process the recorded audio
async function processRecording() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    
    const formData = new FormData();
    formData.append('audio', audioBlob);
    
    try {
        const response = await fetch('/api/transcribe', {
            method: 'POST',
            body: formData,
        });
        
        const data = await response.json();
        
        // Reset UI
        audioButton.classList.remove('processing');
        audioButton.innerHTML = '<i class="fas fa-microphone"></i>';
        
        // Re-enable the text input and send button
        document.getElementById('message-input').disabled = false;
        document.getElementById('send-button').disabled = false;
        
        if (data.error) {
            alert('Transcription error: ' + data.error);
            return;
        }
        
        // If transcription successful and not empty
        if (data.transcript && data.transcript.trim() !== '') {
            // Set the transcript as the input value
            const messageInput = document.getElementById('message-input');
            messageInput.value = data.transcript;
            
            // Automatically send the message
            sendMessage();
        } else {
            alert('No speech detected. Please try again.');
        }
        
    } catch (error) {
        console.error('Error transcribing audio:', error);
        alert('Error transcribing audio. Please try again.');
        
        // Reset UI on error
        audioButton.classList.remove('processing');
        audioButton.innerHTML = '<i class="fas fa-microphone"></i>';
        
        // Re-enable the text input and send button
        document.getElementById('message-input').disabled = false;
        document.getElementById('send-button').disabled = false;
    }
}


function cleanupAudioStream() {
    if (audioStream) {
        audioStream.getTracks().forEach(track => {
            track.stop();
        });
        audioStream = null;
    }
}

// Add an event listener to clean up when the page is unloaded
window.addEventListener('beforeunload', cleanupAudioStream);

