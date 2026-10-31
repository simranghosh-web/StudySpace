import math
import streamlit as st
import json
import uuid
import html
import pandas as pd

from pathlib import Path
from datetime import date, timedelta


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="StudySpace",
    page_icon="📚",
    layout="wide"
)


# ==========================================
# 2. DATA STORAGE
# ==========================================

FILE_NAME = Path(__file__).with_name("study_data.json")


def default_data():
    return {
        "attendance": {
            "total": 0,
            "attended": 0
        },
        "tasks": [],
        "study_hours": {}
    }


def load_data():

    if not FILE_NAME.exists():
        return default_data()

    try:
        with open(FILE_NAME, "r") as file:
            saved = json.load(file)

        # Support older Study Tracker JSON format
        if isinstance(saved, dict) and "study_hours" not in saved:
            saved = {
                "attendance": {
                    "total": 0,
                    "attended": 0
                },
                "tasks": [],
                "study_hours": saved
            }

        if not isinstance(saved, dict):
            return default_data()

        data = default_data()
        data.update(saved)

        if not isinstance(data["attendance"], dict):
            data["attendance"] = default_data()["attendance"]

        data["attendance"].setdefault("total", 0)
        data["attendance"].setdefault("attended", 0)

        if not isinstance(data["tasks"], list):
            data["tasks"] = []

        if not isinstance(data["study_hours"], dict):
            data["study_hours"] = {}

        return data

    except (json.JSONDecodeError, OSError):
        st.error("Could not read saved data. Check study_data.json.")
        return default_data()


def save_data(data):

    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)


# Load saved data AFTER defining load_data()

data = load_data()


# ==========================================
# 3. STUDY STREAK CALCULATION
# ==========================================

def calculate_streak(study_data):

    study_dates = {
        date.fromisoformat(day)
        for day, hours in study_data.items()
        if float(hours) > 0
    }

    if not study_dates:
        return 0

    today = date.today()

    # Allow yesterday as the starting point
    # if the user hasn't logged today's study yet.

    current = (
        today
        if today in study_dates
        else today - timedelta(days=1)
    )

    streak = 0

    while current in study_dates:
        streak += 1
        current -= timedelta(days=1)

    return streak


current_streak = calculate_streak(data["study_hours"])


# ==========================================
# 4. GLASS DESIGN
# ==========================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at 10% 10%, #33245c 0%, transparent 35%),
        radial-gradient(circle at 90% 20%, #59345b 0%, transparent 30%),
        linear-gradient(135deg, #11101f, #211a35, #171526);

    color: #f7f2ff;
}

[data-testid="stSidebar"] {
    background: rgba(30, 23, 51, 0.95);
    border-right: 1px solid rgba(255,255,255,0.15);
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,0.09);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 18px;
    padding: 20px;
    backdrop-filter: blur(15px);
}

.stButton > button {
    background: linear-gradient(135deg, #9874ed, #c18af1);
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    padding: 10px 22px;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #ad91fa, #d5a1fa);
    color: white;
    border: none;
}

div[data-testid="stForm"] {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 16px;
    padding: 20px;
}

h1, h2, h3 {
    color: #f4eaff;
}

p, label {
    color: #e5dcf6;
}

hr {
    border-color: rgba(255,255,255,0.15);
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 5. CALCULATE STATISTICS
# ==========================================

attendance = data["attendance"]

total_classes = int(attendance["total"])
attended_classes = int(attendance["attended"])

attendance_percentage = (
    attended_classes / total_classes * 100
    if total_classes > 0 else 0
)

pending_tasks = sum(
    1 for task in data["tasks"]
    if not task.get("done", False)
)

total_study_hours = sum(
    float(hours)
    for hours in data["study_hours"].values()
)


# ==========================================
# 6. SIDEBAR NAVIGATION
# ==========================================

st.sidebar.markdown("# 📚 StudySpace")

st.sidebar.caption("PLAN  •  TRACK  •  ACHIEVE")

st.sidebar.divider()

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Dashboard",
        "Attendance",
        "Tasks",
        "Study Tracker"
    ]
)

st.sidebar.divider()

st.sidebar.markdown("✨ Small steps every day!")

st.sidebar.caption(
    "Your personal academic companion."
)


# ==========================================
# 7. MAIN HEADER
# ==========================================

st.title("📚 StudySpace")

