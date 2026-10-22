import os
import json

from flask import Blueprint, flash, redirect, render_template, request, session, url_for,jsonify

from app.tasks import async_start_scraping
from config import Config
from app import celery


main_routes = Blueprint("main_routes", __name__)

# Use environment variables instead of hardcoding credentials


@main_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == Config.USERNAME and password == Config.PASSWORD:
            session["authenticated"] = True
            return redirect(url_for("main_routes.submit_data"))

        flash("Invalid username or password", "error")

    if session.get("authenticated"):
        return redirect(url_for("main_routes.submit_data"))

    return render_template("index.html")

from redis import Redis
redis_client = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)


@main_routes.route("/tasks/running", methods=["GET"])
def list_running_tasks():
    # running_tasks = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT).hgetall("running_tasks")

    tasks_list = []
    for task_id, task_info in Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT).hgetall("running_tasks").items():
        task_info = json.loads(task_info)
        tasks_list.append(task_info)

    return jsonify({"running_tasks": tasks_list}), 200

@main_routes.route("/tasks/<task_id>/status", methods=["GET", "POST"])
def get_task_status_by_id(task_id):
    result = celery.AsyncResult(task_id)
    return jsonify({"status": result.status})


@main_routes.route("/submit", methods=["GET", "POST"])
def submit_data():
    # if not session.get("authenticated"):
    #     return redirect(url_for("main_routes.login"))

    if request.method == "POST":
        data = {
            "keyword": request.form.get("keyword", "").strip(),
            "title": request.form.get("title", "").strip(),
            "abstract": request.form.get("abstract", "").strip(),
            "start_year": request.form.get("start_year", "").strip(),
            "end_year": request.form.get("end_year", "").strip(),
            "site": request.form.get("site", "").strip(),
        }

        # TODO: Replace with actual processing logic
        print("Received submission:", data)
        task = async_start_scraping.delay(data)
        print("Task ID:", task)
        flash(f"Scraping task started (Task ID: {task.id})", "success")

        return redirect(url_for("main_routes.submit_data"))

    return render_template("process_started.html")


@main_routes.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main_routes.login"))
