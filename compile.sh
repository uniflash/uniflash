#!/bin/sh

python -m vyper -f abi contracts/uniflash_factory.vy > abi/uniflash_factory.json
python -m vyper -f abi contracts/uniflash_eth.vy > abi/uniflash_eth.json
python -m vyper -f abi contracts/uniflash_erc20.vy > abi/uniflash_erc20.json
python -m vyper -f bytecode contracts/uniflash_factory.vy > bytecode/uniflash_factory.txt
python -m vyper -f bytecode contracts/uniflash_eth.vy > bytecode/uniflash_eth.txt
python -m vyper -f bytecode contracts/uniflash_erc20.vy > bytecode/uniflash_erc20.txt
