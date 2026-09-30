"""Competitive Kaggriculture agent with lightweight economic task planning."""

PARAMS = {
    "sell_floor_ratio": 0.78,
    "shed_sell_ratio": 0.72,
    "hire_action_value": 17.0,
    "max_hires_daily": 8,
    "planting_reserve": 12,
    "max_plants": 25,
    "late_days": 4,
    "expansion_min_days": 13,
}

CROPS = {
    "WHEAT": {"seed": 10, "base": 25, "first": 2, "duration": 4, "yield": 3.2, "days": 4},
    "CARROT": {"seed": 20, "base": 35, "first": 2, "duration": 3, "yield": 2.25, "days": 3},
    "TOMATO": {"seed": 50, "base": 60, "first": 8, "duration": 11, "yield": 1.32, "days": 11},
    "STRAWBERRY": {"seed": 100, "base": 120, "first": 10, "duration": 16, "yield": 0.96, "days": 16},
    "MELON": {"seed": 80, "base": 250, "first": 10, "duration": 10, "yield": 3.3, "days": 10},
}
ANIMALS = {"GOOSE": (300, "EGG", 4, 1), "COW": (400, "MILK", 8, 2), "SHEEP": (500, "WOOL", 6, 3)}
SHOP_DEMAND = {
    "BAKERY": {"EGG": 1, "WHEAT": 1}, "PIZZA_SHOP": {"MILK": 1, "TOMATO": 1, "WHEAT": 1},
    "BRUNCH_SPOT": {"EGG": 1, "WHEAT": 1, "STRAWBERRY": 1}, "YARN_STORE": {"WOOL": 2},
    "ICE_CREAM_SHOP": {"STRAWBERRY": 1, "MILK": 1, "WHEAT": 1}, "PET_CAFE": {"CARROT": 2},
    "SMOOTHIE_SHOP": {"STRAWBERRY": 1, "MILK": 1},
    "FARMERS_MARKET": {"WHEAT": 1, "CARROT": 1, "TOMATO": 1, "STRAWBERRY": 1},
}
SHED_TILES = {(4, 4), (5, 4), (4, 5), (5, 5)}
MOVES = (("NORTH", -1, 0), ("SOUTH", 1, 0), ("WEST", 0, -1), ("EAST", 0, 1))


def _int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _dict(value):
    return value if isinstance(value, dict) else {}


def _tiles(farm):
    tiles = farm.get("tiles", [])
    result = []
    for y in range(10):
        for x in range(10):
            try:
                tile = tiles[y][x]
            except (IndexError, TypeError):
                tile = None
            result.append((y, x, tile))
    return result


def _price(obs, item):
    prices = _dict(_dict(obs.get("market")).get("prices"))
    return max(1, _int(prices.get(item), 1))


def _shop_counts(obs):
    counts = {item: 0 for item in ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "EGG", "MILK", "WOOL")}
    shops = _dict(obs.get("town")).get("unlocked_shops", [])
    if not isinstance(shops, list):
        return counts
    for shop in shops:
        name = str(shop.get("kind", shop.get("type", shop.get("name", "")))).upper() if isinstance(shop, dict) else str(shop).upper()
        demand = SHOP_DEMAND.get(name, {})
        for item, amount in demand.items():
            counts[item] = counts.get(item, 0) + amount
    return counts


def _crop_score(crop, obs, opponent_pressure, demand, days_left):
    info = CROPS[crop]
    harvest_day = {"WHEAT": 4, "CARROT": 3, "MELON": 10}.get(crop, info["first"])
    if days_left < harvest_day + 1:
        return -1e6
    price = _price(obs, crop)
    pressure = max(0.0, min(0.8, opponent_pressure.get(crop, 0) * 0.025))
    scarcity = min(0.22, demand.get(crop, 0) * 0.035)
    expected = info["yield"] * price * (1.0 - pressure + scarcity)
    days_in_season = min(info["days"], days_left)
    if crop in ("TOMATO", "STRAWBERRY") and days_left < info["duration"] + 1:
        expected *= min(1.0, max(0.15, (days_left - info["first"] + 1) / max(1, info["duration"] - info["first"] + 1)))
    seed_cost = info["seed"]
    maintenance = 1.0 + max(0, days_in_season - 2) * 0.22
    action_adjusted = (expected - seed_cost) / (1.0 + maintenance + info["first"] * 0.08)
    return action_adjusted + scarcity * price * 0.08


def _opponent_pressure(obs, opponent):
    counts = {crop: 0 for crop in CROPS}
    for _, _, tile in _tiles(opponent):
        if isinstance(tile, dict):
            crop = str(tile.get("crop", "")).upper()
            if crop in counts:
                counts[crop] += 1
    return counts


def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _next_move(pos, target):
    dx, dy = target[0] - pos[0], target[1] - pos[1]
    if dx:
        return "SOUTH" if dx > 0 else "NORTH"
    if dy:
        return "EAST" if dy > 0 else "WEST"
    return "PASS"


def _is_locked(tile):
    return tile == "LOCKED" or (isinstance(tile, dict) and tile.get("kind") == "LOCKED")


