# The script of the game goes in this file.

# Test Game - Demonstrating NVL-style narration and ADV-style dialogue

# Handle window close button (X) properly
init python:
    # Function to show quit confirmation when X button is clicked
    def quit_confirm():
        return renpy.invoke_in_new_context(renpy.call_screen, "confirm", 
                                         message="Are you sure you want to quit?", 
                                         yes_action=Quit(confirm=False), 
                                         no_action=Return(False))
    
    # Set up proper quit handling for window close button
    config.quit_action = Function(quit_confirm)

# Define a character for NVL-style narration
define nvl_narrator = Character(None, kind=nvl)

init -1 python:
    if persistent.experimental_sprites is None:
        persistent.experimental_sprites = False

init python:
    spawned_speaker_tag = None
    
    def speaker_pop_callback(event, interact=True, img_tag=None, **kwargs):
        if not getattr(persistent, "experimental_sprites", False):
            return
        if not interact:
            return
            
        global spawned_speaker_tag
        
        if event == "begin" and img_tag:
            # We want to make sure characters pop up, but we don't mess with existing scene layout.
            if not renpy.showing(img_tag):
                if spawned_speaker_tag and renpy.showing(spawned_speaker_tag):
                    renpy.hide(spawned_speaker_tag)
                    
                renpy.show(f"{img_tag} neutral")
                spawned_speaker_tag = img_tag
                
        elif event == "end" and img_tag:
            # Hide the character after their line finishes, if they were popped up by this callback
            if spawned_speaker_tag == img_tag:
                renpy.hide(spawned_speaker_tag)
                spawned_speaker_tag = None

# Define characters
define mc = Character("Arian")
define y = Character("Yukino", callback=renpy.curry(speaker_pop_callback)(img_tag="y"))
define c = Character("Dr. Cain", callback=renpy.curry(speaker_pop_callback)(img_tag="c"))
define n = Character("Neuro", callback=renpy.curry(speaker_pop_callback)(img_tag="n"))
define o1 = Character("Onika", callback=renpy.curry(speaker_pop_callback)(img_tag="o1"))
define o2 = Character("Obie", callback=renpy.curry(speaker_pop_callback)(img_tag="o2"))
define p = Character("X", callback=renpy.curry(speaker_pop_callback)(img_tag="p"))
define d = Character("Dexter", callback=renpy.curry(speaker_pop_callback)(img_tag="d"))
define k = Character("Kitchens", callback=renpy.curry(speaker_pop_callback)(img_tag="k")) # The 9th character
define os = Character("OS")
define meta_char = Character("Meta Character")


# Define images
image bg creepy = "images/bg_creepy.jpg"
image bg blood_splatter = "images/bg_blood_splatter.png"
image bg door_lock = "images/bg_door_lock.png"
image bg escape_room_1 = "images/bg_escape_room_1.png"
image bg flashback1_nightclub_outside = "images/bg_flashback1_nightclub_outside.png"
image bg flashback2_empty_alley = "images/bg_flashback2_empty_alley.png"
image bg flashback3_kidnapping_chair = "images/bg_flashback3_kidnapping_chair.png"
image bg heavens_door = "images/bg_heavens_door.png"
image bg monitor = "images/bg_monitor.png"
image bg ring = "images/bg_ring.png"
image bg sleeping_chamber1 = "images/bg_sleeping_chamber1.png"
image bg_voting_room = "images/bg_voting_room.png"
image space_reveal_1 = "images/space_reveal_1.png"
image space_reveal_2_earth_reveal = "images/space_reveal_2_earth_reveal.png"

image exp sprite meta = Transform("images/exp_sprite_meta.png", zoom=0.8)


# Map character placeholders to the sprite
# Yukino uses original sprite from TEST02-YUKINOSPRITE
image yukino = ConditionSwitch("persistent.experimental_sprites", Transform("images/exp_sprite_yukino.png", zoom=0.8), "True", "images/yukino.png")
image y normal = ConditionSwitch("persistent.experimental_sprites", Transform("images/exp_sprite_yukino.png", zoom=0.8), "True", "images/yukino.png")
image y angry = ConditionSwitch("persistent.experimental_sprites", Transform("images/exp_sprite_yukino.png", zoom=0.8), "True", "images/yukino.png")
image y neutral = ConditionSwitch("persistent.experimental_sprites", Transform("images/exp_sprite_yukino.png", zoom=0.8), "True", "images/yukino.png")
image y worried = ConditionSwitch("persistent.experimental_sprites", Transform("images/exp_sprite_yukino.png", zoom=0.8), "True", "images/yukino.png")

image c silhouette = Transform("images/exp_sprite_cain.png", zoom=0.8)

# Cain sprites
image c neutral = ConditionSwitch("persistent.experimental_sprites", Transform("images/exp_sprite_cain.png", zoom=0.8), "True", "images/cain_tired_eyes.png")
image c tired = ConditionSwitch("persistent.experimental_sprites", Transform("images/exp_sprite_cain.png", zoom=0.8), "True", "images/cain_tired_eyes.png")
image c empty = ConditionSwitch("persistent.experimental_sprites", Transform("images/exp_sprite_cain.png", zoom=0.8), "True", "images/cain_empty_eyes.png")

image n neutral = Transform("images/exp_sprite_neuro.png", zoom=0.8)
image o1 neutral = Transform("images/exp_sprite_onika.png", zoom=0.8)

# Obie sprites
image o2 neutral = ConditionSwitch("persistent.experimental_sprites", Transform("images/exp_sprite_obie.png", zoom=0.8), "True", "images/obie_tired_eyes.png")
image o2 tired = ConditionSwitch("persistent.experimental_sprites", Transform("images/exp_sprite_obie.png", zoom=0.8), "True", "images/obie_tired_eyes.png")
image o2 empty = ConditionSwitch("persistent.experimental_sprites", Transform("images/exp_sprite_obie.png", zoom=0.8), "True", "images/obie_empty_eyes.png")
image o2 surprised = ConditionSwitch("persistent.experimental_sprites", Transform("images/exp_sprite_obie.png", zoom=0.8), "True", "images/obie_surprise_eyes_open.png")

image p neutral = Transform("images/exp_sprite_question_mark.png", zoom=0.8)
image p scared = Transform("images/exp_sprite_question_mark.png", zoom=0.8)
image d neutral = Transform("images/exp_sprite_dexter.png", zoom=0.8)
image k neutral = Transform("images/exp_sprite_kitchens.png", zoom=0.8)

image devil_avatar = Transform("images/exp_sprite_question_mark.png", zoom=0.8)

# Screen for the voting mechanism
screen vote_screen():
    modal True
    add Solid("#000000") alpha 0.9
    
    vbox:
        align (0.5, 0.5)
        spacing 30
        
        text "CHOOSE WHO DIES" size 50 color "#ff0000" xalign 0.5
        
        vpgrid:
            cols 3
            spacing 20
            
            python:
                vote_options = [
                    ("mc", "Arian"), ("y", "Yukino"), ("c", "Dr. Cain"),
                    ("n", "Neuro"), ("o1", "Onika"), ("o2", "Obie"),
                    ("p", "X"), ("d", "Dexter"), ("k", "Kitchens")
                ]
            
            for code, name in vote_options:
                button:
                    xysize (200, 250)
                    background Solid("#333")
                    hover_background Solid("#555")
                    action Return(code)
                    python:
                        portrait_map = {
                            "Arian": "voting_arian",
                            "Yukino": "voting_yukino",
                            "Dr. Cain": "voting_cain",
                            "Neuro": "voting_neuro",
                            "Onika": "voting_onika",
                            "Obie": "voting_obie",
                            "X": "voting_mysterious",
                            "Dexter": "voting_dexter",
                            "Kitchens": "voting_kitchens",
                        }
                        portrait_img = portrait_map.get(name, "voting_placeholder")
                    vbox:
                        align (0.5, 0.5)
                        spacing 10
                        add portrait_img zoom 0.18 xalign 0.5
                        text name align (0.5, 0.5) size 26

