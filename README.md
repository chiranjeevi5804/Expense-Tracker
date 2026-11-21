
# Expense Tracker

A web-based personal finance management application built using Python, Flask, SQLite, HTML, CSS and JavaScript.

The application helps users record daily expenses, organize spending by category, create monthly budgets and monitor their financial activities through an interactive dashboard.

## Features

- **Expense Management:** Add, view, edit and delete expenses.
- **Category Management:** Create and organize expense categories.
- **Monthly Budgets:** Set and update budgets for individual categories.
- **Budget Alerts:** Identify categories where spending exceeds the allocated budget.
- **Dashboard Analytics:** View monthly spending, transaction counts and average expenses.
- **Visual Reports:** Analyze category-wise spending through interactive charts.
- **Monthly Reports:** View spending, budget and remaining balance by category.
- **CSV Export:** Download monthly financial reports.
- **Responsive Interface:** Dark-themed dashboard suitable for desktop and mobile screens.
- **Input Validation:** Validate expense amounts, categories and budget details.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| Flask-SQLAlchemy | Database integration |
| SQLite | Database |
| HTML5 | Web page structure |
| CSS3 | Dashboard styling |
| JavaScript | Frontend functionality |
| Chart.js | Data visualization |
| Docker | Application containerization |

## Project Structure

```text
Expense-Tracker/
│
├── app.py
├── run.py
├── models.py
├── views.py
├── commands.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── README.md
├── test_basic.py
│
├── templates/
│   └── index.html
│
└── static/
    └── style.css
```

## Application Modules

### 1. Expense Management
Users can record expenses with descriptions, amounts and categories. Existing records can be edited or deleted.

### 2. Category Management
Users can create categories to organize expenses and understand spending patterns.

### 3. Budget Management
Monthly budgets can be assigned to individual categories. The application compares actual expenses against allocated budgets.

### 4. Dashboard and Analytics
The dashboard displays total monthly spending, transaction count, average expense, total budget and category-wise spending charts.

### 5. Monthly Reports
Users can review monthly financial summaries and download reports in CSV format.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Dashboard homepage |
| GET, POST | `/categories` | View and add categories |
| GET, POST | `/expenses` | View and add expenses |
| PUT, DELETE | `/expenses/<id>` | Update or delete an expense |
| GET, POST | `/budgets` | View and save budgets |
| GET | `/reports/monthly?month=YYYY-MM` | Monthly spending report |
| GET | `/reports/monthly.csv?month=YYYY-MM` | Download monthly CSV report |

## Installation

1. Clone the repository:

```bash
git clone https://github.com/chiranjeevi5804/L7.git
```

2. Navigate to the project directory:

```bash
cd L7
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Initialize the database:

```bash
flask --app run.py db-init
```

5. Start the application:

```bash
python run.py
```

6. Open the application in your browser:

```text
http://127.0.0.1:5000
```

## Docker Setup

Build and start the application:

```bash
docker compose up --build
```

Access the application at:

```text
http://localhost:5000
```

## Database

The application uses SQLite with three primary database models:

- **Category:** Stores expense categories.
- **Expense:** Stores expense descriptions, amounts, categories and dates.
- **Budget:** Stores category-wise monthly budget allocations.

## Future Enhancements

- User authentication and personalized accounts.
- Advanced financial analytics.
- Monthly and yearly comparison reports.
- Recurring expense management.
- Enhanced data visualization.

## Author

Developed as a personal finance management project.
