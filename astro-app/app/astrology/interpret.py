"""Free natal chart report, built from a library of interpretations.

No external API is used: the report is assembled from the calculated chart
(planet signs, houses, aspects and element balance), so it is instant and costs nothing.
Output uses "## " section headings, which the frontend renders.
"""

SIGNS = {
    "Aries": {"element": "Fire", "style": "directly, boldly and with a need to act first",
              "traits": ["courageous", "independent", "impatient"]},
    "Taurus": {"element": "Earth", "style": "steadily, sensually and at your own pace",
               "traits": ["loyal", "patient", "stubborn"]},
    "Gemini": {"element": "Air", "style": "curiously, quickly and through conversation",
               "traits": ["witty", "adaptable", "restless"]},
    "Cancer": {"element": "Water", "style": "protectively, intuitively and through emotional bonds",
               "traits": ["caring", "sensitive", "moody"]},
    "Leo": {"element": "Fire", "style": "warmly, generously and with a flair for self-expression",
            "traits": ["confident", "creative", "proud"]},
    "Virgo": {"element": "Earth", "style": "carefully, practically and with an eye for detail",
              "traits": ["helpful", "analytical", "self-critical"]},
    "Libra": {"element": "Air", "style": "gracefully, diplomatically and through partnership",
              "traits": ["fair-minded", "charming", "indecisive"]},
    "Scorpio": {"element": "Water", "style": "intensely, privately and with great depth",
                "traits": ["determined", "perceptive", "guarded"]},
    "Sagittarius": {"element": "Fire", "style": "adventurously, optimistically and in search of meaning",
                    "traits": ["honest", "free-spirited", "restless"]},
    "Capricorn": {"element": "Earth", "style": "responsibly, ambitiously and with long-term vision",
                  "traits": ["disciplined", "reliable", "reserved"]},
    "Aquarius": {"element": "Air", "style": "independently, inventively and with an eye on the bigger picture",
                 "traits": ["original", "humanitarian", "detached"]},
    "Pisces": {"element": "Water", "style": "imaginatively, compassionately and through intuition",
               "traits": ["empathetic", "artistic", "dreamy"]},
}

PLANETS = {
    "Sun": ("your core identity and vitality", "sense of self"),
    "Moon": ("your emotional needs and instincts", "emotions"),
    "Mercury": ("the way you think and communicate", "mind"),
    "Venus": ("how you love, relate and enjoy life", "heart"),
    "Mars": ("your drive and how you go after what you want", "drive"),
    "Jupiter": ("where you grow and find opportunity", "optimism"),
    "Saturn": ("your sense of responsibility and the lessons that build lasting strength", "discipline"),
    "Uranus": ("your urge for freedom and change", "need for freedom"),
    "Neptune": ("your imagination and spiritual longing", "imagination"),
    "Pluto": ("your capacity for deep transformation", "inner intensity"),
    "North Node": ("the direction of growth your life keeps pointing you towards", "life direction"),
}

HOUSES = {
    1: "self-image and first impressions", 2: "money, possessions and self-worth",
    3: "communication, learning and siblings", 4: "home, family and roots",
    5: "creativity, romance and joy", 6: "daily work, routines and health",
    7: "partnerships and marriage", 8: "shared resources, intimacy and transformation",
    9: "travel, higher learning and beliefs", 10: "career, reputation and public life",
    11: "friends, groups and future hopes", 12: "solitude, the unconscious and your inner life",
}

SUN = {
    "Aries": "At your core you are a starter. You come alive when there is something to begin, win or defend, and you prefer action to waiting.",
    "Taurus": "At your core you value stability, comfort and things that last. You build slowly and reliably, and once you commit, you rarely let go.",
    "Gemini": "At your core you are curious and quick. Variety, ideas and conversation keep you alive, and you learn by trying many things.",
    "Cancer": "At your core you are a protector. Home, family and emotional safety matter deeply to you, and you care for others instinctively.",
    "Leo": "At your core you want to shine and create. You have natural warmth and generosity, and you thrive when your efforts are seen and appreciated.",
    "Virgo": "At your core you want to be useful and to get things right. You notice details others miss and find meaning in making things better.",
    "Libra": "At your core you seek harmony, beauty and fairness. You understand people well and often discover yourself through relationships.",
    "Scorpio": "At your core you are intense and private. You look beneath the surface, commit completely, and have a remarkable ability to rebuild after hardship.",
    "Sagittarius": "At your core you are an explorer. Freedom, truth and wide horizons motivate you, and your optimism carries you through difficult times.",
    "Capricorn": "At your core you are a builder with long-term goals. You take responsibility seriously and earn your success through patience and effort.",
    "Aquarius": "At your core you are independent and forward-looking. You think differently, value friendship and ideals, and resist being told how to live.",
    "Pisces": "At your core you are sensitive, imaginative and compassionate. You feel what others feel and are drawn to art, spirituality or helping people.",
}

