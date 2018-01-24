'''
=====================================================================================================================================================
FILE	: agent.py
NAME	: Rohit Rane
EMAIL	: rrrane@indiana.edu
=====================================================================================================================================================
'''

#Logical Constructs:

# Symbol  Semantics
# ------  -----------------------------------------
# 1       Pit in THIS tile
# 2       Pit in LEFT tile
# 3       Pit in RIGHT tile
# 4       Pit in UP tile
# 5       Pit in DOWN tile
# 6       Breeze in THIS tile
# 7       Breeze in LEFT tile
# 8       Breeze in RIGHT tile
# 9       Breeze in UP tile
# 10      Breeze in DOWN tile
# 11      Wumpus in THIS tile
# 12      Wumpus in LEFT tile
# 13      Wumpus in RIGHT tile
# 14      Wumpus in UP tile
# 15      Wumpus in DOWN tile
# 16      Stench in THIS tile
# 17      Stench in LEFT tile
# 18      Stench in RIGHT tile
# 19      Stench in UP tile
# 20      Stench in DOWN tile

import random
import math
import dpll
import copy

class Agent:

  def __init__(self):
    self.prev_x = 1
    self.prev_y = 1
    self.cur_x = 1
    self.cur_y = 1
    self.last_action = 'GAME_START'
    self.wump = set()
    self.no_wump = {(1,1)}
    self.arrow = True
    self.safe = {(1,1)}
    self.visited = {(1,1)}
    self.breeze = set()
    self.no_breeze = set()
    self.stench = set()
    self.no_stench = set()
    self.pit = set()
    self.no_pit = {(1,1)}
    self.block = {(0,0), (0,1), (1,0)}
    self.no_block = {(1,1)}
    self.base_cnf = [{-1,7},{-1,8},{-1,9},{-1,10},{-6,2,3,4,5},{-2,6},{-3,6},{-4,6},{-5,6},{-11,17},{-11,18},{-11,19},{-11,20},{-16,12,13,14,15},{-12,16},{-13,16},{-14,16},{-15,16}]
    
  
  def get_action(self):
    
    self.prev_x, self.prev_y = self.cur_x, self.cur_y
    nbr = self.get_neighbours(self.cur_x, self.cur_y)
    
    #Look for a Wumpus in neighbouring cells
    if self.arrow:
      for n in nbr:
        if n in self.wump:
          self.last_action = self.shoot(n)
          return self.last_action

    #Find out visited and not visited safe neighbours
    nvsafenbr   = []  #Not visited safe neighbours
    vsafenbr    = []  #Visited safe neighbours

    for n in nbr:
      if n in self.safe:
        if n in self.visited:
          vsafenbr.append(n)
        elif not n in self.block:
          nvsafenbr.append(n)
          
    self.last_action = self.select_action(vsafenbr, nvsafenbr)
    return self.last_action
    pass

  def give_senses(self, location, breeze, stench):
    self.prev_x, self.prev_y = self.cur_x, self.cur_y
    self.cur_x, self.cur_y = location[0], location[1]

        
    #Check for wall to the right and to the top and update the knowledge base
    if (not self.last_action == 'GAME_START') and (not self.last_action[0:5] == 'SHOOT') and ( self.cur_x == self.prev_x ) and ( self.cur_y == self. prev_y ):
      if ( self.last_action == 'MOVE_RIGHT' ):
        self.block.add( ( self.cur_x + 1, self.cur_y ) )
      elif ( self.last_action == 'MOVE_UP' ):
        self.block.add( ( self.cur_x, self.cur_y + 1 ) )
        
    else:
      x , y = self.cur_x , self.cur_y
      self.visited.add( ( x , y ) )
      self.no_wump.add( ( x , y ) )
      self.no_pit.add( ( x , y ) )
      self.safe.add( ( x , y ) )
      self.no_block.add( ( x , y ) )
      #assume wall to the left and to the bottom and update the knowledge base
      self.block.add( ( self.cur_x , 0 ) )
      self.block.add( ( 0 , self.cur_y ) )
      self.no_wump.add( ( self.cur_x , 0 ) )
      self.no_wump.add( ( 0 , self.cur_y ) )
      self.no_pit.add( ( self.cur_x , 0 ) )
      self.no_pit.add( ( 0 , self.cur_y ) )
      
      #Update Breeze and Stench percepts
      if breeze:
        self.breeze.add( ( x , y ) )
      else:
        self.no_breeze.add( ( x , y ) )

      if stench:
        self.stench.add( ( x , y ) )
      else:
        self.no_stench.add( (x , y ) )

      self.update_knowledge_base((x, y))
    
    pass

  def killed_wumpus(self):
    w = self.wump.pop()
    self.no_wump.add(w)
    self.arrow = False
    
    pass

  def get_neighbours(self, x, y):
    return { ( x - 1 , y ) , ( x + 1, y ) , ( x , y - 1 ), (x , y + 1 ) }

  def select_action( self, vsafenbr, nvsafenbr ):
    
    nbr = []
    n = None
    if len( nvsafenbr ) > 0:
      nbr = nvsafenbr
      n = random.choice( nbr )
    else:
      nbr = vsafenbr
      tuples = set()
      nvsafecells = self.safe - self.visited
      if len(nvsafecells) > 0:
        for u in nvsafecells:
          for k in nbr:
            dist = abs(u[0] - k[0]) + abs(u[1] - k[1])
            tuples.add((u, k, dist))
        
        minval = math.inf
        for t in tuples:
          if t[2] < minval:
            minval = t[2]
            n = t[1]
      else:
        n = random.choice( nbr )
    
    
    if not ( n is None ):
      x , y = n[0] , n[1]

      if( x == self.cur_x - 1 ):
        return 'MOVE_LEFT'

      if( x == self.cur_x + 1 ):
        return 'MOVE_RIGHT'

      if( y == self.cur_y + 1 ):
        return 'MOVE_UP'

      if( y == self.cur_y - 1 ):
        return 'MOVE_DOWN'
    else:
      return 'QUIT'

    pass

  def shoot(self, n):
    x, y = n[0], n[1]

    if( x == self.cur_x - 1 ):
      return 'SHOOT_LEFT'

    if( x == self.cur_x + 1 ):
      return 'SHOOT_RIGHT'

    if( y == self.cur_y + 1 ):
      return 'SHOOT_UP'

    if( y == self.cur_y - 1 ):
      return 'SHOOT_DOWN'

  

  def update_knowledge_base(self, n):
    
    neighbours = self.get_neighbours(n[0],n[1])
    neighbours = (neighbours - self.block) - self.safe
    
    for nbr in neighbours:
      self.update_wumpus(nbr)
      self.update_pit(nbr)
      self.update_safe(nbr)

    neighbours = neighbours  - self.safe
    x, y = n[0], n[1]

    if (x - 1,y) in neighbours:
      self.update_wumpus_left(n)
      self.update_pit_left(n)
      self.update_safe((x - 1,y))

    neighbours = neighbours  - self.safe
    
    if (x + 1,y) in neighbours:
      self.update_wumpus_right(n)
      self.update_pit_right(n)
      self.update_safe((x + 1,y))
      
    neighbours = neighbours  - self.safe
    
    if (x,y + 1) in neighbours:
      self.update_wumpus_up(n)
      self.update_pit_up(n)
      self.update_safe((x,y + 1))

    neighbours = neighbours  - self.safe
    
    if (x,y - 1) in neighbours:
      self.update_wumpus_down(n)
      self.update_pit_down(n)
      self.update_safe((x,y - 1))
    
    pass

  def update_safe(self, n):
    if n in self.no_wump and n in self.no_pit:
      self.safe.add(n)
    pass
  
  def update_wumpus( self, n ):
    alpha = copy.deepcopy(self.base_cnf)
    self.get_cnf(alpha, n)

    alpha_wump = copy.deepcopy(alpha)
    alpha_no_wump = copy.deepcopy(alpha)
    alpha_wump.append({-11})
    alpha_no_wump.append({11})
    s = dpll.Solver(alpha_wump)
    if not s.solve():
      self.wump.add(n)
      return

    s = dpll.Solver(alpha_no_wump)
    if not s.solve():
      self.no_wump.add(n)
      
    pass

  def update_wumpus_left( self, n ):
    alpha = copy.deepcopy(self.base_cnf)
    self.get_cnf(alpha, n)

    alpha_wump = copy.deepcopy(alpha)
    alpha_no_wump = copy.deepcopy(alpha)
    alpha_wump.append({-12})
    alpha_no_wump.append({12})
    s = dpll.Solver(alpha_wump)
    if not s.solve():
      self.wump.add((n[0]-1,n[1]))
      return

    s = dpll.Solver(alpha_no_wump)
    if not s.solve():
      self.no_wump.add((n[0]-1,n[1]))
      
    pass

  def update_wumpus_right( self, n ):
    alpha = copy.deepcopy(self.base_cnf)
    self.get_cnf(alpha, n)

    alpha_wump = copy.deepcopy(alpha)
    alpha_no_wump = copy.deepcopy(alpha)
    alpha_wump.append({-13})
    alpha_no_wump.append({13})
    s = dpll.Solver(alpha_wump)
    if not s.solve():
      self.wump.add((n[0]+1,n[1]))
      return

    s = dpll.Solver(alpha_no_wump)
    if not s.solve():
      self.no_wump.add((n[0]+1,n[1]))
      
    pass

  def update_wumpus_up( self, n ):
    
    alpha = copy.deepcopy(self.base_cnf)
    self.get_cnf(alpha, n)
    

    alpha_wump = copy.deepcopy(alpha)
    alpha_no_wump = copy.deepcopy(alpha)
    alpha_wump.append({-14})
    alpha_no_wump.append({14})
    s = dpll.Solver(alpha_wump)
    if not s.solve():
      self.wump.add((n[0],n[1]+1))
      return

    s = dpll.Solver(alpha_no_wump)
    if not s.solve():
      self.no_wump.add((n[0],n[1]+1))
      
    pass

  def update_wumpus_down( self, n ):
    alpha = copy.deepcopy(self.base_cnf)
    self.get_cnf(alpha, n)

    alpha_wump = copy.deepcopy(alpha)
    alpha_no_wump = copy.deepcopy(alpha)
    alpha_wump.append({-15})
    alpha_no_wump.append({15})
    s = dpll.Solver(alpha_wump)
    if not s.solve():
      self.wump.add((n[0],n[1]-1))
      return

    s = dpll.Solver(alpha_no_wump)
    if not s.solve():
      self.no_wump.add((n[0],n[1]-1))
      
    pass
  
  def update_pit( self, n ):
    alpha = copy.deepcopy(self.base_cnf)
    self.get_cnf(alpha, n)

    alpha_pit = copy.deepcopy(alpha)
    alpha_no_pit = copy.deepcopy(alpha)
    alpha_pit.append({-1})
    alpha_no_pit.append({1})
    s = dpll.Solver(alpha_pit)
    if not s.solve():
      self.pit.add(n)
      return

    s = dpll.Solver(alpha_no_pit)
    if not s.solve():
      self.no_pit.add(n)
      
    pass

  def update_pit_left( self, n ):
    alpha = copy.deepcopy(self.base_cnf)
    self.get_cnf(alpha, n)

    alpha_pit = copy.deepcopy(alpha)
    alpha_no_pit = copy.deepcopy(alpha)
    alpha_pit.append({-2})
    alpha_no_pit.append({2})
    s = dpll.Solver(alpha_pit)
    if not s.solve():
      self.pit.add((n[0]-1, n[1]))
      return

    s = dpll.Solver(alpha_no_pit)
    if not s.solve():
      self.no_pit.add((n[0]-1, n[1]))
      
    pass

  def update_pit_right( self, n ):
    alpha = copy.deepcopy(self.base_cnf)
    self.get_cnf(alpha, n)

    alpha_pit = copy.deepcopy(alpha)
    alpha_no_pit = copy.deepcopy(alpha)
    alpha_pit.append({-3})
    alpha_no_pit.append({3})
    s = dpll.Solver(alpha_pit)
    if not s.solve():
      self.pit.add((n[0]+1, n[1]))
      return

    s = dpll.Solver(alpha_no_pit)
    if not s.solve():
      self.no_pit.add((n[0]+1, n[1]))
      
    pass

  def update_pit_up( self, n ):
    alpha = copy.deepcopy(self.base_cnf)
    self.get_cnf(alpha, n)

    alpha_pit = copy.deepcopy(alpha)
    alpha_no_pit = copy.deepcopy(alpha)
    alpha_pit.append({-4})
    alpha_no_pit.append({4})
    s = dpll.Solver(alpha_pit)
    if not s.solve():
      self.pit.add((n[0], n[1] + 1))
      return

    s = dpll.Solver(alpha_no_pit)
    if not s.solve():
      self.no_pit.add((n[0], n[1] + 1))
      
    pass

  def update_pit_down( self, n ):
    alpha = copy.deepcopy(self.base_cnf)
    self.get_cnf(alpha, n)

    alpha_pit = copy.deepcopy(alpha)
    alpha_no_pit = copy.deepcopy(alpha)
    alpha_pit.append({-5})
    alpha_no_pit.append({5})
    s = dpll.Solver(alpha_pit)
    if not s.solve():
      self.pit.add((n[0], n[1]-1))
      return

    s = dpll.Solver(alpha_no_pit)
    if not s.solve():
      self.no_pit.add((n[0], n[1]-1))
      
    pass

  def get_cnf( self , alpha , n ):
    #look for pit
    if n in self.pit:
      alpha.append({1})
    elif n in self.no_pit:
      alpha.append({-1})
      
    if (n[0] - 1, n[1]) in self.pit:
      alpha.append({2})
    elif (n[0] - 1, n[1]) in self.no_pit:
      alpha.append({-2})
      
    if (n[0] + 1, n[1]) in self.pit:
      alpha.append({3})
    elif (n[0] + 1, n[1]) in self.no_pit:
      alpha.append({-3})
      
    if (n[0], n[1] + 1) in self.pit:
      alpha.append({4})
    elif (n[0], n[1] + 1) in self.no_pit:
      alpha.append({-4})
      
    if (n[0], n[1] - 1) in self.pit:
      alpha.append({5})
    elif (n[0], n[1] - 1) in self.no_pit:
      alpha.append({-5})

    #look for Wumpus

    if n in self.wump:
      alpha.append({11})
    elif n in self.no_wump:
      alpha.append({-11})
      
    if (n[0] - 1, n[1]) in self.wump:
      alpha.append({12})
    elif (n[0] - 1, n[1]) in self.no_wump:
      alpha.append({-12})
      
    if (n[0] + 1, n[1]) in self.wump:
      alpha.append({13})
    elif (n[0] + 1, n[1]) in self.no_wump:
      alpha.append({-13})
      
    if (n[0], n[1] + 1) in self.wump:
      alpha.append({14})
    elif (n[0], n[1] + 1) in self.no_wump:
      alpha.append({-14})
      
    if (n[0], n[1] - 1) in self.wump:
      alpha.append({15})
    elif (n[0], n[1] - 1) in self.no_wump:
      alpha.append({-15})

    #look for Breeze
    if (n[0], n[1]) in self.breeze:
      alpha.append({6})
    elif (n[0], n[1]) in self.no_breeze:
      alpha.append({-6})
      
    if (n[0] - 1, n[1]) in self.breeze:
      alpha.append({7})
    elif (n[0] - 1, n[1]) in self.no_breeze:
      alpha.append({-7})
      
    if (n[0] + 1, n[1]) in self.breeze:
      alpha.append({8})
    elif (n[0] + 1, n[1]) in self.no_breeze:
      alpha.append({-8})
      
    if (n[0], n[1] + 1) in self.breeze:
      alpha.append({9})
    elif (n[0], n[1] + 1) in self.no_breeze:
      alpha.append({-9})
      
    if (n[0], n[1] - 1) in self.breeze:
      alpha.append({10})
    elif (n[0], n[1] - 1) in self.no_breeze:
      alpha.append({-10})

    #look for Stench
    if self.arrow:
      if (n[0], n[1]) in self.stench:
        alpha.append({16})
      elif (n[0], n[1]) in self.no_stench:
        alpha.append({-16})
    
      if (n[0] - 1, n[1]) in self.stench:
        alpha.append({17})
      elif (n[0] - 1, n[1]) in self.no_stench:
        alpha.append({-17})
      
      if (n[0] + 1, n[1]) in self.stench:
        alpha.append({18})
      elif (n[0] + 1, n[1]) in self.no_stench:
        alpha.append({-18})
      
      if (n[0], n[1] + 1) in self.stench:
        alpha.append({19})
      elif (n[0], n[1] + 1) in self.no_stench:
        alpha.append({-19})
      
      if (n[0], n[1] - 1) in self.stench:
        alpha.append({20})
      elif (n[0], n[1] - 1) in self.no_stench:
        alpha.append({-20})
        
    else:
      alpha.append({-16})
      alpha.append({-17})
      alpha.append({-18})
      alpha.append({-19})
      alpha.append({-20})
