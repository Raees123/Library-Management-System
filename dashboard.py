from flask import Blueprint, render_template
from models import db, Book, Transaction, Member
import datetime

class DashboardManager:
    dashboard_blueprint = Blueprint('dashboard', __name__)

    @staticmethod
    @dashboard_blueprint.route('/')
    def index():
        borrowed_books = db.session.query(Transaction).filter(Transaction.return_date == None).count()
        total_books = Book.query.count()
        total_members = Member.query.count()
        total_rent_current_month = DashboardManager.calculate_total_rent_current_month()
        recent_transactions = db.session.query(Transaction, Book).join(Book).order_by(Transaction.issue_date.desc()).limit(
            5).all()

        return render_template(
            'index.html',
            borrowed_books=borrowed_books,
            total_books=total_books,
            total_members=total_members,
            recent_transactions=recent_transactions,
            total_rent_current_month=total_rent_current_month
        )

    @staticmethod
    def calculate_total_rent_current_month():
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year
        start_date = datetime.datetime(current_year, current_month, 1)

        if current_month == 12:
            end_date = datetime.datetime(current_year, 12, 31)
        else:
            end_date = datetime.datetime(current_year, current_month + 1, 1) - datetime.timedelta(days=1)

        total_rent = db.session.query(db.func.sum(Transaction.rent_fee)).filter(
            Transaction.issue_date >= start_date,
            Transaction.issue_date <= end_date
        ).scalar()

        return total_rent if total_rent else 0
