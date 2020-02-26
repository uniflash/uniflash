import random

from tests.constants import *

INTEREST = ETH_DEPOSIT * INTEREST_FACTOR // 10000

def add_liquidity(w3, eth_flash, amount, _from):
    if random.choice([True, False]):
        eth_flash.functions.addLiquidity().transact({'value': amount, 'from': _from})
    else:
        w3.eth.sendTransaction({'to': eth_flash.address, 'value': amount, 'from': _from})

def remove_liquidity(eth_flash, amount, _from):
    eth_flash.functions.removeLiquidity(amount).transact({'from': _from})

def withdraw(eth_flash, _from):
    eth_flash.functions.withdraw().transact({'from': _from})

def flash(borrower, eth_flash, amount):
    borrower.functions.flash_loan_eth(eth_flash.address, amount).transact({})

def test_add_liquidity(w3, eth_flash, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    assert_fail(lambda: w3.eth.sendTransaction({'to': eth_flash.address, 'value': 0, 'from': a1}))

    add_liquidity(w3, eth_flash, ETH_DEPOSIT, a1)
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT
    assert eth_flash.caller.totalSupply() == ETH_DEPOSIT
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT
    eth_flash.caller.balanceOf(a1) == ETH_DEPOSIT

    add_liquidity(w3, eth_flash, ETH_DEPOSIT, a1)
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT * 2
    assert eth_flash.caller.totalSupply() == ETH_DEPOSIT * 2
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT * 2
    eth_flash.caller.balanceOf(a1) == ETH_DEPOSIT * 2

def test_remove_liquidity_wo_flash(w3, eth_flash, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    add_liquidity(w3, eth_flash, ETH_DEPOSIT, a1)
    add_liquidity(w3, eth_flash, ETH_DEPOSIT, a2)

    assert_fail(lambda: remove_liquidity(eth_flash, ETH_DEPOSIT, a0))
    assert_fail(lambda: remove_liquidity(eth_flash, 0, a1))
    assert_fail(lambda: remove_liquidity(eth_flash, ETH_DEPOSIT + 1, a1))
    remove_liquidity(eth_flash, ETH_DEPOSIT, a1)
    assert_fail(lambda: remove_liquidity(eth_flash, 1, a1))
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT
    assert eth_flash.caller.totalSupply() == ETH_DEPOSIT
    assert w3.eth.getBalance(a1) == INITIAL_ETH
    assert eth_flash.caller.balanceOf(a1) == 0
    assert w3.eth.getBalance(a2) == INITIAL_ETH - ETH_DEPOSIT
    assert eth_flash.caller.balanceOf(a2) == ETH_DEPOSIT

    assert_fail(lambda: remove_liquidity(eth_flash, ETH_DEPOSIT + 1, a2))
    withdraw(eth_flash, a2)
    assert_fail(lambda: remove_liquidity(eth_flash, 1, a2))
    assert w3.eth.getBalance(eth_flash.address) == 0
    assert eth_flash.caller.totalSupply() == 0
    assert w3.eth.getBalance(a1) == INITIAL_ETH
    assert eth_flash.caller.balanceOf(a1) == 0
    assert w3.eth.getBalance(a2) == INITIAL_ETH
    assert eth_flash.caller.balanceOf(a2) == 0

def _init_test_flash(w3, eth_flash, a1):
    add_liquidity(w3, eth_flash, ETH_DEPOSIT, a1)
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT
    assert eth_flash.caller.totalSupply() == ETH_DEPOSIT
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert eth_flash.caller.balanceOf(a1) == ETH_DEPOSIT

def test_flash_good_borrower(w3, eth_flash, good_borrower, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    _init_test_flash(w3, eth_flash, a1)

    w3.eth.sendTransaction({'to': good_borrower.address, 'value': ETH_DEPOSIT})
    assert w3.eth.getBalance(good_borrower.address) == ETH_DEPOSIT
    assert_fail(lambda: flash(good_borrower, eth_flash, 0))
    flash(good_borrower, eth_flash, ETH_DEPOSIT)
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT + INTEREST
    assert eth_flash.caller.totalSupply() == ETH_DEPOSIT
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert eth_flash.caller.balanceOf(a1) == ETH_DEPOSIT
    assert w3.eth.getBalance(good_borrower.address) == ETH_DEPOSIT - INTEREST

    remove_liquidity(eth_flash, ETH_DEPOSIT, a1)
    assert_fail(lambda: remove_liquidity(eth_flash, 1, a2))
    assert_fail(lambda: remove_liquidity(eth_flash, ETH_DEPOSIT, a2))
    assert w3.eth.getBalance(eth_flash.address) == 0
    assert eth_flash.caller.totalSupply() == 0
    assert w3.eth.getBalance(a1) == INITIAL_ETH + INTEREST
    assert eth_flash.caller.balanceOf(a1) == 0
    assert w3.eth.getBalance(good_borrower.address) == ETH_DEPOSIT - INTEREST

def test_flash_bad_borrower(w3, eth_flash, bad_borrower, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    _init_test_flash(w3, eth_flash, a1)

    w3.eth.sendTransaction({'to': bad_borrower.address, 'value': ETH_DEPOSIT})
    assert w3.eth.getBalance(bad_borrower.address) == ETH_DEPOSIT
    assert_fail(lambda: flash(bad_borrower, eth_flash, 1))
    assert_fail(lambda: flash(bad_borrower, eth_flash, ETH_DEPOSIT))

def test_flash_with_liquidity(w3, eth_flash, good_borrower, assert_fail):
    a0, a1, a2, a3 = w3.eth.accounts[:4]
    _init_test_flash(w3, eth_flash, a1)

    w3.eth.sendTransaction({'to': good_borrower.address, 'value': ETH_DEPOSIT})
    assert w3.eth.getBalance(good_borrower.address) == ETH_DEPOSIT
    flash(good_borrower, eth_flash, ETH_DEPOSIT)
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT + INTEREST
    assert eth_flash.caller.totalSupply() == ETH_DEPOSIT
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert eth_flash.caller.balanceOf(a1) == ETH_DEPOSIT
    assert w3.eth.getBalance(good_borrower.address) == ETH_DEPOSIT - INTEREST

    add_liquidity(w3, eth_flash, ETH_DEPOSIT + INTEREST, a2)
    assert w3.eth.getBalance(eth_flash.address) == (ETH_DEPOSIT + INTEREST) * 2
    assert eth_flash.caller.totalSupply() == ETH_DEPOSIT * 2
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert eth_flash.caller.balanceOf(a1) == ETH_DEPOSIT
    assert w3.eth.getBalance(a2) == INITIAL_ETH - ETH_DEPOSIT - INTEREST
    assert eth_flash.caller.balanceOf(a2) == ETH_DEPOSIT

    flash(good_borrower, eth_flash, ETH_DEPOSIT)
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT * 2 + INTEREST * 3
    assert eth_flash.caller.totalSupply() == ETH_DEPOSIT * 2
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert eth_flash.caller.balanceOf(a1) == ETH_DEPOSIT
    assert w3.eth.getBalance(a2) == INITIAL_ETH - ETH_DEPOSIT - INTEREST
    assert eth_flash.caller.balanceOf(a2) == ETH_DEPOSIT
    assert w3.eth.getBalance(good_borrower.address) == ETH_DEPOSIT - INTEREST * 2

    add_liquidity(w3, eth_flash, ETH_DEPOSIT + INTEREST * 3 // 2, a3)
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT * 3 + INTEREST * 9 // 2
    assert eth_flash.caller.totalSupply() == ETH_DEPOSIT * 3
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert eth_flash.caller.balanceOf(a1) == ETH_DEPOSIT
    assert w3.eth.getBalance(a2) == INITIAL_ETH - ETH_DEPOSIT - INTEREST
    assert eth_flash.caller.balanceOf(a2) == ETH_DEPOSIT
    assert w3.eth.getBalance(a3) == INITIAL_ETH - ETH_DEPOSIT - INTEREST * 3 // 2
    assert eth_flash.caller.balanceOf(a3) == ETH_DEPOSIT