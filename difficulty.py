"""
Difficulty levels: each maps to its own sentence pool and an optional
countdown time limit (seconds). None means untimed.
"""

DIFFICULTIES = {
    "Easy": {
        "time_limit": None,
        "sentences": [
            "The cat sat on the mat.",
            "I like to read books.",
            "She has a red bike.",
            "We went to the park.",
            "The sun is very bright.",
            "He can run very fast.",
            "Dogs are good pets.",
            "It is time for lunch.",
            "The sky is blue today.",
            "I want a cup of tea.",
            "They play games at night.",
            "My mom made a cake.",
        ],
    },
    "Medium": {
        "time_limit": 45,
        "sentences": [
            "The quick brown fox jumps over the lazy dog.",
            "Practice makes perfect, especially with typing.",
            "Programming is the art of telling a computer what to do.",
            "She sells seashells by the seashore every summer.",
            "A journey of a thousand miles begins with a single step.",
            "Never underestimate the power of a good night's sleep.",
            "The early bird catches the worm, but the second mouse gets the cheese.",
            "Typing quickly is a skill that improves with daily practice.",
            "Curiosity is the engine of achievement in any field.",
            "Simplicity is the ultimate form of sophistication.",
            "Great things are never done by one person alone.",
            "The only way to do great work is to love what you do.",
            "Consistency beats intensity when building a new habit.",
            "Keep your friends close and your keyboard closer.",
            "Success is the sum of small efforts repeated daily.",
        ],
    },
    "Hard": {
        "time_limit": 20,
        "sentences": [
            "In 2024, the company reported a 37.5% increase in quarterly revenue.",
            "\"Well,\" she said, \"I suppose we'll never really know, will we?\"",
            "The recipe calls for 2.5 cups of flour, 3 eggs, and 1/4 tsp of salt.",
            "Dr. Alvarez's report (dated 04/12/2023) cited 12 separate anomalies.",
            "Please remit payment of $1,240.99 within 30 days; late fees apply.",
            "The API returned a 404 error after exactly 3.2 seconds of latency.",
            "Section 7(b)(2) of the contract voids clause #4 under these conditions.",
            "Coordinates 40.7128° N, 74.0060° W mark the intersection precisely.",
            "\"Don't forget,\" he warned, \"the meeting starts at 9:15 a.m. sharp!\"",
            "The algorithm's complexity is O(n log n), a significant improvement.",
            "Inventory #A-2291 shipped on 11/03/2025 via Flight QF-402 at 06:45.",
            "Her thesis, titled \"Entropy & Order,\" spans 214 pages and 3 appendices.",
        ],
    },
}