st.subheader(
    "Your personal student productivity dashboard"
)

st.write(
    f"Welcome back! Today is {date.today().strftime('%d %B %Y')}."
)

st.divider()


# ==========================================
# 8. DASHBOARD
# ==========================================

if page == "Dashboard":

    st.header("✨ Your Dashboard")

    st.write(
        "Everything you need to stay organised."
    )

    # Dashboard statistics

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🎓 Attendance",
            f"{attendance_percentage:.1f}%",
            f"{attended_classes}/{total_classes} classes"
        )

    with col2:

        st.metric(
            "📝 Pending Tasks",
            pending_tasks
        )

    with col3:

        st.metric(
            "⏰ Study Hours",
            f"{total_study_hours:.1f} hrs",
            "Total recorded"
        )

    st.success(
        "Your productivity journey starts here!"
    )

    st.divider()

    # Weekly study chart

    st.subheader("📈 Your Weekly Study Progress")

    today = date.today()

    weekly_dates = [
        today - timedelta(days=i)
        for i in range(6, -1, -1)
    ]

    weekly_data = {
        "Day": [
            d.strftime("%a")
            for d in weekly_dates
        ],

        "Study Hours": [
            float(
                data["study_hours"].get(str(d), 0)
            )
            for d in weekly_dates
        ]
    }

    chart_df = pd.DataFrame(weekly_data).set_index("Day")

    st.line_chart(chart_df)

    st.divider()

    # Upcoming deadlines

    st.subheader("📅 Upcoming Deadlines")

    upcoming = []

    for task in data["tasks"]:

        if not task.get("done", False):

            try:

                deadline = date.fromisoformat(
                    task["deadline"]
                )

                if deadline >= today:

                    upcoming.append(
                        (deadline, task.get("title", "Untitled"))
                    )

            except (ValueError, KeyError, TypeError):
                pass

    upcoming.sort(key=lambda item: item[0])

    if upcoming:

        for deadline, title in upcoming[:5]:

            days_left = (deadline - today).days

            col1, col2 = st.columns([3, 1])

            with col1:

                st.write(
                    f"📌 **{html.escape(str(title))}**"
                )

                st.caption(
                    deadline.strftime("%d %B %Y")
                )

            with col2:

                if days_left == 0:
                    st.warning("Due today")

                else:
                    st.info(f"{days_left} days left")

    else:

        st.info(
            "No upcoming deadlines. Add a task to get started!"
        )

    st.divider()

    # Study streak

    st.subheader("🔥 Your Study Streak")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Current Study Streak",
            f"{current_streak} days"
        )

    with col2:

        weekly_total = sum(
            float(
                data["study_hours"].get(
                    str(date.today() - timedelta(days=i)),
                    0
                )
            )
            for i in range(7)
        )

        st.metric(
            "This Week's Study Hours",
            f"{weekly_total:.1f} hrs"
        )

    if current_streak >= 7:

        st.success(
            "Amazing! You've maintained a 7-day study streak! 🎉"
        )

    elif current_streak > 0:

        st.info(
            "Keep going! Build your daily study habit."
        )

    else:

        st.info(
            "Start studying today to begin your streak!"
        )

    st.divider()

    st.markdown(
        "### 💜 Small steps lead to big achievements."
    )

    st.divider()


# ==========================================
# 9. ATTENDANCE CALCULATOR
# ==========================================

