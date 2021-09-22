import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    # Initialise start node, frontier and path
    start_node = Node(source, None, None)
    queueFrontier = QueueFrontier()
    queueFrontier.add(start_node)
    explored = QueueFrontier()
    path = []

    # Loop to find the shortest path
    while(True):

        # 1. If the frontier is empty, stop. There is no solution
        if queueFrontier.empty():
            print("No solution")
            return None

        # 2. Remove a node from the frontier
        node = queueFrontier.remove()

        # 3. If the node contains the goal state, return the solution
        if node.state == target:
            path = calculate_path(start_node, node, explored)
            return path
            
        # Else, Expand the node and add resulting nodes to the frontier and add node to the explored set
        else:
            for row in neighbors_for_person(node.state):
                next_node = Node(row[1], node.state, row[0])

                #check if node is the targuet
                if next_node.state == target:
                    path = calculate_path(start_node, next_node, explored)
                    return path

                #check if the node not in the explored / frotier 
                elif not explored.contains_state(next_node.state) and not queueFrontier.contains_state(next_node.state):
                    queueFrontier.add(next_node)
                    explored.add(node)


def calculate_path(source_node, target_node, explored):
    """
    Returns the followed path to solution.
    """
    path = []
    last_node = target_node
    print("Target: " + target_node.state)

    while(True):
        # Take the action and state from last node and add to path
        path.append((last_node.action, last_node.state))

        # Check if last node parent is the source node
        if last_node.parent == source_node.state:
            path.reverse()
            return path

        # Look for the parent node
        for n in explored.frontier:
            if n.state == last_node.parent:
                parent = n 
                break
        
        # Update last node
        last_node = parent

    
def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
