from datetime import date, datetime, timedelta, time

from application import db
from application.auth.models import User
from application.game.game_status import GameStatus
from application.game.models import Game
from application.lineup.models import LineupEntry
from application.memberships.models import Membership
from application.players.models import Player
from application.teams.models import Team


def import_test_data():
    if len(Team.query.all()) > 0:
        # otherwise this will import same data many times
        return

    user = User("hello", "hello", "world")
    db.session().add(user)

    team_hifk = Team("HIFK", "Helsinki")
    team_tps = Team("TPS", "Turku")
    team_hpk = Team("HPK", "Hämeenlinna")
    team_ilves = Team("Ilves", "Tampere")
    team_tappara = Team("Tappara", "Tampere")
    team_jyp = Team("JYP", "Jyväskylä")
    teams = [team_hifk, team_hpk, team_jyp, team_tps, team_ilves, team_tappara]
    hifk_players = parse_players(get_raw_hifk_players(), team_hifk, teams)
    hpk_players = parse_players(get_raw_hpk_players(), team_hpk, teams)
    jyp_players = parse_players(get_raw_jyp_players(), team_jyp, teams)
    tps_players = parse_players(get_raw_tps_players(), team_tps, teams)
    ilves_players = parse_players(get_raw_ilves_players(), team_ilves, teams)
    tappara_players = parse_players(get_raw_tappara_players(), team_tappara, teams)
    add_objects_to_session(teams)
    add_objects_to_session(hifk_players)
    add_objects_to_session(hpk_players)
    add_objects_to_session(jyp_players)
    add_objects_to_session(tps_players)
    add_objects_to_session(ilves_players)
    add_objects_to_session(tappara_players)
    db.session().commit()
    games = generate_games(teams)
    add_objects_to_session(games)
    db.session().commit()


def is_member_during_game(x: Membership, game_start):
    if game_start.date() < x.membership_start:
        return False
    if x.membership_end is None:
        return True
    return game_start.date() < x.membership_end


def membership_to_lineup(x: Membership, game: Game):
    return LineupEntry(game.id, x.id)


def create_game(game_start, home_team, guest_team, result):
    game = Game(home_team.id, guest_team.id, game_start, home_team.city, GameStatus.FINISHED)
    home_memberships = [x for x in home_team.memberships if is_member_during_game(x, game_start)][:20]
    guest_memberships = [x for x in guest_team.memberships if is_member_during_game(x, game_start)][:20]
    game.lineup.extend([membership_to_lineup(x, game) for x in home_memberships])
    game.lineup.extend([membership_to_lineup(x, game) for x in guest_memberships])
    return game


def generate_games(teams):
    def generate_for_month(start_day):
        def conflict_in_schedule(x: Game, home_team, guest_team, game_start):
            if game_start != x.time:
                return False
            return guest_team.id in {x.home_id, x.guest_id} or home_team.id in {x.home_id, x.guest_id}

        games = []
        result = 1
        for home_team in teams:
            for guest_team in [x for x in teams if x != home_team]:
                for x in range(30):
                    game_date = start_day + timedelta(days=x)
                    game_time = time(hour=18)
                    game_start = datetime.combine(game_date, game_time)
                    conflict_games = [x for x in games if conflict_in_schedule(x, home_team, guest_team, game_start)]
                    if len(conflict_games) > 0:
                        continue
                    games.append(create_game(game_start, home_team, guest_team, result))
                    result += 1
                    break
        return games

    start_days = [date(2018, 8, 1), date(2018, 9, 1), date(2018, 10, 1)]
    return [game for x in start_days for game in generate_for_month(x)]