MOON = {
    "Aries": "Emotionally you react quickly and honestly. You need independence and action to feel settled, and your moods pass as fast as they arrive.",
    "Taurus": "Emotionally you need security, routine and physical comfort. You are calm and steady, though sudden change can unsettle you.",
    "Gemini": "Emotionally you process feelings by talking and thinking them through. You need mental stimulation and variety to feel at ease.",
    "Cancer": "Emotionally you are deeply sensitive and nurturing. You need a safe home base and close bonds, and you remember how people made you feel.",
    "Leo": "Emotionally you need warmth, loyalty and appreciation. You give love generously and feel best when you are valued.",
    "Virgo": "Emotionally you feel secure when life is orderly and you are being useful. You show care through practical help, and may worry more than you need to.",
    "Libra": "Emotionally you need harmony and companionship. Conflict unsettles you, and you feel most at peace in balanced relationships.",
    "Scorpio": "Emotionally you feel everything intensely, even when you don't show it. You need trust and depth, and you don't give your heart lightly.",
    "Sagittarius": "Emotionally you need freedom, humour and room to explore. You recover from setbacks by looking for the bigger meaning.",
    "Capricorn": "Emotionally you are reserved and self-reliant. You feel secure when you have a plan, and you show love through commitment and reliability.",
    "Aquarius": "Emotionally you need space and independence. You tend to observe your feelings from a little distance, and you value friendship as much as romance.",
    "Pisces": "Emotionally you are receptive and empathetic, absorbing the moods around you. You need quiet time, creativity and kindness to recharge.",
}

RISING = {
    "Aries": "Others see you as direct, energetic and ready for action, and you approach new situations head-on.",
    "Taurus": "Others see you as calm, grounded and dependable, and you move through life at a steady pace with a sense of style.",
    "Gemini": "Others see you as lively, talkative and curious, and you meet the world with questions and quick wit.",
    "Cancer": "Others see you as gentle, caring and approachable, though you protect yourself until you feel safe.",
    "Leo": "Others see you as warm, confident and noticeable, and you tend to make a strong first impression.",
    "Virgo": "Others see you as modest, observant and capable, and you approach life carefully and practically.",
    "Libra": "Others see you as charming, polite and easy to be around, and you naturally look for balance and good relations.",
    "Scorpio": "Others see you as intense, magnetic and a little mysterious, and you reveal yourself slowly.",
    "Sagittarius": "Others see you as friendly, open and adventurous, and you meet life with enthusiasm and humour.",
    "Capricorn": "Others see you as serious, capable and mature, and you carry yourself with quiet authority.",
    "Aquarius": "Others see you as unique, friendly and a little unconventional, and you meet the world on your own terms.",
    "Pisces": "Others see you as gentle, dreamy and sensitive, and you adapt easily to the people around you.",
}

ASPECT_TEXT = {
    "conjunction": "Your {a} and your {b} are fused together and act as one, which gives this combination real force in your personality.",
    "trine": "Your {a} and your {b} support each other easily. This is a natural gift that works best when you use it consciously rather than take it for granted.",
    "sextile": "Your {a} and your {b} cooperate well when you make an effort, opening doors that reward initiative.",
    "square": "Your {a} and your {b} pull against each other. The tension can feel frustrating, but it is also one of the strongest engines of growth in your chart.",
    "opposition": "Your {a} and your {b} sit on opposite sides, so you may swing between them or meet one of them through other people. The task is to find balance rather than pick a side.",
}

ELEMENT_STRONG = {"Fire": "enthusiasm, courage and inspiration", "Earth": "practicality, patience and reliability",
                  "Air": "ideas, communication and objectivity", "Water": "feeling, intuition and empathy"}
ELEMENT_WEAK = {"Fire": "confidence and spontaneity may take conscious effort",
                "Earth": "routines, money and practical follow-through may need deliberate attention",
                "Air": "stepping back to look at situations objectively may take practice",
                "Water": "expressing and trusting your feelings may take practice"}


def _sign(chart, body):
    return chart["planets"][body]["sign"]


def _house_phrase(chart, body):
    h = chart["planets"][body].get("house")
    return f", in the area of {HOUSES[h]}" if h else ""


def _aspect_sentence(asp):
    name = f"{asp['a']} {asp['aspect']} {asp['b']}"
    body = ASPECT_TEXT[asp["aspect"]].format(a=PLANETS[asp["a"]][1], b=PLANETS[asp["b"]][1])
    return f"{name}. {body}"


def _a(sign):
    return f"an {sign}" if sign[0] in "AEIOU" else f"a {sign}"


