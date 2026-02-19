"""
LLM Helper Module
Centralized module for LLM interactions used by various parts of the application.
Supports:
  - Generating math questions tailored to specific primary levels (P1-P6, PLSE)
  - Text translation (English ↔ Myanmar)
"""

import os
from typing import Optional, List, Dict, Tuple
from openai import OpenAI


class LLMHelper:
    """Helper class for LLM operations across the application."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM Helper.
        
        Args:
            api_key: OpenRouter API key. If None, will attempt to load from environment.
        """
        if api_key is None:
            api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
        
        if not api_key:
            raise ValueError("API key not provided and not found in environment")
        
        self.api_key = api_key
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = "deepseek/deepseek-r1-0528:free"
        self.last_error: Optional[str] = None
    
    # ==========================================
    # MATH QUESTION GENERATION
    # ==========================================
    
    def generate_math_questions(self, level: str, count: int = 10, style: str = "Balanced (Mixed)", fast: bool = True) -> List[Tuple[str, float]]:
        """
        Generate math questions for a specific primary level.
        
        Args:
            level: One of "P1", "P2", "P3", "P4", "P5", "P6", or "PLSE"
            count: Number of questions to generate (default: 10)
            style: One of the style descriptors (e.g., "Balanced (Mixed)") to bias question types
            fast: When True, ask for a shorter/concise response and reduce max tokens for speed
        
        Returns:
            List of tuples (question_string, correct_answer)
            Example: [("3 + 5 = ?", 8), ("12 - 4 = ?", 8)]
        """
        level = level.upper()
        valid_levels = ["P1", "P2", "P3", "P4", "P5", "P6", "PLSE"]
        
        if level not in valid_levels:
            raise ValueError(f"Invalid level: {level}. Must be one of {valid_levels}")
        
        try:
            prompt = self._build_math_prompt(level, count, style=style)

            # Tune request for speed when requested
            if fast:
                max_tokens = max(300, min(1200, 80 * int(count)))
                temperature = 0.2
            else:
                max_tokens = 2000
                temperature = 0.7

            response = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "http://localhost:8501",
                    "X-Title": "Math Practice App"
                },
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )

            response_text = response.choices[0].message.content.strip()
            questions = self._parse_math_response(response_text)

            return questions

        except Exception as e:
            self.last_error = str(e)
            return self._fallback_math_questions(level, count)
    
    def _build_math_prompt(self, level: str, count: int, style: str = "Balanced (Mixed)") -> str:
        """Build the prompt for generating math questions by level."""
        level_specs = {
            "P1": {
                "desc": "Primary 1 (Ages 6-7)",
                "topics": "addition and subtraction within 20, simple multiplication facts, basic word problems",
                "examples": "3 + 5, 12 - 4, 2 × 3, simple story problems with objects",
                "bonus": "Use simple numbers, friendly characters like animals and kids"
            },
            "P2": {
                "desc": "Primary 2 (Ages 7-8)",
                "topics": "addition and subtraction within 100, multiplication and division facts (1-12 times tables), word problems with everyday items",
                "examples": "25 + 18, 50 - 23, 6 × 7, 30 ÷ 5, 'Tom has 15 apples, buys 8 more, how many total?'",
                "bonus": "Make scenarios about school, toys, snacks, animals, daily life"
            },
            "P3": {
                "desc": "Primary 3 (Ages 8-9)",
                "topics": "operations within 1000, multiplication/division (up to 12×12), fractions, word problems, logic/puzzle problems",
                "examples": "234 + 156, 500 - 278, 9 × 8, 48 ÷ 6, 1/2 + 1/4, 'Rabbits and chickens have 10 heads and 28 legs, how many of each?'",
                "bonus": "Include logic puzzles and multi-step decisions"
            },
            "P4": {
                "desc": "Primary 4 (Ages 9-10)",
                "topics": "multi-digit operations, fractions and decimals, geometry (area/perimeter), word problems, mixed operations",
                "examples": "1234 + 567, 2000 - 845, 12 × 15, 144 ÷ 12, 0.5 + 0.25, 'Rectangle 12cm × 8cm, find area', 'If apples cost $3 each and I buy 5, total cost?'",
                "bonus": "Include money problems, shopping, measurements, real-world scenarios"
            },
            "P5": {
                "desc": "Primary 5 (Ages 10-11)",
                "topics": "fractions/decimals/percentages, ratios, basic algebra, geometry, word problems with multiple steps, consumer math",
                "examples": "3/4 × 2/3, 15% of 80, ratio 2:3, solve x + 5 = 12, 'Discount of 20% on $50, final price?', 'Speed and distance problems'",
                "bonus": "Include discounts, taxes, speed-distance-time, proportion problems"
            },
            "P6": {
                "desc": "Primary 6 (Ages 11-12)",
                "topics": "advanced algebra, percentages/ratios/proportions, geometry (area, volume, perimeter), statistics, multi-step problems, profit/loss",
                "examples": "120% of 50, solve 2x + 3 = 11, 'If cost is $80 and profit margin is 25%, selling price?', 'Ratio 2:5, if total is 70, find first part'",
                "bonus": "Include complex scenarios with profit/loss, compound ratios, advanced geometry"
            },
            "PLSE": {
                "desc": "Pre-Lower Secondary Exam (Ages 11-13)",
                "topics": "comprehensive: algebra equations, geometry proofs, statistics, number theory, problem-solving, real-world applications",
                "examples": "Solve quadratic equations, find area and volume, 'A train travels at 60km/h for 2.5 hours, distance?', 'Profit and loss calculations', 'Probability problems'",
                "bonus": "Include challenging multi-step problems, algebra, geometry proofs, statistics"
            }
        }
        
        spec = level_specs.get(level, level_specs["P1"])
        
        # Incorporate style into the prompt to bias question types.
        style_line = f"Prefer style: {style}." if style else ""

        prompt = f"""Generate {count} DIVERSE and ENGAGING math questions suitable for {spec['desc']}.

Topics to cover: {spec['topics']}
Example question types: {spec['examples']}
Special focus: {spec['bonus']}

    {style_line}

IMPORTANT: Create a BALANCED MIX of question types:
1. Pure calculations (mental math, operations) - about 3-4 questions
2. REAL WORLD WORD PROBLEMS - about 4-5 questions (with context, names, items, money)
3. LOGIC/PUZZLE PROBLEMS - about 1-2 questions (multi-step thinking)
4. GEOMETRY/MEASUREMENTS - about 1-2 questions (where applicable for this level)

Format each question EXACTLY as follows (IMPORTANT):
Q: [question text here]
A: [numeric answer only]

CRITICAL RULES:
1. EVERY line with Q: must be followed by a line with A:
2. Q: and A: must be ON SEPARATE LINES
3. Answer must be a NUMBER ONLY (no units, no text, no "=" sign)
4. For word problems, make them SHORT but CLEAR with character names and scenarios
5. Answers must be exact: integers for whole numbers, decimals where needed (e.g., 3.5 not 3.5 cm)
6. All {count} questions should be DIFFERENT and INTERESTING
7. Mix difficulty within the level - some easier, some harder

Format example:
Q: If Sarah has 15 apples and gives 3 to her friend, how many does she have left?
A: 12

Q: 25 + 17 = ?
A: 42

Now generate {count} diverse, interesting, and well-formatted questions.

REQUIREMENTS:
- Be concise and avoid any extra text outside the Q/A pairs.
- Use the exact Q/A format below and do not number the pairs.
- Output should be as short as possible while following the format.

Format example:
Q: If Sarah has 15 apples and gives 3 to her friend, how many does she have left?
A: 12

Q: 25 + 17 = ?
A: 42

Now generate {count} diverse, interesting, and well-formatted questions:"""
        
        return prompt
    
    def _parse_math_response(self, response_text: str) -> List[Tuple[str, float]]:
        """Parse LLM response to extract questions and answers."""
        questions = []
        lines = response_text.strip().split('\n')
        
        current_question = None
        for line in lines:
            line = line.strip()
            
            if line.startswith("Q:"):
                current_question = line[2:].strip()
            elif line.startswith("A:") and current_question:
                try:
                    # Try to convert answer to float
                    answer_str = line[2:].strip()
                    answer = float(answer_str)
                    questions.append((current_question, answer))
                    current_question = None
                except (ValueError, IndexError):
                    pass
        
        # If parsing failed, return fallback
        if not questions:
            return self._fallback_math_questions("P1", 10)
        
        return questions
    
    def _fallback_math_questions(self, level: str, count: int) -> List[Tuple[str, float]]:
        """Provide fallback math questions if LLM call fails."""
        fallback_questions = {
            "P1": [
                ("3 + 5 = ?", 8),
                ("12 - 4 = ?", 8),
                ("2 × 6 = ?", 12),
                ("10 - 3 = ?", 7),
                ("Tom has 4 apples and gets 5 more. How many apples does he have?", 9),
                ("15 - 5 = ?", 10),
                ("4 × 3 = ?", 12),
                ("9 + 1 = ?", 10),
                ("There are 8 red balls and 2 blue balls. How many balls total?", 10),
                ("3 × 2 = ?", 6),
            ],
            "P2": [
                ("25 + 18 = ?", 43),
                ("50 - 23 = ?", 27),
                ("6 × 7 = ?", 42),
                ("30 ÷ 5 = ?", 6),
                ("Sarah has $34 and buys a book for $21. How much money does she have left?", 13),
                ("48 - 17 = ?", 31),
                ("8 × 5 = ?", 40),
                ("24 ÷ 4 = ?", 6),
                ("A box has 15 candies. After eating 7, how many are left?", 8),
                ("60 - 28 = ?", 32),
            ],
            "P3": [
                ("234 + 156 = ?", 390),
                ("500 - 278 = ?", 222),
                ("9 × 8 = ?", 72),
                ("48 ÷ 6 = ?", 8),
                ("Rabbits and chickens have 10 heads and 28 legs total. How many rabbits?", 4),
                ("600 - 234 = ?", 366),
                ("11 × 7 = ?", 77),
                ("56 ÷ 8 = ?", 7),
                ("A rectangle has length 12cm and width 8cm. What is the area?", 96),
                ("1/2 + 1/4 = ?", 0.75),
            ],
            "P4": [
                ("1234 + 567 = ?", 1801),
                ("2000 - 845 = ?", 1155),
                ("12 × 15 = ?", 180),
                ("144 ÷ 12 = ?", 12),
                ("Ducks and goats have 15 heads and 42 feet. How many goats?", 6),
                ("3000 - 1678 = ?", 1322),
                ("25 × 4 = ?", 100),
                ("Apples cost $3 each. If you buy 5 apples, how much do you pay?", 15),
                ("A box with length 10cm, width 6cm, height 4cm. What is the volume?", 240),
                ("0.5 + 0.75 = ?", 1.25),
            ],
            "P5": [
                ("3/4 × 2/3 = ?", 0.5),
                ("15% of 80 = ?", 12),
                ("0.75 + 0.25 = ?", 1.0),
                ("2/5 of 100 = ?", 40),
                ("A shirt costs $50. With a 20% discount, what is the final price?", 40),
                ("8/10 as percentage = ?", 80),
                ("Solve: 3x - 5 = 10, x = ?", 5),
                ("5/8 × 16 = ?", 10),
                ("If ratio of boys to girls is 3:5 and there are 24 boys, how many girls?", 40),
                ("20% of 150 = ?", 30),
            ],
            "P6": [
                ("120% of 50 = ?", 60),
                ("Solve: 2x + 3 = 11, x = ?", 4),
                ("30% of 250 = ?", 75),
                ("Ratio 2:3, if first is 10, second = ?", 15),
                ("Area of triangle with base 12cm and height 10cm = ?", 60),
                ("Solve: 3x - 5 = 10, x = ?", 5),
                ("5/8 × 16 = ?", 10),
                ("45% of 200 = ?", 90),
                ("Solve: x/2 + 3 = 8, x = ?", 10),
                ("Perimeter of rectangle: length 8cm, width 5cm = ?", 26),
            ],
            "PLSE": [
                ("Solve: 2x + 5 = 17, x = ?", 6),
                ("60% of 180 = ?", 108),
                ("A table costs $100 and profit margin is 25%. Selling price = ?", 125),
                ("Ratio 3:5:2, if total is 100, what is the first part?", 30),
                ("Circumference of circle with radius 5cm (π≈3.14) = ?", 31.4),
                ("Solve: 3(x - 2) = 15, x = ?", 7),
                ("Area of triangle with base 10cm and height 8cm = ?", 40),
                ("A discount of 30% on $200, final price = ?", 140),
                ("Speed is 60km/h, travel time is 2.5 hours, distance = ?", 150),
                ("Mean of 10, 20, 30, 40, 50 = ?", 30),
            ]
        }
        
        questions = fallback_questions.get(level.upper(), fallback_questions["P1"])
        return questions[:count]
    
    # ==========================================
    # TRANSLATION
    # ==========================================
    
    def translate_to_english(self, text: str) -> str:
        """Translate text to English."""
        return self._translate(text, "en")
    
    def translate_to_myanmar(self, text: str) -> str:
        """Translate text to Myanmar (Burmese)."""
        return self._translate(text, "my")
    
    def _translate(self, text: str, target_lang: str) -> str:
        """Call LLM for translation."""
        try:
            if target_lang == "en":
                instruction = "Translate this to English:"
            else:  # my
                instruction = "Translate this to Myanmar (Burmese) language:"
            
            prompt = f"{instruction}\n\n{text}\n\nOnly provide the translation, no explanations."
            
            response = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "http://localhost:8501",
                    "X-Title": "Translation Chat App"
                },
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            translated_text = response.choices[0].message.content.strip()
            return translated_text
            
        except Exception as e:
            self.last_error = str(e)
            # Return a more user-friendly error message
            if "401" in str(e):
                return "Translation error: Invalid API key"
            elif "402" in str(e):
                return "Translation error: Insufficient credits"
            elif "429" in str(e):
                return "Translation error: Rate limit exceeded"
            else:
                return f"Translation error: {str(e)[:100]}"


# ==========================================
# FACTORY FUNCTION (for easy imports)
# ==========================================

def get_llm_helper(api_key: Optional[str] = None) -> LLMHelper:
    """
    Factory function to create and return an LLMHelper instance.
    
    Args:
        api_key: Optional API key. If not provided, will load from environment.
    
    Returns:
        LLMHelper instance
    """
    return LLMHelper(api_key)
