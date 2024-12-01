import networkx as nx

class Board:
    '''
    Die Klasse Board repräsentiert das Spielfeld des Spiels Quoridor
    '''
    def __init__(self, size):
        '''
        Das Spielfeld wird als Graph angelegt, auf Basis der Library networkx
        Zur Darstellung der Knoten und Kanten:
            ein Knoten wird über einen String 'row,col' identifiziert
            Knoten enthalten als Attribute ihre Reihe und Zeile und ihr aktuelles Symbol
            eine Kante wird über ein Tupel (node_a,node_b) identifiziert
        :param size: Spielfeldgröße == size x size
        '''
        self.graph = nx.Graph()
        self.size = size
        #Knoten erzeugen
        for row in range(self.size):
            for col in range(self.size):
                self.graph.add_node(f'{row},{col}',row = row, col = col, symbol = '□')

        #Kanten erzeugen
        for row in range(self.size):
            for col in range(self.size):
                if(f'{row + 1},{col}'  in self.graph.nodes):
                    self.graph.add_edge(f'{row},{col}', f'{row + 1},{col}')
                if (f'{row},{col + 1}' in self.graph.nodes):
                    self.graph.add_edge(f'{row},{col}', f'{row},{col + 1}')
        #TODO Zielknoten hinzufügen die mit zielreihen verbunden sind

        #Spieler erzeugen
        self.player_a = Player(self,0,4,'A')
        self.player_b = Player(self,8,4,'B')
        self.nodes_used_for_blocking = []

    def print_board(self):
        '''
        grafische Ausgabe des Spielfeldes auf der Konsole
        :return:
        '''
        for row in range(self.size):
            for col in range(self.size):
                print(self.graph.nodes.get(f'{row},{col}').get('symbol'), end='')
                print('  ', end='')
                if((f'{row},{col}', f'{row},{col + 1}') in self.graph.edges):
                    print('———', end ='')
                else:
                    print('   ', end='')
                print('  ', end='')
            print()
            for col in range(self.size):
                if((f'{row},{col}', f'{row + 1},{col}') in self.graph.edges):
                    print('|', end ='')
                else:
                    print(' ', end='')
                print('       ', end='')
            print()

    # Simulation eines Spieles implementieren
    # zunächst manuell steuerbar (Konsole), dann per programmierter KI

    def simulate_game(self):
        current_player = self.player_a
        while not self.player_a.won and not self.player_b.won:
            self.print_board()
            print(f"Spieler {current_player.name} ist am Zug.")

            action = input("Wählen Sie eine Aktion: (move [direction] oder block [row] [col] [orientation]): ")
            action_parts = action.split()

            #Wenn spieler a auf spieler b steht (sprung), dann nicht blockieren
            if current_player == self.player_a and self.player_a.node == self.player_b.node:
                blocking_invalid = True
            else:
                blocking_invalid = False

            move_ok = True
            #Prüfen des move Befehls
            if action_parts[0] == 'move' and len(action_parts) == 2:
                direction = action_parts[1]
                if not current_player.move(direction):
                    move_ok = False
                    print("Ungültiger Zug, bitte erneut versuchen.")

            #Prüfen des block Befehls
            elif action_parts[0] == 'block' and len(action_parts) == 4:
                if blocking_invalid:
                    print("Blockieren ist nicht erlaubt, da Sie über den Gegner springen.")
                    continue  # Gehe zurück zur Eingabeaufforderung
                row, col, orientation = int(action_parts[1]), int(action_parts[2]), action_parts[3]
                if not current_player.place_blocking_element(row, col, orientation):
                    print("Blockade konnte nicht platziert werden, bitte erneut versuchen.")

            else:
                move_ok = False
                print(
                    "Ungültige Aktion. Bitte verwenden Sie 'move [direction]' oder 'block [row] [col] [orientation]'.")

            #Wechsel des Spielers oder nochmal, falls Spielzug ungültig
            if move_ok:
                current_player = self.player_b if current_player == self.player_a else self.player_a
            else:
                current_player = self.player_a if current_player == self.player_a else self.player_b

        #Spiel beendet, Ausgabe des Gewinners
        self.print_board()
        if self.player_a.won:
            print("Spieler A hat gewonnen!")
        else:
            print("Spieler B hat gewonnen!")

