"""
Sentence categories: each category owns its own Easy/Medium/Hard pools, so the
difficulty selector keeps working exactly as before and the category simply
decides *which* set of pools to read from.

A sentence entry is either a plain string, or a (text, note) tuple where the
note is a short teaching hint shown under the sentence during the game.
"""

import random

from difficulty import DIFFICULTIES

GRAMMAR = {
    "Easy": {
        "time_limit": 60,
        "sentences": [
            ("She goes to school every day.",
             "Present Simple - add -s to the verb for he, she or it."),
            ("I am a teacher and he is a student.",
             "The verb 'to be': I am, he/she/it is, we/you/they are."),
            ("There is a book on the table.",
             "'There is' for one thing, 'There are' for more than one."),
            ("An apple a day keeps the doctor away.",
             "Use 'an' before a vowel sound and 'a' before a consonant sound."),
            ("He does not like cold coffee.",
             "Present Simple negatives use 'does not' plus the base verb."),
            ("Do you live near the station?",
             "Yes/no questions in Present Simple start with 'Do' or 'Does'."),
            ("This is my sister's bag.",
             "Possession - the bag belongs to my sister."),
            ("The children are playing in the garden.",
             "Irregular plural: one child, two children."),
            ("I go to work by bus at eight o'clock.",
             "'by' for transport and 'at' for clock times."),
            ("We have two cats and three dogs.",
             "Regular plurals just add -s: cat becomes cats."),
        ],
    },
    "Medium": {
        "time_limit": 45,
        "sentences": [
            ("I have lived in this city since 2019.",
             "Present Perfect with 'since' - it started in the past and is still true."),
            ("She visited Paris last summer.",
             "Past Simple, because 'last summer' is a finished time."),
            ("If it rains tomorrow, we will stay at home.",
             "First conditional: if + Present Simple, then will + base verb."),
            ("The letter was written by my grandmother.",
             "Passive voice: be + past participle, and 'by' introduces the doer."),
            ("The man who called you is waiting outside.",
             "Relative pronoun 'who' for people, 'which' for things."),
            ("You should see a doctor about that cough.",
             "'should' gives advice, and modals are never followed by 'to'."),
            ("This road is longer than the old one.",
             "Comparatives: short adjectives take -er and are followed by 'than'."),
            ("They were watching a film when the power went out.",
             "Past Continuous sets the scene, Past Simple interrupts it."),
            ("I have already finished my homework.",
             "'already' sits between 'have' and the past participle."),
            ("He is used to working late on Fridays.",
             "'be used to' + -ing means accustomed to, not a past habit."),
        ],
    },
    "Hard": {
        "time_limit": 20,
        "sentences": [
            ("If I had left earlier, I would be home by now.",
             "Mixed conditional: a past condition with a present result."),
            ("She said that she had been waiting for two hours.",
             "Reported speech shifts Present Perfect back to Past Perfect."),
            ("Never before had we seen such a beautiful sunset.",
             "Inversion: after a negative adverb the auxiliary comes before the subject."),
            ("The committee recommended that he resign immediately.",
             "Subjunctive after 'recommend that' - base verb, no -s."),
            ("Hardly had the meeting begun when the fire alarm rang.",
             "'Hardly ... when' takes Past Perfect plus inversion."),
            ("Were I in your position, I would accept the offer.",
             "Formal conditional: 'Were I' replaces 'If I were'."),
            ("It is essential that every document be signed in triplicate.",
             "Subjunctive 'be' after 'It is essential that'."),
            ("Not only did he apologise, but he also paid for the damage.",
             "'Not only' at the front forces 'did' plus the base verb."),
            ("The proposal, which had been rejected twice, was finally approved.",
             "A non-defining relative clause is fenced off by commas."),
            ("Having completed the report, she submitted it before the deadline.",
             "The perfect participle shows one action finished before the next."),
        ],
    },
}

