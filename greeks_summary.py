#!/usr/bin/env python3
"""
Option Greeks Summary and Practical Examples

This script provides practical examples and insights about Option Greeks
that complement the comprehensive notebook.
"""

import math

# Import our validated Greeks functions
from greeks_validation import (
    black_scholes_price, delta_analytical, gamma_analytical, 
    theta_analytical, vega_analytical, rho_analytical,
    GreeksCalculator
)

def practical_hedging_example():
    """Demonstrate practical delta hedging scenario"""
    print("=" * 60)
    print("PRACTICAL DELTA HEDGING EXAMPLE")
    print("=" * 60)
    print()
    
    # Portfolio: Long 10 call contracts (1000 shares equivalent)
    S, K, T, r, sigma = 100, 105, 0.25, 0.05, 0.25  # 3-month OTM call
    contracts = 10
    shares_per_contract = 100
    total_shares_equivalent = contracts * shares_per_contract
    
    calc = GreeksCalculator(S, K, T, r, sigma)
    call_price = calc.all_greeks('call')['price']
    call_delta = calc.all_greeks('call')['delta']
    
    hedge_shares = int(call_delta * total_shares_equivalent)
    
    print(f"Portfolio: Long {contracts} call contracts (Strike ${K}, {T*12:.0f} months)")
    print(f"Current stock price: ${S}")
    print(f"Call option price: ${call_price:.4f}")
    print(f"Call delta: {call_delta:.4f}")
    print(f"")
    print(f"Delta hedge: Sell {hedge_shares} shares of underlying stock")
    print(f"Hedge ratio: {call_delta:.1%} (for every option, sell {call_delta:.2f} shares)")
    print()
    
    # Scenario analysis
    print("SCENARIO ANALYSIS: Stock price movements")
    print("-" * 50)
    print(f"{'Stock Move':<12} {'New Price':<12} {'Option P&L':<12} {'Stock P&L':<12} {'Total P&L':<12}")
    print("-" * 60)
    
    for move in [-3, -2, -1, 0, 1, 2, 3]:
        new_S = S + move
        calc_new = GreeksCalculator(new_S, K, T, r, sigma)
        new_call_price = calc_new.all_greeks('call')['price']
        
        option_pnl = (new_call_price - call_price) * total_shares_equivalent
        stock_pnl = -move * hedge_shares  # Negative because we're short stock
        total_pnl = option_pnl + stock_pnl
        
        print(f"{move:+8.0f}     ${new_S:8.2f}     ${option_pnl:+8.0f}     ${stock_pnl:+8.0f}     ${total_pnl:+8.0f}")
    
    print()
    print("Note: Small total P&L shows effective hedging. Larger moves show gamma risk.")
    print()

def time_decay_analysis():
    """Analyze time decay (Theta) behavior"""
    print("=" * 60)
    print("TIME DECAY (THETA) ANALYSIS")
    print("=" * 60)
    print()
    
    S, K, r, sigma = 100, 100, 0.05, 0.2  # ATM option
    
    print("Theta acceleration as expiration approaches (ATM Call):")
    print(f"{'Days to Exp':<12} {'Option Price':<14} {'Theta/Day':<12} {'% of Price':<12}")
    print("-" * 52)
    
    for days in [90, 60, 30, 21, 14, 7, 3, 1]:
        T = days / 365
        calc = GreeksCalculator(S, K, T, r, sigma)
        greeks = calc.all_greeks('call')
        price = greeks['price']
        theta_daily = greeks['theta']
        theta_percent = (abs(theta_daily) / price) * 100
        
        print(f"{days:8.0f}     ${price:8.4f}     ${theta_daily:8.4f}     {theta_percent:8.2f}%")
    
    print()
    print("Key Insights:")
    print("- Theta accelerates dramatically in final weeks")
    print("- Daily decay becomes significant portion of option value")
    print("- Time decay is highest for at-the-money options")
    print()

