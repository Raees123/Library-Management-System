from flask import Flask
from flask_migrate import Migrate
from models import db
from books import BookManager
from members import MemberManager
from borrowing import BorrowingManager
from dashboard import DashboardManager

class LibraryApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.configure_app()
        db.init_app(self.app)
        self.migrate = Migrate(self.app, db)
        self.register_blueprints()

    def configure_app(self):
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
        self.app.config['SECRET_KEY'] = 'af9d4e10d142994285d0c1f861a70925'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    def register_blueprints(self):
        self.app.register_blueprint(DashboardManager.dashboard_blueprint, url_prefix='/')
        self.app.register_blueprint(BookManager.books_blueprint, url_prefix='/books')
        self.app.register_blueprint(MemberManager.members_blueprint, url_prefix='/members')
        self.app.register_blueprint(BorrowingManager.borrowing_blueprint, url_prefix='/borrowing')

    def run(self, host='127.0.0.1', port=5000):
        self.app.run(host=host, port=port)

if __name__ == '__main__':
    library_app = LibraryApp()
    library_app.run()
