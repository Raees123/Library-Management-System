from flask import Blueprint, render_template, request, redirect, flash, url_for
from models import db, Book, Member, Transaction, Stock, Charges
import datetime
from sqlalchemy import desc
#from sqlalchemy.exc import IntegrityError

class BorrowingManager:
    borrowing_blueprint = Blueprint('borrowing', __name__)

    @staticmethod
    def calculate_dbt(member):
        dbt = 100
        charge = db.session.query(Charges).first()
        transactions = db.session.query(Transaction).filter_by(member_id=member.id, return_date=None).all()

        for transaction in transactions:
            days_difference = (datetime.date.today() - transaction.issue_date.date()).days
            if days_difference > 0:
                dbt += days_difference * charge.rentfee
        return dbt

    @staticmethod
    @borrowing_blueprint.route('/issuebook', methods=['GET', 'POST'])
    def issue_book():
        if request.method == "POST":
            memberid = request.form['mk']
            title = request.form['bk']

            book = db.session.query(Book, Stock).join(Stock).filter(
                Book.title.like(f'%{title}%')).first() or db.session.query(Book, Stock).join(Stock).filter(
                Book.id.like(title)).first()

            mem = db.session.query(Member).get(memberid)
            if not book and not mem:
                flash("Member not found and Book Not Found.", "error")
                return redirect('/borrowing/issuebook')
            elif not mem:
                flash("Member not found .", "error")
                return redirect('/borrowing/issuebook')
            elif not book:
                flash("Book not found .", "error")
                return redirect('/borrowing/issuebook')

            dbt =BorrowingManager.calculate_dbt(mem)
            return render_template('issuebook.html', book=book, member=mem, debt=dbt)

        return render_template('issuebook.html')

    @staticmethod
    @borrowing_blueprint.route('/issuebookconfirm', methods=['POST'])
    def issue_book_confirm():
        if request.method == "POST":
            memberid = request.form['memberid']
            bookid = request.form['bookid']

            stock = db.session.query(Stock).filter_by(book_id=bookid).first()
            if stock.available_quantity <= 0:
                flash("Book is not available for issuance.", "error")
                return redirect('/borrowing/issuebook')

            new_transaction = Transaction(book_id=bookid, member_id=memberid, issue_date=datetime.date.today())
            print(new_transaction)

            stock.available_quantity -= 1
            stock.borrowed_quantity += 1
            stock.total_borrowed += 1

            db.session.add(new_transaction)
            db.session.commit()

            flash("Transaction added successfully", "success")
            return redirect('/borrowing/issuebook')

        return render_template('issuebook.html')

    @staticmethod
    @borrowing_blueprint.route('/transactions', methods=['GET', 'POST'])
    def view_borrowings():
        # Filter transactions to include only unreturned books
        transactions = db.session.query(Transaction, Member, Book).join(Book).join(Member).filter(
            Transaction.return_date == None
        ).order_by(desc(Transaction.issue_date)).all()

        if request.method == "POST":
            search = request.form['search']

            transactions_by_name = db.session.query(Transaction, Member, Book).join(Book).join(Member).filter(
                Transaction.return_date == None,
                Member.name.like(f'%{search}%')
            ).order_by(desc(Transaction.issue_date)).all()

            transaction_by_id = db.session.query(Transaction, Member, Book).join(Book).join(Member).filter(
                Transaction.return_date == None,
                Transaction.id == search
            ).order_by(desc(Transaction.issue_date)).all()

            if transactions_by_name:
                transactions = transactions_by_name
            elif transaction_by_id:
                transactions = transaction_by_id
            else:
                transactions = []

        return render_template('transactions.html', trans=transactions)

    @staticmethod
    @borrowing_blueprint.route('/view_member/<int:id>')
    def view_member(id):
        member = Member.query.get(id)
        transaction = Transaction.query.filter_by(member_id=member.id).all()
        dbt = BorrowingManager.calculate_dbt(member)
        return render_template('view_member.html', member=member, trans=transaction, debt=dbt)

    @staticmethod
    @borrowing_blueprint.route('/returnbook/<int:id>', methods=['GET', 'POST'])
    def return_book(id):
        transaction = db.session.query(Transaction, Member, Book).join(Book).join(Member).filter(
            Transaction.id == id).first()
        rent = BorrowingManager.calculate_rent(transaction)
        print(rent)
        return render_template("returnbook.html", trans=transaction, rent=rent)

    @staticmethod
    @borrowing_blueprint.route('/returnbookconfirm', methods=['POST'])
    def return_book_confirm():
        if request.method == "POST":
            id = request.form["id"]
            trans, member = db.session.query(Transaction, Member).join(Member).filter(Transaction.id == id).first()
            stock = Stock.query.filter_by(book_id=trans.book_id).first()
            charge = Charges.query.first()
            if not charge:
                charge = 100
                rent = (datetime.date.today() - trans.issue_date.date()).days * charge
            else:
                rent = (datetime.date.today() - trans.issue_date.date()).days * charge.rentfee
            if stock:
                stock.available_quantity += 1
                stock.borrowed_quantity -= 1

                trans.return_date = datetime.date.today()
                trans.rent_fee = rent
                db.session.commit()
                flash(f"{member.name} Returned book successfully", 'success')
            else:
                flash("Error updating stock information", 'error')

        return redirect('transactions')

    @staticmethod
    def calculate_debt(member):
        charges = Charges.query.first()
        transactions = Transaction.query.filter_by(member_id=member.id, return_date=None).all()

        debt = 0
        for transaction in transactions:
            overdue_days = (datetime.date.today() - transaction.issue_date).days
            if overdue_days > 0:
                debt += overdue_days * (charges.rentfee if charges else 10)

        return debt

    @staticmethod
    def calculate_rent(transaction):
        charge = Charges.query.first()
        if not charge:
            charge = 100
            rent = (datetime.date.today() - transaction.Transaction.issue_date.date()).days * charge
        else:
            print(f"charge----{charge}")
            rent = (datetime.date.today() - transaction.Transaction.issue_date.date()).days * charge.rentfee

        return rent
