from itertools import combinations 

import random
from copy import deepcopy
from enum import Enum
from Insights import Insight 

###### HELPER FUNCTIONS ####### 
def cross_out(puzzle, cat1, cat2, ent1, ent2):
    """
    places Xs in the all the rows and columns
    after you found a correct hint
    """
    is_valid = True

    # x out the cross sections
    for ent in cat1.entities:
        if ent != ent1:
            symb = puzzle.get_symbol(cat1, cat2, ent, ent2)
            if symb == "*":
                puzzle.answer(cat1, cat2, ent, ent2, "X")
            elif symb == "O":
                is_valid = False

    for ent in cat2.entities:
        if ent != ent2:
            symb = puzzle.get_symbol(cat1, cat2, ent1, ent)
            if symb == "*":
                puzzle.answer(cat1, cat2, ent1, ent, "X")
            elif symb == "O":
                is_valid = False

    return is_valid


def apply_is(puzzle, terms, forbidden_insights=set(), return_entities = False):
    """
    Apply the is rule to puzzle, will always complete in one step
    puzzle: the current state of the grid
    terms: the terms making up the is hint's grammar
    return: applied, is_valid, complete
    """
    applied = False
    is_valid = True
    complete = False  
    insights = set()
    cat1 = terms[0]
    ent1 = terms[1]
    cat2 = terms[2]
    ent2 = terms[3]

    entities = []

    current_term = puzzle.get_symbol(cat1, cat2, ent1, ent2)

    if current_term == "*" and Insight.APPLY_IS not in forbidden_insights:
        applied = True
        complete = True
        puzzle.answer(cat1, cat2, ent1, ent2, "O")
        is_valid = cross_out(puzzle, cat1, cat2, ent1, ent2)
        if is_valid:
            insights.add(Insight.APPLY_IS)
            entities.append({"type": "is", "ents":((cat1.title, ent1), (cat2.title, ent2))})

    elif current_term == "X":
        # something logic error occured
        is_valid = False
        complete = True

    elif current_term == "O":
        # someone already answered
        complete = True
    if return_entities:
        return applied, is_valid, complete, insights, entities 
    return applied, is_valid, complete, insights


class Category:
    def __init__(self, title, entities, is_numeric, increment=1):
        self.title = title
        self.entities = entities
        self.is_numeric = is_numeric
        self.increment = increment

    def __str__(self):
        return self.title

def apply_not(puzzle, terms, forbidden_insights=set(), return_entities=False):
    """
    Apply the not rule to puzzle, will always complete in one step
    puzzle: the current state of the grid
    terms: the terms making up the is hint's grammar
    return: applied, is_valid, complete
    """
    applied = False
    is_valid = True
    complete = False  
    insights = set()
    cat1 = terms[0]
    ent1 = terms[1]
    cat2 = terms[2]
    ent2 = terms[3]
    entities = [] 

    current_term = puzzle.get_symbol(cat1, cat2, ent1, ent2)

    if current_term == "*" and Insight.APPLY_NOT not in forbidden_insights:
        puzzle.answer(cat1, cat2, ent1, ent2, "X")
        applied = True
        complete = True
        insights.add(Insight.APPLY_NOT)
        entities.append({"type": "not", "ents": ((cat1.title, ent1), (cat2.title, ent2))})
    elif current_term == "O":
        is_valid = False
        complete = True
    elif current_term == "X":
        complete = True
        
    if return_entities:
        return applied, is_valid, complete, insights, entities
    return applied, is_valid, complete, insights

def find_openings(puzzle, slow=True, return_entities=False, forbidden_insights=set()):
    applied = False
    complete = False
    is_valid = True
    insights = set()
    entities = []
    # The puzzle to update. Update in place in normal mode; in slow mode update a copy.
    update_puzzle = puzzle
    if slow:
        update_puzzle = deepcopy(puzzle)

    # For every combination of categories:
    for cat1 in puzzle.categories:
        for cat2 in puzzle.categories:
            grid = puzzle.get_grid(cat1, cat2)
            if grid != None:
                # For each row:
                for i, row in enumerate(grid):
                    blanks = [i for i in range(len(row)) if row[i] == "*"]
                    os = [i for i in range(len(row)) if row[i] == "O"]
                    if len(blanks) == 0 and len(os) == 0:
                        # The row is all Xs; contradiction
                        is_valid = False
                        applied = False
                        return applied, is_valid, complete, insights
                    if len(os) > 1:
                        # There are multiple Os; this is a contradiction
                        is_valid = False
                        applied = False
                        return applied, is_valid, complete, insights
                    if (
                        len(os) == 1
                        and len(blanks) >= 1
                        and Insight.CROSS_OUT not in forbidden_insights
                    ):
                        # There is an O; the rest of the row and column can be crossed out.
                        ent1 = cat1.entities[os[0]]
                        ent2 = cat2.entities[i]
                        applied = True
                        is_valid = cross_out(update_puzzle, cat1, cat2, ent1, ent2)
                        if not is_valid:
                            applied = False
                            return applied, is_valid, complete, insights
                        insights.add(Insight.CROSS_OUT)
                    # If there is only 1 blank value:
                    elif len(blanks) == 1 and Insight.OPENING not in forbidden_insights:
                        ent1 = cat1.entities[blanks[0]]
                        ent2 = cat2.entities[i]
                        applied = True
                        # Answer it as 0.
                        update_puzzle.answer(cat1, cat2, ent1, ent2, "O")
                        is_valid = cross_out(update_puzzle, cat1, cat2, ent1, ent2)
                        if not is_valid:
                            applied = False
                            return applied, is_valid, complete, insights
                        insights.add(Insight.OPENING)
                # For each column:
                for j in range(len(grid[0])):
                    blanks = [i for i in range(len(grid)) if grid[i][j] == "*"]
                    os = [i for i in range(len(grid)) if grid[i][j] == "O"]
                    if len(blanks) == 0 and len(os) == 0:
                        # The row is all Xs; contradiction
                        is_valid = False
                        applied = False
                        return applied, is_valid, complete, insights
                    if len(os) > 1:
                        # There are multiple Os; this is a contradiction
                        is_valid = False
                        applied = False
                        return applied, is_valid, complete, insights
                    if (
                        len(os) == 1
                        and len(blanks) >= 1
                        and Insight.CROSS_OUT not in forbidden_insights
                    ):
                        # There is an O; the rest of the row and column can be crossed out.
                        ent1 = cat1.entities[j]
                        ent2 = cat2.entities[os[0]]
                        applied = True
                        is_valid = cross_out(update_puzzle, cat1, cat2, ent1, ent2)
                        entities.append({"type":"cross_out", "ents":[(cat1.title, ent1), (cat2.title, ent2)]})
                        if not is_valid:
                            applied = False
                            return applied, is_valid, complete, insights
                        insights.add(Insight.CROSS_OUT)
                    # If there is only one blank value:
                    elif len(blanks) == 1 and Insight.OPENING not in forbidden_insights:
                        ent1 = cat1.entities[j]
                        ent2 = cat2.entities[blanks[0]]
                        applied = True
                        # Answer it as 0.
                        update_puzzle.answer(cat1, cat2, ent1, ent2, "O")
                        entities.append({"type":"opening", "ents":[(cat1.title, ent1), (cat2.title, ent2)]})
                        is_valid = cross_out(update_puzzle, cat1, cat2, ent1, ent2)
                        if not is_valid:
                            applied = False
                            return applied, is_valid, complete, insights
                        insights.add(Insight.OPENING)
    # Apply updates.
    puzzle.grids = update_puzzle.grids
    if return_entities:
        return applied, is_valid, complete, insights, entities
    return applied, is_valid, complete, insights

