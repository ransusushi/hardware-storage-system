"""CRUD views for customers."""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..auth import login_required, role_required
from ..db import execute, query_all, query_one

bp = Blueprint("customers", __name__, url_prefix="/customers")


@bp.route("/")
@login_required
def list_view():
    rows = query_all("SELECT * FROM customers ORDER BY full_name")
    return render_template("customers/list.html", rows=rows)


def _form_values():
    return (
        request.form["full_name"].strip(),
        request.form["email"].strip(),
        request.form.get("phone", "").strip() or None,
        request.form.get("address", "").strip() or None,
        request.form.get("city", "").strip() or None,
        request.form.get("customer_type", "retail"),
    )


@bp.route("/new", methods=("GET", "POST"))
@role_required("admin", "manager", "staff")
def create():
    if request.method == "POST":
        execute(
            """INSERT INTO customers (full_name, email, phone, address, city, customer_type)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            _form_values(),
        )
        flash("Customer created.", "success")
        return redirect(url_for("customers.list_view"))
    return render_template("customers/form.html", row=None)


@bp.route("/<int:customer_id>/edit", methods=("GET", "POST"))
@role_required("admin", "manager", "staff")
def edit(customer_id: int):
    row = query_one("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
    if row is None:
        flash("Customer not found.", "warning")
        return redirect(url_for("customers.list_view"))
    if request.method == "POST":
        execute(
            """UPDATE customers SET full_name=%s, email=%s, phone=%s, address=%s,
               city=%s, customer_type=%s WHERE customer_id=%s""",
            (*_form_values(), customer_id),
        )
        flash("Customer updated.", "success")
        return redirect(url_for("customers.list_view"))
    return render_template("customers/form.html", row=row)


@bp.route("/<int:customer_id>/delete", methods=("POST",))
@role_required("admin", "manager")
def delete(customer_id: int):
    try:
        execute("DELETE FROM customers WHERE customer_id=%s", (customer_id,))
        flash("Customer deleted.", "success")
    except Exception as exc:  # noqa: BLE001
        flash(f"Cannot delete customer. {exc}", "danger")
    return redirect(url_for("customers.list_view"))
