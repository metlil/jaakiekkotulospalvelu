SELECT
  Team.name,
  COUNT(*) AS game_count,
  COUNT(
    CASE WHEN
      (Team.id = Result.home_id AND Result.home_goal_count > Result.guest_goal_count)
      OR (Team.id = Result.guest_id AND Result.home_goal_count < Result.guest_goal_count)
    THEN 1
    ELSE NULL
    END
  ) AS win,
  COUNT(
    CASE WHEN
      (Team.id = Result.home_id AND Result.home_goal_count < Result.guest_goal_count)
      OR (Team.id = Result.guest_id AND Result.home_goal_count > Result.guest_goal_count)
    THEN 1
    ELSE NULL
    END
  ) AS loss,
  COUNT(CASE WHEN Result.home_goal_count = Result.guest_goal_count THEN 1 ELSE NULL END) AS tie,
  SUM(CASE WHEN Team.id = Result.home_id THEN Result.home_goal_count ELSE Result.guest_goal_count END) AS goals_for,
  SUM(CASE WHEN Team.id = Result.home_id THEN Result.guest_goal_count ELSE Result.home_goal_count END) AS goals_against
FROM
  (
    SELECT
      Game.id,
      Game.home_id,
      Game.guest_id,
      COUNT(CASE WHEN Goal.team_id = Game.home_id THEN 1 ELSE NULL END) AS home_goal_count,
      COUNT(CASE WHEN Goal.team_id = Game.guest_id THEN 1 ELSE NULL END) AS guest_goal_count
    FROM
      Game,
      Goal
    WHERE
      Game.id = Goal.game_id
    GROUP BY Game.id, Game.home_id, Game.guest_id
  ) AS Result,
  Team
WHERE
  Team.id = Result.home_id
  OR Team.id = Result.guest_id
GROUP BY Team.id;

SELECT
  Game.id,
  Game.home_id,
  Game.guest_id,
  count(CASE WHEN Goal.team_id = Game.home_id THEN 1 ELSE NULL END) as home_goal_count,
  count(CASE WHEN Goal.team_id = Game.guest_id THEN 1 ELSE NULL END) as guest_goal_count
FROM
  Game,
  Goal
WHERE
  Game.id = Goal.game_id
group by Game.id, Game.home_id, Game.guest_id


SELECT Game.id, Game.home_id, Game.guest_id, count(CASE WHEN Goal.team_id = Game.home_id THEN 1 ELSE NULL END) as home_goal_count FROM Game, Goal WHERE Goal.id = Goal.game_id group by Game.id