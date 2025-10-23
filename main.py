
from agents.inventory_agent import run_inventory_agent

run_inventory_agent(
    '''
    check our inventory, identify items where sum(quantity) below threshold level, 
    search for suppliers for those items.
    send me an email summary of the items and the suppliers for the items with links. 
    If there is such item, just send me an email saying all items are sufficiently stocked.
    '''
)

"""


if __name__ == "__main__":
    print("What can I help you today. (Type 'exit' to exit.)")
    while True:
        try:
            user_input = input("You: ").strip()
        except EOFError:
            break
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Inventory Agent: Bye!")
            break
        answer = run_inventory_agent(user_input)
        print(f"Inventory Agent: {answer}")

"""