import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from email_utils import send_grievance_email
from requests.auth import HTTPBasicAuth

# =========================
# SERVICENOW CONFIG
# =========================

INSTANCE_URL = st.secrets["INSTANCE_URL"]

USERNAME = st.secrets["USERNAME"]

PASSWORD = st.secrets["PASSWORD"]

TABLE_NAME = "x_2054267_colleg_0_grievance"
def predict_priority(text):

    text = text.lower()

    high_keywords = [
        "wifi",
        "not working",
        "unable",
        "cannot",
        "error",
        "failed",
        "exam",
        "registration"
    ]

    medium_keywords = [
        "mess",
        "food",
        "delay",
        "issue",
        "problem"
    ]

    for word in high_keywords:
        if word in text:
            return "high"

    for word in medium_keywords:
        if word in text:
            return "medium"

    return "low"

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="GITAM Grievance Portal",
    page_icon="📢",
    layout="wide"
)

st.title("📢 GITAM Grievance Portal")

tab1, tab2, tab3 = st.tabs([
    "📝 Submit Grievance",
    "🎫 Track Grievance",
    "📊 Admin Dashboard"
])

# ==================================================
# TAB 1 : SUBMIT GRIEVANCE
# ==================================================

with tab1:

    st.markdown(
        "Submit your complaint — we will route it to the right department automatically."
    )

    st.divider()

    with st.form("grievance_form"):

        st.subheader("Student Information")

        col1, col2 = st.columns(2)

        with col1:
            student_name = st.text_input("Full Name")

        with col2:
            roll_number = st.text_input("Roll Number")

        student_email = st.text_input("College Email")

        st.subheader("Complaint Details")

        category = st.selectbox(
            "Category",
            [
                "hostel",
                "mess_food",
                "exam",
                "exam_result",
                "course_registration",
                "college_portal",
                "wifi",
                "lift",
                "ac",
                "library",
                "parking",
                "fees_payment"
            ]
        )



        description = st.text_area(
            "Describe your issue",
            height=150
        )
        priority = "low"

        if description:
            priority = predict_priority(description)
            st.info(f"🤖 AI Predicted Priority: {priority.upper()}")

        submit_btn = st.form_submit_button(
            "Submit Grievance"
        )

    if submit_btn:

        if not student_name:

            st.error(
                "Please enter your name."
            )

        elif not roll_number:

            st.error(
                "Please enter roll number."
            )

        elif not student_email:

            st.error(
                "Please enter email."
            )

        elif not description:

            st.error(
                "Please enter grievance description."
            )

        else:

            payload = {
                "student_name": student_name,
                "roll_number": roll_number,
                "student_email": student_email,
                "category": category,
                "priority": priority,
                "description": description,
                "status": "open"
            }

            url = (
                f"{INSTANCE_URL}/api/now/table/{TABLE_NAME}"
            )

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            try:

                response = requests.post(
                    url,
                    auth=HTTPBasicAuth(
                        USERNAME,
                        PASSWORD
                    ),
                    headers=headers,
                    json=payload
                )

                if response.status_code in [200, 201]:

                    result = response.json()["result"]

                    ticket_no = result.get(
                        "number",
                        "Generated"
                    )

                    # Department Mapping

                    if category == "wifi":
                        department = "IT Department"

                    elif category == "hostel":
                        department = "Hostel Department"

                    elif category == "mess_food":
                        department = "Mess Department"

                    elif category == "library":
                        department = "Library Department"

                    elif category in ["exam", "exam_result"]:
                        department = "Exam Department"

                    elif category == "ac":
                        department = "Facilities Department"

                    elif category == "course_registration":
                        department = "Academic Department"

                    elif category == "college_portal":
                        department = "Academic Department"

                    elif category == "parking":
                        department = "Transport Department"

                    elif category == "fees_payment":
                        department = "Accounts Department"

                    else:
                        department = "Department Pending"

                    # Send Email

                    email_sent = send_grievance_email(
                        student_name,
                        student_email,
                        ticket_no,
                        department,
                        "Open"
                    )

                    st.success(
                        "✅ Grievance submitted successfully!"
                    )

                    st.info(
                        f"🎫 Ticket Number: {ticket_no}"
                    )

                    st.info(
                        f"🏢 Department: {department}"
                    )

                    st.info(
                        "Please save this ticket number for tracking."
                    )

                    if email_sent:

                        st.success(
                            "📧 Confirmation email sent successfully!"
                        )

                    else:

                        st.warning(
                            "⚠️ Ticket created but email could not be sent."
                        )

                else:

                    st.error(
                        f"ServiceNow Error: {response.text}"
                    )

            except Exception as e:

                st.error(
                    f"Error: {str(e)}"
                )

# ==================================================
# TAB 2 : TRACK GRIEVANCE
# ==================================================