def parse_players(raw_players, team, teams):
    players = []
    number = 1
    other_teams = [x for x in teams if x != team]
    for raw_player in raw_players:
        values = raw_player.split(",")
        player = Player(values[1], values[0], number)
        if number > 2 * len(other_teams):
            membership = Membership({'membership_start': date(2018, 8, 1)})
            player.memberships.append(membership)
            team.memberships.append(membership)
        elif number > len(other_teams):
            membership1 = Membership({'membership_start': date(2018, 8, 1), 'membership_end': date(2018, 8, 31)})
            membership2 = Membership({'membership_start': date(2018, 9, 1)})
            player.memberships.append(membership1)
            player.memberships.append(membership2)
            other_teams[number % len(other_teams)].memberships.append(membership1)
            team.memberships.append(membership2)
        else:
            membership1 = Membership({'membership_start': date(2018, 8, 1), 'membership_end': date(2018, 8, 31)})
            membership2 = Membership({'membership_start': date(2018, 9, 1), 'membership_end': date(2018, 9, 30)})
            membership3 = Membership({'membership_start': date(2018, 10, 1)})
            player.memberships.append(membership1)
            player.memberships.append(membership2)
            player.memberships.append(membership3)
            other_teams[number % len(other_teams)].memberships.append(membership1)
            other_teams[(number + 1) % len(other_teams)].memberships.append(membership2)
            team.memberships.append(membership3)
        players.append(player)
        number += 1
    return players


def get_raw_jyp_players():
    return [
        "Allén,Roni,JYP,Rovaniemi,FIN,,10.10.1998,19,183,91,L",
        "Honka,Anttoni,JYP,Jyväskylä,FIN,,5.10.2000,17,178,79,R",
        "Hytönen,Juha-Pekka,JYP,Jyväskylä,FIN,,22.5.1981,37,178,84,L",
        "Ikonen,Ossi,JYP,Toivakka,FIN,,4.3.1990,28,179,75,L",
        "Immonen,Jarkko,JYP,Rantasalmi,FIN,,19.4.1982,36,181,92,R",
        "Jokinen,Jaakko,JYP,Jämsä,FIN,,17.7.1993,25,189,90,L",
        "Jokinen,Markus,JYP,Mänttä,FIN,,13.9.1988,29,184,91,L",
        "Kalteva,Mikko,JYP,Hyvinkää,FIN,,25.5.1984,34,192,92,L",
        "Kanninen,Henri,JYP,Jyväskylä,FIN,,17.10.1994,23,190,83,L",
        "Kolehmainen,Janne,JYP,Lappeeranta,FIN,,22.3.1986,32,190,101,L",
        "Kuukka,Mikko,JYP,Hämeenkyrö,FIN,,3.11.1985,32,193,92,L",
        "Lahti,Miika,JYP,Konnevesi,FIN,,6.2.1987,31,188,100,L",
        "Laurikainen,Eetu,JYP,Jyväskylä,FIN,,1.2.1993,25,183,88,L",
        "Lindroos,Alex,JYP,Helsinki,FIN,,4.9.1995,22,194,99,L",
        "Louhivaara,Ossi,JYP,Kotka,FIN,,31.8.1983,34,186,89,R",
        "Mikkonen,Justus,JYP,Jyväskylä,FIN,,5.3.1997,21,181,76,L",
        "Mustonen,Matias,JYP,Kajaani,FIN,,26.5.1997,21,175,82,L",
        "Mäenpää,Mikko,JYP,Tampere,FIN,,19.4.1983,35,180,79,L",
        "Perrin,Eric,JYP,Laval,QC,CAN,,1.11.1975,42,175,81,L",
        "Ratinen,Samuli,JYP,Saarijärvi,FIN,,13.4.1998,20,183,92,L",
        "Rooba,Robert,JYP,Tallinna,EST,,2.9.1993,24,191,94,L",
        "Rutanen,Aleksi,JYP,Espoo,FIN,,19.7.1994,24,185,85,L",
        "Saari,Micke,JYP,Kirkkonummi,FIN,,19.4.1994,24,185,81,L",
        "Stråka,Anton,JYP,Pietarsaari,FIN,,6.4.1998,20,191,95,L",
        "Tamminen,Henri,JYP,Espoo,FIN,,22.4.1993,25,190,92,R",
        "Tomasek,David,JYP,Praha,CZE,-,10.2.1996,22,187,87,R",
        "Tuppurainen,Jani,JYP,Oulu,FIN,,30.3.1980,38,180,80,L",
        "Turkulainen,Jerry,JYP,Mikkeli,FIN,,22.9.1998,19,170,72,R",
        "Vainio,Juuso,JYP,Hämeenlinna,FIN,,6.9.1994,23,185,90,R",
        "Viinikainen,Joonas,JYP,-,-,28.8.1998,19,185,77,L",
        "Voutilainen,Joona,JYP,Espoo,FIN,,17.11.1996,21,186,74,L"
    ]


