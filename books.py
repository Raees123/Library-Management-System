from flask import Blueprint, render_template, request, redirect, flash, url_for
from models import db, Book, Stock, Transaction
from sqlalchemy.exc import IntegrityError

class BookManager:
    books_blueprint = Blueprint('books', __name__)

    @staticmethod
    @books_blueprint.route('/add_book', methods=['GET', 'POST'])
    def add_book():
        if request.method == 'POST':
            try:
                title = request.form['title']
                author = request.form['author']
                isbn = request.form['isbn']
                publisher = request.form['publisher']
                page = int(request.form['page'])
                stock = int(request.form['stock'])

                new_book = Book(title=title, author=author, isbn=isbn, publisher=publisher, page=page)
                db.session.add(new_book)
                db.session.flush()

                new_stock = Stock(book_id=new_book.id, total_quantity=stock, available_quantity=stock)
                db.session.add(new_stock)
                db.session.commit()

                flash('Book added successfully!', 'success')
            except IntegrityError:
                db.session.rollback()
                flash('Error adding book. Please check the details.', 'error')
            return redirect(url_for('books.add_book'))

        return render_template('add_book.html')

    @staticmethod
    @books_blueprint.route('/view_books', methods=['GET', 'POST'])
    def view_books():
        if request.method == 'POST':
            title = request.form.get('searcht', '')
            author = request.form.get('searcha', '')
            books = db.session.query(Book, Stock).join(Stock).filter(
                Book.title.like(f'%{title}%'),
                Book.author.like(f'%{author}%')
            ).all()
        else:
            books = db.session.query(Book, Stock).join(Stock).all()

        return render_template('view_books.html', books=books)

    @staticmethod
    @books_blueprint.route('/edit_book/<int:id>', methods=['GET', 'POST'])
    def edit_book(id):
        book = Book.query.get(id)
        stock = Stock.query.filter_by(book_id=id).first()
        if request.method == 'POST':
            try:
                book.title = request.form['title']
                book.author = request.form['author']
                book.isbn = request.form['isbn']
                book.publisher = request.form['publisher']
                book.page = int(request.form['page'])
                stock.total_quantity = int(request.form['stock'])

                db.session.commit()
                flash('Book updated successfully!', 'success')
            except IntegrityError:
                db.session.rollback()
                flash('Error updating book. Please check the details.', 'error')

        return render_template('edit_book.html', book=book, stock=stock)

    @staticmethod
    @books_blueprint.route('/delete_book/<int:id>', methods=['GET', 'POST'])
    def delete_book(id):
        try:
            book = Book.query.get(id)
            stock = Stock.query.filter_by(book_id=book.id).first()
            db.session.delete(book)
            db.session.delete(stock)
            db.session.commit()
            flash('Book removed successfully!', 'success')
        except IntegrityError as e:
            db.session.rollback()
            flash(f'Error removing book: {e}', 'error')

        return redirect(url_for('books.view_books'))

    @staticmethod
    @books_blueprint.route('/view_book/<int:id>')
    def view_book(id):
        book = Book.query.get(id)
        stock = Stock.query.filter_by(book_id=id).first()
        transaction = Transaction.query.filter_by(book_id=id).all()
        return render_template('view_book.html', book=book, trans=transaction, stock=stock)
