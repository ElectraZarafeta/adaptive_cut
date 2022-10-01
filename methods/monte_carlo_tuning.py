#%%

import random


def simulation():
    a = random.uniform(0, 1)
    
    if a>0.5:
        # Continue
        return True
    else:
        # Stop
        return False

prob = []

for _ in range(1000):
    
    output_list = []
    N = 100

    for _ in range(N):
        output_list.append(simulation())

    n_continue = sum(output_list)
    p_continue = n_continue/N
    prob.append(p_continue)
 

p_continue_MC = sum(prob)/1000
print("Probability to continue is {:.3f}".format(p_continue_MC))

#%%