screen door_keypad():
    modal True
    default current_code = ""
    
    add Solid("#000000cc") # Dim background
    
    vbox:
        align (0.5, 0.5)
        spacing 20
        
        text "ENTER PASSCODE" size 40 color "#ffffff" xalign 0.5
        
        # Display
        frame:
            xalign 0.5
            xsize 400
            ysize 100
            background Solid("#000000")
            # Display code or underscores
            text "[current_code]" size 60 align (0.5, 0.5) color "#00ff00" font "gui/fonts/Mohr.ttf" kerning 10

        # Keypad
        grid 3 4:
            spacing 15
            xalign 0.5
            
            for i in range(1, 10):
                textbutton str(i):
                    xysize (100, 100)
                    background Solid("#333333")
                    hover_background Solid("#555555")
                    action If(len(current_code) < 4, SetScreenVariable("current_code", current_code + str(i)))
                    text_size 50
                    text_align 0.5
                    
            # Bottom row
            textbutton "CLR":
                xysize (100, 100)
                background Solid("#550000")
                hover_background Solid("#770000")
                action SetScreenVariable("current_code", "")
                text_size 30
                text_color "#ffaaaa"
                text_align 0.5
                
            textbutton "0":
                xysize (100, 100)
                background Solid("#333333")
                hover_background Solid("#555555")
                action If(len(current_code) < 4, SetScreenVariable("current_code", current_code + "0"))
                text_size 50
                text_align 0.5
                
            textbutton "ENT":
                xysize (100, 100)
                background Solid("#005500")
                hover_background Solid("#007700")
                action Return(current_code)
                text_size 30
                text_color "#aaffaa"
                text_align 0.5
                
        textbutton "Cancel":
            xalign 0.5
            action Return(None)
            text_size 30
            text_color "#aaaaaa"

# Logo animation transform
transform logo_appear:
    alpha 0.0 blur 20.0 zoom 1.05
    pause 1.0
    linear 3.0 alpha 1.0 blur 0.0 zoom 1.0
    pause 3.0
    linear 2.0 alpha 0.0
    pause 0.5

# The game starts here.

label bad_end:
    scene black with fade
    pause 1.5
    "You didn't make it."
    pause 0.5
    menu:
        "Return to main menu":
            $ renpy.full_restart()
        "Quit":
            $ renpy.quit(save_persistent=True)

label start:
    $ renpy.movie_cutscene("images/sleeping_chamber_intro.webm")
    
    scene black
    play music "audio/01-bass-slop.mp3" fadein 1.0
    pause 1.0
    show expression "images/gb_logo.png" at truecenter, logo_appear
    pause 10.5
    scene black with Dissolve(1.5)
    pause 0.5
    
    jump chapter1_scene1

label chapter1_scene1:
    # Scene 1: Brutal wake up
    # MC wakes up in unknown place without memory. Talks to Dexter and then gets punched, which knocks him out.
    
    play music "audio/03-nine-inch-slop.mp3" fadeout 1.0 fadein 1.0
    
    scene black with fade
    scene bg sleeping_chamber1 with dissolve
    "(MC internal monologue: waking up, pain, confusion)"
    
    mc "(Dialogue: Asks where he is, mentions memory loss)"
    
    # Dexter is the one confronting him here
    show d neutral
    
    d "(Dialogue: Dexter coldly acknowledges MC is awake)"
    
    mc "(Dialogue: Asks who Dexter is)"
    
    # Gets punched
    with vpunch
    
    "(Narration: Dexter cuts him off and punches Arian hard enough to drop him. The strike is sudden, deliberate, and brutal, not a random outburst.)"
    
    scene black with fade
    
    "(Narration: Fading to black, losing consciousness)"
    
    jump chapter1_scene2

label chapter1_scene2:
    # Scene 2: Flashback
    # MC remembers how he was beaten up because of his gambling/drug addiction bets and his body was sold to an unknown place.
    # (Add. the hook: person - the guy who buys him (C), flashbacks incomplete)
    
    play music "audio/09-industrial-slop.mp3" fadeout 1.5 fadein 0.5
    scene bg flashback1_nightclub_outside with dissolve
    
    # NVL Mode for Flashback
    window show
    
    nvl_narrator "(NVL Narration: Flashback starts. Sensory details of rain and blood.)"
    
    nvl_narrator "He felt sick. He couldn’t relax. He couldn’t do anything. There was something laying down on him like tiger, paralising his whole body."
    nvl_narrator "He thought about it every day and every night, it was part of his personality, part of his psyche, part of his body. It was just a small mistake he made few years ago. He always have too reckless."
    
    nvl clear
    
    nvl_narrator "Why shouldn’t I take risk - he thought? Then he decided to bet on a 2038 presidental race. On the underdog candidate, too. Why would he bet on the candidate that was predicted to win? You don’t make money this way."
    nvl_narrator "So he bet. It was a huge bet. He didn’t exactly have a money, so he borrowed from a friend of a friend, some shady guy he barely know. Little did he know that this debt would ruin his life in a long run."
    nvl_narrator "Not letting, go, always following him like dangerious debt collectors. He wasn’t exactly sure what organization he owe that huge amount of money. Maybe it was mafia? Something like that. But they were ruthless."

    nvl clear
    
    scene black with fade
    scene bg flashback2_empty_alley with dissolve

    nvl_narrator "(NVL Narration: Explaining the beating, gambling debts, and addiction context.)"

    nvl_narrator "He strolled off the night club slowly, walking down the alley and thinking how he can never enjoy things again. There’s always a huge burden on his chest."
    nvl_narrator "Then, he saw them. Two shadow figures. One at the end of the street, second one on the beginning. He had nowhere to run. Doesn’t mean he didn’t try."
    
    nvl clear
    
    mc "No, wait, I’ll—"
    nvl_narrator "He could barely say anything as two figures held him down and injectd him with a syrigae really quick, like they’re putting down an animal."

    nvl clear

    scene black with fade
    scene bg flashback3_kidnapping_chair with dissolve
    # Placeholder for character C (Buyer)
    show c silhouette with dissolve

    nvl_narrator "(NVL Narration: Memory of being sold. Description of the buyer (C).)"

    nvl_narrator "He woke up, but it was like he couldn’t wake up. His vision was completley blurred. Words were barely getting to him."
    nvl_narrator "All he knew in a second is that he’s in some place, tied to a chair. There were figures talking and moving but he couldn’t hear or see them."

    nvl clear
    window hide
    
    jump chapter1_scene3