def _join(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def natal_report(name: str, chart: dict) -> str:
    p = chart["planets"]
    sun, moon = _sign(chart, "Sun"), _sign(chart, "Moon")
    rising = chart["summary"].get("rising")
    known = chart.get("time_known", False)
    first = name.split()[0].title() if name else "you"
    elements = chart["elements"]
    strong = max(elements, key=elements.get)
    weak = min(elements, key=elements.get)
    aspects = [a for a in chart["aspects"] if "North Node" not in (a["a"], a["b"])]
    easy = [a for a in aspects if a["aspect"] in ("trine", "sextile")]
    hard = [a for a in aspects if a["aspect"] in ("square", "opposition")]
    s = []

    # Overview
    ov = (f"{first}, your chart combines {_a(sun)} Sun, {_a(moon)} Moon and {_a(rising)} rising sign." if rising
          else f"{first}, your chart combines {_a(sun)} Sun and {_a(moon)} Moon.")
    ov += (
          f" The strongest element in your chart is {strong}, which gives you a natural gift for "
          f"{ELEMENT_STRONG[strong]}.")
    if elements[weak] <= 1:
        ov += f" {weak} is your least represented element, so {ELEMENT_WEAK[weak]}."
    retro = [b for b in ("Mercury", "Venus", "Mars") if p[b]["retrograde"]]
    if retro:
        ov += (f" {_join(retro)} {'was' if len(retro) == 1 else 'were'} retrograde when you were born, which "
               "tends to turn that energy inward: you reflect before you act, and your way in these areas is "
               "more personal than conventional.")
    if not known:
        ov += (" Because your birth time is unknown, this report doesn't use your rising sign or houses, "
               "which depend on the exact minute of birth.")
    s.append(("Overview", [ov]))

    # Sun, Moon, Rising
    sun_house = p["Sun"].get("house")
    big = [SUN[sun] + (f" This shows up most in the area of {HOUSES[sun_house]}." if sun_house else ""),
           MOON[moon]]
    if rising:
        big.append(RISING[rising])
    s.append(("Sun, Moon and Rising", [" ".join(big)]))

    # Key aspects
    key = aspects[:5]
    if key:
        s.append(("Key aspects", [_aspect_sentence(a) for a in key]))

    # Strengths
    t = SIGNS[sun]["traits"]
    st = (f"Your {sun} Sun makes you {t[0]} and {t[1]}, and your {moon} Moon adds a way of caring that is "
          f"{SIGNS[moon]['traits'][0]}. ")
    st += (f"Jupiter in {_sign(chart, 'Jupiter')} shows where luck and growth come most easily: you expand "
           f"{SIGNS[_sign(chart, 'Jupiter')]['style']}{_house_phrase(chart, 'Jupiter')}.")
    paras = [st]
    if easy:
        a = easy[0]
        paras.append(f"Your most helpful aspect is {a['a']} {a['aspect']} {a['b']}: your "
                     f"{PLANETS[a['a']][1]} and your {PLANETS[a['b']][1]} work together smoothly, "
                     "and this is a talent worth building on.")
    s.append(("Strengths", paras))

    # Challenges and growth
    ch = (f"Every sign has a shadow side, and for a {sun} Sun it is being {t[2]}. Noticing this "
          "is the first step to using it well. ")
    ch += (f"Saturn in {_sign(chart, 'Saturn')} points to your life lessons: maturity comes when you learn to "
           f"act {SIGNS[_sign(chart, 'Saturn')]['style']}{_house_phrase(chart, 'Saturn')}, "
           "even when it feels slow or demanding.")
    paras = [ch]
    if hard:
        a = hard[0]
        paras.append(f"Your most important growth aspect is {a['a']} {a['aspect']} {a['b']}. "
                     + ASPECT_TEXT[a["aspect"]].format(a=PLANETS[a["a"]][1], b=PLANETS[a["b"]][1]))
    s.append(("Challenges and growth", paras))

    # Love and relationships
    v = _sign(chart, "Venus")
    love = (f"With Venus in {v}, you love {SIGNS[v]['style']}{_house_phrase(chart, 'Venus')}. "
            f"You are attracted to people who feel {SIGNS[v]['traits'][0]} and {SIGNS[v]['traits'][1]}. ")
    if known and chart.get("houses"):
        seventh = chart["houses"][6]["sign"]
        love += (f"Your seventh house of partnership begins in {seventh}, so a long-term partner who is "
                 f"{SIGNS[seventh]['traits'][0]} and {SIGNS[seventh]['traits'][1]} tends to balance you well. ")
    love += (f"With your {moon} Moon, you feel emotionally safe with someone who lets you connect "
             f"{SIGNS[moon]['style']}.")
    s.append(("Love and relationships", [love]))

    # Work and purpose
    m = _sign(chart, "Mars")
    work = (f"Mars in {m} shows how you work towards goals: {SIGNS[m]['style']}{_house_phrase(chart, 'Mars')}. ")
    if known and chart.get("angles"):
        mc = chart["angles"]["Midheaven"]["sign"]
        tenth = [b for b, d in p.items() if d.get("house") == 10 and b != "North Node"]
        work += (f"Your Midheaven in {mc} suggests a public path where you can work "
                 f"{SIGNS[mc]['style']}, and roles that value being {SIGNS[mc]['traits'][1]} suit you. ")
        if tenth:
            work += (f"With {_join(tenth)} in your tenth house, career and reputation are a major theme "
                     "in your life, and others notice what you achieve. ")
    node = _sign(chart, "North Node")
    work += (f"Your North Node in {node} points to your long-term purpose: you grow most by learning to live "
             f"{SIGNS[node]['style']}.")
    s.append(("Work and purpose", [work]))

    return "\n\n".join(f"## {title}\n" + "\n\n".join(paras) for title, paras in s)
