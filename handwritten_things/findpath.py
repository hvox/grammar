rules = {"S":{"AB"}, "A":{"Aa", "bB"}, "B":{"a", "Sb"}}
target = "baabaab"

print("rules: ", rules)
print("target: ", target)
next_states = {"S":None}
visited, states = set(), []
turn = 0
while target not in visited:
    turn += 1
    print(f"iteration {turn:<2}", " #words=" + str(len(visited) + len(next_states)))
    old_next_state, next_states = next_states, {}
    for state, prev in old_next_state.items():
        visited.add(state)
        state_numb = len(states)
        states.append((state, prev))
        for i, nt in enumerate(state):
            for dest in rules.get(nt, ()):
                next_state = state[:i] + dest + state[i+1:]
                if next_state not in visited:
                    next_states[next_state] = state_numb
i = len(states) - 1
while states[i][0] != target:
    i -= 1
s, prev = states[i]
result = [s]
while prev != None:
    s, prev = states[prev]
    result.append(s)
result = list(reversed(result))
print(" -> ".join(result))