label chapter1_scene3:
    # Scene 3: Getting shit together
    # MC wakes up again, takes his clothes, talks to Y and slowly mets cast members.
    # (Y, C, N, O1)
    
    scene black with fade
    pause 1.0

    play music "audio/12-piano-slop.mp3" fadeout 2.0 fadein 1.0
    scene bg sleeping_chamber1 with dissolve
    
    "(Narration: Waking up again, safe this time.)"
    
    "(Narration: MC finding and putting on clothes.)"
    
    show y neutral
    
    y "(Dialogue: Neutral greeting)"
    
    hide y
    
    # Show all characters with sprites together
    show y neutral at left
    show c silhouette at right
    
    "(Narration: My head is throbbing. My jaw hurts where Dexter punched me before I passed out...)"
    
    mc "Who... what is happening? Where the hell are we?! What is this place?!"

    scene bg creepy with fade
    show exp sprite meta with dissolve
    
    meta_char "Hi there. I'm a meta character."
    pause 0.2
    meta_char "Let me explain the game rules for you."
    pause 0.2
    meta_char "Characters can converse using procedurally generated dialogues."
    pause 0.2
    meta_char "Whenever the dialogue is procedurally generated, it will appear as {color=#FFE000}yellow text{/color}."
    pause 0.2
    meta_char "These dialogues are unique each round."
    pause 0.2
    meta_char "The only way to save is if you take a screenshot."
    pause 0.2
    meta_char "Anyway."
    pause 0.2
    meta_char "The goal of the game is to gain trust of the character and not die in the voting phase."
    pause 0.2
    meta_char "All characters vote based on their individual personality, results of past voting rounds, and your conversations with them."
    pause 0.2
    meta_char "If you can gain their trust by interacting with them, they will not vote you out and you will survive."
    pause 0.2
    meta_char "You can speak to them directly by clicking the speak button and entering your text."
    pause 0.2
    meta_char "That's all for now."
    
    scene bg sleeping_chamber1 with fade
    show y neutral at left
    show c silhouette at right
    
    # Random generated group conversation!
    python:
        context = "Arian just woke up completely disoriented and terrified. He has no idea what is happening or where they are. None of the characters know each other yet. Arian is demanding answers. The group must start establishing the situation and introducing themselves. Arian is secretly a former addict whose body was 'sold', and Dr. Cain secretly bought him (though Dr. Cain is hiding this and pretending to be a victim)."
        chars = {
            "Yukino": "A cute, soft-spoken kuudere girl who approaches problems with intense, emotionless logic. She thinks like an android analyzing odds, but acts like a quiet human.",
            "Dr. Cain": "A cold, calculating older scientist. He secretly arranged to buy Arian's body to pay off Arian's debts before they ended up trapped here, but he finds the current situation amusing and speaks cryptically.",
            "Neuro": "Terrified neurosurgeon. He clinically analyzes their panic, heart rates, and emotions, trying to understand fear.",
            "Onika": "A street-smart woman with a tough exterior. She's impatient, distrusts Arian because he looks pathetic, and just wants to find a way out."
        }
        char_objs = {
            "Yukino": y,
            "Dr. Cain": c,
            "Neuro": n,
            "Onika": o1
        }
        
    label .chat_selection:
        # Pre-seed the conversation so the group reacts to the outburst
        python:
            if not ai_director.history:
                ai_director.add_message("Arian", "Who... what is happening? Where the hell are we?! What is this place?! Who are you people?!")
                
        call start_group_scene(context, chars, char_objs) from _call_group_scene_chap1_3
        
        if _return:
            hide y
            hide c
            
            label .meet_group1:
                menu:
                    "The group conversation has concluded. Who should I talk to individually now?"
                    
                    "Talk to the girl who hit me (Yukino)":
                        show y neutral
                        "She looks at me with a cold, analytical gaze."
                        $ start_npc_conversation("Yukino", y)
                        hide y
                        jump .meet_group1
                        
                    "Talk to the older man (Dr. Cain)":
                        show c silhouette
                        "He smiles politely, though there's something deeply unsettling about it."
                        $ start_npc_conversation("Dr. Cain", c)
                        hide c
                        jump .meet_group1
                        
                    "Talk to the terrified man (Neuro)":
                        show n neutral
                        "He's hyperventilating and looking at the ceiling like it's going to collapse on us."
                        $ start_npc_conversation("Neuro", n)
                        hide n
                        jump .meet_group1
                        
                    "Talk to the energetic girl (Onika)":
                        show o1 neutral
                        "She gives me a weak, albeit optimistic smile."
                        $ start_npc_conversation("Onika", o1)
                        hide o1
                        jump .meet_group1
                        
                    "I've learned enough for now.":
                        pass
        
    jump chapter1_scene4

label chapter1_scene4:
    # Scene 4: What’s going on?
    # MC talks to other people who are locked in. Meeting full cast.
    # (O2, P, D)
    
    "(Narration: As I step further into the room, I notice the rest of the survivors.)"
    
    label .meet_group2:
        menu:
            "Who should I approach next?"
            
            "Talk to the exhausted woman (Obie)":
                show o2 tired
                o2 "...another one's awake. Name's Obie. And if I knew where we were, you think I'd still be sitting here?"
                $ start_npc_conversation("Obie", o2)
                hide o2
                jump .meet_group2
                
            "Talk to the arrogant guy (Dexter)":
                show d neutral
                "He grins cruelly, like he's enjoying the situation too much."
                $ start_npc_conversation("Dexter", d)
                hide d
                jump .meet_group2
                
            "Talk to the composed man (Kitchens)":
                show k neutral
                "He seems observant and rational, trying to make sense of the group."
                $ start_npc_conversation("Kitchens", k)
                hide k
                jump .meet_group2
                
            "I think I'm ready to figure a way out.":
                pass

    jump chapter1_scene5

label chapter1_scene5:
    # Scene 5: How do we get out?
    # MC & others solve the door puzzle and get out.
    # (Add. Timer)
    
    play music "audio/04-aethereal-slop-1.mp3" fadeout 1.0 fadein 0.5
    
    "(Narration: Realization they need to escape.)"
    
    "(Narration: Discovery of the door puzzle.)"
    scene black with fade
    scene bg door_lock with dissolve
    
    $ door_unlocked = False
    
    while not door_unlocked:
        menu:
            "Examine the lock":
                "It's a digital keypad. It requires a 4-digit code."
                
            "Talk to Yukino":
                show y worried
                y "I don't know... usually these things have a default password, right?"
                y "Like 1234? Or maybe all zeros?"
                menu:
                    "Keep talking to her":
                        $ start_npc_conversation("Yukino", y)
                    "Thanks":
                        pass
                hide y
                
            "Talk to Neuro":
                show n neutral
                n "If the admin was lazy, it's probably just 0000."
                n "Try that."
                menu:
                    "Keep talking to them":
                        $ start_npc_conversation("Neuro", n)
                    "Thanks":
                        pass
                hide n
                
            "Talk to Obie":
                show o2 tired
                o2 "You're still messing with that thing?"
                show o2 empty
                o2 "I already tried everything. Birthday combos, 1234, even random stuff."
                show o2 surprised
                o2 "Wait... did anyone try all zeros? Like 0000?"
                show o2 tired
                o2 "Ugh, I'm too exhausted to think straight."
                menu:
                    "Keep talking to her":
                        $ start_npc_conversation("Obie", o2)
                    "Thanks":
                        pass
                hide o2
                
            "Enter Code":
                call screen door_keypad
                $ entered_code = _return
                
                if entered_code == "0000":
                    play audio "audio/ui_click.wav" # Assuming this exists, or just silence
                    "The lock beeps positively."
                    $ door_unlocked = True
                elif entered_code is None:
                    "You step away from the keypad."
                else:
                    "The lock buzzes. Incorrect code."
    
    "(Narration: Sound of door unlocking and opening.)"
    
    jump chapter1_scene6

