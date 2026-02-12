"""
Email Task Extractor - Web Application
User-friendly interface for extracting tasks from emails
"""
import streamlit as st
import json
from datetime import datetime
from task_extractor import process_email
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Email Task Extractor",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .big-font {
        font-size: 20px !important;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
    }
    .success-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 10px 0;
    }
    .warning-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        margin: 10px 0;
    }
    .danger-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processed_tasks' not in st.session_state:
    st.session_state.processed_tasks = None
if 'extraction_history' not in st.session_state:
    st.session_state.extraction_history = []

# Header
st.title("📧 AI Email Task Extractor")
st.markdown("### Extract structured tasks from unstructured emails using AI")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    confidence_threshold = st.slider(
        "Auto-Approve Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.05,
        help="Tasks with confidence above this will be auto-approved"
    )
    
    st.markdown("---")
    
    st.header("📊 Stats")
    if st.session_state.extraction_history:
        total_emails = len(st.session_state.extraction_history)
        total_tasks = sum(len(e['tasks']) for e in st.session_state.extraction_history)
        st.metric("Emails Processed", total_emails)
        st.metric("Total Tasks Extracted", total_tasks)
    else:
        st.info("No emails processed yet")
    
    st.markdown("---")
    
    st.header("ℹ️ How it works")
    st.markdown("""
    1. **Paste** your email text
    2. **Extract** tasks using AI
    3. **Review** confidence scores
    4. **Export** or edit as needed
    
    **Confidence Levels:**
    - 🟢 High (≥0.7): Auto-approved
    - 🟡 Medium (0.5-0.7): Needs review
    - 🔴 Low (<0.5): Urgent review
    """)
    
    if st.button("🗑️ Clear History"):
        st.session_state.extraction_history = []
        st.session_state.processed_tasks = None
        st.rerun()

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📥 Input Email")
    
    # Tab for different input methods
    input_tab1, input_tab2 = st.tabs(["✍️ Paste Email", "📁 Upload File"])
    
    with input_tab1:
        email_text = st.text_area(
            "Email Content",
            height=300,
            placeholder="Paste your email here...\n\nExample:\nHi team,\nSarah - please finish the Q1 report by March 15th.\nJohn should review the code by end of week.\n...",
            help="Copy and paste the full email body"
        )
        
        sender = st.text_input(
            "From (optional)",
            placeholder="sender@company.com",
            help="Email sender - helps with context"
        )
    
    with input_tab2:
        uploaded_file = st.file_uploader(
            "Upload email file (.txt, .eml)",
            type=['txt', 'eml'],
            help="Upload a text file containing the email"
        )
        
        if uploaded_file:
            email_text = uploaded_file.read().decode('utf-8')
            st.text_area("Preview", email_text, height=200, disabled=True)
            sender = st.text_input("From (optional)", key="file_sender")
    
    # Extract button
    extract_button = st.button("🚀 Extract Tasks", type="primary", use_container_width=True)
    
    # Sample email option
    if st.checkbox("📝 Load sample email"):
        sample_email = """Subject: Q1 Deliverables and Team Meeting

Hi team,

I need everyone to complete the following by end of March:

1. Sarah - Please finalize the marketing analysis report by March 20th. This is critical for our board presentation.

2. The engineering team should review and approve the new API documentation. Not sure exactly when, but ideally before the end of the quarter.

3. Mike, can you schedule a team retrospective meeting? Maybe sometime in the first week of April?

4. We also need someone to update the client database, but I haven't decided who yet.

Let me know if you have any questions.

Best,
Jennifer
Manager, Product Team"""
        email_text = sample_email
        sender = "jennifer@company.com"
        st.text_area("Sample Email Loaded", sample_email, height=200, disabled=True)

