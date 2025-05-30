import os
import pygame

def run_battle(hero_type=1, boss_type=1, tree_stats=None, enemy_id=None):
    """
    Run the battle game with specified configuration
    hero_type: 1 for BloodReaper, 2 for AshenKnight
    boss_type: 1-5 for different bosses
    tree_stats: dict with keys 'strength', 'energy', 'health'
    """
    if tree_stats is None:
        tree_stats = {'strength': 0, 'energy': 0, 'health': 0}

    try:
        # Set environment variables first
        os.environ['HERO_TYPE'] = str(hero_type)
        os.environ['BOSS_TYPE'] = str(boss_type)
        os.environ['TREE_STAT_STRENGTH'] = str(tree_stats['strength'])
        os.environ['TREE_STAT_ENERGY'] = str(tree_stats['energy']) 
        os.environ['TREE_STAT_HEALTH'] = str(tree_stats['health'])
        os.environ['ENEMY_ID'] = str(enemy_id) if enemy_id else '0'

        import battle
        battle.run_battle_loop()

    except Exception as e:
        print(f"Battle error: {str(e)}")
        return "QUIT"

if __name__ == "__main__":
    # Example usage
    run_battle(
        hero_type=1,  # BloodReaper
        boss_type=1,  # First boss
        tree_stats={
            'strength': 0,
            'energy': 0,
            'health': 0
        }
    )
