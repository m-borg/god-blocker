init python:
    import json
    import re
    import random
    import traceback
    import urllib.request
    import urllib.error
    import threading
    import time
    import ssl

    if not hasattr(store, 'api_stats'):
        store.api_stats = {
            "current_model": "None",
            "current_provider": "None",
            "current_key_masked": "None",
            "last_success_at": 0,
            "last_error": "",
            "gemini_usage": {},
            "openrouter_usage": {"requests": 0, "last_reset": time.time()},
            "openrouter_key_usage": {},
            "gemini_keys": {},
            "openrouter_keys": {},
            "openrouter_rate": {"limit": None, "remaining": None, "reset": None, "updated_at": 0}
        }

    def _mask_key(key):
        return "..." + key[-4:] if key and len(key) >= 4 else "Unknown"

    def _safe_header(headers, names):
        if not headers:
            return None
        for n in names:
            val = headers.get(n)
            if val is not None:
                return val
        return None

    def _to_int_or_none(value):
        if value is None:
            return None
        try:
            return int(float(str(value).strip()))
        except Exception:
            return None

    def _ensure_stats_schema():
        now = time.time()
        if not hasattr(store, 'api_stats') or not isinstance(store.api_stats, dict):
            store.api_stats = {}
        stats = store.api_stats
        stats.setdefault("current_model", "None")
        stats.setdefault("current_provider", "None")
        stats.setdefault("current_key_masked", "None")
        stats.setdefault("last_success_at", 0)
        stats.setdefault("last_error", "")
        stats.setdefault("gemini_usage", {})
        stats.setdefault("openrouter_usage", {"requests": 0, "last_reset": now})
        stats.setdefault("openrouter_key_usage", {})
        stats.setdefault("gemini_keys", {})
        stats.setdefault("openrouter_keys", {})
        stats.setdefault("openrouter_rate", {"limit": None, "remaining": None, "reset": None, "updated_at": 0})

    def update_key_status(api_type, key, ok, http_code=None, error_text="", model_name=None, response_headers=None):
        _ensure_stats_schema()
        now = time.time()
        stats = store.api_stats
        key_map = stats["gemini_keys" if api_type == "gemini" else "openrouter_keys"]

        if key not in key_map:
            key_map[key] = {
                "status": "unknown",
                "consecutive_failures": 0,
                "last_used": 0,
                "last_success": 0,
                "last_failure": 0,
                "last_code": None,
                "last_error": ""
            }

        entry = key_map[key]
        entry["last_used"] = now

        if ok:
            entry["status"] = "healthy"
            entry["consecutive_failures"] = 0
            entry["last_success"] = now
            entry["last_code"] = http_code
            entry["last_error"] = ""
            stats["current_provider"] = "OpenRouter" if api_type == "openrouter" else "Gemini Direct"
            stats["current_model"] = model_name or stats.get("current_model", "None")
            stats["current_key_masked"] = _mask_key(key)
            stats["last_success_at"] = now
            stats["last_error"] = ""
        else:
            entry["consecutive_failures"] += 1
            entry["last_failure"] = now
            entry["last_code"] = http_code
            entry["last_error"] = (error_text or "").strip()
            if http_code == 429:
                entry["status"] = "rate_limited"
            elif http_code == 402:
                entry["status"] = "billing_blocked"
            elif http_code in (401, 403):
                entry["status"] = "unauthorized"
            elif entry["consecutive_failures"] >= 3:
                entry["status"] = "degraded"
            else:
                entry["status"] = "error"
            stats["last_error"] = f"{api_type} {_mask_key(key)}: {entry['status']} ({http_code if http_code is not None else 'n/a'})"

        if api_type == "openrouter" and response_headers:
            stats["openrouter_rate"] = {
                "limit": _to_int_or_none(_safe_header(response_headers, ["x-ratelimit-limit", "x-ratelimit-limit-requests"])),
                "remaining": _to_int_or_none(_safe_header(response_headers, ["x-ratelimit-remaining", "x-ratelimit-remaining-requests"])),
                "reset": _to_int_or_none(_safe_header(response_headers, ["x-ratelimit-reset", "x-ratelimit-reset-requests"])),
                "updated_at": now
            }

    def record_api_usage(api_type, key=None, model_name=None):
        _ensure_stats_schema()
        now = time.time()

        if getattr(persistent, 'api_usage_daily', None) is None:
            persistent.api_usage_daily = {"gemini": {}, "openrouter": {"requests": 0, "reset": now}, "openrouter_keys": {}}

        daily = persistent.api_usage_daily
        daily.setdefault("openrouter_keys", {})

        if api_type == "gemini":
            if key not in store.api_stats["gemini_usage"]:
                store.api_stats["gemini_usage"][key] = {"requests": 0, "last_reset": now}
            usage = store.api_stats["gemini_usage"][key]
            if now - usage["last_reset"] > 60:
                usage["requests"] = 0
                usage["last_reset"] = now

            if key not in daily["gemini"] or now - daily["gemini"][key]["reset"] > 86400:
                daily["gemini"][key] = {"requests": 0, "reset": now}

            usage["requests"] += 1
            daily["gemini"][key]["requests"] += 1
            store.api_stats["current_model"] = model_name or f"Gemini 2.5 Flash ({_mask_key(key)})"

        elif api_type == "openrouter":
            usage = store.api_stats["openrouter_usage"]
            if now - usage["last_reset"] > 60:
                usage["requests"] = 0
                usage["last_reset"] = now

            if key and key not in store.api_stats["openrouter_key_usage"]:
                store.api_stats["openrouter_key_usage"][key] = {"requests": 0, "last_reset": now}
            if key:
                key_usage = store.api_stats["openrouter_key_usage"][key]
                if now - key_usage["last_reset"] > 60:
                    key_usage["requests"] = 0
                    key_usage["last_reset"] = now

            if now - daily["openrouter"]["reset"] > 86400:
                daily["openrouter"] = {"requests": 0, "reset": now}
            if key and (key not in daily["openrouter_keys"] or now - daily["openrouter_keys"][key]["reset"] > 86400):
                daily["openrouter_keys"][key] = {"requests": 0, "reset": now}

            usage["requests"] += 1
            daily["openrouter"]["requests"] += 1
            if key:
                store.api_stats["openrouter_key_usage"][key]["requests"] += 1
                daily["openrouter_keys"][key]["requests"] += 1
            store.api_stats["current_model"] = model_name or "OpenRouter (google/gemini-2.5-flash)"

    def _parse_ai_response(text):
        text = re.sub(r'\*[^*]+\*', '', text)
        text = " ".join(text.split())
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        if ":" in text:
            name, dialogue = text.split(":", 1)
            name = name.strip().replace("*", "")
            dialogue = dialogue.strip()
            if name in ("Narration", "System", "Narrator"):
                # AI sometimes wraps "Character: dialogue" inside "Narration: Character: dialogue"
                # Re-parse the inner content if it looks like a character line
                if ":" in dialogue:
                    inner_name, inner_text = dialogue.split(":", 1)
                    inner_name = inner_name.strip()
                    inner_text = inner_text.strip()
                    if inner_text and len(inner_name) <= 15 and re.match(r'^[\w\s\.]+$', inner_name):
                        return inner_name, inner_text
                name = "Narration"
            if name and dialogue and len(dialogue) > 5:
                return name, dialogue
        return "Narration", text or "What do we do now?"


    class AIDirector:
        def __init__(self):
            self.history = []
            self._last_meta = None

        def clear_history(self):
            self.history = []

        def add_message(self, name, message, meta=None):
            self.history.append({"name": name, "message": message})
            if len(self.history) > 15:
                self.history = self.history[-15:]
            try:
                log_ai_dialogue(name, message, "Group", meta=meta)
            except Exception:
                pass

        def _build_prompts(self, scene_context, available_characters):
            char_personalities = "\n".join(
                f"- {name}: {desc}" for name, desc in available_characters.items()
            )
            system_prompt = f"""You are an expert, award-winning visual novel writer.

Characters:
{char_personalities}

CRITICAL WRITING RULES:
1. OUTPUT FORMAT: Choose ONE format: "CharacterName: Dialogue." OR "Narration: Description."
2. PACING & BREATHING ROOM: Use "Narration: ..." responses occasionally for pauses, nervous glances, and atmosphere.
3. NATURAL LANGUAGE: No philosophical rambling or purple prose. They are normal, stressed people speaking bluntly.
4. ENGAGE THE PLAYER (ARIAN): Force Arian to participate. Ask him for his opinion on the current topic or challenge his usefulness. Give him an actual question to answer!
5. FOCUSED TOPIC: Stay laser-focused on the 'Scene' context provided below. DO NOT talk about memory loss, who Arian is, or random lore unless the scene specifically mentions it! Focus on what Arian is trying to do and the topic of the conversation.
6. DIRECT RESPONSE: If a character was just specifically spoken to or asked a question by name, they MUST be the one to reply next.
7. GROUNDED TENSION: Keep focused on survival, their mistrust, and the immediate situation defined in the Scene prompt.
8. NO ASTERISK ACTIONS: Do NOT use asterisks or parentheses for actions like *sighs* or (laughs). If you want to describe an action, output a "Narration: Description." instead."""

            history_str = ""
            for msg in self.history[-12:]:
                if msg['name'] == "System":
                    history_str += f"\n[SYSTEM CONTEXT UPDATE: {msg['message']}]\n"
                else:
                    history_str += f"{msg['name']}: {msg['message']}\n"

            length_hint = ""
            if len(self.history) > 12:
                length_hint = " (Hint: The conversation has been going for a while - someone needs to cut it short or take action.)"

            content_prompt = f"""Scene: {scene_context}

Recent dialogue:
{history_str if history_str else "(Beginning)"}

Write ONE NEXT line (either a character's dialogue OR a narration line) responding naturally to the scene and previous lines. Keep it grounded, high-stakes, and give the scene room to breathe.{length_hint}
Format ONLY as:
CharacterName: Dialogue
OR
Narration: Description"""

            return system_prompt, content_prompt

        def _try_openrouter(self, system_prompt, content_prompt):
            keys = OPENROUTER_API_KEYS
            data = json.dumps({
                "model": "google/gemini-2.5-flash",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content_prompt}
                ],
                "temperature": 0.75,
                "max_tokens": 500
            }).encode('utf-8')

            for key in keys:
                headers = {
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                }
                req = urllib.request.Request(
                    "https://openrouter.ai/api/v1/chat/completions",
                    data=data, headers=headers
                )
                try:
                    t0 = time.time()
                    with urllib.request.urlopen(req, context=ssl_context, timeout=12) as resp:
                        result = json.loads(resp.read().decode('utf-8'))
                        latency = time.time() - t0
                        usage = result.get('usage', {})
                        self._last_meta = f"OR|{latency:.1f}s|{usage.get('prompt_tokens',0)}in/{usage.get('completion_tokens',0)}out"
                        update_key_status("openrouter", key, True, model_name="google/gemini-2.5-flash", response_headers=resp.headers)
                        record_api_usage("openrouter", key, "OpenRouter (google/gemini-2.5-flash)")
                        if result.get('choices'):
                            return _parse_ai_response(result['choices'][0]['message']['content'].strip())
                except urllib.error.HTTPError as e:
                    update_key_status("openrouter", key, False, http_code=e.code, error_text=str(e), model_name="google/gemini-2.5-flash", response_headers=getattr(e, "headers", None))
                    print(f"[AI ERROR] OpenRouter key failed: HTTP {e.code}")
                except Exception as e:
                    update_key_status("openrouter", key, False, error_text=str(e), model_name="google/gemini-2.5-flash")
                    print(f"[AI ERROR] OpenRouter key failed: {e}")
            return None

        def _request_gemini(self, key, data, headers, model):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            req = urllib.request.Request(url, data=data, headers=headers)
            t0 = time.time()
            with urllib.request.urlopen(req, context=ssl_context, timeout=12) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                latency = time.time() - t0
                usage = result.get('usageMetadata', {})
                self._last_meta = f"Gem|{latency:.1f}s|{usage.get('promptTokenCount',0)}in/{usage.get('candidatesTokenCount',0)}out"
                update_key_status("gemini", key, True, model_name=model, response_headers=resp.headers)
                record_api_usage("gemini", key)
                if result.get('candidates'):
                    return _parse_ai_response(result['candidates'][0]['content']['parts'][0]['text'].strip())
                return None

        def _try_gemini(self, system_prompt, content_prompt):
            if not GEMINI_API_KEYS:
                return None

            data = json.dumps({
                "systemInstruction": {"parts": [{"text": system_prompt}]},
                "contents": [{"role": "user", "parts": [{"text": content_prompt}]}],
                "generationConfig": {"temperature": 0.75, "maxOutputTokens": 2000}
            }).encode('utf-8')
            headers = {"Content-Type": "application/json"}
            primary = GEMINI_MODEL or "gemini-2.5-flash"

            keys = list(GEMINI_API_KEYS)
            random.shuffle(keys)

            for key in keys:
                try:
                    result = self._request_gemini(key, data, headers, primary)
                    if result:
                        return result
                except urllib.error.HTTPError as e:
                    update_key_status("gemini", key, False, http_code=e.code, error_text=str(e), model_name=primary, response_headers=getattr(e, "headers", None))
                    if e.code == 503:
                        try:
                            result = self._request_gemini(key, data, headers, GEMINI_FALLBACK_MODEL)
                            if result:
                                return result
                        except Exception:
                            pass
                    elif e.code in (429, 500):
                        time.sleep(1.5)
                except Exception as e:
                    update_key_status("gemini", key, False, error_text=str(e), model_name=primary)
                    time.sleep(1.0)
            return None

        def get_next_line(self, scene_context, available_characters):
            system_prompt, content_prompt = self._build_prompts(scene_context, available_characters)
            return (
                self._try_openrouter(system_prompt, content_prompt)
                or self._try_gemini(system_prompt, content_prompt)
                or random.choice([
                    ("Narration", "A heavy, suffocating silence fills the room as the tension refuses to break."),
                    ("Narration", "They all seem too lost in their own thoughts to speak."),
                    (list(available_characters.keys())[0], "I don't think I have anything else to add right now."),
                    ("Narration", "A quiet moment passes. No one makes a move.")
                ])
            )

    ai_director = AIDirector()

    def start_bg_ai_line(scene_context, chars):
        if store._next_ai_line_state is None or store._next_ai_line_state.get("done", True):
            store._next_ai_line_state = {"done": False, "result": None, "meta": None}
            def worker():
                try:
                    store._next_ai_line_state["result"] = ai_director.get_next_line(scene_context, chars)
                    store._next_ai_line_state["meta"] = ai_director._last_meta
                except Exception as e:
                    traceback.print_exc()
                    store._next_ai_line_state["result"] = ("Narration", f"Error: {e}")
                    store._next_ai_line_state["meta"] = "error"
                finally:
                    store._next_ai_line_state["done"] = True
            threading.Thread(target=worker, daemon=True).start()

    def wait_for_ai_line(timeout=25.0):
        start = time.time()
        show_think = False
        prefetch_hit = store._next_ai_line_state.get("done", False)
        while not store._next_ai_line_state.get("done", False):
            if not show_think and (time.time() - start) > 1.2:
                renpy.show_screen("thinking_indicator")
                show_think = True
            renpy.pause(0.1, hard=True)
            if timeout and (time.time() - start) > timeout:
                if show_think:
                    renpy.hide_screen("thinking_indicator")
                return "Narration", "The silence stretches on uncomfortably..."
        if show_think:
            renpy.hide_screen("thinking_indicator")
        store._next_ai_line_state["prefetch_hit"] = prefetch_hit
        return store._next_ai_line_state.get("result") or ("Narration", "...")

    def _advance_ai_line(scene_context, char_dict):
        start_bg_ai_line(scene_context, char_dict)
        name, text = wait_for_ai_line()
        state = store._next_ai_line_state or {}
        api_meta = state.get("meta")
        hit = state.get("prefetch_hit", False)
        meta = (f"{api_meta}|" if api_meta else "") + ("HIT" if hit else "MISS")
        ai_director.add_message(name, text, meta=meta)
        store._next_ai_line_state = None
        start_bg_ai_line(scene_context, char_dict)
        return name, text

    def _resolve_speaker(name, char_obj_dict):
        char = char_obj_dict.get(name)
        if char:
            return char
        if name == "System":
            return nvl_narrator
        if name in ("Narration", "Narrator"):
            return narrator
        return Character(name)

    def _sanitize_renpy(text):
        return (text
            .replace("%", "%%")
            .replace("[", "[[")
            .replace("]", "]]")
            .replace("{", "{{")
            .replace("}", "}}"))


