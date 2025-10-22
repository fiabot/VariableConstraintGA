from enum import Enum

class Insight(Enum):
    NO_INSIGHT = 0
    CROSS_OUT = (
        1  # If there is an O in a row/column, the rest of the row/column must be X
    )
    OPENING = 2  # If a row/column has one opening and the rest are Xs, it must be O
    APPLY_IS = 3  # Apply an is hint
    APPLY_NOT = 4  # Apply a not hint
    APPLY_OR = 5  # Apply an or hint once one of the clauses has been answered.
    APPLY_BEFORE_ONE_SPOT = (
        6  # If A is answered and B is 1 after A, then answer B is one after A
    )
    APPLY_BEFORE_N_SPOTS = (
        7  # If A is answered and B is N after A, then answer B is N after A
    )
    APPLY_BEFORE_UNDEFINED_SPOTS = (
        8  # If A is answered then B must be one of the spots after A
    )
    SIMPLE_OR_SAME_CAT = (
        9  # If A or B from category 0 is C then no other entity from category 0 is C
    )
    SIMPLE_OR_DIFF_CAT = 10  # If A or B is C then A is not B
    BEFORE_DIFF_CAT = (
        11  # If A < B and A, B are not in the same category, then A is not B.
    )
    BEFORE_ONE_SPOT_NOINFO = 12  # The before entity can't be in the last spot (and vice versa for the after entity) Same for undefined spots
    BEFORE_N_SPOTS_NOINFO = 13  # The before entity can't be in the last N spots (and vice versa for the after entity)
    TRANS_ABC_TRUE = 14  # A -> B and B -> C, so A -> C
    TRANS_ABC_FALSE = 15  # A -> B and B !> C, so A !> C
    BEFORE_N_SPOTS_SHIFT = 16  # A streak of Xs at the beginning/end forces the first available position for the other entity to shift.
    BEFORE_N_SPOTS_CROSSCHECK = 17  # For a position to be a valid answer, the corresponding position +/- num must be valid for the other entity
    TRANS_SETS = 18  # A and B don't share any possibilities; A != B
    REPAIR = 100  # Repair broken puzzle

ALL_INSIGHTS = {insight for insight in Insight}
