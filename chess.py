#!/usr/bin/env python

"""Minimal Chess"""

__copyright__ = "Copyright 2007, Scott Forbes"
__license__ = "GPL"

import sys, string, re, copy


# piece valuations
valuation = {"P": 1, "B": 3, "N": 3, "R": 5, "Q": 10, "K": 1000}

# list of move directions (dx, dy, maxStep) for each linear-moving piece
# fmt: off
legal_moves = {
    "B": ((-1,-1, 8), (-1, 1, 8), ( 1,-1, 8), ( 1, 1, 8)),
    "R": ((-1, 0, 8), ( 0,-1, 8), ( 1, 0, 8), ( 0, 1, 8)),
    "Q": ((-1,-1, 8), (-1, 1, 8), ( 1,-1, 8), ( 1, 1, 8),
          (-1, 0, 8), ( 0,-1, 8), ( 1, 0, 8), ( 0, 1, 8)),
    "K": ((-1,-1, 1), (-1, 1, 1), ( 1,-1, 1), ( 1, 1, 1),
          (-1, 0, 1), ( 0,-1, 1), ( 1, 0, 1), ( 0, 1, 1)) }
# fmt: on


class Piece:
    """A chess piece."""

    def __init__(self, type, side):
        self.type = type
        self.side = side
        self.has_moved = False


class Move:
    """A chess move of a piece, from (x1, y1) to (x2, y2)."""

    def __init__(self, piece=None, val=0, x2=None, y2=None):
        self.piece = piece
        self.val = val
        self.x2, self.y2 = x2, y2
        self.next = None


class Board:
    """A state of the chess board."""

    def __init__(self):
        self.pos = []
        for y1 in range(0, 8):
            self.pos.append(8 * [None])
        back_row = "RNBQKBNR"
        for i in range(0, 8):
            self.pos[0][i] = Piece(back_row[i], 1)
            self.pos[1][i] = Piece("P", 1)
            self.pos[6][i] = Piece("P", 0)
            self.pos[7][i] = Piece(back_row[i], 0)
        self.side = 0
        self.ply = 0

    def print_repr(self):
        print("     a  b  c  d  e  f  g  h")
        for y in range(7, -1, -1):
            print(y + 1, ":", end=" ")
            for x in range(0, 8):
                p = self.pos[y][x]
                if p:
                    if p.side:
                        s = f" {p.type} "
                    else:
                        s = f"{{{p.type}}}"
                else:
                    s = " . "
                sys.stdout.write(s)
            print()
        print()

    def find_best_move(self):
        """Find and return the best move for current side."""

        # copy board
        b2 = copy.copy(self)

        # set up search for our turn
        b2.ply = self.ply + 1
        b2.side = 1 - self.side
        b2.best_move = Move(None, -9999)

        # for each of X's pieces on board
        for b2.y1 in range(0, 8):
            for b2.x1 in range(0, 8):
                # lift piece from starting position (x1, y1)
                piece = b2.pos[b2.y1][b2.x1]
                b2.pos[b2.y1][b2.x1] = None
                if piece and piece.side == self.side:
                    # for each possible move of piece, search for best next move
                    b2.piece = piece
                    p_type = piece.type
                    b2.p_repr = repr(b2.piece)

                    if p_type == "P":  # pawn:
                        if piece.side:
                            adv = 1
                        else:
                            adv = -1
                        move1Ok = b2.check_moves(((0, adv),), can_capture=False)
                        if not piece.has_moved and move1Ok:
                            b2.check_moves(((0, 2 * adv),), can_capture=False)
                        b2.check_moves(((1, adv), (-1, adv)), can_move=False)

                    elif p_type == "N":  # knight:
                        # fmt: off
                        b2.check_moves(((-1, -2), (-2, -1), ( 1, -2), ( 2, -1),
                                        ( 1,  2), ( 2,  1), (-1,  2), (-2,  1)))
                        # fmt: on

                    else:  # standard piece: try all legal moves for it
                        b2.find_best_move_linearly()

                # restore original position of our piece
                b2.pos[b2.y1][b2.x1] = piece

        # return best move and its value
        return b2.best_move

    def check_moves(self, pos_list, can_capture=True, can_move=True):
        """Check all moves from (x1, y1) to positions in pos_list. Updates self.best_move."""

        for dx, dy in pos_list:
            self.check_move(self.x1 + dx, self.y1 + dy, can_capture, can_move)

    def find_best_move_linearly(self):
        """Find the best move for standard piece at (x1, y1). Updates self.best_move."""

        for dx, dy, max_dist in legal_moves[self.piece.type]:
            # move starts with self.piece at (x1, y1)
            x2, y2 = self.x1, self.y1
            while max_dist > 0:
                x2 += dx
                y2 += dy
                if not self.check_move(x2, y2, True, True):
                    break
                max_dist -= 1

    def check_move(self, x2, y2, can_capture, can_move):
        """Check a single move of piece at (x1, y1) to (x2, y2). Updates self.best_move
        and returns True if successful."""

        # stop when we run off of board
        if x2 < 0 or y2 < 0 or x2 >= 8 or y2 >= 8:
            return False
        m = Move(self.piece, 0, x2, y2)
        m.x1, m.y1 = self.x1, self.y1
        piece2 = self.pos[y2][x2]

        if piece2:
            if can_capture and piece2.side == self.side:
                # if move is a capture: move value = piece value
                m.val = valuation[piece2.type]
            else:
                # stop if we run into our own piece
                return False

        elif not can_move:
            return False

        # if not at deepest ply level:
        if self.ply < 4:
            # make our actual move
            orig_has_moved = self.piece.has_moved
            self.piece.has_moved = True
            self.pos[y2][x2] = self.piece

            # make move for other side on board copy
            m2 = self.find_best_move()

            # subtract that move value from our value
            m.val -= m2.val
            m.next = m2

            # remove our piece from this position
            self.pos[y2][x2] = piece2
            self.piece.has_moved = orig_has_moved

        # add in board position value (center is best)
        m.val += 0.8 - (abs(3.5 - x2) + abs(3.5 - y2)) * 0.1

        # only keep move if best
        if m.val > self.best_move.val:
            self.best_move = m
        return not piece2

    def move(self, m):
        """Actually make move m."""

        self.pos[m.y2][m.x2] = self.pos[m.y1][m.x1]
        self.pos[m.y1][m.x1] = None