def find_transitives(puzzle, forbidden_insights=set(), slow=False, return_entities = False):
    """
    slow: set to True to apply only the first valid insight.
    """
    applied = False
    complete = False
    is_valid = True
    insights = set()
    entities = [] 

    # For every pair of related entities:
    #   If A == B and B == C then A != C
    #   If A == B and B == C then A != C
    for catA in puzzle.categories:
        for entA in catA.entities:
            # All known relations for A
            entA_relations = puzzle.get_known_relations(catA, entA)

            # For each category for which A has relations
            for catB, catB_relations in entA_relations.items():

                # For A's truth value in catB, A and B share all relations
                entB = catB_relations["true"]
                if entB != None:
                    # A is related to B, so A and B share relations for all other categories
                    # Get all realations for B
                    entB_relations = puzzle.get_known_relations(catB, entB)

                    # Relate A to B's truth and false values.
                    for catC, catC_relations in entB_relations.items():
                        entC = catC_relations["true"]
                        if entC != None and entC != entA:
                            # A -> B and B -> C, so A -> C
                            sy = puzzle.get_symbol(catA, catC, entA, entC)
                            if (
                                sy == "*"
                                and Insight.TRANS_ABC_TRUE not in forbidden_insights
                            ):
                                insights.add(Insight.TRANS_ABC_TRUE)
                                applied = True
                                puzzle.answer(catA, catC, entA, entC, "O")
                                entities.append({"type":"abc_true", "ents": ((catA.title, entA), (catB.title, entB), (catC.title, entC))})
                                is_valid = cross_out(puzzle, catA, catC, entA, entC)
                                if not is_valid or slow:
                                    return applied, is_valid, complete, insights
                            elif sy == "X":
                                # Can't link A to C
                                is_valid = False
                                return applied, is_valid, complete, insights
                        # For all false values for B in category C
                        for entC in catC_relations["false"]:
                            # A -> B and B !> C, so A !> C
                            sy = puzzle.get_symbol(catA, catC, entA, entC)
                            if (
                                sy == "*"
                                and Insight.TRANS_ABC_FALSE not in forbidden_insights
                            ):
                                insights.add(Insight.TRANS_ABC_FALSE)
                                applied = True
                                puzzle.answer(catA, catC, entA, entC, "X")
                                entities.append({"type":"abc_false", "ents": ((catA.title, entA), (catB.title, entB), (catC.title, entC))})
                                if slow:
                                    return applied, is_valid, complete, insights
                            elif sy == "O":
                                # Can't reject A to C
                                is_valid = False
                                return applied, is_valid, complete, insights

    # For every pair of entities:
    #   If A and B don't share any possible values for category C, then A != B
    # This loop is separate to enforce that harder insights are only used when the easier insights have been exhausted.
    for catA in puzzle.categories:
        for entA in catA.entities:
            # All known relations for A
            entA_relations = puzzle.get_known_relations(catA, entA)

            # For each category for which A has relations
            for catB, catB_relations in entA_relations.items():
                # for A's indeterminate values in category B, if A and B can't be related in some category, then A != B
                for entB in catB_relations["nil"]:
                    # All relations for B
                    entB_relations = puzzle.get_known_relations(catB, entB)
                    for catC, catCA_relations in entA_relations.items():
                        if catC not in [catA, catB]:
                            # catCA_relations are A's relations for category C.
                            # catCB_relations are B's relations for category C.
                            catCB_relations = entB_relations[catC]

                            A_possibles = catCA_relations["nil"].copy()
                            B_possibles = catCB_relations["nil"].copy()

                            entCA = catCA_relations["true"]
                            entCB = catCB_relations["true"]
                            if entCA != None:
                                A_possibles.append(entCA)
                            if entCB != None:
                                B_possibles.append(entCB)

                            # Now possibles include all positive or nil values for category C
                            # If A and B don't share any entities in their possible lists, then A != B
                            setA = set(A_possibles)
                            setB = set(B_possibles)
                            if (
                                not (setA & setB)
                                and Insight.TRANS_SETS not in forbidden_insights
                            ):
                                # A and B don't share any possibilities; A != B
                                sy = puzzle.get_symbol(catA, catB, entA, entB)
                                if sy == "O":
                                    is_valid = False
                                    return applied, is_valid, complete, insights
                                elif sy == "*":
                                    insights.add(Insight.TRANS_SETS)
                                    applied = True
                                    puzzle.answer(catA, catB, entA, entB, "X")
                                    entities.append({"type":"trans_set", "ents": ((catA.title, entA), (catB.title, entB), (catC.title))})
                                    if slow:
                                        return applied, is_valid, complete, insights
    if return_entities:
        return applied, is_valid, complete, insights, entities
    
    return applied, is_valid, complete, insights


