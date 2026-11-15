import threading
import time
from flask import Flask, render_template, request, jsonify
from src.config import load_config, save_config
from src.database import get_recent_articles, get_stats, get_unsent_articles, init_db
from src.dispatchers import get_dispatcher
from bot_service import run_pipeline_once

app = Flask(__name__)
init_db()

# Background worker state
background_worker_running = False
worker_thread = None


def background_loop():
    global background_worker_running
    print("[Background Worker] Started automatic polling loop.")
    while background_worker_running:
        try:
            cfg = load_config()
            interval = max(5, cfg.get("polling_interval_minutes", 30))
            print(f"[Background Worker] Running scheduled scan...")
            run_pipeline_once(cfg)
            # Sleep in increments so thread can be stopped gracefully
            for _ in range(interval * 60):
                if not background_worker_running:
                    break
                time.sleep(1)
        except Exception as e:
            print(f"[Background Worker Error] {e}")
            time.sleep(30)
    print("[Background Worker] Stopped.")


@app.route("/")
def index():
    cfg = load_config()
    stats = get_stats()
    articles = get_recent_articles(limit=25)
    return render_template(
        "index.html",
        config=cfg,
        stats=stats,
        articles=articles,
        is_worker_running=background_worker_running
    )


@app.route("/api/news")
def api_news():
    exam_filter = request.args.get("exam", "ALL")
    limit = int(request.args.get("limit", 50))
    articles = get_recent_articles(limit=limit, exam_filter=exam_filter)
    return jsonify({"success": True, "articles": articles})


@app.route("/api/stats")
def api_stats():
    stats = get_stats()
    stats["is_worker_running"] = background_worker_running
    return jsonify({"success": True, "stats": stats})


@app.route("/api/scan", methods=["POST"])
def api_scan():
    try:
        cfg = load_config()
        result = run_pipeline_once(cfg)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/test-whatsapp", methods=["POST"])
def api_test_whatsapp():
    try:
        cfg = load_config()
        dispatcher = get_dispatcher(cfg)
        success, message = dispatcher.test_connection()
        return jsonify({
            "success": success,
            "message": message,
            "provider": cfg.get("whatsapp_provider")
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/settings", methods=["POST"])
def api_settings():
    try:
        data = request.json or {}
        current_cfg = load_config()

        # Update provider
        if "whatsapp_provider" in data:
            current_cfg["whatsapp_provider"] = data["whatsapp_provider"]

        # Update CallMeBot credentials
        if "callmebot_phone" in data or "callmebot_apikey" in data:
            current_cfg["callmebot"]["phone"] = data.get("callmebot_phone", current_cfg["callmebot"]["phone"]).strip()
            current_cfg["callmebot"]["apikey"] = data.get("callmebot_apikey", current_cfg["callmebot"]["apikey"]).strip()

        # Update Twilio credentials
        if "twilio_account_sid" in data:
            current_cfg["twilio"]["account_sid"] = data.get("twilio_account_sid", "").strip()
            current_cfg["twilio"]["auth_token"] = data.get("twilio_auth_token", "").strip()
            current_cfg["twilio"]["from_number"] = data.get("twilio_from_number", "").strip()
            current_cfg["twilio"]["to_number"] = data.get("twilio_to_number", "").strip()

        # Update Meta credentials
        if "meta_phone_number_id" in data:
            current_cfg["meta"]["phone_number_id"] = data.get("meta_phone_number_id", "").strip()
            current_cfg["meta"]["access_token"] = data.get("meta_access_token", "").strip()
            current_cfg["meta"]["recipient_phone"] = data.get("meta_recipient_phone", "").strip()

        # Update polling interval & batch size
        if "polling_interval_minutes" in data:
            current_cfg["polling_interval_minutes"] = max(5, int(data["polling_interval_minutes"]))
        if "max_alerts_per_run" in data:
            current_cfg["max_alerts_per_run"] = max(1, int(data["max_alerts_per_run"]))

        # Update monitored exams
        if "monitored_exams" in data and isinstance(data["monitored_exams"], list):
            current_cfg["monitored_exams"] = data["monitored_exams"]

        # Update dry_run
        if "dry_run" in data:
            current_cfg["dry_run"] = bool(data["dry_run"])

        save_config(current_cfg)
        return jsonify({"success": True, "message": "Settings saved successfully!", "config": current_cfg})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/toggle-bot", methods=["POST"])
def api_toggle_bot():
    global background_worker_running, worker_thread
    data = request.json or {}
    desired_state = data.get("enable")

    if desired_state is None:
        desired_state = not background_worker_running

    if desired_state and not background_worker_running:
        background_worker_running = True
        worker_thread = threading.Thread(target=background_loop, daemon=True)
        worker_thread.start()
        status_msg = "Background auto-monitoring started!"
    elif not desired_state and background_worker_running:
        background_worker_running = False
        status_msg = "Background auto-monitoring stopped."
    else:
        status_msg = f"Bot monitoring is already {'running' if background_worker_running else 'stopped'}."

    return jsonify({
        "success": True,
        "is_worker_running": background_worker_running,
        "message": status_msg
    })


if __name__ == "__main__":
    print("==================================================")
    print("🌐 EduAlert Web Dashboard starting on http://localhost:5000")
    print("==================================================")
    app.run(host="0.0.0.0", port=5000, debug=False)
