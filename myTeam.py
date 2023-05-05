# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util, sys
from game import Directions
import game
import distanceCalculator
from util import nearestPoint
from capture import halfGrid
import time
#################
# Team creation #
#################
currentFood = 0
foodlistLength = 0
initFoodListLength = 0
ourCapsules = []
enemyCapsules = []

def createTeam(firstIndex, secondIndex, isRed,
               first = 'Flex', second = 'Defense'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class generalAgents(CaptureAgent):
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    global foodlistLength
    foodlistLength = len(self.getFood(gameState).asList())

  def findPowerPellets(self, gameState):
    global ourCapsules
    global enemyCapsules
    if self.red:
      enemyCapsules = gameState.getBlueCapsules()
      ourCapsules = gameState.getRedCapsules()
    else:
      ourCapsules = gameState.getBlueCapsules()
      enemyCapsules = gameState.getRedCapsules()
    
  #rewrite this
  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
  
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    # time.sleep(0.1)
    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor
  
  def midIndex(self, gameState):
    if self.red:
      return gameState.data.layout.width / 2 - 1
    else:
      return gameState.data.layout.width / 2
    
  # determines how many enemies have crossed over
  # therefore, number of enemy ghosts = 2 - numAttackers
  def numAttackers(self, gameState):
    """
    Determines how many enemies have crossed over to steal pellets.
    The number of ghosts is equal to 2 - numAttackers(self, gameState).
    """
    numEnemies = 0
    for i in self.getOpponents(gameState):
      if gameState.getAgentState(i).isPacman:
        numEnemies += 1
    return numEnemies
  
  def isWinning(self, gameState):
    """
    Evaluates if we are winning or not.
    """
    return self.getScore(gameState) > 0
  
  #rewrite this
  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  #overwrite this in the flex and defense classes
  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  #overwrite this in the flex and defense classes
  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

class Flex(generalAgents):
  def getFeatures(self, gameState, action):

    if not self.isWinning(gameState):
      global currentFood
      global foodlistLength
      global initFoodListLength
      comparelength = len(self.getFood(gameState).asList())
      features = util.Counter()
      successor = self.getSuccessor(gameState, action)
      foodList = self.getFood(successor).asList()
      myPos = successor.getAgentState(self.index).getPosition()
      features['successorScore'] = -len(foodList)#self.getScore(successor)
      print(currentFood)
      
      print(comparelength, foodlistLength)
      if comparelength > foodlistLength:
        foodlistLength = comparelength
      if comparelength < foodlistLength:
        currentFood += 1
        foodlistLength = comparelength
      

      # Compute distance to the nearest food
      minDistance = 0
      if len(foodList) > 0: # This should always be True,  but better safe than sorry
        minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
        features['distanceToFood'] = minDistance
      
      # Compute the distance between us and the closest enemy
      minDistGhost = 999999999
      if successor.getAgentState(self.index).isPacman:
        for i in self.getOpponents(gameState):
          if not gameState.getAgentState(i).isPacman:
            minDistGhost = min(minDistGhost, self.getMazeDistance(myPos, successor.getAgentState(i).getPosition())) + 1
        features['criticalDistance'] = minDistGhost
      
      # See if we got a food pellet
      if currentFood > 0:
        features['food'] = self.getMazeDistance(self.start, successor.getAgentState(self.index).getPosition())
        if not successor.getAgentState(self.index).isPacman:
          features['returned'] = 99999
          currentFood = 0
      return features
    
    else:
      features = util.Counter()
      successor = self.getSuccessor(gameState, action)

      myState = successor.getAgentState(self.index)
      myPos = myState.getPosition()

      # Computes whether we're on defense (1) or offense (0)
      features['onDefense'] = 1
      if myState.isPacman: features['onDefense'] = 0

      # Computes distance to invaders we can see
      enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
      features['numInvaders'] = len(invaders)
      if len(invaders) > 0:
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
        features['invaderDistance'] = min(dists)

      if action == Directions.STOP: features['stop'] = 1
      rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
      if action == rev: features['reverse'] = 1

      return features

  def getWeights(self, gameState, action):
    if not self.isWinning(gameState):
      return {'successorScore': 50, 'criticalDistance': 1, 'distanceToFood': -1, 'food': -20, 'returned': 999}
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}
  
class Defense(generalAgents):
  def getFeatures(self, gameState, action):
    enemyCapsules = []
    ourCapsules = []
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if self.red:
      enemyCapsules = gameState.getBlueCapsules()
      ourCapsules = gameState.getRedCapsules()
    else:
      ourCapsules = gameState.getBlueCapsules()
      enemyCapsules = gameState.getRedCapsules()
    
    # If the distance bewteen the enemy to the power pellets is greater than the distance between us and the power pellets, do something.
    # Also take into account the distance between us and the enemy, as well as us to the power pellets
    # We also need to take into account the distance between us and the cutoff points/closest exits.
    #Instead of reversing here, lets do something else. Have it hover around the area between power pellet and enemy
    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}


#test