with tab2:

    st.header("🎫 Track Your Complaint")

    st.write(
        "Enter your grievance ticket number to check current status."
    )

    ticket_number = st.text_input(
        "Ticket Number",
        placeholder="GRI0001012"
    )

    if st.button("Track Complaint"):

        if not ticket_number:

            st.warning(
                "Please enter a ticket number."
            )

        else:

            url = (
                f"{INSTANCE_URL}/api/now/table/{TABLE_NAME}"
            )

            params = {
                "sysparm_query": f"number={ticket_number}",
                "sysparm_limit": "1"
            }

            try:

                response = requests.get(
                    url,
                    auth=HTTPBasicAuth(
                        USERNAME,
                        PASSWORD
                    ),
                    params=params
                )

                if response.status_code == 200:

                    records = response.json()["result"]

                    if records:

                        row = records[0]

                        st.success(
                            "✅ Complaint Found"
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            st.info(
                                f"🎫 Ticket Number: {row['number']}"
                            )

                            st.info(
                                f"📂 Category: {row['category']}"
                            )

                            st.info(
                                f"⚡ Priority: {row['priority']}"
                            )

                        with col2:

                            status = row["status"].strip().lower()

                            if status == "open":
                                st.warning(
                                    "🟡 Status : OPEN"
                                )

                            elif status == "in_progress":
                                st.info(
                                    "🔵 Status : IN PROGRESS"
                                )

                            elif status == "resolved":
                                st.success(
                                    "🟢 Status : RESOLVED"
                                )

                            elif status == "closed":
                                st.success(
                                    "✅ Status : CLOSED"
                                )

                            else:

                                st.info(
                                    f"📌 Status : {row['status']}"
                                )

                            st.info(
                                f"🏢 Department: {row['department']}"
                            )

                        st.text_area(
                            "Description",
                            value=row["description"],
                            disabled=True,
                            height=150
                        )

                    else:

                        st.error(
                            "❌ Ticket Not Found"
                        )

                else:

                    st.error(
                        "Unable to connect to ServiceNow"
                    )

            except Exception as e:

                st.error(
                    f"Error: {str(e)}"
                )
# ==================================================
# TAB 3 : ADMIN DASHBOARD
# ==================================================

with tab3:

    st.header("📊 Admin Dashboard")

    try:

        url = f"{INSTANCE_URL}/api/now/table/{TABLE_NAME}"

        response = requests.get(
            url,
            auth=HTTPBasicAuth(
                USERNAME,
                PASSWORD
            )
        )

        if response.status_code == 200:

            records = response.json()["result"]

            if len(records) > 0:

                df = pd.DataFrame(records)

                total = len(df)

                open_count = len(
                    df[df["status"] == "open"]
                )

                progress_count = len(
                    df[df["status"] == "in_progress"]
                )

                resolved_count = len(
                    df[df["status"] == "resolved"]
                )

                closed_count = len(
                    df[df["status"] == "closed"]
                )

                st.subheader("Overview")

                c1, c2, c3, c4, c5 = st.columns(5)

                c1.metric("Total", total)
                c2.metric("Open", open_count)
                c3.metric("In Progress", progress_count)
                c4.metric("Resolved", resolved_count)
                c5.metric("Closed", closed_count)

                st.divider()

                left, right = st.columns(2)

                with left:

                    st.subheader(
                        "Complaints By Category"
                    )

                    category_df = (
                        df["category"]
                        .value_counts()
                        .reset_index()
                    )

                    category_df.columns = [
                        "Category",
                        "Count"
                    ]

                    fig1 = px.bar(
                        category_df,
                        x="Category",
                        y="Count"
                    )

                    st.plotly_chart(
                        fig1,
                        use_container_width=True
                    )

                with right:

                    st.subheader(
                        "Complaints By Priority"
                    )

                    priority_df = (
                        df["priority"]
                        .value_counts()
                        .reset_index()
                    )

                    priority_df.columns = [
                        "Priority",
                        "Count"
                    ]

                    fig2 = px.pie(
                        priority_df,
                        names="Priority",
                        values="Count"
                    )

                    st.plotly_chart(
                        fig2,
                        use_container_width=True
                    )

                st.subheader(
                    "Complaints By Status"
                )

                status_df = (
                    df["status"]
                    .value_counts()
                    .reset_index()
                )

                status_df.columns = [
                    "Status",
                    "Count"
                ]

                fig3 = px.bar(
                    status_df,
                    x="Status",
                    y="Count"
                )

                st.plotly_chart(
                    fig3,
                    use_container_width=True
                )

                st.subheader(
                    "Recent Complaints"
                )

                display_cols = [
                    "number",
                    "student_name",
                    "category",
                    "priority",
                    "status",
                    "department"
                ]

                available_cols = [
                    c for c in display_cols
                    if c in df.columns
                ]

                st.dataframe(
                    df[available_cols],
                    use_container_width=True
                )

            else:

                st.warning(
                    "No grievances found."
                )

        else:

            st.error(
                f"ServiceNow Error: {response.text}"
            )

    except Exception as e:

        st.error(
            str(e)
        )
