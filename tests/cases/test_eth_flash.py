from tests.contants import *

def test_default(w3, eth_flash, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    assert_fail(lambda: w3.eth.sendTransaction({'to': eth_flash.address, 'value': 0, 'from': a1}))
    eth_flash.addLiquidity(transact={'value': ETH_DEPOSIT, 'from': a1})
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert eth_flash.totalSupply() == ETH_DEPOSIT
    eth_flash.addLiquidity(transact={'value': ETH_DEPOSIT, 'from': a1})
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT * 2
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT * 2
    assert eth_flash.totalSupply() == ETH_DEPOSIT * 2

def test_withdraw_wo_flash(w3, eth_flash, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    eth_flash.addLiquidity(transact={'value': ETH_DEPOSIT, 'from': a1})
    eth_flash.addLiquidity(transact={'value': ETH_DEPOSIT, 'from': a2})
    eth_flash.removeLiquidity(ETH_DEPOSIT, transact={'from': a1})
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT
    assert eth_flash.totalSupply() == ETH_DEPOSIT
    assert w3.eth.getBalance(a1) == INITIAL_ETH
    assert eth_flash.balanceOf(a1) == 0
    assert w3.eth.getBalance(a2) == INITIAL_ETH - ETH_DEPOSIT
    assert eth_flash.balanceOf(a2) == ETH_DEPOSIT
    eth_flash.removeLiquidity(ETH_DEPOSIT, transact={'from': a2})
    assert w3.eth.getBalance(eth_flash.address) == 0
    assert eth_flash.totalSupply() == 0
    assert w3.eth.getBalance(a1) == INITIAL_ETH
    assert eth_flash.balanceOf(a1) == 0
    assert w3.eth.getBalance(a2) == INITIAL_ETH
    assert eth_flash.balanceOf(a2) == 0

def test_flash_good_lender(w3, eth_flash, factory, good_eth_lender, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    eth_flash.addLiquidity(transact={'value': ETH_DEPOSIT, 'from': a1})
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT
    assert eth_flash.totalSupply() == ETH_DEPOSIT
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert eth_flash.balanceOf(a1) == ETH_DEPOSIT
    w3.eth.sendTransaction({'to': good_eth_lender.address, 'value': ETH_DEPOSIT})
    assert w3.eth.getBalance(good_eth_lender.address) == ETH_DEPOSIT

    good_eth_lender.flash_loan_eth(eth_flash.address, ETH_DEPOSIT, DEADLINE, transact={})
    interest = ETH_DEPOSIT * 8 // 10000
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT + interest
    assert eth_flash.totalSupply() == ETH_DEPOSIT
    assert eth_flash.balanceOf(a1) == ETH_DEPOSIT
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert w3.eth.getBalance(good_eth_lender.address) == ETH_DEPOSIT - interest

    eth_flash.removeLiquidity(ETH_DEPOSIT, transact={'from': a1})
    assert_fail(lambda: eth_flash.removeLiquidity(ETH_DEPOSIT, transact={'from': a2}))
    assert w3.eth.getBalance(eth_flash.address) == 0
    assert eth_flash.totalSupply() == 0
    assert eth_flash.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == INITIAL_ETH + interest
    assert w3.eth.getBalance(good_eth_lender.address) == ETH_DEPOSIT - interest

def test_flash_bad_lender(w3, eth_flash, factory, bad_eth_lender, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    eth_flash.addLiquidity(transact={'value': ETH_DEPOSIT, 'from': a1})
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT
    assert eth_flash.totalSupply() == ETH_DEPOSIT
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert eth_flash.balanceOf(a1) == ETH_DEPOSIT
    w3.eth.sendTransaction({'to': bad_eth_lender.address, 'value': ETH_DEPOSIT})
    assert w3.eth.getBalance(bad_eth_lender.address) == ETH_DEPOSIT
    assert_fail(lambda: bad_eth_lender.flash_loan_eth(eth_flash.address, ETH_DEPOSIT, DEADLINE, transact={}))