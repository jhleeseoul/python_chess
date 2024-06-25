import time
import pygame
import sys

class ChessPiece:
    def __init__(self, color):
        self.color = color

    def is_valid_move(self, board, start, end):
        return False

class Pawn(ChessPiece):
    def is_valid_move(self, board, start, end):
        x1, y1 = start
        x2, y2 = end
        if self.color == 'white':
            if y1 == 1 and y2 == 3 and x1 == x2 and board[2][x1] is None:
                return True
            return y2 == y1 + 1 and abs(x2 - x1) <= 1
        else:
            if y1 == 6 and y2 == 4 and x1 == x2 and board[5][x1] is None:
                return True
            return y2 == y1 - 1 and abs(x2 - x1) <= 1

class Rook(ChessPiece):
    def is_valid_move(self, board, start, end):
        x1, y1 = start
        x2, y2 = end
        return x1 == x2 or y1 == y2

class Knight(ChessPiece):
    def is_valid_move(self, board, start, end):
        x1, y1 = start
        x2, y2 = end
        return (abs(x2 - x1) == 2 and abs(y2 - y1) == 1) or (abs(x2 - x1) == 1 and abs(y2 - y1) == 2)

class Bishop(ChessPiece):
    def is_valid_move(self, board, start, end):
        x1, y1 = start
        x2, y2 = end
        return abs(x2 - x1) == abs(y2 - y1)

class Queen(ChessPiece):
    def is_valid_move(self, board, start, end):
        x1, y1 = start
        x2, y2 = end
        return x1 == x2 or y1 == y2 or abs(x2 - x1) == abs(y2 - y1)

