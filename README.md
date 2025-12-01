Smart Task Analyzer – Technical Assessment Project

A full-stack mini-application that prioritizes tasks using an intelligent scoring algorithm based on urgency, importance, effort, and dependencies.
Built as part of the Software Development Intern Technical Assessment using Python, Django, HTML, CSS, and JavaScript.

Project Structure
task-analyzer/
│
├── backend/
│   ├── manage.py
│   ├── task_analyzer/
│   ├── tasks/
│   │   ├── serializers.py
│   │   ├── scoring.py      ← Core algorithm logic
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
│
└── README.md

Setup Instructions
1. Clone the repository
git clone https://github.com/swagatikasahu123/Task-Analyzer
cd Task-Analyzer/backend

2. Create virtual environment
python -m venv venv


Activate:

Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate

3. Install Python dependencies
pip install -r requirements.txt

4. Apply migrations
python manage.py migrate

5. Run backend server
python manage.py runserver


Backend will run at:
http://127.0.0.1:8000

6. Run Frontend

Open another terminal:

cd frontend
python -m http.server 5500


Frontend runs on:
 http://127.0.0.1:5500

Algorithm Explanation (400–450 words)

The Smart Task Analyzer uses a multi-factor priority scoring algorithm to help users identify the most important tasks to complete first. Each task contains five key fields: title, due date, estimated hours, importance (1–10), and dependencies. The goal of the algorithm is to evaluate these factors, normalize them, detect special conditions like circular dependencies, and calculate a final priority score between 0 and 1.

1. Urgency

Urgency is based on the number of days until the due date.

Tasks due soon receive a higher urgency score.

Past-due tasks automatically receive the maximum urgency value (1.0).

Tasks without a due date receive low urgency (0.1).

Urgency is computed as:

urgency = max(0, (30 - days_remaining) / 30)


This allows tasks within 30 days to be scaled appropriately.

2. Importance (1–10 scale)

Importance is normalized into a 0–1 score using:

importance_score = (importance - 1) / 9


This ensures consistent weighting across strategies.

3. Effort

Effort represents the number of hours required. Lower-effort tasks (“quick wins”) receive higher scores.
Effort is inverted using:

effort_score = 1 / (1 + estimated_hours)


So 1-hour tasks get higher scores than 10-hour tasks.

4. Dependency Weight

Tasks that block other tasks are treated as more important.
A graph traversal counts how many tasks depend (directly or indirectly) on the current task.
This count is normalized and contributes to the final score.

5. Circular Dependency Detection

Circular dependencies (A → B → C → A) are automatically detected by applying DFS with a recursion stack.
If a cycle exists, the task is flagged and penalized:

final_score *= 0.55

6. Strategies

The system supports four strategies using different weight combinations:

Strategy	Urgency	Importance	Effort	Dependencies
Smart Balance	0.35	0.30	0.20	0.15
Fastest Wins	0.20	0.15	0.50	0.15
High Impact	0.15	0.65	0.10	0.10
Deadline Driven	0.70	0.15	0.05	0.10

The final score is:

score = u*w1 + i*w2 + e*w3 + d*w4


This flexible model ensures tasks are prioritized realistically based on the chosen strategy.

Frontend Functionality

✔ Add individual tasks
✔ Bulk JSON input
✔ Strategy selector
✔ Calls backend APIs using fetch()
✔ Color-coded priority (High/Medium/Low)
✔ Detailed explanation for each task
✔ Responsive layout

Unit Tests

Included tests validate:

Priority score calculation

Circular dependency detection

Strategy behavior

Input validation

Run tests:

python manage.py test

Design Decisions
1. Algorithm-first approach

The algorithm was developed before UI to ensure logical correctness, as required in the assessment.

2. Modular code

Separated files:

scoring.py → all scoring logic

serializers.py → validation

views.py → API endpoints
This increases maintainability.

3. Strategy-based scoring

Allows users to choose different priority models without rewriting code.

4. No database usage

Since tasks are sent in request payloads, a DB is unnecessary and speeds up testing.

⏱ Time Breakdown
Task	Time
Algorithm Design	1 hr
Backend Setup & API	45 min
Scoring Logic Implementation	40 min
Frontend Development	1 hr
Testing & Debugging	20 min
Documentation	20 min
Total	~4 hrs
Bonus Challenges Attempted

✔ Circular Dependency Detection
✔ Multiple Priority Strategies
✔ Detailed Score Explanation

Future Improvements

Add database storage & login

Add visual dependency graph

Add Eisenhower Matrix

Add drag-and-drop UI

Reinforcement-based learning (user feedback improves scores)

Conclusion

This project demonstrates algorithm design, backend API development, frontend interaction, edge-case handling, and clean, modular code structure. It fully satisfies the requirements for the Software Development Intern Technical Assessment.
