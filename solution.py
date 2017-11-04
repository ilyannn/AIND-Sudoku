assignments = []


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    units_naked_twins = [] # Sets of naked twins
    
    # Find all instances of naked twins
    for unit in unitlist:
        naked = set() # Digits that are naked twins
        seen = [] # Sets we've seen in this unit
        for box in unit:
            value = set(values[box])
            if len(value) != 2: continue
            if value in seen:
                naked |= value
            else:
                seen += [value]
        units_naked_twins += [(unit, naked)]

    # Eliminate the naked twins as possibilities for their peers
    for unit, naked in units_naked_twins:
        for box in unit:
            value = values[box]
            new_value_set = set(value) - naked
            if len(new_value_set) > 0:
                assign_value(values, box, ''.join(sorted(new_value_set)))

    return values

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a + b for a in A for b in B]

# Basic definitions
rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# Add diagonal units
def diagonal(columns):
    "Diagonal with rows and different column order."
    return [a + b for a, b in zip(rows, columns)]

diag_units = [diagonal(cols), diagonal(reversed(cols))]
unitlist = row_units + column_units + square_units + diag_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    return dict([(a, '123456789' if b == '.' else b) for a, b in zip(boxes, grid)])


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    # Copied from the utils.py
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    for (box, value) in values.copy().items():
        if len(value) == 1:
            for another in peers[box]:
                assign_value(values, another, values[another].replace(value, ''))

    return values


def only_choice(values):
    for unit in unitlist:
        count = {}
        for peer in unit:
            for choice in values[peer]:
                count[choice] = '' if choice in count else peer
        for (found, peer) in count.items():
            if peer != '':
                assign_value(values, peer, found)
    return values


def makes_sense(values):
    """
    Check if the solution still seems possible.
    Args:
        values(dict): The sudoku in dictionary form
    """
    return 0 not in map(len, values.values())


def total_choices(values):
    """
    Add the possible number of choices in all boxes.
    Args:
        values(dict): The sudoku in dictionary form
    """
    return sum(map(len, values.values()))


def reduce_puzzle(values):
    # Sanity check, return False if there is a box with zero available values:
    while makes_sense(values):
        # Check how many steps are left.
        choices_before = total_choices(values)
        
        # Use the Eliminate Strategy. Use the Only Choice Strategy.
        values = eliminate(only_choice(values))

        # If we are not getting closer, stop now.
        if choices_before == total_choices(values):
            return values

    return False

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values == False:
        return False
    
    # Choose one of the unfilled squares with the fewest possibilities
    
    fill = [(len(value), box, value) for box, value in values.items() if len(value) > 1]

    if fill == []: # Solved!
        return values
    
    guess = min(fill)
    
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for choice in guess[2]:
        copy = values.copy()
        assign_value(copy, guess[1], choice)
        result = search(copy)
        if result:
            return result

    return False


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    #    display(values)
    return search(values)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
