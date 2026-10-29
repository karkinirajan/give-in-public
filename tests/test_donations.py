from datetime import date

from Website import db
from Website.models import Donation


def add_donation(user, amount=50, org="Red Cross", day=date(2026, 1, 5)):
    d = Donation(
        amount=amount, organisation=org, description="x", date_donated=day, user_id=user.id
    )
    db.session.add(d)
    db.session.commit()
    return d


def test_pages_render_for_anonymous_visitors(client):
    assert client.get("/").status_code == 200
    assert client.get("/subscribe").status_code == 200
    assert client.get("/login").status_code == 200
    assert client.get("/signup").status_code == 200


def test_mission_page_is_404_not_500_when_template_missing(client):
    assert client.get("/mission").status_code == 404


def test_dashboard_requires_login(client):
    for path in ("/dashboard/configure", "/dashboard/manage-plan", "/dashboard/feedback"):
        assert client.get(path).status_code == 302


def test_logged_in_pages_render(client, make_user, login):
    make_user()
    login()
    for path in ("/dashboard/configure", "/dashboard/manage-plan", "/dashboard/feedback"):
        assert client.get(path).status_code == 200


def test_add_donation(client, make_user, login):
    user = make_user()
    login()
    res = client.post(
        "/dashboard/configure",
        data={
            "organisation-name": "Red Cross",
            "donation-amount": "75",
            "donation-description": "Flood relief",
            "donation-date": "2026-02-01",
        },
    )
    assert res.status_code == 200
    d = Donation.query.one()
    assert (d.amount, d.organisation, d.user_id) == (75, "Red Cross", user.id)


def test_invalid_amount_or_date_is_rejected_without_crashing(client, make_user, login):
    make_user()
    login()
    base = {"organisation-name": "X", "donation-description": "d"}
    assert (
        client.post(
            "/dashboard/configure",
            data=base | {"donation-amount": "abc", "donation-date": "2026-02-01"},
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/dashboard/configure",
            data=base | {"donation-amount": "5", "donation-date": "not a date"},
        ).status_code
        == 200
    )
    assert client.post("/dashboard/configure", data=base).status_code == 200
    assert Donation.query.count() == 0


def test_delete_is_post_only_and_owner_only(client, make_user, login):
    alice, bob = make_user(), make_user("bob@example.com", name="Bob")
    bobs = add_donation(bob)
    login()
    assert client.get(f"/delete/{bobs.id}").status_code == 405  # no delete-by-link
    assert client.post(f"/delete/{bobs.id}").status_code == 403
    assert db.session.get(Donation, bobs.id) is not None
    mine = add_donation(alice)
    res = client.post(f"/delete/{mine.id}")
    assert res.status_code == 302
    assert db.session.get(Donation, mine.id) is None


def test_delete_unknown_id_is_404(client, make_user, login):
    make_user()
    login()
    assert client.post("/delete/999").status_code == 404


def test_public_dashboard_aggregates_and_is_public(client, make_user):
    user = make_user()
    add_donation(user, 10, "A", date(2026, 1, 1))
    add_donation(user, 30, "A", date(2026, 1, 2))
    add_donation(user, 5, "B", date(2026, 1, 2))
    res = client.get(f"/dashboard/public/{user.id}")
    assert res.status_code == 200
    page = res.get_data(as_text=True)
    assert "45" in page  # total
    assert client.get("/dashboard/public/9999").status_code == 404
