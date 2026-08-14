#!/usr/bin/env python3
"""
conlang.py — build a typed-only secret language from a list of roots

One command does the whole pipeline:

    1. ask how you want the language to work
    2. read roots.txt, reject roots that break the rules
    3. top the list back up to the minimum
    4. assign roots to meanings at random
    5. build the language engine (encoder + decoder)
    6. write lookup.html and open it in your browser

Run it offline. No network calls, no dependencies, and the page it writes
has no external requests in it.

    python3 conlang.py                  first run: setup wizard, then build
    python3 conlang.py --reconfigure    change the rules and rebuild
    python3 conlang.py --rebuild        rebuild from saved settings, no prompts
    python3 conlang.py --encode "..."   English -> language
    python3 conlang.py --decode "..."   language -> English
    python3 conlang.py --shell          interactive translation

Files it reads and writes, all beside the script:
    roots.txt        your roots, one per line (offered if missing)
    roots.txt.bak    backup, written once before the first overwrite
    rejected.txt     every rejected root and why
    language.json    settings + full dictionary
    dictionary.md    readable vocabulary tables
    lookup.html      offline searchable dictionary
"""

import argparse
import html
import json
import os
import re
import secrets
import shutil
import string
import sys
import webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
F_ROOTS = os.path.join(HERE, "roots.txt")
F_BACKUP = os.path.join(HERE, "roots.txt.bak")
F_REJECTED = os.path.join(HERE, "rejected.txt")
F_STATE = os.path.join(HERE, "language.json")
F_MARKDOWN = os.path.join(HERE, "dictionary.md")
F_HTML = os.path.join(HERE, "lookup.html")

ALPHABET = string.ascii_lowercase
rng = secrets.SystemRandom()

# ==========================================================================
# Blocklists
# ==========================================================================

WORDS_3 = """
ace act add ado aft age ago aid ail aim air ale all alt amp and ant any ape apt
arc are ark arm art ash ask asp ate awe axe aye bad bag ban bar bat bay bed bee
beg bet bib bid big bin bit boa bob bog bon boo bop bot bow box boy bra bro bud
bug bum bun bus but buy bye cab cad cam can cap car cat caw cob cod cog con coo
cop cot cow coy cry cub cud cue cup cur cut dab dad dam day den dew did die dig
dim din dip doe dog don dot dry dub dud due dug duo dye ear eat ebb eel egg ego
eke elf elk elm emu end eon era err eve ewe eye fad fan far fat fax fay fed fee
fen few fez fib fig fin fir fit fix flu fly foe fog for fox fry fun fur gag gal
gap gas gel gem get gig gin git gnu gob god goo got gum gun gut guy gym had hag
ham has hat haw hay hem hen her hew hex hey hid him hip his hit hob hoe hog hop
hot how hub hue hug hum hut ice icy ill imp ink inn ion ire irk its ivy jab jag
jam jar jaw jay jet jig job jog jot joy jug jut keg ken key kid kin kit lab lad
lag lam lap law lax lay led leg let lid lie lip lit lob log lot low lug lye mad
man map mar mat maw may men met mew mid mix mob mod mom mop mow mud mug mum nab
nag nap nay net new nib nil nip nit nod nor not now nub nun nut oaf oak oar oat
odd ode off oft ohm oil old one opt orb ore our out ova owe owl own pad pal pan
par pat paw pay pea peg pen pep per pet pew pie pig pin pit ply pod poi pop pot
pow pox pry pub pug pun pup pus put rag ram ran rap rat raw ray red ref rep rev
rib rid rig rim rip rob rod roe rot row rub rue rug rum run rut rye sac sad sag
sap sat saw sax say sea see set sew sex she shy sic sin sip sir sis sit six ski
sky sly sob sod son sop sow soy spa spy sty sub sue sum sun sup tab tad tag tan
tap tar tat tax tea tee ten the thy tic tie til tin tip tit toe tog ton too top
tot tow toy try tub tug tun tut two urn use van vat vet vex via vie vow wad wag
wan war was wax way web wed wee wet who why wig win wit woe wok won woo wow wry
yak yam yap yaw yea yen yep yes yet yew yin you zag zap zed zen zig zip zit zoo
ala ama ano ave asi aun bien cal casi con cual dar del dia dio dos ese eso esa
fin fue hay ida ley los las luz mal mar mas mes mia mil mio muy nos ojo oro paz
pie pez pon por pos pro que rey rio sal sea sed ser sin sol son sos sur sus tal
tan tas tez tia tio tos una uno vas ven ver vez vid vil vio voy voz ola oso res
roe rue san ten uso vea ves vos ide ido iba ira era ere eres
aal aas abt ach akt als alt amt auf aus bad bau bei bin bis bot dam das dem den
der des die dir dom ehe ein eis end erd eur fee fes gab gar geb gel gen ger gib
gut hab hai hat hau heu hin hof hut ich ihm ihn ihr ins ist jag jed kam kap kuh
lag lau leb lid lob luv mag meh mir mit mut nah neu nie nix nun nur ohr ort pol
rad rat rau reh rum sag sah sau sei sie sog tag tal tat tau tor tot tun uhr und
uns vor weg weh wem wen wer wie wir zag zeh zog zum zur ost kar kin nen
afk aka api arp asl atm avi aws bbc bff bmw bot brb btc btw cad cam ccc cdc ceo
cfo cgi cia cli cms cnc cnn cod coo cpa cpu crm csi css csv cto ctr dae dao dev
dhl dlc dna dns doc dod dot dpi dps dvd dvi ebt edm edt ekg emt epa esp est etc
eth exe faa faq fbi fda fps ftp fyi gba gdp gfx gif gmo gnu gop gpa gps gpt gpu
gsm gta gtx gui hbo hdd hdr hoa hov hrs hsn htm iam ibm icu ide idk ids ifr img
imo inc ios iot ips irc irs iso isp jdk jpg jre jsp jvm jwt kfc kgb kia kpi lan
lcd led lfg lgb llc llm lmk lol lsd lte ltd mac mba mcu mdf mfa mkv mlb mls mma
mmo mms mod moe mov mp3 mp4 mpg mri msc msg mtb mtv nas nba nbc nda nes net nfc
nfl nft nhl nic nos npc npu nra nsa ntp nvm nyc obs ocd ocr oem ofc omg omw ops
orm otp owo pbs pci pdf pdt pfp phd php pin pll png ppi ppl ppt psa psi psn pvc
pve pvp qos raf ram rar rbi rdp rgb rip rna roi rom rpg rpm rsa rss rtx sat sdk
sec seo sfw sha sim sms smh sns soc sos spf sql src ssd ssh ssl ssn sso suv svg
svn tbh tbs tcp tsa tsv ttl ttv tui uae ufc ufo uhd uml upc ups uri url usa usb
usd utc utf uwu vga vhs vip vpn vps wan wav web wgu wip wtb wtf www xml xss ytd
ass tit cum fap fck fuk sht dik dic nig nga fag hoe jiz sex xxx kkk ana mia
"""

