# Pickomino

Pickomino is a fun board game where players collect dominos with different worm values.
The goal of the game is to have the most worms at the end of the game. The game can be found on [Board Game Geek](https://boardgamegeek.com/boardgame/15818/pickomino).

## Simulating Game State

`GameState` contains the game state and logic for simulating games. Below is the pseudocode for simulating a game. 

```python
# Initialize GameState to a new game
game_state = GameState()

# Play one action at a time until the game is complete
while not game_state.is_game_over():

  # Get possible actions that can be taken with the current GameState
  actions = game_state.get_next_possible_actions()
  
  # Each player is controlled by an ai function. Players can have different ais
  ai = game_state.get_current_turn_ai()
  
  # Ai for the current player picks the next action to play
  chosen_action = ai(game_state, actions)
  
  # Update the GameState with the chosen action
  game_state.resolve_action(chosen_action)
```

## AI

A Monte Carlo Tree Search (MCTS) AI, 2 Greedy AIs, and a Random AI were created to play against each other.

As expected, the MCTS AI performed the best, followed by the Greedy AIs, followed by the Random AI

### 🥇 Monte Carlo Tree Search

[Monte Carlo Tree Search](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search) (MCTS) is a tree search algorithm which performs well in games
with a high branching factor. In the Pickomino simulation, a Monte Carlo Tree Search algorithm was implemented and performed better than
the greedy AIs. The MCTS AI used change in the player's number of worms at the end of their turn as the Q values and used random playouts in the simulation step

### 🥈 Greedy AI

A simple greedy algorithm (called `safe_ai` in the `ai.py`) that takes a domino (which increases a player's worm count) whenever possible and otherwise takes the largest
available dice. The slightly more complex greedy algorithm (`safe_ai_better_die_saving`) had slightly more complex dice saving logic.
Both greedy AIs had similar performance and performed significantly better than the random AI and slightly worse than the MCTS AI.

### 🥉 Random AI

The random AI chose a random valid action to perform. As expected, it performed very poorly. However, the game is short enough and involves enough luck
(the game is based around dice rolls) that the random AI would not always come in last place in all games.

## Analyzing Results

Results were analyzed by plotting with `matplotlib`. The number of worms held by the player at the end of the game is the x-axis
and the number of games with that number of worms is the y-axis
