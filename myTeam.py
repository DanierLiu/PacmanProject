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
crossoverPositions = []
enemyCapsules = []
ourCapsules = []

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

#########################
##### General Agent #####
#########################

class generalAgents(CaptureAgent):
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    global foodlistLength
    foodlistLength = len(self.getFood(gameState).asList())
    self.findCrossovers(gameState)
    self.findCapsules(gameState)

  # Find where the power pellets in the map are:
  def findCapsules(self, gameState):
    global enemyCapsules
    global ourCapsules
    if self.red:
      enemyCapsules = gameState.getBlueCapsules()
      ourCapsules = gameState.getRedCapsules()
    else:
      ourCapsules = gameState.getBlueCapsules()
      enemyCapsules = gameState.getRedCapsules()
  
  # Find the access positions
  def findCrossovers(self, gameState):
    """
    Returns a list of location tuples.
    Each tuple corresponds to where agents can cross over.
    """
    global crossoverPositions
    if self.red:
      for pos in gameState.getRedFood():
        if pos[0] == gameState.data.layout.width / 2 - 1:
          if not gameState.hasWall(pos[0] + 1, pos[1]):
            crossoverPositions.append(pos)
  
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

    print(features * weights)
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








######################
##### Flex Agent #####
######################

class Flex(generalAgents):
  def getFeatures(self, gameState, action):

    # defense features
    if not self.isWinning(gameState):
      global crossoverPositions
      global currentFood
      global foodlistLength
      global initFoodListLength
      features = util.Counter()
      successor = self.getSuccessor(gameState, action)
      foodList = self.getFood(successor).asList()
      myPos = successor.getAgentState(self.index).getPosition()
      features['successorScore'] = -len(foodList)

      

      # Compute distance to the nearest food
      minDistance = 0
      if len(foodList) > 0: # This should always be True,  but better safe than sorry
        minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
        features['distanceToFood'] = minDistance
      
      # Compute the distance between us and the closest enemy
      # This actually doesn't matter?
      minDistGhost = 999999999
      if successor.getAgentState(self.index).isPacman:
        for i in self.getOpponents(gameState):
          if not gameState.getAgentState(i).isPacman:
            minDistGhost = min(minDistGhost, self.getMazeDistance(myPos, successor.getAgentState(i).getPosition())) + 1
        features['criticalDistance'] = minDistGhost
      
      # Compute the distance between us and the closest enemy power pellet
      distToCaps = 0
      if successor.getAgentState(self.index).isPacman:
        distToCaps = min([self.getMazeDistance(myPos, cap) for cap in enemyCapsules])
      features['capsule'] = distToCaps
          
      # If the distance between us and the capsule is less than the distance between us and the enemy, go for the capsule:
      # While the global variable is capsule is active, prioritize food and run back to base when remaining moves is less
      # Than the distance between us and the distance back.
      if distToCaps < minDistGhost:
        features['goCaps'] = 999
      

      # Heuristic to space out agents.
      # If the distance to the closest food is less than the distance between the closest enemy and that food:
      # If the enemy comes after us, we should go for the power pellet?
      
      # If the distance to the closest food and back home is less than the distance between the 

      # See if we got a food pellet
      # This works for now, but won't work in the future since we're going back to the start rather than entry position.
      # I'll find entry positions.
      if successor.getAgentState(self.index).numCarrying > 0:

        min_dist_to_mid = 99999999
        for boundary_pos in crossoverPositions:
          dist_to_mid = self.getMazeDistance(successor.getAgentState(self.index).getPosition(), boundary_pos)
          if dist_to_mid < min_dist_to_mid:
            min_dist_to_mid = dist_to_mid

        features['boundary'] = min_dist_to_mid
        if not successor.getAgentState(self.index).isPacman:
          features['returned'] = 10
          currentFood = 0


      print(features)
      print("^^^ is not winning")
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

      print(features)
      print("is winning")
      return features

  # Weights should be negative if the lower the numbers is better.
  # For example, the lower the distance between us and an enemy, the worse the choice is, so weight is positive.
  # However, the lower the distance between us and food is, the better the choice is, so weight is negative.
  # Food and returned are negligible for now.
  def getWeights(self, gameState, action):
    if not self.isWinning(gameState):
      return {'successorScore': 50, 'criticalDistance': 1, 'distanceToFood': -1, 'capsule': -1, 'goCaps': 1, 'boundary': -1, 'returned': 1}
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}








#########################
##### Defense Agent #####
#########################

# This first defense will be getting the closest to the power pellets, while the second will get entries after it attacked
class Defense(generalAgents):
  def getFeatures(self, gameState, action):
    global crossoverPositions
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

    
    
    # Compute the distance the closest enemy to the middle is:
    # There is something wrong with this section:
    # enemyDistToMid = 999999999
    # closestEnemy = 0
    # posUnderAttack = (0,0)
    # for e in enemies:
    #   for entry in crossoverPositions:
    #     tempDist = self.getMazeDistance(e.getPosition(), entry)
    #     if tempDist < enemyDistToMid:
    #       enemyDistToMid = tempDist
    #       closestEnemy = e
    #       posUnderAttack = entry
    
    # if self.getMazeDistance(myPos, posUnderAttack) < enemyDistToMid:
    #   features['goMid'] = 1
      


    # Calculate distance between the enemy and the closest capsule to them
    # enemyDistToCaps = 99999999999
    # closestCapsuleToEnemy = (0,0)
    # if len(invaders) > 0:
    #   for enemy in invaders:
    #     for c in ourCapsules:
    #       d = self.getMazeDistance(enemy.getPosition(), c)
    #       if d < enemyDistToCaps:
    #         enemyDistToCaps = d
    #         closestCapsuleToEnemy = c
    
    # Calculate distance between us and said capsule.
    # distToCaps = self.getMazeDistance(myPos, closestCapsuleToEnemy)

    # if enemyDistToCaps > distToCaps:
    #   features['intruderCapsule'] = -1
    # else:
    #   features['intruderCapsule'] = 1
    # If features['intruderCapsule'] = 1, we want to move to try and intercept the attacker.
    # If that is too far for us and they will certainly get the power pellet, move to the cutoff point at mid.
    # If we are trying to get to the intruder, we want to intercept at the path
    
    # If the distance bewteen the enemy to the power pellets is greater than the distance between us and the power pellets, do something.
    # Also take into account the distance between us and the enemy, as well as us to the power pellets
    # We also need to take into account the distance between us and the cutoff points/closest exits.
    # Instead of reversing here, lets do something else. Have it hover around the area between power pellet and enemy
    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2, 'IntruderCapsule': 1}


#test