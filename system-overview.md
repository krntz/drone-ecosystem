# 0 `SystemManager`
Keeps track of all entities in the system.

Runs update loop for entities.

**Attributes:**
- `time_step`: `float` - How often, in seconds, one iteration of the update loop is run

## 0.1 Entities
- 1..* `Flower`
- 1..* `Mushroom`
- 1..* `Floor`
- 2 `Mate`
- 1 `Hermit`
- 3 `Swarm`
- 0/1 `Chameleon`
- 0/1 `Predator`
- 0..* `Tracker`

# 1 Entity
Main class for representing any entity in the system.

**Attributes:**
- `uid`: `string` - Unique id of the entity, used for specific updates
- `position`: `float vector` - x, y, and z coordinates for the entity in the system

## 1.0 Plants
Represents plants in the system.

### 1.0.1 `Flower`
Is activated or deactivated based on its level of polination.

Main focus of attraction for `Swarm` `Boid`s.

Should perhaps take some time to "synthesize" pollen into food so that `Swarm` and `Mate` do not activate at the same time?

**Attributes:**
- `collision_radius`: `float` - describes the sphere that contains the `Flower`, used to avoid collision
- `activation_radius`: `float` - describes how close the `Boid`s have to get to activate the `Flower`
- `active`: `boolean` - `True` when `polination_level` reaches `polination_level`; `False` when `polination_level` reaches 0
- `polination_threshold`: `int` - the `polination_level` required for the plant to be activated
- `polination_level`: `float` - the current polination level of the `Flower`, is increased when `Swarm`s are nearby

### 1.0.2 `Mushroom`
Home-base for `Swarm`s and `Mate`s.

**Attributes:**
- `collision_radius`: `float` - describes the sphere that contains the `Mushroom`, used to avoid collision
- `activation_radius`: `float` - describes how close the `Boid`s have to get to activate the `Mushroom`
- `residents`: list of `Boids` - list of the `Boids`s that call this `Mushroom` home
- `occupants`: list of `Boids` - list of the `Boids`s that are currently in the `Mushroom`
- `current_food`: `int` - The current amount of food in the `Mushroom`
- `food_threshold`: `int` - The amount of food required for the `Mushroom` to start activating the `Floor` around it
- `floor`: `Floor` - The section of `Floor` around the `Mushroom`

### 1.0.3 `Floor`
Represents sections of the floor in the ecosystem.

Becomes active when a nearby `Mushroom` is saturated with food, becomes inactive when a `Hermit` has fed from it.

**Attributes:**
- `radius`: `float` - The radius of the `Floor` section, in meters
- `active`: `boolean` - `True` if the `Floor` section has been activated by a `Mushroom`; `False` when `available_food` is 0
- `available_food`: `int` - How much food is available for the `Hermit` to feed on

## 1.1 `Boid`
Maintains simple system-level rules for e.g. not crashing or leaving `flight_zone`.

More behaviour-specific rules are described by the `Boid` subtypes.
(NOTE: All rules should be implemented centrally and then called from each `Boid` subtype for maintainability.)

Currently represents one [Bitcraze Crazyflie 2.1](https://www.bitcraze.io/products/crazyflie-2-1/).

**Attributes:**
- `visual_range`: `float` - How many meters around the `Boid` it is able to detect other `Boid`s
- `detected_boids`: list of `string`s - List of the `uid`s of the `Boid`s within `visual_range`; updated by `SystemManager`
- `type`: `string` - Which of the `Boid` subtypes the current `Boid` is
- `velocity`: `float` vector - How many meters per `time_step` the `Boid` moves in x, y, and z directions
- `minimum_distance`: `float` - How close the `Boid` can get to another `Boid`; measured in meters

#### Rules
1. `avoid_others`
2. `avoid_hovering_above`
3. `limit_speed`
4. `keep_within_bounds`

#### Available Rules
* `fly_towards_center`
    - `Boid` should fly towards the center of the `Boid`s within its `visual_range`
    - Standard `Boid` rule #1
* `avoid_others`
    - Keep `minimum_distance` to other `Boid`s
    - Avoids crashing into other `Boid`s
    - Standard `Boid` rule #2
* `match_velocity`
    - Try to match `velocity` of the `Boid`s within its `visual_range`
    - Standard `Boid` rule #3
* `move_towards_place`
    - Can be used to move the `Boid` towards e.g. a plant
* `limit_speed`
    - Speed should not exceed realistic limits
    - Should maybe depend on the physicality of the system?
* `keep_within_bounds`
    - `Boid`s should not be able to leave the pre-determined flight zone
* `avoid_hovering_above`
    - A `Drone` hovering above another `Drone` leads to unstable behaviour
    - `Drone`s should prefer to stay at least 0.3 meters above each other

### 1.1.0 `Swarm`
Moves between their home-base `Mushroom` and `Flower`s within their `sensory_range` to pollinate.

**Attributes:**
- `home`: `string` - The `uid` of the `Mushroom` the `Boid` calls home
- `polination_factor`: `int` - How much pollen the `Boid` can deposit in one `time_step`
- `sensory_range`: `float` - How many meters around the `Swarm` is able to detect inactive `Flower`s

#### Rules
* `fly_towards_center`
    - Should only be with regards to `Boid`s of the same `type`
* `match_velocity`
    - Should only be with regards to `Boid`s of the same `type`
* `move_towards_place`
    - If inactive `Flower` is detected, move towards it; otherwise, move towards `home`

### 1.1.1 `Mate`
When `Swarm` has finished pollinating, will exit its home and move towards the active `Flower`s.

**Attributes:**
- `home`: `string` - The `uid` of the `Mushroom` the `Mate` calls home
- `at_home`: `boolean` - `True` if the `Mate` is at its `home`; otherwise `False`
- `sensory_range`: `float` - How many meters around the `Mate` is able to detect active `Flower`s
- `carrying_capacity`: `int` - How much food the `Mate` can carry
- `current_food`: `int` - How much food the `Mate` is currently carrying
- `collection_rate`: `int` - How much food the `Mate` can gather in one `time_step`
- `deposit_rate`: `int` - How much food the `Mate` can deposit at its `home` in one `time_step`
- `depositing`: `boolean` - `True` if the `Mate` is currently depositing food at its `home`; `False` otherwise

#### Rules
* `fly_towards_center`
    - Should only be with regards to `Boid`s of the same `type`
* `match_velocity`
    - Should only be with regards to `Boid`s of the same `type`
* `move_towards_place`
    - If active `Flower` is detected, move towards it; otherwise, move towards `home`

### 1.1.2 `Hermit`
When a `Mushroom` has started dispersing food, the `Hermit` will move towards the `Floor` around the `Mushroom` and start feeding on it.

Prefers to hang around the lower levels of the ecosystem.

**Attributes:**
- `eating_rate`: `int` - How fast the `Hermit` can eat food from the `Floor`

#### Rules
* `move_towards_place`
    - If active `Floor` is detected, move towards it; otherwise, wander around

### 1.1.3 (`Chameleon`)

#### Rules

### 1.1.4 (`Predator`)

#### Rules

## 1.2 `Tracker`
Represents the [Vive Trackers](https://www.vive.com/eu/accessory/tracker3/) carried by the users.

# 2 `SwarmController`

## 2.0 `CrazyflieSwarmController`
Interface between the `SystemManager` and the [Bitcraze Python API](https://www.bitcraze.io/documentation/repository/crazyflie-lib-python/master/).
