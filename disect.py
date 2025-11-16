#!/usr/bin/env python3
import os
import sys


def read_dependencies(path):
    with open(path) as f:
        dependencies = {}
        for row in f.read().split('\n'):
            if row != '' and not row.strip().startswith('#'):
                name, _, version = row.partition('==')
                dependencies[name] = None if version == '' else version
    return dependencies


def read_state(path):
    with open(path) as f:
        state = []
        for row in f.read().split('\n'):
            if row.startswith('# __BISECT_STATE__'):
                _, _, state = row.partition(':')
                state = [c == 'y' for c in state]
                break
    return state


def write_dependency_list(path, deps, state=None):
    with open(path, 'w') as f:
        if state is not None:
            state_repr = "".join('y' if s else 'n' for s in state)
            f.write(f'# __BISECT_STATE__:{state_repr}\n')
        f.write(
            '\n'.join(
                (
                    f'{name}=={version}'
                    if version is not None else
                    name
                    for name, version in sorted(deps.items(), key=lambda x: (x[1] is not None, x[0]))
                )
            )
        )


def print_usage():
    print("usage: disect GOOD_DEPS NEW_DEPS <command>\n")
    print("Commands:")
    print("  start        Begin a dependency bisect session")
    print("  good         Mark the last test result as good")
    print("  bad          Mark the last test result as bad")


if '-h' in sys.argv or '--help' in sys.argv:
    print()
    print("disect is a program that helps you find what dependencies caused a regression.")
    print("It minimizes the number of environments that needs to be tested by leveraging combinatorical group testing.")
    print("It works similar to 'git bisect', and will repeatedly ask the user to mark")
    print("dependency sets as good or bad, splitting the search space based on the results.")
    print()
    print("To run it you need to provide:")
    print("    1. A pip requirements file where the dependencies that might have caused the regression")
    print("       are pinned to known good versions.")
    print("    2. A filename where the prgram will write the next environment to be tested.")
    print()
    print_usage()
    exit()

if len(sys.argv) < 4:
    print_usage()
    sys.exit(1)

if sys.argv[3] not in ('start', 'good', 'bad'):
    print(f"Unknown command: '{sys.argv[3]}'. Must be 'start', 'good', or bad.")
    print_usage()
    sys.exit(1)

good_dependencies_path = sys.argv[1]

if not os.path.isfile(good_dependencies_path):
    print(f"The known good dependencies file '{good_dependencies_path}' does not exists.")
    exit(1)

new_dependencies_path = sys.argv[2]
dependencies = read_dependencies(good_dependencies_path)

if sys.argv[3] == 'start':
    if os.path.isfile(new_dependencies_path):
        print("The new dependency file exists. To refine it further you must specify if it is good or bad.")
        print("Specify if it is good or bad by passing the argument 'good' or 'bad'.")
        sys.exit(1)

    replay_state = []
else:
    if not os.path.isfile(new_dependencies_path):
        print("The new dependency file does not exists.")
        print("Start a new session by passing the 'start' argument.")
        sys.exit(1)

    replay_state = [*read_state(new_dependencies_path), sys.argv[3] == 'good']


def search(options, contains):
    if len(options) < 2:
        return options
    first = set(sorted(options)[:len(options)//2])
    second = options - first
    return (
        (search(first, contains) if contains(first) else set()) |
        (search(second, contains) if contains(second) else set())
    )


times_called = 0


def set_contains_bad_dependency(to_unpin):
    global times_called
    if len(replay_state) > times_called:
        is_good_state = replay_state[times_called]
        times_called += 1
        # Return True if the state is bad.
        return not is_good_state

    new_dependencies = {
        name: None if name in to_unpin else version
        for name, version in dependencies.items()
    }
    if all(version is None for version in dependencies.values()):
        # If all dependencies are unpinned we know the bug is present
        return False
    write_dependency_list(new_dependencies_path, new_dependencies, replay_state)

    print("Now unpinning", len(to_unpin), '/', sum(1 for version in dependencies.values() if version is not None), 'dependencies')

    minimum_remaining_tests = estimate_remaining()
    print("Minimum remaining tests:", minimum_remaining_tests - len(replay_state))

    print(f"\nNext step:")
    print(f"  Apply and test these dependencies with your environment tool (example):")
    print(f"      uv run --with-requirements {os.path.abspath(new_dependencies_path)}\n")
    print("When your test completes, report the result:")
    print(f"      disect {good_dependencies_path} {new_dependencies_path} good    # if the test succeeded")
    print(f"      disect {good_dependencies_path} {new_dependencies_path} bad     # if the test failed")
    sys.exit()
 

def estimate_remaining():
    tc = 0
    unpinned_has_been_one = False
    def counter(unpinned):
        nonlocal tc, unpinned_has_been_one
        tc += 1
        index = tc - 1
        unpinned_has_been_one |= len(unpinned) == 1

        if len(replay_state) > index:
            is_good_state = replay_state[index]
            # Return True if the state is bad.
            return not is_good_state

        if not unpinned_has_been_one:
            # Assume every state is bad before on dependency
            # had been isolated.
            return True

        # Assume every state is good after that point.
        return False

    options = {name for name, version in dependencies.items() if version is not None}
    search(options, counter)
    return tc


bad_deps = search(
    {name for name, version in dependencies.items() if version is not None},
    set_contains_bad_dependency
)
write_dependency_list(
    new_dependencies_path,
    {
        name: version if name in bad_deps else None
        for name, version in dependencies.items()
    },
    replay_state,
)
print("Dependency bisection complete.")
