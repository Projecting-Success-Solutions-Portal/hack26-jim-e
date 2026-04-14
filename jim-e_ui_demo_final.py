import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
import pandas as pd


def generate_pdf_report(history):
    """Generate a PDF report of submission history"""
    buffer = io.BytesIO()
    # The title in the PDF function is updated to 'Jim-E'
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1f77b4',
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#333333',
        spaceAfter=12,
        spaceBefore=12
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        textColor='#555555'
    )

    # Title
    # Using 'Jim-E' as it appeared in one of the original scripts
    story.append(Paragraph("Jim-E Risk Review Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
    story.append(Spacer(1, 0.3 * inch))

    # Add each submission
    for i, entry in enumerate(reversed(history)):
        story.append(Paragraph(f"<b>Submission {len(history) - i}</b>", heading_style))
        story.append(Paragraph(f"<b>Timestamp:</b> {entry['timestamp']}", body_style))
        story.append(Spacer(1, 0.1 * inch))

        # Check if this is a file upload or single description
        if entry.get('is_file_upload'):
            story.append(Paragraph("<b>Source:</b> File Upload", body_style))
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph("<b>Selected Risks:</b>", body_style))
            for risk in entry['risks']:
                story.append(Paragraph(f"• {risk}", body_style))
        else:
            story.append(Paragraph("<b>Risk Description:</b>", body_style))
            desc_text = entry['description'].replace('\n', '<br/>')
            story.append(Paragraph(desc_text, body_style))

        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph(f"<b>Agreement Status:</b> {entry['agreement']}", body_style))

        if entry['agreement'] == "Disagree":
            if entry.get('is_file_upload') and entry.get('individual_reasons'):
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph("<b>Disagreement Reasons by Risk:</b>", body_style))
                for risk, reason in entry['individual_reasons'].items():
                    if reason:
                        story.append(Paragraph(f"<b>• {risk}:</b> {reason}", body_style))
            elif entry.get('disagree_reason'):
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph("<b>Reason for Disagreement:</b>", body_style))
                reason_text = entry['disagree_reason'].replace('\n', '<br/>')
                story.append(Paragraph(reason_text, body_style))

        story.append(Spacer(1, 0.3 * inch))

    doc.build(story)
    buffer.seek(0)
    return buffer


# Initialise session state variables
if "description" not in st.session_state:
    st.session_state.description = ""
if "test_description" not in st.session_state:
    st.session_state.test_description = ""
if "submit_enabled" not in st.session_state:
    st.session_state.submit_enabled = False
if "last_analysed_description" not in st.session_state:
    st.session_state.last_analysed_description = ""
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "agreement" not in st.session_state:
    st.session_state.agreement = None
if "disagree_reason" not in st.session_state:
    st.session_state.disagree_reason = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "input_mode" not in st.session_state:
    st.session_state.input_mode = "text"
if "uploaded_risks" not in st.session_state:
    st.session_state.uploaded_risks = []
if "analysis_message" not in st.session_state:
    st.session_state.analysis_message = ""
if "selected_risks" not in st.session_state:
    st.session_state.selected_risks = []
if "all_risks_from_file" not in st.session_state:
    st.session_state.all_risks_from_file = []
if "individual_reasons" not in st.session_state:
    st.session_state.individual_reasons = {}
if "selected_template" not in st.session_state:
    st.session_state.selected_template = "-- Select a test input --"


# --- Header and Export Button ---
col1, col2, col3 = st.columns([5, 8, 5])

with col2:
    # Use "Jim-E" to be consistent with the PDF function
    st.title("Jim-E")
    st.markdown("<div style='text-align: '>Judgement-Informed Machine for Evaluation</div>", unsafe_allow_html=True)
with col3:
    if len(st.session_state.history) > 0:
        pdf_buffer = generate_pdf_report(st.session_state.history)
        st.download_button(
            label="📄",
            data=pdf_buffer,
            file_name=f"risk_review_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            help="Export submission history as PDF"
        )
with col1:
    st.image("image.png", width=300)
    pass


# --- Submission History ---
if st.session_state.history:
    st.subheader("📋 Submission History")
    for i, entry in enumerate(reversed(st.session_state.history)):
        with st.expander(f"Submission {len(st.session_state.history) - i} - {entry['timestamp']}"):
            if entry.get('is_file_upload'):
                st.write("**Source:** File Upload")
                st.write("**Selected Risks:**")
                for risk in entry['risks']:
                    st.write(f"- {risk}")
            else:
                st.write("**Description:**")
                st.write(entry['description'])
            st.write(f"**Agreement:** {entry['agreement']}")
            if entry['agreement'] == "Disagree":
                if entry.get('is_file_upload') and entry.get('individual_reasons'):
                    st.write("**Disagreement Reasons:**")
                    for risk, reason in entry['individual_reasons'].items():
                        if reason:
                            st.write(f"- **{risk}:** {reason}")
                elif entry.get('disagree_reason'):
                    st.write(f"**Reason:** {entry['disagree_reason']}")
    st.divider()


