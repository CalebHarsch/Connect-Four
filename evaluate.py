import time
from engine import Connect4Game, PLAYER1, PLAYER2, EMPTY
from agents import RandomAgent, GreedyAgent, MinimaxAgent

def run_match(player1_agent, player2_agent):
    """Runs a single headless match and returns metrics."""
    game = Connect4Game()
    
    # Reset TTable if agent supports it (keep memory fresh per match, or we could keep it across matches)
    for agent in [player1_agent, player2_agent]:
        if hasattr(agent, 'clear_ttable'):
            agent.clear_ttable()

    metrics = {
        PLAYER1: {'time': 0, 'moves': 0, 'nodes': 0, 'tt_hits': 0, 'tt_size': 0},
        PLAYER2: {'time': 0, 'moves': 0, 'nodes': 0, 'tt_hits': 0, 'tt_size': 0}
    }
    
    winner = 0

    while True:
        current_agent = player1_agent if game.current_player == PLAYER1 else player2_agent
        start_time = time.time()
        
        col = current_agent.get_action(game)
        
        elapsed = time.time() - start_time
        metrics[game.current_player]['time'] += elapsed
        metrics[game.current_player]['moves'] += 1
        
        if hasattr(current_agent, 'nodes_expanded'):
            metrics[game.current_player]['nodes'] += current_agent.nodes_expanded
            metrics[game.current_player]['tt_hits'] += current_agent.ttable_hits
            metrics[game.current_player]['tt_size'] = len(current_agent.ttable)

        if col is None:
            # Should not happen unless board is completely full and not caught
            break
            
        game.make_move(col)
        
        if game.winning_move(PLAYER1):
            winner = PLAYER1
            break
        elif game.winning_move(PLAYER2):
            winner = PLAYER2
            break
        elif len(game.get_valid_locations()) == 0:
            winner = 0 # Draw
            break

    return winner, metrics

def run_experiment(agent1_name, player1, agent2_name, player2, num_games=10):
    print(f"--- RUNNING EXPERIMENT: {agent1_name} (P1) vs {agent2_name} (P2) | {num_games} Games ---")
    
    p1_wins = 0
    p2_wins = 0
    draws = 0
    
    total_p1_nodes = 0
    total_p2_nodes = 0
    total_p1_time = 0
    total_p2_time = 0
    total_p1_moves = 0
    total_p2_moves = 0
    total_p1_hits = 0
    
    p1_tt_sizes = []

    for i in range(num_games):
        winner, metrics = run_match(player1, player2)
        if winner == PLAYER1:
            p1_wins += 1
        elif winner == PLAYER2:
            p2_wins += 1
        else:
            draws += 1
            
        total_p1_time += metrics[PLAYER1]['time']
        total_p1_moves += metrics[PLAYER1]['moves']
        total_p1_nodes += metrics[PLAYER1]['nodes']
        total_p1_hits += metrics[PLAYER1]['tt_hits']
        p1_tt_sizes.append(metrics[PLAYER1]['tt_size'])
        
        total_p2_time += metrics[PLAYER2]['time']
        total_p2_moves += metrics[PLAYER2]['moves']
        total_p2_nodes += metrics[PLAYER2]['nodes']
        
        print(f"Game {i+1}/{num_games} completed. Winner: Player {winner if winner else 'Draw (0)'}")

    print("\n" + "="*50)
    print("EXPERIMENT RESULTS")
    print("="*50)
    print(f"Win Rate:")
    print(f"  {agent1_name} (P1): {p1_wins/num_games * 100:.1f}%")
    print(f"  {agent2_name} (P2): {p2_wins/num_games * 100:.1f}%")
    print(f"  Draws: {draws/num_games * 100:.1f}%")
    
    print(f"\n{agent1_name} Performance:")
    avg_p1_time = total_p1_time / max(1, total_p1_moves)
    avg_p1_nodes = total_p1_nodes / max(1, total_p1_moves)
    print(f"  Avg Decision Time: {avg_p1_time:.4f} sec / move")
    if hasattr(player1, 'max_depth'):
        print(f"  Search Depth Configured: {player1.max_depth}")
        print(f"  Avg Nodes Expanded: {avg_p1_nodes:.1f} / move")
        print(f"  Total Transposition Hits: {total_p1_hits}")
        avg_tt = sum(p1_tt_sizes) / len(p1_tt_sizes) if p1_tt_sizes else 0
        print(f"  Avg Table Entries (Memory Size): {avg_tt:.1f} states cached per game")
        
    print(f"\n{agent2_name} Performance:")
    avg_p2_time = total_p2_time / max(1, total_p2_moves)
    avg_p2_nodes = total_p2_nodes / max(1, total_p2_moves)
    print(f"  Avg Decision Time: {avg_p2_time:.4f} sec / move")
    if hasattr(player2, 'max_depth'):
        print(f"  Avg Nodes Expanded: {avg_p2_nodes:.1f} / move")
        print(f"  Search Depth Configured: {player2.max_depth}")
    
    print("="*50 + "\n")