def get_raw_hpk_players():
    return [
        "Almari,Niclas,HPK,Espoo,FIN,,11.5.1998,20,187,78,L",
        "Cornet,Philippe,HPK,Val d Or,QC,CAN,,28.3.1990,28,183,89,L",
        "Friman,Niklas,HPK,Rauma,FIN,,30.8.1993,24,189,88,L",
        "Innala,Jere,HPK,Hämeenlinna,FIN,,17.3.1998,20,174,76,L",
        "Jokinen,Janne,HPK,Janakkala,FIN,,7.10.1999,18,176,75,L",
        "Kainulainen,Harri,HPK,Hämeenlinna,FIN,,21.3.1996,22,188,82,R",
        "Karjalainen,Antti,HPK,Kajaani,FIN,,23.8.1995,22,188,90,L",
        "Karjalainen,Miro,HPK,Vihti,FIN,,23.5.1996,22,197,97,R",
        "Krivosik,Filip,HPK,Bratislava,SVK,,27.3.1999,19,193,94,R",
        "Kuusisto,Jaakko,HPK,Hyvinkää,FIN,,29.8.1997,20,176,80,L",
        "Laatikainen,Arto,HPK,Espoo,FIN,,24.5.1980,38,181,83,L",
        "Laavainen,Roope,HPK,Vantaa,FIN,,23.8.1998,19,187,85,R",
        "Lahti,Janne,HPK,Riihimäki,FIN,,20.7.1982,36,189,91,L",
        "Larmi,Emil,HPK,Lahti,FIN,,28.9.1996,21,182,83,L",
        "Latvala,Otto,HPK,Alajärvi,FIN,,14.7.1999,19,195,86,R",
        "Lehtinen,Oskari,HPK,-,-,9.2.1994,24,185,90,R",
        "Leino,Robert,HPK,Hämeenlinna,FIN,,14.4.1993,25,182,83,R",
        "Lindgren,Jesper,HPK,Umeå,SWE,,19.5.1997,21,183,73,R",
        "Maansaari,Olli,HPK,Valkeakoski,FIN,,20.1.1999,19,181,80,L",
        "Nenonen,Markus,HPK,Jämsänkoski,FIN,,29.10.1992,25,187,94,L",
        "Niemeläinen,Markus,HPK,Kuopio,FIN,,8.6.1998,20,197,93,L",
        "Nikkilä,Petteri,HPK,Hämeenlinna,FIN,,27.7.1992,26,180,83,L",
        "Paajanen,Otto,HPK,Loppi,FIN,,13.9.1992,25,180,87,L",
        "Puustinen,Valtteri,HPK,-,,4.6.1999,19,175,81,R",
        "Riska,Filip,HPK,Pietarsaari,FIN,,13.5.1985,33,184,91,L",
        "Ruokonen,Miro,HPK,Forssa,FIN,,27.3.1996,22,182,87,L",
        "Seppälä,Erkka,HPK,Hämeenlinna,FIN,,19.5.1999,19,174,78,L",
        "Turunen,Teemu,HPK,Helsinki,FIN,,24.11.1995,22,179,80,L",
        "Tuulola,Eetu,HPK,Hämeenlinna,FIN,,17.3.1998,20,190,98,R",
        "Uimonen,Joonas,HPK,-,-,17.8.1998,20,189,86,L",
        "Viitaluoma,Ville,HPK,Espoo,FIN,,16.2.1981,37,184,91,L"
    ]