WORDS_4 = """
able acid also area army away baby back ball band bank base bath bear beat been
beer bell belt bend best bike bill bird bite blow blue boat body bomb bone book
boot born boss both bowl bulk burn bush busy cake call calm camp card care case
cash cast cell chat chef chip city club coal coat code cold come cook cool copy
core corn cost crew crop dark data date dawn dead deal dear debt deep deer desk
diet dirt dish disk does dog does done door down draw drew drop drug drum duck
dust duty each earn ease east easy edge else even ever evil exit face fact fade
fail fair fall fame farm fast fate fear feed feel feet fell fell file fill film
find fine fire firm fish five flag flat flew flow food foot ford form four free
from fuel full fund gain game gate gave gear gene gift girl give glad glow goal
goat gold golf gone good gray grew grid grow gulf hair half hall hand hang hard
harm hate have hawk head heal heap hear heat held hell help herb here hero hide
high hill hint hire hold hole holy home hook hope horn host hour huge hunt hurt
icon idea inch into iron item join joke jump july june jury just keen keep kept
kick kill kind king kiss knee knew know lack lady laid lake lamp land lane last
late lava lawn lazy lead leaf lean leap left lend lens less life lift like line
link lion list live load loan lock logo long look lord lose loss lost loud love
luck lung made mail main make male mall many mark mask mass mate meal mean meat
meet melt menu mere mesh mess mice mild mile milk mind mine miss mode mood moon
more most move much must myth nail name navy near neck need news next nice nine
node none noon norm nose note noun okay once only open oral over pace pack page
paid pain pair pale palm park part pass past path peak pear peer pick pile pill
pine pink pipe plan play plot plug plus poem poet pole poll pond pool poor pope
port pose post pour pray prep prey pull pump pure push quit race rack rage raid
rail rain rank rare rate read real rear rely rent rest rice rich ride ring riot
rise risk road rock role roll roof room root rope rose rule rush ruth safe said
sail sake sale salt same sand save scan seal seat seed seek seem seen self sell
send sent sept ship shoe shop shot show shut side sign silk sing sink site size
skin skip slip slot slow snap snow soap sock soft soil sold sole solo some song
soon sort soul soup spot star stay stem step stir stop stub such suit sure swim
tail take tale talk tall tank tape task taxi team tear tech teen tell tend tent
term test text than that them then they thin this thus tide tidy tied tile till
time tiny tips tire told toll tone took tool torn tour town toxi tram trap tree
trim trip true tube tuna tune turn twin type ugly unit upon urge used user vary
vast very vice view vote wade wage wait wake walk wall want ward warm warn wash
wave weak wear week well went were west what when whom wide wife wild will wind
wine wing wipe wire wise wish with wolf wood wool word wore work worm worn wrap
yard yarn yeah year yoga your zero zone zoom
auch aber alle also bald dank dein dort drei eine eins fest ganz gebe gehe gern
gibt groß gute habe hier hoch ihre jede jetzt kann kein komm lang laut lebe mehr
mein nach nein neun nichts noch oder ohne sehr sein seit setz sich sind soll
tage tief toll uber viel voll wann warm wenn wert wieder wird wohl zeit zwei
como cada casa cosa dice dios ella esta este hace hasta hola hora joya lado lugar
mano mesa mira mismo modo mucho nada nadie noche nota otra otro para pero peso
poco puede sabe sala solo tema tener tiempo tipo toda todo trabajo unos vida vive
asap bios ceos ddos eula fifa fpga gbps html http imap isbn json lmao ngmi nsfw
oled pptx rest rfid rtfm sdlc smtp soap tldr tos ttyl uefi utf8 uuid vlan wifi
xbox yolo asic crud jrpg mmog nasa nato ntfs perl repo ruby saas scss sudo tiff
webp xlsx yaml
"""


def build_blocklist(length):
    words = set()
    for chunk in (WORDS_3, WORDS_4):
        for w in chunk.split():
            if len(w) == length and w.isalpha() and w.isascii():
                words.add(w.lower())
    for path in ("/usr/share/dict/words", "/usr/dict/words"):
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8", errors="ignore") as fh:
                    for line in fh:
                        w = line.strip().lower()
                        if len(w) == length and w.isalpha() and w.isascii():
                            words.add(w)
            except OSError:
                pass
            break
    return words


# ==========================================================================
# Vocabulary slots
# ==========================================================================

SLOTS = [
    ("Pronouns", "I / me / my", True),
    ("Pronouns", "you / your (singular)", True),
    ("Pronouns", "he / she / they (sing.) / him / her", True),
    ("Pronouns", "we / us / our", True),
    ("Pronouns", "they / them (plural)", True),
    ("Pronouns", "it / this / that", True),

    ("Particles", "NEGATION (not / don't / won't)", True),
    ("Particles", "QUESTION particle", True),
    ("Particles", "PAST time marker", True),
    ("Particles", "PRESENT / now marker", True),
    ("Particles", "FUTURE time marker", True),
    ("Particles", "PLURAL suffix", True),
    ("Particles", "and / plus / also", True),
    ("Particles", "but / however", False),
    ("Particles", "if / when (conditional)", False),
    ("Particles", "because", False),
    ("Particles", "EMPHASIS (very / really)", False),
    ("Particles", "MAYBE / uncertain", False),

    ("Core Verbs", "go / leave / travel / move / come", True),
    ("Core Verbs", "have / get / take / hold / own", True),
    ("Core Verbs", "say / tell / speak / ask / talk", True),
    ("Core Verbs", "see / look / watch / find / notice", True),
    ("Core Verbs", "know / think / believe / remember", True),
    ("Core Verbs", "want / need / wish", True),
    ("Core Verbs", "make / build / do / create / fix", True),
    ("Core Verbs", "give / send / share / pay", True),
    ("Core Verbs", "can / able / allowed", True),
    ("Core Verbs", "like / enjoy / love", True),

    ("Secondary Verbs", "eat / drink / consume", False),
    ("Secondary Verbs", "sleep / rest", False),
    ("Secondary Verbs", "work / study / practice", False),
    ("Secondary Verbs", "play / game", False),
    ("Secondary Verbs", "buy / sell / trade", False),
    ("Secondary Verbs", "write / type / record", False),
    ("Secondary Verbs", "read / watch (media)", False),
    ("Secondary Verbs", "listen / hear", False),
    ("Secondary Verbs", "start / open / turn on", False),
    ("Secondary Verbs", "stop / close / finish / turn off", False),
    ("Secondary Verbs", "wait / stay / remain", False),
    ("Secondary Verbs", "help / support", False),
    ("Secondary Verbs", "hide / conceal / keep secret", False),
    ("Secondary Verbs", "show / reveal / send to someone", False),
    ("Secondary Verbs", "meet / gather / visit", False),
    ("Secondary Verbs", "break / damage / fail", False),
    ("Secondary Verbs", "win / succeed", False),
    ("Secondary Verbs", "lose / miss / fail to get", False),
    ("Secondary Verbs", "forget", False),
    ("Secondary Verbs", "laugh / joke", False),

    ("People & Social", "person / human / someone", False),
    ("People & Social", "friend / ally / one of us", False),
    ("People & Social", "outsider / stranger / not one of us", False),
    ("People & Social", "family / relative", False),
    ("People & Social", "parent / adult in charge", False),
    ("People & Social", "teacher / boss / authority", False),
    ("People & Social", "group / crew / team", False),
    ("People & Social", "name / handle / username", False),

    ("Places & Things", "home / house / place you live", False),
    ("Places & Things", "school / work / place you must go", False),
    ("Places & Things", "store / shop / market", False),
    ("Places & Things", "outside / street / public place", False),
    ("Places & Things", "room / inside space", False),
    ("Places & Things", "car / bus / vehicle", False),
    ("Places & Things", "food / meal", False),
    ("Places & Things", "water / drink", False),
    ("Places & Things", "money / cost / payment", False),
    ("Places & Things", "thing / object / item", False),
    ("Places & Things", "phone / device", False),
    ("Places & Things", "computer / console / machine", False),
    ("Places & Things", "message / text / post", False),
    ("Places & Things", "game", False),
    ("Places & Things", "book / document / file", False),
    ("Places & Things", "clothes / gear", False),
    ("Places & Things", "door / entrance / exit", False),
    ("Places & Things", "road / path / way", False),

    ("Time", "day", False),
    ("Time", "night", False),
    ("Time", "morning", False),
    ("Time", "today", False),
    ("Time", "tomorrow", False),
    ("Time", "yesterday", False),
    ("Time", "now / right now", False),
    ("Time", "later / soon", False),
    ("Time", "before / earlier", False),
    ("Time", "week", False),
    ("Time", "month", False),
    ("Time", "year", False),
    ("Time", "hour / minute / short time", False),
    ("Time", "long time / a while", False),
    ("Time", "always / every time", False),
    ("Time", "never", False),
    ("Time", "sometimes", False),

    ("Descriptors", "big / tall / wide / a lot", False),
    ("Descriptors", "small / short / narrow / a little", False),
    ("Descriptors", "good / fine / nice / okay", False),
    ("Descriptors", "bad / wrong / broken / gross", False),
    ("Descriptors", "new / fresh / recent", False),
    ("Descriptors", "old / used / previous", False),
    ("Descriptors", "fast / quick / early", False),
    ("Descriptors", "slow / late", False),
    ("Descriptors", "easy / simple", False),
    ("Descriptors", "hard / difficult / complicated", False),
    ("Descriptors", "safe / secure / private", False),
    ("Descriptors", "dangerous / risky / exposed", False),
    ("Descriptors", "true / real / correct", False),
    ("Descriptors", "false / fake / lying", False),
    ("Descriptors", "happy / glad / excited", False),
    ("Descriptors", "angry / annoyed / upset", False),
    ("Descriptors", "sad / tired / low", False),
    ("Descriptors", "funny / weird / strange", False),
    ("Descriptors", "important / serious", False),
    ("Descriptors", "boring / pointless", False),
    ("Descriptors", "hot / warm", False),
    ("Descriptors", "cold / cool", False),

    ("Prepositions", "in / on / at / inside", False),
    ("Prepositions", "to / toward / into", False),
    ("Prepositions", "from / out of / since", False),
    ("Prepositions", "with / using / by means of", False),
    ("Prepositions", "for / because of / on behalf of", False),
    ("Prepositions", "under / below", False),
    ("Prepositions", "over / above", False),
    ("Prepositions", "near / next to", False),
    ("Prepositions", "far / away from", False),
    ("Prepositions", "between / among", False),

    ("Numbers", "zero / none", False),
    ("Numbers", "one", False),
    ("Numbers", "two", False),
    ("Numbers", "three", False),
    ("Numbers", "four", False),
    ("Numbers", "five", False),
    ("Numbers", "six", False),
    ("Numbers", "seven", False),
    ("Numbers", "eight", False),
    ("Numbers", "nine", False),
    ("Numbers", "ten", False),
    ("Numbers", "hundred", False),
    ("Numbers", "thousand", False),
    ("Numbers", "many / lots", False),
    ("Numbers", "few / some", False),
    ("Numbers", "all / every", False),
    ("Numbers", "half / part", False),

    ("Question Words", "who", False),
    ("Question Words", "what", False),
    ("Question Words", "where", False),
    ("Question Words", "when", False),
    ("Question Words", "why", False),
    ("Question Words", "how", False),
    ("Question Words", "how many / how much", False),
    ("Question Words", "which", False),
]