def _task_list(obs, farm, own_index, days_left):
    tasks = []
    plants = 0
    empty = []
    crops_owned = _dict(_dict(obs.get("private")).get("seeds"))
    day = _int(obs.get("day"))
    for x, y, tile in _tiles(farm):
        pos = (x, y)
        if _is_locked(tile):
            continue
        if tile is None or tile == "EMPTY" or (isinstance(tile, dict) and tile.get("kind") == "EMPTY"):
            empty.append(pos)
            continue
        if not isinstance(tile, dict):
            continue
        kind = str(tile.get("kind", "")).upper()
        if kind == "PLANT":
            plants += 1
            crop = str(tile.get("crop", "")).upper()
            age = max(0, day - _int(tile.get("planted_day"), day))
            # One-time crops gain most of their yield from watering after the
            # first harvestable day. Wait for that bonus before harvesting.
            harvest_age = {"WHEAT": 4, "CARROT": 3, "MELON": 10}.get(
                crop, CROPS.get(crop, {}).get("first", 999)
            )
            ripe = _int(tile.get("yield_units")) > 0 and age >= harvest_age
            watered = bool(tile.get("watered_today", False))
            urgency = 200 if _int(tile.get("consecutive_unwatered")) >= 1 and not watered else 0
            if ripe:
                value = _price(obs, crop) * min(4, _int(tile.get("yield_units")))
                tasks.append((max(130, 70 + min(70, value / 10)), pos, ["HARVEST"], "harvest", crop))
            if not watered:
                tasks.append((max(urgency, 115 + (45 if _int(obs.get("hour")) >= 18 else 0)), pos, ["WATER"], "water", crop))
            if not ripe and crop in CROPS and not bool(tile.get("fertilized_until_day", -1) >= day):
                next_yield = _price(obs, crop) * (1.0 if crop in ("WHEAT", "CARROT") else 0.45)
                if next_yield > 145 and days_left > 5:
                    tasks.append((25 + min(20, next_yield / 30), pos, ["FERTILIZE"], "optional", crop))
        elif kind in ("COOP", "PASTURE") and tile.get("animal"):
            animal = str(tile.get("animal")).upper()
            unfed = _int(tile.get("consecutive_unfed"))
            fed = bool(tile.get("fed_today", False))
            if not fed and unfed >= 1:
                tasks.append((175, pos, ["FEED"], "feed", animal))
            elif not fed:
                tasks.append((90, pos, ["FEED"], "feed", animal))
            if _int(tile.get("yield_units")) > 0:
                product = ANIMALS.get(animal, (0, "", 0, 0))[1]
                tasks.append((max(95, 55 + _price(obs, product) * _int(tile.get("yield_units")) / 12), pos, ["HARVEST"], "harvest", product))
            if tile.get("fertilizer_available"):
                tasks.append((36, pos, ["COLLECT_FERTILIZER"], "optional", "FERTILIZER"))

    max_active = min(PARAMS["max_plants"], max(5, 4 + len(farm.get("hands", [])) * 3))
    if plants < max_active and days_left >= 4:
        farms = obs.get("farms", [])
        opponent = farms[1 - own_index] if isinstance(farms, list) and len(farms) > 1 else {}
        pressure = _opponent_pressure(obs, opponent)
        demand = _shop_counts(obs)
        stocked = [crop for crop in CROPS if _int(crops_owned.get(crop)) > 0
                   and _crop_score(crop, obs, pressure, demand, days_left) > 0]
        if stocked:
            crop = max(stocked, key=lambda item: _crop_score(item, obs, pressure, demand, days_left))
            remaining_seeds = _int(crops_owned.get(crop))
            for pos in empty:
                if plants >= max_active or remaining_seeds <= 0:
                    break
                tasks.append((34 + max(0, _crop_score(crop, obs, pressure, demand, days_left)) * 0.12, pos, ["PLANT", crop], "plant", crop))
                plants += 1
                remaining_seeds -= 1
    for x, y, tile in _tiles(farm):
        if isinstance(tile, dict) and str(tile.get("kind", "")).upper() == "WEED":
            tasks.append((8, (x, y), ["DIG"], "optional", "WEED"))
    return sorted(tasks, key=lambda task: (-task[0], task[1][0], task[1][1], task[2][0]))


def _fibonacci_cost(n):
    a, b = 1, 1
    for _ in range(max(0, n - 1)):
        a, b = b, a + b
    return a