def get_raw_hifk_players():
    return [
        "Engberg,Teemu,HIFK,Loviisa,FIN,,9.6.1999,19,181,83,L",
        "Engren,Atte,HIFK,Rauma,FIN,,19.2.1988,30,185,84,L",
        "Eronen,Teemu,HIFK,Vantaa,FIN,,22.11.1990,27,180,87,L",
        "Finley,Joe,HIFK,Edina,USA,,29.6.1987,31,203,105,L",
        "Halonen,Niilo,HIFK,Loppi,FIN,,15.7.1998,20,186,77,L",
        "Hämäläinen,Janne,HIFK,Nurmijärvi,FIN,,12.2.1998,20,176,81,L",
        "Jääskä,Juha,HIFK,Helsinki,FIN,,9.2.1998,20,180,88,L",
        "Kangasniemi,Iikka,HIFK,Oulu,FIN,,18.2.1995,23,167,70,L",
        "Kankaanperä,Markus,HIFK,Skellefteå,SWE,,7.4.1980,38,187,97,L",
        "Keränen,Juho,HIFK,Keitele,FIN,,7.4.1985,33,176,89,R",
        "Koivisto,Henrik,HIFK,Kerava,FIN,,9.4.1990,28,180,78,L",
        "Kulmala,Lauri,HIFK,Porvoo,FIN,,3.2.1999,19,188,81,L",
        "Laakso,Aleksi,HIFK,Seinäjoki,FIN,,16.3.1990,28,181,81,L",
        "Lessio,Lucas,HIFK,-,,CAN,23.1.1993,25,185,94,L",
        "Lundell,Anton,HIFK,Espoo,FIN,,3.10.2001,16,185,83,L",
        "Motin,Johan,HIFK,Karlskoga,SWE,,10.10.1989,28,188,96,R",
        "Myllylä,Wiljami,HIFK,Haapajärvi,FIN,,9.4.2001,17,182,71,R",
        "Nordgren,Niklas,HIFK,Helsinki,FIN,,4.5.2000,18,174,75,R",
        "Nykopp,Thomas,HIFK,Helsinki,FIN,,6.3.1993,25,191,88,L",
        "O'Connor,Ryan,HIFK,Hamilton,CAN,,12.1.1992,26,180,85,R",
        "Petrell,Lennart,HIFK,Helsinki,FIN,,13.4.1984,34,191,95,L",
        "Pitkänen,Ilmari,HIFK,Viljakkala,FIN,,18.7.1990,28,182,87,L",
        "Rask,Joonas,HIFK,Savonlinna,FIN,,24.3.1990,28,180,82,R",
        "Ruusu,Markus,HIFK,Jämsä,FIN,,23.8.1997,20,188,83,L",
        "Santala,Tommi,HIFK,-,,,27.6.1979,39,190,95,R",
        "Seppälä,Niko,HIFK,-,-,,9.9.1998,19,185,93,L",
        "Tallberg,Teemu,HIFK,Helsinki,FIN,,13.5.1991,27,186,91,L",
        "Thorell,Erik,HIFK,Karlstad,SWE,,3.3.1992,26,179,83,L",
        "Tyrväinen,Juhani,HIFK,Seinäjoki,FIN,,11.9.1990,27,181,86,L",
        "Ulander,Elias,HIFK,Helsinki,FIN,,13.3.1997,21,182,83,L",
        "Varakas,Ville,HIFK,Helsinki,FIN,,13.2.1984,34,183,85,L",
        "Winberg,Tobias,HIFK,Helsinki,FIN,,2.10.1998,19,189,91,L",
        "Åsten,Micke-Max,HIFK,Helsinki,FIN,,10.6.1992,26,182,88,L"
    ]