class King(ChessPiece):
    def is_valid_move(self, board, start, end):
        x1, y1 = start
        x2, y2 = end
        return abs(x2 - x1) <= 1 and abs(y2 - y1) <= 1

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_board()
        self.last_move = None
        self.castling_rights = {'white': {'kingside': True, 'queenside': True},
                                'black': {'kingside': True, 'queenside': True}}

    def setup_board(self):
        # Set up pawns
        for i in range(8):
            self.board[1][i] = Pawn('white')
            self.board[6][i] = Pawn('black')

        # Set up other pieces
        pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i in range(8):
            self.board[0][i] = pieces[i]('white')
            self.board[7][i] = pieces[i]('black')

    def move_piece(self, start, end):
        x1, y1 = start
        x2, y2 = end
        piece = self.board[y1][x1]
        if piece and self.is_valid_move(start, end):
            captured_piece = self.board[y2][x2]
            
            # Handle en passant
            if isinstance(piece, Pawn) and abs(x2 - x1) == 1 and self.board[y2][x2] is None:
                captured_piece = self.board[y1][x2]
                self.board[y1][x2] = None

            # Handle castling
            if isinstance(piece, King) and abs(x2 - x1) == 2:
                if x2 > x1:  # Kingside
                    rook = self.board[y1][7]
                    self.board[y1][5] = rook
                    self.board[y1][7] = None
                else:  # Queenside
                    rook = self.board[y1][0]
                    self.board[y1][3] = rook
                    self.board[y1][0] = None

            self.board[y2][x2] = piece
            self.board[y1][x1] = None
            
            # Update castling rights
            if isinstance(piece, King):
                self.castling_rights[piece.color]['kingside'] = False
                self.castling_rights[piece.color]['queenside'] = False
            elif isinstance(piece, Rook):
                if x1 == 0:
                    self.castling_rights[piece.color]['queenside'] = False
                elif x1 == 7:
                    self.castling_rights[piece.color]['kingside'] = False

            # Check if this move puts the current player in check
            if self.is_in_check(piece.color):
                # If so, revert the move
                self.board[y1][x1] = piece
                self.board[y2][x2] = captured_piece
                if isinstance(piece, Pawn) and abs(x2 - x1) == 1 and captured_piece is None:
                    self.board[y1][x2] = self.board[y2][x2]
                    self.board[y2][x2] = None
                return False

            self.last_move = (start, end)
            return True
        return False

    def is_valid_move(self, start, end, check_castling=True):
        x1, y1 = start
        x2, y2 = end
        piece = self.board[y1][x1]
        target = self.board[y2][x2]

        if not (0 <= x2 < 8 and 0 <= y2 < 8):
            return False

        if target and target.color == piece.color:
            return False

        if isinstance(piece, Pawn):
            if piece.color == 'white':
                if y2 == y1 + 1 and x2 == x1 and not target:
                    return True
                if y1 == 1 and y2 == 3 and x2 == x1 and not target and not self.board[2][x1]:
                    return True
                if y2 == y1 + 1 and abs(x2 - x1) == 1 and (target or self.is_en_passant(start, end)):
                    return True
            else:
                if y2 == y1 - 1 and x2 == x1 and not target:
                    return True
                if y1 == 6 and y2 == 4 and x2 == x1 and not target and not self.board[5][x1]:
                    return True
                if y2 == y1 - 1 and abs(x2 - x1) == 1 and (target or self.is_en_passant(start, end)):
                    return True
            return False

        if isinstance(piece, King) and abs(x2 - x1) == 2 and check_castling:
            return self.is_castling_valid(start, end)

        # Check if the path is clear for other pieces
        if not isinstance(piece, Knight):
            dx = x2 - x1
            dy = y2 - y1
            distance = max(abs(dx), abs(dy))
            for i in range(1, distance):
                x = x1 + i * (dx // distance)
                y = y1 + i * (dy // distance)
                if self.board[y][x] is not None:
                    return False

        return piece.is_valid_move(self.board, start, end)

    def is_en_passant(self, start, end):
        if not self.last_move:
            return False
        x1, y1 = start
        x2, y2 = end
        lx1, ly1, lx2, ly2 = self.last_move[0][0], self.last_move[0][1], self.last_move[1][0], self.last_move[1][1]
        piece = self.board[y1][x1]
        last_piece = self.board[ly2][lx2]
        return (isinstance(piece, Pawn) and isinstance(last_piece, Pawn) and
                abs(ly2 - ly1) == 2 and abs(x2 - lx2) == 1 and y1 == ly2 and x2 == lx2)

    def is_castling_valid(self, start, end):
        x1, y1 = start
        x2, y2 = end
        piece = self.board[y1][x1]
        if not isinstance(piece, King):
            return False
        if self.is_in_check(piece.color):
            return False
        if x2 > x1:  # Kingside
            if not self.castling_rights[piece.color]['kingside']:
                return False
            for x in range(5, 7):
                if self.board[y1][x] is not None:
                    return False
            return isinstance(self.board[y1][7], Rook) and not self.is_square_attacked(5, y1, piece.color) and not self.is_square_attacked(6, y1, piece.color)
        else:  # Queenside
            if not self.castling_rights[piece.color]['queenside']:
                return False
            for x in range(1, 4):
                if self.board[y1][x] is not None:
                    return False
            return isinstance(self.board[y1][0], Rook) and not self.is_square_attacked(2, y1, piece.color) and not self.is_square_attacked(3, y1, piece.color)

    def is_square_attacked(self, x, y, color):
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece and piece.color != color:
                    if self.is_valid_move((j, i), (x, y), check_castling=False):
                        return True
        return False

    def get_valid_moves(self, start):
        valid_moves = []
        x, y = start
        piece = self.board[y][x]
        if piece:
            for end_y in range(8):
                for end_x in range(8):
                    if self.is_valid_move(start, (end_x, end_y)):
                        # Check for en passant
                        if isinstance(piece, Pawn) and abs(end_x - x) == 1 and self.board[end_y][end_x] is None:
                            if (piece.color == 'white' and y == 4) or (piece.color == 'black' and y == 3):
                                if self.is_en_passant(start, (end_x, end_y)):
                                    valid_moves.append((end_x, end_y))
                        else:
                            valid_moves.append((end_x, end_y))
        return valid_moves

    def is_in_check(self, color):
        king_pos = self.find_king(color)
        if not king_pos:
            return False

        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if piece and piece.color != color:
                    if self.is_valid_move((x, y), king_pos, check_castling=False):
                        return True
        return False

    def find_king(self, color):
        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if isinstance(piece, King) and piece.color == color:
                    return (x, y)
        return None

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False

        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if piece and piece.color == color:
                    if self.get_valid_moves((x, y)):
                        return False
        return True

    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False

        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if piece and piece.color == color:
                    if self.get_valid_moves((x, y)):
                        return False
        return True


class ChessGame:
    def __init__(self):
        pygame.init()
        self.WIDTH = 480
        self.HEIGHT = 560
        self.SQUARE_SIZE = self.WIDTH // 8
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Chess")
        
        self.board = ChessBoard()
        self.load_images()
        
        self.selected_piece = None
        self.valid_moves = []
        self.players = ['white', 'black']
        self.current_player = 0
        self.game_over = False
        self.winner = None
        self.in_check = False

        self.font = pygame.font.Font(None, 36)
        self.time_left = [600, 600]  # 10 minutes for each player
        self.last_move_time = time.time()

        self.load_board_texture()
        self.resign_button_white = pygame.Rect(self.WIDTH - 100, 10, 80, 25)
        self.resign_button_black = pygame.Rect(self.WIDTH - 100, self.HEIGHT - 35, 80, 25)
        
    

    def load_images(self):
        pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
        self.images = {}
        for piece in pieces:
            self.images[piece] = pygame.transform.scale(
                pygame.image.load(f"chess/chess_pieces/{piece}.png"),
                (self.SQUARE_SIZE, self.SQUARE_SIZE)
            )
            
    def load_board_texture(self):
        self.board_texture = pygame.image.load("wood_texture.png")
        self.board_texture = pygame.transform.scale(self.board_texture, (self.WIDTH, self.WIDTH))        

    def draw_board(self):
        self.screen.blit(self.board_texture, (0, 40))
        
        # Create checkered pattern
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 0:
                    s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
                    s.set_alpha(100)  # Semi-transparent
                    s.fill(pygame.Color(240, 217, 181))  # Light square color
                    self.screen.blit(s, (col * self.SQUARE_SIZE, row * self.SQUARE_SIZE + 40))
                else:
                    s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
                    s.set_alpha(120)  # Semi-transparent
                    s.fill(pygame.Color(139,69,19))  # Dark square color
                    self.screen.blit(s, (col * self.SQUARE_SIZE, row * self.SQUARE_SIZE + 40))
        
        # Draw grid lines
        for i in range(9):
            pygame.draw.line(self.screen, pygame.Color("black"), 
                            (0, i * self.SQUARE_SIZE + 40), 
                            (self.WIDTH, i * self.SQUARE_SIZE + 40))
            pygame.draw.line(self.screen, pygame.Color("black"), 
                            (i * self.SQUARE_SIZE, 40), 
                            (i * self.SQUARE_SIZE, self.HEIGHT - 40))

    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                piece = self.board.board[row][col]
                if piece:
                    color = piece.color[0]
                    piece_type = type(piece).__name__[0]
                    if isinstance(piece, Pawn):
                        piece_type = 'p'
                    elif isinstance(piece, Knight):
                        piece_type = 'N'
                    self.screen.blit(self.images[f"{color}{piece_type}"],
                                     pygame.Rect(col * self.SQUARE_SIZE, row * self.SQUARE_SIZE + 40,
                                                 self.SQUARE_SIZE, self.SQUARE_SIZE))

    def draw_valid_moves(self):
        for move in self.valid_moves:
            x, y = move
            center = (x * self.SQUARE_SIZE + self.SQUARE_SIZE // 2, 
                      y * self.SQUARE_SIZE + self.SQUARE_SIZE // 2 + 40)
            if self.board.board[y][x]:
                pygame.draw.circle(self.screen, pygame.Color(192, 192, 192, 128), center, self.SQUARE_SIZE // 3, 4)
            else:
                pygame.draw.circle(self.screen, pygame.Color(192, 192, 192, 128), center, self.SQUARE_SIZE // 8)

    def draw_timers(self):
        white_time = self.font.render(f"White: {int(self.time_left[0]//60)}:{int(self.time_left[0]%60):02d}", True, pygame.Color("black"))
        black_time = self.font.render(f"Black: {int(self.time_left[1]//60)}:{int(self.time_left[1]%60):02d}", True, pygame.Color("black"))
        self.screen.blit(white_time, (10, 10))
        self.screen.blit(black_time, (10, self.HEIGHT - 30))

    def draw_check_indicator(self):
        if self.in_check:
            color = "white" if self.current_player == 1 else "black"
            text = self.font.render("Check", True, pygame.Color("red"))
            if color == "white":
                self.screen.blit(text, (self.WIDTH - 100, 10))
            else:
                self.screen.blit(text, (self.WIDTH - 100, self.HEIGHT - 30))

    def draw_resign_buttons(self):
        pygame.draw.rect(self.screen, pygame.Color("red"), self.resign_button_white)
        pygame.draw.rect(self.screen, pygame.Color("red"), self.resign_button_black)
        
        font = pygame.font.Font(None, 24)
        text_white = font.render("Resign", True, pygame.Color("white"))
        text_black = font.render("Resign", True, pygame.Color("white"))
        
        text_rect_white = text_white.get_rect(center=self.resign_button_white.center)
        text_rect_black = text_black.get_rect(center=self.resign_button_black.center)
        
        self.screen.blit(text_white, text_rect_white)
        self.screen.blit(text_black, text_rect_black)

    def handle_click(self, pos):
        if self.game_over:
            return

        if self.resign_button_white.collidepoint(pos) and self.current_player == 0:
            self.game_over = True
            self.winner = self.players[1]
            return
        elif self.resign_button_black.collidepoint(pos) and self.current_player == 1:
            self.game_over = True
            self.winner = self.players[0]
            return

        col = pos[0] // self.SQUARE_SIZE
        row = (pos[1] - 40) // self.SQUARE_SIZE
        
        if 0 <= row < 8:  # Make sure the click is within the board
            if self.selected_piece:
                start = self.selected_piece
                end = (col, row)
                if self.board.move_piece(start, end):
                    self.selected_piece = None
                    self.valid_moves = []
                    self.current_player = 1 - self.current_player
                    self.last_move_time = time.time()

                    # Check for checkmate or stalemate
                    if self.board.is_checkmate(self.players[self.current_player]):
                        self.game_over = True
                        self.winner = self.players[1 - self.current_player]
                    elif self.board.is_stalemate(self.players[self.current_player]):
                        self.game_over = True
                        self.winner = "Stalemate"

                    # Update check status
                    self.in_check = self.board.is_in_check(self.players[self.current_player])
                else:
                    self.selected_piece = None
                    self.valid_moves = []
            else:
                piece = self.board.board[row][col]
                if piece and piece.color == self.players[self.current_player]:
                    self.selected_piece = (col, row)
                    self.valid_moves = self.board.get_valid_moves(self.selected_piece)

    def draw_game_over(self):
        s = pygame.Surface((self.WIDTH, self.HEIGHT))
        s.set_alpha(192)
        s.fill((255, 255, 255))
        self.screen.blit(s, (0, 0))

        if self.winner == "Stalemate":
            text = self.font.render("Stalemate", True, pygame.Color("black"))
        elif self.winner:
            text = self.font.render(f"{self.winner.capitalize()} wins", True, pygame.Color("black"))
        else:
            text = self.font.render("Time's up", True, pygame.Color("black"))
        
        text_rect = text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2))
        pygame.draw.rect(self.screen, pygame.Color(161, 102, 47), text_rect.inflate(80, 80))
        self.screen.blit(text, text_rect)

    def run(self):
        while True:
            current_time = time.time()
            if not self.game_over:
                self.time_left[self.current_player] -= current_time - self.last_move_time
                self.last_move_time = current_time

                if self.time_left[self.current_player] <= 0:
                    self.game_over = True
                    self.winner = self.players[1 - self.current_player]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())

            self.screen.fill(pygame.Color("white"))
            self.draw_board()
            self.draw_pieces()
            self.draw_valid_moves()
            self.draw_timers()
            self.draw_check_indicator()
            self.draw_resign_buttons()
            
            if self.selected_piece:
                pygame.draw.rect(self.screen, pygame.Color("green"), pygame.Rect(
                    self.selected_piece[0] * self.SQUARE_SIZE,
                    self.selected_piece[1] * self.SQUARE_SIZE + 40,
                    self.SQUARE_SIZE, self.SQUARE_SIZE
                ), 3)
            
            if self.game_over:
                self.draw_game_over()

            pygame.display.flip()

if __name__ == "__main__":
    game = ChessGame()
    game.run()