elif page == "Attendance":

    st.header("🎓 Attendance Calculator")

    st.write(
        "Track your attendance and reach your academic goals."
    )

    target = 75

    # Current attendance

    attendance = data["attendance"]

    total_classes = int(attendance["total"])

    attended_classes = int(attendance["attended"])

    percentage = (
        attended_classes / total_classes * 100
        if total_classes > 0 else 0
    )

    # Attendance metrics

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Your Attendance",
            f"{percentage:.1f}%"
        )

    with col2:

        st.metric(
            "Your Target",
            f"{target}%"
        )

    st.progress(
        min(max(percentage / 100, 0.0), 1.0)
    )

    st.divider()

    # Update attendance

    st.subheader("📝 Update Your Attendance")

    with st.form("attendance_form"):

        total = st.number_input(
            "Total classes conducted",
            min_value=0,
            step=1,
            value=total_classes
        )

        attended = st.number_input(
            "Classes attended",
            min_value=0,
            step=1,
            value=attended_classes
        )

        submitted = st.form_submit_button(
            "💾 Save Attendance"
        )

        if submitted:

            if total == 0:

                st.warning(
                    "Enter the total classes first."
                )

            elif attended > total:

                st.error(
                    "Attended classes cannot exceed total classes."
                )

            else:

                data["attendance"] = {
                    "total": int(total),
                    "attended": int(attended)
                }

                save_data(data)

                st.success(
                    "Attendance saved successfully!"
                )

                st.rerun()

    st.divider()

    # 75% attendance goal calculator

    st.subheader("🎯 Your 75% Attendance Goal")

    if total_classes == 0:

        st.info(
            "Save your attendance details to calculate your goal."
        )

    elif percentage < target:

        classes_needed = math.ceil(
            (0.75 * total_classes - attended_classes) / 0.25
        )

        st.warning(
            f"Your attendance is currently {percentage:.1f}%."
        )

        st.markdown(
            f"### You need to attend your next "
            f"**{classes_needed} consecutive classes** "
            f"to reach 75% attendance."
        )

        st.info(
            "Keep attending classes without missing any "
            "to achieve your target!"
        )

    else:

        classes_you_can_miss = math.floor(
            attended_classes / 0.75 - total_classes + 1e-9
        )

        st.success(
            "Congratulations! You have reached your "
            "75% attendance goal! 🎉"
        )

        st.write(
            f"You can miss up to **{classes_you_can_miss} "
            f"additional classes** and still maintain at least 75%, "
            "assuming no other classes are missed."
        )

    st.divider()

    st.caption(
        "StudySpace calculates your attendance using your "
        "saved class records."
    )


# ==========================================
# 10. TASK MANAGER
# ==========================================