label chapter1_scene6:
    # Scene 6: The Devil
    # Computer program appears on screen and explains the rules of the game, the stakes (oxygen is running out, they have rings that could kill them any time and they can’t take it off, they have to unlock Heaven’s Door.
    # (Add. One person waking up after puzzle is solved, explanation of The Devil incomplete)
    
    play music "audio/11-monokuma-slop.mp3" fadeout 0.5 fadein 0.3
    scene black with fade
    scene bg monitor with dissolve
    
    "(Narration: The screen turns on.)"
    
    # Placeholder for The Devil (Computer Program)
    show devil_avatar
    
    os "(Dialogue: Welcome message)"
    
    os "(Dialogue: Explaining Rule 1 - Oxygen depletion)"
    os "(Dialogue: Explaining Rule 2 - Lethal rings/collars)"
    os "(Dialogue: Explaining the Goal - Unlock Heaven's Door)"
    
    # One person wakes up late
    "(Narration: One character wakes up late, missing the explanation.)"
    
    jump chapter1_scene7

label chapter1_scene7:
    # Scene 7: Heaven’s Door
    # First door unlocks and cast goes at the end of corridor where the Heaven’s Door is. It needs 4 McGuyvers from 4 escape rooms to unlock it. Unlocking it and getting out is the cast’s goal.
    # (Add. Countdown on the door, someone breaking down, name Seraph Nodes or similar)
    
    play music "audio/08-doki-slop.mp3" fadeout 1.0 fadein 1.0
    scene black with fade
    scene bg heavens_door with dissolve
    
    "(Narration: Arrival at Heaven's Door. Description of the door.)"
    
    "(Narration: Explanation of the 4 keys/Seraph Nodes requirement.)"
    
    # Countdown on the door
    "(Narration: Description of the countdown timer on the door.)"
    
    # Someone breaking down
    show p scared
    p "(Dialogue: Panicking, breaking down about dying)"
    
    jump chapter1_scene8

label chapter1_scene8:
    # Scene 8: Into Escape Room #1
    # Reluctant cast goes into first escape room (only door open). The Door closes behind them.
    
    play music "audio/14-vidya-slop.mp3" fadeout 1.0 fadein 0.5
    
    "(Narration: Noticing the only open door (Escape Room #1).)"
    
    "(Narration: Reluctant decision to enter.)"
    
    scene black with fade
    scene bg escape_room_1 with dissolve
    
    "(Narration: The door slamming shut behind them.)"
    
    jump chapter1_scene9

label chapter1_scene9:
    # Scene 9: Escape Room #1
    # Escape Room #1 requires them to go by pairs to cabins and choose who dies. If all of them vote for themselves, all survive.
    # (Add. Paranoia)
    
    "(Narration: Discovery of the room rules.)"
    
    window show
    
    nvl_narrator "(NVL Narration: Explaining the mechanics: Pairs, Cabins, Voting.)"
    
    nvl_narrator "(NVL Narration: The grim choice of who dies.)"
    
    nvl_narrator "(NVL Narration: The loophole: if everyone votes self, all survive.)"
    
    # Paranoia sets in
    nvl_narrator "(NVL Narration: If everyone follows the plan, we walk out alive. But if even one person betrays another...)"
    
    nvl clear
    window hide
    
    scene bg escape_room_1 with dissolve
    
    "Before we step into the voting booths, the tension in the room is suffocating."
    mc "Wait. Let's talk before we go in there."
    
    python:
        context = (
            "Location: outside the voting booths. The group just heard Arian say: "
            "'Everyone listen. The rules say if every single person gets exactly one death vote, nobody dies. "
            "There are 9 of us, each with one vote. If we all vote for ourselves, we each get one vote and the machine has no majority to execute. "
            "I'm proposing a survival pact — we all vote for ourselves. Nobody betrays anyone. We all walk out alive.' "
            "The characters must now react to this proposal, argue, agree or push back, and collectively commit to the plan before entering the booths. "
            "The conversation has just started. React to what Arian said first."
        )
        chars = {
            "Yukino": "A cute, soft-spoken kuudere girl who approaches problems with intense, emotionless logic. She quickly confirms the math is correct.",
            "Dr. Cain": "Condescending elite scientist pretending to be a victim. He agrees the pact is logically sound but makes it sound like his own idea.",
            "Neuro": "Terrified, anxious young guy who is smarter than he looks. He is scared but quickly sees the logic and wants everyone to commit.",
            "Onika": "Street-smart girl deeply attached to Obie. She is deeply relieved by the pact idea but suspicious someone will betray it.",
            "Obie": "Gentle, withdrawn doctor who deeply loves Onika. Quiet, but clearly agrees — he just wants everyone to survive.",
            "Dexter": "Sadistic, arrogant guy. He finds the pact boring but agrees out of cold self-preservation logic.",
            "Kitchens": "Stoic investigator. He strongly advocates for the pact and points out: anyone who receives 0 votes is immediately exposed as a traitor."
        }
        char_objs = {
            "Yukino": y,
            "Dr. Cain": c,
            "Neuro": n,
            "Onika": o1,
            "Obie": o2,
            "Dexter": d,
            "Kitchens": k
        }
        
    call start_group_scene(context, chars, char_objs) from _call_pact_chat
    
    "The agreement is sealed. At least, verbally."
    "But as everyone turns toward the dark voting booths, the silence grows heavy. A horrifying thought creeps into my mind: can I really trust them?"
    
    jump chapter1_scene10

label chapter1_scene10:
    # Scene 10: The Choice
    # MC discusses with Y who to choose. The Player makes the choice, voting on one of the 9 cast to die,
    # (Add. Multiple dialogues tones)
    
    play music "audio/02-electronic-slop.mp3" fadeout 1.0 fadein 0.5
    scene bg_voting_room with fade
    show y worried
    
    "(Narration: We step into the voting booth. The screen glows maliciously. We have a few moments to talk before the countdown ends.)"
    
    label .voting_discussion:
        menu:
            "Discuss the vote with Yukino"
            
            "Talk to her":
                python:
                    if not ai_dialogue_manager.get_npc("Yukino").history:
                        ai_dialogue_manager.get_npc("Yukino").add_message("user", "System note: They are currently standing inside the voting booth, deciding who to kill. If everyone votes for themselves, they all live, but if someone betrays them, they could die.")
                $ start_npc_conversation("Yukino", y)
                jump .voting_discussion
                
            "I've made my decision. Time to vote.":
                pass
    
    # Player choice using the visual vote screen
    window hide
    call screen vote_screen
    $ vote = _return
    window show
    
    if vote == "mc":
        mc "(Dialogue: Deciding to vote self (Trust path))"
    elif vote == "y":
        mc "(Dialogue: Deciding to vote Y (Betray path))"
    else:
        mc "(Dialogue: Deciding to vote for [vote])"
        
    jump chapter1_scene11

