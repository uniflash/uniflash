from tests.constants import *

INTEREST = ETH_DEPOSIT * INTEREST_FACTOR // 10000

def init_hay_balance(w3, erc20_flash, HAY_token):
    for account in w3.eth.accounts[:4]:
        HAY_token.transfer(account, INITIAL_HAY, transact={})

def add_liquidity(erc20_flash, HAY_token, amount, _from):
    HAY_token.approve(erc20_flash.address, amount, transact={'from':_from})
    erc20_flash.addLiquidity(amount, transact={'from':_from})

def test_add_liquidity(w3, erc20_flash, HAY_token, assert_fail):
    init_hay_balance(w3, erc20_flash, HAY_token)
    a0, a1, a2 = w3.eth.accounts[:3]

    add_liquidity(erc20_flash, HAY_token, HAY_DEPOSIT, a1)
    assert HAY_token.balanceOf(erc20_flash.address) == ETH_DEPOSIT
    assert erc20_flash.totalSupply() == ETH_DEPOSIT
    assert HAY_token.balanceOf(a1) == INITIAL_ETH - ETH_DEPOSIT
    erc20_flash.balanceOf(a1) == ETH_DEPOSIT

    add_liquidity(erc20_flash, HAY_token, HAY_DEPOSIT, a1)
    assert HAY_token.balanceOf(erc20_flash.address) == ETH_DEPOSIT * 2
    assert erc20_flash.totalSupply() == ETH_DEPOSIT * 2
    assert HAY_token.balanceOf(a1) == INITIAL_ETH - ETH_DEPOSIT * 2
    erc20_flash.balanceOf(a1) == ETH_DEPOSIT * 2

def test_remove_liquidity_wo_flash(w3, erc20_flash, HAY_token, assert_fail):
    init_hay_balance(w3, erc20_flash, HAY_token)
    a0, a1, a2 = w3.eth.accounts[:3]
    add_liquidity(erc20_flash, HAY_token, HAY_DEPOSIT, a1)
    add_liquidity(erc20_flash, HAY_token, HAY_DEPOSIT, a2)

    assert_fail(lambda: erc20_flash.removeLiquidity(ETH_DEPOSIT + 1, transact={'from': a1}))
    erc20_flash.removeLiquidity(ETH_DEPOSIT, transact={'from': a1})
    assert_fail(lambda: erc20_flash.removeLiquidity(ETH_DEPOSIT, transact={'from': a0}))
    assert HAY_token.balanceOf(erc20_flash.address) == ETH_DEPOSIT
    assert erc20_flash.totalSupply() == ETH_DEPOSIT
    assert HAY_token.balanceOf(a1) == INITIAL_ETH
    assert erc20_flash.balanceOf(a1) == 0
    assert HAY_token.balanceOf(a2) == INITIAL_ETH - ETH_DEPOSIT
    assert erc20_flash.balanceOf(a2) == ETH_DEPOSIT
    assert_fail(lambda: erc20_flash.removeLiquidity(1, transact={'from': a1}))

    assert_fail(lambda: erc20_flash.removeLiquidity(ETH_DEPOSIT + 1, transact={'from': a2}))
    erc20_flash.removeLiquidity(ETH_DEPOSIT, transact={'from': a2})
    assert HAY_token.balanceOf(erc20_flash.address) == 0
    assert erc20_flash.totalSupply() == 0
    assert HAY_token.balanceOf(a1) == INITIAL_ETH
    assert erc20_flash.balanceOf(a1) == 0
    assert HAY_token.balanceOf(a2) == INITIAL_ETH
    assert erc20_flash.balanceOf(a2) == 0
    assert_fail(lambda: erc20_flash.removeLiquidity(1, transact={'from': a2}))