def apply_before(puzzle, terms, forbidden_insights=set(), slow=False, return_entities=False):
    """
    apply the before rule to the puzzle
    puzzle: the current state of the grid
    terms: the terms making up the is hint's grammar
    slow: set to True to apply only the first insight
    return: applied, is_valid, complete
    """
    applied = False
    complete = False
    is_valid = True
    insights = set()
    numbered = len(terms) == 6

    bef_cat = terms[0]
    bef_ent = terms[1]  # bef entity is before aft_ent
    aft_cat = terms[2]
    aft_ent = terms[3]

    num_cat = terms[4]
    entities = [] 

    num = 1
    if numbered:
        num = terms[5]

    # If A < B and A, B are not in the same category, then A is not B.
    if bef_cat != aft_cat:
        sy = puzzle.get_symbol(bef_cat, aft_cat, bef_ent, aft_ent)
        if sy == "*" and Insight.BEFORE_DIFF_CAT not in forbidden_insights:
            insights.add(Insight.BEFORE_DIFF_CAT)
            applied = True
            puzzle.answer(bef_cat, aft_cat, bef_ent, aft_ent, "X")
            entities.append({"type": "before_diff_cat", "ents":((bef_cat.title, bef_ent), (aft_cat.title, aft_ent))})
            if slow:
                if return_entities: 
                    return applied, is_valid, complete, insights, entities 
                return applied, is_valid, complete, insights
        elif sy == "O":
            # Contradiction
            complete = True
            is_valid = False
            return applied, is_valid, complete, insights

    # Get all the current symbols for the two entities in the num category
    before_symbols = [
        puzzle.get_symbol(bef_cat, num_cat, bef_ent, ent) for ent in num_cat.entities
    ]
    after_symbols = [
        puzzle.get_symbol(aft_cat, num_cat, aft_ent, ent) for ent in num_cat.entities
    ]

    # if both entities have answer, we can determine if this rule is valid
    if "O" in before_symbols and "O" in after_symbols:
        applied = False
        complete = True
        if numbered:
            is_valid = after_symbols.index("O") - before_symbols.index("O") == num
        else:
            is_valid = before_symbols.index("O") < after_symbols.index("O")
        return applied, is_valid, complete, insights

    # determine the possible after entities if the before entity is solved
    if "O" in before_symbols:
        bef_index = before_symbols.index("O")
        if numbered:
            if (
                bef_index + num < len(after_symbols)
                and after_symbols[bef_index + num] == "*"
            ):
                pos_aft_index = [bef_index + num]
            else:
                pos_aft_index = []
        else:
            pos_aft_index = [
                i
                for i in list(range(bef_index, len(after_symbols)))
                if after_symbols[i] == "*"
            ]
        if len(pos_aft_index) == 0:
            complete = True
            is_valid = False
            return applied, is_valid, complete, insights
        elif len(pos_aft_index) == 1:
            needed_insight = None
            if numbered:
                if num == 1:
                    needed_insight = Insight.APPLY_BEFORE_ONE_SPOT
                else:
                    needed_insight = Insight.APPLY_BEFORE_N_SPOTS
            else:
                needed_insight = Insight.APPLY_BEFORE_UNDEFINED_SPOTS
            if needed_insight not in forbidden_insights:
                insights.add(needed_insight)
                complete = True
                aft_index = pos_aft_index[0]
                applied = True
                puzzle.answer(
                    aft_cat, num_cat, aft_ent, num_cat.entities[aft_index], "O"
                )
                entities.append({"type": "apply_before", "ents": ((aft_cat.title, aft_ent), (bef_cat.title, bef_ent), (num_cat.title, num_cat.entities[aft_index]))})
                is_valid = cross_out(
                    puzzle, aft_cat, num_cat, aft_ent, num_cat.entities[aft_index]
                )
                if not is_valid or slow:
                    if return_entities: 
                        return applied, is_valid, complete, insights, entities 
                    return applied, is_valid, complete, insights
        else:
            for i in range(0, bef_index):
                sy = puzzle.get_symbol(aft_cat, num_cat, aft_ent, num_cat.entities[i])
                if sy == "*":
                    applied = True
                    puzzle.answer(aft_cat, num_cat, aft_ent, num_cat.entities[i], "X")
                elif sy == "O":
                    complete = True
                    is_valid = False
                    return applied, is_valid, complete, insights
            if applied and slow:
                if return_entities: 
                    return applied, is_valid, complete, insights, entities 
                return applied, is_valid, complete, insights

    # determine the possible before entities if the after entity is solved
    if "O" in after_symbols:
        aft_index = after_symbols.index("O")
        if numbered:
            if aft_index - num >= 0 and before_symbols[aft_index - num] == "*":
                pos_bef_index = [aft_index - num]
            else:
                pos_bef_index = []
        else:
            pos_bef_index = [
                i for i in list(range(0, aft_index)) if before_symbols[i] == "*"
            ]

        if len(pos_bef_index) == 0:
            complete = True
            is_valid = False
            return applied, is_valid, complete, insights
        elif len(pos_bef_index) == 1:
            needed_insight = None
            if numbered:
                if num == 1:
                    needed_insight = Insight.APPLY_BEFORE_ONE_SPOT
                else:
                    needed_insight = Insight.APPLY_BEFORE_N_SPOTS
            else:
                needed_insight = Insight.APPLY_BEFORE_UNDEFINED_SPOTS
            if needed_insight not in forbidden_insights:
               
                insights.add(needed_insight)
                complete = True
                bef_index = pos_bef_index[0]
                applied = True
                entities.append({"type": "apply_before", "ents": ((bef_cat.title, bef_ent), (aft_cat.title, aft_ent), (num_cat.title, num_cat.entities[bef_index]))})
                puzzle.answer(
                    bef_cat, num_cat, bef_ent, num_cat.entities[bef_index], "O"
                )
                is_valid = cross_out(
                    puzzle, bef_cat, num_cat, bef_ent, num_cat.entities[bef_index]
                )
                if not is_valid or slow:
                    return applied, is_valid, complete, insights
        else:
            for i in range(aft_index, len(before_symbols)):
                sy = puzzle.get_symbol(bef_cat, num_cat, bef_ent, num_cat.entities[i])
                if sy == "*":
                    applied = True
                    puzzle.answer(bef_cat, num_cat, bef_ent, num_cat.entities[i], "X")
                elif sy == "O":
                    complete = True
                    is_valid = False
                    return applied, is_valid, complete, insights
            if applied and slow:
                if return_entities: 
                    return applied, is_valid, complete, insights, entities 
                return applied, is_valid, complete, insights

    # Narrow down possiblities with no information for entities yet
    # The before entity can't be in the last num spots (or there won't be room for the after entity)
    for i in range(len(before_symbols) - num, len(before_symbols)):
        sy = puzzle.get_symbol(bef_cat, num_cat, bef_ent, num_cat.entities[i])
        needed_insight = Insight.BEFORE_ONE_SPOT_NOINFO
        if num > 1:
            needed_insight = Insight.BEFORE_N_SPOTS_NOINFO
        if sy == "*" and needed_insight not in forbidden_insights:
            insights.add(needed_insight)
            applied = True
            puzzle.answer(bef_cat, num_cat, bef_ent, num_cat.entities[i], "X")
            entities.append({"type": "before_noinfo", "ents":((bef_cat.title, bef_ent), (num_cat.title, num_cat.entities[i]))})
        elif sy == "O":
            complete = True
            is_valid = False
            return applied, is_valid, complete, insights
    # And the inverse is true for the after entity
    for i in range(0, num):
        sy = puzzle.get_symbol(aft_cat, num_cat, aft_ent, num_cat.entities[i])
        needed_insight = Insight.BEFORE_ONE_SPOT_NOINFO
        if num > 1:
            needed_insight = Insight.BEFORE_N_SPOTS_NOINFO
        if sy == "*" and needed_insight not in forbidden_insights:
            insights.add(needed_insight)
            applied = True
            entities.append({"type": "before_noinfo", "ents":((aft_cat.title, aft_ent), (num_cat.title, num_cat.entities[i]))})
            puzzle.answer(aft_cat, num_cat, aft_ent, num_cat.entities[i], "X")
        elif sy == "O":
            complete = True
            is_valid = False
            return applied, is_valid, complete, insights
    if applied and slow:
        if return_entities: 
            return applied, is_valid, complete, insights, entities
        return applied, is_valid, complete, insights

    # Determine possible answers with constraints on either entity
    if "X" in before_symbols or "X" in after_symbols:
        # A streak of Xs at the beginning/end forces the first available position for the other entity to shift.
        for i in range(len(before_symbols) - num):
            if before_symbols[i] != "X":
                break
            sy = puzzle.get_symbol(aft_cat, num_cat, aft_ent, num_cat.entities[i + num])
            if sy == "*" and Insight.BEFORE_N_SPOTS_SHIFT not in forbidden_insights:
                insights.add(Insight.BEFORE_N_SPOTS_SHIFT)
                applied = True
                puzzle.answer(aft_cat, num_cat, aft_ent, num_cat.entities[i + num], "X")
                entities.append({"type": "spots_shift", "ents":((aft_cat.title, aft_ent), (bef_cat.title, bef_ent), (num_cat.title, num_cat.entities[i + num]))})

        for i in range(len(after_symbols) - 1, num - 1, -1):
            if after_symbols[i] != "X":
                break
            sy = puzzle.get_symbol(bef_cat, num_cat, bef_ent, num_cat.entities[i - num])
            if sy == "*" and Insight.BEFORE_N_SPOTS_SHIFT not in forbidden_insights:
                insights.add(Insight.BEFORE_N_SPOTS_SHIFT)
                applied = True
                puzzle.answer(bef_cat, num_cat, bef_ent, num_cat.entities[i - num], "X")
                entities.append({"type": "spots_shift", "ents":((bef_cat.title, bef_ent), (aft_cat.title, aft_ent), (num_cat.title, num_cat.entities[i - num]))})

        if applied and slow:
            if return_entities: 
                return applied, is_valid, complete, insights, entities
            return applied, is_valid, complete, insights

        if numbered:
            # All Xs for the before entity where the index is valid (i+num exists).
            before_Xs = [
                i
                for i in range(len(before_symbols))
                if before_symbols[i] == "X" and i + num < len(before_symbols) - 1
            ]
            # All Xs for the after entity where the index is valid (i-num exists).
            after_Xs = [
                i
                for i in range(len(after_symbols))
                if after_symbols[i] == "X" and i - num > -1
            ]

            # For a position to be a valid answer, the corresponding position +/- num must be valid for the other entity
            for i in before_Xs:
                sy = puzzle.get_symbol(
                    aft_cat, num_cat, aft_ent, num_cat.entities[i + num]
                )
                if sy == "*" and Insight.BEFORE_N_SPOTS_CROSSCHECK not in forbidden_insights:
                    insights.add(Insight.BEFORE_N_SPOTS_CROSSCHECK)
                    applied = True
                    puzzle.answer(
                        aft_cat, num_cat, aft_ent, num_cat.entities[i + num], "X"
                    )
                    entities.append({"type": "spots_cross", "ents":((aft_cat.title, aft_ent),(bef_cat.title, bef_ent), (num_cat.title, num_cat.entities[i + num]))})

            for i in after_Xs:
                sy = puzzle.get_symbol(
                    bef_cat, num_cat, bef_ent, num_cat.entities[i - num]
                )
                if sy == "*" and Insight.BEFORE_N_SPOTS_CROSSCHECK not in forbidden_insights:
                    insights.add(Insight.BEFORE_N_SPOTS_CROSSCHECK)
                    applied = True
                    puzzle.answer(
                        bef_cat, num_cat, bef_ent, num_cat.entities[i - num], "X"
                    )
                    entities.append({"type": "spots_cross", "ents":((bef_cat.title, bef_ent),(aft_cat.title, aft_cat), (num_cat.title, num_cat.entities[i - num]))})

            if applied and slow:
                if return_entities: 
                    return applied, is_valid, complete, insights, entities
                return applied, is_valid, complete, insights
    if return_entities: 
        return applied, is_valid, complete, insights, entities
    return applied, is_valid, complete, insights


