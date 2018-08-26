#Note: Implementation of naked twins strategy and diagonal constraint propagation
# based on Udacity AIND 'Solving a Sudoku using AI' lecture notes

# encoding the board
rows = 'ABCDEFGHI'
cols = '123456789'


# helper function to form a list of all the possible concatenations of a letter s in
# string a with a letter t in string b.
def cross(a, b):
    return [s+t for s in a for t in b]

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
# construct a list of units, where each unit is a list of labels of a diagonal
diag_units = [[r + c for r, c in zip(rows, cols)], [r + c for r, c in zip(rows, cols[::-1])]]
# construct an overall list of all the units above
unitlist = row_units + column_units + square_units + diag_units
# construct a dictionary for unitlist,
# where key is any box and value is a list of all the lists of units that contain that box
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
# construct a dictionary of peers,
# where key is any box and value is a list of all the peers of that box,
# (all the peers from row column and square units)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)

assignments = []


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


""" 'assignments' stores a trail of board changes.
visualize filters these assignments to avoid changes involving no actual board value changes.
Then it's played back in the pygame.
This provides a visual simulation of the game as you make board changes using your algorithm."""


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    for unit in unitlist:  # for each unit (row/column/square/diagonal)
        # create a dictionary 'inv_twin_dict' that inverse maps value to box,
        # i.e., key is the value of that box, and value is the box label
        unit_values = [values[element] for element in unit]
        unit_dict = dict(zip(unit, unit_values))
        inverse_map = {}
        for key, value in unit_dict.items():
            inverse_map.setdefault(value, []).append(key)
        inv_twin_dict = {key: value for key, value in inverse_map.items() if len(value) == 2 and len(key) == 2}

        # create a list of unsolved boxes in that unit
        unsolved_boxes = [key for key in unit_dict.keys() if len(unit_dict[key]) > 1]

        # check the value of any unsolved box (exclude twin boxes)
        # if a digit is in any twin box, delete that digit from the unsolved box value
        for twin_value, twin_box in inv_twin_dict.items():
            for unsolved_box in unsolved_boxes:
                if unsolved_box not in twin_box:
                    for digit in twin_value:
                        # values[unsolved_box] = values[unsolved_box].replace(digit, '')
                        new_value = values[unsolved_box].replace(digit, '')
                        assign_value(values, unsolved_box, new_value)
    return values


def grid_values(grid):
    """Convert grid string into {<box>: <value>} dict with '.' value for empties.
    Args:
        grid: Sudoku grid in string form, 81 characters long
    Returns:
        Sudoku grid in dictionary form:
        - keys: Box labels, e.g. 'A1'
        - values: Value in corresponding box, e.g. '8', or '.' if it is empty.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))


def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    if not values:
        print('fail')
        exit()
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)
    return


def eliminate(values):
    """Eliminate values from peers of each box with a single value.
    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.
    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            # values[peer] = values[peer].replace(digit, '')
            new_value = values[peer].replace(digit, '')
            assign_value(values, peer, new_value)
    return values


def only_choice(values):
    """Finalize all values that are the only choice for a unit.
    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.
    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                # values[dplaces[0]] = digit
                new_value = digit
                box = dplaces[0]
                assign_value(values, box, new_value)
    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Use the Naked Twins Strategy
        values = naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """ Using depth-first search and propagation, try all possible values. """
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False  # Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values  # Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        # new_sudoku[s] = value
        assign_value(new_sudoku, s, value)
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    puzzle = grid_values(grid)
    # solve the puzzle
    solved_puzzle = search(puzzle)
    return solved_puzzle


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    solution = solve(diag_sudoku_grid)
    # display(solution)

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')