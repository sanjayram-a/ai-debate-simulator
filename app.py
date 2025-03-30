import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from knowledge_base.rag import DomainKnowledgeBaseManager
from agents.specializations import create_agent_for_domain
from agents.orchestrator import DebateOrchestrator

app = Flask(__name__)

# Disable static file caching during development
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Initialize knowledge base manager
kb_manager = DomainKnowledgeBaseManager(base_dir="knowledge_base/domains")

# Store active debates
active_debates = {}

@app.route('/')
def index():
    """Home page with form to start a new debate."""
    return render_template('index.html')

@app.route('/debates', methods=['GET'])
def list_debates():
    """List all active debates."""
    debates_info = []
    for debate_id, debate in active_debates.items():
        debates_info.append({
            'id': debate_id,
            'topic': debate.topic,
            'status': debate.status,
            'agents': [agent.name for agent in debate.agents],
            'rounds': debate.total_rounds
        })
    return render_template('debates.html', debates=debates_info)

@app.route('/start_debate', methods=['POST'])
def start_debate():
    """Start a new debate with the given topic and agents."""
    topic = request.form.get('topic', 'AI and Data Science Trends')
    selected_domains = request.form.getlist('domains')
    rounds = int(request.form.get('rounds', 3))
    llm_type = request.form.get('llm_type', 'ollama')
    model_name = request.form.get('model_name', 'llama2')

    # Ensure at least 2 domains are selected
    if len(selected_domains) < 2:
        return render_template('index.html',
                             error="Please select at least 2 domains for the debate")

    # Create agents for selected domains
    agents = []
    for domain in selected_domains:
        kb = kb_manager.get_knowledge_base(domain)
        if kb:
            agent = create_agent_for_domain(domain, kb, llm_type, model_name)
            agents.append(agent)

    # Create a debate ID
    debate_id = f"debate_{len(active_debates) + 1}"

    # Create and start the debate
    orchestrator = DebateOrchestrator(
        topic=topic,
        agents=agents,
        rounds=rounds,
        summary_llm_type=llm_type,
        summary_model_name=model_name
    )

    # Store the debate
    active_debates[debate_id] = orchestrator

    # Start the debate in the background
    orchestrator.conduct_debate_async()

    return redirect(url_for('view_debate', debate_id=debate_id))

@app.route('/debate/<debate_id>')
def view_debate(debate_id):
    """View a specific debate."""
    if debate_id not in active_debates:
        return render_template('error.html', message=f"Debate {debate_id} not found")

    debate = active_debates[debate_id]
    return render_template('debate.html',
                         debate_id=debate_id,
                         topic=debate.topic,
                         status=debate.status)

@app.route('/api/debate/<debate_id>/status')
def debate_status(debate_id):
    """Get the current status of a debate."""
    if debate_id not in active_debates:
        return jsonify({"error": f"Debate {debate_id} not found"}), 404

    debate = active_debates[debate_id]
    return jsonify(debate.get_status())

@app.route('/api/debate/<debate_id>/log')
def debate_log(debate_id):
    """Get the debate log and summary."""
    if debate_id not in active_debates:
        return jsonify({"error": f"Debate {debate_id} not found"}), 404

    debate = active_debates[debate_id]
    # Get debate analysis
    analysis = debate._analyze_debate_quality()
    
    # Structure the response data
    log_data = {
        "status": debate.status,
        "debate_info": {
            "topic": debate.topic,
            "total_rounds": debate.total_rounds,
            "current_round": debate.current_round,
            "participants": [agent.name for agent in debate.agents]
        },
        "debate_content": {
            "log": debate.debate_log,
            "summary": debate.summary
        },
        "debate_analysis": {
            "participation_metrics": analysis["participation"],
            "interaction_score": round(analysis["interaction_score"] * 100, 2),
            "knowledge_usage": analysis["knowledge_usage"],
            "topic_adherence": round(analysis["topic_adherence"] * 100, 2)
        }
    }
    return jsonify(log_data)

if __name__ == '__main__':
    app.run(debug=True)