def apply_simple_or(puzzle, terms, forbidden_insights=set(), slow=False, return_entities=False):
    """
    Apply the or rule to puzzle, will be incomplete if not enough information is known
    slow: set to True to apply only the first valid insight
    return: applied, is_valid, complete
    """
    applied = False
    is_valid = True
    complete = False
    insights = set()

    pos_cat1 = terms[0]
    pos_ent1 = terms[1]  # either ent1 or ent2 = ans_ent
    pos_cat2 = terms[2]
    pos_ent2 = terms[3]

    ans_cat = terms[4]
    ans_ent = terms[5]
    entities= [] 

    pos_symb1 = puzzle.get_symbol(pos_cat1, ans_cat, pos_ent1, ans_ent)
    pos_symb2 = puzzle.get_symbol(pos_cat2, ans_cat, pos_ent2, ans_ent)

    if pos_symb1 == "*" and pos_symb2 == "*":
        # we can't apply hint yet (don't have enough information)
        complete = False
    elif pos_symb1 == pos_symb2:
        # this rule can't be applied (both are true or both are false)
        complete = True
        is_valid = False
        return applied, is_valid, complete, insights
    elif pos_symb1 == "O":
        # hint says that ent2 cannot be the answer ent
        if pos_symb2 == "*" and Insight.APPLY_OR not in forbidden_insights:
            # we can change game state
            applied = True
            complete = True
            puzzle.answer(pos_cat2, ans_cat, pos_ent2, ans_ent, "X")
            entities.append({"type":"or_false", "ents":((pos_cat2.title, pos_ent2), (pos_cat1.title, pos_ent1), (ans_cat.title, ans_ent))})
            insights.add(Insight.APPLY_OR)
            if return_entities: 
                return applied, is_valid, complete, insights, entities 
            return applied, is_valid, complete, insights
        elif pos_symb2 == "X":
            # game state is correct, but nothing to change
            complete = True
    elif pos_symb1 == "X":
        # hint says that ent2 must be the answer ent
        if pos_symb2 == "*" and Insight.APPLY_OR not in forbidden_insights:
            # we can change the game state
            applied = True
            complete = True
            puzzle.answer(pos_cat2, ans_cat, pos_ent2, ans_ent, "O")
            is_valid = cross_out(puzzle, pos_cat2, ans_cat, pos_ent2, ans_ent)
            insights.add(Insight.APPLY_OR)
            entities.append({"type":"or_true", "ents":((pos_cat2.title, pos_ent2), (pos_cat1.title, pos_ent1), (ans_cat.title, ans_ent))})
            if return_entities: 
                return applied, is_valid, complete, insights, entities 
            return applied, is_valid, complete, insights
        elif pos_symb2 == "O":
            # game state is correct, but we cannot change
            complete = True
    elif pos_symb1 == "*":
        if pos_symb2 == "O" and Insight.APPLY_OR not in forbidden_insights:
            # hint says ent1 is not ans_ent and we can change this
            applied = True
            complete = True
            puzzle.answer(pos_cat1, ans_cat, pos_ent1, ans_ent, "X")
            insights.add(Insight.APPLY_OR)
            entities.append({"type":"or_false", "ents":((pos_cat1.title, pos_ent1), (pos_cat2.title, pos_ent2), (ans_cat.title, ans_ent))})
            if return_entities: 
                return applied, is_valid, complete, insights, entities 
            return applied, is_valid, complete, insights
        elif pos_symb2 == "X" and Insight.APPLY_OR not in forbidden_insights:
            # hint says ent1 is ans_ent and we can change this
            applied = True
            complete = True
            puzzle.answer(pos_cat1, ans_cat, pos_ent1, ans_ent, "O")
            is_valid = cross_out(puzzle, pos_cat1, ans_cat, pos_ent1, ans_ent)
            insights.add(Insight.APPLY_OR)
            entities.append({"type":"or_true", "ents":((pos_cat1.title, pos_ent1), (pos_cat2.title, pos_ent2), (ans_cat.title, ans_ent))})
            if return_entities: 
                return applied, is_valid, complete, insights, entities 
            return applied, is_valid, complete, insights

    if pos_cat1 != pos_cat2:
        if  Insight.SIMPLE_OR_DIFF_CAT not in forbidden_insights:
            # A and B are in different categories
            # If A or B is C then A is not B
            applied, is_valid, _, _ = apply_not(
                puzzle, [pos_cat1, pos_ent1, pos_cat2, pos_ent2]
            )
            if applied:
                insights.add(Insight.SIMPLE_OR_DIFF_CAT)
                entities.append({"type":"or_diff", "ents":((pos_cat1.title, pos_ent1), (pos_cat2.title, pos_ent2), (ans_cat.title, ans_ent))})
            if slow or not is_valid:
                if return_entities: 
                    return applied, is_valid, complete, insights, entities 
                return applied, is_valid, complete, insights
    else:
        # A and B are in the same category
        # If A or B from category 0 is C then no other entity from category 0 is C
        for ent in pos_cat1.entities:
            if ent not in [pos_ent1, pos_ent2]:
                sy = puzzle.get_symbol(pos_cat1, ans_cat, ent, ans_ent)
                if sy == "O":
                    # Logical error.
                    is_valid = False
                    complete = True
                    return applied, is_valid, complete, insights
                elif sy == "*" and Insight.SIMPLE_OR_SAME_CAT not in forbidden_insights:
                    # No other entity from cat1 is ans_ent
                    insights.add(Insight.SIMPLE_OR_SAME_CAT)
                    applied = True
                    puzzle.answer(pos_cat1, ans_cat, ent, ans_ent, "X")
                    entities.append({"type":"or_same", "ents":((pos_cat1.title, ent), (ans_cat.title, ans_ent))})
            
                    
        if applied and slow:
            if return_entities: 
                return applied, is_valid, complete, insights, entities 
            return applied, is_valid, complete, insights
    if return_entities: 
        return applied, is_valid, complete, insights, entities 
    return applied, is_valid, complete, insights

