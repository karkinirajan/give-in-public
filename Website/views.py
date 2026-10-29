import json

from dateutil import parser
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from jinja2 import TemplateNotFound
from sqlalchemy import desc, func

from . import db
from .models import Donation, User

views = Blueprint("views", __name__, template_folder="templates")


@views.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html", user=current_user)


@views.route("/mission")
def mission():
    try:
        return render_template("vision.html")
    except TemplateNotFound:  # the page was never written; 404 rather than a server error
        abort(404)


@views.route("/subscribe")
def subscribe():
    return render_template("form.html")


@views.route("/dashboard/configure", methods=["GET", "POST"])
@login_required
def configureDashboard():
    if request.method == "POST":
        organisation = request.form.get("organisation-name")
        amount = request.form.get("donation-amount", "")
        description = request.form.get("donation-description")
        try:
            date_donated = parser.parse(request.form.get("donation-date", ""))
        except (ValueError, OverflowError):
            date_donated = None

        if not amount.isdigit():
            flash("Please enter a valid digit", category="error")
        elif date_donated is None:
            flash("Please enter a valid date", category="error")
        else:
            db.session.add(
                Donation(
                    amount=int(amount),
                    description=description,
                    organisation=organisation,
                    date_donated=date_donated,
                    user_id=current_user.id,
                )
            )
            db.session.commit()

    total_donations = db.session.query(
        db.func.sum(Donation.amount).filter(Donation.user_id == current_user.id)
    ).scalar()
    donations_by_grp = (
        db.session.query(db.func.sum(Donation.amount), Donation.organisation)
        .filter(Donation.user_id == current_user.id)
        .group_by(Donation.organisation)
        .all()
    )

    return render_template(
        "Configure.html",
        user=current_user,
        total_donations=total_donations,
        donations_by_grp=donations_by_grp,
    )


@views.route("/delete/<int:id>", methods=["POST"])
@login_required
def deleteDonation(id):
    donation = db.get_or_404(Donation, id)
    if donation.user_id != current_user.id:
        abort(403)
    db.session.delete(donation)
    db.session.commit()
    return redirect(url_for("views.configureDashboard"))


@views.route("/dashboard/public/<int:id>")
def publicdashboard(id):

    # user = db.session.query(User).filter(User.id==id).all()

    user = db.get_or_404(User, id)
    total_donations = db.session.query(
        db.func.sum(Donation.amount).filter(Donation.user_id == id)
    ).scalar()
    donations_by_grp = (
        db.session.query(db.func.sum(Donation.amount), Donation.organisation)
        .filter(Donation.user_id == id)
        .group_by(Donation.organisation)
        .all()
    )
    dates = (
        db.session.query(db.func.sum(Donation.amount), Donation.date_donated)
        .filter(Donation.user_id == id)
        .group_by(Donation.date_donated)
        .order_by(Donation.date_donated)
        .all()
    )

    total = func.sum(Donation.amount).label("Total")
    sum_donations = (
        db.session.query(User.first_name, Donation.user_id, total)
        .join(User, Donation.user_id == User.id)
        .group_by(Donation.user_id, User.first_name)
        .order_by(desc(total))
        .all()
    )

    groups_donations = []
    amount_by_grp = []

    for amount, groups in donations_by_grp:
        amount_by_grp.append(amount)
        groups_donations.append(groups)

    over_time_donations = []
    dates_labels = []
    cum_amount = 0

    for amount, date_donated in dates:
        cum_amount = cum_amount + amount
        over_time_donations.append(cum_amount)
        dates_labels.append(date_donated.strftime("%Y-%m-%d"))

    return render_template(
        "publicdashboard.html",
        user=user,
        total_donations=total_donations,
        donations_by_grp=donations_by_grp,
        over_time_donations=json.dumps(over_time_donations),
        dates_labels=json.dumps(dates_labels),
        groups_donations=json.dumps(groups_donations),
        amount_by_grp=json.dumps(amount_by_grp),
        sum_donations=sum_donations,
    )


@views.route("/dashboard/manage-plan")
@login_required
def manageplan():
    return render_template("managePlan.html", user=current_user)


@views.route("/dashboard/feedback")
@login_required
def feedback():
    return render_template("feedback.html", user=current_user)
