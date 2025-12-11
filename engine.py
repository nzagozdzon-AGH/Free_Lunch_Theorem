# Imports
import random
import numpy as np
import math
import matplotlib.pyplot as plt

def monte_carlo(offer: dict, overround: float, stake: int = 10, odds: float = None) -> np.ndarray:
    """
    Performs Monte carlo simulation, but it's really qucik.
    """
    if odds is None:
        odds = offer["min_odds"] + 0.15 
    legs = offer["legs"]
    money = offer["bonus"] + offer["deposit"]
    req_turnover = offer["turnover"]
    tax = offer["tax"]
    freebet = offer["free_bet"]
    number_of_simulations = 10000
    p_win_regular_bet = 1/(odds*overround**legs)
    needed_bets = math.ceil(req_turnover/stake)


    random_values = np.random.random(size=(number_of_simulations, needed_bets))
    won_bets = random_values < p_win_regular_bet
    won_bets = won_bets.astype(float)

    if freebet is not None:
        p_win_freebet = 1/(freebet["odds"]*overround**freebet["legs"])
        freebet_random_values = np.random.random(size=(number_of_simulations))
        won_freebets = freebet_random_values < p_win_freebet
        won_freebets = won_freebets.astype(float)
    else:
        won_freebets = 0

    if tax:
        won_bets *= stake*0.88*odds

        if freebet is not None:
            if freebet["SR"]:
                won_freebets *= freebet["value"]*freebet["odds"]*0.88
            else:
                winnings = freebet["value"]*freebet["odds"]*0.88 - freebet["value"]
                won_freebets *= winnings
    else:
        won_bets *= stake*odds

        if freebet is not None:
            if freebet["SR"]:
                won_freebets *= freebet["value"]*freebet["odds"]
            else:
                winnings = freebet["value"]*freebet["odds"] - freebet["value"]
                won_freebets *= winnings

    won_bets -= stake

    # Tracks history of balance
    history = np.cumsum(won_bets, axis=1) + money
    fails = history < 0
    fails = np.any(fails, axis=1)
    results = history[:,-1] + won_freebets - offer["deposit"] 
    results[fails] = -1*money

    return results


def overround_calculator(list_of_odds: list) -> int:
    """
    It calculates bookmaker overround for given betting odds. 
    """
    avg_overround = 0
    for odds in list_of_odds:
        p1 = 1/odds[0]
        p2 = 1/odds[1]
        # If more than two odds where given for function
        if len(odds) == 3:
            p3 = 1/odds[2]
        else:
            p3 = 0
        overround = p1+p2+p3
        avg_overround += overround
    avg_overround /= len(list_of_odds)
    return avg_overround


def visualize_results(results: np.ndarray, title: str, color: str = "#0A2F80CF") -> None:
    """
    Displays histogram to present data from monte carlo simulation.
    """
    # Calculating p_win and of loss
    win_count = np.sum(results > 0)
    total = len(results)
    p_win = (win_count / total) * 100
    p_loss = 100-p_win

    plt.figure(figsize=(10, 6))
    plt.hist(results, bins=26, color=color, edgecolor='black')
    plt.axvline(0, color="#a80000", linewidth=5, linestyle='--')
    
    y_min, y_max = plt.ylim()
    x_min, x_max = plt.xlim()
    

    plt.text(x_min * 0.5, y_max * 0.9, 
             f"Chance of loss:\n{p_loss:.1f}%", 
             color='#a80000', fontsize=12, fontweight='bold', ha='center')


    text_pos_x = max(x_max * 0.5, x_max * 0.1) if x_max > 0 else 0
    
    plt.text(text_pos_x, y_max * 0.9, 
             f"Chance of profit:\n{p_win:.1f}%", 
             color='#27ae60', fontsize=12, fontweight='bold', ha='center')


    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Net Result (PLN)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.6)
    
    plt.show()


def confidence_interval(results: np.ndarray) -> str:
    lower = np.percentile(results, 25)
    upper = np.percentile(results, 75)
    return f"50% confidence interval: [{lower:.2f}, {upper:.2f}]"


def bet_free_bet(free_bet_dict: dict, overround: float, tax: bool) -> float:
    """
    Performs simulation of betting a single free bet
    """
    stake = free_bet_dict["value"]
    odds = free_bet_dict["odds"]
    overround = overround**free_bet_dict["legs"]
    p_win = 1/odds/overround

    if random.random() < p_win:
        if free_bet_dict["SR"] and tax:
            return stake*0.88*odds
        elif not free_bet_dict["SR"] and tax:
            return stake*0.88*odds - stake
        elif free_bet_dict["SR"] and not tax:
            return stake*odds
        else:
            return stake*odds - stake
    else:
        return 0
    

def chance_of_profit(results: np.ndarray) -> float:
    """
    It calculates chance of going positive when playing given offer
    """
    win_count = np.sum(results > 0)
    total = len(results)
    p_win = (win_count / total) * 100
    return p_win


def widget(offer: dict, overround: float, title: str, stake: int = 10, odds: float = None, color: str = "#0A2F80CF") -> None:
    overround = overround/100 + 1
    results = monte_carlo(offer, overround, stake, odds)
    visualize_results(results, title, color)  