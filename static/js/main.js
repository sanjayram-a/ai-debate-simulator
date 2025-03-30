// Only initialize polling if we're on a debate page
if (typeof debateId !== 'undefined') {
    const updateInterval = 2000; // 2 seconds
    let isPolling = true;

    function updateLoadingState(show) {
        const loadingIndicator = document.getElementById('loading');
        loadingIndicator.style.display = show ? 'block' : 'none';
    }

    async function updateDebateStatus() {
        try {
            const response = await fetch(`/api/debate/${debateId}/status`);
            const data = await response.json();
            
            if (data.error) {
                console.error('Error:', data.error);
                return;
            }

            document.getElementById('status').textContent = data.status;
            document.getElementById('status').className = `debate-status status-${data.status}`;

            // Show loading indicator while debate is in progress
            updateLoadingState(data.status === 'in_progress');

            // Stop polling if debate is completed or errored
            if (data.status === 'completed' || data.status === 'error') {
                isPolling = false;
                updateLoadingState(false);
                await updateDebateLog();
            }
        } catch (error) {
            console.error('Error fetching status:', error);
        }
    }

    async function updateDebateLog() {
        try {
            const response = await fetch(`/api/debate/${debateId}/log`);
            const data = await response.json();
            
            if (data.error) {
                console.error('Error:', data.error);
                return;
            }

            // Update debate info
            const logContainer = document.getElementById('debate-log');
            logContainer.innerHTML = '';

            // Add debate analysis if available
            if (data.debate_info && data.debate_analysis) {
                const analysisDiv = document.createElement('div');
                analysisDiv.className = 'debate-analysis';
                analysisDiv.innerHTML = `
                    <h3>Debate Information</h3>
                    <p><strong>Topic:</strong> ${data.debate_info.topic}</p>
                    <p><strong>Round:</strong> ${data.debate_info.current_round}/${data.debate_info.total_rounds}</p>
                    <p><strong>Participants:</strong> ${data.debate_info.participants.join(', ')}</p>
                    <p><strong>Interaction Score:</strong> ${data.debate_analysis.interaction_score}%</p>
                    <p><strong>Topic Adherence:</strong> ${data.debate_analysis.topic_adherence}%</p>
                `;
                logContainer.appendChild(analysisDiv);
            }

            // Add debate messages
            if (data.debate_content && data.debate_content.log && data.debate_content.log.length > 0) {
                const messagesDiv = document.createElement('div');
                messagesDiv.className = 'debate-messages';
                data.debate_content.log.forEach(entry => {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'debate-message';
                    
                    const agentDiv = document.createElement('div');
                    agentDiv.className = 'agent-name';
                    agentDiv.textContent = entry.agent;
                    
                    const responseDiv = document.createElement('div');
                    responseDiv.className = 'agent-response';
                    responseDiv.textContent = entry.response;
                    
                    messageDiv.appendChild(agentDiv);
                    messageDiv.appendChild(responseDiv);
                    messagesDiv.appendChild(messageDiv);
                });
                logContainer.appendChild(messagesDiv);
            }

            // Update summary handling
            const summaryDiv = document.getElementById('debate-summary');
            const summaryContent = document.getElementById('summary-content');

            if (data.status === 'in_progress') {
                summaryContent.innerHTML = `
                    <div class="summary-processing">
                        Debate in progress... Summary will be available when completed.
                    </div>
                `;
                summaryDiv.style.display = 'block';
            } else if (data.debate_content && data.debate_content.summary) {
                // Check if marked library is loaded
                if (typeof marked === 'undefined') {
                    console.error('Marked library not loaded. Displaying raw content.');
                    summaryContent.innerHTML = `
                        <div class="summary-section">
                            <h3>Debate Summary</h3>
                            <div class="summary-text">${data.debate_content.summary}</div>
                        </div>
                    `;
                } else {
                    try {
                        // Convert markdown to HTML using marked
                        const markdownContent = data.debate_content.summary;
                        const htmlContent = marked.parse(markdownContent);
                        
                        summaryContent.innerHTML = `
                            <div class="summary-section markdown-content">
                                <h3>Debate Summary</h3>
                                <div class="summary-text">${htmlContent}</div>
                            </div>
                        `;
                    } catch (error) {
                        console.error('Error parsing summary:', error);
                        summaryContent.innerHTML = `
                            <div class="summary-section">
                                <h3>Debate Summary</h3>
                                <div class="summary-text">${data.debate_content.summary}</div>
                            </div>
                        `;
                    }
                }
                summaryDiv.style.display = 'block';
            }
        } catch (error) {
            console.error('Error fetching log:', error);
        }
    }

    // Start polling
    async function pollDebate() {
        while (isPolling) {
            await updateDebateStatus();
            await updateDebateLog();
            await new Promise(resolve => setTimeout(resolve, updateInterval));
        }
    }

    // Initialize
    pollDebate();
}