def get_raw_tps_players():
    return [
        "Bjorkstrand,Patrick,TPS,Herning,DEN,,1.7.1992,26,184,87,L",
        "Budish,Zach,TPS,Edina,MN,USA,,9.5.1991,27,191,101,R",
        "Ekeståhl-Jonsson,Lucas,TPS,Stockholm,SWE,,25.3.1996,22,185,76,L",
        "Eronen,Elmeri,TPS,Turku,FIN,,27.1.1995,23,176,79,R",
        "Filppula,Ilari,TPS,Vantaa,FIN,,5.11.1981,36,182,89,L",
        "Forsström,Jani,TPS,Lahti,FIN,,19.2.1986,32,186,95,L",
        "Haukeland,Henrik,TPS,-,,6.12.1994,23,186,83,L",
        "Heikkinen,Ilkka,TPS,Rauma,FIN,,13.11.1984,33,190,93,L",
        "Isiguzo,Bernard,TPS,Helsinki,FIN,,2.8.1999,19,180,85,R",
        "Kakko,Kaapo,TPS,Turku,FIN,,13.2.2001,17,186,82,L",
        "Karvonen,Elias,TPS,Turku,FIN,,28.7.1994,24,183,88,L",
        "Kaskinen,Olli,TPS,Raisio,FIN,,27.1.1999,19,184,85,L",
        "Korpikoski,Lauri,TPS,Turku,FIN,,28.7.1986,32,185,93,L",
        "Kuru,Hannu,TPS,Kaarina,FIN,,12.5.1993,25,182,88,L",
        "Lukka,Santeri,TPS,Pori,FIN,,19.7.1991,27,180,86,R",
        "Nevasaari,Arttu,TPS,Oulu,FIN,,23.1.2000,18,181,81,R",
        "Nieminen,Otto,TPS,Somero,FIN,,8.5.1996,22,175,87,L",
        "Nurmi,Markus,TPS,Turku,FIN,,29.6.1998,20,192,76,R",
        "Pajuniemi,Lauri,TPS,Tampere,FIN,,12.9.1999,18,182,83,R",
        "Palve,Oula,TPS,Keuruu,FIN,,19.2.1992,26,183,80,L",
        "Piskula,Joe,TPS,Antigo,WI,USA,,5.7.1984,34,191,93,L",
        "Pylkkänen,Eetu,TPS,Espoo,FIN,,29.4.1998,20,182,88,R",
        "Pärssinen,Juuso,TPS,Hämeenlinna,FIN,,1.2.2001,17,187,82,L",
        "Savolainen,Joonas,TPS,Turku,FIN,,18.6.1997,21,184,86,L",
        "Siiki,Oskari,TPS,Turku,FIN,,5.5.1995,23,182,84,L",
        "Suoranta,Simon,TPS,Vaasa,FIN,,21.5.1992,26,190,94,L",
        "Tirronen,Rasmus,TPS,Kirkkonummi,FIN,,9.11.1990,27,191,92,L",
        "Virtanen,Jonne,TPS,Turku,FIN,,13.3.1988,30,197,113,L",
        "Väyrynen,Teemu,TPS,Joensuu,FIN,,28.4.1997,21,175,78,L"
    ]


def get_raw_ilves_players():
    return [
        "Ahtola,Jerry,Ilves,Turku,FIN,,25.3.1986,32,192,91,L",
        "Antonen,Joose,Ilves,Tampere,FIN,,28.4.1995,23,187,82,R",
        "Flood,Mark,Ilves,Charlottetown,PE,CAN,,29.9.1984,33,186,88,R",
        "Generous,Matt,Ilves,Cheshire,CT,USA,,4.5.1985,33,191,88,R",
        "Haapanen,Topias,Ilves,Pirkkala,FIN,,27.4.1998,20,185,84,L",
        "Helenius,Riku,Ilves,Pälkäne,FIN,,1.3.1988,30,190,83,L",
        "Ikonen,Joona,Ilves,Tampere,FIN,,14.5.1998,20,178,82,R",
        "Laakso,Jerry,Ilves,-,,5.3.1993,25,180,79,L",
        "Laaksonen,Oskari,Ilves,Tampere,FIN,,2.7.1999,19,188,75,R",
        "Laitamäki,Elias,Ilves,Seinäjoki,FIN,,21.8.2000,17,187,93,L",
        "Lehtonen,Antti,Ilves,Jyväskylä,FIN,,6.8.1993,25,183,80,L",
        "Leimu,Juha,Ilves,Tampere,FIN,,30.1.1983,35,185,84,L",
        "Lepaus,Teemu,Ilves,Tampere,FIN,,12.3.1993,25,181,81,L",
        "Liuksiala,Juho,Ilves,Vammala,FIN,,2.11.1995,22,171,80,R",
        "Matinpalo,Nikolas,Ilves,-,-,5.10.1998,19,190,92,R",
        "Mieho,Panu,Ilves,Helsinki,FIN,,24.1.1995,23,186,84,L",
        "Nalli,Miro,Ilves,-,-,28.1.1999,19,187,82,L",
        "Parikka,Jarkko,Ilves,Imatra,FIN,,6.9.1997,20,182,87,L",
        "Rautiainen,Teemu,Ilves,Nurmijärvi,FIN,,13.3.1992,26,169,75,L",
        "Ruotsalainen,Arttu,Ilves,Oulu,FIN,,29.10.1997,20,173,81,L",
        "Salmela,Tuomas,Ilves,Tornio,FIN,,30.6.1995,23,188,92,L",
        "Savilahti,Eero,Ilves,Tampere,FIN,,10.8.1992,26,186,89,L",
        "Suomi,Eemeli,Ilves,Tampere,FIN,,4.12.1995,22,177,82,L",
        "Tamminen,Juhani,Ilves,Hämeenlinna,FIN,,11.1.1989,29,190,93,L",
        "Vainio,Olli,Ilves,Tampere,FIN,,23.4.1994,24,185,82,R",
        "Vainionpää,Samuli,Ilves,-,-,5.10.1999,18,190,94,L",
        "Valtonen,Julius,Ilves,Tuusula,FIN,,9.8.1995,23,190,93,R"
    ]