def volatility_impact_analysis():
    """Analyze volatility (Vega) impact"""
    print("=" * 60)
    print("VOLATILITY (VEGA) IMPACT ANALYSIS")
    print("=" * 60)
    print()
    
    S, K, T, r = 100, 100, 1.0, 0.05  # 1-year ATM option
    
    print("Impact of volatility changes on option value:")
    print(f"{'Vol Change':<12} {'New Vol':<10} {'Call Price':<12} {'Put Price':<12} {'Price Change':<12}")
    print("-" * 60)
    
    base_sigma = 0.20
    calc_base = GreeksCalculator(S, K, T, r, base_sigma)
    base_call = calc_base.all_greeks('call')['price']
    base_put = calc_base.all_greeks('put')['price']
    
    for vol_change in [-0.10, -0.05, -0.02, 0, +0.02, +0.05, +0.10]:
        new_sigma = base_sigma + vol_change
        if new_sigma <= 0:
            continue
            
        calc_new = GreeksCalculator(S, K, T, r, new_sigma)
        new_call = calc_new.all_greeks('call')['price']
        new_put = calc_new.all_greeks('put')['price']
        
        call_change = new_call - base_call
        put_change = new_put - base_put
        
        print(f"{vol_change:+8.0%}     {new_sigma:6.0%}     ${new_call:8.4f}     ${new_put:8.4f}     ${call_change:+8.4f}")
    
    vega = calc_base.all_greeks('call')['vega']
    print(f"\nVega (per 1% vol change): ${vega:.4f}")
    print("Note: Vega is same for calls and puts")
    print()

def moneyness_analysis():
    """Analyze Greeks across different moneyness levels"""
    print("=" * 60)
    print("GREEKS vs MONEYNESS ANALYSIS")
    print("=" * 60)
    print()
    
    S, T, r, sigma = 100, 0.25, 0.05, 0.2  # 3-month options
    
    print("Call Option Greeks at different strike prices:")
    print(f"{'Strike':<8} {'Moneyness':<12} {'Delta':<8} {'Gamma':<10} {'Theta':<10} {'Vega':<8}")
    print("-" * 60)
    
    for K in [85, 90, 95, 100, 105, 110, 115]:
        calc = GreeksCalculator(S, K, T, r, sigma)
        greeks = calc.all_greeks('call')
        
        if K < S:
            moneyness = "ITM"
        elif K == S:
            moneyness = "ATM"
        else:
            moneyness = "OTM"
        
        print(f"{K:<8} {moneyness:<12} {greeks['delta']:<8.3f} {greeks['gamma']:<10.5f} {greeks['theta']:<10.4f} {greeks['vega']:<8.3f}")
    
    print()
    print("Key Observations:")
    print("- Delta increases with moneyness (ITM > ATM > OTM)")
    print("- Gamma is highest for ATM options")
    print("- Vega is highest for ATM options")
    print("- Theta (time decay) is most negative for ATM options")
    print()

def risk_management_insights():
    """Provide risk management insights using Greeks"""
    print("=" * 60)
    print("RISK MANAGEMENT INSIGHTS")
    print("=" * 60)
    print()
    
    print("1. DELTA RISK (Directional Risk)")
    print("-" * 35)
    print("• Delta measures directional exposure to underlying price")
    print("• Portfolio delta = sum of individual position deltas")
    print("• Delta-neutral portfolio: portfolio delta ≈ 0")
    print("• Rebalance frequency depends on gamma (delta sensitivity)")
    print()
    
    print("2. GAMMA RISK (Convexity Risk)")
    print("-" * 35)
    print("• Gamma measures how fast delta changes")
    print("• High gamma = frequent rebalancing needed")
    print("• Gamma risk highest for ATM options near expiration")
    print("• Long options: positive gamma (beneficial)")
    print("• Short options: negative gamma (risk)")
    print()
    
    print("3. THETA RISK (Time Decay Risk)")
    print("-" * 35)
    print("• Theta measures daily time decay")
    print("• Long options: negative theta (lose value daily)")
    print("• Short options: positive theta (gain value daily)")
    print("• Theta accelerates as expiration approaches")
    print("• ATM options have highest theta risk")
    print()
    
    print("4. VEGA RISK (Volatility Risk)")
    print("-" * 35)
    print("• Vega measures sensitivity to volatility changes")
    print("• Long options: positive vega (benefit from vol increase)")
    print("• Short options: negative vega (hurt by vol increase)")
    print("• Vega highest for ATM options with more time")
    print("• Implied volatility can be as important as direction")
    print()
    
    print("5. RHO RISK (Interest Rate Risk)")
    print("-" * 35)
    print("• Rho measures sensitivity to interest rate changes")
    print("• Generally smallest Greek for short-term options")
    print("• More important for long-term options (LEAPS)")
    print("• Call rho positive, put rho negative")
    print()

def main():
    """Run all analyses"""
    practical_hedging_example()
    time_decay_analysis()
    volatility_impact_analysis()
    moneyness_analysis()
    risk_management_insights()
    
    print("=" * 60)
    print("GREEKS SUMMARY COMPLETE")
    print("=" * 60)
    print()
    print("For detailed mathematical derivations and code implementations,")
    print("see the Option_Greeks.ipynb notebook.")

if __name__ == "__main__":
    main()