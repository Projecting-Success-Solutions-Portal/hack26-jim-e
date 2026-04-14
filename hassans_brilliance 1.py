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
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

    story = []
    styles = getSampleStyleSheet()

    #Add Logo
    #st.image("image.png", width=150)  # Adjust width as needed

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


# Initialise session state variables first
if "description" not in st.session_state:
    st.session_state.description = ""
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

# Title with export button
col1, col2, col3 = st.columns([5, 8, 5])

with col2:
    st.title("JIM-E")
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
    st.image("image.png", width=300)  # Adjust width as needed

# Display submission history at the top (most recent first)
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

# Input mode selection
input_mode = st.radio("Input Method:", ["Text Input", "Excel Upload"], horizontal=True)

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

else:
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
                    # Limit to displaying 3 risks
                    limited_risks = all_risks[:3]
                    st.write(f"**3 Random Risks from File:**")

                    # Create checkboxes for risk selection (only showing the first 3)
                    selected = []
                    for idx, risk in enumerate(limited_risks):
                        if st.checkbox(risk, key=f"risk_checkbox_{idx}"):
                            selected.append(risk)

                    # # Show warning if not exactly 3 selected
                    # if len(selected) < 2:
                    #     st.warning(f"Please select at least 2 risk. Currently selected: {len(selected)}")

                    # Analyse button for file (only enabled when exactly 3 selected)
                    if st.button("Analyse File"):
                        st.session_state.selected_risks = selected
                        st.session_state.uploaded_risks = selected
                        st.session_state.submit_enabled = True
                        st.session_state.submitted = False
                        st.session_state.analysis_message = "File analysed!"
                        st.session_state.individual_reasons = {risk: "" for risk in selected}
                        st.success(st.session_state.analysis_message)
                else:
                    st.warning("No risks found in the 'Risk' column.")
            else:
                st.error("Excel file must contain a column named 'Risk'")
        except Exception as e:
            st.error(f"Error reading file: {e}")

# Agree/Disagree radio buttons (only show after analysis)
if st.session_state.submit_enabled:
    st.session_state.agreement = st.radio(
        "Do you agree with the analysis?",
        ["Agree", "Disagree"],
        index=0 if st.session_state.agreement == "Agree" else 1 if st.session_state.agreement == "Disagree" else 0
    )

    # If user disagrees, show appropriate input
    if st.session_state.agreement == "Disagree":
        if st.session_state.input_mode == "file":
            st.write("**Please provide disagreement reasons for each risk:**")
            for risk in st.session_state.selected_risks:
                st.session_state.individual_reasons[risk] = st.text_area(
                    f"Reason for '{risk}':",
                    value=st.session_state.individual_reasons.get(risk, ""),
                    key=f"reason_{risk}"
                )
        else:
            st.session_state.disagree_reason = st.text_area("Please explain why you disagree:")

# Submit button
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
        st.session_state.history.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'is_file_upload': False,
            'description': st.session_state.description,
            'agreement': st.session_state.agreement,
            'disagree_reason': st.session_state.disagree_reason if st.session_state.agreement == "Disagree" else ""
        })

    # Clear the form for next entry
    st.session_state.description = ""
    st.session_state.last_analysed_description = ""
    st.session_state.uploaded_risks = []
    st.session_state.selected_risks = []
    st.session_state.individual_reasons = {}
    st.session_state.submit_enabled = False
    st.session_state.agreement = None
    st.session_state.disagree_reason = ""
    st.session_state.submitted = True
    st.rerun()

# Show success message if submitted
if st.session_state.submitted:
    st.success("Submission successful! You can enter a new risk description above.")
    st.session_state.submitted = False
