import sys
sys.path.insert(0, "../")  # add Folder_2 path to search list

from ProblemSpaceInterface import ProblemSpace, Constraint
from HintGrammar import generate_hint
import random 


## Constant constraints 

class GridIsValid(Constraint):
    def __init__(self, grid_key):
        self.grid_key = grid_key 
    
    def apply(self, indv):
        puzz = indv.completed_puzzle 
        grid = puzz.get_grid_by_key(self.grid_key)
        return puzz.grid_is_valid(grid)

    def __str__(self):
        return "grid: {} is valid".format(self.grid_key)

class GridIsComplete(Constraint):
    def __init__(self, grid_key):
        self.grid_key = grid_key 
    
    def apply(self, indv):
        puzz = indv.completed_puzzle 
        grid = puzz.get_grid_by_key(self.grid_key)
        return puzz.grid_is_complete(grid)
    
    def __str__(self):
        return "grid: {} is complete".format(self.grid_key)

class NoViolations(Constraint):

    def apply(self, indv):
        puzz = indv.completed_puzzle 
        return puzz.num_violations() == 0 

    def __str__(self):
        return "No violations in puzzle" 

def get_constant_constraints(puzz):
    grid_keys = puzz.get_grid_keys()

    valid_constraints = [GridIsValid(key) for key in grid_keys]
    complete_constraints = [GridIsComplete(key) for key in grid_keys]
    violations = NoViolations()

    return valid_constraints + complete_constraints + [violations]


def get_duplicates(hint):
        try:
            rule = list(hint.keys())[0]
        except:
            print(hint)
            raise Exception("Getting rule failed")
        
        terms = hint[rule]
       
        if rule == "is":
            part1 = terms[:2]
            part2 = terms[2:]
            return [{"is": part2 + part1}]
            
        elif rule == "not":
            return [{"not": get_duplicates(terms[0])[0]}]
            
        elif rule == "before":
            return []
           
        elif rule == "simple_or":
            part1 = terms[:2]
            part2 = terms[2:4]
            return [{"simple_or": part2 + part1 + terms[4:]}]
            
        elif rule == "compound_or":
            possible1 = [terms[0], get_duplicates(terms[0])]
            possible2 = [terms[1], get_duplicates(terms[1])]

            all_combos = [] 
            for pos1 in possible1:
                for pos2 in possible2:
                    all_combos.append({"compound_or": [pos1] + [pos2]})
                    all_combos.append({"compound_or": [pos2] + [pos1]})
            return all_combos


## Variable constraints 
def str_hint(hint, str_so_far=""):
    if isinstance(hint, dict):
        rule = list(hint.keys())[0]
        str_so_far += rule + ": "
        return str_hint(hint[rule], str_so_far)
    elif isinstance(hint, list):
        str_so_far += "[ "
        for i, term in enumerate(hint):
            str_so_far += str_hint(term)
            if i != len(hint) - 1:
                str_so_far += ", "
        str_so_far += " ]"
    else:
        str_so_far += str(hint)
    return str_so_far

class HasHint(Constraint):
    def __init__(self, hint):

        self.hint = hint 
        self.duplicates = [hint] + get_duplicates(hint)

    def _has_hint(self, ind, hint):
        hint = str_hint(hint)
        all_hints = [str_hint(h) for h in ind.hints]

        return hint in all_hints
    
    
    def apply(self, indv):
        has_hint = False 
        for hint in self.duplicates:
            if not has_hint: 
                has_hint = self._has_hint(indv, hint)
        
        return has_hint 

    def __str__(self):
        return "Has Hint: " + str_hint(self.hint)

def random_constraint(puzzle):
    return HasHint(generate_hint(puzzle))

def constraint_in_ind(ind):
    hint = random.choice(ind.hints)

    return HasHint(hint)


def is_contradictory(puzzle, constraints): 
    hintList = [con.hint for con in constraints if isinstance(con, HasHint)]
    completed_puzzle, valid, loops,solver_insights = puzzle.apply_hints(hintList)
    return valid 