# Meaning labels that carry grammar. Must match SLOTS exactly.
M_NEG = "NEGATION (not / don't / won't)"
M_QUESTION = "QUESTION particle"
M_PAST = "PAST time marker"
M_PRESENT = "PRESENT / now marker"
M_FUTURE = "FUTURE time marker"
M_PLURAL = "PLURAL suffix"

VERB_CATEGORIES = {"Core Verbs", "Secondary Verbs"}
PLURALIZABLE = {"People & Social", "Places & Things", "Time"}

MARKER_SETS = {
    "accented": {"name": "\u00c4", "foreign": "\u00d6",
                 "number": "\u00dc", "quote": "\u00d1"},
    "ascii": {"name": "Qq", "foreign": "Xx", "number": "Zz", "quote": "Vv"},
    "none": {},
}

# ==========================================================================
# English handling
# ==========================================================================

ARTICLES = {"the", "a", "an"}
COPULA = {"is", "are", "am", "was", "were", "be", "been", "being",
          "s", "re", "m"}
AUXILIARIES = {"do", "does", "did", "will", "shall", "would",
               "have", "has", "had"}
OF_WORD = {"of"}

NEGATORS = {"not", "n't", "nt", "dont", "doesnt", "didnt", "wont", "cant",
            "cannot", "isnt", "arent", "wasnt", "werent", "shouldnt",
            "couldnt", "wouldnt", "havent", "hasnt", "hadnt", "no"}
PAST_CUES = {"was", "were", "did", "had", "yesterday", "ago", "went", "saw",
             "said", "took", "got", "made", "gave", "knew", "thought",
             "came", "wanted", "used"}
FUTURE_CUES = {"will", "shall", "gonna", "tomorrow", "later", "soon"}
WH_WORDS = {"who", "what", "where", "when", "why", "how", "which", "whose"}
COUNT_HEADS = ("one", "two", "three", "four", "five", "six", "seven", "eight",
               "nine", "ten", "hundred", "thousand", "many", "few", "all",
               "half")

IRREGULAR = {
    "went": "go", "gone": "go", "goes": "go", "going": "go",
    "came": "come", "comes": "come", "coming": "come",
    "saw": "see", "seen": "see", "sees": "see", "seeing": "see",
    "said": "say", "says": "say", "saying": "say",
    "took": "take", "taken": "take", "takes": "take", "taking": "take",
    "got": "get", "gotten": "get", "gets": "get", "getting": "get",
    "made": "make", "makes": "make", "making": "make",
    "gave": "give", "given": "give", "gives": "give", "giving": "give",
    "knew": "know", "known": "know", "knows": "know", "knowing": "know",
    "thought": "think", "thinks": "think", "thinking": "think",
    "had": "have", "has": "have", "having": "have",
    "ate": "eat", "eaten": "eat", "eats": "eat", "eating": "eat",
    "slept": "sleep", "sleeps": "sleep", "sleeping": "sleep",
    "bought": "buy", "buys": "buy", "buying": "buy",
    "sold": "sell", "sells": "sell", "selling": "sell",
    "wrote": "write", "written": "write", "writes": "write",
    "heard": "hear", "hears": "hear", "hearing": "hear",
    "began": "start", "begun": "start", "started": "start",
    "stopped": "stop", "stops": "stop", "stopping": "stop",
    "waited": "wait", "waits": "wait", "waiting": "wait",
    "helped": "help", "helps": "help", "helping": "help",
    "hid": "hide", "hidden": "hide", "hides": "hide", "hiding": "hide",
    "showed": "show", "shown": "show", "shows": "show", "showing": "show",
    "met": "meet", "meets": "meet", "meeting": "meet",
    "broke": "break", "broken": "break", "breaks": "break",
    "won": "win", "wins": "win", "winning": "win",
    "lost": "lose", "loses": "lose", "losing": "lose",
    "forgot": "forget", "forgotten": "forget", "forgets": "forget",
    "laughed": "laugh", "laughs": "laugh", "laughing": "laugh",
    "wanted": "want", "wants": "want", "wanting": "want",
    "needed": "need", "needs": "need", "needing": "need",
    "liked": "like", "likes": "like", "liking": "like",
    "loved": "love", "loves": "love", "loving": "love",
    "sent": "send", "sends": "send", "sending": "send",
    "paid": "pay", "pays": "pay", "paying": "pay",
    "held": "hold", "holds": "hold", "holding": "hold",
    "found": "find", "finds": "find", "finding": "find",
    "told": "tell", "tells": "tell", "telling": "tell",
    "asked": "ask", "asks": "ask", "asking": "ask",
    "children": "child", "people": "person", "men": "man", "women": "woman",
    "me": "i", "my": "i", "mine": "i", "us": "we", "our": "we",
    "your": "you", "yours": "you", "him": "he", "her": "he", "his": "he",
    "them": "they", "their": "they", "hers": "he", "its": "it",
    "could": "can", "able": "can",
}

WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d[\d,]*|[.!?]")


# ==========================================================================
# Prompt helpers
# ==========================================================================