def apply_compound_or(puzzle, options, forbidden_insights = set(), return_entities=False):
    """
    Apply the compound or rule to puzzle, will be incomplete if not enough information is known
    return: applied, is_valid, complete
    """
    applied = False
    complete = False
    is_valid = True
    insights = (
        set()
    )  # There are no insights for compound or, but keep the return signature consistent
    entities = [] 

    optionA = options[0]
    catA1 = optionA[0]
    entA1 = optionA[1]
    catA2 = optionA[2]
    entA2 = optionA[3]
    currentA = puzzle.get_symbol(catA1, catA2, entA1, entA2)

    optionB = options[1]
    catB1 = optionB[0]
    entB1 = optionB[1]
    catB2 = optionB[2]
    entB2 = optionB[3]
    currentB = puzzle.get_symbol(catB1, catB2, entB1, entB2)

    if currentA == currentB:
        if currentA != "*":
            # Both can't be true or false, something has gone wrong.
            is_valid = False
            complete = True
        # There is no info to apply.
        return applied, is_valid, complete, insights

    # At least one term is answered; the hint is guaranteed complete.
    complete = True

    currents = [currentA, currentB]
    if "X" in currents and "O" in currents:
        # Someone already answered.
        return applied, is_valid, complete, insights

    # One is answered and the other is not; we are guaranteed to apply.
    applied = True

    if currentA == "X" and Insight.APPLY_OR not in forbidden_insights:
        puzzle.answer(catB1, catB2, entB1, entB2, "O")
        insights.add(Insight.APPLY_OR)
        is_valid = cross_out(puzzle, catB1, catB2, entB1, entB2)
        entities.append({"type": "or_true", "ents": ((catB1.title, entB1), (catA1.title, entA1), (catB2.title, entB2))})
    elif currentB == "X" and Insight.APPLY_OR not in forbidden_insights:
        puzzle.answer(catA1, catA2, entA1, entA2, "O")
        insights.add(Insight.APPLY_OR)
        entities.append({"type": "or_true", "ents": ((catA1.title, entA1), (catB1.title, entB1), (catA2.title, entA2))})
        is_valid = cross_out(puzzle, catA1, catA2, entA1, entA2)
    elif currentA == "O" and Insight.APPLY_OR not in forbidden_insights:
        insights.add(Insight.APPLY_OR)
        entities.append({"type": "or_false", "ents": ((catB1.title, entB1), (catA1.title, entA1), (catB2.title, entB2))})
        puzzle.answer(catB1, catB2, entB1, entB2, "X")
    elif currentB == "O" and Insight.APPLY_OR not in forbidden_insights:
        insights.add(Insight.APPLY_OR)
        puzzle.answer(catA1, catA2, entA1, entA2, "X")
        entities.append({"type": "or_false", "ents": ((catA1.title, entA1), (catB1.title, entB1), (catA2.title, entA2))})
    if return_entities:
        return applied, is_valid, complete, insights, entities
    return applied, is_valid, complete, insights