CONVERSATION = {
    "Easy": {
        "time_limit": 60,
        "sentences": [
            ("Hi, how are you doing today?",
             "Everyday greeting - friendlier than 'How do you do?'"),
            ("Nice to meet you. I'm Sam.",
             "First introduction; the usual reply is 'Nice to meet you too.'"),
            ("Sorry, could you say that again please?",
             "Polite way to ask someone to repeat themselves."),
            ("Thank you so much for your help.",
             "'so much' makes the thanks sound warmer and more sincere."),
            ("Excuse me, where is the nearest station?",
             "Open with 'Excuse me' before asking a stranger anything."),
            ("See you tomorrow. Have a good evening!",
             "Common friendly goodbye at the end of the day."),
            ("What do you do in your free time?",
             "Small talk opener that invites the other person to talk about hobbies."),
            ("I'm sorry, I don't understand.",
             "Simple, polite way to signal that you are lost."),
            ("Can I help you with that bag?",
             "'Can I ...?' is the everyday way to offer help."),
            ("It's really nice weather today, isn't it?",
             "A tag question invites the other person to agree."),
        ],
    },
    "Medium": {
        "time_limit": 45,
        "sentences": [
            ("Could I have a coffee and a croissant, please?",
             "Ordering at a cafe - 'Could I have' is politer than 'I want'."),
            ("Excuse me, how do I get to the museum from here?",
             "Asking a stranger for directions."),
            ("Hello, this is Maria calling about the appointment.",
             "On the phone you say 'this is', never 'I am'."),
            ("Would you mind if I opened the window?",
             "'Would you mind if I ...' asks permission very politely."),
            ("I'd like to book a table for four at seven.",
             "'I'd like' is the standard polite request in shops and restaurants."),
            ("Sorry to bother you, but do you have a minute?",
             "A softener used before interrupting someone."),
            ("How long does it take to get to the airport?",
             "'How long does it take' asks about duration, not distance."),
            ("Could you speak a little more slowly, please?",
             "Asks someone to slow down without sounding rude."),
            ("That sounds great, but let me check my schedule.",
             "Agrees in principle while keeping your options open."),
            ("I'm afraid I can't make it on Friday.",
             "'I'm afraid' softens bad news or a refusal."),
        ],
    },
    "Hard": {
        "time_limit": 20,
        "sentences": [
            ("I see your point, but I'm not entirely convinced by that argument.",
             "Disagreeing politely - acknowledge first, then object."),
            ("To be honest, I'd rather we postponed the trip until next month.",
             "'I'd rather' plus a past tense expresses a strong preference."),
            ("If you don't mind me asking, what made you change careers?",
             "A softener placed before a personal question."),
            ("I'm not sure I follow, so could you walk me through it again?",
             "Admits confusion without blaming the speaker."),
            ("Correct me if I'm wrong, but didn't we agree on Thursday?",
             "A negative question challenges a fact gently."),
            ("On the one hand it's cheaper; on the other, it takes far longer.",
             "'On the one hand ... on the other' balances two opposing views."),
            ("I'd appreciate it if you could let me know by the end of the day.",
             "More insistent than 'please tell me', but still polite."),
            ("It's not that I don't want to go; I simply don't have the time.",
             "'It's not that ... I simply ...' corrects a wrong assumption."),
            ("Now that you mention it, I did notice something strange.",
             "'Now that you mention it' introduces a recalled detail; 'did' adds emphasis."),
            ("Let's agree to disagree and move on to the next item.",
             "Ends an argument politely without either side winning."),
        ],
    },
}