BANNER = r"""
 a88888b.                   dP                            
d8'   `88                   88                            
88        .d8888b. 88d888b. 88 .d8888b. 88d888b. .d8888b. 
88        88'  `88 88'  `88 88 88'  `88 88'  `88 88'  `88 
Y8.   .88 88.  .88 88    88 88 88.  .88 88    88 88.  .88 
 Y88888P' `88888P' dP    dP dP `88888P8 dP    dP `8888P88 
oooooooooooooooooooooooooooooooooooooooooooooooooo~~~~.88~
                                                  d8888P  
"""


def print_banner(subtitle=None):
    """Show the wordmark. Falls back to plain text on narrow terminals."""
    width = shutil.get_terminal_size((80, 24)).columns or 80
    print()
    if width < 60:
        print("  C O N L A N G")
    else:
        print(BANNER)
    if subtitle:
        print(f"  {subtitle}")
    print()


def interactive():
    return sys.stdin.isatty() and sys.stdout.isatty()


def rule(char="─", width=64):
    print(char * width)


def choose(question, options, default=0, note=None):
    """Numbered single-select. options is a list of (label, value, blurb)."""
    print()
    print(f"  {question}")
    if note:
        print(f"  {note}")
    print()
    for i, (label, _, blurb) in enumerate(options, 1):
        tag = " (default)" if i - 1 == default else ""
        print(f"    {i}. {label}{tag}")
        if blurb:
            print(f"       {blurb}")
    print()

    if not interactive():
        return options[default][1]

    while True:
        raw = input(f"  choose 1-{len(options)} [{default + 1}]: ").strip()
        if not raw:
            return options[default][1]
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1][1]
        print("  not one of the options.")


def choose_many(question, options, default_on, note=None):
    """Numbered multi-select. Returns a set of values."""
    print()
    print(f"  {question}")
    if note:
        print(f"  {note}")
    print()
    for i, (label, value, blurb) in enumerate(options, 1):
        mark = "x" if value in default_on else " "
        print(f"    {i}. [{mark}] {label}")
        if blurb:
            print(f"          {blurb}")
    print()
    print("  enter numbers to toggle, separated by spaces. blank to accept.")

    chosen = set(default_on)
    if not interactive():
        return chosen

    while True:
        raw = input("  toggle: ").strip()
        if not raw:
            return chosen
        ok = True
        for part in raw.split():
            if part.isdigit() and 1 <= int(part) <= len(options):
                value = options[int(part) - 1][1]
                chosen.symmetric_difference_update({value})
            else:
                ok = False
        if not ok:
            print("  ignored something that wasn't an option number.")
        current = [lbl for lbl, val, _ in options if val in chosen]
        print(f"  on: {', '.join(current) if current else '(none)'}")


def ask_text(question, default):
    print()
    if not interactive():
        return default
    raw = input(f"  {question} [{default}]: ").strip()
    return raw or default


def ask_int(question, default, low, high):
    print()
    if not interactive():
        return default
    while True:
        raw = input(f"  {question} [{default}]: ").strip()
        if not raw:
            return default
        if raw.isdigit() and low <= int(raw) <= high:
            return int(raw)
        print(f"  needs to be a number from {low} to {high}.")


def confirm(question, default=True):
    if not interactive():
        return default
    suffix = "Y/n" if default else "y/N"
    raw = input(f"  {question} [{suffix}]: ").strip().lower()
    if not raw:
        return default
    return raw.startswith("y")


# ==========================================================================
# The wizard
# ==========================================================================

DEFAULT_CONFIG = {
    "title": "Dictionary",
    "root_length": 3,
    "min_roots": 250,
    "strict_similarity": True,
    "rotation": 3,
    "boundary": "capitals",
    "markers": "accented",
    "delete": ["articles", "copula", "of", "infinitive"],
}


def run_wizard(existing=None):
    config = dict(DEFAULT_CONFIG)
    if existing:
        config.update(existing)

    print()
    rule("═")
    print("  LANGUAGE SETUP")
    rule("═")
    print("  Every answer changes how the language works. Press enter to")
    print("  take the default, which is what the spec recommends.")

    config["title"] = ask_text("What is the language called?", config["title"])

    config["root_length"] = choose(
        "How long is a root word?",
        [("3 letters", 3, "17,576 possible roots. Fastest to type."),
         ("4 letters", 4, "456,976 possible. Far fewer collisions, more typing.")],
        default=0 if config["root_length"] == 3 else 1,
    )

    config["strict_similarity"] = choose(
        "Reject roots that differ from another by only one letter?",
        [("Yes, reject them", True,
          "A typo can't turn one word into another. Costs you a lot of roots."),
         ("No, allow them", False,
          "Keeps almost everything you generated. Typos become silent errors.")],
        default=0 if config["strict_similarity"] else 1,
        note="At 3 letters this rule is brutal — expect to lose a third or more.",
    )

    config["rotation"] = choose(
        "How many interchangeable forms should common words have?",
        [("Three (A/B/C)", 3, "Strongest against frequency analysis."),
         ("Two (A/B)", 2, "Middle ground. Less to memorise."),
         ("One", 1, "Easiest to learn. Frequency analysis works on you.")],
        default={3: 0, 2: 1, 1: 2}.get(config["rotation"], 0),
        note="This is the main thing standing between you and a cracked language.",
    )

    config["boundary"] = choose(
        "How are words separated?",
        [("No spaces, capital starts each word", "capitals",
          "DorKastilMur. Hides word lengths. Recommended."),
         ("Normal spaces", "spaces",
          "dor kastil mur. Easier to read, leaks word lengths.")],
        default=0 if config["boundary"] == "capitals" else 1,
    )

    config["markers"] = choose(
        "How should names, numbers and foreign words be marked?",
        [("Accented letters (Ä Ö Ü Ñ)", "accented",
          "Visually distinct. Needs a long-press on phone keyboards."),
         ("Plain letter pairs (Qq Xx Zz Vv)", "ascii",
          "Types instantly anywhere. Less distinct on the page."),
         ("No markers", "none",
          "Names and numbers go in as-is. This is a real leak.")],
        default={"accented": 0, "ascii": 1, "none": 2}.get(config["markers"], 0),
    )

    config["delete"] = sorted(choose_many(
        "Which English features should the grammar delete?",
        [("Articles (the, a, an)", "articles", "The single biggest giveaway."),
         ("Copula (is, are, am, was)", "copula", "\"He tall\" instead of \"he is tall\"."),
         ("The word \"of\"", "of", "Possessor comes first instead."),
         ("Infinitive \"to\"", "infinitive", "\"I want go\" instead of \"I want to go\".")],
        default_on=set(config["delete"]),
        note="Each one you keep is a common word an attacker can anchor on.",
    ))

    needed = slots_needed(config["rotation"])
    floor = max(needed, 50)
    suggested = max(config["min_roots"], needed)
    config["min_roots"] = ask_int(
        f"Minimum root count? ({needed} slots to fill, spares are useful)",
        suggested, floor, 5000)

    print()
    rule()
    print("  SETTINGS")
    rule()
    print(f"    name              {config['title']}")
    print(f"    root length       {config['root_length']} letters")
    print(f"    similarity rule   {'strict' if config['strict_similarity'] else 'off'}")
    print(f"    rotation          {config['rotation']}-way")
    print(f"    word boundaries   {config['boundary']}")
    print(f"    markers           {config['markers']}")
    print(f"    deleting          {', '.join(config['delete']) or 'nothing'}")
    print(f"    minimum roots     {config['min_roots']}")
    rule()

    if interactive() and not confirm("Build with these?", True):
        return run_wizard(config)

    return config


def slots_needed(rotation):
    return sum(rotation if rotated else 1 for _, _, rotated in SLOTS)


# ==========================================================================
# Step 1-2: check roots, top up
# ==========================================================================

