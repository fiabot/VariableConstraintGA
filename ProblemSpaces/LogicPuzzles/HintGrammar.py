import random 
from itertools import combinations  
import math 
###### HELPER FUNCTIONS #########

terminals = [
    "cat",
    "ent",
    "cat1",
    "cat2",
    "cat3",
    "cat4",
    "cat5",
    "ent1",
    "ent2",
    "ent3",
    "ent4",
    "ent5",
    "num",
    "alp",
    "int",
]

hint_grammar = {
    "hint": {
        "is": [["cat1", "ent", "cat2", "ent"]],
        "not": [["is"]],
        "before": [
            ["alp", "ent1", "alp", "ent2", "num"],
            ["alp", "ent1", "alp", "ent2", "num", "int"],
        ],
        "simple_or": [
            ["cat1", "ent1", "cat1", "ent2", "cat2", "ent"],
            ["cat1", "ent", "cat2", "ent", "cat3", "ent"],
        ],
        "compound_or": [["is", "is"]],
    }
}

def sub_grammar(grammar, rule):
    queue = []
    queue.append(grammar)
    while queue:
        grammar = queue.pop(0)
        if rule in list(grammar.keys()):
            return grammar[rule]
        for r in list(grammar.keys()):
            if isinstance(grammar[r], dict):
                queue.append(grammar[r])
    return


def generate_word(grammar, terminals, grand_grammar=None):
    """
    randomly choice production rules to create new hint base
    will fill out production rules until all terms are terminals
    """
    if grand_grammar is None:
        grand_grammar = grammar
    rule = ""
    if isinstance(grammar, dict):
        # Grammar has named rules; select one at random
        rule = random.choice(list(grammar.keys()))
        if isinstance(grammar[rule], dict):
            # Rule is a subgrammar with named rules itself; recurse
            return {rule: generate_word(grammar[rule], terminals, grand_grammar)}
        else:
            # Rule is a list of alternates
            grammar = grammar[rule]
    # Grammar is a list of alternates; select one at random
    production = random.choice(grammar)
    terms = []
    for word in production:
        if word in terminals:
            terms.append(word)
        else:
            terms.append({
                word: generate_word(
                    sub_grammar(grand_grammar, word), terminals, grand_grammar
                )
            })
    if rule != "":
        return {rule: terms}
    else:
        return terms


def create_cats(puzzle):
    """
    shuffle categories and entities within categories and return as a nested list
    ex: [[cat1, [ent1.1, ent1.2, ent1.2]], [cat2, [ent2.1, ent2.2, ent2.3]]]
    """
    li = puzzle.categories[:]
    random.shuffle(li)
    cats = []
    for cat in li:
        shuf_ents = cat.entities[:]
        random.shuffle(shuf_ents)
        cats.append([cat, shuf_ents])
    return cats


def get_alps(cats):
    """
    return all alphabetic categories
    """
    return [cat for cat in cats if not cat[0].is_numeric]


def get_num(cats):
    """
    return all numeric categories
    """
    return [cat for cat in cats if cat[0].is_numeric]


def fill_in_word(puzzle, word):
    """
    Replace all terminal terms with random and appropriate
    categories, entities, or integers from a puzzle
    """
    filled_word = {}
    for key in word:
        value = word[key]
        if isinstance(value, dict):
            filled_word[key] = fill_in_word(puzzle, word[key])
        else:
            new_terms = []
            cats = create_cats(puzzle)
            alps = get_alps(cats)
            nums = get_num(cats)
            last_cat = None

            for term in value:
                if isinstance(term, dict):
                    new_terms.append(fill_in_word(puzzle, term))
                else:
                    if term == "cat":
                        last_cat = random.choice(cats)
                        new_terms.append(last_cat[0])
                    elif term == "cat1":
                        if len(cats) < 1:
                            raise Exception("CAT_COUNT")
                        else:
                            last_cat = cats[0]
                            new_terms.append(last_cat[0])
                    elif term == "cat2":
                        if len(cats) < 2:
                            raise Exception("CAT_COUNT")
                        else:
                            last_cat = cats[1]
                            new_terms.append(last_cat[0])
                    elif term == "cat3":
                        if len(cats) < 3:
                            raise Exception("CAT_COUNT")
                        else:
                            last_cat = cats[2]
                            new_terms.append(last_cat[0])
                    elif term == "alp":
                        if len(alps) == 0:
                            raise Exception("ALPH_COUNT")
                        else:
                            last_cat = random.choice(alps)
                            new_terms.append(last_cat[0])
                    elif term == "num":
                        if len(nums) == 0:
                            raise Exception("NUM_COUNT")
                        else:
                            last_cat = random.choice(nums)
                            new_terms.append(last_cat[0])
                    elif term == "ent":
                        new_terms.append(random.choice(last_cat[1]))
                    elif term == "ent1":
                        if len(last_cat[1]) < 1:
                            raise Exception("ENT_COUNT")
                        else:
                            new_terms.append(last_cat[1][0])
                    elif term == "ent2":
                        if len(last_cat[1]) < 2:
                            raise Exception("ENT_COUNT")
                        else:
                            new_terms.append(last_cat[1][1])
                    elif term == "ent3":
                        if len(last_cat[1]) < 3:
                            raise Exception("ENT_COUNT")
                        else:
                            new_terms.append(last_cat[1][2])
                    elif term == "int":
                        new_terms.append(
                            random.randrange(1, len(last_cat[1]) - 1)
                        )  # 2 spaces to make decision
            filled_word[key] = new_terms
    return filled_word


def generate_hint(puzzle):
    """
    given a puzzle generate a random, valid hint
    """
    word = generate_word(hint_grammar, terminals)
    try:
        return fill_in_word(puzzle, word)["hint"]
    except:
        return generate_hint(puzzle)
    

class HintSet:
    def __init__(
        self, hints, puzzle) -> None:
        self.hints = hints
        self.puzzle = puzzle  
    
        self.completed_puzzle, self.valid, self.loops, self.solver_insights = puzzle.apply_hints(hints)

        self.insights = set()
        

    def mutate(self, add_rate):
        hint_copy = self.hints[:]
        roll = random.random()
        if ((roll < 0.45) and len(hint_copy) <= 20) or len(hint_copy) <= 0:
            new_hint = generate_hint(self.puzzle)
            hint_copy.append(new_hint)
        elif roll < 0.90:
            index = random.randint(0, len(hint_copy) - 1)
            del hint_copy[index]
        else:
            self.swap_hints()

        return HintSet(
            hint_copy,
            self.puzzle
        )

    def swap_hints(self):
        i = random.randint(0, len(self.hints) - 1)
        j = random.randint(0, len(self.hints) - 1)
        temp = self.hints[i]
        self.hints[i] = self.hints[j]
        self.hints[j] = temp

    def cross_over(self, other):
        hints = self.hints[:] + other.hints[:]
        random.shuffle(hints)
        threshold = math.floor(len(hints) / 2)

        return HintSet(
            hints[0:threshold],
            self.puzzle
        ), HintSet(
            hints[threshold : len(hints)],
            self.puzzle
        )


    def is_feasible(self):
        valid = (
            len(self.hints) > 0
            and self.valid
            and self.completed_puzzle.is_complete()
        )

        return valid

    def solver_loops(self):
        if len(self.hints) == 0:
            return 0

        return self.loops

    def hint_size(self):
        return len(self.hints)