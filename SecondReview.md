As for the smart contract shown in [SpokkzCoin.py](https://github.com/Spuul/spokkz-ontology-smart-contracts/blob/master/contracts/contracts/SpokkzCoin.py), here is some humble suggestions.

1. ```ctx = GetContext()```  is the global variable, some (private) methods don't have to pass in the parameter ```_context```. And you should know that there is no much difference.

2. In the ```burn()``` method, you are using ``` Notify(['burn', _amount])``` to fire the burn event. Suggest you use ```Notify(['burn', account, amount])``` to identify the tokens are burnt from which account.

3. Besides, typo error here, ```burned = _burn(ctx, owner_key, _amount)``` should be ```burned = _burn(ctx, owner, _amount)```
4. There is nothing wrong within ```transferMulti()``` method, but it is better to use ```Require(transfer(p[0], [[1], p[2])``` to make sure ```transfer```method is invoked successfully.
Other places like the following, you can consider it as redundant, but it's an additional way to make sure nothing will be abnormal. 
```
Require(_transferFrom(ctx, _originator, _from, _to, _amount))

Require(_approve(ctx, _from, _to, _amount))

Require(_burn(ctx, owner_key, _amount))
```