def run_presentation_experiments(num_games=10):
    print("\n" + "="*85)
    print("RUNNING PRESENTATION EXPERIMENTS (This may take a minute...)")
    print("="*85)
    
    opponents = [
        ("Random Agent", RandomAgent(PLAYER2)),
        ("Greedy Agent", GreedyAgent(PLAYER2)),
        ("Minimax (Depth 3)", MinimaxAgent(PLAYER2, max_depth=3)),
        ("Final Agent (Depth 5)", MinimaxAgent(PLAYER2, max_depth=5))
    ]
    
    results = []
    
    for opp_name, opp_agent in opponents:
        matchup_name = f"Final Agent vs {opp_name}"
        print(f"Testing: {matchup_name}...")
        p1_wins = 0
        total_p1_nodes = 0
        total_p1_time = 0
        total_p1_moves = 0
        
        for i in range(num_games):
            player1 = MinimaxAgent(PLAYER1, max_depth=5)
            # Fresh opponent instance if needed, though run_match clears ttable
            if opp_name == "Random Agent":
                opp_agent = RandomAgent(PLAYER2)
            elif opp_name == "Greedy Agent":
                opp_agent = GreedyAgent(PLAYER2)
            elif opp_name == "Minimax (Depth 3)":
                opp_agent = MinimaxAgent(PLAYER2, max_depth=3)
            elif opp_name == "Final Agent (Depth 5)":
                opp_agent = MinimaxAgent(PLAYER2, max_depth=5)

            winner, metrics = run_match(player1, opp_agent)
            
            if winner == PLAYER1:
                p1_wins += 1
                
            total_p1_time += metrics[PLAYER1]['time']
            total_p1_moves += metrics[PLAYER1]['moves']
            total_p1_nodes += metrics[PLAYER1]['nodes']
            
        win_rate = (p1_wins / num_games) * 100
        avg_nodes = total_p1_nodes / max(1, total_p1_moves)
        avg_time = total_p1_time / max(1, total_p1_moves)
        
        # Store matchup_name instead of just opp_name to be perfectly clear
        results.append((matchup_name, win_rate, avg_nodes, avg_time))
        print(f"  -> Final Agent Win Rate: {win_rate:.1f}%, Avg Nodes: {avg_nodes:.1f}, Avg Time: {avg_time:.4f}s")

    print("\n\n" + "="*95)
    print("FINAL PERFORMANCE TABLE (Copy into your presentation slide)")
    print("Note: Win Rate is the percentage of games won by the FINAL AGENT (Player 1)")
    print("="*95)
    print(f"{'Matchup (Player 1 vs Player 2)':<45} | {'P1 Win Rate':<12} | {'Avg Nodes/Move':<15} | {'Avg Time/Move':<15}")
    print("-" * 95)
    for matchup_name, win_rate, avg_nodes, avg_time in results:
         print(f"{matchup_name:<45} | {win_rate:>11.1f}% | {avg_nodes:>14.1f} | {avg_time:>13.4f}s")
    print("="*95 + "\n")
import random

def run_ab_performance_test(num_games=5):
    print("\n" + "="*95)
    print(f"MEASURING ALPHA-BETA PRUNING IMPROVEMENT (Depth 4) over {num_games} games")
    print("="*95)
    
    total_ab_nodes = 0
    total_ab_time = 0
    total_raw_nodes = 0
    total_raw_time = 0
    
    print(f"Running matches against RandomAgent (with identical seeds for fair comparison)...")
    
    for i in range(num_games):
        ab_agent = MinimaxAgent(PLAYER1, max_depth=4, use_ab=True, use_tt=False)
        raw_agent = MinimaxAgent(PLAYER1, max_depth=4, use_ab=False, use_tt=False)
        
        # Give both agents the exact same randomized opponent for a 1-to-1 fair comparison
        seed_val = i * 1000
        
        random.seed(seed_val)
        _, metrics_ab = run_match(ab_agent, RandomAgent(PLAYER2))
        
        random.seed(seed_val)
        _, metrics_raw = run_match(raw_agent, RandomAgent(PLAYER2))
        
        total_ab_nodes += metrics_ab[PLAYER1]['nodes']
        total_ab_time += metrics_ab[PLAYER1]['time']
        
        total_raw_nodes += metrics_raw[PLAYER1]['nodes']
        total_raw_time += metrics_raw[PLAYER1]['time']
        
        print(f"  Game {i+1} completed.")
        
    print(f"\nResults (Total for {num_games} games vs RandomAgent):")
    print(f"Alpha-Beta Minimax : {total_ab_nodes} nodes searched, {total_ab_time:.4f} sec")
    print(f"Raw Minimax        : {total_raw_nodes} nodes searched, {total_raw_time:.4f} sec")
    
    node_reduction = (total_raw_nodes - total_ab_nodes) / max(1, total_raw_nodes) * 100
    time_reduction = (total_raw_time - total_ab_time) / max(1, total_raw_time) * 100
    
    print(f"\nImprovement:")
    print(f"Nodes searched reduced by: {node_reduction:.2f}% (Saved {total_raw_nodes - total_ab_nodes} nodes)")
    print(f"Time reduced by:           {time_reduction:.2f}%")
    print("="*95 + "\n")
    
    # reset seed to none for normal random behavior later
    random.seed(None)

if __name__ == "__main__":
    # Test 1: Greedy vs Random
    # run_experiment(
    #     "GreedyAgent", GreedyAgent(PLAYER1), 
    #     "RandomAgent", RandomAgent(PLAYER2), 
    #     num_games=10
    # )
    
    # Test 2: Minimax (Depth 3) vs Greedy
    # run_experiment(
    #     "Minimax (D3)", MinimaxAgent(PLAYER1, max_depth=3), 
    #     "GreedyAgent", GreedyAgent(PLAYER2), 
    #     num_games=5
    # )

    # experiments
    run_presentation_experiments(num_games=5) # number of games ran
    
    # Alpha-Beta Pruning measurement
    run_ab_performance_test()
