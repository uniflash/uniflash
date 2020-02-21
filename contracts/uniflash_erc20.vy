units: {
    ufo: "UniFlashlOan"
    erc: "ERC20"
}

contrat ERC20Lender():
    # DeFi is all you want :)
    def erc20DeFi(token_amount: uint256(erc), interest: uint256(erc)): modifying

contract Factory():
    def create_erc20_flash(token_address: address): constant

AddLiquidity: event({provider: indexed(address), token_amount: indexed(uint256(erc))})
RemoveLiquidity: event({provider: indexed(address), token_amount: indexed(uint256(erc))})
Transfer: event({_from: indexed(address), to: indexed(address), value: uint256(ufo)})
Approval: event({owner: indexed(address), spender: indexed(address), value: uint256(ufo)})

factoryAddress: public(Factory)
token: public(ERC20)
name: public(bytes32)                                   # Uniflash for ETH V1
symbol: public(bytes32)                                 # UFO-V1
decimals: public(uint256)
subsidyFactor: public(uint256)                          # subsidy rate = factor / 10000
totalSupply: public(uint256(ufo))
balances: map(address, uint256(ufo))
allowances: map(address, map(address, uint256(ufo)))

@public
def setup(token_address: address, subsidy_factor: uint256):
    assert self.factoryAddress == ZERO_ADDRESS and \
             self.token == ZERO_ADDRESS and token_address != ZERO_ADDRESS \
             self.subsidyFactor == 0 and subsidy_factor > 0
    self.factoryAddress = Factory(msg.sender)
    self.token = ERC20(token_address)
    self.name = 0x556e69666c61736820666f722045544820563100000000000000000000000000
    self.symbol = 0x55464f2d56310000000000000000000000000000000000000000000000000000
    self.decimals = 18
    self.subsidyFactor = subsidy_factor

@private
def add_liquidity(provider: address, token_amount: uint256(erc)) -> uint256(ufo):
    assert token_amount >= 1_000_000_000_000_000
    old_liquidity: uint256(ufo) = self.totalSupply
    if old_liquidity > 0:
        token_reserve: uint256(erc) = self.token.balanceOf(self)
        ufo_mint: uint256(ufo) = self.totalSupply * token_amount / token_reserve
        self.balances[provider] += ufo_mint
        self.totalSupply = old_liquidity + ufo_mint
        assert self.token.transferFrom(provider, self, token_amount)
        log.AddLiquidity(provider, token_amount)
        log.Transfer(ZERO_ADDRESS, provider, ufo_mint)
        return ufo_mint
    else:
        assert self.factoryAddress != ZERO_ADDRESS and self.token != ZERO_ADDRESS and self.subsidyFactor > 0
        initial_ufo_mint: uint256(ufo) = token_amount
        self.balances[provider] = initial_ufo_mint
        self.totalSupply = initial_ufo_mint
        assert self.token.transferFrom(provider, self, token_amount)
        log.AddLiquidity(provider, token_amount)
        log.Transfer(ZERO_ADDRESS, provider, initial_ufo_mint)
        return initial_ufo_mint

@public
@payable
def addLiquidity(token_amount: uint256(erc)) -> uint256(ufo):
    return self.add_liquidity(msg.sender, token_amount)

@private
def remove_liquidity(provider: address, ufo_amount: uint256(ufo)) -> uint256(erc):
    assert ufo_amount > 0
    old_liquidity: uint256(ufo) = self.totalSupply
    token_amount: uint256(erc) = self.token.balancesOf(self) * ufo_amount / old_liquidity
    self.balances[provider] -= ufo_amount
    self.totalSupply = old_liquidity -  ufo_amount
    assert self.token.transfer(provider, token_amount)
    log.RemoveLiquidity(provider, token_amount)
    log.Transfer(provider, ZERO_ADDRESS, ufo_amount)
    return token_amount

@public
def removeLiquidity(ufo_amount: uint256(ufo)) -> uint256(erc):
    return self.remove_liquidity(msg.sender, ufo_amount)

@public
def withdraw() -> uint256(erc):
    ufo_amount: uint256(ufo) = self.balances[msg.sender]
    return self.remove_liquidity(msg.sender, ufo_amount)

@public
def flash(token_amount: uint256(erc), deadline: timestamp) -> uint256(erc):
    old_liquidity: uint256(ufo) = self.totalSupply
    old_balance: uint256(erc) = self.token.balanceOf(self)
    assert self.token.transfer(msg.sender, token_amount)
    subsidy: uint256(erc) = token_amount * self.subsidyFactor / 10000
    ERC20Lender(msg.sender).erc20DeFi(token_amount, subsidy)
    assert self.totalSupply == old_liquidity
    assert self.token.balanceOf(self) >= old_balance + subsidy
    return subsidy

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