screen display_votes(tally_text):
    zorder 100
    frame:
        align (0.6, 0.4)
        padding (40, 40)
        background Solid("#000000DD")
        vbox:
            spacing 10
            text "LIVE VOTE TALLY" size 40 color "#FF0000" bold True xalign 0.5
            null height 20
            text tally_text size 30 color "#FFFFFF" xalign 0.5 text_align 0.5

label chapter1_scene11:
    # Scene 11: Consequences
    
    play music "audio/13-smooth-slop.mp3" fadeout 0.5 fadein 0.3
    scene black with fade
    scene bg ring with dissolve
    
    python:
        char_names = {
            "mc": "Arian", "y": "Yukino", "c": "Dr. Cain", "n": "Neuro",
            "o1": "Onika", "o2": "Obie", "d": "Dexter", "k": "Kitchens", "p": "X"
        }
        name_to_id = {v: k for k, v in char_names.items()}
        
        # The full name list for voting (Chapter 1 — all 9 are alive)
        all_names = list(char_names.values())
        
        # Personality blurbs for each NPC voter — drives character-consistent decisions
        npc_voter_roster = {
            "Yukino":   "Calm, logical kuudere. Votes for whoever poses the greatest mathematical threat to the group's survival.",
            "Dr. Cain": "Cold, calculating scientist. Votes to protect himself and eliminate competitors who might expose him.",
            "Neuro":    "Terrified neurosurgeon barely holding together. Votes for whoever scares them most.",
            "Onika":    "Street-smart survivor. Votes to protect Obie and eliminate anyone hostile or suspicious.",
            "Obie":     "Gentle, withdrawn doctor. Deeply distrusts Arian. Will vote for Arian unless trust has been established.",
            "Dexter":   "Sadistic and calculating. Votes for whoever is weakest and easiest to justify eliminating.",
            "Kitchens": "Stoic investigator. Votes for whoever is acting most suspicious based on their behavior.",
            "X":        "Silent, alien, unreadable. Votes entirely randomly to protect their own strange agenda.",
        }
        
        # Arian votes (player choice already captured in `vote`)
        votes = {k: 0 for k in char_names.keys()}
        votes[vote] += 1
        
        # The survival pact context — every NPC knows the agreement was to vote for themselves
        pact_context = (
            "IMPORTANT GAME CONTEXT: Before the vote, all 9 survivors unanimously agreed to a 'Survival Pact' "
            "where everyone votes for THEMSELVES so no one dies. However, you may choose to secretly betray "
            "this pact and vote for someone more dangerous, or honor it and vote for yourself."
        )
        
        # Each NPC casts a real AI vote
        for npc_name, blurb in npc_voter_roster.items():
            ai_vote_name = conduct_blind_ai_vote(npc_name, blurb, all_names, pact_context)
            vote_id = name_to_id.get(ai_vote_name, None)
            if vote_id and vote_id in votes:
                votes[vote_id] += 1
            else:
                # Safefall: self-vote (pact)
                self_id = name_to_id.get(npc_name, None)
                if self_id and self_id in votes:
                    votes[self_id] += 1
        
        # Determine outcome — true highest vote count wins, no rigging
        highest = max(votes.values())
        top_chars = [k for k, v in votes.items() if v == highest]
        
        if len(top_chars) > 1 and all(v == 1 for v in votes.values()):
            # Perfect zero-sum tie — everyone voted for themselves, pact held
            dead_char_id = "none"
        else:
            if len(top_chars) > 1:
                # Real tie — 50/50 if Arian is involved, else random
                if "mc" in top_chars and random.random() < 0.5:
                    dead_char_id = "mc"
                else:
                    dead_char_id = random.choice(top_chars)
            else:
                dead_char_id = top_chars[0]
                
        # List of tuples, sorted by votes ascending (lowest first, highest last)
        tally_array = []
        for v_id, count in sorted(votes.items(), key=lambda x: x[1]):
            tally_array.append((v_id, count))
                
        vote_mechanics_briefing = (
            "VOTING MECHANICS (understand this perfectly): 9 people, each casting exactly ONE death vote. "
            "The survival pact was everyone votes for themselves so each person gets 1 vote and nobody dies. "
            "ONLY a person with 0 votes is a CONFIRMED traitor — nobody voted for them, not even themselves, so they must have voted for someone else. "
            "A person with 1 vote almost certainly voted for themselves and nobody else targeted them. "
            "A person with 2+ votes was targeted by multiple people — but this does NOT make them a traitor. "
            "One of those votes is almost certainly their own self-vote. So 3 votes = they self-voted + 2 others targeted them. They are likely innocent. "
            "NEVER accuse someone of being a traitor just because they received many votes. Only 0-vote people are confirmed traitors. "
            "ONE PERSON CANNOT VOTE TWICE. Do not suggest or imply that. "
        )
        zero_vote_traitors = [char_names[vid] for vid, cnt in votes.items() if cnt == 0 and vid != "none"]
        traitor_note = f" CONFIRMED TRAITORS (received 0 votes, meaning they voted for someone else): {', '.join(zero_vote_traitors)}. Accuse them first!" if zero_vote_traitors else " Everyone received at least 1 vote."
        death_summary = ", ".join([f"{char_names[vid]}: {count} votes" for vid, count in votes.items() if count > 0])

        death_context_prefix = (
            vote_mechanics_briefing +
            f"EXACT VOTE BOARD RESULTS: {death_summary}.{traitor_note} "
            "Nobody knows WHO voted for whom, only the totals on the board. "
            "React with horror, paranoia, and furious finger-pointing. Accuse based on the numbers. "
            "Arian must NOT be purely defensive — he should also accuse others aggressively. "
            "React like real terrified humans, not psychopaths."
        )
        
        death_context = death_context_prefix
        dead_char = ""
        surviving_chars = {
            "Yukino": "A cute, soft-spoken kuudere girl who approaches problems with intense, emotionless logic. Thinks in probabilities but speaks like a quiet human.",
            "Dr. Cain": "Condescending elite scientist pretending to be a victim.",
            "Onika": "Bright girl deeply attached to Obie. Unaware she is a clone.",
            "Neuro": "Terrified neurosurgeon.",
            "Obie": "Withdrawn doctor who deeply loves Onika and hates Arian.",
            "Dexter": "Sadistic associate who enjoys violence.",
            "Kitchens": "Stoic investigator trying to maintain order."
        }
        surviving_objs = {
            "Yukino": y, "Dr. Cain": c, "Onika": o1, "Neuro": n, 
            "Obie": o2, "Dexter": d, "Kitchens": k
        }

    "System" "VOTING PERIOD CONCLUDED. TABULATING RESULTS."
    "The central screen flickers on, casting a harsh red light over the room."
    
    $ current_tally_text = ""
    show screen display_votes(current_tally_text)
    
    python:
        # Register Arian so we can generate his lines too
        ai_dialogue_manager.register_npc(
            "Arian",
            "the terrified but defensive player character",
            "You are Arian. You just woke up in a deadly death game with no memory. You are extremely defensive, paranoid, and scared."
        )

    $ i = 0
    while i < len(tally_array):
        $ v_id, v_count = tally_array[i]
        $ v_name = char_names[v_id].upper()
        $ npc_name = char_names[v_id]
        $ v_str = "VOTES" if v_count != 1 else "VOTE"

        $ current_tally_text += v_name + " -- " + str(v_count) + " " + v_str + "\n"
        show screen display_votes(current_tally_text)

        if v_id == "p":
            p "..."
        elif random.random() < 0.6 or v_count > 0:
            python:
                mechanics = (
                    "VOTING MECHANICS: There are 9 people. Each person casts exactly ONE death vote for one other person (or themselves). "
                    "The survival pact was: everyone votes for THEMSELVES so everyone gets exactly 1 vote and nobody dies. "
                    "Getting 0 votes means NOBODY voted for you — including yourself — so YOU voted for someone else and broke the pact. CONFIRMED TRAITOR. "
                    "Getting 1 vote means you almost certainly voted for yourself and nobody else targeted you. Honored the pact. "
                    "Getting 2+ votes means multiple people voted for you — but this does NOT make you a traitor. "
                    "One of those votes is almost certainly your own self-vote. 3 votes = you self-voted + 2 others targeted you. You are likely innocent. "
                    "NEVER assume someone is a traitor because they received many votes. Only 0-vote people are confirmed traitors. "
                    "It is IMPOSSIBLE for one person to vote multiple times. "
                )
                if v_count == 0:
                    prompt = mechanics + f"The board just showed {npc_name} received ZERO death votes. You are now publicly exposed — you did not vote for yourself, which means you cast your death vote on someone else and betrayed the pact. React with ONE sentence of panicked denial or a desperate excuse. Output only spoken dialogue, no asterisks."
                elif v_count == 1:
                    prompt = mechanics + f"The board shows {npc_name} received exactly ONE death vote — almost certainly your own self-vote. You honored the pact and survived. React with ONE sentence of relief, smugness, or shaky exhale. Output only spoken dialogue, no asterisks."
                elif v_count >= 2 and v_id != dead_char_id:
                    prompt = mechanics + f"The board shows {npc_name} received {v_count} death votes. That means {v_count} different people each cast their single vote for you — you barely survived because you weren't the highest. React with ONE sentence of furious rage at whoever targeted you. Output only spoken dialogue, no asterisks."
                else:
                    prompt = mechanics + f"The board shows {npc_name} received the most death votes and will be executed. React with ONE sentence of pure terror and outrage. Output only spoken dialogue, no asterisks."

                react_line = ai_dialogue_manager.get_response(npc_name, prompt)
                react_line = react_line.replace("*", "").replace("(", "").replace(")", "").replace('"', '')
                react_line = "{color=#FFE000}" + react_line + "{/color}"

                char_map = {"mc": mc, "y": y, "c": c, "n": n, "o1": o1, "o2": o2, "d": d, "k": k}
                speaker = char_map.get(v_id)
                if speaker:
                    speaker(react_line)
        else:
            "System" "..."

        $ i += 1

    # BUILD VOTE CONTEXT FOR THE AI
    python:
        vote_summary = ", ".join([f"{char_names[k]}: {v} votes" for k,v in votes.items()])
        log_ai_dialogue("STATE", f"VOTE_RESULT | tally: {vote_summary} | executed: {dead_char if dead_char_id != 'none' else 'none'}", "State")
        death_context += f" THE EXACT FINAL VOTE COUNT WAS: {vote_summary}. Use this information to accuse people! CRITICAL GAME LOGIC: The characters agreed to all vote for themselves to survive. Therefore, ANYONE who received exactly 0 votes is a confirmed traitor who broke the agreement! ATTACK THEM AND ACCUSE THEM FIRST! "
        death_context += "CRITICAL INSTRUCTION FOR DEXTER: If Arian (the player) is extremely suspiciously denying things and the group turns on him, AND Dexter is still alive, Dexter can decide to literally murder Arian mid-argument. If Dexter executes Arian, YOU MUST MENTION THE PHRASE [DEXTER KILLS ARIAN] IN YOUR RESPONSE. Do NOT kill Arian unless he acts incredibly weak or sus!"

    "System" "TABULATION COMPLETE."
    
    if dead_char_id == "none":
        "System" "ALL PARTICIPANTS RECEIVED 1 VOTE. ZERO-SUM PROTOCOL INITIATED. NO CASUALTIES."
        hide screen display_votes
        "The screen flashes green. A heavy mechanical clunk echoes through the room."
        scene bg ring with dissolve
        "We step out of the booths. Everyone is looking at each other, chests heaving."
        $ death_context += "[VOTING RESOLVED PEACEFULLY: Arian voted for himself, completing the zero-sum loop. No one died. Everyone is stepping out of the booths. React with EXTREME relief, panting, and deep suspicion! Accuse each other!]"
    else:
        $ dead_name = char_names.get(dead_char_id, "Unknown")
        "System" "WARNING. MAXIMUM VOTES RECEIVED BY: [dead_name]."
        
        # PRE-DEATH REACTION
        if dead_char_id == "mc":
            mc "Wait... me? ME?! No! This has to be a mistake! Who voted for me?!"
        elif dead_char_id == "y":
            y "Wait, no... seriously? You're actually killing me? Which one of you backstabbing cowards did this?!"
        elif dead_char_id == "c":
            c "Fools! Idiots! Do you even comprehend who you're killing?!"
        elif dead_char_id == "n":
            n "No no no! PLEASE! I'm sorry! I take it back! Let me out! AAAAAGH!"
        elif dead_char_id == "o1":
            o1 "Obie...? I'm scared... Obie, please save me!"
            o2 "ONIKA! NO! WHO VOTED FOR MY SISTER?! I'LL KILL YOU ALL!"
        elif dead_char_id == "o2":
            o2 "Dammit... Predictable. Onika... don't look... close your eyes!"
            o1 "Obie?! What's happening?!"
        elif dead_char_id == "d":
            d "What?! You little rats actually voted for me?! WHICH ONE OF YOU SCUMBAGS DID THIS?! I'LL KILL EVERY SINGLE ONE OF YOU!"
        elif dead_char_id == "k":
            k "Predictable panic. Try to survive without me, you animals. Remember that whoever voted for me is the real traitor."
        elif dead_char_id == "p":
            p "Hey wait! Let me out of here! This isn't funny! Who voted for me?!"

        "System" "EXECUTING PENALTY PROTOCOL."
        scene bg blood_splatter with hpunch
        
        if dead_char_id == "mc":
            "Before I can even process the betrayal, the booth fills with a searing, flesh-melting fire."
            "The agony is absolute. My body turns to ash as my final screams echo in the chamber."
            "DEAD END."
            jump bad_end
            
        elif dead_char_id == "y":
            "The moment Yukino finishes her sentence, a massive steel spear drops, impaling her violently through the chest."
            "Her eyes don't widen. She just stares down at the hole in her torso, synthetic white fluid leaking out instead of blood before she collapses."
            $ dead_char = "Yukino"
            $ death_context += "[GORE CONTEXT: Yukino was expertly IMPALED by a steel spear from the ceiling. SCREAM IN HORROR. POINT FINGERS. EVERYONE IS TERRIFIED AND PANICKING!]"

        elif dead_char_id == "c":
            "A violent crunch echoes across the room. The glass of Dr. Cain's booth suddenly shrinks inward, crushing him with thousands of pounds of pressure."
            "His ribs shatter while he ominously laughs his final breath."
            $ dead_char = "Dr. Cain"
            $ death_context += "[GORE CONTEXT: Dr. Cain was violently CRUSHED to death by his glass booth. Blood everywhere. Everyone is horrified! Accuse each other of murder!]"

        elif dead_char_id == "n":
            "The ceiling above Neuro's booth opens. A blinding beam of heated light drops squarely onto Neuro."
            "He agonizingly burns to ash while begging for his life, leaving nothing but a charred, smoking stain on the floor."
            $ dead_char = "Neuro"
            $ death_context += "[GORE CONTEXT: Neuro was brutally BURNED ALIVE by a laser. Scream and vomit! Panic! Who voted to murder him?!]"

        elif dead_char_id == "o1":
            "Before Onika can even say another word, a mechanized wire wraps around her throat, pulling tight."
            "A sickening *snap* echoes through the air as her body goes limp and falls."
            $ dead_char = "Onika"
            $ death_context += "[GORE CONTEXT: Onika's neck was violently snapped by a wire. Obie MUST BE WEEPING AND SCREAMING IN HYSTERICS, aggressively attacking everyone! Completely horrific panic!]"

        elif dead_char_id == "o2":
            "A heavy metallic slab drops from the ceiling of Obie's booth, crushing her lower half instantly."
            "The booth fills with a green, acidic gas, melting her skin before she can finish."
            $ dead_char = "Obie"
            $ death_context += "[GORE CONTEXT: Obie was cut in half by a slab and melted by acidic gas. Onika MUST BE WEEPING AND SCREAMING. Total devastation! Accuse each other!]"

        elif dead_char_id == "d":
            "While Dexter continues raging, a floor panel gives way beneath him. He drops into a pit of spinning industrial blades."
            "The blades spin faster, tearing him limb from limb. His arrogant scream turns into a pathetic gurgle of blood."
            $ dead_char = "Dexter"
            $ death_context += "[GORE CONTEXT: Dexter was shredded by industrial blades! Blood and guts spray up. SCREAM IN HORROR AND FEAR! YOU MIGHT BE NEXT!]"

        elif dead_char_id == "k":
            "A high caliber bullet fires from an automated turret, piercing straight through Kitchens' skull."
            "His brains paint the wall behind him as his body slumps over."
            $ dead_char = "Kitchens"
            $ death_context += "[GORE CONTEXT: Kitchens' head was blown open by a turret. Brains everywhere! React with survival terror! Scream! Tremble!]"

        elif dead_char_id == "p":
            "A deafening alarm rings out, and the masked figure's booth violently ejects out of the room, sending him into a gruesome spatial vortex."
            "He makes no sound as he vanishes."
            $ dead_char = "X"
            $ death_context += "[GORE CONTEXT: X was violently sucked out of the room. Panic and fear sets in immediately. Accuse the others!]"

        python:
            if dead_char in surviving_chars:
                del surviving_chars[dead_char]
            if dead_char in surviving_objs:
                del surviving_objs[dead_char]

    if dead_char_id != "mc":
        if "Yukino" in surviving_chars:
            show y neutral at left
        if "Dr. Cain" in surviving_chars:
            show c silhouette at right

        call start_group_scene(death_context, surviving_chars, surviving_objs) from _call_group_scene_chap1_11
        hide screen display_votes