screen group_chat_interruption():
    vbox:
        align (0.95, 0.05)
        textbutton "Speak / Interrupt" action [SetVariable("chat_action", "interrupt"), Return(True)]
        textbutton "End Conversation" action [SetVariable("chat_action", "end"), Return(True)]

screen death_game_interruption(turns_left):
    vbox:
        align (0.95, 0.05)
        text "Turns Remaining: [turns_left]" size 30 color "#ff0000" bold True
        textbutton "Speak / Accuse" action [SetVariable("chat_action", "interrupt"), Return(True)]
        if getattr(store, "chapter2_vote_history", None):
            textbutton "View Vote History" action Show("chapter2_vote_history_menu")

screen thinking_indicator():
    zorder 100
    frame:
        align (0.5, 0.95)
        background Solid("#00000088")
        padding (10, 5)
        text "Characters are thinking..." size 20 color "#999999"


label start_group_scene(scene_context, char_dict, char_obj_dict):
    $ ai_director.clear_history()
    $ ai_director.add_message("System", scene_context)
    $ loop_count = 0
    $ chat_action = None
    $ store._next_ai_line_state = None
    $ log_ai_dialogue("STATE", f"GROUP_SCENE_START | chars: {', '.join(char_dict.keys())}", "State")

    label .chat_loop:
        if loop_count > 16:
            hide screen group_chat_interruption
            window auto
            jump .end_conversation

        window show
        show screen group_chat_interruption

        python:
            name, text = _advance_ai_line(scene_context, char_dict)

        $ speaker_char = _resolve_speaker(name, char_obj_dict)
        $ chat_action = None
        $ safe_text = _sanitize_renpy(text)

        if "[DEXTER KILLS ARIAN]" in text or "[[DEXTER KILLS ARIAN]]" in safe_text:
            $ clean_text = text.replace("[DEXTER KILLS ARIAN]", "").strip()
            if clean_text:
                if name != "System":
                    $ clean_text = "{color=#FFE000}" + clean_text + "{/color}"
                $ speaker_char(clean_text)
            hide screen group_chat_interruption
            scene bg blood_splatter with hpunch
            "Before I can even react to the accusations, Dexter lunges forward with terrifying speed."
            "He tackles me to the ground. A blade flashes in the harsh light."
            "My throat is severed before I have the chance to scream. As the light fades from my eyes, the last thing I hear is his manic laughter."
            "DEAD END."
            jump bad_end

        if name != "System":
            $ safe_text = "{color=#FFE000}" + safe_text + "{/color}"
        $ speaker_char(safe_text)

        if chat_action == "interrupt":
            hide screen group_chat_interruption
            $ player_text = renpy.input("Arian: ", length=300).strip()
            if player_text:
                $ ai_director.add_message("Arian", player_text)
                mc "[player_text]"
                $ store._next_ai_line_state = None
            jump .chat_loop

        elif chat_action == "end":
            hide screen group_chat_interruption
            window auto
            jump .end_conversation

        $ loop_count += 1
        jump .chat_loop

    label .end_conversation:
        $ log_ai_dialogue("STATE", f"GROUP_SCENE_END | turns: {loop_count}", "State")
        window auto
        menu:
            "Continue to next scene":
                return
            "Talk to another character":
                $ store._next_ai_line_state = None
                $ loop_count = 0
                return True
            "Take a moment to yourself":
                return


