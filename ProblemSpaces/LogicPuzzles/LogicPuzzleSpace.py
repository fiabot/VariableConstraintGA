import sys
import os 
from pathlib import Path
import math 
import json 

sys.path.append(str(Path.cwd().parent.parent)) 
sys.path.append(str(Path.cwd().parent)) 
sys.path.append(str(Path.cwd())) 
from ProblemSpaceInterface import ProblemSpace, Constraint
try: 
    from LogicPuzzle import Puzzle, Category
    from HintGrammar import HintSet, generate_hint
    from Constraints import get_constant_constraints, random_constraint, constraint_in_ind, is_contradictory, HasHint
    from HintToEnglish import hint_to_english, serialized_hint_grammar, deserialized_hint_grammar
    from examples import examples 
except: 
    from ProblemSpaces.LogicPuzzles.LogicPuzzle import Puzzle, Category
    from ProblemSpaces.LogicPuzzles.HintGrammar import HintSet, generate_hint
    from ProblemSpaces.LogicPuzzles.Constraints import get_constant_constraints, random_constraint, constraint_in_ind, is_contradictory, HasHint
    from ProblemSpaces.LogicPuzzles.HintToEnglish import hint_to_english, serialized_hint_grammar, deserialized_hint_grammar
    from ProblemSpaces.LogicPuzzles.examples import examples 
import random 

order = Category("order", ["1st", "2nd", "3rd", "4th"], True)
method = Category("method", ["whole", "halved", "chopped", "mashed"], False)
ingredient = Category(
    "ingredient", ["Potatoes", "Carrots", "Mushrooms", "Onions"], False
)

SOUP_PUZZLE = Puzzle([order, method, ingredient])

def make_puzzle(data):
 
    categories = []
    if "categories" in data:
        for element in data["categories"]:
            name = element["name"]
            entities = element["entities"]
            is_numeric = element["is_numeric"]
            category = Category(name, entities, is_numeric)
            categories.append(category)
        puzzle = Puzzle(categories)
        return puzzle
    else:
        return SOUP_PUZZLE

def category_to_json(cat):
    di = {}
    di["name"] = cat.title 
    di["entities"] = cat.entities 
    di["is_numeric"] = cat.is_numeric
    return di 

class LogicPuzzleSpace (ProblemSpace):
    def __init__(self, basePuzzle = None): 
        if basePuzzle is None:
            basePuzzle = SOUP_PUZZLE
        self.basePuzzle = basePuzzle 
    
    def generate_random_individual(self):
        '''
        Return a random in individual in the problem space 
        for initialization 
        '''
        num = random.randint(1, 5)
        hints = [generate_hint(self.basePuzzle) for i in range(num)]
        return HintSet(hints, self.basePuzzle)

    def mutate(self, individual, mutation_rate):
        '''
        Take in an individual and return a mutation

        Amount of mutation can vary between 0 and 1 from mutation rate 
        e.g. each bit has a X% chance of flipping 

        Should NOT modify starting individual 
        '''
        return individual.mutate(mutation_rate)

    def cross_over(self, ind1, ind2):
        """
        Take in two individuals and return a random combination of the two

        Should NOT modify the starting individuals  

        """
        return ind1.cross_over(ind2)  
    
    def fitness(self, individual): 
        """
        Fitness value of an individual. Should be expresses as a maximization function 
        """
        return 15 - min(individual.hint_size(),15)
    
    def get_num_bins(self):
        """
        Return the number of bins of the diversity measure 
        """
        return 8 
    
    def place_in_bin(self, ind):
        """
        Return an index between 0 and num_bins - 1 
        for which bin the individual should be placed 
        """
        return min(ind.solver_loops() - 1, 7)

    def get_constant_constraints(self):
        """
        Return a list of constraints that 
        all individuals must obey

        These constraints should be ATOMIC rather then general 
        """
        return get_constant_constraints(self.basePuzzle) 
    
    def get_initial_variable_constraints(self):
     
        return [] 
    
    def is_contradictory(self, constraints):
        return is_contradictory(self.basePuzzle, constraints) 
    
    def get_rand_constraint(self):
        return random_constraint(self.basePuzzle)
    
    def get_ind_constraint(self, ind):
        return constraint_in_ind(ind)
    
    def to_json(self, ind, data = {},database={}):
        """
        Return a dictionary 
        that represents an individual 
        that can be passed through https 
        """

        di = {}
        di["solution"] = ind.completed_puzzle.print_grid_small()
        di["categories"] = [
            category_to_json(cat) for cat in ind.completed_puzzle.categories
        ]
        di["hints"] = [
            hint_to_english(hint, grammar_dict=database) for hint in ind.hints
        ]
        di["hint_grammar"] = [serialized_hint_grammar(hint) for hint in ind.hints]
    
        if "name" in data:
            di["name"] = data["name"]
        if "scenario" in data:
            di["scenario"] = data["scenario"]
        return di
    
    def json_to_constraint(self, json):
        """
        Takes a json representing a constraint 
        and return a constraint object 
        """
        grammar = deserialized_hint_grammar(json, self.basePuzzle.categories)
        if grammar is None:
            return None 
        return HasHint(grammar)
    
    def get_examples(self):
        """
        Provide examples of scenarios for this enviroment 
        """
        return examples["examples"] 

    