label chapter1_scene12:
    # Scene 12: The Reveal
    
    "(Narration: Obtaining the Seraph Node (Key).)"
    
    play music "audio/10-midi-slop.mp3" fadeout 2.0 fadein 1.5
    scene space_reveal_1 with fade
    
    "Before we can even process what we're holding, a low, mechanical hum echoes through the floor."
    "The metal walls surrounding us begin to shift, turning translucent before vanishing entirely into pure glass."
    "Then, we see it."
    "Stars."
    
    scene space_reveal_2_earth_reveal with fade
    
    "We aren't in a basement. We aren't in a bunker."
    "We are on a massive spacecraft, suspended in the dark void of space."
    "And looming massively beneath us is the blue and brown marble of Earth... except it's tainted, broken, and churning with unnatural storms."
    "Suddenly, the entire ship lurches violently. Alarms blare. A red flashing warning indicates orbital decay."
    "We are plunging straight down toward the dying planet."

    python:
        reveal_context = (
            "The walls of the escape room have just turned to glass, revealing that the entire 'death game' is taking place on a spaceship orbiting Earth! "
            "Not only that, but the ship has just lost orbit and is actively plummeting toward a ruined, apocalyptic version of Earth. "
            "Everyone must react to this insane plot twist—taking in the horrifying reality that they are trapped in space, falling to their deaths on a ruined planet. "
            "Mix absolute despair with desperate panic. React to the environment and incorporate the plot twist into the dialogue!"
        )
        
        # We use the surviving characters from the voting scene.
        ai_director.clear_history()
        ai_director.add_message("System", "CRITICAL VISUAL UPDATE: The walls just vanished to reveal you are on a spaceship in orbit. The ship is now crashing down toward a ruined Earth. REACT TO THIS EXTREME TWIST!")

    call start_group_scene(reveal_context, surviving_chars, surviving_objs) from _call_reveal_chat

    "The sheer scale of our nightmare is finally clear."
    
    nvl_narrator "(NVL Narration: Chapter One End.)"
    
    nvl clear
    window hide
    
    scene black with fade
    show text "{size=80}CHAPTER 1 COMPLETE{/size}" at truecenter with dissolve
    pause 4.0
    hide text with dissolve
    
    jump chapter2_scene1

