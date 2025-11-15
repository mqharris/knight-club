# Knight Club - Game System Manifesto

## Overview
Knight Club is a slow-paced, text-based RPG where players create and manage knights, equipping them with gear and sending them into battle against monsters. The game emphasizes patience and strategic decision-making.

## Core Concepts

### User System
- Users create accounts with username and password
- Passwords are hashed with bcrypt for security
- Each user can have multiple knights
- Users access their account through a web-based login page

### Knight System

#### Knight Classes
There are four knight classes, each with distinct visual representation:
1. **Knight** - Balanced warrior with sword and shield
2. **Paladin** - Holy warrior with divine powers, uses mace and blessed shield
3. **Lancer** - Agile fighter with long-range spear attacks
4. **Templar** - Heavily armored crusader with broadsword and large shield

#### Knight Attributes
- **Name**: Unique identifier per user (user can have multiple knights with different names)
- **Class**: One of the four classes listed above
- **Level**: Starting at 1, max level 10
- **Age**: Days since knight creation
- **Hit Points (HP)**: Knight's current health
- **Stats**: Strength, Defense, Agility, Intelligence (base value: 10 each)

#### Knight Creation Rules
- Users can create their first knight at any time
- Additional knights can only be created when ALL existing knights are level 10
- Knights start at level 1 with base stats

#### Knight Healing
- Knights regenerate health passively
- Healing rate: 1 HP per 15 minutes
- Healing occurs whether the player is online or offline

### Equipment System

#### Equipment Slots
Each knight has 11 equipment slots:
1. Weapon
2. Shield
3. Helm
4. Chest
5. Cape
6. Belt
7. Gloves
8. Pants
9. Boots
10. Ring (slot 1)
11. Ring (slot 2)

#### Equipment Effects
- Equipment modifies knight stats
- Better equipment provides higher stat bonuses
- Equipment can affect: Strength, Defense, Agility, Intelligence, Max HP

### Stats System

#### Primary Stats
1. **Strength**: Increases attack damage
2. **Defense**: Reduces incoming damage (armor value)
3. **Agility**: Determines attack speed and turn order
4. **Intelligence**: May affect special abilities (future implementation)

#### Derived Stats
- **Max HP**: Base health capacity
- **Armor**: Direct damage reduction from Defense stat
- **Attack Damage**: Based on Strength stat
- **Attack Speed**: Based on Agility stat

## Battle System

### Battle Initiation
- Player clicks the "BATTLE" button on a knight's page
- Player selects difficulty: Easy, Medium, Hard
- System creates a Kubernetes job to process the battle
- Battle runs asynchronously and reports results when complete

### Monster Selection
- Monsters are selected based on difficulty tier
- Selection is semi-random within the tier
- **Easy Tier**:
  - Level 1 Slime (starter monster)
  - Giant Rat
  - Weak Goblin
- **Medium Tier**:
  - Forest Wolf
  - Goblin Warrior
  - Troglodite
- **Hard Tier**:
  - Orc
  - Giant Spider

### Combat Mechanics

#### Turn Order
- Turn order determined by Agility stat
- Higher agility acts first
- Each combatant takes turns attacking

#### Damage Calculation
```
Damage Dealt = Attacker's Attack Damage - Defender's Armor
Minimum Damage = 1 (attacks always do at least 1 damage)
```

#### Combat Flow
1. Compare agility: determine who attacks first
2. Attacker deals damage to defender
3. Defender's HP is reduced
4. Roles switch for next turn
5. Combat continues until one combatant reaches 0 HP

#### Battle Example (Naked Knight vs Level 1 Slime)
- Naked knight has base stats (10 in each)
- Knight has no equipment, therefore minimal armor
- Level 1 Slime deals consistent damage per attack
- Over the course of a full battle, slime deals approximately 4 HP damage to naked knight
- Knight can defeat slime but will need time to heal afterward

### Battle Results
- Victory: Knight gains experience, may level up, may receive loot
- Defeat: Knight loses HP (cannot go below 1 HP), no experience gained
- Battle log shows turn-by-turn actions
- Results are saved to database

### Battle Processing
- Battles run as Kubernetes Jobs
- Job contains battle logic and outcome calculation
- Job updates knight's HP and experience in database
- Job records battle history for player review

## Progression System

### Experience and Leveling
- Knights gain experience from victories
- Reaching experience threshold increases level
- Level cap: 10
- Stats may increase with level (implementation pending)

### Equipment Acquisition
- Equipment drops from defeated monsters
- Drop rates vary by monster and difficulty
- Better equipment from harder difficulties
- Equipment must be manually equipped by player

#### Equipment Tiers
1. **Wooden Tier** (Easy monsters):
   - Wooden Sword, Wooden Shield, Wooden Helmet, Wooden Chest Armor, Wooden Gloves, Wooden Pants, Wooden Boots, Wooden Ring
   - Low stat bonuses
   
2. **Stone Tier** (Medium monsters):
   - Stone Axe, Stone Shield, Stone Helmet, Stone Chest Armor, Stone Gloves, Stone Pants, Stone Boots
   - Medium stat bonuses
   
3. **Iron Tier** (Hard monsters):
   - Iron Sword, Iron Axe, Iron Shield, Iron Helmet, Iron Chest Armor, Iron Gloves, Iron Pants, Iron Boots
   - High stat bonuses
   