IDIOMS = {
    "Easy": {
        "time_limit": 60,
        "sentences": [
            ("It is raining cats and dogs outside.",
             "'raining cats and dogs' - raining very heavily."),
            ("That test was a piece of cake.",
             "'a piece of cake' - very easy."),
            ("Break a leg at your audition tonight!",
             "'break a leg' - good luck, said to performers."),
            ("You hit the nail on the head.",
             "'hit the nail on the head' - to be exactly right."),
            ("I am feeling under the weather today.",
             "'under the weather' - slightly ill."),
            ("Let us call it a day and go home.",
             "'call it a day' - stop working for now."),
            ("She is a couch potato on Sundays.",
             "'couch potato' - someone who sits around watching television."),
            ("Keep an eye on my bag for a minute.",
             "'keep an eye on' - watch or look after something."),
            ("He spilled the beans about the party.",
             "'spill the beans' - reveal a secret."),
            ("Once in a blue moon we eat out.",
             "'once in a blue moon' - very rarely."),
        ],
    },
    "Medium": {
        "time_limit": 45,
        "sentences": [
            ("Those new headphones cost an arm and a leg.",
             "'cost an arm and a leg' - to be extremely expensive."),
            ("You are barking up the wrong tree with that theory.",
             "'bark up the wrong tree' - to pursue a mistaken idea."),
            ("Let's not beat around the bush; tell me the truth.",
             "'beat around the bush' - avoid saying something directly."),
            ("I am afraid that ship has already sailed.",
             "'that ship has sailed' - the opportunity has passed."),
            ("He was left out in the cold after the merger.",
             "'out in the cold' - excluded from a group or a decision."),
            ("We will have to bite the bullet and pay the fine.",
             "'bite the bullet' - accept something unpleasant you cannot avoid."),
            ("She passed the exam by the skin of her teeth.",
             "'by the skin of your teeth' - only just, very narrowly."),
            ("Don't put all your eggs in one basket.",
             "'all your eggs in one basket' - risking everything on a single plan."),
            ("The whole project went south very quickly.",
             "'go south' - to go badly wrong."),
            ("I heard it straight from the horse's mouth.",
             "'from the horse's mouth' - from the original, reliable source."),
        ],
    },
    "Hard": {
        "time_limit": 20,
        "sentences": [
            ("The decision to cut funding was the straw that broke the camel's back.",
             "'the straw that broke the camel's back' - the small last problem that causes collapse."),
            ("Once he retires, filling his shoes will be no mean feat.",
             "'fill someone's shoes' - replace them; 'no mean feat' - a genuinely hard achievement."),
            ("She has a chip on her shoulder about where she went to university.",
             "'a chip on your shoulder' - a lasting resentment about being treated unfairly."),
            ("Their argument over the budget is a storm in a teacup.",
             "'a storm in a teacup' - a big fuss about something trivial."),
            ("He was caught between a rock and a hard place when both offers expired.",
             "'between a rock and a hard place' - forced to choose between two bad options."),
            ("The new manager hit the ground running on her very first day.",
             "'hit the ground running' - start something quickly and effectively."),
            ("Don't look a gift horse in the mouth; just say thank you.",
             "'look a gift horse in the mouth' - criticise something you were given for free."),
            ("Their proposal is, at best, a shot in the dark.",
             "'a shot in the dark' - a wild guess made with very little information."),
            ("After the scandal, the chief executive threw his deputy under the bus.",
             "'throw someone under the bus' - betray them to save yourself."),
            ("We were burning the candle at both ends before the deadline.",
             "'burn the candle at both ends' - exhaust yourself with early starts and late nights."),
        ],
    },
}

BUSINESS = {
    "Easy": {
        "time_limit": 60,
        "sentences": [
            ("Please find the report attached.",
             "Standard line for pointing to an email attachment."),
            ("Thank you for your quick reply.",
             "Short, polite acknowledgement of a fast response."),
            ("I will send you the details tomorrow.",
             "A clear commitment with a clear deadline."),
            ("Could we meet at ten on Monday?",
             "Proposing a time as a question sounds more considerate."),
            ("Let me know if you have any questions.",
             "Common closing line in a work email."),
            ("Sorry for the late reply.",
             "Brief apology for a delayed response."),
            ("I am writing to confirm our meeting.",
             "'I am writing to ...' states the purpose of the email up front."),
            ("Please let me know your availability this week.",
             "Asks for someone's free times without proposing one yourself."),
            ("Kind regards, and thank you again.",
             "'Kind regards' is a safe semi-formal sign-off."),
            ("The team will review your proposal today.",
             "A neutral status update, stated as a plain fact."),
        ],
    },
    "Medium": {
        "time_limit": 45,
        "sentences": [
            ("I am following up on my email from last Tuesday.",
             "'following up' is the polite way to chase an unanswered email."),
            ("Apologies for the delay; I have been out of the office.",
             "Explains a delay briefly without over-apologising."),
            ("Could you please confirm receipt of the invoice?",
             "'confirm receipt' is standard for documents and payments."),
            ("As discussed, I have attached the revised figures.",
             "'As discussed' ties the email back to an earlier conversation."),
            ("Unfortunately, we are unable to meet that deadline.",
             "'Unfortunately' plus 'we are unable to' delivers bad news formally."),
            ("Please do not hesitate to contact me if anything is unclear.",
             "A formal closing offer of help."),
            ("I would like to schedule a call to discuss next steps.",
             "Proposes a meeting in professional register."),
            ("Thank you for bringing this to my attention.",
             "Acknowledges a problem someone raised without admitting fault."),
            ("We appreciate your patience while we resolve this issue.",
             "Buys time politely during a delay."),
            ("Looking forward to hearing from you soon.",
             "A standard sign-off that invites a reply."),
        ],
    },
    "Hard": {
        "time_limit": 20,
        "sentences": [
            ("Q3 revenue rose 12.4% year-on-year, exceeding our forecast of $4.7M.",
             "In financial writing the % and $ signs stay attached to their numbers."),
            ("Please review Section 3.2 of the attached agreement before our 09:30 call.",
             "Numbered clauses use a full stop; 24-hour times use a colon."),
            ("Invoice #INV-2025-0417 is now 45 days overdue; payment is due immediately.",
             "A semicolon joins two closely linked statements in formal writing."),
            ("The contract renews automatically on 01/04/2026 unless cancelled in writing.",
             "'unless ... in writing' is standard notice-clause phrasing."),
            ("Headcount grew from 218 to 341 (a 56.4% increase) in eighteen months.",
             "Parentheses add a supporting figure without breaking the sentence."),
            ("Our margin fell to 8.9%, down from 11.2% in the previous quarter.",
             "'down from' makes the direction of the change explicit."),
            ("Either party may terminate this agreement with 60 days' written notice.",
             "Plural possessive: '60 days' notice' takes the apostrophe after the s."),
            ("Please forward the signed agreement to legal@example.com by 17:00 GMT.",
             "A formal instruction with a hard deadline and a stated time zone."),
            ("The audit identified 7 material weaknesses across 3 business units.",
             "Audit findings are stated as plain counts, without adjectives."),
            ("Budget approval (ref. FIN-2024/118) requires two directors' signatures.",
             "'ref.' abbreviates reference; 'directors'' is another plural possessive."),
        ],
    },
}

