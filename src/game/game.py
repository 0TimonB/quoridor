
import networkx as nx

class Board:
    def __init__(self, size):
        self.graph = nx.Graph()
        self.size = size
        for col in range(self.size):
            for row in range(self.size):
                self.graph.add_node(f'{row},{col}',row = row, col = col, symbol = '□')

        for col in range(self.size):
            for row in range(self.size):
                if(f'{row + 1},{col}'  in self.graph.nodes):
                    self.graph.add_edge(f'{row},{col}', f'{row + 1},{col}')
                if (f'{row},{col + 1}' in self.graph.nodes):
                    self.graph.add_edge(f'{row},{col}', f'{row},{col + 1}')
        self.player_a = Player(self,4,0,'A')
        self.player_b = Player(self,4,8,'B')

    def print_board(self):
        for col in range(self.size):
            for row in range(self.size):
                print(self.graph.nodes.get(f'{col},{row}').get('symbol'), end='')
                print('  ', end='')
                if((f'{row},{col}', f'{row + 1},{col}') in self.graph.edges):
                    print('———', end ='')
                else:
                    print('   ', end='')
                print('  ', end='')
            print()
            for row in range(self.size):
                if((f'{row},{col}', f'{row},{col + 1}') in self.graph.edges):
                    print('|', end ='')
                else:
                    print(' ', end='')
                print('       ', end='')
            print()






class Player:
    def __init__(self, board, row, col, name):
        self.board = board
        self.name = name
        self.node = board.graph.nodes.get(f'{col},{row}')
        self.node['symbol'] = self.name

    def move(self, direction):
        if((direction == 'right')
                and (f'{self.node['row']},{self.node['col']}',f'{self.node["row"]},{self.node["col"] + 1}') in self.board.graph.edges):
            self.node['symbol'] = '□'
            self.node = board.graph.nodes.get(f'{self.node["row"]},{self.node["col"] + 1}')
            self.node['symbol'] = self.name
            return True
        elif((direction == 'left')
             and (f'{self.node['row']},{self.node['col']}',f'{self.node["row"]},{self.node["col"] - 1}') in self.board.graph.edges):
            self.node['symbol'] = '□'
            self.node = board.graph.nodes.get(f'{self.node["row"]},{self.node["col"] - 1}')
            self.node['symbol'] = self.name
            return True
        elif((direction == 'up')
             and (f'{self.node['row']},{self.node['col']}',f'{self.node["row"] - 1},{self.node["col"]}') in self.board.graph.edges):
            self.node['symbol'] = '□'
            self.node = board.graph.nodes.get(f'{self.node["row"] - 1},{self.node["col"]}')
            self.node['symbol'] = self.name
            return True
        elif((direction == 'down')
             and (f'{self.node['row']},{self.node['col']}',f'{self.node["row"] + 1},{self.node["col"]}') in self.board.graph.edges):
            self.node['symbol'] = '□'
            self.node = board.graph.nodes.get(f'{self.node["row"] + 1},{self.node["col"]}')
            self.node['symbol'] = self.name
            return True
        return False

if __name__ == '__main__':
    board = Board(9)
    board.graph.remove_edge(f'{4},{4}', f'{5},{4}')
    board.player_b.move('right')
    board.player_b.move('right')
    board.player_b.move('right')
    board.player_b.move('right')
    board.player_b.move('up')
    board.player_a.move('down')
    board.player_a.move('left')
    board.print_board()
    print(nx.has_path(board.graph,f'{0},{0}',f'{7},{8}'))

