# 0 Manager
Keeps track of all entities in the system.

Runs update loop for entities.

## 0.1 Entities
- 1..* Flower
- 1..* Mushroom
- 2 Mate
- 1 Hermit
- 3 Swarm
- 0/1 Chameleon
- 0/1 Predator

# 1 Entity
Keeps track of position of entity in the ecosystem.

May optionally update location of entity (Drone = yes, Flower = no).

**Attributes:**
- uid: string - unique id of the entity, used for specific updates
- position: float vector - x, y, and z coordinates for the entity in the system

## 1.0 Plants
Describes physical plants in the system

### 1.0.1 Flower
Is activated or deactivated based on its level of polination.

**Attributes:**
- collision_radius: float - describes the sphere that contains the flower, used to avoid collision
- activation_radius: float - describes how close the boids have to get to activate the flower
- activated: boolean - true if the flower has been activated, false if not
- polination_threshold: int - the level of polination required for the plant to be activated
- polination_level: float - the current polination level of the flower, is increased when Swarm boids are nearby

### 1.0.2 Mushroom
Used as home-bases for the different boids

**Attributes:**
-k

## 1.1 Drone

### 1.1.0 Boid
Maintains simple system-level rules for e.g. not crashing or leaving flight zone.

##### Rules
1. Keep minimum distance to other boids
    - Avoids crashing into other boids
2. Limit speed
    - Speed should not exceed realistic limits
        - Should maybe depend on the physicality of the system?
3. Remain within bounds
    - Boids should not be able to leave the pre-determined flight zone

#### 1.1.1 Swarm


##### Rules

#### 1.1.2 Mate

##### Rules

#### 1.1.3 Hermit

##### Rules

#### 1.1.4 (Chameleon)

##### Rules

#### 1.1.5 (Predator)

##### Rules