# Dict order drives the order of the radio buttons on the main menu.
SENTENCE_SETS = {
    "General": DIFFICULTIES,
    "Grammar": GRAMMAR,
    "Conversation": CONVERSATION,
    "Idioms": IDIOMS,
    "Business": BUSINESS,
}

DEFAULT_CATEGORY = "General"

# The level that is always shown without any punctuation at all.
BEGINNER_LEVEL = "Easy"

# Marks that become a space when stripped, instead of being deleted outright.
_SEPARATORS = "-/"


def _pool(category, level):
    """Look up one pool, falling back to General if a category goes stale."""
    return SENTENCE_SETS.get(category, DIFFICULTIES)[level]


def get_time_limit(category, level):
    return _pool(category, level)["time_limit"]


def pick_sentence(category, level):
    """Return (text, note) at random; note is "" for plain-string entries."""
    entry = random.choice(_pool(category, level)["sentences"])
    if isinstance(entry, tuple):
        return entry
    return entry, ""


def _strip_punctuation(text, keep_word_marks=True):
    """Drop punctuation from a sentence.

    With keep_word_marks, apostrophes and hyphens inside a word survive so that
    contractions and compounds stay readable:
    "Don't beat around the bush; tell me." -> "Don't beat around the bush tell me"

    Without it nothing survives, and separators become a space rather than
    fusing two words together:
    "Don't beat around the bush; tell me." -> "Dont beat around the bush tell me"
    "12.4% year-on-year"                   -> "124 year on year"
    """
    kept = []
    for i, ch in enumerate(text):
        if ch.isalnum() or ch.isspace():
            kept.append(ch)
        elif keep_word_marks:
            if (ch in "'-" and 0 < i < len(text) - 1
                    and text[i - 1].isalnum() and text[i + 1].isalnum()):
                kept.append(ch)
        elif ch in _SEPARATORS:
            kept.append(" ")
    return " ".join("".join(kept).split())


def format_sentence(text, level, punctuation=True, capitals=True):
    """Apply the player's typing options to a sentence before it is displayed.

    Beginners get plain letter keys: on Easy every punctuation mark goes,
    whatever the menu toggle says. Medium and Hard follow the toggle and keep
    their contractions.
    """
    if level == BEGINNER_LEVEL:
        text = _strip_punctuation(text, keep_word_marks=False)
    elif not punctuation:
        text = _strip_punctuation(text, keep_word_marks=True)
    if not capitals:
        text = text.lower()
    return text