def hamming(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


def neighbours(root):
    out = []
    for i, current in enumerate(root):
        for letter in ALPHABET:
            if letter != current:
                out.append(root[:i] + letter + root[i + 1:])
    return out


def check_roots(raw_lines, config, blocklist):
    length = config["root_length"]
    strict = config["strict_similarity"]

    accepted, rejected = [], []
    accepted_set, blocked = set(), set()

    for raw in raw_lines:
        root = raw.strip().lower()
        if not root:
            continue
        if len(root) != length:
            rejected.append((raw.strip(), f"wrong length (need {length})"))
        elif not (root.isalpha() and root.isascii()):
            rejected.append((raw.strip(), "contains a non a-z character"))
        elif root in accepted_set:
            rejected.append((root, "duplicate"))
        elif root in blocklist:
            rejected.append((root, "real word or common abbreviation"))
        elif strict and root in blocked:
            clash = next((a for a in accepted if hamming(a, root) == 1), "?")
            rejected.append((root, f"too similar to '{clash}' (one letter apart)"))
        else:
            accepted.append(root)
            accepted_set.add(root)
            blocked.add(root)
            if strict:
                blocked.update(neighbours(root))
            continue

    return accepted, rejected, blocked


def top_up(accepted, blocked, config, blocklist, target):
    """Walk a shuffled copy of the whole root space. Exhaustive, so it
    either reaches the target or proves the target is impossible."""
    length = config["root_length"]
    strict = config["strict_similarity"]
    accepted, blocked = list(accepted), set(blocked)
    added = []

    if len(accepted) >= target:
        return accepted, added

    if length == 3:
        space = [a + b + c for a in ALPHABET for b in ALPHABET for c in ALPHABET]
    else:
        space = [a + b + c + d for a in ALPHABET for b in ALPHABET
                 for c in ALPHABET for d in ALPHABET]
    rng.shuffle(space)

    for candidate in space:
        if len(accepted) >= target:
            break
        if candidate in blocklist or candidate in blocked:
            continue
        accepted.append(candidate)
        added.append(candidate)
        blocked.add(candidate)
        if strict:
            blocked.update(neighbours(candidate))

    return accepted, added


def generate_fresh(count, config, blocklist):
    accepted, _ = top_up([], set(), config, blocklist, count)
    return accepted


# ==========================================================================
# Step 3: assignment
# ==========================================================================

def take_group(pool, size, length):
    """Pull `size` roots that differ from each other in every position."""
    if size == 1:
        return [pool.pop()] if pool else None

    for i in range(len(pool)):
        group = [pool[i]]
        indexes = [i]
        for j in range(len(pool)):
            if j in indexes:
                continue
            if all(hamming(pool[j], g) == length for g in group):
                group.append(pool[j])
                indexes.append(j)
                if len(group) == size:
                    for index in sorted(indexes, reverse=True):
                        pool.pop(index)
                    return group
    return None


def assign(roots, config):
    pool = list(roots)
    rng.shuffle(pool)
    rotation = config["rotation"]
    length = config["root_length"]
    labels = ["A", "B", "C", "D"][:rotation]

    assignments = {}
    order = []
    for category, meaning, rotated in SLOTS:
        if category not in assignments:
            assignments[category] = []
            order.append(category)

        size = rotation if rotated else 1
        group = take_group(pool, size, length)
        if group is None:
            raise RuntimeError(f"ran out of usable roots at '{meaning}'")

        if rotated and rotation > 1:
            assignments[category].append({
                "meaning": meaning, "rotated": True,
                "roots": dict(zip(labels, group)),
            })
        else:
            assignments[category].append({
                "meaning": meaning, "rotated": False, "roots": group[0],
            })

    return {k: assignments[k] for k in order}, pool


# ==========================================================================
# Step 4: the language
# ==========================================================================

class Language:
    def __init__(self, state):
        self.config = state["config"]
        self.vocabulary = state["vocabulary"]
        self.spare = state.get("spare", [])
        self.length = self.config["root_length"]
        self.markers = MARKER_SETS[self.config["markers"]]
        self.delete = set(self.config["delete"])

        self.entries, self.categories = [], []
        self.by_meaning, self.by_root, self.by_word = {}, {}, {}
        self._build_indexes()

    # -- indexes ----------------------------------------------------------

    def _build_indexes(self):
        for category, entries in self.vocabulary.items():
            self.categories.append(category)
            for entry in entries:
                rotated = entry["rotated"]
                record = {
                    "category": category,
                    "meaning": entry["meaning"],
                    "rotated": rotated,
                    "roots": list(entry["roots"].values()) if rotated
                    else [entry["roots"]],
                    "slots": list(entry["roots"].keys()) if rotated else ["—"],
                }
                self.entries.append(record)
                self.by_meaning[record["meaning"]] = record
                for slot, root in zip(record["slots"], record["roots"]):
                    self.by_root[root] = (record["meaning"], slot)

        for record in self.entries:
            for word in self._surface_forms(record["meaning"]):
                self.by_word.setdefault(word, record["meaning"])

        for form, base in IRREGULAR.items():
            if base in self.by_word:
                self.by_word.setdefault(form, self.by_word[base])

        for word in list(self.by_word):
            meaning = self.by_word[word]
            for inflected in (word + "s", word + "es", word + "ed",
                              word + "d", word + "ing"):
                self.by_word.setdefault(inflected, meaning)
            if word.endswith("e"):
                self.by_word.setdefault(word[:-1] + "ing", meaning)

    @staticmethod
    def _surface_forms(meaning):
        text = meaning.replace("(", " / ").replace(")", " / ")
        skip = {"sing.", "singular", "plural", "media", "conditional",
                "negation", "question particle", "plural suffix",
                "past time marker", "present", "future time marker",
                "emphasis", "maybe"}
        forms = set()
        for chunk in text.split("/"):
            chunk = chunk.strip().lower()
            if not chunk or chunk in skip:
                continue
            forms.add(chunk)
            if " " in chunk:
                forms.add(chunk.split()[0])
        return {f for f in forms if f.replace(" ", "").isalpha()}

    # -- helpers ----------------------------------------------------------

    def pick(self, meaning, avoid=()):
        record = self.by_meaning.get(meaning)
        if record is None:
            return None
        options = [r for r in record["roots"] if r not in avoid] \
            or record["roots"]
        return rng.choice(options)

    def lookup_word(self, word):
        word = word.lower().strip("'")
        if word in self.by_word:
            return self.by_word[word]
        if word in IRREGULAR and IRREGULAR[word] in self.by_word:
            return self.by_word[IRREGULAR[word]]
        for suffix in ("ing", "ed", "es", "s", "d"):
            if word.endswith(suffix):
                stem = word[: -len(suffix)]
                if stem in self.by_word:
                    return self.by_word[stem]
                if stem + "e" in self.by_word:
                    return self.by_word[stem + "e"]
        return None

    def is_plural(self, word):
        low = word.lower()
        if low in IRREGULAR and IRREGULAR[low] != low:
            return IRREGULAR[low] in self.by_word and low.endswith(("s", "n"))
        return (low.endswith("s") and not low.endswith("ss")
                and self.lookup_word(low[:-1]) is not None)

    def _verb_at(self, words, index):
        if index >= len(words):
            return False
        meaning = self.lookup_word(words[index])
        return (meaning is not None
                and self.by_meaning[meaning]["category"] in VERB_CATEGORIES)

    def mark(self, kind, body):
        prefix = self.markers.get(kind)
        return (prefix + body) if prefix else body

    # -- encode -----------------------------------------------------------

    def encode(self, text):
        notes = []
        out = []
        running_tense = None

        for sentence in re.split(r"(?<=[.!?])\s+", text.strip()):
            if not sentence.strip():
                continue
            words = [w for w in WORD_RE.findall(sentence) if w not in ".!?"]
            if not words:
                continue

            question = (sentence.strip().endswith("?")
                        or words[0].lower() in WH_WORDS)
            counted = any(
                w[0].isdigit()
                or (self.lookup_word(w) or "").startswith(COUNT_HEADS)
                for w in words
            )
            tense = self._detect_tense(words)

            used, tokens = set(), []

            if tense != running_tense:
                root = self.pick({"past": M_PAST, "future": M_FUTURE,
                                  "present": M_PRESENT}[tense])
                if root:
                    tokens.append(root)
                    used.add(root)
                running_tense = tense

            if question:
                root = self.pick(M_QUESTION, avoid=used)
                if root:
                    tokens.append(root)
                    used.add(root)

            skip_to = False
            for index, word in enumerate(words):
                low = word.lower().replace("'", "")

                if low in ARTICLES and "articles" in self.delete:
                    continue
                if low in COPULA and "copula" in self.delete:
                    continue
                if low in OF_WORD and "of" in self.delete:
                    continue
                if low in AUXILIARIES and low not in {"have", "has", "had"}:
                    continue
                if low in {"do", "does", "did"} and index == 0:
                    continue

                if low == "going" and index + 1 < len(words) \
                        and words[index + 1].lower() == "to" \
                        and self._verb_at(words, index + 2):
                    skip_to = True
                    continue
                if low == "to":
                    if skip_to:
                        skip_to = False
                        continue
                    if "infinitive" in self.delete and self._verb_at(words, index + 1):
                        continue
                if low in {"gonna", "wanna"}:
                    low = "want"

                if low in NEGATORS and low != "never":
                    root = self.pick(M_NEG, avoid=used)
                    if root:
                        tokens.append(root)
                        used.add(root)
                    continue

                if word[0].isdigit():
                    tokens.append(self.mark("number", word.replace(",", "")[::-1]))
                    continue

                meaning = self.lookup_word(low)
                if meaning is None:
                    if index > 0 and word[0].isupper():
                        tokens.append(self.mark("name", word.lower()[::-1]))
                        notes.append(f"name: {word}")
                    else:
                        tokens.append(self.mark("foreign", word.lower()[::-1]))
                        notes.append(f"no root for '{word}' — assign one from "
                                     f"your spares")
                    continue

                root = self.pick(meaning, avoid=used)
                used.add(root)

                if not counted \
                        and self.by_meaning[meaning]["category"] in PLURALIZABLE \
                        and self.is_plural(word):
                    plural = self.pick(M_PLURAL, avoid=used)
                    if plural:
                        root += plural
                        used.add(plural)

                tokens.append(root)

            out.append(self._join(tokens))

        return " ".join(out), notes

    def _join(self, tokens):
        if self.config["boundary"] == "spaces":
            return " ".join(tokens) + "."
        return "".join(self._cap(t) for t in tokens) + "."

    def _cap(self, token):
        for prefix in self.markers.values():
            if token.startswith(prefix):
                return token
        return token[:1].upper() + token[1:]

    def _detect_tense(self, words):
        lows = {w.lower().replace("'", "") for w in words}
        if lows & FUTURE_CUES:
            return "future"
        if lows & PAST_CUES:
            return "past"
        for word in words:
            low = word.lower()
            if low.endswith("ed") and self.lookup_word(low[:-2]):
                return "past"
        return "present"

    # -- decode -----------------------------------------------------------

    def decode(self, text):
        notes, glosses = [], []
        plural_roots = set(self.by_meaning[M_PLURAL]["roots"]) \
            if M_PLURAL in self.by_meaning else set()

        for sentence in text.split("."):
            if not sentence.strip():
                continue
            words = [self._decode_token(t, plural_roots, notes)
                     for t in self._split_words(sentence)]
            glosses.append(" ".join(w for w in words if w))

        return (". ".join(glosses) + "." if glosses else ""), notes

    def _split_words(self, sentence):
        if self.config["boundary"] == "spaces":
            return [t for t in sentence.split() if t]

        prefixes = sorted(self.markers.values(), key=len, reverse=True)
        tokens, current, i = [], "", 0
        while i < len(sentence):
            matched = next((p for p in prefixes if sentence.startswith(p, i)), None)
            char = sentence[i]
            if matched:
                if current:
                    tokens.append(current)
                current = matched
                i += len(matched)
                continue
            if char.isspace():
                if current:
                    tokens.append(current)
                current = ""
            elif char.isupper():
                if current:
                    tokens.append(current)
                current = char
            else:
                current += char
            i += 1
        if current:
            tokens.append(current)
        return tokens

    def _decode_token(self, token, plural_roots, notes):
        if not token:
            return ""

        for kind, prefix in self.markers.items():
            if token.startswith(prefix):
                body = token[len(prefix):]
                if kind == "name":
                    return f"[name: {body[::-1].title()}]"
                if kind == "foreign":
                    return f"[{body[::-1]}]"
                if kind == "number":
                    return body[::-1]
                if kind == "quote":
                    return '"'

        body = token.lower()
        n = self.length

        if body in self.by_root:
            return self._headword(self.by_root[body][0])

        if len(body) == 2 * n:
            head, tail = body[:n], body[n:]
            if tail in plural_roots and head in self.by_root:
                return self._headword(self.by_root[head][0]) + "s"
            if head in self.by_root and tail in self.by_root:
                return (self._headword(self.by_root[head][0]) + "-"
                        + self._headword(self.by_root[tail][0]))

        notes.append(f"unknown root: {body}")
        return f"?{body}?"

    def _headword(self, meaning):
        fixed = {M_NEG: "not", M_QUESTION: "[?]", M_PAST: "[past]",
                 M_FUTURE: "[future]", M_PRESENT: "[now]",
                 M_PLURAL: "[plural]"}
        if meaning in fixed:
            return fixed[meaning]
        head = re.sub(r"\s*\(.*?\)", "", meaning.split("/")[0].strip())
        return head or meaning


# ==========================================================================
# Step 5: outputs
# ==========================================================================

def write_markdown(language, path):
    config = language.config
    lines = [
        f"# {config['title']} — Vocabulary", "",
        "Roots were assigned at random. **This file is the key: anyone who "
        "reads it can read everything written in the language.**", "",
        "| Setting | Value |", "|---|---|",
        f"| Root length | {config['root_length']} letters |",
        f"| Rotation | {config['rotation']}-way |",
        f"| Word boundaries | {config['boundary']} |",
        f"| Markers | {config['markers']} |",
        f"| Deleted from grammar | {', '.join(config['delete']) or 'nothing'} |",
        "",
    ]

    for category in language.categories:
        lines += [f"## {category}", "", "| Meaning | Slot | Root |", "|---|---|---|"]
        for record in language.entries:
            if record["category"] != category:
                continue
            for slot, root in zip(record["slots"], record["roots"]):
                lines.append(f"| {record['meaning']} | {slot} | `{root}` |")
        lines.append("")

    lines += ["## Named People", "",
              "Assign by hand. Consider storing this table separately.", "",
              "| Person | Root |", "|---|---|"]
    for root in language.spare[:10]:
        lines.append(f"| | `{root}` |")
    lines.append("")

    if len(language.spare) > 10:
        lines += ["## Unassigned Roots", "",
                  "Spares for vocabulary you add later.", "", "```"]
        rest = language.spare[10:]
        for i in range(0, len(rest), 12):
            lines.append(" ".join(rest[i:i + 12]))
        lines += ["```", ""]

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def build_html(language):
    config = language.config
    title = config["title"]

    payload = [{
        "c": r["category"], "m": r["meaning"], "r": r["roots"], "s": r["slots"],
        "w": sorted(w for w, m in language.by_word.items() if m == r["meaning"]),
    } for r in language.entries]

    data = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
    cats = json.dumps(language.categories, ensure_ascii=False)

    grammar = [
        ("boundaries",
         "A capital letter starts each word, no spaces."
         if config["boundary"] == "capitals" else "Words separated by spaces."),
        ("rotation",
         f"Pick freely between the {config['rotation']} forms. "
         f"Never repeat one in a sentence."
         if config["rotation"] > 1 else "No rotation. One root per meaning."),
        ("tense", "Time marker at the start. Holds until changed."),
        ("questions", "Question particle first. Never invert word order."),
        ("negation", "Particle immediately before the verb."),
        ("plural", "Suffix on the root. Skip it if a number is present."),
    ]
    for key, label in (("articles", "Deleted. No the, a, an."),
                       ("copula", "Deleted. \"He tall\" not \"he is tall\"."),
                       ("of", "Deleted. Possessor comes first."),
                       ("infinitive", "Deleted. \"I want go\" not \"I want to go\".")):
        if key in config["delete"]:
            grammar.append((key, label))
    for kind, label in (("name", "Name follows, spelled backwards."),
                        ("foreign", "Foreign word follows, backwards."),
                        ("number", "Number follows, digits backwards."),
                        ("quote", "Opens and closes quoted speech.")):
        prefix = language.markers.get(kind)
        if prefix:
            grammar.append((prefix, label))

    rows = "\n".join(
        f"      <tr><td>{html.escape(k)}</td><td>{html.escape(v)}</td></tr>"
        for k, v in grammar)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{html.escape(title)}</title>
<style>
:root {{
  --paper:#e4e7e1; --raised:#f4f6f1; --ink:#17211f; --soft:#5f6d69;
  --rule:#c8cfc6; --root:#0d5f54; --mark:#5b3fbf; --focus:#0d5f54;
  --mono: ui-monospace,"SF Mono","Cascadia Mono","Roboto Mono",Menlo,Consolas,monospace;
  --sans: system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",sans-serif;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --paper:#141a19; --raised:#1d2523; --ink:#e2e7e2; --soft:#8b9994;
    --rule:#2e3835; --root:#5fc9b6; --mark:#a58bff; --focus:#5fc9b6;
  }}
}}
* {{ box-sizing:border-box; }}
html {{ -webkit-text-size-adjust:100%; }}
body {{ margin:0; padding:0 0 4rem; background:var(--paper); color:var(--ink);
  font-family:var(--sans); font-size:16px; line-height:1.45; }}
