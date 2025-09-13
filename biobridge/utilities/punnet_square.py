import random
from typing import List

# Sample word list (you can replace this with an actual dictionary or crossword clues)
WORDS = ["cat", "dog", "mouse", "house", "bat", "rat", "hat"]

# Initialize population size
POPULATION_SIZE = 100
MUTATION_RATE = 0.05
GENERATIONS = 1000


# Fitness function to evaluate how well the crossword matches the dictionary
def fitness_function(board: List[List[str]]) -> int:
    score = 0
    # Example fitness: Count number of valid words in rows and columns
    rows = [''.join(row).strip() for row in board]
    cols = [''.join(col).strip() for col in zip(*board)]

    for word in rows + cols:
        if word in WORDS:
            score += len(word)  # Add length of valid word as score
    return score


# Initialize a random crossword board
def random_board(size: int) -> List[List[str]]:
    return [[random.choice(['X', 'O']) for _ in range(size)] for _ in range(size)]


# Mutation: randomly flip a letter in the board
def mutate(board: List[List[str]]) -> List[List[str]]:
    new_board = [row[:] for row in board]  # Copy the board
    if random.random() < MUTATION_RATE:
        i = random.randint(0, len(board) - 1)
        j = random.randint(0, len(board) - 1)
        # Flip between 'X' and 'O'
        new_board[i][j] = 'O' if board[i][j] == 'X' else 'X'
    return new_board


# Crossover: create a child from two parent boards
def crossover(parent1: List[List[str]], parent2: List[List[str]]) -> List[List[str]]:
    size = len(parent1)
    child = [row[:] for row in parent1]
    crossover_point = random.randint(0, size - 1)
    for i in range(crossover_point, size):
        child[i] = parent2[i][:]
    return child


# Genetic Crossword Solver (GCS) using a genetic algorithm
def gcs(board: List[List[str]], generations: int = GENERATIONS) -> List[List[str]]:
    population = [random_board(len(board)) for _ in range(POPULATION_SIZE)]

    for gen in range(generations):
        # Evaluate fitness for the population
        fitness_scores = [(fitness_function(individual), individual) for individual in population]
        fitness_scores.sort(reverse=True, key=lambda x: x[0])  # Sort by fitness score

        # Check if the best solution is a valid crossword
        best_fitness, best_board = fitness_scores[0]
        print(f"Generation {gen}, Best Fitness: {best_fitness}")
        if best_fitness == len(board) * len(board[0]):  # Perfect score
            return best_board

        # Selection: pick top 50% of the population for breeding
        top_half = [individual for _, individual in fitness_scores[:POPULATION_SIZE // 2]]

        # Generate new population through crossover and mutation
        new_population = []
        while len(new_population) < POPULATION_SIZE:
            parent1, parent2 = random.sample(top_half, 2)
            child = crossover(parent1, parent2)
            child = mutate(child)
            new_population.append(child)

        population = new_population

    return best_board

