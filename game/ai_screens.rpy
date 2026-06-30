init python:
    import json
    import threading
    import time
    import urllib.request

    def _fmt_ago(ts):
        if not ts:
            return "never"
        delta = int(max(0, time.time() - ts))
        if delta < 60:
            return f"{delta}s ago"
        if delta < 3600:
            return f"{delta // 60}m ago"
        return f"{delta // 3600}h ago"

    def _status_color(status):
        if status == "healthy":
            return "#44ff44"
        if status in ("rate_limited", "degraded"):
            return "#ffaa00"
        if status in ("billing_blocked", "unauthorized", "error"):
            return "#ff4444"
        return "#aaaaaa"

    def _status_label(status):
        return {
            "healthy": "HEALTHY",
            "rate_limited": "RATE LIMITED",
            "billing_blocked": "BILLING BLOCKED (402)",
            "unauthorized": "UNAUTHORIZED",
            "degraded": "DEGRADED",
            "error": "ERROR",
            "unknown": "UNKNOWN"
        }.get(status, "UNKNOWN")

    def _short_error(txt, max_len=56):
        if not txt:
            return ""
        txt = " ".join(str(txt).split())
        return txt if len(txt) <= max_len else txt[:max_len - 3] + "..."

    def get_openrouter_credits():
        now = time.time()
        cached = getattr(store, "openrouter_credits_cache", None)
        if cached and now - cached["time"] < 60:
            return cached["value"]
        try:
            key = OPENROUTER_API_KEYS[-1]
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/credits",
                headers={"Authorization": f"Bearer {key}"}
            )
            with urllib.request.urlopen(req, context=ssl_context, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                credits = float(data.get("data", {}).get("total_credits", 0))
                usage = float(data.get("data", {}).get("total_usage", 0))
                val = f"${credits:.3f} left (${usage:.3f} used)"
                store.openrouter_credits_cache = {"time": now, "value": val}
                return val
        except Exception:
            return "Error checking credits"

    def _ask_ai_npc_worker(state, npc_name, player_input):
        try:
            state["result"] = ask_ai_npc(npc_name, player_input)
        except Exception as e:
            state["error"] = str(e)
        finally:
            state["done"] = True

    def ask_ai_npc_nonblocking(npc_name, player_input, character=None, timeout=25.0, poll_interval=0.3):
        state = {"done": False, "result": None, "error": None}
        t = threading.Thread(target=_ask_ai_npc_worker, args=(state, npc_name, player_input))
        t.daemon = True
        t.start()

        start = time.time()
        dots = 0
        while not state["done"]:
            dots = (dots % 3) + 1
            if character:
                renpy.say(character, f"{{i}}{'.' * dots}{{/i}}", interact=False)
            renpy.pause(poll_interval, hard=True)
            if timeout and (time.time() - start) > timeout:
                return ["(Timed out waiting for AI. Try again.)"]

        if state["error"]:
            return [f"(AI error: {state['error']})"]
        return state["result"] or ["..."]

    def start_npc_conversation(npc_name, character, exit_words=None):
        if exit_words is None:
            exit_words = ["goodbye", "bye", "exit", "quit", "leave", "done", "end"]

        while True:
            player_input = renpy.input(f"Talk to {npc_name}: (type 'goodbye' to end)", length=300)
            player_input = player_input.strip()

            if player_input.lower() in exit_words:
                return
            if not player_input:
                renpy.say(character, "...")
                continue

            for chunk in ask_ai_npc_nonblocking(npc_name, player_input, character=character):
                safe_chunk = _sanitize_renpy(chunk)
                renpy.say(character, "{color=#FFE000}" + safe_chunk + "{/color}")


screen api_stats():
    tag menu
    use game_menu(_("API Usage Stats"), scroll="viewport"):
        vbox:
            spacing 20

            $ stats = getattr(store, "api_stats", {})
            $ current_provider = stats.get("current_provider", "None")
            $ current_model = stats.get("current_model", "None")
            $ current_key = stats.get("current_key_masked", "None")
            $ last_success = stats.get("last_success_at", 0)
            $ last_error = stats.get("last_error", "")

            text "Current Active Route:" size 30 color "#fff"
            text "Provider: [current_provider]" size 22 color "#ddd"
            text "Model: [current_model]" size 22 color "#ddd"
            text "Key: [current_key]" size 22 color "#ddd"
            text "Last success: [_fmt_ago(last_success)]" size 20 color "#aaa"
            if last_error:
                text "Last error: [_short_error(last_error, 85)]" size 20 color "#ff7777"

            null height 20

            text "OpenRouter Global Rate Headers (from last OR response):" size 30 color "#fff"
            $ or_rate = stats.get("openrouter_rate", {})
            $ or_rate_limit = or_rate.get("limit", None)
            $ or_rate_remaining = or_rate.get("remaining", None)
            $ or_rate_reset = or_rate.get("reset", None)
            $ or_rate_seen = or_rate.get("updated_at", 0)
            if or_rate_limit is None and or_rate_remaining is None:
                text "No rate headers captured yet." size 22 color "#888"
            else:
                text "Limit: [or_rate_limit if or_rate_limit is not None else 'n/a']" size 22 color "#ddd"
                text "Remaining: [or_rate_remaining if or_rate_remaining is not None else 'n/a']" size 22 color "#ddd"
                text "Reset: [or_rate_reset if or_rate_reset is not None else 'n/a']" size 22 color "#ddd"
                text "Header age: [_fmt_ago(or_rate_seen)]" size 20 color "#888"

            null height 20

            text "OpenRouter Keys (real status):" size 30 color "#fff"
            $ openrouter_key_list = list(globals().get("OPENROUTER_API_KEYS", []))
            if not openrouter_key_list:
                text "No OpenRouter keys configured." size 22 color "#888"
            else:
                for key_idx, key in enumerate(openrouter_key_list):
                    $ key_status = stats.get("openrouter_keys", {}).get(key, {})
                    $ status = key_status.get("status", "unknown")
                    $ code = key_status.get("last_code", None)
                    $ last_used = key_status.get("last_used", 0)
                    $ minute_usage = stats.get("openrouter_key_usage", {}).get(key, {"requests": 0, "last_reset": time.time()})
                    $ minute_requests = minute_usage.get("requests", 0)
                    $ daily_requests = getattr(persistent, 'api_usage_daily', {}).get("openrouter_keys", {}).get(key, {"requests": 0}).get("requests", 0)
                    $ is_active = _mask_key(key) == current_key
                    $ label_color = _status_color(status)

                    frame:
                        background Solid("#202020")
                        padding (14, 14)
                        xfill True
                        vbox:
                            spacing 4
                            text "OR Key [key_idx + 1] ([_mask_key(key)])" size 22 color "#fff"
                            text "Status: [_status_label(status)]" size 20 color label_color
                            text "HTTP: [code if code is not None else 'n/a']  |  60s: [minute_requests]  |  24h: [daily_requests]" size 19 color "#bbb"
                            text "Last used: [_fmt_ago(last_used)]" size 18 color "#888"
                            if is_active:
                                text "ACTIVE NOW" size 18 color "#44ddff"
                            $ err_line = _short_error(key_status.get("last_error", ""), 80)
                            if err_line:
                                text "Error: [err_line]" size 18 color "#ff7777"

            null height 20

            text "Gemini Direct Keys (real status):" size 30 color "#fff"

            if hasattr(store, 'api_stats'):
                for key_idx, key in enumerate(GEMINI_API_KEYS):
                    $ usage = store.api_stats["gemini_usage"].get(key, {"requests": 0, "last_reset": time.time()})
                    $ requests = usage.get("requests", 0)
                    $ last_reset = usage.get("last_reset", time.time())
                    $ time_left = max(0, 60 - int(time.time() - last_reset))
                    if time_left == 0 and requests > 0:
                        $ requests = 0
                    $ masked_key = "Gemini Key " + str(key_idx + 1) + " (..." + key[-4:] + ")"
                    $ key_status = stats.get("gemini_keys", {}).get(key, {})
                    $ status = key_status.get("status", "unknown")
                    $ code = key_status.get("last_code", None)
                    $ daily_stats = getattr(persistent, 'api_usage_daily', {}).get("gemini", {}).get(key, {"requests": 0})
                    $ daily_requests = daily_stats.get("requests", 0)
                    $ is_active = _mask_key(key) == current_key

                    frame:
                        background Solid("#202020")
                        padding (14, 14)
                        xfill True
                        vbox:
                            spacing 4
                            text "[masked_key]" size 22 color "#fff"
                            text "Status: [_status_label(status)]" size 20 color _status_color(status)
                            text "HTTP: [code if code is not None else 'n/a']  |  60s: [requests]  |  24h: [daily_requests]" size 19 color "#bbb"
                            if requests > 0:
                                text "Minute window resets in [time_left]s" size 18 color "#888"
                            text "Last used: [_fmt_ago(key_status.get('last_used', 0))]" size 18 color "#888"
                            if is_active:
                                text "ACTIVE NOW" size 18 color "#44ddff"
                            $ err_line = _short_error(key_status.get("last_error", ""), 80)
                            if err_line:
                                text "Error: [err_line]" size 18 color "#ff7777"

            null height 20

            text "OpenRouter Credits:" size 30 color "#fff"
            $ or_credits = get_openrouter_credits()
            text "[or_credits]" size 24 color "#44dd44"
            text "(Counts shown above are real in-game request outcomes and per-key error states.)" size 18 color "#aaaaaa"

            null height 40
            textbutton "Refresh" action ShowMenu("api_stats")
