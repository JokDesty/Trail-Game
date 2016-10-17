#!/usr/bin/python3
# coding=utf-8
import figlet_helper
import screen
import screens

from debug import *
from misc_utils import *

from events import events
import survivors

from datetime import timedelta

# This is the main file for the trail game.


# You must use this method when changing the time
def pass_time(hours):
    if survivors.current_datetime.hour == 20 or (int(survivors.current_datetime.hour) < 20 < int(survivors.current_datetime.hour + hours)):
        amount_of_food = 0
        food = survivors.group_inventory["Food"]

        if food is not None:
            amount_of_food = food["amount"]

        remaining_survivors = count_survivors(True, True, False, False)
        required_food = remaining_survivors * 10

        if amount_of_food < required_food:
            screen.print_notification("You did not have enough food to feed the party fully, they go hungry.")

            amount_not_fed = required_food - amount_of_food

            for survivor in survivors.survivor_list:
                if survivor["alive"] and not survivor["zombified"]:
                    survivor["health"] -= int(amount_not_fed * 1.5)

            food["amount"] = 0
        else:
            # TODO: what if you're alone, or in a 2, or a 3?
            screen.print_notification("The party enjoys a full meal together.")

            food["amount"] -= required_food

        screen.print_notification("You have " + str(food["amount"]) + " food remaining.")

    survivors.ticks_elapsed += 1
    survivors.current_datetime += timedelta(hours=hours)
    survivors.distance_travelled += survivors.car_speed


# This is called every tick of the game
def game_tick():
    if not survivors.survivor_list[0]["alive"]:
        screens.open_screen(screens.screen_list["dead"])

    screens.open_screen(screens.screen_list["travelling"])

    if survivors.ticks_elapsed > 3:
        for event in events:
            event_random = random.uniform(0.0, 100.0)
            if event["occurrence_chance"] > event_random:
                event_function = None

                if event["notification_handler_function"] is not None:
                    event_function = event["notification_handler_function"]

                # TODO: Add support for other handler functions that are more complex than a notification

                if event_function is not None:
                    did_execute = event_function()

                    if did_execute:
                        # NOTE: We don't want more than one event per tick if the event worked
                        break

    for survivor in survivors.survivor_list:
        if survivor["alive"] and survivor["zombified"]:
            random_number = random.randrange(1, 100)

            if random_number <= 50:
                random_survivor = get_random_survivor(True, True, False, False)
                survivor["alive"] = False

                # TODO: Subtract a bullet from ammo?
                screen.print_notification(random_survivor["name"] + " managed to shoot a zombified " + survivor["name"] + " dead.")

                # NOTE: We don't want another zombie event this tick, as one has just been shot
                break
            elif random_number <= 90:
                random_survivor = get_random_survivor(True, True, False, False)
                random_damage = random.randrange(1, 20)

                random_survivor["health"] -= random_damage

                screen.print_notification("A zombified " + survivor["name"] + " damaged " + random_survivor["name"] + " for " + str(random_damage) + " damage.")
            else:
                random_survivor = get_random_survivor(False, False, False, False)

                if random_survivor is not None:
                    random_survivor["bitten"] = True

                    screen.print_notification("A zombified " + survivor["name"] + " bit " + random_survivor["name"] + ".")

    for survivor in survivors.survivor_list:
        if survivor["alive"] and survivor["bitten"] and not survivor["zombified"]:
            ticks_since_bitten = survivor["ticks_since_bitten"]

            if ticks_since_bitten > 4:
                if ticks_since_bitten < 24:
                    random_number = random.randrange(1, 100)

                    should_turn = random_number <= ticks_since_bitten * 2
                else:
                    should_turn = True

                if should_turn:
                    survivor["zombified"] = True

                    screen.print_notification(survivor["name"] + " turned into a zombie.")

            survivor["ticks_since_bitten"] = ticks_since_bitten + 1

    next_city = get_next_city(survivors.distance_travelled)

    if next_city is None:
        screens.screen_list["win"]["draw_function"]()

    if next_city["distance_from_start"] - survivors.distance_travelled <= survivors.car_speed:
        screen.print_notification("You arrived in " + next_city["name"] + ".")

        if next_city["name"] == "New York":
            screens.screen_list["win"]["draw_function"]()

        screens.open_screen(screens.screen_list["city"])

    for survivor in survivors.survivor_list:
        if survivor["alive"] and survivor["health"] <= 0:
            survivor["alive"] = False

            screen.print_notification(survivor["name"] + " died.")

    pass_time(1)


# This is the program entry point
def main():
    screen.init()
    screen.clear()

    # while True:
    #     big_font = figlet_helper.load_font("resources/fonts/big.flf")
    #     screen.draw_ascii_font_text(0, 0, "Dad is that you?", big_font)
    #
    #     screen.flush()
    #
    #     time.sleep(1)

    # while True:
    #     decision_text = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."

    #     #decision_text = "This is some text that should wrap to the next line because it is so long. If it doesn't, it probably needs fixing."

    #     screen.draw_decision(decision_text,
    #         ["Decision 1", "Decision 2"])

    #     screen.flush()

    #     time.sleep(1)
    screens.open_screen(screens.screen_list["travelling"])

    # The main game loop
    while True:
        # Simulate one game tick
        game_tick()

        # NOTE: This may cause weird drawing bugs
        if screens.current_screen is not None and screens.current_screen["name"] != "travelling":
            # NOTE: I think this is okay to do because the current screen is technically the travelling screen
            screens.screen_list["travelling"]["draw_function"]()


# Are we being run as a script? If so, run main().
# '__main__' is the name of the scope in which top-level code executes.
# See https://docs.python.org/3.4/library/__main__.html for explanation
if __name__ == "__main__":
    main()
