"""
Streamlit Web UI for AWS Bedrock Code Review Agent
"""
import streamlit as st
import os
import json
import tempfile
from pathlib import Path
from review_agent import (
    analyze_code,
    analyze_file,
    analyze_diff,
    save_results,
    apply_fix_to_file,
    extract_suggestion_code
)
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AWS Bedrock Code Review Agent",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if 'review_results' not in st.session_state:
    st.session_state.review_results = None
if 'current_file' not in st.session_state:
    st.session_state.current_file = None


def main():
    st.title("🔍 AWS Bedrock Code Review Agent")
    st.markdown("Analyze code files or diffs using AWS Bedrock Claude models")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Check AWS credentials
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        aws_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
        model_id = os.getenv("MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
        
        if not aws_key or not aws_secret:
            st.error("⚠️ AWS credentials not configured!")
            st.info("Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your .env file")
        else:
            st.success("✅ AWS credentials configured")
        
        st.info(f"**Region:** {aws_region}")
        st.info(f"**Model:** {model_id.split('/')[-1] if '/' in model_id else model_id}")
        
        st.markdown("---")
        st.markdown("### 📚 How to use:")
        st.markdown("""
        1. **Upload a file** or **paste code** directly
        2. Click **Analyze Code** to get review
        3. Review suggestions and issues
        4. Click **Apply Fix** to auto-fix issues
        """)


    # Main content area
    tab1, tab2, tab3 = st.tabs(["📁 File Upload", "📝 Code Input", "📊 Review Results"])
    
    with tab1:
        st.header("Upload Code File or Diff")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['py', 'js', 'ts', 'java', 'cpp', 'c', 'go', 'rs', 'diff', 'patch'],
            help="Upload a code file or diff file for review"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            file_path_input = st.text_input(
                "Or enter file path:",
                placeholder="/path/to/your/file.py",
                help="Enter the path to a file on your local system"
            )
        
        with col2:
            if st.button("🔍 Analyze File", type="primary", use_container_width=True):
                if uploaded_file:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        temp_path = tmp_file.name
                    
                    st.session_state.current_file = temp_path
                    with st.spinner("Analyzing code with AWS Bedrock..."):
                        if uploaded_file.name.endswith(('.diff', '.patch')):
                            results = analyze_diff(temp_path)
                        else:
                            results = analyze_file(temp_path)
                        st.session_state.review_results = results
                        save_results(results)
                    st.success("✅ Analysis complete!")
                    st.rerun()
                    
                elif file_path_input:
                    st.session_state.current_file = file_path_input
                    with st.spinner("Analyzing code with AWS Bedrock..."):
                        if file_path_input.endswith(('.diff', '.patch')):
                            results = analyze_diff(file_path_input)
                        else:
                            results = analyze_file(file_path_input)
                        st.session_state.review_results = results
                        save_results(results)
                    st.success("✅ Analysis complete!")
                    st.rerun()
                else:
                    st.error("Please upload a file or enter a file path")
    
    with tab2:
        st.header("Paste Code Directly")
        
        code_input = st.text_area(
            "Enter your code:",
            height=300,
            placeholder="def example_function():\n    pass",
            help="Paste your code here for review"
        )
        
        file_path_for_code = st.text_input(
            "File path (optional, for context):",
            placeholder="src/example.py",
            help="Optional: provide file path for better context"
        )
        
        if st.button("🔍 Analyze Code", type="primary", use_container_width=True):
            if code_input:
                st.session_state.current_file = file_path_for_code or "pasted_code"
                with st.spinner("Analyzing code with AWS Bedrock..."):
                    results = analyze_code(code_input, file_path_for_code)
                    st.session_state.review_results = results
                    save_results(results)
                st.success("✅ Analysis complete!")
                st.rerun()
            else:
                st.error("Please enter some code to analyze")
    
    with tab3:
        st.header("Review Results")
        
        if st.session_state.review_results is None:
            st.info("👆 Upload a file or paste code in the tabs above to get started")
        else:
            results = st.session_state.review_results
            
            # Display error if any
            if "error" in results:
                st.error(f"❌ Error: {results['error']}")
                return
            
            # Summary section
            st.subheader("📋 Summary")
            summary = results.get('summary', 'No summary available')
            st.info(summary)
            
            # Overall score
            score = results.get('overall_score', 0)
            score_color = "🟢" if score >= 8 else "🟡" if score >= 5 else "🔴"
            st.metric("Overall Score", f"{score}/10", delta=None)
            st.markdown(f"{score_color} {'Excellent' if score >= 8 else 'Good' if score >= 5 else 'Needs Improvement'}")
            
            st.markdown("---")
            
            # Issues section
            issues = results.get('issues', [])
            if issues:
                st.subheader(f"⚠️ Issues Found ({len(issues)})")
                
                for idx, issue in enumerate(issues):
                    severity = issue.get('severity', 'low').upper()
                    issue_type = issue.get('type', 'unknown')
                    line_num = issue.get('line', 'N/A')
                    message = issue.get('message', 'No message')
                    suggestion = issue.get('suggestion', '')
                    
                    # Severity color coding
                    if severity == 'HIGH':
                        severity_icon = "🔴"
                        severity_color = "red"
                    elif severity == 'MEDIUM':
                        severity_icon = "🟡"
                        severity_color = "orange"
                    else:
                        severity_icon = "🔵"
                        severity_color = "blue"
                    
                    with st.expander(f"{severity_icon} [{severity}] {issue_type} - Line {line_num}"):
                        st.markdown(f"**Message:** {message}")
                        
                        if suggestion:
                            st.markdown("**Suggestion:**")
                            st.code(suggestion, language='python')
                            
                            # Apply fix button
                            if st.session_state.current_file and st.session_state.current_file != "pasted_code":
                                if st.button(f"✅ Apply Fix #{idx + 1}", key=f"apply_{idx}"):
                                    with st.spinner("Applying fix..."):
                                        success, msg = apply_fix_to_file(
                                            st.session_state.current_file,
                                            issue
                                        )
                                        if success:
                                            st.success(msg)
                                            st.info("🔄 Please re-analyze the file to see updated results")
                                        else:
                                            st.error(msg)
            else:
                st.success("✅ No issues found!")
            
            st.markdown("---")
            
            # Missing docstrings section
            missing_docs = results.get('missing_docstrings', [])
            if missing_docs:
                st.subheader(f"📝 Missing Docstrings ({len(missing_docs)})")
                
                for doc in missing_docs:
                    func_name = doc.get('function', 'unknown')
                    line_num = doc.get('line', 'N/A')
                    doc_suggestion = doc.get('suggestion', '')
                    
                    with st.expander(f"Function: `{func_name}` (Line {line_num})"):
                        if doc_suggestion:
                            st.code(doc_suggestion, language='python')
                        else:
                            st.info("No docstring suggestion available")
            
            # Raw JSON view
            st.markdown("---")
            with st.expander("📄 View Raw JSON"):
                st.json(results)
            
            # Download results
            st.markdown("---")
            json_str = json.dumps(results, indent=2)
            st.download_button(
                label="📥 Download Results as JSON",
                data=json_str,
                file_name=f"review_results_{results.get('file_path', 'unknown').replace('/', '_')}.json",
                mime="application/json"
            )


if __name__ == "__main__":
    main()

