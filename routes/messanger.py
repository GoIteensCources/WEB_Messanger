from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import select
from werkzeug.security import check_password_hash, generate_password_hash

from models import Friends, Message, User
from settings import DatabaseConfig, Session, cache


bp = Blueprint("messanger", __name__)


@bp.route("/search_friends", methods=["GET", "POST"])
@login_required
def search_friends():
    found_user = None
    if request.method == "POST":
        username = request.form["username"]
        found_user = User.get_by_username(username)

        if not found_user:
            flash("Користувача не знайдено.")
        elif found_user.id == current_user.id:
            flash("Не можна додати самого себе.")
        else:
            # Перевірка чи вже є дружба або запит
            with Session() as db:
                stmt = select(Friends).filter_by(
                    sender=current_user.id, recipient=found_user.id
                )

                existing = db.scalar(stmt)
                if existing:
                    flash("Запит вже існує або ви вже друзі.")
                else:
                    friend_request = Friends(
                        sender=current_user.id, recipient=found_user.id, status=False
                    )
                    db.add(friend_request)
                    db.commit()
                    flash("Запит у друзі надіслано!")
    return render_template("messanger/search_friends.html", found_user=found_user)


@bp.route("/friend_requests")
@login_required
def friend_requests():
    with Session() as session_db:
        # Отримуємо всі запити на дружбу, надіслані поточному користувачу
        stmt = select(Friends).where(
            Friends.recipient == current_user.id, Friends.status == False
        )
        friend_requests = session_db.execute(stmt).scalars().all()

        # Отримуємо деталі користувачів, які надіслали запити
        senders = {}
        for req in friend_requests:
            sender = User.get(req.sender)
            senders[req.sender] = sender

    return render_template(
        "messanger/friend_requests.html",
        friend_requests=friend_requests,
        senders=senders,
    )


@bp.route("/friend_requests/accept/<int:request_id>")
@login_required
def accept_friend_request(request_id):
    with Session() as session_db:
        # Знаходимо запит на дружбу
        stmt = select(Friends).where(
            Friends.id == request_id, Friends.recipient == current_user.id
        )
        friend_request = session_db.execute(stmt).scalar()

        if friend_request:
            # Підтверджуємо запит
            friend_request.status = True
            session_db.commit()
            flash("Запит на дружбу прийнято!")
        else:
            flash("Запит на дружбу не знайдено.")

    return redirect(url_for("messanger.friend_requests"))


@bp.route("/friend_requests/decline/<int:request_id>")
@login_required
def decline_friend_request(request_id):
    with Session() as session_db:
        # Знаходимо запит на дружбу
        stmt = select(Friends).where(
            Friends.id == request_id, Friends.recipient == current_user.id
        )
        friend_request = session_db.execute(stmt).scalar()

        if friend_request:
            # Видаляємо запит
            session_db.delete(friend_request)
            session_db.commit()
            flash("Запит на дружбу відхилено.")
        else:
            flash("Запит на дружбу не знайдено.")

    return redirect(url_for("messanger.friend_requests"))


def make_cache_key():
    return f"user {current_user.id}|{request.full_path}"


@bp.route("/my_friends")
@cache.cached(timeout=5*60, key_prefix=make_cache_key) # type: ignore
@login_required
def my_friends():
    with Session() as session:
        all_friends1 = (
            session.query(Friends).filter_by(sender=current_user.id, status=True).all()
        )
        all_friends2 = (
            session.query(Friends)
            .filter_by(recipient=current_user.id, status=True)
            .all()
        )
        friend_names = []
        for i in all_friends1:
            friend_names.append(i.recipient_user)
        for i in all_friends2:
            friend_names.append(i.sender_user)
        return render_template("messanger/my_friends.html", friends=friend_names)


@bp.route("/messages/create/<recipient_name>", methods=["get", "post"])
@login_required
def create_message(recipient_name):
    if request.method == "POST":
        message_text = request.form["text"]
        with Session() as session:
            user_recipient = (
                session.query(User).filter_by(username=recipient_name).first()
            )
            if not user_recipient:
                flash("Отримувача не знайдено", "danger")
                return render_template("messanger/create_message.html")

            check_request1 = (
                session.query(Friends)
                .filter_by(
                    sender=user_recipient.id, recipient=current_user.id, status=True
                )
                .first()
            )
            check_request2 = (
                session.query(Friends)
                .filter_by(
                    sender=current_user.id, recipient=user_recipient.id, status=True
                )
                .first()
            )

            if check_request1 or check_request2:
                new_message = Message(
                    sender=current_user.id,
                    recipient=user_recipient.id,
                    message_text=message_text,
                )
                session.add(new_message)
                session.commit()
                flash("Повідомлення надіслано!", "success")
            else:
                flash("Отримувача не являється другом", "danger")
    return render_template("messanger/send_message.html", for_user=recipient_name)


@bp.route("/new_messages")
@login_required
def new_messages():
    with Session() as session:
        # unread_messages
        stmt = select(Message).filter_by(recipient=current_user.id, status_check=False)
        new_messages = session.scalars(stmt).fetchall()

        name_text_list = []
        for i in new_messages:
            name_text_list.append({i.sender_user.username: i.message_text})
            i.status_check = True
            session.commit()

    return render_template("messanger/new_messages.html", data=name_text_list)