def apply_hint(puzzle, hint, forbidden_insights=set(), slow=False, return_entities=False):
    """
    Given a hint dictionary and a puzzle, apply next step of the hint to the puzzle

    forbidden_insights: insights the solution can't use
    slow: set to True to apply only the first insight for the hint
    return:
     applied  = whether the hint changed the state
     is_valid = whether the hint contradicts the current state
     complete = whether the hint has no more information to offer
     contradiction = the contradiction if the hint is invalid
     insights = the insights required for the move
    """

    applied = False
    complete = False
    is_valid = True
    insights = set()
    entities = [] 

    rule = list(hint.keys())[0]
    terms = hint[rule]
    if rule == "simple_hint":
        rule = list(hint.keys())[0]
    if rule == "is":
        return apply_is(puzzle, terms, forbidden_insights=forbidden_insights, return_entities=return_entities)
    elif rule == "not":
        return apply_not(puzzle, terms[0]["is"], forbidden_insights=forbidden_insights, return_entities=return_entities)
    elif rule == "before":
        return apply_before(
            puzzle, terms, forbidden_insights=forbidden_insights, slow=slow, return_entities=return_entities
        )
    elif rule == "simple_or":
        return apply_simple_or(
            puzzle, terms, forbidden_insights=forbidden_insights, slow=slow, return_entities=return_entities
        )
    elif rule == "compound_or":
        return apply_compound_or(puzzle, [terms[0]["is"], terms[1]["is"]], forbidden_insights=forbidden_insights, return_entities=return_entities)
    else:
        print(
            "This hint has no apply rules! Something has gone horribly wrong. The offending hint: "
        
        )

    return applied, is_valid, complete, insights

def apply_hints(puzzle, hints, forbidden_insights=set()):
    """
    solver
    """
    is_valid = True
    copy = Puzzle(puzzle.categories)
    queue = hints[:]
    # trace = {}
    backlog = []
    applied = True
    insights = set()
    loop = 0
    if len(hints) == 0:
        is_valid = False
        return copy, is_valid, loop, insights
    while is_valid and applied and len(queue) > 0:
        applied = False
        loop += 1

        for hint in queue:
            og = deepcopy(copy)
            a, is_valid, complete, hint_insights = apply_hint(
                copy, hint, forbidden_insights=forbidden_insights
            )
            applied = applied or a
            insights = insights | hint_insights
            if not complete:
                backlog.append(hint)

            if not is_valid:
                return copy, is_valid, loop, insights

            # Apply additional logic
            if a:
                a_2 = True
                a_3 = True
                while a_2 or a_3:
                    # Apply openings and transitives as many times as you can.
                    a_2, is_valid, complete, opening_insights = find_openings(
                        copy, forbidden_insights=forbidden_insights
                    )
                    if not is_valid:
                        return copy, is_valid, loop, insights
                    a_3, is_valid, complete, trans_insights = find_transitives(
                        copy, forbidden_insights=forbidden_insights
                    )
                    if not is_valid:
                        return copy, is_valid, loop, insights
                    applied = applied or a_2 or a_3  # test if anything was changed
                    hint_insights = hint_insights | trans_insights | opening_insights
                    insights = insights | hint_insights
                if not is_valid:
                    return copy, is_valid, loop, insights
        queue = backlog
        backlog = []

    return copy, is_valid, loop, insights


