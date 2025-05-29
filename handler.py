import subprocess
import os

def run_battle(hero_type=1, boss_type=1, tree_stats=None):
    """
    Run the battle game with specified configuration
    hero_type: 1 for BloodReaper, 2 for AshenKnight
    boss_type: 1-5 for different bosses
    tree_stats: dict with keys 'strength', 'energy', 'health'
    """
    if tree_stats is None:
        tree_stats = {'strength': 0, 'energy': 0, 'health': 0}

    # Set environment variables for battle.py to use
    os.environ['HERO_TYPE'] = str(hero_type)
    os.environ['BOSS_TYPE'] = str(boss_type)
    os.environ['TREE_STAT_STRENGTH'] = str(tree_stats['strength'])
    os.environ['TREE_STAT_ENERGY'] = str(tree_stats['energy'])
    os.environ['TREE_STAT_HEALTH'] = str(tree_stats['health'])

    # Run battle.py
    script_path = os.path.join(os.path.dirname(__file__), 'battle.py')
    subprocess.run(['python', script_path])

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
