from pandas_paddles import DF

sel = (
    # DF['a'] == DF['b'].str
    ((DF['a'].str.lower() == 'a')
     | (DF['b'] >= DF['c']))
    & DF['asdf'].clip(lower=DF['yyy'].str.length())
)

print(sel)

t = sel.as_tree()

print(t)
print('---')
print(t.pprint())
print('---')

tc, collapsed = t.collapse()
print(tc, collapsed)
print('===')
print(tc.pprint())
print('===')