# --- Input Mode Selection ---
input_mode = st.radio("Input Method:", ["Text Input", "Excel Upload", "Text Input (Example Cases)"], horizontal=True)


# --- Text Input (Standard) ---
if input_mode == "Text Input":
    st.session_state.input_mode = "text"
    # Description input
    description = st.text_area("Enter a detailed description of the risk", value=st.session_state.description,
                               key="desc_input")

    # Check if description has changed since last analysis
    if description != st.session_state.last_analysed_description:
        st.session_state.submit_enabled = False
        st.session_state.submitted = False

    # Analyse button
    if st.button("Analyse Description"):
        st.session_state.last_analysed_description = description
        st.session_state.description = description
        st.session_state.submit_enabled = True
        st.session_state.submitted = False
        st.session_state.analysis_message = "Description analysed!"
        st.success(st.session_state.analysis_message)


# --- Text Input (Example Cases) ---
elif input_mode == "Text Input (Example Cases)":
    st.session_state.input_mode = "text_test" # New mode to distinguish it from standard text input

    # Predefined risk templates
    risk_templates = {
        "-- Select a test input --": "",
        "Example Prompt 1: ChatGPT gpt-4o-mini": "Risk: Critical personnel. Risk description: Loss of critical personnel within business strategy can delay strategic initiatives, highlighting the need for succession planning.",
        "Example Prompt 2: Qwen2.5-3B-Instruct": "Risk: Non-Recurring Engineering higher than expected. Please suggest possible mitigations."
    }

    # Analysis messages
    chatgpt_analysis_text = """To improve the risk description regarding "Critical personnel," consider the following recommendations based on the insights gathered from tacit heuristics:
    
1. Define Specificity: Be specific about who the "critical personnel" are. For example, are they project managers, engineers, or key stakeholders? Specify their roles and the impact of their absence.

2. Include Quantitative Measures: Quantify the impact of losing critical personnel. Mention potential delays in specific timelines or financial implications, such as estimated costs incurred due to project delays.

3. Clarify Triggers: Identify clear triggers for when this risk might manifest. For example, specify conditions like "if the key personnel are absent for more than two weeks" which can help in monitoring and preparing for the risk more efficiently.

4. Mitigation Actions: Expand on the importance of succession planning by detailing what it entails—developing internal talent, conducting knowledge transfer sessions, or creating a mentorship program.

5. Ownership and Accountability: Assign ownership for monitoring the risk and implementing succession planning. Clarifying who is responsible will enhance accountability.

6. Ensure Measurable Outcomes: Outline what success looks like for mitigation efforts. For instance, "by Q2, ensure at least two identified successors are ready to assume responsibilities."
"""
    rithik_analysis_text = 'Mitigation: Project_Manager to set KPI ≥95% OTIF by Q-end; review weekly; escalate if <90% for 2 consecutive weeks.'

    # Dropdown to select a template
    st.write("**Select a test input:**")
    selected_template = st.selectbox(
        "Choose a test input to populate the text area",
        options=list(risk_templates.keys()),
        index=list(risk_templates.keys()).index(st.session_state.selected_template)
        if st.session_state.selected_template in risk_templates else 0,
        key="template_select"
    )

    # Update test_description based on selected template
    if selected_template != st.session_state.selected_template:
        st.session_state.test_description = risk_templates[selected_template]
        st.session_state.selected_template = selected_template
        # Use st.experimental_rerun() or remove if st.rerun() is not supported/needed in your environment
        # st.rerun()

    # Description input
    description = st.text_area("Enter a detailed description of the risk",
                               value=st.session_state.test_description)

    # Check if description has changed since last analysis
    if description != st.session_state.last_analysed_description:
        st.session_state.submit_enabled = False
        st.session_state.submitted = False

    # Analyse button
    if st.button("Analyse Description", key="analyse_test"):
        st.session_state.last_analysed_description = description
        st.session_state.test_description = description
        st.session_state.submit_enabled = True
        st.session_state.submitted = False
        st.session_state.analysis_message = "Description analysed!"
        st.success(st.session_state.analysis_message)

        # Conditional analysis message display
        if st.session_state.selected_template == "Example Prompt 2: Qwen2.5-3B-Instruct":
            st.info(rithik_analysis_text)
        else:
            # Default to ChatGPT text for any other selection
            st.info(chatgpt_analysis_text)


