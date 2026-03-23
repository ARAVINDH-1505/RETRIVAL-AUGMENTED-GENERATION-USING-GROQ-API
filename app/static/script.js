document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const chatForm = document.getElementById('chatForm');
    const queryInput = document.getElementById('queryInput');
    const chatMessages = document.getElementById('chatMessages');
    const sendBtn = document.getElementById('sendBtn');
    
    // Upload Elements
    const uploadForm = document.getElementById('uploadForm');
    const documentInput = document.getElementById('documentInput');
    const fileNameDisplay = document.getElementById('file-name');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadSpinner = document.getElementById('uploadSpinner');
    const uploadStatus = document.getElementById('uploadStatus');
    
    // Document List Elements
    const documentList = document.getElementById('documentList');
    const refreshDocsBtn = document.getElementById('refreshDocsBtn');

    // State Variables
    let isProcessing = false;

    // --- Document Management API Calls ---

    // Fetch and Display Indexed Documents
    const fetchDocuments = async () => {
        try {
            documentList.innerHTML = '<li style="text-align: center; color: var(--text-secondary);"><div class="spinner"></div></li>';
            
            const response = await fetch('/api/documents');
            const docs = await response.json();
            
            documentList.innerHTML = '';
            
            if (docs.length === 0) {
                documentList.innerHTML = '<li style="text-align: center; color: var(--text-secondary); padding: 10px;">No documents indexed yet.</li>';
                return;
            }

            docs.forEach(doc => {
                const li = document.createElement('li');
                li.className = 'document-item';
                
                // Format date
                const uploadDate = new Date(doc.upload_time).toLocaleDateString(undefined, {
                    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                });

                li.innerHTML = `
                    <div class="doc-info">
                        <span class="doc-name" title="${doc.filename}">${doc.filename}</span>
                        <span class="doc-meta">${uploadDate}</span>
                    </div>
                    <button class="delete-btn" onclick="deleteDocument('${doc.id}')" title="Delete from Portal">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                `;
                documentList.appendChild(li);
            });
        } catch (error) {
            console.error('Failed to fetch documents:', error);
            documentList.innerHTML = '<li style="color: var(--danger); text-align: center;">Failed to load docs</li>';
        }
    };

    // Delete Document
    window.deleteDocument = async (id) => {
        if (!confirm('Are you sure you want to delete this document from the RAG timeline?')) return;
        
        try {
            const response = await fetch(`/api/document/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                fetchDocuments();
            } else {
                alert('Failed to delete document.');
            }
        } catch (error) {
            console.error('Delete error:', error);
            alert('Error deleting document.');
        }
    };

    // Initial fetch
    fetchDocuments();
    refreshDocsBtn.addEventListener('click', fetchDocuments);

    // --- File Upload Handling ---
    documentInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileNameDisplay.textContent = e.target.files[0].name;
            fileNameDisplay.style.color = 'var(--portal-green)';
        } else {
            fileNameDisplay.textContent = 'No file selected';
            fileNameDisplay.style.color = 'var(--text-secondary)';
        }
    });

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (documentInput.files.length === 0) return;
        
        const file = documentInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        // UI State
        uploadBtn.disabled = true;
        uploadSpinner.style.display = 'block';
        uploadBtn.querySelector('span').textContent = 'Uploading...';
        uploadStatus.textContent = '';
        uploadStatus.className = 'status-message';
        
        try {
            const response = await fetch('/api/upload_document', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (response.ok) {
                uploadStatus.textContent = data.message || 'Added to the portal! Indexing in background...';
                uploadStatus.classList.add('success');
                uploadForm.reset();
                fileNameDisplay.textContent = 'No file selected';
                fileNameDisplay.style.color = 'var(--text-secondary)';
                
                // Refresh list after brief delay assuming short processing time or at least they see UI reaction
                setTimeout(fetchDocuments, 2000); 
            } else {
                uploadStatus.textContent = data.detail || 'Upload failed.';
                uploadStatus.classList.add('error');
            }
        } catch (error) {
            console.error('Upload Error:', error);
            uploadStatus.textContent = 'Network error occurred.';
            uploadStatus.classList.add('error');
        } finally {
            // Restore UI
            uploadBtn.disabled = false;
            uploadSpinner.style.display = 'none';
            uploadBtn.querySelector('span').textContent = 'Upload to Portal';
        }
    });

    // --- Chat System Integration ---
    
    const scrollToBottom = () => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    const addMessage = (role, content, sources = null) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        
        let avatarIcon = role === 'user' ? 'fa-user-astronaut' : 'fa-robot';
        
        let messageHtml = `
            <div class="avatar"><i class="fa-solid ${avatarIcon}"></i></div>
            <div class="content">
                ${role === 'bot' ? marked.parse(content) : `<p>${content}</p>`}
        `;

        if (sources && sources.length > 0) {
            let sourcesHtml = `
                <div class="sources-container">
                    <strong>References:</strong>
                    <div class="sources-list">
            `;
            // Remove duplicates based on document name
            const uniqueSources = [...new Set(sources.map(s => s.document))];
            
            uniqueSources.forEach(docName => {
                sourcesHtml += `<span class="source-badge"><i class="fa-solid fa-file-lines"></i> ${docName}</span>`;
            });
            sourcesHtml += `</div></div>`;
            messageHtml += sourcesHtml;
        }

        messageHtml += `</div>`;
        messageDiv.innerHTML = messageHtml;
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    };

    const addTypingIndicator = () => {
        const id = 'typing-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.className = `message bot-message`;
        messageDiv.id = id;
        
        messageDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="content typing-indicator">
                <div class="type-dot"></div>
                <div class="type-dot"></div>
                <div class="type-dot"></div>
            </div>
        `;
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
        return id;
    };

    const removeElement = (id) => {
        const el = document.getElementById(id);
        if (el) el.remove();
    };
    
    // Handle submitting a query
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const query = queryInput.value.trim();
        if (!query || isProcessing) return;
        
        // Add user message to UI
        addMessage('user', query);
        queryInput.value = '';
        isProcessing = true;
        sendBtn.disabled = true;
        
        // Add bot typing indicator
        const indicatorId = addTypingIndicator();
        
        // Bot mouth animation trigger
        const botMouth = document.querySelector('.mouth');
        botMouth.style.animationDuration = '0.2s';
        
        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ input1: query })
            });
            
            removeElement(indicatorId);
            
            if (response.ok) {
                const data = await response.json();
                addMessage('bot', data.answer, data.sources);
            } else {
                addMessage('bot', 'Aw jeez... The portal gun is jammed! (Error getting response from the RAG backend).');
            }
        } catch (error) {
            console.error('Chat error:', error);
            removeElement(indicatorId);
            addMessage('bot', 'Wubba lubba dub dub! Network error. Check your inter-galactic connection!');
        } finally {
            isProcessing = false;
            sendBtn.disabled = false;
            botMouth.style.animationDuration = '1s'; // Revert mouth animation
            queryInput.focus();
        }
    });

    // --- Spaceship Animation System ---
    const spaceship = document.getElementById('spaceship');
    
    const startSpaceshipAttack = () => {
        spaceship.style.display = 'block';
        
        // Random starting position off-screen
        const startX = Math.random() > 0.5 ? -300 : window.innerWidth + 300;
        const startY = Math.random() * window.innerHeight;
        
        spaceship.style.left = `${startX}px`;
        spaceship.style.top = `${startY}px`;
        spaceship.style.transform = `scaleX(${startX < 0 ? -1 : 1})`; // face direction
        
        // Move towards the center/target over 1.5 seconds
        setTimeout(() => {
            const targetX = (window.innerWidth / 2) + ((Math.random() - 0.5) * 600);
            const targetY = (window.innerHeight / 2) + ((Math.random() - 0.5) * 400);
            
            spaceship.style.left = `${targetX}px`;
            spaceship.style.top = `${targetY}px`;
            // Add a slight rotation based on direction
            spaceship.style.transform = `scaleX(${targetX > startX ? -1 : 1}) rotate(${(Math.random() - 0.5) * 30}deg)`;

            // Shoot lasers after it arrives
            setTimeout(() => {
                shootLasers(targetX, targetY);
                
                // Fly away after shooting
                setTimeout(() => {
                    const exitX = targetX > (window.innerWidth / 2) ? -400 : window.innerWidth + 400;
                    const exitY = Math.random() * window.innerHeight;
                    spaceship.style.left = `${exitX}px`;
                    spaceship.style.top = `${exitY}px`;
                    spaceship.style.transform = `scaleX(${exitX > targetX ? -1 : 1}) rotate(${(exitY > targetY ? 15 : -15)}deg)`;
                    
                    // Hide after flying off
                    setTimeout(() => {
                        spaceship.style.display = 'none';
                    }, 2000);
                }, 1500);

            }, 1800);
            
        }, 100);
    };

    const shootLasers = (x, y) => {
        // Fire 3-5 rapid lasers
        const numLasers = Math.floor(Math.random() * 3) + 3;
        for (let i = 0; i < numLasers; i++) {
            setTimeout(() => {
                const laser = document.createElement('div');
                laser.className = 'laser-beam';
                // Fire from center of spaceship
                const fireOriginX = x + 125; // half of 250px width
                const fireOriginY = y + 75;  // half of 150px height
                laser.style.left = `${fireOriginX}px`;
                laser.style.top = `${fireOriginY}px`; 
                
                // Random target on the UI
                const targetX = Math.random() * window.innerWidth;
                const targetY = Math.random() * window.innerHeight;
                
                const dx = targetX - fireOriginX;
                const dy = targetY - fireOriginY;
                
                const angle = Math.atan2(dy, dx) * 180 / Math.PI;
                laser.style.setProperty('--angle', `${angle}deg`);
                laser.style.setProperty('--dx', `${dx}px`);
                laser.style.setProperty('--dy', `${dy}px`);
                
                document.body.appendChild(laser);
                
                // Remove laser element after animation and trigger explosion
                setTimeout(() => {
                    laser.remove();
                    createExplosion(targetX, targetY);
                }, 500);
            }, i * 150);
        }
    };

    const createExplosion = (x, y) => {
        const explosion = document.createElement('div');
        explosion.style.position = 'fixed';
        explosion.style.left = `${x - 25}px`;
        explosion.style.top = `${y - 25}px`;
        explosion.style.width = '50px';
        explosion.style.height = '50px';
        explosion.style.background = 'radial-gradient(circle, #39ff14 0%, #00e5ff 40%, transparent 70%)';
        explosion.style.borderRadius = '50%';
        explosion.style.zIndex = '998';
        explosion.style.pointerEvents = 'none';
        explosion.style.transition = 'transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), opacity 0.4s ease-out';
        explosion.style.transform = 'scale(0.1)';
        explosion.style.opacity = '1';
        
        document.body.appendChild(explosion);
        
        requestAnimationFrame(() => {
            explosion.style.transform = 'scale(2.5)';
            explosion.style.opacity = '0';
        });
        
        setTimeout(() => explosion.remove(), 400);
    };

    // Trigger every 10 seconds
    setInterval(startSpaceshipAttack, 10000);

});
