import networkx as nx
from src.game.game import *


class MinimaxGameSearch:
    def __init__(self, board, active_player):
        self.board = board.copy()
        self.active_player = active_player
        self.opponent = self.board.player_b if active_player == self.board.player_a else self.board.player_a

    def minimax(self, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.is_terminal_node():
            return self.evaluate_board(), None

        if maximizing_player:  # Maximizing player (current player)
            max_eval = float('-inf')
            best_move = None
            for move in self.get_all_possible_moves(self.active_player):
                self.perform_move(move)
                eval = self.minimax(depth - 1, alpha, beta, False)[0]
                self.undo_move(move)

                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:  # Minimizing player (opponent)
            min_eval = float('inf')
            best_move = None
            for move in self.get_all_possible_moves(self.opponent):
                self.perform_move(move)
                eval = self.minimax(depth - 1, alpha, beta, True)[0]
                self.undo_move(move)

                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def is_terminal_node(self):
        return self.board.player_a.won or self.board.player_b.won

    def evaluate_board(self):
        score = 0

        # Kürzeste Distanz des aktiven Spielers zur Zielreihe
        player_a_dist = nx.shortest_path_length(
            self.board.graph, source=f'{self.board.player_a.node["row"]},{self.board.player_a.node["col"]}',
            target=f'{self.board.size - 1},0'  # Ziel für Spieler A
        )
        player_b_dist = nx.shortest_path_length(
            self.board.graph, source=f'{self.board.player_b.node["row"]},{self.board.player_b.node["col"]}',
            target=f'0,0'  # Ziel für Spieler B
        )

        # Je kürzer die Distanz, desto höher der Score
        score -= player_a_dist
        score += player_b_dist

        # Berücksichtige verbleibende Blockelemente
        score += self.board.player_a.blocks - self.board.player_b.blocks

        return score

    def get_all_possible_moves(self, player):
        possible_moves = []
        current_position = player.node

        # Überprüfe mögliche Bewegungen
        for neighbor in nx.neighbors(self.board.graph, f'{current_position["row"]},{current_position["col"]}'):
            if self.is_valid_move(player, neighbor):
                possible_moves.append(f"move {neighbor}")  # Rückgabe als String

        # Füge mögliche Blockierungen hinzu
        for row in range(self.board.size):
            for col in range(self.board.size):
                if f'{row},{col}' not in self.board.nodes_used_for_blocking:
                    for orientation in ['horizontal', 'vertical']:
                        if player.place_blocking_element(row, col, orientation):
                            possible_moves.append(f"block {row} {col} {orientation}")  # Rückgabe als String
        return possible_moves

    def is_valid_move(self, player, target):
        # Prüfen, ob der Knoten im richtigen Format 'row,col' vorliegt
        if isinstance(target, str) and ',' in target:
            row, col = map(int, target.split(','))
            return (0 <= row < self.board.size) and (0 <= col < self.board.size) and (self.board.graph.has_node(target))
        return False

    def perform_move(self, move):
        action_parts = move.split()
        action = action_parts[0]

        if action == "move":
            target = action_parts[1]
            row, col = map(int, target.split(','))
            self.active_player.node = {"row": row, "col": col}
        elif action == "block":
            row, col, orientation = int(action_parts[1]), int(action_parts[2]), action_parts[3]
            self.active_player.place_blocking_element(row, col, orientation)

    def undo_move(self, move):
        action_parts = move.split()
        action = action_parts[0]

        if action == "move":
            # Rückgängig machen des Moves (falls vorherige Position gespeichert wurde)
            pass
        elif action == "block":
            row, col, orientation = int(action_parts[1]), int(action_parts[2]), action_parts[3]
            # Blockade rückgängig machen (Kante wieder hinzufügen etc.)
            pass

    def search_next_move(self, depth):
        _, best_move = self.minimax(depth, float('-inf'), float('inf'), True)
        return best_move


if __name__ == "__main__":
    board = Board(9)
    minimax_search = MinimaxGameSearch(board, board.player_a)
    print(minimax_search.search_next_move(3))  # Stellen Sie sicher, dass die Tiefe Ihren Anforderungen entspricht.