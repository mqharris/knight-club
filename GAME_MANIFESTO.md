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
Each knight has 9 equipment slots:
1. Helm
2. Chest
3. Cape
4. Belt
5. Gloves
6. Pants
7. Boots
8. Ring (slot 1)
9. Ring (slot 2)

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
- **Easy Tier (Initial Implementation)**:
  - Level 1 Slime (starter monster)

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

## Technical Architecture

### Frontend (webui)
- **index.html**: Login and account creation
- **dashboard.html**: List of user's knights, knight creation
- **knight.html**: Individual knight detail page with equipment, stats, and battle button
- **Images**: SVG images for each knight class (160x160 pixels)

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
- **knights table**: Knight data (id, user_id, name, class, level, created_at, updated_at)
- **equipment table** (to be implemented): Equipment items
- **knight_equipment table** (to be implemented): Equipped items per knight
- **battles table** (to be implemented): Battle history and results

### Deployment
- Containerized with Docker
- Deployed on DigitalOcean Droplet using Kubernetes
- Frontend: Nginx serving static HTML/JS
- Backend: Flask API server
- Database: MySQL StatefulSet with persistent storage

## Future Enhancements
- Additional monster types and difficulty tiers
- Equipment crafting and enhancement
- Knight skill trees and abilities
- Multiplayer features (PvP, guilds)
- Quest system with storylines
- Leaderboards and achievements

---

## Current Implementation Status

### ✅ Completed
- User authentication (login/signup)
- Knight creation with class selection
- Knight listing on dashboard
- Knight detail page with equipment slots, stats, HP bar
- Level 10 requirement for creating additional knights
- Class-specific images for all 4 classes
- Database schema for users and knights

### 🚧 In Progress
- Battle system (Easy difficulty, Level 1 Slime)
- HP regeneration system (1 HP per 15 minutes)

### 📋 Planned
- Equipment system and item drops
- Experience and leveling mechanics
- Battle history and logs
- Medium and Hard difficulty monsters
- Additional monster varieties

---

*This manifesto serves as the single source of truth for Knight Club's game mechanics and can be provided to LLMs for modification, extension, or implementation guidance.*