def _init_test_flash(w3, erc20_flash, HAY_token, a1):
    init_hay_balance(w3, erc20_flash, HAY_token)
    add_liquidity(erc20_flash, HAY_token, HAY_DEPOSIT, a1)
    assert HAY_token.balanceOf(erc20_flash.address) == ETH_DEPOSIT
    assert erc20_flash.totalSupply() == ETH_DEPOSIT
    assert HAY_token.balanceOf(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert erc20_flash.balanceOf(a1) == ETH_DEPOSIT

def test_flash_good_lender(w3, erc20_flash, HAY_token, good_lender, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    _init_test_flash(w3, erc20_flash, HAY_token, a1)

    HAY_token.transfer(good_lender.address, ETH_DEPOSIT, transact={})
    assert HAY_token.balanceOf(good_lender.address) == ETH_DEPOSIT
    good_lender.flash_loan_eth(erc20_flash.address, ETH_DEPOSIT, DEADLINE, transact={})
    assert HAY_token.balanceOf(erc20_flash.address) == ETH_DEPOSIT + INTEREST
    assert erc20_flash.totalSupply() == ETH_DEPOSIT
    assert HAY_token.balanceOf(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert erc20_flash.balanceOf(a1) == ETH_DEPOSIT
    assert HAY_token.balanceOf(good_lender.address) == ETH_DEPOSIT - INTEREST

    erc20_flash.removeLiquidity(ETH_DEPOSIT, transact={'from': a1})
    assert_fail(lambda: erc20_flash.removeLiquidity(ETH_DEPOSIT, transact={'from': a2}))
    assert HAY_token.balanceOf(erc20_flash.address) == 0
    assert erc20_flash.totalSupply() == 0
    assert HAY_token.balanceOf(a1) == INITIAL_ETH + INTEREST
    assert erc20_flash.balanceOf(a1) == 0
    assert HAY_token.balanceOf(good_lender.address) == ETH_DEPOSIT - INTEREST

def test_flash_bad_lender(w3, erc20_flash, HAY_token, bad_lender, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    _init_test_flash(w3, erc20_flash, HAY_token, a1)

    HAY_token.transfer(bad_lender.address, ETH_DEPOSIT, transact={})
    assert HAY_token.balanceOf(bad_lender.address) == ETH_DEPOSIT
    assert_fail(lambda: bad_lender.flash_loan_eth(erc20_flash.address, ETH_DEPOSIT, DEADLINE, transact={}))

def test_flash_with_liquidity(w3, erc20_flash, HAY_token, good_lender, assert_fail):
    a0, a1, a2, a3 = w3.eth.accounts[:4]
    _init_test_flash(w3, erc20_flash, HAY_token, a1)

    HAY_token.transfer(good_lender.address, ETH_DEPOSIT, transact={})
    assert HAY_token.balanceOf(good_lender.address) == ETH_DEPOSIT
    good_lender.flash_loan_eth(erc20_flash.address, ETH_DEPOSIT, DEADLINE, transact={})
    assert HAY_token.balanceOf(erc20_flash.address) == ETH_DEPOSIT + INTEREST
    assert erc20_flash.totalSupply() == ETH_DEPOSIT
    assert HAY_token.balanceOf(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert erc20_flash.balanceOf(a1) == ETH_DEPOSIT
    assert HAY_token.balanceOf(good_lender.address) == ETH_DEPOSIT - INTEREST

    add_liquidity(erc20_flash, HAY_token, HAY_DEPOSIT + INTEREST, a2)
    assert HAY_token.balanceOf(erc20_flash.address) == (ETH_DEPOSIT + INTEREST) * 2
    assert erc20_flash.totalSupply() == ETH_DEPOSIT * 2
    assert HAY_token.balanceOf(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert erc20_flash.balanceOf(a1) == ETH_DEPOSIT
    assert HAY_token.balanceOf(a2) == INITIAL_ETH - ETH_DEPOSIT - INTEREST
    assert erc20_flash.balanceOf(a2) == ETH_DEPOSIT

    good_lender.flash_loan_eth(erc20_flash.address, ETH_DEPOSIT, DEADLINE, transact={})
    assert HAY_token.balanceOf(erc20_flash.address) == ETH_DEPOSIT * 2 + INTEREST * 3
    assert erc20_flash.totalSupply() == ETH_DEPOSIT * 2
    assert HAY_token.balanceOf(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert erc20_flash.balanceOf(a1) == ETH_DEPOSIT
    assert HAY_token.balanceOf(a2) == INITIAL_ETH - ETH_DEPOSIT - INTEREST
    assert erc20_flash.balanceOf(a2) == ETH_DEPOSIT
    assert HAY_token.balanceOf(good_lender.address) == ETH_DEPOSIT - INTEREST * 2

    add_liquidity(erc20_flash, HAY_token, HAY_DEPOSIT + INTEREST * 3 // 2, a3)
    assert HAY_token.balanceOf(erc20_flash.address) == ETH_DEPOSIT * 3 + INTEREST * 9 // 2
    assert erc20_flash.totalSupply() == ETH_DEPOSIT * 3
    assert HAY_token.balanceOf(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert erc20_flash.balanceOf(a1) == ETH_DEPOSIT
    assert HAY_token.balanceOf(a2) == INITIAL_ETH - ETH_DEPOSIT - INTEREST
    assert erc20_flash.balanceOf(a2) == ETH_DEPOSIT
    assert HAY_token.balanceOf(a3) == INITIAL_ETH - ETH_DEPOSIT - INTEREST * 3 // 2
    assert erc20_flash.balanceOf(a3) == ETH_DEPOSIT