screen dynamic_room_vote(valid_names):
    modal True
    
    # Semi-transparent dark overlay — lets the voting room bg show through
    add Solid("#00000088")
    
    vbox:
        align (0.5, 0.5)
        spacing 10
        
        text "CHOOSE WHO DIES" size 50 color "#ff0000" xalign 0.5 bold True
        
        vpgrid:
            cols min(4, len(valid_names))
            spacing 20
            xalign 0.5
            for name in valid_names:
                button:
                    xysize (200, 250)
                    background Solid("#222222CC")
                    hover_background Solid("#660000CC")
                    action Return(name)
                    python:
                        portrait_map = {
                            "Arian": "voting_arian",
                            "Yukino": "voting_yukino",
                            "Dr. Cain": "voting_cain",
                            "Neuro": "voting_neuro",
                            "Onika": "voting_onika",
                            "Obie": "voting_obie",
                            "X": "voting_mysterious",
                            "Dexter": "voting_dexter",
                            "Kitchens": "voting_kitchens",
                        }
                        portrait_img = portrait_map.get(name, "voting_placeholder")
                    vbox:
                        align (0.5, 0.5)
                        spacing 10
                        add portrait_img zoom 0.18 xalign 0.5
                        text name align (0.5, 0.5) size 26 color "#ffffff"

