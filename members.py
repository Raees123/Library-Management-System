from flask import Blueprint, render_template, request, redirect, flash, url_for
from models import db, Member, Transaction
from sqlalchemy.exc import IntegrityError

class MemberManager:
    members_blueprint = Blueprint('members', __name__)

    @staticmethod
    @members_blueprint.route('/add_member', methods=['GET', 'POST'])
    def add_member():
        if request.method == 'POST':
            try:
                name = request.form['name']
                email = request.form['email']
                phone = request.form['phone']
                address = request.form['address']

                new_member = Member(name=name, email=email, phone=phone, address=address)
                db.session.add(new_member)
                db.session.commit()

                flash('Member added successfully!', 'success')
            except IntegrityError:
                db.session.rollback()
                flash('Error adding member. Please check the details.', 'error')
            return redirect(url_for('members.add_member'))

        return render_template('add_member.html')

    @staticmethod
    @members_blueprint.route('/view_member', methods=['GET', 'POST'])
    def view_members():
        if request.method == 'POST':
            search = request.form.get('search')
            member = db.session.query(Member).filter(Member.name.like(f'%{search}%')).all()
        else:
            member = db.session.query(Member).all()

        return render_template('view_members.html', member=member)

    @staticmethod
    @members_blueprint.route('/edit_member/<int:id>', methods=['GET', 'POST'])
    def edit_member(id):
        member = Member.query.get(id)
        if request.method == 'POST':
            try:
                member.name = request.form['name']
                member.email = request.form['email']
                member.phone = request.form['phone']
                member.address = request.form['address']

                db.session.commit()
                flash('Member updated successfully!', 'success')
            except IntegrityError:
                db.session.rollback()
                flash('Error updating member. Please check the details.', 'error')

        return render_template('edit_member.html', member=member)

    @staticmethod
    @members_blueprint.route('/delete_member/<int:id>', methods=['GET', 'POST'])
    def delete_member(id):
        try:
            member = Member.query.get(id)
            db.session.delete(member)
            db.session.commit()
            flash('Member removed successfully!', 'success')
        except IntegrityError as e:
            db.session.rollback()
            flash(f'Error removing member: {e}', 'error')

        return redirect(url_for('members.view_members'))
