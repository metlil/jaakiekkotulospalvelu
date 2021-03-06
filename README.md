# Jääkiekkotulospalvelu

Harjoitustyönä tehty sovellus kurssille Tietokantasovellus, kevät 2018.
Sovellus Herokussa:
https://jaakiekkotulospalvelu.herokuapp.com/

## Aihekuvaus

Tarkoitus välittää jääkiekkopelien loppu- ja välituloksia reaaliaikaisesti. Tulospalvelutietokannasta saadaan
raportteina päättyneen ja keskeneräisen ottelun maalit ja kokoonpano.
Sieltä saadaan myös sarjataulukko, johon laskettu kaikkien joukkueiden pisteet (maalien, voittojen, häviöiden, tasapelien
mukaan) ja järjestetty joukkueet alenevaan järjestykseen.

## Toimintoja

*   Ottelun luonti, muokkaus, poisto
*   Joukkueiden luonti
*	Pelaajien luonti, poisto, muokkaus (jäsenyydet joukkueisiin)
*	kokoonpanon lisäys/muokkaus otteluun
*	pelitilanteen lisäys/muokkaus/poisto otteluun (maalit)
*	pelin tuloksen vahvistaminen ja pelin merkitseminen loppuneeksi
*	kirjaajan kirjautuminen
*	otteluiden tulokset
*	sarjataulukko
*   kirjautuneille käyttäjille oma lista eniten kiinnostavista peleistä

## Testaaminen
Sovelluksen herokuun on lisätty admin käyttäjä testausta varten. Kirjautuminen
tapahtuu navigointipalkin oikeasta kulmasta Log in -linkistä syöttämällä usernameksi "admin" ja salasanaksi "nimda".

## Linkit:

[Dokumentaatio](documentation/jaakiekkotulospalvelu_dokumentaatio.pdf)

[User storyt](documentation/user_stories.md)

[Tietokantakaavio](documentation/jaakiekkotulospalvelu_database_diagram.pdf)