header {{ position:sticky; top:0; z-index:10; background:var(--paper);
  border-bottom:1px solid var(--rule); padding:1rem 1rem .75rem; }}
.wrap {{ max-width:52rem; margin:0 auto; }}
h1 {{ font-family:var(--mono); font-size:.8rem; font-weight:600;
  letter-spacing:.18em; text-transform:uppercase; color:var(--soft); margin:0 0 .6rem; }}
#q {{ width:100%; padding:.7rem .85rem; font-size:1.05rem; font-family:var(--mono);
  color:var(--ink); background:var(--raised); border:1px solid var(--rule);
  border-radius:.35rem; outline:none; }}
#q:focus {{ border-color:var(--focus);
  box-shadow:0 0 0 3px color-mix(in srgb,var(--focus) 22%,transparent); }}
#q::placeholder {{ color:var(--soft); }}
.chips {{ display:flex; flex-wrap:wrap; gap:.35rem; margin-top:.6rem; }}
.chip {{ font:inherit; font-size:.75rem; padding:.25rem .6rem; cursor:pointer;
  background:none; color:var(--soft); border:1px solid var(--rule); border-radius:1rem; }}
.chip[aria-pressed="true"] {{ background:var(--ink); color:var(--paper); border-color:var(--ink); }}
.chip:focus-visible,.triplet:focus-visible {{ outline:2px solid var(--focus); outline-offset:2px; }}
#count {{ font-size:.75rem; color:var(--soft); margin:.55rem 0 0; font-family:var(--mono); }}
main {{ padding:1rem; }}
.entry {{ display:flex; gap:1rem; align-items:flex-start; justify-content:space-between;
  padding:.7rem 0; border-bottom:1px solid var(--rule); }}