class Puzzle:
    def __init__(self, categories):
        """
        Set up a blank puzzle

        The set up is a bit goofy but it works

        First determine which entities to put on the top, and which to put down the left

        This can be used to determine how to arrange grids so that each category
        is matched with each other exactly once

        In the dictory every pair of categories is represented as "cat1:cat2"
        where cat1 is the category on the top and cat2 is one the left. The value
        of the diction is a 2d array, such that grid[x][y] represents the symbol
        for the xth entitity in cat2 and the yth entity in cat1.
        """
        self.categories = categories
        self.left_right = self.categories[0 : len(categories) - 1]
        self.top_bottom = []
        for i in range(len(self.categories) - 1, 0, -1):
            self.top_bottom.append(self.categories[i])
        self.grids = {}

        rows = len(self.top_bottom)

        for top_category in self.left_right:
            for i in range(rows):
                left_cat = self.top_bottom[i]
                title = self._to_key(top_category, left_cat)
                array = []
                for i in range(len(left_cat.entities)):
                    array += [["*"] * len(top_category.entities)]
                self.grids[title] = array

            rows -= 1

    def get_category(self, entity):
        """
        return a category where entity
        belong to it
        """
        for cat in self.categories:
            if entity in cat.entites:
                return cat
        return None

    def get_grid(self, cat1, cat2):
        """
        Get the grid for cat1 and cat2
        assuming cat1 is the top category
        """
        if self._to_key(cat1, cat2) in self.grids:
            return self.grids[self._to_key(cat1, cat2)]
        else:
            return None
        
    def get_grid_keys(self):
        return list(self.grids.keys())

    def get_grid_by_key(self, key):
        return self.grids[key]

    def trim_ent(self, ent):
        """
        trim an entity to three character
        to be able to print
        """
        if len(ent) > 3:
            return ent[0:3]
        else:
            return ent

    def _to_key(self, cat1, cat2):
        """
        return a string key for cat1 and cat2
        where cat1 is the top category and cat2
        is the left
        """
        return cat1.title + ":" + cat2.title

    def answer(self, cat1, cat2, ent1, ent2, new_symbol):
        """
        given ent1 in cat1 and ent2 in cat1
        change the symbol in the grid.

        This works regardless of the order of cat1 and cat2
        ex: you don't need to put the top category first
        """
        index1 = cat1.entities.index(ent1)
        index2 = cat2.entities.index(ent2)
        if self._to_key(cat1, cat2) in self.grids:
            grid = self.grids[self._to_key(cat1, cat2)]
            grid[index2][index1] = new_symbol

        elif self._to_key(cat2, cat1) in self.grids:
            grid = self.grids[self._to_key(cat2, cat1)]
            grid[index1][index2] = new_symbol

    def _print_row(self, top_cats, cat2, remove_top=False):
        """
        return a singular row for the puzzle,
        given the columns (top_cats) and the row (cat2)
        should be used internally
        """

        top_ents = []
        for cat in top_cats:
            top_ents += cat.entities

        return_str = ""
        bar = "  " * 2 + "-" * (len(top_ents) * 5) + "\n"
        if not remove_top:
            top_string = " " * 4 + "  "
            top_string += "  ".join([self.trim_ent(ent) for ent in top_ents])
            return_str += top_string + "\n"
            return_str += bar

        grid1 = self.grids[top_cats[0].title + ":" + cat2.title]
        for i in range(len(grid1)):

            left_ent = self.trim_ent(cat2.entities[i]) + "| "
            return_str += left_ent
            for cat in top_cats:
                row = self.grids[cat.title + ":" + cat2.title][i]
                row_str = " " + "    ".join(row) + "  |"
                return_str += row_str
            return_str += "\n"

        return_str += bar

        return return_str

    def _print_row_small(self, top_cats, cat2):
        """
        return a singular row for the puzzle,
        given the columns (top_cats) and the row (cat2)
        should be used internally
        """

        top_ents = []
        for cat in top_cats:
            top_ents += cat.entities

        return_str = ""
        bar = "-" * (len(top_ents) + len(top_cats) + 1) + "\n"
        return_str += bar

        grid1 = self.grids[top_cats[0].title + ":" + cat2.title]
        for i in range(len(grid1)):

            left_ent = "|"
            return_str += left_ent
            for cat in top_cats:
                row = self.grids[cat.title + ":" + cat2.title][i]
                row_str = "".join(row) + "|"
                return_str += row_str
            return_str += "\n"

        return return_str

    def print_row(self, row, small=False):
        """
        find the top categories and the vertical categories
        for a single row
        """
        left_cat = self.top_bottom[row]
        num_top = len(self.left_right) - row
        if not small:
            remove_top = row > 0
            return self._print_row(self.left_right[0:num_top], left_cat, remove_top)
        else:
            return self._print_row_small(self.left_right[0:num_top], left_cat)

    def print_grid(self):
        """
        return the entire puzzle string
        """
        return_str = ""
        for i in range(len(self.top_bottom)):
            return_str += self.print_row(i)

        return return_str

    def print_grid_small(self):
        """
        return the entire puzzle string
        """
        return_str = ""
        for i in range(len(self.top_bottom)):
            return_str += self.print_row(i, True)

        return return_str

    def grid_is_valid(self, grid):
        """
        Check that there are one or less "O"s
        for each row and column in a grid
        """
        # check rows
        rows_valid = [row.count("O") <= 1 for row in grid]
        if False in rows_valid:
            return False

        # check columns
        for i in range(len(grid[0])):
            c = 0
            for row in grid:
                if row[i] == "O":
                    c += 1
            if c > 1:
                return False

        return True

    def grid_is_complete(self, grid):
        """
           Check that there is exactly 1 "O"s
        for each row and column in a grid
        """
        # check rows
        rows_valid = [row.count("O") == 1 for row in grid]
        if False in rows_valid:
            return False

        # check columns
        for i in range(len(grid[0])):
            c = 0
            for row in grid:
                if row[i] == "O":
                    c += 1
            if c != 1:
                return False

        return True

    def cats_is_valid(self, cat1, cat2):
        """
        Return true if there is at most 1 "O"
        in each row and column
        """
        if self._to_key(cat1, cat2) in self.grids:
            grid = self.grids[self._to_key(cat1, cat2)]
        elif self._to_key(cat2, cat1) in self.grids:
            grid = self.grids[self._to_key(cat2, cat1)]

        return self._grid_is_valid(grid)

    def find_truths(self, category, ent):
        """
        return an dictionary where the
        keys are category names where the
        value of the entity is know, and the values
        are which entity in that category "ent" is
        connected to
        """
        truths = {}
        index = category.entities.index(ent)

        for cat2 in self.categories:
            if cat2 != category:
                if self._to_key(category, cat2) in self.grids:
                    grid = self.grids[self._to_key(category, cat2)]
                    answers = [grid[i][index] for i in range(len(grid))]

                elif self._to_key(cat2, category) in self.grids:
                    grid = self.grids[self._to_key(cat2, category)]
                    answers = grid[index]

                if "O" in answers:
                    truths[cat2.title] = cat2.entities[answers.index("O")]

        return truths

    def get_known_relations(self, category, ent):
        """
        return {
          category: {
            true: connected entity
            false: []not connected entities
            nil: []entities that are undetermined
          }
        }
        """
        relations = {}
        index = category.entities.index(ent)

        for cat2 in self.categories:
            relations[cat2] = {
                "true": None,
                "false": [],
                "nil": [],
            }
            if cat2 != category:
                if self._to_key(category, cat2) in self.grids:
                    grid = self.grids[self._to_key(category, cat2)]
                    answers = [grid[i][index] for i in range(len(grid))]

                elif self._to_key(cat2, category) in self.grids:
                    grid = self.grids[self._to_key(cat2, category)]
                    answers = grid[index]
                else:
                    print("SOMETHING HAS GONE HORRIBLY WRONG")
                    print(type(category))
                    print(category)
                    print("\n")
                    print(type(cat2))
                    print(cat2)

                    print("\n")
                    print(self.grids)
         

                for i, val in enumerate(answers):
                    if val == "O":
                        relations[cat2]["true"] = cat2.entities[i]
                    elif val == "X":
                        relations[cat2]["false"].append(cat2.entities[i])
                    else:
                        relations[cat2]["nil"].append(cat2.entities[i])

        return relations

    def get_symbol(self, cat1, cat2, ent1, ent2):
        """
        return the symbol at ent1 and ent2
        """
        index1 = cat1.entities.index(ent1)
        index2 = cat2.entities.index(ent2)
        if self._to_key(cat1, cat2) in self.grids:
            grid = self.grids[self._to_key(cat1, cat2)]
            return grid[index2][index1]

        elif self._to_key(cat2, cat1) in self.grids:
            grid = self.grids[self._to_key(cat2, cat1)]
            return grid[index1][index2]

    def get_category(self, title):
        """
        get category object from title
        """
        titles = [cat.title for cat in self.categories]

        return self.categories[titles.index(title)]

    def _all_ents(self):
        """
        return a nested list
        with all categories and their
        entities
        """
        ents = []
        for cat in self.categories:
            for ent in cat.entities:
                ents.append([cat, ent])

        return ents

    def num_violations(self):
        """
        Return the number of truth violations
        in the puzzle
        """
        violations = 0
        count = 0
        for cat, ent in self._all_ents():
            truths = self.find_truths(cat, ent)
            if len(truths) >= 2:
                pairs = list(combinations(truths.keys(), 2))
                count += len(pairs)
                for first, second in pairs:

                    # if these two entites are in the truth of ent
                    # then they should also be true
                    cat1 = self.get_category(first)
                    cat2 = self.get_category(second)
                    ent1 = truths[first]
                    ent2 = truths[second]

                    # The symbol should be "O" or empty ("*")
                    if self.get_symbol(cat1, cat2, ent1, ent2) == "X":
                        violations += 1

                    # make sure there is not a truth somewhere else
                    truths1 = self.find_truths(cat1, ent1)
                    if cat2.title in truths1 and truths1[cat2.title] != ent2:
                        violations += 1
                    truths2 = self.find_truths(cat2, ent2)
                    if cat1.title in truths2 and truths2[cat1.title] != ent1:
                        violations += 1
        return violations

    def _truths_valid(self):
        """
        Make sure there is not violations in
        truths of each entity

        There is absoluely a more efficent way to do this
        """
        for cat, ent in self._all_ents():
            truths = self.find_truths(cat, ent)
            if len(truths) >= 2:
                pairs = combinations(truths.keys(), 2)
                for first, second in pairs:

                    # if these two entites are in the truth of ent
                    # then they should also be true
                    cat1 = self.get_category(first)
                    cat2 = self.get_category(second)
                    ent1 = truths[first]
                    ent2 = truths[second]

                    # The symbol should be "O" or empty ("*")
                    if self.get_symbol(cat1, cat2, ent1, ent2) == "X":
                        return False

                    # make sure there is not a truth somehwere else
                    truths1 = self.find_truths(cat1, ent1)
                    if cat2.title in truths1 and truths1[cat2.title] != ent2:
                        return False

                    truths2 = self.find_truths(cat2, ent2)
                    if cat1.title in truths2 and truths2[cat1.title] != ent1:
                        return False
        return True

    def is_valid(self):
        """
        return true of there there is at
        most 1 "O" for each column and row

        and if there are no truth violaitons
        """
        # make sure there is at most 1 truth
        # in each row and column
        for grid in self.grids.values():
            if not self._grid_is_valid(grid):
                return False

        # make sure truths have no violations
        return self._truths_valid()

    def is_complete(self):
        """
        return true if there is exactly 1 "O"
        in each row and column

        and there are no truth violations
        """
        if self.is_valid():
            for grid in self.grids.values():
                if not self._grid_is_complete(grid):
                    return False

            return True
        else:
            return False

    def _per_complete_grid(self, grid):
        s = 0
        v = 0  # amount of rows with exactly 1 "O"
        l = 0
        for row in grid:
            s += row.count("X") + row.count("O")
            if (row.count("O")) == 1:
                v += 1
            l += len(row)
        return s / l, v / (len(grid))

    def percent_complete(self):
        """
        return the ratio of cells that
        have an "X" or "O"
        """
        grid_sums = 0
        grid_len = 0
        valid_sums = 0
        for grid in self.grids.values():
            s, valid = self._per_complete_grid(grid)
            grid_sums += s
            valid_sums += valid
            grid_len += 1
        return grid_sums / grid_len, valid_sums / grid_len

    def apply_hints(self, hints, forbidden_insights = set()):
        """
        Return a copy of the puzzle
        here all hints in a list are
        applied
        Starts with a blank verison
        of the puzzle (i.e. does not copy grids)
        """
        return apply_hints(self, hints, forbidden_insights)

