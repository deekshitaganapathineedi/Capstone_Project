from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Flask app setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://deekshita:deekshita123@DESKTOP-90EC5LN\\SQLEXPRESS/RetailDB?driver=ODBC+Driver+17+for+SQL+Server&timeout=80'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


if not os.path.exists('static/charts'):
    os.makedirs('static/charts')


def load_data(query):
    connection=db.engine.connect()
    df=pd.read_sql(query,connection)
    connection.close()
    return df


def create_charts():
    charts=[]
    scale_factor=1_000_000

    def plot_and_save(data,x,y,kind,title,xlabel,ylabel,filepath,palette=None):

        plt.figure(figsize=(8, 5))
        if kind=="bar":
            sns.barplot(data=data,x=x,y=y,palette=palette)
        elif kind=="line":
            sns.lineplot(data=data,x=x,y=y,marker='o',color=palette)
        elif kind=="hist":
            sns.histplot(data[x], kde=True, color=palette)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.savefig(filepath)
        charts.append(filepath)
        plt.close()

    # Query 1: Total Loan Amount Disbursed by Geography
    query1 = """
        SELECT 
            g.City, g.State, 
            SUM(CAST(REPLACE(REPLACE(f.DisbursementGross, '$', ''), ',', '') AS DECIMAL(18,2))) AS TotalLoanDisbursed
        FROM Loan_Fact f
        JOIN dim_geography_data g ON f.Geography_ID = g.Geography_ID
        WHERE ISNUMERIC(REPLACE(REPLACE(f.DisbursementGross, '$', ''), ',', '')) = 1
        GROUP BY g.City, g.State
        ORDER BY TotalLoanDisbursed DESC;
    """
    geography_df=load_data(query1)
    if not geography_df.empty:
        geography_df['TotalLoanDisbursed']/= scale_factor
        plot_and_save(
            geography_df.head(10),
            x='TotalLoanDisbursed',
            y='City',
            kind="bar",
            title='Top 10 Cities by Total Loan Disbursed (in millions)',
            xlabel='Total Loan Disbursed (in millions)',
            ylabel='City',
            filepath='static/charts/total_loan_disbursed_by_city.png',
            palette='Blues_r'
        )

    # Query 2: Number of Loans Approved by Year
    query2 = """
        SELECT 
            l.ApprovalFY AS ApprovalYear, 
            COUNT(l.LoanNr_ChkDgt) AS LoanCount
        FROM dim_LoanDetails_Dimension l
        GROUP BY l.ApprovalFY
        ORDER BY ApprovalYear;
    """
    loans_by_year_df = load_data(query2)
    if not loans_by_year_df.empty:
        plot_and_save(
            loans_by_year_df,
            x='ApprovalYear',
            y='LoanCount',
            kind="line",
            title='Number of Loans Approved by Year',
            xlabel='Year',
            ylabel='Number of Loans Approved',
            filepath='static/charts/loans_approved_by_year.png',
            palette='green'
        )

    # Query 3: Jobs Created or Retained per Business
    query3 = """
        SELECT 
            bb.Name,
            SUM(bb.CreateJob) AS TotalCreated,
            SUM(bb.RetainedJob) AS TotalRetained,
            SUM(bb.CreateJob + bb.RetainedJob) AS TotalJobs
        FROM dim_borrower_data bb
        GROUP BY bb.Name
        ORDER BY TotalJobs DESC;
    """
    jobs_df = load_data(query3)
    if not jobs_df.empty:
        plot_and_save(
            jobs_df.head(10),
            x='TotalJobs',
            y='Name',
            kind="bar",
            title='Top 10 Businesses by Total Jobs (Created + Retained)',
            xlabel='Total Jobs (Created + Retained)',
            ylabel='Business Name',
            filepath='static/charts/top_businesses_by_jobs.png',
            palette='Oranges_r'
        )

    # Query 4: Loans by Urban vs. Rural Areas
    query4= """
        SELECT 
            bb.UrbanRural,
            COUNT(f.ID) AS LoanCount, 
            SUM(CAST(REPLACE(REPLACE(f.DisbursementGross, '$', ''), ',', '') AS DECIMAL(18,2))) AS TotalLoanDisbursed
        FROM Loan_Fact f
        JOIN dim_borrower_data bb ON f.Borrower_ID = bb.Borrower_ID
        GROUP BY bb.UrbanRural
        ORDER BY TotalLoanDisbursed DESC;
    """
    urban_rural_df = load_data(query4)
    if not urban_rural_df.empty:
        urban_rural_df['TotalLoanDisbursed'] /= scale_factor
        plot_and_save(
            urban_rural_df,
            x='UrbanRural',
            y='TotalLoanDisbursed',
            kind="bar",
            title='Loans by Urban vs. Rural Areas (in millions)',
            xlabel='Urban (1) / Rural (0)',
            ylabel='Total Loan Disbursed (in millions)',
            filepath='static/charts/urban_vs_rural_loans.png',
            palette='coolwarm'
        )
    query5 = """
            SELECT 
                YEAR(f.DisbursementDate) AS LoanYear,
                SUM(CAST(REPLACE(REPLACE(f.DisbursementGross, '$', ''), ',', '') AS DECIMAL(18,2))) AS TotalDisbursed
            FROM Loan_Fact f
            WHERE f.DisbursementDate IS NOT NULL
            GROUP BY YEAR(f.DisbursementDate)
            ORDER BY LoanYear;
        """
    trends_df = load_data(query5)
    if not trends_df.empty:
        trends_df['TotalDisbursed'] /= scale_factor
        plot_and_save(
            trends_df,
            x='LoanYear',
            y='TotalDisbursed',
            kind="line",
            title='Loan Disbursement Trends by Year (in millions)',
            xlabel='Year',
            ylabel='Total Loan Disbursed (in millions)',
            filepath='static/charts/loan_disbursement_trends.png',
            palette='blue'
        )

    return charts


# Flask routes


@app.route('/dashboard')
def dashboard():
    charts = create_charts()
    return render_template('dashboard_cap.html', charts=charts)

# Main app runner
if __name__ == '__main__':
    app.run(debug=True)