.meaning {{ font-size:.95rem; }}
.cat {{ display:block; font-family:var(--mono); font-size:.65rem; letter-spacing:.12em;
  text-transform:uppercase; color:var(--soft); margin-bottom:.15rem; }}
.roots {{ display:flex; flex-direction:column; gap:.3rem; flex-shrink:0; }}
.rootrow {{ display:flex; align-items:center; gap:.4rem; }}
.slot {{ font-family:var(--mono); font-size:.65rem; color:var(--mark); width:.8rem; }}
.triplet {{ display:flex; gap:2px; background:none; border:0; padding:0; cursor:pointer; }}
.triplet span {{ font-family:var(--mono); font-size:1rem; font-weight:600; color:var(--root);
  background:var(--raised); border:1px solid var(--rule); width:1.5rem; height:1.75rem;
  display:grid; place-items:center; border-radius:.2rem; }}
.triplet:hover span {{ border-color:var(--root); }}
.triplet.copied span {{ background:var(--root); color:var(--raised); border-color:var(--root); }}
.empty {{ color:var(--soft); padding:2rem 0; text-align:center; }}
details {{ margin-top:2rem; border-top:1px solid var(--rule); padding-top:1rem; }}
summary {{ cursor:pointer; font-family:var(--mono); font-size:.75rem;
  letter-spacing:.12em; text-transform:uppercase; color:var(--soft); }}
details table {{ width:100%; border-collapse:collapse; margin-top:.8rem; font-size:.85rem; }}
details td {{ padding:.35rem .5rem; border-bottom:1px solid var(--rule); vertical-align:top; }}
details td:first-child {{ font-family:var(--mono); color:var(--mark);
  white-space:nowrap; width:6rem; }}
.warn {{ margin-top:1.5rem; font-size:.75rem; color:var(--soft);
  border-left:2px solid var(--mark); padding-left:.7rem; }}
@media (prefers-reduced-motion:reduce) {{ * {{ transition:none !important; }} }}
</style>
</head>
<body>
<header><div class="wrap">
  <h1>{html.escape(title)}</h1>
  <input id="q" type="search" placeholder="english word or root" autocomplete="off"
         autocapitalize="off" autocorrect="off" spellcheck="false" aria-label="Search">
  <div class="chips" id="chips"></div>
  <p id="count"></p>
</div></header>

<main class="wrap">
  <div id="results"></div>
  <details>
    <summary>Grammar</summary>
    <table>
{rows}
    </table>
  </details>
  <p class="warn">This file is the key. Anyone who opens it can read everything
  written in the language. Keep it off shared drives and out of chat apps.</p>
</main>

<script>
const DATA = {data};
const CATS = {cats};
const results = document.getElementById('results');
const q = document.getElementById('q');
const count = document.getElementById('count');
const chips = document.getElementById('chips');
let active = null;

CATS.forEach(cat => {{
  const b = document.createElement('button');
  b.className = 'chip'; b.textContent = cat; b.setAttribute('aria-pressed','false');
  b.onclick = () => {{
    active = (active === cat) ? null : cat;
    [...chips.children].forEach(c =>
      c.setAttribute('aria-pressed', String(c.textContent === active)));
    render();
  }};
  chips.appendChild(b);
}});

function copy(text, el) {{
  navigator.clipboard?.writeText(text).then(() => {{
    el.classList.add('copied');
    setTimeout(() => el.classList.remove('copied'), 700);
  }}).catch(() => {{}});
}}

function score(e, t) {{
  if (e.r.includes(t)) return 0;
  if (e.w.includes(t)) return 1;
  if (e.w.some(w => w.startsWith(t))) return 2;
  if (e.r.some(r => r.startsWith(t))) return 3;
  if (e.m.toLowerCase().includes(t)) return 4;
  if (e.w.some(w => w.includes(t))) return 5;
  return -1;
}}