class Player:
    def __init__(self, board, row, col, name):
        '''
        Player repräsentiert einen der beiden Spieler auf dem Spielfeld
        :param board: Das Spielfeld, auf welchem gespielt wird
        :param row: Startposition, Zeile
        :param col: Startposition, Spalte
        :param name: Symbol des Spielers (für die grafische Spielfeldausgabe in der Konsole)
        '''
        self.board = board
        self.name = name
        self.node = board.graph.nodes.get(f'{row},{col}')
        self.node['symbol'] = self.name
        self.blocks = 10
        self.won = False

        if (row == 0):
            self.goal = 8
        if (row == 8):
            self.goal = 0

    def game_won(self):
        '''
        Falls ein Spieler seine ZielReihe erreicht hat, wird die Klassenvariable self.won auf True gesetzt
        '''
        if(self.node['row'] == self.goal):
            self.won = True


    def move(self, direction):
        '''
        Bewegung eines Spielers auf dem Spielfeld
        :param direction: Richtung in welche der Spieler sich bewegen will
        :return: Falls die Bewegung ungültig ist (außerhalb des Felder oder keine Verbindung zwischen 2 positionen, nach der Bewegung)
                    oder der Spieler auf dem anderen Spieler steht (nach der Bewegung):
                    False
                sonst:
                    True
        '''
        moved = False #hat der Spieler sich bewegt?
        next_node = self.node
        if((direction == 'right')
                and (f'{self.node["row"]},{self.node["col"]}',f'{self.node["row"]},{self.node["col"] + 1}') in self.board.graph.edges): #String zur Identifikation der Kante prüfen
            next_node = board.graph.nodes.get(f'{self.node["row"]},{self.node["col"] + 1}')
            moved = True
        elif((direction == 'left')
             and (f'{self.node["row"]},{self.node["col"]}',f'{self.node["row"]},{self.node["col"] - 1}') in self.board.graph.edges):
            next_node = board.graph.nodes.get(f'{self.node["row"]},{self.node["col"] - 1}')
            moved = True
        elif((direction == 'up')
             and (f'{self.node["row"]},{self.node["col"]}',f'{self.node["row"] - 1},{self.node["col"]}') in self.board.graph.edges):
            next_node = board.graph.nodes.get(f'{self.node["row"] - 1},{self.node["col"]}')
            moved = True
        elif((direction == 'down')
             and (f'{self.node["row"]},{self.node["col"]}',f'{self.node["row"] + 1},{self.node["col"]}') in self.board.graph.edges):
            next_node = board.graph.nodes.get(f'{self.node["row"] + 1},{self.node["col"]}')
            moved = True

        if(moved):
            self.node['symbol'] = '□' #altes Feld bekommt Symbol für leeres Feld zugewiesen
            self.node = next_node #Spielerfeld wird aktualisiert
            self.node['symbol'] = self.name #neues Feld bekommt Symbol vom Spieler
            self.game_won() #Prüfung, ob das Spiel gewonnen wurde
        if((moved is False) or #Bewegung war ungültig
                (moved is True and self.name == 'A' and self.node == board.player_b.node) # oder Spieler A springt über Spieler B
                or (moved is True and self.name == 'B' and self.node == board.player_a.node)): #oder Spieler B springt über Spieler A
            return False
        return True #Bewegung war gültig und der Spieler springt nicht über den anderen

    def place_blocking_element(self, row, col, orientation):
        '''
        Platzieren einer Blockade auf dem Spielfeld,
            Näheres in der Klasse Blocking_element
        :param row: Ausgangszeile der Blockade
        :param col: Ausgangsspalte der Blockade
        :param orientation: orientierung der Blockade ('vertical' oder 'horizontal')
        :return: Falls Blockade platziert werden konnte:
                    True
                sonst (eine oder beide der Kanten sind schon blockiert):
                    False
        '''
        blocking_element = Blocking_element(self, row, col, orientation)
        edge_a, edge_b = blocking_element.return_blocked_paths()
        if (edge_a in self.board.graph.edges
            and edge_b in self.board.graph.edges
            and f'{row},{col}' not in self.board.nodes_used_for_blocking):
            self.board.graph.remove_edge(edge_a[0], edge_a[1])
            self.board.graph.remove_edge(edge_b[0], edge_b[1])
            if (not self.check_if_path_exists()):
                self.board.add_edge(edge_a[0], edge_a[1])
                self.board.add_edge(edge_b[0], edge_b[1])
                return False
            self.blocks -= 1
            self.board.nodes_used_for_blocking.append(f'{row},{col}')
            return True
        return False

    def check_if_path_exists(self):
        #TODO Auf zusatzknoten prüfen, statt ganze zielreihe, wenn zusatzknoten da
        path_player_a_exists = False
        path_player_b_exists = False
        for col in range(9): #check for both players, if any path to a tile of the goal row exists
            if nx.has_path(self.board.graph,f'{board.player_a.node["row"]},{board.player_a.node["col"]}',f'{board.player_a.goal},{col}'):
                path_player_a_exists = True
            if nx.has_path(self.board.graph,f'{board.player_b.node["row"]},{board.player_b.node["col"]}',f'{board.player_b.goal},{col}'):
                path_player_b_exists = True
            if path_player_a_exists and path_player_b_exists:
                return True
        return False


class Blocking_element:
    def __init__(self, board, row, col, orientation):
        '''
                Spielteil zum Blockieren des Weges
                in dem folgenden Beispiel zur Auswirkung von direction
                hat 'a' die Position [row,col]

                Die Knoten stehen wie folgt zueinander:

                    a-----b
                    |     |
                    c-----d

                wenn orientation == horizontal:
                    die Verbindungen (Kanten) zwischen a und c (bzw. b und d) sind blockiert (gelöscht)

                    a-----b

                    c-----d

                wenn orientation == vertical:
                    die Verbindungen (Kanten) zwischen a und b (bzw. c und d) sind blockiert (gelöscht)

                    a     b
                    |     |
                    c     d

                :param row: row-Position von a
                :param col: col-Position von a
                :param orientation: Ausrichtung des blockierenden Elementes
                :param board: Spielfeld
                '''
        self.row = row
        self.col = col
        self.orientation = orientation
        self.board = board

        self.pos_a = f'{row},{col}'
        self.pos_b = f'{row + 1},{col}'
        self.pos_c = f'{row},{col + 1}'
        self.pos_d = f'{row + 1},{col + 1}'

    def return_blocked_paths(self):
        '''
        Rückgabe der beiden blockierten Kanten,
        je nach Ausrichtung
        :return: Kante a, Kante b
        '''
        if self.orientation == 'horizontal':
            edge_a = (self.pos_a,self.pos_b)
            edge_b = (self.pos_c,self.pos_d)
            return edge_a,edge_b
        elif self.orientation == 'vertical':
            edge_a = (self.pos_a,self.pos_c)
            edge_b = (self.pos_b,self.pos_d)
            return edge_a,edge_b



if __name__ == '__main__':
    #Ein paar beispielhafte Züge und wie das Spielfeld danach aussieht
    board = Board(9)
    board.graph.remove_edge(f'{4},{4}', f'{5},{4}')
    board.simulate_game()

