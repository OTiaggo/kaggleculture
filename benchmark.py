"""Multi-seed local benchmark for the Kaggriculture submission agent."""

import argparse
import statistics
import time

from src.agent import agent


def pass_agent(obs):
    farm = obs.get("farms", [])[obs.get("player", 0)]
    return {"farmer": ["PASS"], "hands": [["PASS"] for _ in farm.get("hands", [])], "market": []}


def run_match(opponent, seed, agent_first):
    from kaggle_environments import make

    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
    try:
        env.reset(seed=seed)
    except TypeError:
        env.reset()
    players = [agent, opponent] if agent_first else [opponent, agent]
    started = time.perf_counter()
    env.run(players)
    elapsed = time.perf_counter() - started
    final = env.steps[-1]
    rewards = [float(step.reward or 0) for step in final]
    statuses = [step.status for step in final]
    own_index = 0 if agent_first else 1
    other_index = 1 - own_index
    return rewards[own_index], rewards[other_index], statuses, elapsed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--opponents", nargs="+", default=["random", "pass", "starter"])
    parser.add_argument("--self-play-only", action="store_true")
    args = parser.parse_args()
    try:
        from kaggle_environments import make
    except ImportError as error:
        raise SystemExit("kaggle_environments is required: install kaggle-environments to run benchmarks") from error

    for opponent_name in ([] if args.self_play_only else args.opponents):
        if opponent_name == "pass":
            opponent = pass_agent
        else:
            opponent = opponent_name
        results = []
        errors = 0
        for seed in range(args.seeds):
            for agent_first in (True, False):
                try:
                    own, other, statuses, elapsed = run_match(opponent, seed, agent_first)
                except Exception as error:
                    if opponent_name == "starter":
                        print("starter unavailable; skipping")
                        results = []
                        break
                    print(f"seed={seed} side={'P0' if agent_first else 'P1'} failed: {error}")
                    errors += 1
                    continue
                errors += int("ERROR" in statuses)
                results.append((own, other, elapsed))
            if opponent_name == "starter" and not results:
                break
        if not results:
            continue
        margins = [own - other for own, other, _ in results]
        wins = sum(margin > 0 for margin in margins)
        draws = sum(margin == 0 for margin in margins)
        money = [own for own, _, _ in results]
        print(f"{opponent_name}: games={len(results)} wins={wins} draws={draws} losses={len(results)-wins-draws} win_rate={(wins + draws / 2) / len(results):.3f} avg_money={statistics.mean(money):.1f} median={statistics.median(money):.1f} min={min(money):.1f} max={max(money):.1f} avg_margin={statistics.mean(margins):.1f} errors={errors} avg_seconds={statistics.mean(row[2] for row in results):.3f}")

    self_play_results = []
    self_play_errors = 0
    for seed in range(min(args.seeds, 30)):
        for agent_first in (True, False):
            try:
                own, other, statuses, elapsed = run_match(agent, seed, agent_first)
                self_play_results.append((own, other, elapsed))
                self_play_errors += int("ERROR" in statuses)
            except Exception as error:
                print(f"self-play seed={seed} failed: {error}")
                self_play_errors += 1
    if self_play_results:
        margins = [own - other for own, other, _ in self_play_results]
        wins = sum(margin > 0 for margin in margins)
        draws = sum(margin == 0 for margin in margins)
        money = [own for own, _, _ in self_play_results]
        print(f"self-play: games={len(self_play_results)} wins={wins} draws={draws} losses={len(self_play_results)-wins-draws} win_rate={(wins + draws / 2) / len(self_play_results):.3f} avg_money={statistics.mean(money):.1f} median={statistics.median(money):.1f} min={min(money):.1f} max={max(money):.1f} avg_margin={statistics.mean(margins):.1f} errors={self_play_errors} avg_seconds={statistics.mean(row[2] for row in self_play_results):.3f}")


if __name__ == "__main__":
    main()