label start_death_game_scene(scene_context, char_dict, char_obj_dict, max_turns=7):
    $ ai_director.clear_history()
    $ ai_director.add_message("System", scene_context)
    $ loop_count = 0
    $ chat_action = None
    $ store._next_ai_line_state = None

    label .dg_chat_loop:
        if loop_count >= max_turns:
            hide screen death_game_interruption
            window auto
            $ hist = ""
            python:
                for msg in ai_director.history:
                    hist += f"{msg['name']}: {msg['message']}\n"
            return hist

        window show
        $ turns_left = max_turns - loop_count
        show screen death_game_interruption(turns_left)

        python:
            name, text = _advance_ai_line(scene_context, char_dict)

        $ speaker_char = _resolve_speaker(name, char_obj_dict)
        $ chat_action = None
        $ safe_text = _sanitize_renpy(text)

        if "[DEXTER KILLS ARIAN]" in text or "[[DEXTER KILLS ARIAN]]" in safe_text:
            $ clean_text = text.replace("[DEXTER KILLS ARIAN]", "").strip()
            if clean_text:
                if name != "System":
                    $ clean_text = "{color=#FFE000}" + clean_text + "{/color}"
                $ speaker_char(clean_text)
            hide screen death_game_interruption
            scene bg blood_splatter with hpunch
            "Before I can even react to the accusations, Dexter lunges forward with terrifying speed."
            "He tackles me to the ground. A blade flashes in the harsh light."
            "My throat is severed before I have the chance to scream. As the light fades from my eyes, the last thing I hear is his manic laughter."
            "DEAD END."
            jump start

        if name != "System":
            $ safe_text = "{color=#FFE000}" + safe_text + "{/color}"
        $ speaker_char(safe_text)

        if chat_action == "interrupt":
            hide screen death_game_interruption
            $ player_text = renpy.input("Arian: ", length=300).strip()
            if player_text:
                $ ai_director.add_message("Arian", player_text)
                mc "[player_text]"
                $ store._next_ai_line_state = None

        $ loop_count += 1
        jump .dg_chat_loop
