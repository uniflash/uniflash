units: {
    ufo: "UniFlashlOan"
}

contract ETHLender():
    # DeFi is all you want :)
    def defi(loan: uint256(wei), interest: uint256(wei)): modifying

AddLiquidity: event({provider: indexed(address), eth_amount: indexed(uint256(wei))})
RemoveLiquidity: event({provider: indexed(address), eth_amount: indexed(uint256(wei))})
Transfer: event({_from: indexed(address), to: indexed(address), value: uint256(ufo)})
Approval: event({owner: indexed(address), spender: indexed(address), value: uint256(ufo)})

name: public(bytes32)                               # Uniflash for ETH V1
symbol: public(bytes32)                             # UFO-V1
decimals: public(uint256)
subsidy_factor: public(uint256)                     # subsidy rate = factor / 10000
totalSupply: public(uint256(ufo))
balances: map(address, uint256(ufo))
allowances: map(address, map(address, uint256(ufo)))

@public
def setup(_subsidy_factor: uint256):
    assert self.totalSupply == 0 and self.subsidy_factor == 0 and _subsidy_factor != 0
    self.name = 0x556e69666c61736820666f722045544820563100000000000000000000000000
    self.symbol = 0x55464f2d56310000000000000000000000000000000000000000000000000000
    self.decimals = 18
    self.subsidy_factor = _subsidy_factor

@private
def add_liquidity(provider: address, eth_amount: uint256(wei)) -> uint256(ufo):
    assert eth_amount >= 1_000_000_000_000_000
    old_liquidity: uint256(ufo) = self.totalSupply
    if old_liquidity > 0:
        eth_reserve: uint256(wei) = self.balance - eth_amount
        ufo_mint: uint256(ufo) = self.totalSupply * eth_amount / eth_reserve
        self.balances[provider] += ufo_mint
        self.totalSupply = old_liquidity + ufo_mint
        log.AddLiquidity(provider, eth_amount)
        log.Transfer(ZERO_ADDRESS, provider, ufo_mint)
        return ufo_mint
    else:
        assert self.subsidy_factor != 0
        initial_ufo_mint: uint256(ufo) = as_unitless_number(self.balance)
        self.balances[provider] = initial_ufo_mint
        self.totalSupply = initial_ufo_mint
        log.AddLiquidity(provider, eth_amount)
        log.Transfer(ZERO_ADDRESS, provider, initial_ufo_mint)
        return initial_ufo_mint

@public
@payable
def addLiquidity() -> uint256(ufo):
    return self.add_liquidity(msg.sender, msg.value)

@public
@payable
def __default__():
    self.add_liquidity(msg.sender, msg.value)

@private
def remove_liquidity(provider: address, ufo_amount: uint256(ufo)) -> uint256(wei):
    assert ufo_amount > 0
    old_liquidity: uint256(ufo) = self.totalSupply
    eth_amount: uint256(wei) = self.balance * ufo_amount / old_liquidity
    self.balances[provider] -= ufo_amount
    self.totalSupply = old_liquidity -  ufo_amount
    send(provider, eth_amount)
    log.RemoveLiquidity(provider, eth_amount)
    log.Transfer(provider, ZERO_ADDRESS, ufo_amount)
    return eth_amount

@public
def removeLiquidity(ufo_amount: uint256(ufo)) -> uint256(wei):
    return self.remove_liquidity(msg.sender, ufo_amount)

@public
def withdraw() -> uint256(wei):
    ufo_amount: uint256(ufo) = self.balances[msg.sender]
    return self.remove_liquidity(msg.sender, ufo_amount)

@public
def flash(eth_amount: uint256(wei), deadline: timestamp) -> uint256(wei):
    old_liquidity: uint256(ufo) = self.totalSupply
    old_balance: uint256(wei) = self.balance
    send(msg.sender, eth_amount)
    subsidy: uint256(wei) = eth_amount * self.subsidy_factor / 10000
    ETHLender(msg.sender).defi(eth_amount, subsidy)
    assert self.totalSupply == old_liquidity
    assert self.balance >= old_balance + subsidy
    return subsidy

@public
@payable
def return_loan():
    pass

# ERC20 compatibility modified from uniswap and vyper

@public
@constant
def balanceOf(owner: address) -> uint256(ufo):
    return self.balances[owner]

@public
def transfer(to: address, value: uint256(ufo)) -> bool:
    self.balances[msg.sender] -= value
    self.balances[to] += value
    log.Transfer(msg.sender, to, value)
    return True

@public
def transferFrom(_from: address, to: address, value: uint256(ufo)) -> bool:
    self.balances[_from] -= value
    self.balances[to] += value
    self.allowances[_from][msg.sender] -= value
    log.Transfer(_from, to, value)
    return True

@public
def approve(spender: address, value: uint256(ufo)) -> bool:
    self.allowances[msg.sender][spender] = value
    log.Approval(msg.sender, spender, value)
    return True

@public
@constant
def allowance(owner: address, spender: address) -> uint256(ufo):
    return self.allowances[owner][spender]