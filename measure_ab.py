import time
from engine import Connect4Game, PLAYER1, PLAYER2
from agents import MinimaxAgent, GreedyAgent
from evaluate import run_match

def test():
    print("Testing pure Alpha-Beta vs Raw Minimax (Depth 4) against Greedy Agent...")
    
    # 1. Alpha Beta Minimax (no TT to isolate AB)
    ab_agent = MinimaxAgent(PLAYER1, max_depth=4, use_ab=True, use_tt=False)
    greedy = GreedyAgent(PLAYER2)
    winner_ab, metrics_ab = run_match(ab_agent, greedy)
    
    # 2. Raw Minimax (no TT)
    raw_agent = MinimaxAgent(PLAYER1, max_depth=4, use_ab=False, use_tt=False)
    greedy = GreedyAgent(PLAYER2)
    winner_raw, metrics_raw = run_match(raw_agent, greedy)
    
    ab_nodes = metrics_ab[PLAYER1]['nodes']
    ab_time = metrics_ab[PLAYER1]['time']
    ab_moves = metrics_ab[PLAYER1]['moves']
    
    raw_nodes = metrics_raw[PLAYER1]['nodes']
    raw_time = metrics_raw[PLAYER1]['time']
    raw_moves = metrics_raw[PLAYER1]['moves']
    
    print(f"\nResults per move (averaged over {ab_moves} moves):")
    avg_ab_nodes = ab_nodes / ab_moves
    avg_ab_time = ab_time / ab_moves
    
    avg_raw_nodes = raw_nodes / raw_moves
    avg_raw_time = raw_time / raw_moves
    
    print(f"Alpha-Beta: {avg_ab_nodes:.1f} nodes, {avg_ab_time:.4f} sec")
    print(f"Raw Minimax: {avg_raw_nodes:.1f} nodes, {avg_raw_time:.4f} sec")
    
    print(f"\nTotal Nodes:")
    print(f"Alpha-Beta: {ab_nodes}")
    print(f"Raw Minimax: {raw_nodes}")
    
    node_reduction = (raw_nodes - ab_nodes) / raw_nodes * 100
    time_reduction = (raw_time - ab_time) / raw_time * 100
    print(f"\nImprovement:")
    print(f"Nodes searched reduced by: {node_reduction:.2f}% (Saved {raw_nodes - ab_nodes} nodes)")
    print(f"Time reduced by: {time_reduction:.2f}%")

if __name__ == "__main__":
    test()
