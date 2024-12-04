from src.game.game import *
import networkx as nx

class MinimaxGameSearch:
    def __init__(self, board, active_player):
        self.board = board.copy()
        self.active_player = active_player
        self.opponent = self.board.player_b if active_player == self.board.player_a else self.board.player_a

    def minimax(self, depth, alpha, beta, maximizing_player):
        if self.is_terminal_node():  # Endzustand überprüfen (Sieger/Mission)
            return self.evaluate_board(), None

        if maximizing_player:  # Maximizing Spieler (Aktiver Spieler)
            max_eval = float('-inf')
            best_move = None
            for move in self.get_all_possible_moves(self.active_player):
                self.perform_move(move)
                eval = self.minimax(depth-1, alpha, beta, False)[0]
                self.undo_move(move)  # Rückgängigmachen

                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:  # Minimizing Spieler (Gegner)
            min_eval = float('inf')
            best_move = None
            for move in self.get_all_possible_moves(self.opponent):
                self.perform_move(move)
                eval = self.minimax(depth-1, alpha, beta, True)[0]
                self.undo_move(move)  # Rückgängigmachen

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
        # Hier kann eine Bewertungsfunktion implementiert werden.
        if self.board.player_a.won:
            return 1
        elif self.board.player_b.won:
            return -1
        else:
            return 0

    def get_all_possible_moves(self, player):
        possible_moves = []

        # Bewegungen
        for direction in ['up', 'down', 'left', 'right']:
            move_action = f'move {direction}'
            # Vorübergehendes Ausführen des Zuges, um zu prüfen, ob dieser gültig ist
            if player.move(direction):
                possible_moves.append(move_action)
                # Rückgängig machen des Zuges
                player.move(direction)  # Rückgängigmachen (da die Methode bereits das Spielbrett aktualisiert)

        # Blockierungen
        for row in range(self.board.size):
            for col in range(self.board.size):
                for orientation in ['horizontal', 'vertical']:
                    block_action = f'block {row} {col} {orientation}'
                    if player.place_blocking_element(row, col, orientation):
                        possible_moves.append(block_action)
                        # Rückgängig machen der Blockierungsaktion
                        player.board.graph.add_edge(f'{row},{col}', f'{row + 1},{col}')  # Beispielhaft
                        player.board.graph.add_edge(f'{row},{col + 1}', f'{row + 1},{col + 1}')  # Beispielhaft
                        player.blocks += 1  # Block zählen zurücksetzen
                        player.board.nodes_used_for_blocking.remove(f'{row},{col}')  # Entfernen
        return possible_moves

    def perform_move(self, move):
        action_parts = move.split()

        if action_parts[0] == 'move':
            direction = action_parts[1]
            self.active_player.move(direction)  # Führt den Zug aus

        elif action_parts[0] == 'block':
            row, col, orientation = int(action_parts[1]), int(action_parts[2]), action_parts[3]
            self.active_player.place_blocking_element(row, col, orientation)  # Blockierung setzen

    def undo_move(self, move):
        action_parts = move.split()

        if action_parts[0] == 'move':
            direction = action_parts[1]
            self.active_player.move(direction)  # Führt einen "Rückwärts-Zug" aus, um die vorherige Position wiederherzustellen

        elif action_parts[0] == 'block':
            row, col, orientation = int(action_parts[1]), int(action_parts[2]), action_parts[3]
            # Rückgängig machen der Blockierungsaktion
            blocking_element = Blocking_element(self.active_player.board, row, col, orientation)
            edge_a, edge_b = blocking_element.return_blocked_paths()
            self.active_player.board.graph.add_edge(edge_a[0], edge_a[1])
            self.active_player.board.graph.add_edge(edge_b[0], edge_b[1])
            self.active_player.blocks += 1  # Rückrechnen
            self.active_player.board.nodes_used_for_blocking.remove(f'{row},{col}')  # Block zurücknehmen

    def search_next_move(self, depth):
        best_move = self.minimax(depth, float('-inf'), float('inf'), True)
        return best_move

if __name__ == "__main__":
    board = Board(9)
    minimax_search = MinimaxGameSearch(board, board.player_a)
    print(minimax_search.search_next_move(3))  # Tiefe auf 3 gesetzt, kann angepasst werden