"""Reproducible local evaluation of the current agent against its Git baseline."""

import argparse
import collections
import statistics
import subprocess

from kaggle_environments import make

from src.agent import agent

BASELINE_REV = "66e34b76232c0d96e907b9b2d74bed6365cc2760"


def baseline_agent():
    source = subprocess.check_output(["git", "show", f"{BASELINE_REV}:src/agent.py"], text=True)
    namespace = {"__name__": "baseline_agent"}
    exec(compile(source, "baseline_agent.py", "exec"), namespace)
    return namespace["agent"]


def run(players, seed):
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=True)
    env.run(players)
    final = env.steps[-1]
    return [float(state.reward or 0) for state in final], [state.status for state in final]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=4)
    parser.add_argument("--trace", action="store_true")
    args = parser.parse_args()
    if args.trace:
        actions = collections.Counter()
        daily = {}

        def tracked(obs):
            result = agent(obs)
            for command in [result["farmer"], *result["hands"], *result["market"]]:
                if command:
                    actions[(command[0], command[1] if len(command) > 1 else "")] += 1
            daily[obs["day"]] = obs["farms"][obs["player"]]["money"]
            return result

        rewards, statuses = run([tracked, "starter"], 0)
        print(f"trace: rewards={rewards} statuses={statuses}")
        print(f"money_by_day={sorted(daily.items())}")
        print(f"actions={actions.most_common(25)}")
        return
    opponents = {"baseline": baseline_agent(), "starter": "starter"}
    for name, opponent in opponents.items():
        rows = []
        for seed in range(args.seeds):
            for side in (0, 1):
                players = [agent, opponent] if side == 0 else [opponent, agent]
                rewards, statuses = run(players, seed)
                own, other = rewards[side], rewards[1 - side]
                rows.append((own, other, statuses[side]))
        money = [row[0] for row in rows]
        margins = [row[0] - row[1] for row in rows]
        print(
            f"{name}: games={len(rows)} avg={statistics.mean(money):.1f} "
            f"median={statistics.median(money):.1f} min={min(money):.0f} "
            f"wins={sum(v > 0 for v in margins)} ties={sum(v == 0 for v in margins)} "
            f"losses={sum(v < 0 for v in margins)} "
            f"avg_margin={statistics.mean(margins):.1f} "
            f"errors={sum(status != 'DONE' for _, _, status in rows)}"
        )


if __name__ == "__main__":
    main()