4. **Special/Epic Items**:
   - Silk Cape (dropped by Giant Spider): +2 defense, +2 agility
   - Additional epic items to be added

#### Materials
- Spider Silk: Rare material dropped by Giant Spider (70% drop rate)
- Used for future crafting system

## Technical Architecture

### Frontend (webui)
- **index.html**: Login and account creation with medieval theme (castle background, shield emblems)
- **dashboard.html**: List of user's knights, knight creation, leaderboard, graveyard link
- **knight.html**: Individual knight detail page with equipment, stats, inventory, battle button, and shop
- **graveyard.html**: Memorial page for deceased knights with dark/greyscale theme
- **Images**: 
  - SVG class icons for each knight class (160x160 pixels)
  - Monster graphics (256x256 pixels): Level 1 Slime, Giant Rat, Weak Goblin, Forest Wolf, Goblin Warrior, Troglodite, Orc, Giant Spider
  - Equipment icons (64x64 for materials, 128x128 for armor/weapons)
  - UI elements: Castle background, shield emblems, decorative banners

### Backend (Python Flask)
- **Authentication endpoints**: `/api/login`, `/api/signup`
- **Knight endpoints**: 
  - `GET /api/knights?user_id=X`: List user's knights
  - `GET /api/knights/{id}`: Get single knight details
  - `POST /api/knights`: Create new knight
- **Battle endpoints** (to be implemented):
  - `POST /api/battle`: Initiate battle, create K8s job
  - `GET /api/battle/{id}`: Get battle status/results

### Database (MySQL)
- **users table**: User accounts (id, username, password_hash, created_at)
- **knights table**: Knight data (id, user_id, name, class, level, hp, max_hp, exp, created_at, updated_at, is_alive)
- **inventory table**: All items owned by knights (id, knight_id, item_id, quantity, is_equipped)
- **battles table**: Battle history and results (id, knight_id, monster_name, difficulty, outcome, hp_before, hp_after, exp_gained, gold_gained, battle_log, created_at)

### Deployment
- Containerized with Docker
- Deployed on DigitalOcean Droplet using Kubernetes
- Frontend: Nginx serving static HTML/JS
- Backend: Flask API server
- Database: MySQL StatefulSet with persistent storage

## UI/UX Design

### Medieval Theme
- Dark color scheme with brown/tan accents (#2d3748, #1a202c backgrounds)
- Golden text for titles and highlights (#FFD700)
- Brown borders and medieval styling (#8B7355)
- Georgia serif font for authentic medieval feel
- Castle silhouette backgrounds (semi-transparent overlays)
- Shield emblems and decorative elements
- Equipment displayed in 3-column grid for visibility

### Visual Feedback
- Hover effects on interactive elements
- Modal dialogs for equipment selection and battle difficulty
- Click-outside-to-close functionality on modals
- HP bars with regeneration timers
- Experience bars showing progress to next level
- Rarity-based item coloring (common, uncommon, rare, epic)

## Future Enhancements
- Equipment crafting system using materials (Spider Silk, etc.)
- Knight skill trees and abilities
- Multiplayer features (PvP, guilds)
- Quest system with storylines
- Leaderboard enhancements (filtering, pagination)
- Achievement system
- More epic/legendary items with unique effects

---

## Current Implementation Status

### ✅ Completed
- User authentication (login/signup) with bcrypt password hashing
- Knight creation with class selection
- Knight listing on dashboard with leaderboard
- Knight detail page with equipment slots, stats, HP bar, inventory, and shop
- Level 10 requirement for creating additional knights
- Class-specific images for all 4 classes
- Database schema for users, knights, inventory, and battles
- Full battle system with all three difficulty tiers
- HP regeneration system (1 HP per 15 minutes via Kubernetes CronJob)
- Experience and leveling system (level cap: 10)
- Equipment system with 11 slots (weapon, shield, helm, chest, cape, belt, gloves, pants, boots, 2 rings)
- Monster roster: 8 monsters across 3 difficulty tiers
  - Easy: Level 1 Slime, Giant Rat, Weak Goblin
  - Medium: Forest Wolf, Goblin Warrior, Troglodite
  - Hard: Orc, Giant Spider
- Equipment tiers: Wooden (easy), Stone (medium), Iron (hard)
- Special items: Silk Cape (epic cape from Giant Spider)
- Materials system: Spider Silk (crafting material)
- Battle history and detailed battle logs
- Graveyard page for deceased knights
- Medieval-themed UI with castle backgrounds, shield emblems, golden accents
- Shop system for purchasing equipment with gold
- Inventory management with equip/unequip functionality
- Equipment slots clickable with filtered item selection
- Sell duplicate equipment feature

### 🚧 In Progress
- Monster graphics refinement (currently using SVG placeholders)
- Equipment icon improvements

### 📋 Planned
- Crafting system using materials (Spider Silk → items)
- Additional epic/legendary items with unique effects
- More monster varieties within each tier
- Knight skill trees and special abilities
- PvP battle system
- Guild/clan system
- Quest and storyline system
- Achievement system with rewards

---

*This manifesto serves as the single source of truth for Knight Club's game mechanics and can be provided to LLMs for modification, extension, or implementation guidance.*