with col2:
    st.header("📋 Extracted Tasks")
    
    if extract_button and email_text:
        with st.spinner("🤖 AI is analyzing your email..."):
            try:
                result = process_email(email_text, sender)
                
                if result['success']:
                    st.session_state.processed_tasks = result
                    
                    # Add to history
                    st.session_state.extraction_history.append({
                        'timestamp': datetime.now(),
                        'tasks': result['processed_tasks'],
                        'sender': sender
                    })
                    
                    st.success(f"✅ Successfully extracted {len(result['processed_tasks'])} tasks!")
                else:
                    st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Display results
    if st.session_state.processed_tasks:
        result = st.session_state.processed_tasks
        
        # Summary metrics
        summary = result['queue_summary']
        
        col_metric1, col_metric2, col_metric3 = st.columns(3)
        col_metric1.metric("🟢 Auto-Approved", summary['auto_approved'])
        col_metric2.metric("🟡 Needs Review", summary['standard_review'])
        col_metric3.metric("🔴 Urgent Review", summary['high_priority_review'])
        
        st.markdown("---")
        
        # Task list
        for i, task in enumerate(result['processed_tasks'], 1):
            confidence = task['confidence_metrics']['final_confidence']
            
            # Color-coded container based on confidence
            if confidence >= confidence_threshold:
                emoji = "🟢"
                box_class = "success-box"
                status = "Auto-Approved"
            elif confidence >= 0.5:
                emoji = "🟡"
                box_class = "warning-box"
                status = "Needs Review"
            else:
                emoji = "🔴"
                box_class = "danger-box"
                status = "Urgent Review"
            
            with st.expander(f"{emoji} Task {i}: {task['task_description']}", expanded=True):
                # Task details
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.markdown(f"**Assignee:**")
                    st.text(task['assignee'])
                
                with col_b:
                    st.markdown(f"**Deadline:**")
                    st.text(task.get('deadline', 'Not specified'))
                
                with col_c:
                    st.markdown(f"**Priority:**")
                    st.text(task['priority'].title())
                
                # Confidence details
                st.markdown(f"**Confidence:** {confidence:.0%} ({status})")
                st.progress(confidence)
                
                # Show reasoning
                with st.expander("🔍 AI Reasoning"):
                    st.info(task.get('reasoning', 'No reasoning provided'))
                    
                    if task['confidence_metrics']['adjustments']:
                        st.warning("Adjustments: " + ", ".join(task['confidence_metrics']['adjustments']))
                
                # Edit options
                with st.form(f"edit_form_{i}"):
                    st.markdown("**Edit Task:**")
                    edited_desc = st.text_input("Description", value=task['task_description'])
                    edited_assignee = st.text_input("Assignee", value=task['assignee'])
                    edited_deadline = st.text_input("Deadline", value=task.get('deadline', ''))
                    edited_priority = st.selectbox("Priority", ['high', 'medium', 'low'], 
                                                   index=['high', 'medium', 'low'].index(task['priority']))
                    
                    if st.form_submit_button("✅ Update Task"):
                        st.success("Task updated! (In production, this would save to database)")
        
        st.markdown("---")
        
        # Ambiguities
        if result['extraction_result'].get('ambiguities'):
            with st.expander("⚠️ Potential Ambiguities Detected", expanded=False):
                for ambiguity in result['extraction_result']['ambiguities']:
                    st.warning(f"• {ambiguity}")
        
        # Export options
        st.markdown("### 📤 Export Options")
        
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        
        with col_exp1:
            # Export as JSON
            json_data = json.dumps(result, indent=2, default=str)
            st.download_button(
                label="📄 Download JSON",
                data=json_data,
                file_name=f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col_exp2:
            # Export as CSV
            tasks_df = pd.DataFrame([{
                'Task': t['task_description'],
                'Assignee': t['assignee'],
                'Deadline': t.get('deadline', ''),
                'Priority': t['priority'],
                'Confidence': f"{t['confidence_metrics']['final_confidence']:.2f}",
                'Status': t['review_status']
            } for t in result['processed_tasks']])
            
            csv_data = tasks_df.to_csv(index=False)
            st.download_button(
                label="📊 Download CSV",
                data=csv_data,
                file_name=f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_exp3:
            # Copy to clipboard (markdown format)
            markdown_output = "# Extracted Tasks\n\n"
            for i, task in enumerate(result['processed_tasks'], 1):
                markdown_output += f"## Task {i}: {task['task_description']}\n"
                markdown_output += f"- **Assignee:** {task['assignee']}\n"
                markdown_output += f"- **Deadline:** {task.get('deadline', 'TBD')}\n"
                markdown_output += f"- **Priority:** {task['priority']}\n"
                markdown_output += f"- **Confidence:** {task['confidence_metrics']['final_confidence']:.0%}\n\n"
            
            st.download_button(
                label="📋 Download Markdown",
                data=markdown_output,
                file_name=f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
    else:
        st.info("👈 Paste an email on the left and click 'Extract Tasks' to get started!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Built with ❤️ using Claude AI | Confidence threshold can be adjusted in sidebar</p>
</div>
""", unsafe_allow_html=True)
