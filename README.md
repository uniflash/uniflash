## Description

Uniflash is a simple and decentralized protocol for flash loans, trying to follow the design of Uniswap. It supports both Eth and ERC20 tokens. All the fee goes to users.

Note that Uniflash is not audited yet, though there are enough test cases. It's currently deployed on the Goerli network for testing.

## Try out

One could use any smart contract interactor to play with Uniflash, e.g. https://justsmartcontracts.dev/. We might add a front-end similar to Uniswap later if the community likes the project.

Testing on Goerli network:
1. Switch to Goerli network
2. Load `abi/uniflash-factory.json` with address: `0x09eb4Ffe5c05F34B27C169b4C21eB616158094Ae`
3. Get the flash-loan address of Eth by calling `getEthFlash` with any interest factor from 1 to 10 (e.g. 9 means 0.09% fee rate)
4. Load `abi/uniflash-eth.json` with the address fetched in Step 3
5. Now one could use `addLiquidity` and `removeLiquidity` to deposit and withdraw your Eth
6. Feel free to play with the other functionalities

One can create a Pool for any ERC20 token using `uniflash-factory`, and then following similar steps to deposit and withdraw your ERC20 tokens in the flash loan pool.

## Fee mechanism

For each token (including Eth), we initialize 10 pools with fee rate ranging from 0.01%, 0.02%, to 0.10%. Users are free to choose a pool with a matched fee rate.

Why don't we design a dynamic fee rate? The reasons are: 1. We don't want to use any price oracle to quantify the volume of each pool, so as to keep the protocol as simple as possible. 2. If the initial fee is high, then nobody would deposit. The protocol would be stuck in the cold-start phase. However, with the current design, users are able to switch between pools with different fee rates. 3. Even we set discrete fee rates, the pool size could change according to demands and supplies.

## Authors
* Cheng Wang - [polarker](https://twitter.com/wachmc)

We thank Uniswap for its pioneering work on DeFi design and implementation.