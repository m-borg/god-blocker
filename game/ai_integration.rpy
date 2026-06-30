init python:
    import json
    import re
    import os
    import random
    import time
    import ssl
    import urllib.request
    import urllib.error

    GEMINI_API_KEYS = [
        # "YOUR_GEMINI_KEY_HERE",
    ]

    OPENROUTER_API_KEYS = [
        # "YOUR_OPENROUTER_KEY_HERE",
    ]

    GEMINI_MODEL = "gemini-2.5-flash"
    GEMINI_FALLBACK_MODEL = "gemini-2.5-flash-lite"

    AI_MAX_TOKENS = 800
    AI_TEMPERATURE = 0.7

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    def log_ai_dialogue(speaker, text, system="Direct", meta=None):
        try:
            log_path = os.path.join(renpy.config.basedir, "ai_dialogue_log.txt")
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            meta_str = f" [{meta}]" if meta else ""
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] [{system}]{meta_str} {speaker}: {text}\n")
        except Exception as e:
            print(f"[LOG ERROR] {e}")

    def clean_ai_text(text):
        if not text:
            return "..."
        text = text.strip().strip('"').strip("'")
        text = re.sub(r'\(.*?\)', '', text)
        text = re.sub(r'\*.*?\*', '', text)
        return " ".join(text.split())


    class NPCMemory:
        def __init__(self, name, personality, background=""):
            self.name = name
            self.personality = personality
            self.background = background
            self.history = []
            self.system_prompt = f"""You are {name} in a dark, tense space-horror Visual Novel.

PROFILE:
{personality}
{background}

WRITING RULES (CRITICAL):
1. VN DIALOGUE STYLE: Write sharp, character-driven dialogue. Avoid generic "we are going to die" yapping. Show your personality (quirks, arrogance, panic, or optimism) with punchy, stylized banter.
2. NO AI SPEAK: Never act like an assistant. Never offer platitudes.
3. FLOW & INTRODUCTIONS: If it's a new encounter, establish who you are through your attitude or words. Move conversations forward; let them have a clear start, middle, and edge.
4. ATMOSPHERE: We are trapped on an abandoned spaceship. It is tense, but your focus is on the direct interaction, your own agenda, and surviving the current room.
5. REACTIVITY: If Arian (the user) gives a short, one-word, or nonsense reply, REACT naturally to it. Get annoyed, confused, or suspicious. DO NOT ignore it to continue a monologue.
6. NO ACTIONS OR QUOTES: Do NOT surround your text in quotes. Do NOT use actions in asterisks like *smiles* or parentheses like (sighs). Output ONLY pure spoken dialogue! Act naturally."""

        def add_message(self, role, content, meta=None):
            self.history.append({"role": role, "content": content})
            if len(self.history) > 10:
                self.history = self.history[-10:]
            log_ai_dialogue(self.name if role == "assistant" else "Arian", content, "1-on-1", meta=meta)

        def clear(self):
            self.history = []


    class AIManager:
        def __init__(self):
            self.npcs = {}

        def register_npc(self, name, personality, background=""):
            self.npcs[name] = NPCMemory(name, personality, background)
            return self.npcs[name]

        def get_npc(self, name):
            return self.npcs.get(name)

        def clear_history(self, name):
            if name in self.npcs:
                self.npcs[name].clear()

        def get_response(self, npc_name, user_message):
            if npc_name not in self.npcs:
                return "..."

            npc = self.npcs[npc_name]
            npc.add_message("user", user_message)

            or_messages = [{"role": "system", "content": npc.system_prompt}]
            for msg in npc.history:
                or_messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["content"]
                })

            data_or = json.dumps({
                "model": "google/gemini-2.5-flash",
                "messages": or_messages,
                "temperature": AI_TEMPERATURE,
                "max_tokens": AI_MAX_TOKENS
            }).encode('utf-8')

            for key in OPENROUTER_API_KEYS:
                headers = {
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                }
                req = urllib.request.Request(
                    "https://openrouter.ai/api/v1/chat/completions",
                    data=data_or, headers=headers
                )
                try:
                    t0 = time.time()
                    with urllib.request.urlopen(req, context=ssl_context, timeout=12) as resp:
                        result = json.loads(resp.read().decode('utf-8'))
                        latency = time.time() - t0
                        usage = result.get('usage', {})
                        meta = f"OR|{latency:.1f}s|{usage.get('prompt_tokens',0)}in/{usage.get('completion_tokens',0)}out"
                        update_key_status("openrouter", key, True, model_name="google/gemini-2.5-flash", response_headers=resp.headers)
                        record_api_usage("openrouter", key, "OpenRouter (google/gemini-2.5-flash)")
                        if result.get('choices'):
                            gen_text = result['choices'][0]['message']['content'].strip()
                            if npc.name + ":" in gen_text:
                                gen_text = gen_text.split(npc.name + ":", 1)[1].strip()
                            gen_text = clean_ai_text(gen_text)
                            npc.add_message("assistant", gen_text, meta=meta)
                            return gen_text
                except urllib.error.HTTPError as e:
                    update_key_status("openrouter", key, False, http_code=e.code, error_text=str(e), model_name="google/gemini-2.5-flash", response_headers=getattr(e, "headers", None))
                    print(f"[AI ERROR OR] HTTP {e.code}: {e}")
                except Exception as e:
                    update_key_status("openrouter", key, False, error_text=str(e), model_name="google/gemini-2.5-flash")
                    print(f"[AI ERROR OR] {e}")

            if GEMINI_API_KEYS:
                contents = [
                    {
                        "role": "user" if msg["role"] == "user" else "model",
                        "parts": [{"text": msg["content"]}]
                    }
                    for msg in npc.history
                ]

                data_g = json.dumps({
                    "systemInstruction": {"parts": [{"text": npc.system_prompt}]},
                    "contents": contents,
                    "generationConfig": {"temperature": AI_TEMPERATURE, "maxOutputTokens": AI_MAX_TOKENS}
                }).encode('utf-8')
                headers_g = {"Content-Type": "application/json"}

                keys = list(GEMINI_API_KEYS)
                random.shuffle(keys)

                for key in keys:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={key}"
                    req = urllib.request.Request(url, data=data_g, headers=headers_g)
                    try:
                        t0 = time.time()
                        with urllib.request.urlopen(req, context=ssl_context, timeout=12) as resp:
                            result = json.loads(resp.read().decode('utf-8'))
                            latency = time.time() - t0
                            usage = result.get('usageMetadata', {})
                            meta = f"Gem|{latency:.1f}s|{usage.get('promptTokenCount',0)}in/{usage.get('candidatesTokenCount',0)}out"
                            update_key_status("gemini", key, True, model_name=GEMINI_MODEL, response_headers=resp.headers)
                            record_api_usage("gemini", key)
                            if result.get('candidates'):
                                gen_text = result['candidates'][0]['content']['parts'][0]['text']
                                if npc.name + ":" in gen_text:
                                    gen_text = gen_text.split(npc.name + ":", 1)[1].strip()
                                gen_text = clean_ai_text(gen_text)
                                npc.add_message("assistant", gen_text, meta=meta)
                                return gen_text
                    except urllib.error.HTTPError as e:
                        update_key_status("gemini", key, False, http_code=e.code, error_text=str(e), model_name=GEMINI_MODEL, response_headers=getattr(e, "headers", None))
                        if e.code == 503:
                            fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_FALLBACK_MODEL}:generateContent?key={key}"
                            try:
                                req_fb = urllib.request.Request(fallback_url, data=data_g, headers=headers_g)
                                t0_fb = time.time()
                                with urllib.request.urlopen(req_fb, context=ssl_context, timeout=12) as resp_fb:
                                    result = json.loads(resp_fb.read().decode('utf-8'))
                                    latency_fb = time.time() - t0_fb
                                    usage_fb = result.get('usageMetadata', {})
                                    meta_fb = f"GemLite|{latency_fb:.1f}s|{usage_fb.get('promptTokenCount',0)}in/{usage_fb.get('candidatesTokenCount',0)}out"
                                    update_key_status("gemini", key, True, model_name=GEMINI_FALLBACK_MODEL, response_headers=resp_fb.headers)
                                    record_api_usage("gemini", key, f"Gemini 2.5 Flash Lite ({_mask_key(key)})")
                                    if result.get('candidates'):
                                        gen_text = result['candidates'][0]['content']['parts'][0]['text']
                                        if npc.name + ":" in gen_text:
                                            gen_text = gen_text.split(npc.name + ":", 1)[1].strip()
                                        gen_text = clean_ai_text(gen_text)
                                        npc.add_message("assistant", gen_text, meta=meta_fb)
                                        return gen_text
                            except Exception:
                                pass
                        else:
                            time.sleep(1.0)
                    except Exception as e:
                        update_key_status("gemini", key, False, error_text=str(e), model_name=GEMINI_MODEL)
                        time.sleep(1.0)

            return random.choice([
                "I don't know what to say...",
                "...",
                "This doesn't make sense."
            ])

    def conduct_blind_ai_vote(voter_name, voter_personality, valid_targets, vote_history_str=""):
        history_section = ""
        if vote_history_str:
            history_section = f"\n\nPAST ROUNDS HISTORY (use this to make an informed, character-consistent decision):\n{vote_history_str}"

        targets_str = ", ".join(valid_targets)
        prompt = (
            f"You are {voter_name}: {voter_personality}. "
            f"You are trapped in a deadly death game. Every round, the person with the most votes is executed. "
            f"You must vote for whoever is most threatening to YOUR survival, or whoever you have personal reason to suspect or hate. "
            f"Stay true to your personality when choosing. "
            f"{history_section}"
            f"\n\nVALID TARGETS: {targets_str}"
            f"\n\nOutput EXACTLY ONE NAME from the valid targets list. No punctuation. No explanation. Just the name."
        )

        # Stateless call — avoids polluting this NPC's persistent memory log.
        messages = [
            {"role": "system", "content": "You are a character in a death game visual novel. Follow all instructions literally."},
            {"role": "user", "content": prompt}
        ]
        data = json.dumps({
            "model": "google/gemini-2.5-flash",
            "messages": messages,
            "temperature": 0.6,
            "max_tokens": 30
        }).encode('utf-8')

        vote = None
        vote_meta = None

        for key in OPENROUTER_API_KEYS:
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
                with urllib.request.urlopen(req, context=ssl_context, timeout=15) as resp:
                    result = json.loads(resp.read().decode('utf-8'))
                    latency = time.time() - t0
                    usage = result.get('usage', {})
                    vote_meta = f"OR|{latency:.1f}s|{usage.get('prompt_tokens',0)}in/{usage.get('completion_tokens',0)}out"
                    update_key_status("openrouter", key, True, model_name="google/gemini-2.5-flash", response_headers=resp.headers)
                    record_api_usage("openrouter", key, "OpenRouter (google/gemini-2.5-flash)")
                    if result.get('choices'):
                        raw = clean_ai_text(result['choices'][0]['message']['content'].strip())
                        vote = next((t for t in valid_targets if t.lower() == raw.lower()), None)
                        if vote is None:
                            vote = next((t for t in valid_targets if t.lower() in raw.lower()), None)
            except urllib.error.HTTPError as e:
                update_key_status("openrouter", key, False, http_code=e.code, error_text=str(e), model_name="google/gemini-2.5-flash", response_headers=getattr(e, "headers", None))
                print(f"[BLIND VOTE ERROR] {voter_name}: HTTP {e.code}")
            except Exception as e:
                update_key_status("openrouter", key, False, error_text=str(e), model_name="google/gemini-2.5-flash")
                print(f"[BLIND VOTE ERROR] {voter_name}: {e}")
            if vote:
                break

        if vote is None and GEMINI_API_KEYS:
            data_g = json.dumps({
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.6, "maxOutputTokens": 30}
            }).encode('utf-8')
            key = random.choice(GEMINI_API_KEYS)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={key}"
            req = urllib.request.Request(url, data=data_g, headers={"Content-Type": "application/json"})
            try:
                t0 = time.time()
                with urllib.request.urlopen(req, context=ssl_context, timeout=15) as resp:
                    result = json.loads(resp.read().decode('utf-8'))
                    latency = time.time() - t0
                    usage = result.get('usageMetadata', {})
                    vote_meta = f"Gem|{latency:.1f}s|{usage.get('promptTokenCount',0)}in/{usage.get('candidatesTokenCount',0)}out"
                    update_key_status("gemini", key, True, model_name=GEMINI_MODEL, response_headers=resp.headers)
                    record_api_usage("gemini", key)
                    if result.get('candidates'):
                        raw = clean_ai_text(result['candidates'][0]['content']['parts'][0]['text'].strip())
                        vote = next((t for t in valid_targets if t.lower() == raw.lower()), None)
                        if vote is None:
                            vote = next((t for t in valid_targets if t.lower() in raw.lower()), None)
            except urllib.error.HTTPError as e:
                update_key_status("gemini", key, False, http_code=e.code, error_text=str(e), model_name=GEMINI_MODEL, response_headers=getattr(e, "headers", None))
            except Exception as e:
                update_key_status("gemini", key, False, error_text=str(e), model_name=GEMINI_MODEL)

        if vote is None:
            vote = voter_name if voter_name in valid_targets else (random.choice(valid_targets) if valid_targets else "Arian")
            vote_meta = "fallback"

        log_ai_dialogue(voter_name, f"voted for: {vote}", "Vote", meta=vote_meta)
        return vote

    def conduct_ai_vote(voter_name, valid_targets, history_str):
        prompt = (
            "CRITICAL: Based on the interrogation below, who do you secretly vote to EXECUTE? "
            "IMPORTANT: You are voting globally across the entire facility. You can vote for the person in your room to betray them, "
            "form an alliance with them to vote against someone else on the list, or vote for yourself if you gave up. "
            "You MUST output EXACTLY ONE NAME from the valid targets list, and nothing else! Output NO punctuation, NO explanation, just the name.\n"
            "VALID TARGETS: " + ", ".join(valid_targets) + "\n\n"
            "CHAT HISTORY:\n" + history_str
        )
        messages = [
            {"role": "system", "content": "You are a character in a death game visual novel. Follow all instructions literally."},
            {"role": "user", "content": prompt}
        ]
        data = json.dumps({
            "model": "google/gemini-2.5-flash",
            "messages": messages,
            "temperature": 0.6,
            "max_tokens": 30
        }).encode('utf-8')

        vote = None

        for key in OPENROUTER_API_KEYS:
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=data, headers=headers
            )
            try:
                with urllib.request.urlopen(req, context=ssl_context, timeout=15) as resp:
                    result = json.loads(resp.read().decode('utf-8'))
                    update_key_status("openrouter", key, True, model_name="google/gemini-2.5-flash", response_headers=resp.headers)
                    record_api_usage("openrouter", key, "OpenRouter (google/gemini-2.5-flash)")
                    if result.get('choices'):
                        raw = clean_ai_text(result['choices'][0]['message']['content'].strip())
                        vote = next((t for t in valid_targets if t.lower() == raw.lower()), None)
                        if vote is None:
                            vote = next((t for t in valid_targets if t.lower() in raw.lower()), None)
            except urllib.error.HTTPError as e:
                update_key_status("openrouter", key, False, http_code=e.code, error_text=str(e), model_name="google/gemini-2.5-flash", response_headers=getattr(e, "headers", None))
                print(f"[AI VOTE ERROR] {voter_name}: HTTP {e.code}")
            except Exception as e:
                update_key_status("openrouter", key, False, error_text=str(e), model_name="google/gemini-2.5-flash")
                print(f"[AI VOTE ERROR] {voter_name}: {e}")
            if vote:
                break

        if vote is None and GEMINI_API_KEYS:
            data_g = json.dumps({
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.6, "maxOutputTokens": 30}
            }).encode('utf-8')
            key = random.choice(GEMINI_API_KEYS)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={key}"
            req = urllib.request.Request(url, data=data_g, headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, context=ssl_context, timeout=15) as resp:
                    result = json.loads(resp.read().decode('utf-8'))
                    update_key_status("gemini", key, True, model_name=GEMINI_MODEL, response_headers=resp.headers)
                    record_api_usage("gemini", key)
                    if result.get('candidates'):
                        raw = clean_ai_text(result['candidates'][0]['content']['parts'][0]['text'].strip())
                        vote = next((t for t in valid_targets if t.lower() == raw.lower()), None)
                        if vote is None:
                            vote = next((t for t in valid_targets if t.lower() in raw.lower()), None)
            except urllib.error.HTTPError as e:
                update_key_status("gemini", key, False, http_code=e.code, error_text=str(e), model_name=GEMINI_MODEL, response_headers=getattr(e, "headers", None))
            except Exception as e:
                update_key_status("gemini", key, False, error_text=str(e), model_name=GEMINI_MODEL)

        if vote is None:
            vote = random.choice(valid_targets) if valid_targets else "Arian"

        log_ai_dialogue(voter_name, f"voted for: {vote}", "Vote")
        return vote

    ai_dialogue_manager = AIManager()

    def ask_ai_npc(npc_name, message):
        response = ai_dialogue_manager.get_response(npc_name, message)
        return split_response(response)

    def split_response(text, max_chars=200):
        if not text:
            return ["..."]
        if len(text) <= max_chars:
            return [text]

        chunks = []
        remaining = text

        while remaining:
            if len(remaining) <= max_chars:
                chunks.append(remaining)
                break

            cut = max_chars
            for end in ['. ', '! ', '? ']:
                pos = remaining[:max_chars + 20].rfind(end)
                if pos > 0:
                    cut = pos + len(end)
                    break

            chunks.append(remaining[:cut].strip())
            remaining = remaining[cut:].strip()

        return chunks if chunks else ["..."]
