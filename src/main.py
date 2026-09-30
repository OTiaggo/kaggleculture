from agent import agent


if __name__ == "__main__":
    import argparse
    import webbrowser
    from pathlib import Path

    from kaggle_environments import make

    parser = argparse.ArgumentParser(description="Run a Kaggriculture match and save its visual replay.")
    parser.add_argument("--opponent", default="random", help="Kaggle agent name, for example random or starter")
    parser.add_argument("--steps", type=int, default=720, help="Maximum episode steps")
    parser.add_argument("--output", default="resultado.html", help="Path for the rendered replay")
    parser.add_argument("--no-open", action="store_true", help="Save the replay without opening a browser")
    args = parser.parse_args()

    env = make("kaggriculture", configuration={"episodeSteps": args.steps}, debug=True)
    env.run([agent, args.opponent])
    replay = Path(args.output).resolve()
    replay.write_text(env.render(mode="html", width=1200, height=850), encoding="utf-8")
    for index, result in enumerate(env.steps[-1]):
        print(f"Player {index}: reward={result.reward} status={result.status}")
    print(f"Replay saved to: {replay}")
    if not args.no_open:
        webbrowser.open(replay.as_uri())
