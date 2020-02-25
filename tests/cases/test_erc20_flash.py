from tests.constants import *

INTEREST = ERC20_DEPOSIT * INTEREST_FACTOR // 10000

def init_hay_balance(w3, erc20_flash, HAY_token):
    for account in w3.eth.accounts[:4]:
        HAY_token.functions.transfer(account, INITIAL_HAY).transact({})

def add_liquidity(erc20_flash, HAY_token, amount, _from):
    HAY_token.functions.approve(erc20_flash.address, amount).transact({'from':_from})
    erc20_flash.functions.addLiquidity(amount).transact({'from':_from})

def test_add_liquidity(w3, erc20_flash, HAY_token, assert_fail):
    init_hay_balance(w3, erc20_flash, HAY_token)
    a0, a1, a2 = w3.eth.accounts[:3]

    add_liquidity(erc20_flash, HAY_token, HAY_DEPOSIT, a1)
    assert HAY_token.caller.balanceOf(erc20_flash.address) == ERC20_DEPOSIT
    assert erc20_flash.caller.totalSupply() == ERC20_DEPOSIT
    assert HAY_token.caller.balanceOf(a1) == INITIAL_ERC20 - ERC20_DEPOSIT
    erc20_flash.caller.balanceOf(a1) == ERC20_DEPOSIT

    add_liquidity(erc20_flash, HAY_token, HAY_DEPOSIT, a1)
    assert HAY_token.caller.balanceOf(erc20_flash.address) == ERC20_DEPOSIT * 2
    assert erc20_flash.caller.totalSupply() == ERC20_DEPOSIT * 2
    assert HAY_token.caller.balanceOf(a1) == INITIAL_ERC20 - ERC20_DEPOSIT * 2
    erc20_flash.caller.balanceOf(a1) == ERC20_DEPOSIT * 2

def test_remove_liquidity_wo_flash(w3, erc20_flash, HAY_token, assert_fail):
    init_hay_balance(w3, erc20_flash, HAY_token)
    a0, a1, a2 = w3.eth.accounts[:3]
    add_liquidity(erc20_flash, HAY_token, HAY_DEPOSIT, a1)
    add_liquidity(erc20_flash, HAY_token, HAY_DEPOSIT, a2)

    assert_fail(lambda: erc20_flash.functions.removeLiquidity(ERC20_DEPOSIT + 1).transact({'from': a1}))
    erc20_flash.functions.removeLiquidity(ERC20_DEPOSIT).transact({'from': a1})
    assert_fail(lambda: erc20_flash.functions.removeLiquidity(ERC20_DEPOSIT).transact({'from': a0}))
    assert HAY_token.caller.balanceOf(erc20_flash.address) == ERC20_DEPOSIT
    assert erc20_flash.caller.totalSupply() == ERC20_DEPOSIT
    assert HAY_token.caller.balanceOf(a1) == INITIAL_ERC20
    assert erc20_flash.caller.balanceOf(a1) == 0
    assert HAY_token.caller.balanceOf(a2) == INITIAL_ERC20 - ERC20_DEPOSIT
    assert erc20_flash.caller.balanceOf(a2) == ERC20_DEPOSIT
    assert_fail(lambda: erc20_flash.functions.removeLiquidity(1).transact({'from': a1}))

    assert_fail(lambda: erc20_flash.functions.removeLiquidity(ERC20_DEPOSIT + 1).transact({'from': a2}))
    erc20_flash.functions.removeLiquidity(ERC20_DEPOSIT).transact({'from': a2})
    assert HAY_token.caller.balanceOf(erc20_flash.address) == 0
    assert erc20_flash.caller.totalSupply() == 0
    assert HAY_token.caller.balanceOf(a1) == INITIAL_ERC20
    assert erc20_flash.caller.balanceOf(a1) == 0
    assert HAY_token.caller.balanceOf(a2) == INITIAL_ERC20
    assert erc20_flash.caller.balanceOf(a2) == 0
    assert_fail(lambda: erc20_flash.functions.removeLiquidity(1).transact({'from': a2}))

def _init_test_flash(w3, erc20_flash, HAY_token, a1):
    init_hay_balance(w3, erc20_flash, HAY_token)
    add_liquidity(erc20_flash, HAY_token, HAY_DEPOSIT, a1)
    assert HAY_token.caller.balanceOf(erc20_flash.address) == ERC20_DEPOSIT
    assert erc20_flash.caller.totalSupply() == ERC20_DEPOSIT
    assert HAY_token.caller.balanceOf(a1) == INITIAL_ERC20 - ERC20_DEPOSIT
    assert erc20_flash.caller.balanceOf(a1) == ERC20_DEPOSIT