def get_raw_tappara_players():
    return [
        "Bäckström,Niklas,Tappara,Helsinki,FIN,,13.2.1978,40,186,89,L",
        "Elorinne,Aleksi,Tappara,Joensuu,FIN,,3.2.1990,28,196,99,L",
        "Erkinjuntti,Antti,Tappara,Rovaniemi,FIN,,30.5.1986,32,181,86,L",
        "Has,Hugo,Tappara,-,,2.2.2001,17,194,88,R",
        "Heljanko,Christian,Tappara,Porvoo,FIN,,2.4.1997,21,182,77,L",
        "Jasu,Juhani,Tappara,Eurajoki,FIN,,19.1.1988,30,184,89,R",
        "Järvinen,Jan-Mikael,Tappara,Pirkkala,FIN,,26.2.1988,30,174,78,L",
        "Järvinen,Matti,Tappara,Lontoo,GBR,,14.10.1989,28,195,98,L",
        "Karjalainen,Jere,Tappara,Helsinki,FIN,,23.5.1992,26,175,80,R",
        "Kemiläinen,Valtteri,Tappara,Jyväskylä,FIN,,16.12.1991,26,184,87,R",
        "Kukkonen,Miska,Tappara,Jokioinen,FIN,-,19.6.2000,18,185,89,R",
        "Kuusela,Kristian,Tappara,Seinäjoki,FIN,,19.2.1983,35,175,82,R",
        "Lehtonen,Matias,Tappara,-,-,4.8.1995,23,184,80,L",
        "Levtchi,Anton,Tappara,Varkaus,FIN,,28.11.1995,22,182,84,L",
        "Luoto,Joona,Tappara,Lempäälä,FIN,,26.9.1997,20,190,88,L",
        "Malinen,Jarkko,Tappara,Kuopio,FIN,,17.3.1988,30,188,84,L",
        "Moilanen,Sami,Tappara,Sipoo,FIN,,22.1.1999,19,175,84,L",
        "Mäkinen,Otto,Tappara,Tampere,FIN,,21.5.1998,20,188,81,L",
        "Mäntylä,Tuukka,Tappara,Tampere,FIN,,25.5.1981,37,171,85,L",
        "Ojamäki,Niko,Tappara,Pori,FIN,,17.6.1995,23,180,84,R",
        "Puistola,Patrik,Tappara,Tampere,FIN,,11.1.2001,17,183,75,L",
        "Rantakari,Otso,Tappara,Helsinki,FIN,,19.11.1993,24,182,84,R",
        "Rauhala,Otto,Tappara,Ylöjärvi,FIN,,12.4.1995,23,180,90,L",
        "Rautanen,Juho,Tappara,Mäntsälä,FIN,-,25.5.1997,21,183,82,L",
        "Rautiainen,Kimmo,Tappara,Savonlinna,FIN,,9.3.1998,20,177,75,L",
        "Tanus,Kristian,Tappara,Tampere,FIN,,17.8.2000,18,172,72,L",
        "Utunen,Toni,Tappara,Kokkola,FIN,,27.4.2000,18,180,78,L",
        "Vittasmäki,Veli-Matti,Tappara,Turku,FIN,,3.7.1990,28,186,93,L",
        "Záborský,Tomas,Tappara,Trencin,SVK,,14.11.1987,30,184,87,L"
    ]


def add_objects_to_session(objects):
    for object in objects:
        db.session().add(object)
