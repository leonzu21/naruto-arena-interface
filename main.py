import requests
import time
import json
from bs4 import BeautifulSoup
import sys
import os

TOKEN_FILE = "token.txt"

class LoadingService:
    def __init__(self):
        self.loading_symbols = ["|", "/", "-", "\\"]
        self.idx = 0

    def print_message(self, message: str):
        sys.stdout.write(f"\r{message}")
        sys.stdout.flush()

    def print_loading(self, message: str):
        sys.stdout.write(f"\r{message} {self.loading_symbols[self.idx]}")
        sys.stdout.flush()
        self.idx = (self.idx + 1) % len(self.loading_symbols)


class NarutoArenaBot:
    BASE_URL = "https://www.naruto-arena.site/api/"
    HEADERS = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "origin": "https://www.naruto-arena.site",
        "pragma": "no-cache",
        "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }

    TEAM = ["Uchiha Sasuke", "Uzumaki Naruto", "Kin Tsuchi"]

    def __init__(self):
        self.token = self.get_token()
        self.headers = {
            **self.HEADERS,
            "authorization": f"Bearer {self.token}",
            "cookie": f"token={self.token}",
        }

        self.team = self.TEAM
        self.loading_service = LoadingService()

    def get_token(self) -> str:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as file:
                token = file.read().strip()
                if token:
                    print("Token loaded from file.")
                    return token

        token = self.handle_login()
        with open(TOKEN_FILE, "w") as file:
            file.write(token)
        return token

    def handle_login(self) -> str:
        url = self.BASE_URL + "login"
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        data = {"action": "login", "username": username, "password": password}
        res = requests.post(url, headers=self.HEADERS, json=data)
        return res.json()["var_content"]["newToken"]

    def handle_search_game(self, player_id: str, team: list) -> requests.Response:
        url = self.BASE_URL + "handleingame"
        data = {
            "action": "searchGame",
            "gameType": "Quick",
            "playerId": player_id,
            "team": team,
        }

        headers = {
            **self.headers,
            "referer": "https://www.naruto-arena.site/light-version/selection",
        }
        return requests.post(url, headers=headers, json=data)

    def handle_check_if_in_battle(self) -> requests.Response:
        url = self.BASE_URL + "handleingame"
        data = {"action": "checkIfInBattle"}

        headers = {
            **self.headers,
            "referer": "https://www.naruto-arena.site/light-version/selection",
        }
        return requests.post(url, headers=headers, json=data)

    def handle_check_if_confirmed_battle(self) -> requests.Response:
        url = self.BASE_URL + "handleingame"
        data = {"action": "checkIfConfirmedBattle"}

        headers = {
            **self.headers,
            "referer": "https://www.naruto-arena.site/light-version/selection",
        }
        return requests.post(url, headers=headers, json=data)

    def handle_request_end_turn(self) -> requests.Response:
        url = self.BASE_URL + "handleingame"
        data = {"action": "requestEndTurn", "languagePreference": "English"}
        return requests.post(url, headers=self.headers, json=data)

    def handle_surrender(self) -> requests.Response:
        url = self.BASE_URL + "handleingame"
        data = {"action": "surrender"}
        return requests.post(url, headers=self.headers, json=data)

    def handle_get_battle(self) -> requests.Response:
        url = "https://www.naruto-arena.site/light-version/battle"
        headers = {
            **self.headers,
            "referer": "https://www.naruto-arena.site/light-version/selection",
        }
        return requests.get(url, headers=headers)

    def get_script_contents(self, html: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__")
        return json.loads(script_tag.contents[0])

    def handle_pass_turn(self, queue, removedChakra) -> requests.Response:
        url = self.BASE_URL + "handleingame"
        data = {
            "action": "passTurn",
            "queue": queue,
            "exchangeInformation": [],
            "removedChakra": removedChakra,
            "languagePreference": "English",
        }
        return requests.post(url, headers=self.headers, json=data)

    def battle(self):
        res = self.handle_get_battle()
        if res.status_code == 200:
            html = res.text
            script_contents = self.get_script_contents(html)
            try:
                battle_state = script_contents["props"]["pageProps"]["serverBattleResponse"]["battleState"]
            
                turn = battle_state["turn"]
                players = battle_state["players"]
                my_chars = [
                    players[0]["team"]["char0"],
                    players[0]["team"]["char1"],
                    players[0]["team"]["char2"],
                ]
                opponent_chars = [
                    players[1]["team"]["char0"],
                    players[1]["team"]["char1"],
                    players[1]["team"]["char2"],
                ]
                chakra = players[0]["chakra"]
                battle_info = self.wait_for_turn(turn, players[0]["playerId"])

                print(battle_info)

                self.print_battle_info(my_chars, opponent_chars, chakra)

                print("\nIt's your turn!")
                self.show_menu()
                if self.check_for_surrender():
                    self.handle_surrender()
                    print("\nYou surrendered.")
                else:
                    if battle_info:
                        battle_info = battle_info["content"]
                    else:
                        battle_info = battle_state

                    players = battle_info["players"]
                    my_chars = [
                        players[0]["team"]["char0"],
                        players[0]["team"]["char1"],
                        players[0]["team"]["char2"],
                    ]
                    opponent_chars = [
                        players[1]["team"]["char0"],
                        players[1]["team"]["char1"],
                        players[1]["team"]["char2"],
                    ]
                    chakra = players[0]["chakra"]

                    self.print_battle_info(my_chars, opponent_chars, chakra)
                    self.handle_turn(my_chars, opponent_chars, chakra)
            except KeyError:
                print("Battle ended.")
                go_again = input("Do you want to search for another game? (y/n): ")

                if go_again == "y":
                    self.run(getattr(self, "player_id", "leonzu"))
                else:
                    print("Goodbye!")

    def handle_turn(self, my_chars, opponent_chars, chakra):
        for i, char in enumerate(my_chars):
            print(f"\n{char['name']} (HP: {char['health']}):")
            for j, skill in enumerate(char["skills"]):
                status = "Available" if not skill["outtagame"] else "Unavailable"
                energy = ", ".join(skill["energy"])
                print(f"  [{i}-{j}] {skill['name']} - {status} - Energy: [{energy}]")

        def print_my_characters():
            print("My characters:")
            for i, char in enumerate(my_chars):
                print(f"  [{i}] {char['name']} (HP: {char['health']})")

        def print_character_skills(char):
            print(f"\nSkills for {char['name']} (HP: {char['health']}):")
            for j, skill in enumerate(char["skills"]):
                status = "Available" if not skill["outtagame"] else "Unavailable"
                energy = ", ".join(skill["energy"])
                print(f"  [{j}] {skill['name']} - {status} - Energy: [{energy}]")

        def print_opponent_characters():
            print("Opponent characters:")
            for i, char in enumerate(opponent_chars):
                print(f"  [{i+3}] {char['name']} (HP: {char['health']})")

        queue = []
        removedChakra = []
        choosing = True
        while choosing:
            print_my_characters()
            char_used = input("Choose a character (Press Enter to end turn): ")

            if char_used != "":
                if not char_used.isdigit() or int(char_used) not in range(len(my_chars)):
                    print("Invalid character index.")
                    continue
                char_idx = int(char_used)
                print_character_skills(my_chars[char_idx])
                skill_used = input("Choose a skill: ")

                if skill_used != "":
                    if not skill_used.isdigit() or int(skill_used) not in range(len(my_chars[char_idx]["skills"])):
                        print("Invalid skill index.")
                        continue
                    skill_idx = int(skill_used)
                    print_my_characters()
                    print_opponent_characters()
                    target = input("Choose a target: ")

                    if target != "":
                        if not target.isdigit() or int(target) not in range(len(opponent_chars) + len(my_chars)):
                            print("Invalid target index.")
                            continue
                        target_val = int(target)
                        side = 0
                        if target_val > 2:
                            side = 1
                            target_val -= 3
                        queue.append(
                            {
                                "name": my_chars[char_idx]["skills"][skill_idx]["name"],
                                "menu_local": [0, char_idx, skill_idx],
                                "side": 0,
                                "index": char_idx,
                                "usedOn": {"s": side, "i": target_val},
                                "new": True,
                            }
                        )
                        skill_energy = my_chars[char_idx]["skills"][skill_idx]["energy"]
                        for energy in skill_energy:
                            if energy in chakra:
                                chakra.remove(energy)
                        random_count = skill_energy.count("Random")
                        for _ in range(random_count):
                            print(f"Chakra: {chakra}")
                            chakra_used = input("Choose a chakra to spend: ")
                            if chakra_used != "":
                                if not chakra_used.isdigit() or int(chakra_used) not in range(len(chakra)):
                                    print("Invalid chakra index.")
                                    continue
                                removedChakra.append(chakra[int(chakra_used)])
                                chakra.pop(int(chakra_used))

            if char_used == "":
                choosing = False

        res = self.handle_pass_turn(queue, removedChakra)
        if res.status_code == 200:
            self.battle()
        else:
            print("An error occurred.")

    def print_battle_info(self, my_chars, opponent_chars, chakra):
        print("My characters:")
        for char in my_chars:
            print(f"{char['name']} - {char['health']} HP")
        print(f"Chakra: {chakra}")
        print("Opponent characters:")
        for char in opponent_chars:
            print(f"{char['name']} - {char['health']} HP")

    def wait_for_turn(self, current_turn, my_player_id) -> dict:
        while current_turn != my_player_id:
            time.sleep(2)
            res = self.handle_request_end_turn()
            if (
                res.status_code == 200
                and res.headers.get("Content-Type") == "application/json; charset=utf-8"
            ):
                if res.json() == {"message": "complete"}:
                    self.loading_service.print_loading("Waiting for your turn...")
                else:
                    current_turn = my_player_id
                    return res.json()

        return None

    def show_menu(self):
        print("\nMenu:")
        print("1. Battle")
        print("2. Surrender")

    def check_for_surrender(self) -> bool:
        user_input = input("Choose an option (1 or 2): ")
        return user_input == "2"

    def run(self, player_id: str):
        self.player_id = player_id
        res_search_game = self.handle_search_game(player_id, self.team)
        if res_search_game.status_code == 200:
            self.loading_service.print_message("Searching for a game...")
            res = self.handle_check_if_in_battle()
            count = 0
            while res.headers.get("Content-Length") == "0":
                self.loading_service.print_loading("Searching for a game...")
                res = self.handle_check_if_in_battle()
                count += 1
                if count == 25:
                    print("\nNo game found...")
                    return
                time.sleep(1)
            if res.json()["action"] == "cancelBattle":
                print("\nGame canceled...")
                return
            if res.json()["action"] == "opponentFound":
                print("\nOpponent found...")
                res = self.handle_check_if_confirmed_battle()
                if res.json()["action"] == "startBattle":
                    print("Battle started...")
                    self.battle()
                elif res.json()["action"] == "cancelBattle":
                    print("\nOpponent canceled the battle...")
                    self.run(player_id)


if __name__ == "__main__":
    bot = NarutoArenaBot()
    player_id = "leonzu"
    bot.run(player_id)