def test_flash_good_borrower(w3, erc20_flash, HAY_token, good_borrower, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    _init_test_flash(w3, erc20_flash, HAY_token, a1)

    HAY_token.functions.transfer(good_borrower.address, ERC20_DEPOSIT).transact({})
    assert HAY_token.caller.balanceOf(good_borrower.address) == ERC20_DEPOSIT
    good_borrower.functions.flash_loan_eth(erc20_flash.address, ERC20_DEPOSIT).transact({})
    assert HAY_token.caller.balanceOf(erc20_flash.address) == ERC20_DEPOSIT + INTEREST
    assert erc20_flash.caller.totalSupply() == ERC20_DEPOSIT
    assert HAY_token.caller.balanceOf(a1) == INITIAL_ERC20 - ERC20_DEPOSIT
    assert erc20_flash.caller.balanceOf(a1) == ERC20_DEPOSIT
    assert HAY_token.caller.balanceOf(good_borrower.address) == ERC20_DEPOSIT - INTEREST

    erc20_flash.functions.removeLiquidity(ERC20_DEPOSIT).transact({'from': a1})
    assert_fail(lambda: erc20_flash.functions.removeLiquidity(ERC20_DEPOSIT).transact({'from': a2}))
    assert HAY_token.caller.balanceOf(erc20_flash.address) == 0
    assert erc20_flash.caller.totalSupply() == 0
    assert HAY_token.caller.balanceOf(a1) == INITIAL_ERC20 + INTEREST
    assert erc20_flash.caller.balanceOf(a1) == 0
    assert HAY_token.caller.balanceOf(good_borrower.address) == ERC20_DEPOSIT - INTEREST

def test_flash_bad_borrower(w3, erc20_flash, HAY_token, bad_borrower, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    _init_test_flash(w3, erc20_flash, HAY_token, a1)

    HAY_token.functions.transfer(bad_borrower.address, ERC20_DEPOSIT).transact({})
    assert HAY_token.caller.balanceOf(bad_borrower.address) == ERC20_DEPOSIT
    assert_fail(lambda: bad_borrower.functions.flash_loan_eth(erc20_flash.address, ERC20_DEPOSIT).transact({}))

def test_flash_with_liquidity(w3, erc20_flash, HAY_token, good_borrower, assert_fail):
    a0, a1, a2, a3 = w3.eth.accounts[:4]
    _init_test_flash(w3, erc20_flash, HAY_token, a1)

    HAY_token.functions.transfer(good_borrower.address, ERC20_DEPOSIT).transact({})
    assert HAY_token.caller.balanceOf(good_borrower.address) == ERC20_DEPOSIT
    good_borrower.functions.flash_loan_eth(erc20_flash.address, ERC20_DEPOSIT).transact({})
    assert HAY_token.caller.balanceOf(erc20_flash.address) == ERC20_DEPOSIT + INTEREST
    assert erc20_flash.caller.totalSupply() == ERC20_DEPOSIT
    assert HAY_token.caller.balanceOf(a1) == INITIAL_ERC20 - ERC20_DEPOSIT
    assert erc20_flash.caller.balanceOf(a1) == ERC20_DEPOSIT
    assert HAY_token.caller.balanceOf(good_borrower.address) == ERC20_DEPOSIT - INTEREST

    add_liquidity(erc20_flash, HAY_token, HAY_DEPOSIT + INTEREST, a2)
    assert HAY_token.caller.balanceOf(erc20_flash.address) == (ERC20_DEPOSIT + INTEREST) * 2
    assert erc20_flash.caller.totalSupply() == ERC20_DEPOSIT * 2
    assert HAY_token.caller.balanceOf(a1) == INITIAL_ERC20 - ERC20_DEPOSIT
    assert erc20_flash.caller.balanceOf(a1) == ERC20_DEPOSIT
    assert HAY_token.caller.balanceOf(a2) == INITIAL_ERC20 - ERC20_DEPOSIT - INTEREST
    assert erc20_flash.caller.balanceOf(a2) == ERC20_DEPOSIT

    good_borrower.functions.flash_loan_eth(erc20_flash.address, ERC20_DEPOSIT).transact({})
    assert HAY_token.caller.balanceOf(erc20_flash.address) == ERC20_DEPOSIT * 2 + INTEREST * 3
    assert erc20_flash.caller.totalSupply() == ERC20_DEPOSIT * 2
    assert HAY_token.caller.balanceOf(a1) == INITIAL_ERC20 - ERC20_DEPOSIT
    assert erc20_flash.caller.balanceOf(a1) == ERC20_DEPOSIT
    assert HAY_token.caller.balanceOf(a2) == INITIAL_ERC20 - ERC20_DEPOSIT - INTEREST
    assert erc20_flash.caller.balanceOf(a2) == ERC20_DEPOSIT
    assert HAY_token.caller.balanceOf(good_borrower.address) == ERC20_DEPOSIT - INTEREST * 2

    add_liquidity(erc20_flash, HAY_token, HAY_DEPOSIT + INTEREST * 3 // 2, a3)
    assert HAY_token.caller.balanceOf(erc20_flash.address) == ERC20_DEPOSIT * 3 + INTEREST * 9 // 2
    assert erc20_flash.caller.totalSupply() == ERC20_DEPOSIT * 3
    assert HAY_token.caller.balanceOf(a1) == INITIAL_ERC20 - ERC20_DEPOSIT
    assert erc20_flash.caller.balanceOf(a1) == ERC20_DEPOSIT
    assert HAY_token.caller.balanceOf(a2) == INITIAL_ERC20 - ERC20_DEPOSIT - INTEREST
    assert erc20_flash.caller.balanceOf(a2) == ERC20_DEPOSIT
    assert HAY_token.caller.balanceOf(a3) == INITIAL_ERC20 - ERC20_DEPOSIT - INTEREST * 3 // 2
    assert erc20_flash.caller.balanceOf(a3) == ERC20_DEPOSIT