# --- Excel Upload ---
else: # input_mode == "Excel Upload"
    st.session_state.input_mode = "file"
    # File upload
    uploaded_file = st.file_uploader("Upload Excel file with 'Risk' column", type=['xlsx', 'xls'])

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)

            if 'Risk' in df.columns:
                # Extract risks and remove NaN values
                all_risks = df['Risk'].dropna().tolist()
                st.session_state.all_risks_from_file = all_risks

                if all_risks:
                    # Limit to displaying only the first 3 risks for selection
                    limited_risks = all_risks[:3]
                    st.write(f"**3 Random Risks from File:**")

                    # Create checkboxes for risk selection (only showing the first 3)
                    selected = []
                    for idx, risk in enumerate(limited_risks):
                        # Ensure the checkbox state is managed correctly
                        if st.checkbox(risk, key=f"risk_checkbox_{idx}_{uploaded_file.name}"):
                            selected.append(risk)

                    # Show warning if not exactly 3 selected
                    if len(selected) > 0 and len(selected) != 3:
                        st.warning(f"Please select exactly 3 risks. Currently selected: {len(selected)}")

                    # Analyse button for file (only enabled when exactly 3 selected)
                    # This enforces the exact 3 selection requirement from the first script
                    if st.button("Analyse File", disabled=len(selected) != 3):
                        st.session_state.selected_risks = selected
                        st.session_state.uploaded_risks = selected
                        st.session_state.submit_enabled = True
                        st.session_state.submitted = False
                        st.session_state.analysis_message = "File analysed!"
                        # Initialize individual disagreement reasons
                        st.session_state.individual_reasons = {risk: "" for risk in selected}
                        st.success(st.session_state.analysis_message)
                else:
                    st.warning("No risks found in the 'Risk' column.")
            else:
                st.error("Excel file must contain a column named 'Risk'")
        except Exception as e:
            st.error(f"Error reading file: {e}")


# --- Agreement/Disagreement Section ---
if st.session_state.submit_enabled:
    st.session_state.agreement = st.radio(
        "Do you agree with the analysis?",
        ["Agree", "Disagree"],
        # Use an index to maintain state if re-run
        index=0 if st.session_state.agreement == "Agree" else 1 if st.session_state.agreement == "Disagree" else 0
    )

    # If user disagrees, show appropriate input
    if st.session_state.agreement == "Disagree":
        if st.session_state.input_mode == "file":
            st.write("**Please provide disagreement reasons for each risk:**")
            for risk in st.session_state.selected_risks:
                # The text area key is dynamically generated to prevent clashes
                st.session_state.individual_reasons[risk] = st.text_area(
                    f"Reason for '{risk}':",
                    value=st.session_state.individual_reasons.get(risk, ""),
                    key=f"reason_{risk}_disagree"
                )
        else: # "text" or "text_test" mode
            st.session_state.disagree_reason = st.text_area("Please explain why you disagree:")


# --- Submit Button and History Logging ---
if st.button("Submit", disabled=not st.session_state.submit_enabled):
    # Save to history
    if st.session_state.input_mode == "file":
        st.session_state.history.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'is_file_upload': True,
            'risks': st.session_state.selected_risks,
            'agreement': st.session_state.agreement,
            'individual_reasons': st.session_state.individual_reasons.copy() if st.session_state.agreement == "Disagree" else {}
        })
    else:
        # Determine which description to save based on current mode
        current_desc = st.session_state.test_description if st.session_state.input_mode == "text_test" else st.session_state.description
        st.session_state.history.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'is_file_upload': False,
            'description': current_desc,
            'agreement': st.session_state.agreement,
            'disagree_reason': st.session_state.disagree_reason if st.session_state.agreement == "Disagree" else ""
        })

    # Clear the form for next entry
    st.session_state.description = ""
    st.session_state.test_description = ""
    st.session_state.last_analysed_description = ""
    st.session_state.uploaded_risks = []
    st.session_state.selected_risks = []
    st.session_state.individual_reasons = {}
    st.session_state.submit_enabled = False
    st.session_state.agreement = None
    st.session_state.disagree_reason = ""
    st.session_state.submitted = True
    st.session_state.selected_template = "-- Select a test input --" # Reset template selection
    st.rerun()

# Show success message if submitted
if st.session_state.submitted:
    st.success("Submission successful! You can enter a new risk description above.")
    # The session_state.submitted is reset within the 'Submit' block before st.rerun(),
    # so this message will only show up for one frame after the rerun, then disappear.
    # This is standard practice when using st.rerun() after submission.
    # st.session_state.submitted = False # This line is moved to the submission logic before rerun