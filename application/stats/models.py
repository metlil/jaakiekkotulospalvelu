from sqlalchemy import text

from application import db


def standings():
    stmt = text(
        "SELECT"
        "  Team.name,"
        "  COUNT(Result.id) AS game_count,"
        "  COUNT("
        "    CASE WHEN"
        "      (Team.id = Result.home_id AND Result.home_goal_count > Result.guest_goal_count)"
        "      OR (Team.id = Result.guest_id AND Result.home_goal_count < Result.guest_goal_count)"
        "    THEN 1"
        "    ELSE NULL"
        "    END"
        "  ) AS win,"
        "  COUNT("
        "    CASE WHEN"
        "      (Team.id = Result.home_id AND Result.home_goal_count < Result.guest_goal_count)"
        "      OR (Team.id = Result.guest_id AND Result.home_goal_count > Result.guest_goal_count)"
        "    THEN 1"
        "    ELSE NULL"
        "    END"
        "  ) AS loss,"
        "  COUNT(CASE WHEN Result.home_goal_count = Result.guest_goal_count THEN 1 ELSE NULL END) AS tie,"
        "  COALESCE("
        "    SUM(CASE WHEN Team.id = Result.home_id THEN Result.home_goal_count ELSE Result.guest_goal_count END),"
        "    0"
        "  ) AS goals_for,"
        "  COALESCE("
        "    SUM(CASE WHEN Team.id = Result.home_id THEN Result.guest_goal_count ELSE Result.home_goal_count END),"
        "    0"
        "  ) AS goals_against "
        "FROM"
        "  Team"
        "  LEFT JOIN ("
        "    SELECT"
        "      Game.id,"
        "      Game.home_id,"
        "      Game.guest_id,"
        "      COUNT(CASE WHEN Goal.team_id = Game.home_id THEN 1 ELSE NULL END) AS home_goal_count,"
        "      COUNT(CASE WHEN Goal.team_id = Game.guest_id THEN 1 ELSE NULL END) AS guest_goal_count"
        "    FROM"
        "      Game,"
        "      Goal"
        "    WHERE"
        "      Game.id = Goal.game_id"
        "    GROUP BY Game.id, Game.home_id, Game.guest_id"
        "  ) AS Result"
        "    ON ("
        "      Team.id = Result.home_id"
        "      OR Team.id = Result.guest_id"
        "    ) "
        "GROUP BY Team.id"
    )

    res = db.engine.execute(stmt)
    response = []
    for row in res:
        response.append({
            "name": row[0], "game_count": row[1], "win": row[2], "loss": row[3],
            "tie": row[4], "goals_for": row[5], "goals_against": row[6],
            "goal_difference": row[5] - row[6], "points": 2 * row[2] + row[4]})

    return sorted(response, key=standing_sort, reverse=True)


def standing_sort(args):
    return args["points"], args["goal_difference"], args["goals_for"]