elif page == "Tasks":

    st.header("📝 Assignment Manager")

    st.write(
        "Plan your assignments, manage deadlines and track progress."
    )

    tasks = data["tasks"]

    # Task statistics

    total_tasks = len(tasks)

    completed = sum(
        1 for t in tasks
        if t.get("done", False)
    )

    pending = total_tasks - completed

    overdue = sum(
        1 for t in tasks
        if (
            not t.get("done", False)
            and t.get("deadline", "9999-12-31") < str(date.today())
        )
    )

    completion = (
        completed / total_tasks
        if total_tasks > 0 else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📋 Total Tasks", total_tasks)

    col2.metric("⏳ Pending", pending)

    col3.metric("✅ Completed", completed)

    col4.metric("🚨 Overdue", overdue)

    st.progress(completion)

    st.caption(
        f"{completion * 100:.1f}% of your assignments completed"
    )

    st.divider()

    # Add new assignment

    st.subheader("➕ Add New Assignment")

    with st.form("task_form"):

        task_title = st.text_input(
            "Assignment name",
            placeholder="Example: Python project submission"
        )

        col1, col2 = st.columns(2)

        with col1:

            deadline = st.date_input(
                "Submission deadline",
                value=date.today() + timedelta(days=7)
            )

        with col2:

            priority = st.selectbox(
                "Priority",
                ["High", "Medium", "Low"]
            )

        submitted = st.form_submit_button(
            "Add Assignment"
        )

        if submitted:

            if task_title.strip():

                data["tasks"].append({
                    "id": str(uuid.uuid4()),
                    "title": task_title.strip(),
                    "deadline": str(deadline),
                    "priority": priority,
                    "done": False
                })

                save_data(data)

                st.success(
                    "Assignment added successfully!"
                )

                st.rerun()

            else:

                st.warning(
                    "Please enter an assignment name."
                )

    st.divider()

    # Filter tasks

    st.subheader("📚 Your Assignments")

    filter_option = st.selectbox(
        "Filter assignments",
        [
            "All Tasks",
            "Pending",
            "Completed",
            "Overdue"
        ]
    )

    visible_tasks = []

    for task in tasks:

        # Support older saved tasks

        task.setdefault("priority", "Medium")
        task.setdefault("done", False)
        task.setdefault("id", str(uuid.uuid4()))
        task.setdefault("title", "Untitled")
        task.setdefault("deadline", "9999-12-31")

        is_overdue = (
            not task["done"]
            and task["deadline"] < str(date.today())
        )

        if filter_option == "All Tasks":

            visible_tasks.append(task)

        elif filter_option == "Pending" and not task["done"]:

            visible_tasks.append(task)

        elif filter_option == "Completed" and task["done"]:

            visible_tasks.append(task)

        elif filter_option == "Overdue" and is_overdue:

            visible_tasks.append(task)

    # Sort by deadline

    visible_tasks.sort(
        key=lambda t: t["deadline"]
    )

    if visible_tasks:

        for task in visible_tasks:

            with st.container(border=True):

                col1, col2 = st.columns([5, 1])

                with col1:

                    st.markdown(
                        f"### {html.escape(str(task['title']))}"
                    )

                    priority_colors = {
                        "High": "🔴",
                        "Medium": "🟡",
                        "Low": "🟢"
                    }

                    st.write(
                        f"{priority_colors.get(task['priority'], '🟡')} "
                        f"Priority: **{task['priority']}**"
                    )

                    st.caption(
                        f"Deadline: {task['deadline']}"
                    )

                    if task["done"]:

                        st.success("Completed!")

                    elif is_overdue if False else False:
                        pass

                    elif task["deadline"] < str(date.today()):

                        st.error("Overdue!")

                    elif task["deadline"] == str(date.today()):

                        st.warning("Due today!")

                    else:

                        st.info("Pending")

                with col2:

                    if st.button(
                        "🗑️",
                        key=f"delete_{task['id']}"
                    ):

                        data["tasks"] = [
                            t for t in data["tasks"]
                            if t["id"] != task["id"]
                        ]

                        save_data(data)

                        st.rerun()

                new_status = st.checkbox(
                    "Mark as completed",
                    value=task["done"],
                    key=f"complete_{task['id']}"
                )

                if new_status != task["done"]:

                    task["done"] = new_status

                    save_data(data)

                    st.rerun()

    else:

        st.info(
            "No assignments found in this category."
        )

    st.divider()

    st.caption(
        "💜 Stay organised. Complete one assignment at a time."
    )


# ==========================================
# 11. STUDY TRACKER
# ==========================================

elif page == "Study Tracker":

    st.header("⏰ Study Tracker")

    st.write(
        "Track your daily learning hours."
    )

    today = str(date.today())

    today_hours = float(
        data["study_hours"].get(today, 0)
    )

    st.metric(
        "Today's Study Hours",
        f"{today_hours:.1f} hrs"
    )

    with st.form("study_form"):

        study_hours = st.number_input(
            "How many hours did you study today?",
            min_value=0.0,
            max_value=24.0,
            value=min(today_hours, 24.0),
            step=0.5
        )

        submitted = st.form_submit_button(
            "💾 Save Study Hours"
        )

        if submitted:

            data["study_hours"][today] = study_hours

            save_data(data)

            st.success(
                "Your study hours have been saved!"
            )

            st.rerun()

    st.divider()

st.subheader("📊 Your Weekly Study Progress")
st.caption("Track your learning progress over the last 7 days.")

# Correct weekday order
weekday_order = [
    "Mon", "Tue", "Wed", "Thu",
    "Fri", "Sat", "Sun"
]

today_date = date.today()

# Create the last 7 days in chronological order
weekly_dates = [
    today_date - timedelta(days=i)
    for i in range(6, -1, -1)
]

weekly_history = pd.DataFrame({
    "Day": [d.strftime("%a") for d in weekly_dates],
    "Study Hours": [
        float(data["study_hours"].get(str(d), 0))
        for d in weekly_dates
    ]
})

# Force Monday-to-Sunday order
weekly_history["Day"] = pd.Categorical(
    weekly_history["Day"],
    categories=weekday_order,
    ordered=True
)

weekly_history = (
    weekly_history
    .sort_values("Day")
    .set_index("Day")
)

# Display compact chart
st.bar_chart(
    weekly_history,
    height=220
)

# Weekly total
weekly_total = weekly_history["Study Hours"].sum()

st.metric(
    "Total Study Hours This Week",
    f"{weekly_total:.1f} hrs"
)

st.divider()

with st.expander("📚 View All Study Records"):

    if data["study_hours"]:

        history = pd.DataFrame([
            {
                "Date": record_date,
                "Study Hours": float(hours)
            }
            for record_date, hours in sorted(
                data["study_hours"].items(),
                reverse=True
            )
        ])

        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No study records yet.")