function render() {{
  const term = q.value.trim().toLowerCase();
  let list = DATA.map((e, i) => ({{e, i}}));
  if (active) list = list.filter(x => x.e.c === active);
  if (term) {{
    list = list.map(x => ({{...x, s: score(x.e, term)}}))
               .filter(x => x.s >= 0).sort((a,b) => a.s - b.s || a.i - b.i);
  }}
  count.textContent = list.length + (list.length === 1 ? ' entry' : ' entries');
  results.innerHTML = '';
  if (!list.length) {{
    const p = document.createElement('p');
    p.className = 'empty';
    p.textContent = 'No match. Try the other language, or a shorter word.';
    results.appendChild(p); return;
  }}
  const frag = document.createDocumentFragment();
  for (const {{e}} of list) {{
    const row = document.createElement('div'); row.className = 'entry';
    const left = document.createElement('div'); left.className = 'meaning';
    const cat = document.createElement('span'); cat.className = 'cat';
    cat.textContent = e.c; left.appendChild(cat);
    left.appendChild(document.createTextNode(e.m));
    const right = document.createElement('div'); right.className = 'roots';
    e.r.forEach((root, i) => {{
      const rr = document.createElement('div'); rr.className = 'rootrow';
      const slot = document.createElement('span'); slot.className = 'slot';
      slot.textContent = e.s[i] === '\\u2014' ? '' : e.s[i];
      const trip = document.createElement('button');
      trip.className = 'triplet'; trip.title = 'Copy ' + root;
      trip.setAttribute('aria-label', 'Copy root ' + root);
      [...root].forEach(ch => {{
        const s = document.createElement('span'); s.textContent = ch; trip.appendChild(s);
      }});
      trip.onclick = () => copy(root, trip);
      rr.appendChild(slot); rr.appendChild(trip); right.appendChild(rr);
    }});
    row.appendChild(left); row.appendChild(right); frag.appendChild(row);
  }}
  results.appendChild(frag);
}}

q.addEventListener('input', render);
render(); q.focus();
</script>
</body>
</html>
"""


# ==========================================================================
# Pipeline
# ==========================================================================

def load_state():
    if not os.path.exists(F_STATE):
        return None
    try:
        with open(F_STATE, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def build(config, open_browser=True):
    blocklist = build_blocklist(config["root_length"])
    needed = slots_needed(config["rotation"])
    target = max(config["min_roots"], needed)

    print()
    rule()
    print("  BUILDING")
    rule()

    # -- roots in --------------------------------------------------------
    if os.path.exists(F_ROOTS):
        with open(F_ROOTS, encoding="utf-8") as fh:
            raw_lines = fh.readlines()
        print(f"    read          {len([l for l in raw_lines if l.strip()])} lines "
              f"from roots.txt")
    else:
        print(f"    roots.txt not found")
        if interactive() and not confirm(
                f"    Generate {target} roots from scratch?", True):
            sys.exit("  stopped. Put roots.txt beside this script and re-run.")
        raw_lines = []

    print(f"    blocklist     {len(blocklist)} words of length "
          f"{config['root_length']}")

    # -- check ------------------------------------------------------------
    accepted, rejected, blocked = check_roots(raw_lines, config, blocklist)
    if raw_lines:
        print(f"    accepted      {len(accepted)}")
        print(f"    rejected      {len(rejected)}")
        reasons = {}
        for _, reason in rejected:
            key = ("too similar to an earlier root" if "too similar" in reason
                   else reason)
            reasons[key] = reasons.get(key, 0) + 1
        for reason, n in sorted(reasons.items(), key=lambda kv: -kv[1]):
            print(f"                  {n:4d}  {reason}")

    # -- top up -----------------------------------------------------------
    accepted, added = top_up(accepted, blocked, config, blocklist, target)
    if added:
        print(f"    generated     {len(added)} new roots")
    if len(accepted) < target:
        sys.exit(
            f"\n  Only reached {len(accepted)} of {target} roots.\n"
            f"  The one-letter rule is packing the space too tightly.\n"
            f"  Re-run with --reconfigure and either turn that rule off\n"
            f"  or move to {config['root_length'] + 1}-letter roots.")
    print(f"    total roots   {len(accepted)}")

    # -- assign -----------------------------------------------------------
    try:
        vocabulary, spare = assign(accepted, config)
    except RuntimeError as exc:
        sys.exit(f"\n  {exc}")
    print(f"    assigned      {needed} slots, {len(spare)} spare")

    # -- write ------------------------------------------------------------
    if raw_lines and not os.path.exists(F_BACKUP):
        with open(F_BACKUP, "w", encoding="utf-8") as fh:
            fh.writelines(raw_lines)

    with open(F_ROOTS, "w", encoding="utf-8") as fh:
        fh.write("\n".join(sorted(accepted)) + "\n")

    with open(F_REJECTED, "w", encoding="utf-8") as fh:
        for root, reason in rejected:
            fh.write(f"{root}\t{reason}\n")

    state = {"config": config, "roots": sorted(accepted),
             "spare": spare, "vocabulary": vocabulary}
    with open(F_STATE, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, ensure_ascii=False)

    language = Language(state)
    write_markdown(language, F_MARKDOWN)
    with open(F_HTML, "w", encoding="utf-8") as fh:
        fh.write(build_html(language))

    print(f"    indexed       {len(language.by_word)} English forms")
    rule()
    print("  WROTE")
    for path in (F_HTML, F_MARKDOWN, F_STATE, F_ROOTS, F_REJECTED):
        print(f"    {os.path.basename(path)}")
    rule()

    if open_browser:
        try:
            webbrowser.open(f"file://{F_HTML}")
            print(f"\n  opened lookup.html in your browser")
        except Exception:
            print(f"\n  open this yourself: {F_HTML}")

    print(f"\n  try:  python3 {os.path.basename(__file__)} --shell\n")
    return language


def run_shell(language):
    print()
    print("  Type English to encode. Type the language to decode.")
    print("  ctrl-c to quit.")
    print()
    while True:
        try:
            line = input("  … ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not line:
            continue
        caps = sum(1 for c in line if c.isupper())
        reverse = caps > 2 and (language.config["boundary"] == "capitals"
                                and " " not in line.strip("."))
        out, notes = (language.decode(line) if reverse else language.encode(line))
        print(f"     {out}")
        for note in notes:
            print(f"     ! {note}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Build a typed-only secret language from a list of roots.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--reconfigure", action="store_true",
                        help="change the rules, then rebuild")
    parser.add_argument("--rebuild", action="store_true",
                        help="rebuild from saved settings without prompting")
    parser.add_argument("--encode", metavar="TEXT", help="English -> language")
    parser.add_argument("--decode", metavar="TEXT", help="language -> English")
    parser.add_argument("--shell", action="store_true",
                        help="interactive translation")
    parser.add_argument("--no-open", action="store_true",
                        help="don't open the browser after building")
    args = parser.parse_args()

    state = load_state()

    # Keep stdout clean for --encode/--decode so output can be piped.
    if not (args.encode or args.decode):
        print_banner("a typed-only secret language")

    if args.encode or args.decode or args.shell:
        if not state:
            sys.exit("  No language built yet. Run this with no arguments first.")
        language = Language(state)
        if args.encode:
            out, notes = language.encode(args.encode)
            print(out)
            for note in notes:
                print(f"  ! {note}", file=sys.stderr)
        elif args.decode:
            out, notes = language.decode(args.decode)
            print(out)
            for note in notes:
                print(f"  ! {note}", file=sys.stderr)
        else:
            run_shell(language)
        return

    if args.rebuild and state:
        build(state["config"], open_browser=not args.no_open)
        return

    if state and not args.reconfigure:
        print()
        print(f"  Found an existing language: {state['config']['title']}")
        print(f"  Rebuilding reassigns every root. Old messages stop decoding.")
        if not confirm("  Change the rules?", False):
            build(state["config"], open_browser=not args.no_open)
            return

    config = run_wizard(state["config"] if state else None)
    build(config, open_browser=not args.no_open)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  cancelled.")
        sys.exit(130)