screen chapter2_vote_history_menu():
    modal True
    add Solid("#000000D0")
    
    vbox:
        align (0.5, 0.5)
        spacing 20
        
        text "VOTE HISTORY" size 50 color "#ff0000" xalign 0.5 bold True
        
        viewport:
            xysize (800, 600)
            scrollbars "vertical"
            mousewheel True
            
            vbox:
                spacing 15
                if "chapter2_vote_history" in store.__dict__ and store.chapter2_vote_history:
                    for rnd in store.chapter2_vote_history:
                        frame:
                            xfill True
                            background Solid("#222222")
                            padding (20, 20)
                            hbox:
                                spacing 40
                                vbox:
                                    xalign 0.5
                                    python:
                                        dead_portrait_map = {
                                            "Arian": "voting_arian",
                                            "Yukino": "voting_yukino",
                                            "Dr. Cain": "voting_cain",
                                            "Neuro": "voting_neuro",
                                            "Onika": "voting_onika",
                                            "Obie": "voting_obie",
                                            "X": "voting_mysterious",
                                            "Dexter": "voting_dexter",
                                            "Kitchens": "voting_kitchens",
                                        }
                                        dead_img = dead_portrait_map.get(rnd['executed'], "voting_placeholder")
                                    add dead_img zoom 0.5 xalign 0.5
                                    text "ELIMINATED" color "#ff0000" size 20 xalign 0.5 bold True
                                vbox:
                                    spacing 5
                                    text "Round [rnd['round']]" size 35 bold True color "#ffffff"
                                    text "Eliminated: [rnd['executed']]" size 28 color "#ff5555"
                                    null height 10
                                    text "Tally Breakdown:" size 22 color "#aaaaaa"
                                    text "[rnd['tally']]" size 20 color "#dddddd"
                else:
                    text "No rounds have been completed yet." size 25 xalign 0.5 color "#ffffff"
        
        textbutton "Close" action Hide("chapter2_vote_history_menu") xalign 0.5

label chapter2_scene1:
    scene space_reveal_2_earth_reveal with fade
    
    window show
    
    nvl_narrator "The vast expanse of space lay before us. The blue marble of Earth, tainted and broken, spinning silently below."
    nvl_narrator "We had survived the first trap, but the game was just beginning."
    nvl_narrator "A metallic screech echoed from the speakers above."
    
    nvl clear
    
    os "CONGRATULATIONS ON COMPLETING THE FIRST PHASE."
    os "HOWEVER... I MUST APOLOGIZE."
    os "THERE ARE ONLY THREE INTACT ESCAPE PODS REMAINING IN THE ARMORY."
    os "ONLY THREE MAY CROSS HEAVEN'S GATE."
    os "THE CULLING PROTOCOL IS NOW ACTIVE."
    
    nvl clear
    
    nvl_narrator "The room split apart. Hidden doors opened, and automated bulkheads descended, separating us."
    nvl_narrator "We were to be locked into small interrogation rooms with random people."
    nvl_narrator "A timer would start. At the end of the timer, we had to cast a vote."
    nvl_narrator "The person with the most votes in each room would be executed. We would repeat this until only three of us remained."
    
    nvl clear
    window hide

    label death_game_loop:
        python:
            if "surviving_chars" not in store.__dict__:
                renpy.jump("start")
            
            # Arian + X others
            current_survivors = len(surviving_chars) + 1
        
        if current_survivors <= 3:
            jump chapter2_ending
            
        scene bg sleeping_chamber1 with fade
        
        python:
            num_to_pick = 1
            room_chars_keys = random.sample(list(surviving_chars.keys()), num_to_pick)
            room_chars = {k: surviving_chars[k] for k in room_chars_keys}
            room_objs = {k: surviving_objs[k] for k in room_chars_keys}
            names_str = ", ".join(room_chars_keys)
            
            history_context = ""
            if "chapter2_vote_history" in store.__dict__ and store.chapter2_vote_history:
                history_context = "PAST ROUNDS HISTORY:\n"
                for rnd in store.chapter2_vote_history:
                    history_context += f"- Round {rnd['round']}: {rnd['executed']} was executed. Tally was: {rnd['tally']}.\n"
                    
            context = f"Arian has been locked in a tiny, claustrophobic execution cabin with exactly one person: {names_str}. This is a 1-on-1 interrogation against {names_str}. You both have exactly 7 conversational turns. IMPORTANT: When the timer ends, you both will vote along with ALL OTHER SURVIVORS globally. The person with the most global votes across the facility dies. Arian must negotiate an alliance with {names_str} to vote against someone else in the facility, or trick them into sacrificing themselves. {history_context}"
            
        "I find myself shoved into a small room."
        "The heavy door seals shut behind me. There's a digital timer on the wall. It's counting down."
        "I'm locked in here with [names_str]."
        "We have to decide who dies."
        
        call start_death_game_scene(context, room_chars, room_objs, max_turns=7) from _call_death_game
        $ chat_history_str = _return
        
        "System" "TIME IS UP. CAST YOUR VOTES."
        
        window hide
        scene bg_voting_room with fade
        $ global_targets = ["Arian"] + list(surviving_chars.keys())
        call screen dynamic_room_vote(global_targets)
        $ arian_vote = _return
        window show
        
        "The screen flashes as the global votes are tabulated..."
        
        python:
            vote_tally = {t: 0 for t in global_targets}
            
            vote_tally[arian_vote] += 1
            
            npc_vote = conduct_ai_vote(names_str, global_targets, chat_history_str)
            if npc_vote in vote_tally:
                vote_tally[npc_vote] += 1
            else:
                vote_tally["Arian"] += 1
                
            # Off-screen survivors: each casts a genuine AI vote based on their personality + history
            for other_name, other_blurb in surviving_chars.items():
                if other_name != names_str:
                    blind_vote = conduct_blind_ai_vote(other_name, other_blurb, global_targets, history_context)
                    if blind_vote in vote_tally:
                        vote_tally[blind_vote] += 1
                    else:
                        vote_tally["Arian"] += 1
                    
            highest_votes = max(vote_tally.values())
            losers = [k for k, v in vote_tally.items() if v == highest_votes]
            
            if len(losers) > 1:
                if "Arian" in losers and random.random() < 0.5:
                    execution_target = "Arian"
                else:
                    execution_target = random.choice(losers)
            else:
                execution_target = losers[0]
                
            tally_text = "\n".join([f"{k}: {v} votes" for k, v in vote_tally.items()])
            
            if "chapter2_vote_history" not in store.__dict__:
                store.chapter2_vote_history = []
            
            history_tally = ", ".join([f"{k}: {v}" for k, v in vote_tally.items() if v > 0])
            store.chapter2_vote_history.append({
                "round": len(store.chapter2_vote_history) + 1,
                "executed": execution_target,
                "tally": history_tally
            })
            
        show screen display_votes(tally_text)
        "System" "TABULATION COMPLETE."
        "System" "EXECUTING: [execution_target]."
        hide screen display_votes
        
        scene bg blood_splatter with hpunch
        
        if execution_target == "Arian":
            "The lasers descend from the ceiling. I scream as my flesh begins to burn."
            "The others watch me burn to ash."
            "DEAD END."
            return
        else:
            "A spike tears through the floor, instantly impaling [execution_target]."
            "[execution_target] dies instantly, blood spraying across our faces."
            "The door slides open."
            
            python:
                del surviving_chars[execution_target]
                del surviving_objs[execution_target]
                
        "We step out of the room, leaving the corpse behind."
        jump death_game_loop
        
    label chapter2_ending:
        scene bg heavens_door with fade
        "System" "CULLING COMPLETE. REQUIRED NUMBER OF PARTICIPANTS REACHED."
        "System" "HEAVEN'S GATE UNLOCKED."
        
        "The massive vault doors grind open."
        "The three of us. Covered in blood. The only ones left."
        "We step forward into the escape pods..."
        
        show text "{size=80}TO BE CONTINUED...\nEND OF DEMO{/size}" at truecenter with dissolve
        pause 5.0
        return
