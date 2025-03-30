// Only initialize polling if we're on a debate page
if (typeof debateId !== 'undefined') {
    const updateInterval = 2000; // 2 seconds
    let isPolling = true;

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

            // Stop polling if debate is completed or errored
            if (data.status === 'completed' || data.status === 'error') {
                isPolling = false;
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

            // Update debate log
            const logContainer = document.getElementById('debate-log');
            logContainer.innerHTML = '';

            data.log.forEach(entry => {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'debate-message';
                
                const agentDiv = document.createElement('div');
                agentDiv.className = 'agent-name';
                agentDiv.textContent = entry.agent;
                
                const responseDiv = document.createElement('div');
                responseDiv.textContent = entry.response;
                
                messageDiv.appendChild(agentDiv);
                messageDiv.appendChild(responseDiv);
                logContainer.appendChild(messageDiv);
            });

            // Update summary if available
            if (data.summary) {
                const summaryDiv = document.getElementById('debate-summary');
                const summaryContent = document.getElementById('summary-content');
                summaryContent.textContent = data.summary;
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