def _market_actions(obs, farm, days_left, tasks, worker_count):
    private = _dict(obs.get("private"))
    shed = _dict(private.get("shed"))
    shed_count = sum(max(0, _int(v)) for v in shed.values())
    capacity = 100
    sales = []
    late = days_left <= PARAMS["late_days"] or _int(obs.get("day")) >= 28
    for item in sorted(shed, key=lambda name: (_price(obs, name), name)):
        qty = max(0, _int(shed.get(item)))
        if not qty:
            continue
        base = CROPS.get(item, {}).get("base", {"EGG": 50, "MILK": 160, "WOOL": 200, "FERTILIZER": 100}.get(item, 1))
        price = _price(obs, item)
        ratio = price / max(1, base)
        target = max(1, min(qty, 12 if not late else qty))
        if late or shed_count >= capacity * PARAMS["shed_sell_ratio"] or ratio >= PARAMS["sell_floor_ratio"] or qty >= 12:
            sales.append(["SELL", item, target])
    orders = []
    seeds = _dict(private.get("seeds"))
    seed_order = None
    if days_left > 3 and farm.get("money", 0) > 150:
        farms = obs.get("farms", [])
        opponent = farms[1 - _int(obs.get("player"))] if isinstance(farms, list) and len(farms) > 1 else {}
        pressure, demand = _opponent_pressure(obs, opponent), _shop_counts(obs)
        crop = max(CROPS, key=lambda c: (_crop_score(c, obs, pressure, demand, days_left), c))
        target_stock = 12 if days_left <= 7 else 6
        desired = max(0, min(target_stock, PARAMS["max_plants"] - sum(
            1 for _, _, tile in _tiles(farm)
            if isinstance(tile, dict) and tile.get("kind") == "PLANT"
        )) - _int(seeds.get(crop)))
        if desired and _int(seeds.get(crop)) < 3:
            seed_order = ["BUY_SEED", crop, desired]
    else:
        seed_order = None
    hires = _int(farm.get("hires_today"))
    available_tasks = len(tasks)
    money = float(farm.get("money", 0) or 0)
    max_hires = 0 if days_left <= 1 else min(PARAMS["max_hires_daily"], max(0, available_tasks - worker_count + 1))
    for n in range(hires, max_hires):
        cost = _fibonacci_cost(n)
        if money < cost + 30:
            break
        if cost > PARAMS["hire_action_value"]:
            break
        orders.append(["HIRE"])
    if late:
        orders.extend(sales)
    else:
        orders.extend(sales[:max(0, 9 - len(orders))])
    if seed_order is not None and len(orders) < 10:
        orders.append(seed_order)
    return orders[:10]


def _plan_workers(obs, farm, tasks):
    farmer = farm.get("farmer", [0, 0])
    workers = [farmer if isinstance(farmer, list) and len(farmer) >= 2 else [0, 0]]
    hands = farm.get("hands", [])
    if isinstance(hands, list):
        workers.extend([h if isinstance(h, list) and len(h) >= 2 else [0, 0] for h in hands])
    inventories = _dict(obs.get("private")).get("inventories", [])
    late = 30 - _int(obs.get("day")) <= 2
    reserved = set()
    commands = []
    for worker_index, worker in enumerate(workers):
        pos = (max(0, min(9, _int(worker[1]))), max(0, min(9, _int(worker[0]))))
        carried = inventories[worker_index] if isinstance(inventories, list) and worker_index < len(inventories) else {}
        if late and isinstance(carried, dict) and sum(max(0, _int(value)) for value in carried.values()) > 0:
            target = min(SHED_TILES, key=lambda tile: (_manhattan(pos, tile), tile))
            commands.append(["DROP"] if pos == target else [_next_move(pos, target)])
            continue
        selected = None
        selected_score = -1e9
        for task in tasks:
            priority, target, action, kind, resource = task
            if (target, action[0]) in reserved:
                continue
            distance = _manhattan(pos, target)
            score = priority - 2.8 * distance
            if score > selected_score:
                selected, selected_score = task, score
        if selected is None or selected_score < 3:
            commands.append(["PASS"])
            continue
        priority, target, action, kind, resource = selected
        reserved.add((target, action[0]))
        if pos == target:
            commands.append(action)
            continue
        commands.append([_next_move(pos, target)])
    return commands


def _agent_impl(obs):
    obs = _dict(obs)
    farms = obs.get("farms", [])
    player = max(0, min(1, _int(obs.get("player"))))
    farm = _dict(farms[player]) if isinstance(farms, list) and len(farms) > player else {}
    day = max(0, _int(obs.get("day")))
    days_left = max(0, 30 - day)
    tasks = _task_list(obs, farm, player, days_left)
    commands = _plan_workers(obs, farm, tasks)
    hands_count = len(farm.get("hands", [])) if isinstance(farm.get("hands", []), list) else 0
    market = _market_actions(obs, farm, days_left, tasks, hands_count + 1)
    return {"farmer": commands[0] if commands else ["PASS"], "hands": commands[1:1 + hands_count], "market": market}


def agent(obs):
    hands = _dict(obs.get("farms", [{}])[max(0, min(1, _int(obs.get("player"))))]).get("hands", []) if isinstance(obs, dict) and isinstance(obs.get("farms"), list) and obs.get("farms") else []
    try:
        result = _agent_impl(obs)
        expected = len(hands) if isinstance(hands, list) else 0
        result["hands"] = (result.get("hands", []) + [["PASS"] for _ in range(expected)])[:expected]
        return result
    except Exception:
        return {"farmer": ["PASS"], "hands": [["PASS"] for _ in range(len(hands) if isinstance(hands, list) else 0)], "market": []}
