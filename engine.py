# Imports
import random
import numpy as np
import matplotlib.pyplot as plt

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

def one_bet(odds: float, stake: float, overround: float, legs: int, tax: bool) -> float:
    """
    Simulates one bet and returns winnings if won.
    """
    overround = overround**legs
    p_win = 1/odds/overround

    if random.random() < p_win:
        if tax:
            return stake*0.88*odds # adjusted for tax
        else:
            return stake*odds
    else:
        return 0
    
def many_bets(odds: float, stake: float, overround: float, legs: int, tax: bool, money: int, req_turnover: int, free_bet: dict | None) -> float:
    """
    Simulates turnover of the bonus
    """
    turnover = 0
    if free_bet is not None:
        money += bet_free_bet(free_bet, overround, tax)
    while turnover < req_turnover:
        money -= stake
        turnover += stake
        money += one_bet(odds, stake, overround, legs, tax)
        if money <= 0:
            break
    return money

def monte_carlo(offer: dict, overround: float) -> np.ndarray:
    """
    Performs Monte Carlo simulation of given betting strategy
    """
    odds = offer["min_odds"] + 0.15 # I add a small value, cause it's hard to find offer with exatcly minimal odds
    stake = 10 # For any offer I reccomend betting 10 PLN in each bet for diversification
    legs = offer["legs"]
    money = offer["bonus"] + offer["deposit"]
    req_turnover = offer["turnover"]
    tax = offer["tax"]
    free_bet = offer["free_bet"]

    results = []
    tries = 10000
    while tries > 0:
        tries -= 1
        results.append(many_bets(odds, stake, overround, legs, tax, money, req_turnover, free_bet))
    results = np.array(results) - offer["deposit"]
    return results


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