if __name__ == "__main__":
    b = Board()
    test_mode = 0

    # if given a starting-position-pattern filename, read in that file
    if len(sys.argv) == 2:
        if sys.argv[1] == "-t":
            test_mode = 1
        else:
            pos = []
            for line in open(sys.argv[1]):
                bd_line = re.match(r" *[1-8]:(.*)", line)
                if bd_line:
                    row = []
                    for p_type in re.findall(r"{*[A-Z.]}*", bd_line.group(1)):
                        if p_type == ".":
                            row.append(None)
                        else:
                            side = 1
                            if p_type[0] == "{":
                                side = 0
                                p_type = p_type[1]
                            row.append(Piece(p_type, side))
                    pos.append(row)
            pos.reverse()
            b.pos = pos

    while 1:
        b.print_repr()

        # ask human for a move and check it for basic validity
        while 1:
            print("Your move:", end=" ")
            sys.stdout.flush()
            h_in = "a2 a4"
            if test_mode:
                print(h_in)
            else:
                h_in = input()
            cmd = re.match(r"([a-h])([1-8])[^a-h1-8]+([a-h])([1-8])", h_in)
            if cmd:
                x1, y1 = ord(cmd.group(1)) - ord("a"), int(cmd.group(2)) - 1
                x2, y2 = ord(cmd.group(3)) - ord("a"), int(cmd.group(4)) - 1
                h_piece = b.pos[y1][x1]
                if not h_piece or h_piece.side != 1:
                    print(f"Not your piece at {chr(97 + x1)}{y1 + 1}")
                    continue
                h_move = Move(x2=x2, y2=y2)
                h_move.x1, h_move.y1 = x1, y1
                b.move(h_move)
                break
            print("? Expected a pair of coordinates")
        b.print_repr()

        # computer's turn:
        m = b.find_best_move()
        b.move(m)

        if test_mode:
            b.print_repr()
            break
